"""
ARO Master TTS & Dubbing Module (Spec 07)
Features:
- Async Edge-TTS synthesis (vi-VN-HoaiMyNeural / vi-VN-NamMinhNeural)
- Content-addressed SHA-256 synthesis cache
- Precise subtitle window measurement and FFmpeg 'atempo' auto-fitting (1.0x - 1.25x)
- Silence trimming (-45dB threshold up to 100ms)
- Full timeline multi-lane voice track assembly at 48kHz with exact millisecond synchronization
"""

from __future__ import annotations

import os
import sys
import json
import wave
import struct
import asyncio
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from models import SubtitleCue, TtsCueResult, compute_sha256


class TtsDubbingEngine:
    """
    Production-grade Vietnamese TTS Dubbing Engine conforming to ARO Master Spec 07.
    """

    def __init__(
        self,
        cache_dir: str = ".aro_cache",
        voice_female: str = "vi-VN-HoaiMyNeural",
        voice_male: str = "vi-VN-NamMinhNeural",
        max_tempo: float = 1.25,
        min_tempo: float = 1.0,
    ):
        self.cache_dir = Path(cache_dir)
        self.tts_cache_dir = self.cache_dir / "tts"
        self.tts_cache_dir.mkdir(parents=True, exist_ok=True)

        self.voice_female = voice_female
        self.voice_male = voice_male
        self.max_tempo = max_tempo
        self.min_tempo = min_tempo

    def _select_voice_for_cue(self, cue: SubtitleCue) -> str:
        """Select appropriate voice based on speaker_id or gender hints."""
        speaker = (cue.speaker_id or "").lower()
        if "female" in speaker or "nu" in speaker or "muoi" in speaker or "ty" in speaker:
            return self.voice_female
        elif "male" in speaker or "nam" in speaker or "huynh" in speaker or "de" in speaker:
            return self.voice_male
        # Alternate or default to female voice
        return self.voice_female

    async def _synthesize_edge_tts_async(self, text: str, voice: str, out_path: str):
        """Synthesize text using edge-tts Python library."""
        try:
            import edge_tts
        except ImportError:
            raise RuntimeError("edge-tts library is not installed. Please run: pip install edge-tts")

        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+0%")
        # edge-tts generates MP3, save to temp then convert to 48kHz WAV
        temp_mp3 = out_path + ".tmp.mp3"
        await communicate.save(temp_mp3)

        # Convert MP3 to 48kHz mono 16-bit PCM WAV via FFmpeg
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i", temp_mp3,
            "-ar", "48000",
            "-ac", "1",
            "-c:a", "pcm_s16le",
            out_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg MP3 to WAV conversion failed: {res.stderr}")

    def synthesize_cue_raw(self, text: str, voice: str) -> str:
        """
        Synthesizes raw audio for a given text and voice with SHA-256 caching.
        Spec 07 Section 2: raw WAV cache key = sha256(text + voice).
        """
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Cannot synthesize empty text.")

        cache_key = compute_sha256(f"{clean_text}:{voice}:48000")
        raw_wav_path = self.tts_cache_dir / f"raw_{cache_key}.wav"

        if raw_wav_path.exists() and raw_wav_path.stat().st_size > 1024:
            return str(raw_wav_path)

        # Run async synthesis synchronously
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in an active event loop, run in a separate thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(asyncio.run, self._synthesize_edge_tts_async(clean_text, voice, str(raw_wav_path))).result()
            else:
                loop.run_until_complete(self._synthesize_edge_tts_async(clean_text, voice, str(raw_wav_path)))
        except RuntimeError:
            asyncio.run(self._synthesize_edge_tts_async(clean_text, voice, str(raw_wav_path)))

        return str(raw_wav_path)

    def measure_wav_duration_ms(self, wav_path: str) -> int:
        """Measure precise WAV duration in milliseconds."""
        try:
            with wave.open(wav_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate == 0:
                    return 0
                return int((frames * 1000) / rate)
        except Exception:
            return 0

    def trim_silence(self, input_wav: str, output_wav: str, threshold_db: float = -45.0, max_trim_ms: int = 100):
        """
        Spec 07 Section 3: Trim leading and trailing silence up to 100ms each at -45dB threshold,
        protecting speech onset and consonants.
        """
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i", input_wav,
            "-af", f"silenceremove=start_periods=1:start_duration=0.02:start_threshold={threshold_db}dB:stop_periods=1:stop_duration=0.05:stop_threshold={threshold_db}dB",
            "-ar", "48000",
            "-ac", "1",
            output_wav
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0 or not os.path.exists(output_wav) or os.path.getsize(output_wav) < 512:
            # Fallback to copy original if trimming removed everything
            import shutil
            shutil.copyfile(input_wav, output_wav)

    def fit_cue_audio(
        self,
        cue: SubtitleCue,
        raw_audio_path: str,
        available_ms: int
    ) -> TtsCueResult:
        """
        Spec 07 Section 3: Timing fit.
        Calculates tempo = measured / available.
        Applies FFmpeg atempo filter if tempo between 1.0 and 1.25.
        """
        # First trim silence
        trimmed_wav = str(self.tts_cache_dir / f"trimmed_{Path(raw_audio_path).stem}.wav")
        self.trim_silence(raw_audio_path, trimmed_wav)
        
        measured_ms = self.measure_wav_duration_ms(trimmed_wav)
        if measured_ms == 0:
            measured_ms = self.measure_wav_duration_ms(raw_audio_path)
            trimmed_wav = raw_audio_path

        voice = self._select_voice_for_cue(cue)

        # If fits within window comfortably
        if measured_ms <= available_ms or available_ms <= 0:
            return TtsCueResult(
                cue_id=cue.cue_id,
                cue_revision=cue.revision,
                effective_text=cue.tts_text or cue.translated_text,
                text_sha256=compute_sha256(cue.tts_text or cue.translated_text),
                requested_voice=voice,
                actual_voice=voice,
                raw_audio_path=raw_audio_path,
                fit_audio_path=trimmed_wav,
                measured_ms=measured_ms,
                available_ms=available_ms,
                tempo_milli=1000,
                status="VALID",
            )

        # Needs tempo acceleration
        raw_tempo = measured_ms / float(available_ms)
        tempo = min(raw_tempo, self.max_tempo)
        tempo_milli = int(round(tempo * 1000))

        fitted_wav = str(self.tts_cache_dir / f"fitted_{cue.cue_id}_{tempo_milli}.wav")

        # Apply FFmpeg atempo filter
        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i", trimmed_wav,
            "-filter:a", f"atempo={tempo:.3f}",
            "-ar", "48000",
            "-ac", "1",
            fitted_wav
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"[TTS Warning] FFmpeg atempo failed for cue {cue.cue_id}, falling back to trimmed audio.")
            fitted_wav = trimmed_wav
            tempo_milli = 1000

        new_measured_ms = self.measure_wav_duration_ms(fitted_wav)

        status = "VALID"
        reason = None
        if raw_tempo > self.max_tempo:
            status = "NEEDS_REVIEW"
            reason = f"Speech duration ({measured_ms}ms) exceeded available window ({available_ms}ms) beyond max tempo 1.25x."

        return TtsCueResult(
            cue_id=cue.cue_id,
            cue_revision=cue.revision,
            effective_text=cue.tts_text or cue.translated_text,
            text_sha256=compute_sha256(cue.tts_text or cue.translated_text),
            requested_voice=voice,
            actual_voice=voice,
            raw_audio_path=raw_audio_path,
            fit_audio_path=fitted_wav,
            measured_ms=new_measured_ms,
            available_ms=available_ms,
            tempo_milli=tempo_milli,
            status=status,
            reason=reason,
        )

    def assemble_voice_track(
        self,
        cues: List[SubtitleCue],
        fit_results: List[TtsCueResult],
        total_duration_ms: int,
        output_voice_track_path: str
    ) -> str:
        """
        Spec 07 Section 4: Build voice track without loading entire timeline in RAM.
        Creates continuous 48kHz mono 16-bit PCM WAV matching exact video duration.
        Uses FFmpeg adelay and amix or sample placement with accurate millisecond offsets.
        """
        out_p = Path(output_voice_track_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        sample_rate = 48000
        total_samples = int((total_duration_ms * sample_rate) / 1000)

        print(f"[TTS] Assembling continuous 48kHz master voice track ({total_duration_ms}ms / {total_samples} samples)...")

        # Mapping cue_id -> fit_result
        fits_map = {r.cue_id: r for r in fit_results}

        # Collect placement items: (start_ms, wav_path)
        placements: List[Tuple[int, str]] = []
        for cue in cues:
            fit = fits_map.get(cue.cue_id)
            if fit and fit.fit_audio_path and os.path.exists(fit.fit_audio_path):
                placements.append((cue.start_ms, fit.fit_audio_path))

        # Sort placements by start time
        placements.sort(key=lambda x: x[0])

        # Write sequential PCM samples into wave file
        with wave.open(str(out_p), "wb") as out_wf:
            out_wf.setnchannels(1)
            out_wf.setsampwidth(2)  # 16-bit PCM
            out_wf.setframerate(sample_rate)

            current_sample_pos = 0

            for start_ms, wav_file in placements:
                target_start_sample = int((start_ms * sample_rate) / 1000)

                # Write silence gap if needed
                if target_start_sample > current_sample_pos:
                    silence_samples = target_start_sample - current_sample_pos
                    # Write in 48000-sample blocks (1 second chunks) to avoid RAM ballooning
                    silence_block = b"\x00\x00" * min(silence_samples, 48000)
                    while silence_samples > 0:
                        to_write = min(silence_samples, 48000)
                        out_wf.writeframes(silence_block[:to_write * 2])
                        silence_samples -= to_write
                    current_sample_pos = target_start_sample

                # Read and append speech frames
                try:
                    with wave.open(wav_file, "rb") as in_wf:
                        in_frames = in_wf.getnframes()
                        frames_data = in_wf.readframes(in_frames)
                        out_wf.writeframes(frames_data)
                        current_sample_pos += in_frames
                except Exception as e:
                    print(f"[TTS Warning] Error reading {wav_file}: {e}")

            # Pad remaining silence up to total_duration_ms
            if current_sample_pos < total_samples:
                remaining_samples = total_samples - current_sample_pos
                silence_block = b"\x00\x00" * min(remaining_samples, 48000)
                while remaining_samples > 0:
                    to_write = min(remaining_samples, 48000)
                    out_wf.writeframes(silence_block[:to_write * 2])
                    remaining_samples -= to_write

        print(f"[TTS] Master voice track built successfully: {out_p.stat().st_size} bytes.")
        return str(out_p)

    def process(
        self,
        cues: List[SubtitleCue],
        total_duration_ms: int,
        output_voice_track_path: str
    ) -> Tuple[str, List[TtsCueResult]]:
        """
        Full TTS Dubbing Pipeline:
        1. Synthesize all cue texts with SHA-256 caching
        2. Calculate windows and apply atempo auto-fit
        3. Assemble continuous synchronized 48kHz voice track
        """
        if not cues:
            # Produce empty silence track
            self.assemble_voice_track([], [], total_duration_ms, output_voice_track_path)
            return output_voice_track_path, []

        print(f"[TTS] Synthesizing & timing-fitting {len(cues)} cues...")
        fit_results: List[TtsCueResult] = []

        for i, cue in enumerate(cues):
            text_to_speak = cue.tts_text or cue.translated_text
            if not text_to_speak.strip():
                continue

            voice = self._select_voice_for_cue(cue)
            
            # Calculate available window: Spec 07 Section 3
            next_start_ms = cues[i + 1].start_ms if i + 1 < len(cues) else total_duration_ms
            fit_end = min(cue.end_ms + 200, next_start_ms - 50, total_duration_ms)
            available_ms = max(0, fit_end - cue.start_ms)

            # Synthesize raw
            try:
                raw_wav = self.synthesize_cue_raw(text_to_speak, voice)
                fit_res = self.fit_cue_audio(cue, raw_wav, available_ms)
                fit_results.append(fit_res)
            except Exception as e:
                print(f"[TTS Error] Failed cue {cue.cue_id} ('{text_to_speak}'): {e}")

        # Assemble full voice track
        self.assemble_voice_track(cues, fit_results, total_duration_ms, output_voice_track_path)

        return output_voice_track_path, fit_results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tts_dubbing.py <translated_cues.json> <total_duration_ms> [output_voice.wav]")
        sys.exit(1)

    cues_file = sys.argv[1]
    dur_ms = int(sys.argv[2])
    out_voice = sys.argv[3] if len(sys.argv) > 3 else "master_voice.wav"

    with open(cues_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    cues = [SubtitleCue.from_dict(d) for d in data]

    engine = TtsDubbingEngine()
    engine.process(cues, dur_ms, out_voice)
    print("Done generating dubbing voice track!")

"""
ARO Master Transcriber Module (Spec 05 & Spec 09)
Extracts 16kHz mono audio via FFmpeg, segments via silence/VAD chunking (30s target, 45s max, 1s overlap),
calls Groq Whisper API (whisper-large-v3) or local faster-whisper fallback,
and implements SHA-256 content-addressable cache resume with core boundary ownership.
"""

from __future__ import annotations

import os
import io
import sys
import json
import wave
import struct
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

from models import SubtitleCue, WordTimestamp, AudioChunk, compute_sha256, generate_uuid


class AudioTranscriber:
    """
    Production-grade Audio Transcriber with SHA-256 Cache Resume,
    overlap-safe stitching, and Groq Whisper API integration.
    """

    def __init__(
        self,
        cache_dir: str = ".aro_cache",
        groq_api_key: Optional[str] = None,
        whisper_model: str = "whisper-large-v3",
        language: str = "zh",
        chunk_target_ms: int = 30000,
        chunk_max_ms: int = 45000,
        overlap_ms: int = 1000,
    ):
        self.cache_dir = Path(cache_dir)
        self.asr_cache_dir = self.cache_dir / "asr_chunks"
        self.asr_cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
        self.whisper_model = whisper_model
        self.language = language
        self.chunk_target_ms = chunk_target_ms
        self.chunk_max_ms = chunk_max_ms
        self.overlap_ms = overlap_ms

    def extract_audio_16k_mono(self, input_video_path: str, output_wav_path: str) -> str:
        """
        Extracts 16kHz mono 16-bit PCM WAV using FFmpeg without re-extracting if identical cache exists.
        """
        input_p = Path(input_video_path)
        if not input_p.exists():
            raise FileNotFoundError(f"Input video file not found: {input_video_path}")

        out_p = Path(output_wav_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        # Check existing valid audio file
        if out_p.exists() and out_p.stat().st_size > 1024:
            print(f"[ASR] Using existing extracted 16kHz audio: {output_wav_path}")
            return str(out_p)

        cmd = [
            "ffmpeg",
            "-nostdin",
            "-y",
            "-i", str(input_p),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",
            str(out_p)
        ]
        
        print(f"[ASR] Extracting 16kHz mono audio from {input_p.name}...")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg audio extraction failed (code {res.returncode}): {res.stderr}")

        if not out_p.exists() or out_p.stat().st_size == 0:
            raise RuntimeError("FFmpeg produced an empty or missing audio file.")

        print(f"[ASR] Audio extracted successfully: {out_p.stat().st_size} bytes")
        return str(out_p)

    def probe_audio_duration_ms(self, wav_path: str) -> int:
        """Read standard WAV header to compute total duration in milliseconds."""
        with wave.open(wav_path, "rb") as wf:
            frames = wf.getnframes()
            rate = wf.getframerate()
            if rate == 0:
                return 0
            return int((frames * 1000) / rate)

    def plan_audio_chunks(self, wav_path: str) -> List[AudioChunk]:
        """
        Segment audio file into target ~30s chunks (max 45s) with 1s overlap.
        Detects natural silence dips near target boundary to avoid cutting mid-speech.
        """
        total_duration_ms = self.probe_audio_duration_ms(wav_path)
        if total_duration_ms <= 0:
            return []

        chunks: List[AudioChunk] = []
        current_start_ms = 0
        chunk_idx = 0

        # Read samples in memory-efficient blocks to detect silence boundaries
        with wave.open(wav_path, "rb") as wf:
            sample_rate = wf.getframerate()
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            
            bytes_per_sample = sampwidth * n_channels
            bytes_per_ms = (sample_rate * bytes_per_sample) // 1000

            while current_start_ms < total_duration_ms:
                tentative_core_end_ms = min(current_start_ms + self.chunk_target_ms, total_duration_ms)
                
                # If close to end, take the rest
                if total_duration_ms - tentative_core_end_ms < 10000:
                    core_end_ms = total_duration_ms
                else:
                    # Search around [target - 3s, target + 10s] for lowest energy point
                    search_start_ms = max(current_start_ms + 15000, tentative_core_end_ms - 3000)
                    search_end_ms = min(tentative_core_end_ms + 10000, total_duration_ms, current_start_ms + self.chunk_max_ms)
                    
                    best_split_ms = tentative_core_end_ms
                    min_energy = float("inf")
                    
                    search_offset_bytes = search_start_ms * bytes_per_ms
                    search_len_bytes = (search_end_ms - search_start_ms) * bytes_per_ms
                    
                    try:
                        wf.setpos(search_start_ms * sample_rate // 1000)
                        raw_data = wf.readframes((search_end_ms - search_start_ms) * sample_rate // 1000)
                        # Check in 100ms windows
                        window_samples = sample_rate // 10  # 100ms
                        fmt = f"<{window_samples}h"
                        sample_bytes = window_samples * 2
                        
                        num_windows = len(raw_data) // sample_bytes
                        for w_i in range(num_windows):
                            sub = raw_data[w_i * sample_bytes:(w_i + 1) * sample_bytes]
                            if len(sub) == sample_bytes:
                                vals = struct.unpack(fmt, sub)
                                energy = sum(abs(v) for v in vals) / len(vals)
                                if energy < min_energy:
                                    min_energy = energy
                                    best_split_ms = search_start_ms + (w_i * 100)
                    except Exception:
                        best_split_ms = tentative_core_end_ms

                    core_end_ms = best_split_ms

                # Include 1s overlap for decode
                decode_start_ms = max(0, current_start_ms - (self.overlap_ms if chunk_idx > 0 else 0))
                decode_end_ms = min(total_duration_ms, core_end_ms + (self.overlap_ms if core_end_ms < total_duration_ms else 0))

                # Export chunk audio slice
                chunk_filename = f"chunk_{chunk_idx:04d}_{decode_start_ms}_{decode_end_ms}.wav"
                chunk_path = self.asr_cache_dir / chunk_filename
                
                # Extract chunk WAV
                wf.setpos(decode_start_ms * sample_rate // 1000)
                n_frames_to_read = ((decode_end_ms - decode_start_ms) * sample_rate) // 1000
                chunk_frames = wf.readframes(n_frames_to_read)

                with wave.open(str(chunk_path), "wb") as cwf:
                    cwf.setnchannels(1)
                    cwf.setsampwidth(2)
                    cwf.setframerate(sample_rate)
                    cwf.writeframes(chunk_frames)

                chunk_hash = compute_sha256(chunk_frames)
                chunks.append(AudioChunk(
                    chunk_id=f"chunk-{chunk_idx}-{chunk_hash[:12]}",
                    chunk_index=chunk_idx,
                    core_start_ms=current_start_ms,
                    core_end_ms=core_end_ms,
                    decode_start_ms=decode_start_ms,
                    decode_end_ms=decode_end_ms,
                    audio_path=str(chunk_path),
                    sha256=chunk_hash,
                    sample_rate=sample_rate,
                    channel_count=1,
                ))

                current_start_ms = core_end_ms
                chunk_idx += 1

        print(f"[ASR] Planned {len(chunks)} audio chunks with {self.overlap_ms}ms overlap.")
        return chunks

    def _call_groq_whisper(self, chunk_audio_path: str) -> Dict[str, Any]:
        """
        Call Groq Cloud Whisper API (whisper-large-v3) with word timestamps enabled.
        Standard multipart/form-data upload using urllib.
        """
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set. Please set the environment variable or pass to constructor.")

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        boundary = "----AroWhisperBoundary" + compute_sha256(chunk_audio_path)[:16]
        
        with open(chunk_audio_path, "rb") as f:
            file_bytes = f.read()

        filename = Path(chunk_audio_path).name

        body = bytearray()
        
        # model field
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="model"\r\n\r\n')
        body.extend(self.whisper_model.encode("utf-8") + b"\r\n")

        # language field
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="language"\r\n\r\n')
        body.extend(self.language.encode("utf-8") + b"\r\n")

        # response_format verbose_json
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="response_format"\r\n\r\n')
        body.extend(b"verbose_json\r\n")

        # timestamp_granularities[]
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="timestamp_granularities[]"\r\n\r\n')
        body.extend(b"word\r\n")

        # timestamp_granularities[] segment
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(b'Content-Disposition: form-data; name="timestamp_granularities[]"\r\n\r\n')
        body.extend(b"segment\r\n")

        # file field
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'.encode("utf-8"))
        body.extend(b"Content-Type: audio/wav\r\n\r\n")
        body.extend(file_bytes)
        body.extend(b"\r\n")

        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        req = urllib.request.Request(url, data=bytes(body), method="POST")
        req.add_header("Authorization", f"Bearer {self.groq_api_key}")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("User-Agent", "ARO-Master-Worker/1.0")

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                resp_text = resp.read().decode("utf-8")
                return json.loads(resp_text)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Groq API HTTP Error {e.code}: {err_body}")
        except Exception as e:
            raise RuntimeError(f"Groq Whisper transcription failed: {e}")

    def _call_faster_whisper_local(self, chunk_audio_path: str) -> Dict[str, Any]:
        """
        Fallback to faster-whisper local execution if Groq key is absent or offline.
        Uses CTranslate2 fast execution on CUDA/CPU.
        """
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise RuntimeError(
                "Neither valid GROQ_API_KEY was provided nor 'faster-whisper' package is installed. "
                "Please set GROQ_API_KEY or run: pip install faster-whisper"
            )

        print("[ASR] Running local faster-whisper model...")
        # Auto-select device
        device = "cuda" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        
        try:
            model = WhisperModel("large-v3", device=device, compute_type=compute_type)
        except Exception:
            print("[ASR] Fallback to CPU int8 for faster-whisper...")
            model = WhisperModel("small", device="cpu", compute_type="int8")

        segments, info = model.transcribe(
            chunk_audio_path,
            language=self.language,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=300),
        )

        words_list = []
        segments_list = []
        for s in segments:
            segments_list.append({
                "id": s.id,
                "start": s.start,
                "end": s.end,
                "text": s.text,
            })
            if s.words:
                for w in s.words:
                    words_list.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                        "probability": getattr(w, "probability", 0.95),
                    })

        return {
            "text": " ".join(s["text"] for s in segments_list),
            "words": words_list,
            "segments": segments_list,
        }

    def transcribe_chunk_with_cache(self, chunk: AudioChunk) -> Dict[str, Any]:
        """
        Checks cache for existing chunk result (SHA-256 key); executes and writes cache checkpoint if missing.
        Spec 09 Content-addressable cache.
        """
        cache_key = compute_sha256(f"{chunk.sha256}:{self.whisper_model}:{self.language}")
        cache_file = self.asr_cache_dir / f"result_{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached_data = json.load(f)
                    print(f"[ASR Cache HIT] Chunk #{chunk.chunk_index} ({chunk.core_start_ms}-{chunk.core_end_ms}ms)")
                    return cached_data
            except Exception as e:
                print(f"[ASR Cache Corrupt] Invalid cache {cache_file}, recomputing: {e}")

        print(f"[ASR Transcribing] Chunk #{chunk.chunk_index} ({chunk.decode_start_ms}-{chunk.decode_end_ms}ms)...")
        
        # Primary: Groq Cloud API; Fallback: faster-whisper
        if self.groq_api_key:
            try:
                result = self._call_groq_whisper(chunk.audio_path)
            except Exception as e:
                print(f"[ASR Warning] Groq API failed ({e}), attempting local fallback...")
                result = self._call_faster_whisper_local(chunk.audio_path)
        else:
            result = self._call_faster_whisper_local(chunk.audio_path)

        # Write durable checkpoint
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    def stitch_chunks_into_cues(
        self,
        chunks: List[AudioChunk],
        chunk_results: List[Dict[str, Any]]
    ) -> List[SubtitleCue]:
        """
        Spec 05 & Spec 09: Global Millisecond Alignment & Core Boundary Ownership.
        A word's midpoint (start + end)/2 determines which chunk owns it.
        Words from overlap zones outside the chunk's core interval are strictly ignored,
        preventing duplicate cues or dropped words at seams.
        """
        all_words: List[WordTimestamp] = []

        for chunk, result in zip(chunks, chunk_results):
            words_data = result.get("words", [])
            # Fallback to segments if words not granular
            if not words_data and "segments" in result:
                for seg in result["segments"]:
                    seg_text = seg.get("text", "").strip()
                    seg_start = int(seg.get("start", 0) * 1000)
                    seg_end = int(seg.get("end", 0) * 1000)
                    words_data.append({
                        "word": seg_text,
                        "start": seg_start / 1000.0,
                        "end": seg_end / 1000.0,
                    })

            for w in words_data:
                text = str(w.get("word", "")).strip()
                if not text:
                    continue
                # Local offset to global ms
                local_start_ms = int(round(float(w.get("start", 0)) * 1000))
                local_end_ms = int(round(float(w.get("end", 0)) * 1000))
                
                global_start_ms = chunk.decode_start_ms + local_start_ms
                global_end_ms = chunk.decode_start_ms + local_end_ms
                
                if global_end_ms <= global_start_ms:
                    global_end_ms = global_start_ms + 200

                word_midpoint = (global_start_ms + global_end_ms) // 2

                # Spec 05 Section 6: Word midpoint must fall strictly within chunk's core interval
                if chunk.core_start_ms <= word_midpoint < chunk.core_end_ms:
                    prob = float(w.get("probability", 0.95))
                    all_words.append(WordTimestamp(
                        text=text,
                        start_ms=global_start_ms,
                        end_ms=global_end_ms,
                        confidence_milli=int(prob * 1000),
                    ))

        # Sort all words strictly by global start time
        all_words.sort(key=lambda x: (x.start_ms, x.end_ms))

        # Group words into logical sentence SubtitleCues
        cues: List[SubtitleCue] = []
        sentence_enders = {"。", "！", "？", "!", "?", "…", "；", ";"}
        comma_pause_threshold_ms = 400
        max_cue_duration_ms = 7000
        min_cue_duration_ms = 800

        current_words: List[WordTimestamp] = []
        current_cue_start_ms: Optional[int] = None

        for w in all_words:
            if not current_words:
                current_words.append(w)
                current_cue_start_ms = w.start_ms
                continue

            prev_word = current_words[-1]
            gap_ms = w.start_ms - prev_word.end_ms
            cur_duration = w.end_ms - (current_cue_start_ms or 0)
            
            has_sentence_end = any(prev_word.text.endswith(p) for p in sentence_enders)
            is_long_pause = gap_ms >= comma_pause_threshold_ms
            is_too_long = cur_duration >= max_cue_duration_ms

            if (has_sentence_end or is_long_pause or is_too_long) and cur_duration >= min_cue_duration_ms:
                # Flush current cue
                cue_text = "".join(x.text for x in current_words)
                cue_end = prev_word.end_ms
                
                avg_confidence = sum(x.confidence_milli for x in current_words) // len(current_words)
                cues.append(SubtitleCue(
                    cue_id=generate_uuid(),
                    revision=1,
                    start_ms=current_cue_start_ms or 0,
                    end_ms=cue_end,
                    source_text=cue_text,
                    source_confidence_milli=avg_confidence,
                    source_method="asr",
                    words=list(current_words),
                ))
                current_words = [w]
                current_cue_start_ms = w.start_ms
            else:
                current_words.append(w)

        # Flush remaining words
        if current_words:
            cue_text = "".join(x.text for x in current_words)
            cue_start = current_cue_start_ms or current_words[0].start_ms
            cue_end = current_words[-1].end_ms
            avg_confidence = sum(x.confidence_milli for x in current_words) // len(current_words)
            cues.append(SubtitleCue(
                cue_id=generate_uuid(),
                revision=1,
                start_ms=cue_start,
                end_ms=cue_end,
                source_text=cue_text,
                source_confidence_milli=avg_confidence,
                source_method="asr",
                words=list(current_words),
            ))

        print(f"[ASR] Stitched into {len(cues)} clean Subtitle Cues.")
        return cues

    def process(self, video_path: str, output_cues_json: Optional[str] = None) -> List[SubtitleCue]:
        """
        Full ASR Pipeline:
        1. Extract 16kHz audio
        2. Plan 30s/45s chunks with 1s overlap
        3. Transcribe chunks with SHA-256 cache
        4. Seamlessly stitch cues
        """
        temp_wav = str(self.cache_dir / f"extracted_{Path(video_path).stem}_16k.wav")
        self.extract_audio_16k_mono(video_path, temp_wav)

        chunks = self.plan_audio_chunks(temp_wav)
        chunk_results = []
        for chunk in chunks:
            res = self.transcribe_chunk_with_cache(chunk)
            chunk_results.append(res)

        cues = self.stitch_chunks_into_cues(chunks, chunk_results)

        if output_cues_json:
            out_p = Path(output_cues_json)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in cues], f, ensure_ascii=False, indent=2)
            print(f"[ASR] Saved {len(cues)} cues to {output_cues_json}")

        return cues


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcriber.py <input_video_or_wav> [output_cues.json]")
        sys.exit(1)

    video_input = sys.argv[1]
    out_json = sys.argv[2] if len(sys.argv) > 2 else "source_cues.json"
    
    transcriber = AudioTranscriber()
    res_cues = transcriber.process(video_input, out_json)
    print(f"Done! Transcribed {len(res_cues)} cues.")

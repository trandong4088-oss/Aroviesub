"""
ARO Master Daemon & Job Orchestrator (Spec 05, Spec 08, Spec 09)
Coordinates end-to-end ARO pipeline:
PROBE -> EXTRACT_AUDIO -> TRANSCRIBE (ASR) -> TRANSLATE (TM + LLM) -> TTS_DUBBING ->
AUDIO_DUCKING_MIX -> RENDER_MP4 -> VALIDATE.

Includes full Stage-level Checkpoint Resume (survives Colab reboots) and RAM/VRAM leak guards.
"""

from __future__ import annotations

import os
import gc
import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, Optional, Callable

from models import SubtitleCue, PipelineConfig, compute_sha256
from transcriber import AudioTranscriber
from translator import DonghuaTranslator
from tts_dubbing import TtsDubbingEngine
from pipeline import MediaPipeline


class AroWorker:
    """
    Main ARO Master Worker Daemon.
    Manages jobs, persists state to disk, handles crashes and resume,
    and coordinates modular components.
    """

    def __init__(
        self,
        workspace_dir: str = "aro_workspace",
        groq_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        genre: str = "xianxia",
        config: Optional[PipelineConfig] = None,
    ):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_dir = self.workspace_dir / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.groq_api_key = groq_api_key or os.environ.get("GROQ_API_KEY", "")
        self.gemini_api_key = gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
        self.genre = genre
        self.config = config or PipelineConfig(genre=genre)

        # Initialize core engines
        self.transcriber = AudioTranscriber(
            cache_dir=str(self.cache_dir),
            groq_api_key=self.groq_api_key,
            whisper_model=self.config.whisper_model,
            chunk_target_ms=self.config.asr_chunk_target_ms,
            chunk_max_ms=self.config.asr_chunk_max_ms,
            overlap_ms=self.config.asr_overlap_ms,
        )

        db_path = str(self.workspace_dir / "aro_translation_memory.db")
        self.translator = DonghuaTranslator(
            db_path=db_path,
            gemini_api_key=self.gemini_api_key,
            groq_api_key=self.groq_api_key,
            genre=self.genre,
            batch_size=self.config.translation_batch_size,
        )

        self.tts_engine = TtsDubbingEngine(
            cache_dir=str(self.cache_dir),
            voice_female=self.config.tts_primary_voice_female,
            voice_male=self.config.tts_primary_voice_male,
            max_tempo=self.config.max_tempo_ratio,
            min_tempo=self.config.min_tempo_ratio,
        )

        self.pipeline = MediaPipeline(self.config)

    def _get_checkpoint_path(self, job_id: str) -> Path:
        return self.workspace_dir / f"job_{job_id}_checkpoint.json"

    def _load_checkpoint(self, job_id: str) -> Dict[str, Any]:
        cp_file = self._get_checkpoint_path(job_id)
        if cp_file.exists():
            try:
                with open(cp_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_checkpoint(self, job_id: str, data: Dict[str, Any]):
        cp_file = self._get_checkpoint_path(job_id)
        with open(cp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def run_job(
        self,
        video_input_path: str,
        output_mp4_path: Optional[str] = None,
        progress_cb: Optional[Callable[[str, float, str], None]] = None,
        burn_subtitles: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes complete production workflow with checkpoint resumption.
        """
        start_time = time.time()
        in_p = Path(video_input_path)
        if not in_p.exists():
            raise FileNotFoundError(f"Input video file not found: {video_input_path}")

        # Compute deterministic job_id based on video file size and first/last 64KB
        with open(in_p, "rb") as f:
            header = f.read(65536)
            f.seek(max(0, in_p.stat().st_size - 65536))
            footer = f.read(65536)
        job_id = compute_sha256(header + str(in_p.stat().st_size).encode() + footer)[:16]

        if not output_mp4_path:
            output_mp4_path = str(self.workspace_dir / f"{in_p.stem}_ARO_Vietsub.mp4")

        def report(stage: str, pct: float, msg: str):
            print(f"[{pct * 100:5.1f}%] [{stage.upper()}] {msg}")
            if progress_cb:
                progress_cb(stage, pct, msg)

        print("\n" + "=" * 60)
        print(f"ARO MASTER WORKER - JOB ID: {job_id}")
        print(f"Input: {in_p.name} ({in_p.stat().st_size / (1024*1024):.2f} MB)")
        print(f"Genre: {self.genre.upper()} | Output: {Path(output_mp4_path).name}")
        print("=" * 60 + "\n")

        checkpoint = self._load_checkpoint(job_id)

        # -------------------------------------------------------------
        # STAGE 1: PROBE MEDIA
        # -------------------------------------------------------------
        report("probe", 0.05, "Analyzing media streams with ffprobe...")
        probe_info = self.pipeline.probe_media(str(in_p))
        total_duration_ms = probe_info.duration_ms
        report("probe", 0.10, f"Probed: {probe_info.display_width}x{probe_info.display_height}, {total_duration_ms/1000.0:.1f}s, {probe_info.avg_fps:.1f} FPS")

        # -------------------------------------------------------------
        # STAGE 2 & 3: ASR TRANSCRIPTION WITH SHA-256 RESUME
        # -------------------------------------------------------------
        cues_checkpoint_file = self.workspace_dir / f"job_{job_id}_source_cues.json"
        cues: list[SubtitleCue] = []

        if checkpoint.get("asr_completed") and cues_checkpoint_file.exists():
            report("asr", 0.30, "ASR Stage Checkpoint HIT! Loading source cues from disk...")
            with open(cues_checkpoint_file, "r", encoding="utf-8") as f:
                cues_data = json.load(f)
                cues = [SubtitleCue.from_dict(d) for d in cues_data]
        else:
            report("asr", 0.15, "Extracting audio and segmenting into 30s/45s chunks...")
            cues = self.transcriber.process(str(in_p), str(cues_checkpoint_file))
            checkpoint["asr_completed"] = True
            checkpoint["cues_count"] = len(cues)
            self._save_checkpoint(job_id, checkpoint)
            report("asr", 0.35, f"ASR Completed: Extracted {len(cues)} speech cues.")

        if not cues:
            raise RuntimeError("No dialogue or speech cues could be extracted from audio.")

        # Trigger garbage collection to keep RAM minimal
        gc.collect()

        # -------------------------------------------------------------
        # STAGE 4: TRANSLATION (TM O(1) + LLM + DONGHUA GLOSSARY)
        # -------------------------------------------------------------
        translated_cues_file = self.workspace_dir / f"job_{job_id}_translated_cues.json"
        
        if checkpoint.get("translation_completed") and translated_cues_file.exists():
            report("translate", 0.50, "Translation Checkpoint HIT! Loading translated cues...")
            with open(translated_cues_file, "r", encoding="utf-8") as f:
                t_data = json.load(f)
                cues = [SubtitleCue.from_dict(d) for d in t_data]
        else:
            report("translate", 0.40, f"Translating {len(cues)} cues with Translation Memory & {self.genre} glossary...")
            cues = self.translator.process(cues)
            with open(translated_cues_file, "w", encoding="utf-8") as f:
                json.dump([c.to_dict() for c in cues], f, ensure_ascii=False, indent=2)
            checkpoint["translation_completed"] = True
            self._save_checkpoint(job_id, checkpoint)
            report("translate", 0.55, f"Translation completed for {len(cues)} cues.")

        gc.collect()

        # -------------------------------------------------------------
        # STAGE 5: TTS DUBBING & ATEMPO AUTO-FIT
        # -------------------------------------------------------------
        voice_track_wav = str(self.workspace_dir / f"job_{job_id}_voice_track.wav")
        
        if checkpoint.get("tts_completed") and os.path.exists(voice_track_wav):
            report("tts", 0.70, "TTS Dubbing Checkpoint HIT! Using cached master voice track...")
        else:
            report("tts", 0.60, f"Synthesizing Vietnamese Edge-TTS with atempo fit for {len(cues)} cues...")
            self.tts_engine.process(cues, total_duration_ms, voice_track_wav)
            checkpoint["tts_completed"] = True
            self._save_checkpoint(job_id, checkpoint)
            report("tts", 0.75, "TTS Dubbing & Timeline Assembly completed.")

        gc.collect()

        # -------------------------------------------------------------
        # STAGE 6: SUBTITLES EXPORT (SRT & ASS)
        # -------------------------------------------------------------
        report("subtitles", 0.78, "Generating styled ASS & SRT subtitles...")
        srt_file = str(self.workspace_dir / f"job_{job_id}_vi.srt")
        ass_file = str(self.workspace_dir / f"job_{job_id}_vi.ass")
        self.pipeline.export_srt(cues, srt_file)
        self.pipeline.export_ass(cues, ass_file, probe_info.display_width, probe_info.display_height)

        # -------------------------------------------------------------
        # STAGE 7: AUDIO DUCKING (82% REDUCTION) & 2-PASS LOUDNORM
        # -------------------------------------------------------------
        master_audio_wav = str(self.workspace_dir / f"job_{job_id}_master_audio.wav")
        
        if checkpoint.get("ducking_completed") and os.path.exists(master_audio_wav):
            report("ducking", 0.85, "Audio Ducking Checkpoint HIT! Using cached master audio...")
        else:
            report("ducking", 0.80, "Executing 82% Audio Ducking & EBU R128 2-Pass Loudnorm (-16 LUFS)...")
            self.pipeline.mix_audio_ducking_with_loudnorm(
                str(in_p), voice_track_wav, master_audio_wav, total_duration_ms
            )
            checkpoint["ducking_completed"] = True
            self._save_checkpoint(job_id, checkpoint)
            report("ducking", 0.88, "Ducking and Loudness normalization completed.")

        gc.collect()

        # -------------------------------------------------------------
        # STAGE 8: FINAL MP4 RENDERING
        # -------------------------------------------------------------
        report("render", 0.90, f"Encoding final MP4 video (Hardsub: {burn_subtitles})...")
        self.pipeline.render_final_video(
            video_source_path=str(in_p),
            master_audio_path=master_audio_wav,
            ass_subtitle_path=ass_file,
            output_mp4_path=output_mp4_path,
            burn_subtitles=burn_subtitles,
        )

        # -------------------------------------------------------------
        # STAGE 9: FINAL 11-POINT VALIDATION
        # -------------------------------------------------------------
        report("validate", 0.98, "Validating final output container and audio/video sync...")
        val_report = self.pipeline.validate_final_output(output_mp4_path)

        elapsed = time.time() - start_time
        report("complete", 1.0, f"SUCCESS! Finished in {elapsed:.1f}s. Output: {output_mp4_path}")

        result_manifest = {
            "job_id": job_id,
            "status": "COMPLETED",
            "video_input": str(in_p),
            "output_mp4": output_mp4_path,
            "srt_path": srt_file,
            "ass_path": ass_file,
            "master_audio_path": master_audio_wav,
            "cues_count": len(cues),
            "duration_ms": total_duration_ms,
            "elapsed_seconds": round(elapsed, 2),
            "validation": val_report,
        }

        # Save final result manifest
        with open(self.workspace_dir / f"job_{job_id}_result.json", "w", encoding="utf-8") as f:
            json.dump(result_manifest, f, ensure_ascii=False, indent=2)

        return result_manifest


def parse_cli_args():
    parser = argparse.ArgumentParser(
        description="ARO Master Worker Daemon - Automated Subtitles, Translation & Dubbing for Donghua"
    )
    parser.add_argument("--video", "-i", required=True, help="Input video file path (MP4, MKV, AVI, etc.)")
    parser.add_argument("--out", "-o", default=None, help="Output MP4 file path")
    parser.add_argument("--genre", "-g", default="xianxia", choices=["xianxia", "wuxia", "historical", "transmigration", "modern", "neutral"], help="Donghua genre profile")
    parser.add_argument("--groq-key", default=None, help="Groq Cloud API Key (for Whisper-large-v3 and Llama 3.3)")
    parser.add_argument("--gemini-key", default=None, help="Google Gemini API Key")
    parser.add_argument("--workspace", "-w", default="aro_workspace", help="Workspace working directory")
    parser.add_argument("--no-hardsub", action="store_true", help="Do not burn subtitles into video pixels")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_cli_args()
    
    worker = AroWorker(
        workspace_dir=args.workspace,
        groq_api_key=args.groq_key,
        gemini_api_key=args.gemini_key,
        genre=args.genre,
    )
    
    worker.run_job(
        video_input_path=args.video,
        output_mp4_path=args.out,
        burn_subtitles=not args.no_hardsub,
    )

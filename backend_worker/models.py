"""
ARO Master Core Data Models (Spec 04 & Spec 05)
Standard data structures for Transcriber, Translator, TTS, and Audio/Video Pipeline.
"""

from __future__ import annotations

import json
import uuid
import hashlib
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict


def generate_uuid() -> str:
    """Generate a lowercase UUIDv4 string."""
    return str(uuid.uuid4()).lower()


def compute_sha256(data: bytes | str) -> str:
    """Compute 64-character lowercase SHA-256 hexadecimal digest."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest().lower()


@dataclass
class WordTimestamp:
    """Word-level timing information from ASR."""
    text: str
    start_ms: int
    end_ms: int
    confidence_milli: int = 1000

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WordTimestamp:
        return cls(
            text=str(data.get("text", "")),
            start_ms=int(data.get("start_ms", 0)),
            end_ms=int(data.get("end_ms", 0)),
            confidence_milli=int(data.get("confidence_milli", 1000)),
        )


@dataclass
class SubtitleCue:
    """
    Standard Cue Model conforming to ARO Master Spec 04.
    Timing is strictly in milliseconds.
    """
    cue_id: str = field(default_factory=generate_uuid)
    revision: int = 1
    start_ms: int = 0
    end_ms: int = 0
    source_text: str = ""
    translated_text: str = ""
    tts_text: str = ""
    kind: str = "dialogue"  # dialogue, narration, sign, song, unknown
    source_method: str = "asr"  # asr, ocr, embedded_text, imported, manual
    source_confidence_milli: int = 900
    speaker_id: Optional[str] = None
    listener_id: Optional[str] = None
    character_id: Optional[str] = None
    voice_assignment_id: Optional[str] = None
    required_translation: bool = True
    required_tts: bool = True
    text_locked: bool = False
    timing_locked: bool = False
    source_evidence_ids: List[str] = field(default_factory=list)
    words: List[WordTimestamp] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    parent_cue_ids: List[str] = field(default_factory=list)

    @property
    def duration_ms(self) -> int:
        return max(0, self.end_ms - self.start_ms)

    def to_dict(self) -> Dict[str, Any]:
        res = asdict(self)
        res["words"] = [w.to_dict() if isinstance(w, WordTimestamp) else w for w in self.words]
        return res

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SubtitleCue:
        words_data = data.get("words", [])
        words = [WordTimestamp.from_dict(w) if isinstance(w, dict) else w for w in words_data]
        return cls(
            cue_id=str(data.get("cue_id", generate_uuid())),
            revision=int(data.get("revision", 1)),
            start_ms=int(data.get("start_ms", 0)),
            end_ms=int(data.get("end_ms", 0)),
            source_text=str(data.get("source_text", "")),
            translated_text=str(data.get("translated_text", "")),
            tts_text=str(data.get("tts_text", "")),
            kind=str(data.get("kind", "dialogue")),
            source_method=str(data.get("source_method", "asr")),
            source_confidence_milli=int(data.get("source_confidence_milli", 900)),
            speaker_id=data.get("speaker_id"),
            listener_id=data.get("listener_id"),
            character_id=data.get("character_id"),
            voice_assignment_id=data.get("voice_assignment_id"),
            required_translation=bool(data.get("required_translation", True)),
            required_tts=bool(data.get("required_tts", True)),
            text_locked=bool(data.get("text_locked", False)),
            timing_locked=bool(data.get("timing_locked", False)),
            source_evidence_ids=list(data.get("source_evidence_ids", [])),
            words=words,
            flags=list(data.get("flags", [])),
            parent_cue_ids=list(data.get("parent_cue_ids", [])),
        )


@dataclass
class AudioChunk:
    """Spec 04 & Spec 09 audio chunk for ASR with core & overlap boundaries."""
    chunk_id: str
    chunk_index: int
    core_start_ms: int
    core_end_ms: int
    decode_start_ms: int
    decode_end_ms: int
    audio_path: str
    sha256: str
    sample_rate: int = 16000
    channel_count: int = 1


@dataclass
class TtsCueResult:
    """Spec 04 & Spec 07 TTS synthesis & tempo-fit result for a single cue."""
    cue_id: str
    cue_revision: int
    effective_text: str
    text_sha256: str
    requested_voice: str
    actual_voice: str
    raw_audio_path: str
    fit_audio_path: Optional[str]
    measured_ms: int
    available_ms: int
    tempo_milli: int  # 1000 = 1.0x, 1150 = 1.15x
    rewrite_attempts: int = 0
    status: str = "VALID"  # VALID, NEEDS_REVIEW, FAILED
    reason: Optional[str] = None
    fit_key: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MediaProbeInfo:
    """Spec 04 MediaProbe container inspection."""
    source_sha256: str
    duration_ms: int
    format_name: str
    video_stream_index: int
    width_encoded: int
    height_encoded: int
    rotation_deg: int
    display_width: int
    display_height: int
    avg_fps: float
    has_audio: bool
    audio_stream_index: Optional[int] = None
    audio_codec: Optional[str] = None
    audio_sample_rate: Optional[int] = None
    audio_channels: Optional[int] = None
    subtitle_streams_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PipelineConfig:
    """Configuration options for ARO pipeline matching Spec 04 Section 7."""
    # Video / Render
    output_width: int = 1920
    output_height: int = 1080
    video_codec: str = "libx264"
    video_preset: str = "medium"
    video_crf: int = 20
    use_nvenc: bool = False
    
    # Audio / Ducking
    audio_mode: str = "duck_original"  # duck_original, separate_or_duck
    background_gain_db: float = -15.0   # Hạ 82% nhạc gốc (~ -15 dB)
    duck_threshold_db: float = -26.0
    duck_ratio: float = 4.0
    duck_attack_ms: int = 20
    duck_release_ms: int = 250
    target_lufs: float = -16.0
    true_peak_db: float = -1.5
    
    # TTS
    tts_primary_voice_female: str = "vi-VN-HoaiMyNeural"
    tts_primary_voice_male: str = "vi-VN-NamMinhNeural"
    max_tempo_ratio: float = 1.25
    min_tempo_ratio: float = 1.0
    
    # Translation & Genre
    genre: str = "xianxia"  # xianxia, wuxia, historical, transmigration, modern, neutral
    translation_batch_size: int = 24
    
    # ASR
    asr_chunk_target_ms: int = 30000
    asr_chunk_max_ms: int = 45000
    asr_overlap_ms: int = 1000
    whisper_model: str = "whisper-large-v3"

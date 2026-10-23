import sys
import json
from pathlib import Path

# Add backend_worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend_worker"))

from backend_worker.models import PipelineConfig
from backend_worker.pipeline import MediaPipeline

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python pipeline.py <source_video> <voice_track.wav> <subtitles.ass> <output.mp4>")
        sys.exit(1)

    src_v = sys.argv[1]
    voice_w = sys.argv[2]
    ass_s = sys.argv[3]
    out_v = sys.argv[4]

    pipe = MediaPipeline()
    p_info = pipe.probe_media(src_v)
    print(f"Source probed: {p_info.duration_ms}ms, {p_info.display_width}x{p_info.display_height}")

    master_audio = "master_audio.wav"
    pipe.mix_audio_ducking_with_loudnorm(src_v, voice_w, master_audio, p_info.duration_ms)
    pipe.render_final_video(src_v, master_audio, ass_s, out_v)
    val = pipe.validate_final_output(out_v)
    print(f"Validation report: {json.dumps(val, indent=2)}")

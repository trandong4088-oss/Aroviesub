import sys
from pathlib import Path

# Add backend_worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend_worker"))

from backend_worker.transcriber import AudioTranscriber

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcriber.py <input_video_or_wav> [output_cues.json]")
        sys.exit(1)

    video_input = sys.argv[1]
    out_json = sys.argv[2] if len(sys.argv) > 2 else "source_cues.json"
    
    transcriber = AudioTranscriber()
    res_cues = transcriber.process(video_input, out_json)
    print(f"Done! Transcribed {len(res_cues)} cues.")

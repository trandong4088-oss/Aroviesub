import sys
import json
from pathlib import Path

# Add backend_worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend_worker"))

from backend_worker.models import SubtitleCue
from backend_worker.tts_dubbing import TtsDubbingEngine

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

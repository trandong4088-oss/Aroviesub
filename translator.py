import sys
import json
from pathlib import Path

# Add backend_worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend_worker"))

from backend_worker.models import SubtitleCue
from backend_worker.translator import DonghuaTranslator, TranslationMemoryStore

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translator.py <input_cues.json> [output_translated.json]")
        sys.exit(1)

    in_file = sys.argv[1]
    out_file = sys.argv[2] if len(sys.argv) > 2 else "translated_cues.json"

    with open(in_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cues_list = [SubtitleCue.from_dict(d) for d in data]
    translator = DonghuaTranslator()
    res = translator.process(cues_list)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in res], f, ensure_ascii=False, indent=2)
    print(f"Saved translated cues to {out_file}")

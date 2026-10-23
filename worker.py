import sys
from pathlib import Path

# Add backend_worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend_worker"))

from backend_worker.worker import AroWorker, parse_cli_args

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

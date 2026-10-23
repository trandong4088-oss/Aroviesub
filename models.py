import sys
from pathlib import Path

# Add backend_worker directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "backend_worker"))

from backend_worker.models import *

if __name__ == "__main__":
    print("ARO Models Module loaded successfully.")

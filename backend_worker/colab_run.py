"""
Google Colab Automated Setup & Runner Script for ARO Master Worker
Run this script inside Google Colab or Kaggle GPU environments.
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_colab_environment():
    print("=" * 60)
    print("ARO MASTER - GOOGLE COLAB ENVIRONMENT BOOTSTRAP")
    print("=" * 60)

    # 1. Check GPU
    try:
        res = subprocess.run(["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print("[GPU Detected]:\n" + "\n".join(res.stdout.splitlines()[:10]))
        else:
            print("[INFO] Running in CPU mode. NVENC hardware encoding disabled.")
    except Exception:
        print("[INFO] No nvidia-smi found. Running on CPU.")

    # 2. Check & Install FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("[FFmpeg]: Available.")
    except Exception:
        print("[FFmpeg]: Installing via apt-get...")
        subprocess.run(["apt-get", "update", "-qq"], check=True)
        subprocess.run(["apt-get", "install", "-y", "-qq", "ffmpeg"], check=True)

    # 3. Install Python requirements
    print("[PIP]: Installing edge-tts, faster-whisper...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts>=6.1.12", "faster-whisper>=1.0.3", "pydantic>=2.7.0"], check=True)
    print("[Environment]: Ready!")


if __name__ == "__main__":
    setup_colab_environment()

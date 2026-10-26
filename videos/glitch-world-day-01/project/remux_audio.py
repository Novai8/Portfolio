#!/usr/bin/env python3
"""
remux_audio.py — swap the mix into an already-rendered picture without re-encoding.

The video stream is copied bit-for-bit, so iterating on the sound design costs
seconds instead of another 17-minute render.

    python3 project/build_audio.py
    python3 project/remux_audio.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine as E

ROOT = E.ROOT
VIDEO = os.path.join(ROOT, "final", "glitch-world-day-01.mp4")
MIX = os.path.join(ROOT, ".work", "mix.wav")
TMP = os.path.join(ROOT, ".work", "remux.mp4")


def main():
    if not (os.path.exists(VIDEO) and os.path.exists(MIX)):
        raise SystemExit("missing final video or mix")
    subprocess.run([E.ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
                    "-i", VIDEO, "-i", MIX,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-shortest", "-movflags", "+faststart", TMP], check=True)
    shutil.move(TMP, VIDEO)
    print("remuxed audio ->", VIDEO, E.probe(VIDEO))


if __name__ == "__main__":
    main()

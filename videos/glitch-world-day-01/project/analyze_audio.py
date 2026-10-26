#!/usr/bin/env python3
"""
analyze_audio.py — measure the real voiceover and extract its speech rhythm.

The recording is the authoritative timing source for the whole edit, so this
script produces machine-readable timing data (duration, speech segments,
pauses) that the renderer and the subtitle builder both consume.

Usage:
    python3 project/analyze_audio.py

Outputs:
    scripts/audio-analysis.json   duration / sr / channels / segments / pauses
    previews/waveform.png         visual reference of the recording
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_MP3 = os.path.join(ROOT, "audio", "original-voiceover.mp3")
WORK = os.path.join(ROOT, ".work")
WAV = os.path.join(WORK, "vo-48k.wav")
OUT_JSON = os.path.join(ROOT, "scripts", "audio-analysis.json")
OUT_PNG = os.path.join(ROOT, "previews", "waveform.png")


def ffmpeg_path() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path: str) -> dict:
    """Read stream info out of ffmpeg's banner (no ffprobe in this image)."""
    proc = subprocess.run(
        [ffmpeg_path(), "-hide_banner", "-i", path],
        capture_output=True, text=True,
    )
    info = {}
    for line in proc.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            info["duration_s"] = int(h) * 3600 + int(m) * 60 + float(s)
        if "Audio:" in line:
            info["audio_stream"] = line.split("Audio:")[1].strip()
    return info


def decode_to_wav(src: str, dst: str, sr: int = 48000) -> None:
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    subprocess.run(
        [ffmpeg_path(), "-y", "-hide_banner", "-loglevel", "error",
         "-i", src, "-ac", "1", "-ar", str(sr), "-c:a", "pcm_s16le", dst],
        check=True,
    )


def read_wav(path: str):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        n = w.getnframes()
        raw = w.readframes(n)
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)
    return data, sr, ch


def speech_segments(x: np.ndarray, sr: int) -> tuple[list[dict], np.ndarray, float]:
    """Adaptive energy gate -> speech segments and pauses."""
    hop = int(0.010 * sr)  # 10 ms
    win = int(0.025 * sr)  # 25 ms
    n_frames = max(1, (len(x) - win) // hop)
    idx = np.arange(n_frames)[:, None] * hop + np.arange(win)[None, :]
    frames = x[idx]
    rms = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)

    # Noise floor from the quietest 15% of frames, speech level from the loud tail.
    floor = float(np.percentile(db, 15))
    loud = float(np.percentile(db, 92))
    thr = floor + max(6.0, (loud - floor) * 0.22)
    active = db > thr

    # Close tiny gaps (<180 ms) so a sentence is not shattered by stop consonants.
    close_gap = int(0.18 / 0.010)
    i = 0
    while i < len(active):
        if not active[i]:
            j = i
            while j < len(active) and not active[j]:
                j += 1
            if i > 0 and j < len(active) and (j - i) < close_gap:
                active[i:j] = True
            i = j
        else:
            i += 1

    # Drop very short blips (<120 ms of speech) as breath/click noise.
    min_len = int(0.12 / 0.010)
    segments: list[dict] = []
    i = 0
    while i < len(active):
        if active[i]:
            j = i
            while j < len(active) and active[j]:
                j += 1
            if (j - i) >= min_len:
                segments.append({
                    "start": round(i * 0.010, 3),
                    "end": round(min(len(x) / sr, j * 0.010 + win / sr), 3),
                    "peak_db": round(float(db[i:j].max()), 1),
                })
            i = j
        else:
            i += 1

    for s in segments:
        s["dur"] = round(s["end"] - s["start"], 3)

    pauses = []
    for a, b in zip(segments, segments[1:]):
        gap = round(b["start"] - a["end"], 3)
        if gap >= 0.20:
            pauses.append({"start": a["end"], "end": b["start"], "dur": gap})
    return segments, db, thr


def envelope_png(db: np.ndarray, sr: float, segments: list[dict], path: str, duration: float):
    from PIL import Image, ImageDraw

    W, H = 1080, 420
    img = Image.new("RGB", (W, H), (10, 12, 24))
    d = ImageDraw.Draw(img)
    top, bot = 40, H - 40
    for k in range(0, int(duration) + 1, 5):
        x = int(k / duration * W)
        d.line([(x, top), (x, bot)], fill=(30, 34, 58))
        d.text((x + 3, 10), f"{k}s", fill=(120, 140, 190))
    n = len(db)
    mid = (top + bot) / 2
    scale = (bot - top) / 2 / max(1.0, float(np.max(np.abs(db - np.median(db)))))
    for i in range(n):
        x = int(i / n * W)
        y = mid - (db[i] - float(np.median(db))) * scale
        d.line([(x, mid), (x, y)], fill=(0, 220, 255))
    for s in segments:
        x0 = int(s["start"] / duration * W)
        x1 = max(x0 + 1, int(s["end"] / duration * W))
        d.rectangle([x0, bot + 6, x1, bot + 16], fill=(255, 60, 160))
    img.save(path)
    return path


def main() -> int:
    if not os.path.exists(SRC_MP3):
        print("missing source audio:", SRC_MP3, file=sys.stderr)
        return 1
    meta = probe(SRC_MP3)
    decode_to_wav(SRC_MP3, WAV)
    x, sr, ch = read_wav(WAV)
    duration = len(x) / sr
    segments, db, thr = speech_segments(x, sr)

    speech_total = sum(s["dur"] for s in segments)
    result = {
        "source_file": os.path.relpath(SRC_MP3, ROOT),
        "source_container": "MP3 (128 kbps, mono, 44.1 kHz as delivered)",
        "measured_duration_s": round(duration, 3),
        "measured_duration_hms": f"{int(duration // 60)}:{duration % 60:05.2f}",
        "decode_sample_rate": sr,
        "decode_channels": ch,
        "peak_db": round(float(20 * np.log10(np.max(np.abs(x)) + 1e-9)), 2),
        "rms_db": round(float(20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)), 2),
        "silence_threshold_db": round(thr, 1),
        "speech_segment_count": len(segments),
        "speech_total_s": round(speech_total, 3),
        "segments": segments,
        "pauses": [
            {"start": a["end"], "end": b["start"], "dur": round(b["start"] - a["end"], 3)}
            for a, b in zip(segments, segments[1:]) if b["start"] - a["end"] >= 0.2
        ],
        "ffmpeg_probe": meta,
    }
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(result, f, indent=2)
    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    envelope_png(db, sr, segments, OUT_PNG, duration)

    print(f"duration      : {result['measured_duration_hms']} ({duration:.3f}s)")
    print(f"speech segs   : {len(segments)}  speech time {speech_total:.2f}s")
    print(f"pauses >=200ms: {len(result['pauses'])}")
    print(f"peak / rms dB : {result['peak_db']} / {result['rms_db']}")
    print("wrote", os.path.relpath(OUT_JSON, ROOT), "and", os.path.relpath(OUT_PNG, ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

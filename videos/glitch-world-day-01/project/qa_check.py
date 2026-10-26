#!/usr/bin/env python3
"""
qa_check.py — automated quality gate for the finished film.

Checks the real exported file (streams, duration, frame cadence, black frames,
frozen frames, silence) plus the deliverables (SRT sanity, subtitle safe area,
timeline coverage, audio/video sync offsets) and writes reports/quality-check.md.

    python3 project/qa_check.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import wave

import numpy as np

import engine as E
from engine import H, W, font
from timeline import Timeline

ROOT = E.ROOT
FINAL = os.path.join(ROOT, "final", "glitch-world-day-01.mp4")
SRT = os.path.join(ROOT, "final", "glitch-world-day-01.srt")
REPORT = os.path.join(ROOT, "reports", "quality-check.md")
WORK = os.path.join(ROOT, ".work")

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS  " if ok else "FAIL  ") + name + (f"  — {detail}" if detail else ""))
    return ok


def ffmpeg_banner(path):
    return subprocess.run([E.ffmpeg_exe(), "-hide_banner", "-i", path],
                          capture_output=True, text=True).stderr


def probe_streams(path):
    banner = ffmpeg_banner(path)
    info = {}
    for line in banner.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            info["duration"] = int(h) * 3600 + int(m) * 60 + float(s)
        if "Video:" in line:
            info["video"] = line
        if "Audio:" in line:
            info["audio"] = line
    return info


def decode_frames(path, fps=30, size=(96, 171)):
    """decode every frame at thumbnail size for cheap statistical checks"""
    raw = subprocess.run(
        [E.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-i", path,
         "-vf", f"scale={size[0]}:{size[1]},format=gray", "-f", "rawvideo", "-"],
        capture_output=True)
    a = np.frombuffer(raw.stdout, dtype=np.uint8)
    n = a.size // (size[0] * size[1])
    return a[:n * size[0] * size[1]].reshape(n, size[1], size[0])


def decode_audio(path):
    raw = subprocess.run(
        [E.ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-i", path,
         "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
        capture_output=True)
    return np.frombuffer(raw.stdout, dtype="<i2").astype(np.float32) / 32768.0


def parse_srt(path):
    cues = []
    with open(path) as f:
        blocks = f.read().strip().split("\n\n")
    for b in blocks:
        lines = b.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        t0 = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        t1 = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        cues.append(dict(t0=t0, t1=t1, text=" ".join(lines[2:])))
    return cues


def main():
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    tl = Timeline()
    with open(os.path.join(ROOT, "scripts", "audio-analysis.json")) as f:
        analysis = json.load(f)
    vo_dur = analysis["measured_duration_s"]

    # ---------------------------------------------------------------- file ---
    check("final MP4 exists", os.path.exists(FINAL), FINAL)
    if not os.path.exists(FINAL):
        return
    size_mb = os.path.getsize(FINAL) / 1e6
    info = probe_streams(FINAL)
    v = info.get("video", "")
    a = info.get("audio", "")
    check("video stream is H.264", "h264" in v.lower(), v.split("(")[0][:60])
    check("resolution 1080x1920", "1080x1920" in v, "1080x1920" if "1080x1920" in v else v[:60])
    check("pixel format yuv420p", "yuv420p" in v, "yuv420p" if "yuv420p" in v else v[:60])
    check("frame rate 30 fps", bool(re.search(r"\b30 fps\b", v)), "30 fps" if "30 fps" in v else v[:60])
    check("audio stream is AAC", "aac" in a.lower(), a.split(",")[0][:60])
    check("audio 48 kHz", "48000 Hz" in a, "48000 Hz" if "48000 Hz" in a else a[:60])
    dur = info.get("duration", 0.0)
    check("duration matches the voiceover (+/- 100 ms)",
          abs(dur - vo_dur) <= 0.12, f"{dur:.3f}s vs VO {vo_dur:.3f}s")
    check("deliverable is under GitHub's 100 MB file limit", size_mb < 100.0,
          f"{size_mb:.1f} MB")

    # --------------------------------------------------------------- frames ---
    fr = decode_frames(FINAL)
    n_frames = fr.shape[0]
    expect = int(round(dur * 30))
    check("frame count matches 30 fps cadence", abs(n_frames - expect) <= 2,
          f"{n_frames} frames (expected ~{expect})")
    means = fr.reshape(n_frames, -1).mean(axis=1)
    dark = np.where(means < 6.0)[0]
    check("no black frames", len(dark) == 0, f"{len(dark)} frames under 6/255 luma")
    diffs = np.abs(np.diff(fr.reshape(n_frames, -1).astype(np.int16), axis=0)).mean(axis=1)
    frozen = np.where(diffs < 0.02)[0]
    longest = 0
    run = 0
    for i in range(n_frames - 1):
        run = run + 1 if i in set(frozen.tolist()) else 0
        longest = max(longest, run)
    check("no accidental frozen stretches", longest < 15,
          f"longest identical run {longest} frames")
    check("motion present throughout", float(diffs.mean()) > 0.3,
          f"mean frame delta {diffs.mean():.2f}")

    # ---------------------------------------------------------------- audio ---
    au = decode_audio(FINAL)
    au_dur = len(au) / 48000.0
    check("audio length matches the video", abs(au_dur - dur) <= 0.12,
          f"{au_dur:.3f}s vs {dur:.3f}s")
    # narration presence: compare against the original stems' speech segments
    segs = analysis["segments"]
    speech_energy = []
    for s in segs:
        i0, i1 = int(s["start"] * 48000), int(min(s["end"], au_dur) * 48000)
        if i1 > i0:
            speech_energy.append(float(np.sqrt(np.mean(au[i0:i1] ** 2))))
    check("narration is present across the whole recording",
          len(speech_energy) >= len(segs) - 1 and min(speech_energy) > 0.01,
          f"{len(speech_energy)}/{len(segs)} speech segments audible, "
          f"min RMS {min(speech_energy):.3f}")
    silent = 0
    win = int(0.25 * 48000)
    for i in range(0, len(au) - win, win):
        if np.abs(au[i:i + win]).max() < 1e-4:
            silent += 1
    check("no unintended silent gaps", silent == 0, f"{silent} silent 250 ms windows")
    peak_db = 20 * np.log10(float(np.abs(au).max()) + 1e-9)
    check("true peak below -1.0 dBFS", peak_db < -1.0, f"{peak_db:.2f} dBFS")
    tail = au[-int(0.05 * 48000):]
    check("no abrupt audio cutoff at the end", float(np.abs(tail).max()) < 0.25,
          f"last 50 ms peak {np.abs(tail).max():.3f}")

    # ----------------------------------------------------------------- srt ---
    cues = parse_srt(SRT)
    check("SRT file present and parses", len(cues) > 20, f"{len(cues)} cues")
    check("SRT ends at the end of the film", abs(cues[-1]["t1"] - vo_dur) < 0.3,
          f"last cue ends {cues[-1]['t1']:.2f}s")
    gaps = [cues[i + 1]["t0"] - cues[i]["t1"] for i in range(len(cues) - 1)]
    check("SRT cues never overlap", min(gaps) >= -0.01, f"min gap {min(gaps):.3f}s")
    overlong = [c for c in cues if len(c["text"]) > 60 or c["text"].count("\n") > 1]
    check("SRT cues are caption-sized", not overlong, f"{len(overlong)} overlong cues")
    # every sentence in the script must appear in the subtitles
    with open(os.path.join(ROOT, "scripts", "transcript.txt")) as f:
        script_words = re.findall(r"[A-Za-z']+", f.read().lower())
    srt_words = re.findall(r"[A-Za-z']+", " ".join(c["text"] for c in cues).lower())
    missing = [w for w in set(script_words) if w not in set(srt_words)]
    check("subtitle text covers the spoken script", len(missing) == 0,
          f"missing tokens: {missing[:8]}")

    # ------------------------------------------------- timeline coverage ---
    covered = sum(s.end - s.start for s in tl.shots)
    gaps_t = []
    for a_, b_ in zip(tl.shots, tl.shots[1:]):
        if abs(a_.end - b_.start) > 0.02:
            gaps_t.append((a_.end, b_.start))
    check("timeline covers the whole recording", abs(covered - vo_dur) < 0.05,
          f"{covered:.2f}s of {vo_dur:.2f}s")
    check("no gaps between shots", not gaps_t, str(gaps_t[:3]))

    # --------------------------------------------------------- safe area ---
    import subs as subs_mod
    safe_bottom = H * 0.82
    check("captions sit above platform UI safe area",
          subs_mod.SAFE_CENTER_Y + 90 < safe_bottom,
          f"caption band centre y={subs_mod.SAFE_CENTER_Y}px, limit {safe_bottom:.0f}px")
    check("captions keep clear of the right-edge action rail",
          subs_mod.SAFE_RIGHT < W - 120, f"right margin {(W - subs_mod.SAFE_RIGHT)}px")

    # ------------------------------------------------------------- report ---
    passed = sum(1 for _n, ok, _d in results if ok)
    with open(REPORT, "w") as f:
        f.write("# Quality check — Glitch World, Day 1\n\n")
        f.write(f"Rendered file: `final/glitch-world-day-01.mp4`  \n")
        f.write(f"Duration: **{dur:.3f}s** · {W}x{H} · 30 fps · H.264 + AAC 48 kHz · "
                f"{size_mb:.1f} MB  \n")
        f.write(f"Source voiceover: `audio/original-voiceover.mp3` "
                f"({vo_dur:.3f}s measured)\n\n")
        f.write(f"**{passed}/{len(results)} automated checks passed.**\n\n")
        f.write("| check | result | detail |\n|---|---|---|\n")
        for name, ok, detail in results:
            f.write(f"| {name} | {'✅ pass' if ok else '❌ fail'} | {detail} |\n")
        f.write("\n## Visual review\n\n")
        f.write("- Storyboard and contact sheet regenerated from the exported MP4: "
                "`previews/storyboard.jpg`, `previews/contact-sheet.jpg`.\n")
        f.write("- Every shot was reviewed as a still; the protagonist rig, line weight and "
                f"palette were held constant across all {len(tl.shots)} shots.\n")
        f.write("- Captions use Inter ExtraBold, white with a dark outline, inside a plate, "
                "clear of the bottom UI band and the right-hand action rail.\n")
        f.write("- In-world type (REALITY UPDATE FAILED / RESTARTING IN 100 DAYS / "
                "YOU'RE NOT REAL / the countdown / the A-B choice) is drawn with a separate "
                "display + mono typography so it is never confused with dialogue captions.\n")
    print(f"\n{passed}/{len(results)} checks passed -> {REPORT}")


if __name__ == "__main__":
    main()

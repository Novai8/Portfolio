#!/usr/bin/env python3
"""
build_timeline.py — writes scripts/scene-timeline.json.

Shots are snapped to the *sentence boundaries* measured from the recording
(scripts/sentences.json), and camera keys are authored in absolute seconds so
the edit stays readable against the transcript. Retime by changing the times
here, re-running this script, then re-rendering.

    python3 project/build_subs.py        # sentence timings (run first)
    python3 project/build_timeline.py
"""
from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO = os.path.join(ROOT, "scripts", "audio-analysis.json")
SENTS = os.path.join(ROOT, "scripts", "sentences.json")
OUT = os.path.join(ROOT, "scripts", "scene-timeline.json")


# world-space ground line per set (must match scenes.py)
FLOOR = dict(bedroom=70, hallway=70, door=76, store=74, cityfail=84, chicken=84,
             celebrate=84, stranger=90, countdown=96, choice=74)


def cam(shot_start, shot_end, keys, scene):
    """
    absolute-second camera keys -> fractions of the shot.
    keys are (t, cx, zoom, ground_px): the vertical camera position is solved so
    the set's ground line lands on ground_px, which keeps every shot composed the
    same way and leaves the lower frame clear for captions.
    """
    fy = FLOOR[scene]
    out = []
    for t, cx, z, ground_px in keys:
        cy = fy - (ground_px - 960.0) / z
        f = 0.0 if shot_end == shot_start else (t - shot_start) / (shot_end - shot_start)
        out.append([round(max(0.0, min(1.0, f)), 4), round(cx, 2), round(cy, 2), round(z, 3)])
    if out[0][0] > 0.0:
        out.insert(0, [0.0, out[0][1], out[0][2], out[0][3]])
    if out[-1][0] < 1.0:
        out.append([1.0, out[-1][1], out[-1][2], out[-1][3]])
    return out


# ---------------------------------------------------------------- shot list ---
# camera keys: (t, centre_x, zoom, ground_line_px)
SHOTS = [
    dict(scene="bedroom", start=0.00, end=9.67, shake=1.2,
         note="cold open - alarm, backward bird, rain falling up",
         keys=[(0.00, 150, 5.6, 1300), (1.60, 128, 5.2, 1290), (3.20, 30, 4.6, 1280),
               (4.90, -66, 6.0, 1290), (6.60, -70, 7.0, 1320), (7.30, -74, 7.6, 1340),
               (9.67, -84, 8.2, 1360)]),
    dict(scene="hallway", start=9.67, end=18.04, shake=0.8,
         note="the frozen neighbour - leg inside the wall",
         params=dict(mode="neighbour"),
         keys=[(9.67, 40, 5.2, 1180), (12.00, 130, 6.0, 1210), (14.60, 200, 7.0, 1250),
               (16.20, -150, 7.4, 1290), (18.04, -150, 8.0, 1320)]),
    dict(scene="door", start=18.04, end=28.13, shake=1.0,
         note="the front door: ocean, slam, grocery store",
         keys=[(18.04, -70, 3.4, 1240), (20.40, 16, 3.2, 1230), (22.60, 14, 3.2, 1230),
               (23.10, -110, 5.8, 1260), (24.60, 12, 3.3, 1235), (26.20, 12, 3.2, 1230),
               (28.13, 8, 3.6, 1250)]),
    dict(scene="store", start=28.13, end=38.66, shake=0.6,
         note="products with his face - 'Even the milk'",
         keys=[(28.13, -50, 3.1, 1210), (30.46, 2, 2.75, 1200), (31.90, 6, 2.70, 1195),
               (34.20, -34, 2.95, 1210), (36.91, -74, 3.05, 1220), (38.66, -84, 3.20, 1230)]),
    dict(scene="cityfail", start=38.66, end=50.71, shake=2.2,
         note="noon - REALITY UPDATE FAILED, then everyone freezes",
         keys=[(38.66, -44, 3.9, 1150), (41.00, -40, 3.7, 1140), (43.95, -18, 3.5, 1120),
               (45.90, 0, 3.2, 1110), (47.60, 0, 3.5, 1120), (50.71, 8, 4.0, 1150)]),
    dict(scene="chicken", start=50.71, end=62.07, shake=1.3,
         note="the frozen officer, then the rock that becomes a chicken",
         params=dict(throw=0.62, hatch=0.74),
         keys=[(50.71, -55, 4.6, 1300), (52.60, -50, 4.4, 1290), (54.40, -45, 4.4, 1290),
               (56.60, -25, 4.2, 1290), (58.20, 40, 3.9, 1280), (59.60, 60, 4.0, 1290),
               (62.07, 60, 4.1, 1290)]),
    dict(scene="celebrate", start=62.07, end=69.27, shake=1.0,
         note="'world's most powerful idiot' - then he notices someone across the street",
         keys=[(62.07, -20, 3.9, 1280), (63.60, 30, 3.4, 1240), (65.20, 80, 3.1, 1210),
               (67.20, 120, 2.95, 1190), (69.27, 130, 2.9, 1180)]),
    dict(scene="stranger", start=69.27, end=81.13, shake=1.0,
         note="the second stickman: YOU'RE NOT REAL",
         params=dict(point=0.30, panel=(0.72, 0.88), vanish=0.86),
         keys=[(69.27, 0, 2.8, 1150), (72.76, -30, 2.75, 1140), (75.00, -20, 2.8, 1140),
               (77.89, -10, 3.1, 1150), (81.13, -20, 2.95, 1140)]),
    dict(scene="countdown", start=81.13, end=90.84, shake=0.7,
         note="the countdown appears: 99 days, 23 hours, 59 minutes",
         keys=[(81.13, 0, 3.4, 1150), (83.52, 0, 3.3, 1150), (86.00, 0, 3.2, 1160),
               (90.84, 0, 3.1, 1160)]),
    dict(scene="choice", start=90.84, end=100.72, shake=0.6,
         note="who created this world? - the two paths",
         keys=[(90.84, -10, 2.95, 1150), (94.69, -4, 2.90, 1135), (98.80, 0, 2.85, 1120),
               (100.72, 0, 2.80, 1105)]),
    dict(scene="choice", start=100.72, end=113.79, shake=0.5,
         note="A or B - choose carefully",
         params=dict(cards=True, a_at=100.9, b_at=105.4),
         keys=[(100.72, -30, 2.52, 1090), (104.00, -30, 2.58, 1075), (108.67, -30, 2.64, 1060),
               (110.40, -30, 2.72, 1050), (113.79, -30, 2.80, 1044)]),
]


OVERLAYS = [
    dict(start=0.25, end=3.40, style="stamp", text="DAY 1", sub="the world is broken",
         y=330, color=(0, 232, 255), fade=0.45),
]


def main():
    with open(AUDIO) as f:
        a = json.load(f)
    duration = a["measured_duration_s"]
    with open(SENTS) as f:
        sents = json.load(f)["sentences"]

    shots = []
    for s in SHOTS:
        shots.append(dict(
            scene=s["scene"], start=round(s["start"], 3), end=round(min(s["end"], duration), 3),
            note=s["note"], shake=s.get("shake", 0.0),
            params=s.get("params", {}),
            camera=cam(s["start"], s["end"], s["keys"], s["scene"]),
        ))
    data = dict(
        title="100 Days Trapped in a Glitched World — Day 1: THE WORLD IS BROKEN",
        fps=30, width=1080, height=1920,
        duration=round(duration, 3),
        voiceover=dict(file="audio/original-voiceover.mp3", duration=round(duration, 3),
                       note="the recording is the timing authority; shots snap to its sentences"),
        shots=shots,
        overlays=OVERLAYS,
        sentences=[dict(t0=s["t0"], t1=s["t1"], text=s["text"]) for s in sents],
    )
    with open(OUT, "w") as f:
        json.dump(data, f, indent=2)
    print(f"wrote {OUT}: {len(shots)} shots, {duration:.3f}s")
    for s in shots:
        print(f"  {s['start']:7.2f} -> {s['end']:7.2f}  {s['scene']:10s} {s['note']}")


if __name__ == "__main__":
    main()

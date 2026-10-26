"""
timeline.py — the edit decision list.

scripts/scene-timeline.json is the single source of truth for what happens
when. Times are absolute seconds into the finished film (the voiceover is the
clock). Camera keyframes are stored as *fractions* of each shot so a shot can be
retimed without re-authoring its camera move.

Edit scripts/scene-timeline.json (or regenerate with build_timeline.py) and
re-render — nothing else needs to change.
"""
from __future__ import annotations

import json
import math
import os

import engine as E
from engine import Cam, clamp, ease, lerp, shake_offset

ROOT = E.ROOT
TL_PATH = os.path.join(ROOT, "scripts", "scene-timeline.json")
AUDIO_PATH = os.path.join(ROOT, "scripts", "audio-analysis.json")


class Shot:
    def __init__(self, d):
        self.start = float(d["start"])
        self.end = float(d["end"])
        self.scene = d["scene"]
        self.params = d.get("params", {}) or {}
        self.keys = [(float(k[0]), (float(k[1]), float(k[2]), float(k[3])))
                     for k in d.get("camera", [[0, 0, 0, 5], [1, 0, 0, 5]])]
        self.shake_amp = float(d.get("shake", 0.0))
        self.note = d.get("note", "")

    @property
    def dur(self):
        return self.end - self.start

    def camera_at(self, t):
        f = clamp((t - self.start) / max(1e-6, self.dur))
        cx, cy, z = self.keys[0][1]
        if f >= self.keys[-1][0]:
            cx, cy, z = self.keys[-1][1]
        else:
            for (f0, v0), (f1, v1) in zip(self.keys, self.keys[1:]):
                if f <= f1:
                    e = ease(clamp((f - f0) / max(1e-6, f1 - f0)), "inout")
                    cx, cy, z = (lerp(v0[0], v1[0], e), lerp(v0[1], v1[1], e),
                                 lerp(v0[2], v1[2], e))
                    break
        sx, sy = shake_offset(t, self.shake_amp, 24.0, seed=int(self.start * 1000))
        return Cam(cx, cy, z, shake=(sx, sy))


class Timeline:
    def __init__(self, path=TL_PATH):
        with open(path) as f:
            data = json.load(f)
        self.raw = data
        self.title = data.get("title", "")
        self.shots = [Shot(s) for s in data["shots"]]
        self.duration = float(data.get("duration") or self.shots[-1].end)
        self.voiceover = data.get("voiceover", {})
        self.cues = []
        cues_path = os.path.join(ROOT, "scripts", "subtitles.json")
        if os.path.exists(cues_path):
            with open(cues_path) as f:
                self.cues = json.load(f).get("cues", [])
        self.overlays = data.get("overlays", [])

    def shot_at(self, t):
        for s in self.shots:
            if s.start <= t < s.end:
                return s
        if self.shots and t >= self.shots[-1].end:
            return None
        return self.shots[0] if self.shots else None

    def cue_at(self, t, hold=0.0):
        for c in self.cues:
            if c["start"] - 0.001 <= t <= c["end"] + hold:
                return c
        return None

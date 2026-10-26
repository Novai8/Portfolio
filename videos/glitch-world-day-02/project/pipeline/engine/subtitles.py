"""Subtitle cue loading and burn-in, synchronized to the measured voiceover."""
import json, os
from . import config as C
from . import draw as D

# Cues rendered physically in-world instead of as captions:
#  9 STOP LOOKING FOR ME, 12 LOOK UP (carved wall), 36/37 (choice cards)
SUPPRESS = {9, 12, 36, 37}

class Subtitles:
    def __init__(self, timing_path):
        with open(timing_path) as f:
            data = json.load(f)
        self.cues = data["sentences"]
        self.duration = data["measured_duration_s"]

    def active(self, t):
        for c in self.cues:
            if c["index"] in SUPPRESS:
                continue
            if c["start"] <= t <= c["end"]:
                return c
        return None

    def burn(self, img, t, y=None, size=44):
        c = self.active(t)
        if not c:
            return img
        y = C.SUB_Y if y is None else y
        D.draw_text(img, (C.W / 2, y), c["text"], size=size, kind="sans",
                    weight="SemiBold", fill=C.WHITE, outline=(5, 7, 15),
                    outline_w=5, shadow=True, max_width=C.W - 2 * C.SAFE_X,
                    line_spacing=1.22)
        return img

    def write_srt(self, path):
        def ts(t):
            h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
            return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
        out = []
        n = 1
        for c in self.cues:
            if c["index"] in SUPPRESS:
                continue
            out.append(f"{n}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n")
            n += 1
        with open(path, "w") as f:
            f.write("\n".join(out))

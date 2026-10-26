#!/usr/bin/env python3
"""Master renderer: scenes -> frames -> ffmpeg H.264 pipe (1080x1920 @ 30fps)."""
import argparse, json, math, os, subprocess, sys, random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import ease, effects
from engine.subtitles import Subtitles

# importing registers every scene
from shots import street, montage, alley, building, stairs, rooftop, isolation, choices
from engine.scene import REGISTRY

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TIMING = os.path.join(ROOT, "voiceover-timing.json")

TEAR_BOUNDARIES = {16.36, 50.79, 57.43, 63.50, 109.80}

class Renderer:
    def __init__(self, burn_subs=True):
        self.timing = json.load(open(TIMING))
        self.duration = self.timing["measured_duration_s"]
        self.scenes = sorted(REGISTRY, key=lambda s: s.start)
        for s in self.scenes:
            s(self.timing)
        self.instances = [s(self.timing) for s in self.scenes]
        self.subs = Subtitles(TIMING) if burn_subs else None
        self.rng = random.Random(909)

    def scene_at(self, t):
        for s in self.instances:
            if t < s.end - 1e-6:
                return s
        return self.instances[-1]

    def frame(self, t, idx):
        sc = self.scene_at(t)
        local = t - sc.start
        img = sc.render(local, idx).convert("RGBA")
        # boundary digital tears: brief, subtle displacement, no chromatic bars
        for b in TEAR_BOUNDARIES:
            d = abs(t - b)
            if d < 0.10:
                u = 1 - d / 0.10
                img = effects.slice_tear(img, self.rng, count=int(2 + u * 3),
                                         max_shift=int(8 + u * 22), band=(4, 14),
                                         tint=None)
        # fine global grain + safe-margin-neutral grade
        arr = D.grain(__import__("numpy").array(img), amount=4, seed=idx)
        img = Image.fromarray(arr, "RGBA")
        if self.subs:
            sub_y = getattr(sc, "subtitle_y", None)
            self.subs.burn(img, t, y=sub_y)
        # flatten onto opaque base so no transparent pixel leaks RGB at encode
        flat = Image.new("RGB", (C.W, C.H), (5, 7, 16))
        flat.paste(img, (0, 0), img)
        return flat

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "renders", "video-only.mp4"))
    ap.add_argument("--preview", action="store_true", help="sparse frames to sheets")
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--scene", default=None)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    r = Renderer()
    total_frames = int(math.ceil(r.duration * C.FPS))

    if args.preview:
        os.makedirs(os.path.join(ROOT, "preview"), exist_ok=True)
        times = [i * args.every for i in range(int(r.duration / args.every) + 1)]
        if args.scene:
            sc = next(s for s in r.instances if s.name == args.scene)
            times = [sc.start + i * args.every
                     for i in range(int((sc.end - sc.start) / args.every) + 1)]
        thumbs = []
        for k, t in enumerate(times):
            img = r.frame(t, int(t * C.FPS))
            img.thumbnail((270, 480), Image.LANCZOS)
            canvas = Image.new("RGB", (270, 510), (12, 14, 26))
            canvas.paste(img, (0, 0))
            dd = ImageDraw.Draw(canvas)
            dd.text((8, 486), f"{t:6.2f}s", fill=(150, 235, 240))
            thumbs.append(canvas)
        cols = 4
        rows = math.ceil(len(thumbs) / cols)
        sheet = Image.new("RGB", (270 * cols, 510 * rows), (8, 10, 20))
        for i, th in enumerate(thumbs):
            sheet.paste(th, ((i % cols) * 270, (i // cols) * 510))
        path = os.path.join(ROOT, "preview", f"contact-{args.scene or 'all'}.png")
        sheet.save(path)
        print("saved", path, sheet.size)
        return

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    cmd = [
        os.path.join(os.path.expanduser("~"), ".venv", "bin", "ffmpeg"), "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{C.W}x{C.H}",
        "-r", str(C.FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", args.out,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n = args.limit or total_frames
    for i in range(n):
        t = i / C.FPS
        img = r.frame(t, i)
        proc.stdin.write(img.tobytes())
        if i % 150 == 0:
            print(f"frame {i}/{total_frames}  t={t:6.2f}s", flush=True)
    proc.stdin.close()
    rc = proc.wait()
    print("ffmpeg rc =", rc, "->", args.out)

if __name__ == "__main__":
    main()

"""
render.py — frame pipeline + CLI.

    python3 project/render.py --still 12.5          # one preview frame
    python3 project/render.py --range 0 6 --preview # quick low-copy render
    python3 project/render.py --all --audio         # final film

The pipeline is: vector scene -> supersampled canvas -> additive glow ->
downscale -> numpy effects -> typography (subtitles/UI) -> H.264 pipe.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine as E
from engine import (C, FPS, H, SH, SS, SW, W, Cam, Pen, clamp, downscale,
                    font, fx_blocks, fx_grain, fx_rgb_split, fx_scanlines,
                    fx_vignette, hash01, lerp, vgrad)
import scenes
import subs as subs_mod
from timeline import Timeline

ROOT = E.ROOT
WORK = os.path.join(ROOT, ".work")
GRAIN_SCALE = 0.55   # keep the filmic texture without paying for it in bitrate


class Ctx:
    """per-frame drawing context handed to every scene"""

    def __init__(self, t, t0, t1, cam, tl):
        self.t = t
        self.t0, self.t1 = t0, t1
        self.lt = t - t0
        self.dur = max(1e-6, t1 - t0)
        self.p = clamp((t - t0) / self.dur)
        self.cam = cam
        self.tl = tl
        self.canvas = Image.new("RGB", (SW, SH), C["night"])
        self.pen = Pen(ImageDraw.Draw(self.canvas), cam)
        self._glow = Image.new("RGB", (SW // 2, SH // 2), (0, 0, 0))
        self.fx = dict(rgb_split=0.0, blocks=0, block_strength=40, scanlines=0.35,
                       grain=5.0, vignette=0.5, tint=(1.0, 1.0, 1.0), contrast=1.0,
                       lift=0.0, flash=0.0, flash_color=(255, 255, 255))

    # -- glow sprites (cheap additive light) --------------------------------
    def ghost(self, sprite, px, py, alpha=1.0):
        if alpha <= 0.01:
            return
        w = max(2, int(sprite.width * 0.5))
        h = max(2, int(sprite.height * 0.5))
        s = sprite.resize((w, h), Image.BILINEAR)
        a = s.getchannel("A")
        if alpha < 1.0:
            a = a.point(lambda v: int(v * min(1.0, alpha)))
        s.putalpha(a)
        self._glow.paste(s, (int(px * 0.5 - w / 2), int(py * 0.5 - h / 2)), s)

    def flush_glow(self, strength=1.0):
        g = self._glow.resize((SW, SH), Image.BILINEAR)
        base = np.asarray(self.canvas, dtype=np.uint16)
        add = (np.asarray(g, dtype=np.uint16) * max(0.0, strength)).astype(np.uint16)
        out = np.clip(base + add, 0, 255).astype(np.uint8)
        self.canvas = Image.fromarray(out, "RGB")
        return self.canvas

    def screen(self, x, y):
        return self.cam.pt(x, y)


# --------------------------------------------------------------- sub-pipeline ---
def apply_fx(img: Image.Image, ctx: Ctx, frame_idx: int) -> Image.Image:
    a = np.asarray(img)
    fx = ctx.fx
    if fx["blocks"]:
        a = fx_blocks(a, fx["blocks"], fx["block_strength"] * SS,
                      seed=frame_idx, rng_scale=1.0)
    if fx["rgb_split"] > 0:
        a = fx_rgb_split(a, fx["rgb_split"] * SS, a=0.85)
    if fx["tint"] != (1.0, 1.0, 1.0) or fx["contrast"] != 1.0 or fx["lift"]:
        a = E.grade(a, fx["tint"], fx["lift"], fx["contrast"])
    if fx["scanlines"] > 0:
        a = fx_scanlines(a, fx["scanlines"])
    if fx.get("dim", 0.0) > 0.002:
        # used by the choice screen: darken the set behind the interface
        f_ = min(0.72, fx["dim"])
        a = (a.astype(np.float32) * (1 - f_) + np.array((9, 8, 18), dtype=np.float32) * f_)
        a = a.clip(0, 255).astype(np.uint8)
    if fx["flash"] > 0.002:
        fc = np.array(fx["flash_color"], dtype=np.float32)
        a = (a.astype(np.float32) * (1 - fx["flash"]) + fc * fx["flash"]).clip(0, 255).astype(np.uint8)
    if fx["grain"] > 0:
        # grain is stylistically nice but expensive at 1080p; keep it subtle
        a = fx_grain(a, fx["grain"] * GRAIN_SCALE, rng=np.random.default_rng(frame_idx % 4096))
    if fx["vignette"] > 0:
        a = fx_vignette(a, fx["vignette"])
    return Image.fromarray(a, "RGB")


def render_frame(t: float, tl: Timeline, frame_idx: int = 0) -> Image.Image:
    shot = tl.shot_at(t)
    if shot is None:
        img = Image.new("RGB", (W, H), (0, 0, 0))
        d = ImageDraw.Draw(img)
        nxt = tl.shots[0]
        d.text((W / 2, H / 2), f"{t:6.2f}s", font=font(E.F_UI, 60), fill=(90, 90, 110), anchor="mm")
        return img
    cam = shot.camera_at(t)
    ctx = Ctx(t, shot.start, shot.end, cam, tl)
    scenes.REGISTRY[shot.scene](ctx, shot.params)
    canvas = ctx.flush_glow()
    img = apply_fx(downscale(canvas), ctx, frame_idx)
    subs_mod.draw_frame_text(img, t, tl)
    return img


def render_range(tl, t_start, t_end, out_path, audio=None, crf=19, preset="medium",
                 progress=True, on_frame=None):
    n = int(round((t_end - t_start) * FPS))
    writer = E.VideoWriter(out_path, audio=audio, crf=crf, preset=preset, total=n)
    t0 = time.time()
    for i in range(n):
        t = t_start + i / FPS
        img = render_frame(t, tl, frame_idx=int(t * FPS))
        writer.write(img)
        if progress and (i % 90 == 0 or i == n - 1):
            el = time.time() - t0
            eta = (el / (i + 1)) * (n - i - 1)
            print(f"  frame {i+1}/{n}  t={t:6.2f}s  {el/(i+1)*1000:5.0f} ms/f  eta {eta/60:4.1f} min",
                  flush=True)
        if on_frame:
            on_frame(t, img)
    rc = writer.close()
    if rc != 0:
        raise SystemExit(f"ffmpeg failed rc={rc}")
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float, nargs="*")
    ap.add_argument("--range", type=float, nargs=2)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--crf", type=int, default=19)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--outdir", default=os.path.join(WORK, "stills"))
    args = ap.parse_args()

    tl = Timeline()
    if args.still is not None:
        os.makedirs(args.outdir, exist_ok=True)
        for t in args.still:
            t0 = time.time()
            img = render_frame(t, tl, frame_idx=int(t * FPS))
            path = os.path.join(args.outdir, f"still_{t:07.2f}.jpg")
            img.save(path, quality=92)
            print(f"still {t:7.2f}s -> {path}  ({(time.time()-t0)*1000:.0f} ms)")
        return

    if args.range or args.all:
        if args.all:
            t0, t1 = 0.0, tl.duration
            out = args.out or os.path.join(ROOT, "final", "glitch-world-day-01.mp4")
            os.makedirs(os.path.dirname(out), exist_ok=True)
        else:
            t0, t1 = args.range
            out = args.out or os.path.join(WORK, f"render_{t0:05.1f}_{t1:05.1f}.mp4")
            os.makedirs(os.path.dirname(out), exist_ok=True)
        audio = args.audio
        print(f"rendering {t0:.2f}s -> {t1:.2f}s ({int((t1-t0)*FPS)} frames) to {out}")
        render_range(tl, t0, t1, out, audio=audio, crf=args.crf, preset=args.preset)
        print("done:", out, E.probe(out))
        return
    ap.print_help()


if __name__ == "__main__":
    main()

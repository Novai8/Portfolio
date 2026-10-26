#!/usr/bin/env python3
"""
make_previews.py — build the storyboard / contact sheet from the FINAL video.

Frames are pulled out of the rendered MP4 (not re-rendered), so the sheets are
evidence of what was actually exported.

    python3 project/make_previews.py

Outputs
    previews/storyboard.jpg     one frame per shot, with captions
    previews/contact-sheet.jpg  6x5 grid of representative frames
    previews/character-sheet.jpg  the protagonist rig, all key poses
"""
from __future__ import annotations

import json
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import engine as E
from engine import W, H, font
from timeline import Timeline

ROOT = E.ROOT
FINAL = os.path.join(ROOT, "final", "glitch-world-day-01.mp4")
PREV = os.path.join(ROOT, "previews")
WORK = os.path.join(ROOT, ".work")


def grab(t, out):
    """pull a single frame at time t (seconds) from the final render"""
    subprocess.run([E.ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
                    "-ss", f"{t:.3f}", "-i", FINAL, "-frames:v", "1", out], check=True)
    return out


def labelled(img, text, sub=""):
    d = ImageDraw.Draw(img)
    f = font(E.F_UI, 24)
    tw = f.getbbox(text)[2]
    d.rectangle([10, 10, 28 + tw, 58], fill=(6, 8, 16))
    d.text((18, 20), text, font=f, fill=(0, 232, 255))
    if sub:
        f2 = font(E.F_UI, 18)
        d.text((18, 40), sub, font=f2, fill=(220, 220, 235))
    return img


def main():
    os.makedirs(PREV, exist_ok=True)
    tl = Timeline()

    # ---- storyboard: one frame per shot ----------------------------------
    tiles = []
    for i, s in enumerate(tl.shots, 1):
        t = min(s.start + s.dur * 0.62, s.end - 0.05)
        p = os.path.join(WORK, f"sb_{i:02d}.png")
        grab(t, p)
        im = Image.open(p).convert("RGB").resize((432, 768), Image.LANCZOS)
        tiles.append((im, f"{i:02d}  {s.scene}", f"{s.start:6.2f}-{s.end:6.2f}s"))

    cols = 3
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (432 * cols + 16 * (cols + 1), 768 * rows + 16 * (rows + 1)),
                      (10, 10, 16))
    d = ImageDraw.Draw(sheet)
    d.text((16, 8), "GLITCH WORLD — DAY 1 · storyboard (frames pulled from the final render)",
           font=font(E.F_UI, 22), fill=(230, 236, 250))
    for i, (im, label, sub) in enumerate(tiles):
        x = 16 + (i % cols) * (432 + 16)
        y = 48 + (i // cols) * (768 + 16)
        sheet.paste(labelled(im, label, sub), (x, y))
    sheet.save(os.path.join(PREV, "storyboard.jpg"), quality=88)
    print("storyboard:", sheet.size)

    # ---- contact sheet: 30 evenly spaced frames --------------------------
    n = 30
    picks = [tl.duration * (i + 0.5) / n for i in range(n)]
    cw, ch = 288, 512
    cols, rows = 6, 5
    cs = Image.new("RGB", (cw * cols, ch * rows), (8, 8, 12))
    d = ImageDraw.Draw(cs)
    for i, t in enumerate(picks):
        p = os.path.join(WORK, f"cs_{i:02d}.png")
        grab(t, p)
        im = Image.open(p).convert("RGB").resize((cw, ch), Image.LANCZOS)
        x, y = (i % cols) * cw, (i // cols) * ch
        cs.paste(im, (x, y))
        d.text((x + 6, y + 6), f"{t:.1f}s", font=font(E.F_UI, 18), fill=(255, 236, 120))
    cs.save(os.path.join(PREV, "contact-sheet.jpg"), quality=88)
    print("contact sheet:", cs.size)

    # ---- character sheet (reusable rig reference for later episodes) -----
    import rig
    poses = ["idle", "walk_a", "run_a", "shock", "confused", "deadpan", "point_up",
             "shrug", "wave", "throw", "facepalm", "scared"]
    cw2, ch2 = 240, 300
    cols2 = 6
    rows2 = (len(poses) + cols2 - 1) // cols2
    sheet2 = Image.new("RGB", (cw2 * cols2, ch2 * rows2 + 46), (16, 18, 38))
    d2 = ImageDraw.Draw(sheet2)
    d2.text((16, 12), "NIX — the protagonist rig (project/rig.py)", font=font(E.F_UI, 22),
            fill=(230, 236, 250))
    from PIL import ImageDraw as ID
    for i, name in enumerate(poses):
        tile = Image.new("RGB", (cw2, ch2), (16, 18, 38))
        cam = E.Cam(0, 0, 1.55)
        pen = E.Pen(ID.Draw(tile), cam)
        rig.draw_stickman(pen, 0, -6, 1.0, rig.POSES[name], rim=(0, 150, 190))
        x, y = (i % cols2) * cw2, (i // cols2) * ch2 + 46
        sheet2.paste(tile, (x, y))
        d2.text((x + 8, y + ch2 - 24), name, font=font(E.F_UI, 18), fill=(150, 200, 255))
    sheet2.save(os.path.join(PREV, "character-sheet.jpg"), quality=90)
    print("character sheet:", sheet2.size)


if __name__ == "__main__":
    main()

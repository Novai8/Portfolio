"""
subs.py — burned-in captions plus editorial overlays.

Captions are generated from the real recording (scripts/subtitles.json) and are
drawn at output resolution so they stay razor sharp. They sit inside a
platform-safe box: clear of the bottom ~22% (UI bars / captions) and clear of
the right-edge action icons.
"""
from __future__ import annotations

import math

from PIL import Image, ImageDraw

import engine as E
from engine import C, H, W, clamp, ease, font, lerp, text_w, wrap

SAFE_LEFT = 74
SAFE_RIGHT = W - 132
SAFE_CENTER_Y = int(H * 0.715)
HIGHLIGHT = {
    "cyan": C["cyan"], "magenta": C["magenta"], "red": C["red"],
    "amber": C["amber"], "violet": C["violet"],
}


def _plate(img, box, alpha=110, radius=26):
    if alpha <= 0:
        return
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle(box, radius=radius, fill=(4, 6, 14, alpha))
    img.alpha_composite(ov) if img.mode == "RGBA" else img.paste(
        Image.alpha_composite(img.convert("RGBA"), ov).convert("RGB"), (0, 0))


def _tokens(text):
    """split into (word, is_highlight); '*' marks an accent inside a word/token"""
    out = []
    for wd in text.split():
        hi = "*" in wd
        out.append((wd.replace("*", ""), hi))
    return out


def draw_cue(img, cue, t, prev_cue=None):
    if not cue:
        return
    f = font(E.F_SUB, 58)
    max_w = SAFE_RIGHT - SAFE_LEFT
    toks = _tokens(cue["text"])
    # colour per token, "hi" -> cycle through accent colours
    cycle = [HIGHLIGHT["cyan"], HIGHLIGHT["magenta"], HIGHLIGHT["amber"]]
    hi_i = 0
    colored = []
    for wd, hi in toks:
        if hi:
            colored.append((wd, cycle[hi_i % len(cycle)]))
            hi_i += 1
        else:
            colored.append((wd, C["white"]))

    # layout into lines
    space = text_w(f, " ")
    lines, cur, cur_w = [], [], 0
    for wd, col in colored:
        ww = text_w(f, wd)
        add = ww if not cur else space + ww
        if cur and cur_w + add > max_w:
            lines.append(cur)
            cur, cur_w = [(wd, col, ww)], ww
        else:
            cur.append((wd, col, ww))
            cur_w += add
    if cur:
        lines.append(cur)
    lines = lines[-2:]  # never more than 2 lines

    line_h = 72
    total_h = line_h * len(lines)
    age = t - cue["start"]
    anim = ease(clamp(age / 0.14), "out")
    rise = int((1 - anim) * 16)
    alpha = int(255 * (0.35 + 0.65 * anim))

    # contrast plate
    widest = max(sum(w for _, _, w in ln) + space * (len(ln) - 1) for ln in lines)
    cx = (SAFE_LEFT + SAFE_RIGHT) / 2
    box = [cx - widest / 2 - 26, SAFE_CENTER_Y - total_h / 2 - 16 + rise,
           cx + widest / 2 + 26, SAFE_CENTER_Y + total_h / 2 + 16 + rise]
    _plate(img, box, alpha=95)

    d = ImageDraw.Draw(img, "RGBA")
    y = SAFE_CENTER_Y - total_h / 2 + line_h / 2 + rise
    for ln in lines:
        lw = sum(w for _, _, w in ln) + space * (len(ln) - 1)
        x = cx - lw / 2
        for wd, col, ww in ln:
            for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (2, -2), (-2, 2)):
                d.text((x + dx, y + dy), wd, font=f, anchor="lm",
                       fill=(3, 4, 10, alpha))
            d.text((x, y), wd, font=f, anchor="lm", fill=tuple(col) + (alpha,))
            x += ww + space
        y += line_h


def draw_overlays(img, t, timeline):
    for o in timeline.overlays:
        if not (o["start"] <= t <= o["end"]):
            continue
        style = o.get("style", "stamp")
        a = clamp((t - o["start"]) / max(0.001, o.get("fade", 0.35)))
        b = clamp((o["end"] - t) / max(0.001, o.get("fade", 0.35)))
        alpha = int(255 * min(a, b))
        if alpha <= 2:
            continue
        d = ImageDraw.Draw(img, "RGBA")
        if style == "stamp":
            f1 = font(E.F_DISPLAY, 58)
            f2 = font(E.F_UI, 26)
            y = o.get("y", 210)
            w1 = text_w(f1, o["text"])
            # dark plate keeps the stamp readable over any background
            d.rounded_rectangle([W / 2 - max(w1, text_w(f2, o.get("sub", "").upper())) / 2 - 34,
                                 y - 46, W / 2 + max(w1, text_w(f2, o.get("sub", "").upper())) / 2 + 34,
                                 y + 66], radius=18, fill=(6, 8, 18, int(alpha * 0.72)))
            d.text((W / 2, y), o["text"], font=f1, anchor="mm",
                   fill=(238, 244, 255, alpha))
            if o.get("sub"):
                d.text((W / 2, y + 44), o["sub"].upper(), font=f2, anchor="mm",
                       fill=tuple(o.get("color", C["cyan"])) + (min(255, alpha),))
            d.line([(W / 2 - w1 / 2 - 26, y + 24), (W / 2 - w1 / 2 - 8, y + 24)],
                   fill=tuple(o.get("color", C["cyan"])) + (alpha,), width=3)
            d.line([(W / 2 + w1 / 2 + 8, y + 24), (W / 2 + w1 / 2 + 26, y + 24)],
                   fill=tuple(o.get("color", C["cyan"])) + (alpha,), width=3)
        elif style == "card":
            f1 = font(E.F_DISPLAY, o.get("size", 150))
            d.text((W / 2, o.get("y", H * 0.42)), o["text"], font=f1, anchor="mm",
                   fill=(245, 248, 255, alpha), stroke_width=2,
                   stroke_fill=(8, 6, 16, alpha))


def draw_frame_text(img, t, timeline):
    draw_overlays(img, t, timeline)
    cue = timeline.cue_at(t)
    if cue:
        draw_cue(img, cue, t)

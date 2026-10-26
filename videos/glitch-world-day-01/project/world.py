"""
world.py — reusable environment + prop builders for the Glitch World series.

All environments are drawn from procedural vector art so the same code can be
re-shot in later episodes with different camera moves.
"""
from __future__ import annotations

import math

from engine import (C, SS, SW, SH, Cam, clamp, font, hash01, inv, kf, kf_list, lerp,
                    pulse, radial_glow, vgrad)
from rig import POSES, draw_stickman, pose

# ------------------------------------------------------------------ sky/scene ---
def sky(ctx, stops, ground_from=None):
    ctx.canvas.paste(vgrad(SW, SH, stops), (0, 0))


def stars(ctx, count=90, seed=3, dim=1.0, drift=0.0, y_max=0.62):
    c = ctx.cam
    d = ctx.pen.d
    for i in range(count):
        sx = hash01(seed, i, 1) * SW
        sy = hash01(seed, i, 2) * SH * y_max
        px = (sx - (c.cx * c.zoom * 0.06) + drift * i) % SW
        py = sy - c.cy * c.zoom * 0.04
        tw = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(ctx.t * (0.7 + hash01(seed, i, 3)) + i))
        r = (1.2 + hash01(seed, i, 4) * 2.2) * SS
        col = tuple(int(v * tw * dim) for v in (200, 225, 255))
        if col[0] + col[1] + col[2] < 18:
            continue
        d.ellipse([px - r, py - r, px + r, py + r], fill=col)


def skyline(ctx, y, seed=1, color=(8, 9, 22), hmin=0.10, hmax=0.36,
            spacing=78, windows=True, win_color=C["cyan"], depth=1.0, t=0.0):
    """procedural city silhouette strip in *screen* space; y = horizon line."""
    d = ctx.pen.d
    x = -SW * 0.1
    i = 0
    while x < SW * 1.1:
        w = spacing * (0.7 + hash01(seed, i, 1) * 0.9) * SS * 0.55
        h = SH * lerp(hmin, hmax, hash01(seed, i, 2))
        top = y - h
        d.rectangle([x, top, x + w, y], fill=color)
        if hash01(seed, i, 9) > 0.80:
            ax = x + w * 0.5
            d.rectangle([ax - 1.6 * SS, top - 30 * SS * depth, ax + 1.6 * SS, top], fill=color)
            if hash01(seed, i, 10) > 0.5:
                r = 2.4 * SS
                ay = top - 32 * SS * depth
                d.ellipse([ax - r, ay - r, ax + r, ay + r], fill=C["red"])
        if windows:
            cols = max(1, int(w / (15 * SS * depth)))
            rows = max(1, int(h / (21 * SS * depth)))
            for ci in range(cols):
                for ry in range(rows):
                    if hash01(seed, i, ci * 31 + ry) > 0.74:
                        wx = x + (ci + 0.3) * (w / cols)
                        wy = y - (ry + 0.7) * (h / rows)
                        fl = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 1.1 + ci + ry * 2))
                        col = tuple(int(v * fl) for v in win_color)
                        d.rectangle([wx, wy, wx + 3.2 * SS * depth, wy + 5.0 * SS * depth], fill=col)
        x += w
        i += 1


def ground(ctx, y, color=C["ink_soft"], top_line=None):
    c = ctx.cam
    d = ctx.pen.d
    p0 = c.pt(-2000, y)
    top = max(0.0, min(SH, p0[1]))
    if top < SH:
        d.rectangle([0, top, SW, SH], fill=color)
    if top_line and 0 <= p0[1] <= SH:
        d.line([(0, p0[1]), (SW, p0[1])], fill=top_line, width=int(2 * SS))


def fog_band(ctx, y, h, color, alpha=60):
    """horizontal haze strip"""
    d = ctx.pen.d
    py = ctx.cam.pt(0, y)[1]
    hh = h * ctx.cam.zoom
    d.rectangle([0, py - hh / 2, SW, py + hh / 2], fill=color)


def light_pool(ctx, x, y, rx, ry, color=C["cyan"], alpha=0.5):
    g = radial_glow(int(200), color, 1.4).resize((int(rx * 4), int(ry * 4)))
    px, py = ctx.cam.pt(x, y)
    ctx.ghost(g, px, py, alpha=alpha)


def lamp(ctx, x, y, color=C["cyan"], size=1.0, flicker=0.0):
    c = ctx.cam
    p = ctx.pen
    px, py = c.pt(x, y)
    f = 1.0 if flicker <= 0 else (1.0 if hash01(int(ctx.t * 18), 3) > 0.12 else 0.25)
    g = radial_glow(int(300 * size), color, 1.7)
    ctx.ghost(g, px, py, alpha=0.85 * f)
    p.circle(x, y, 6 * size, fill=C["white"])


def rain(ctx, t, upward=True, count=140, seed=5, speed=520, slant=0.16,
         color=(150, 210, 255), length=26, band=(0, 1)):
    d = ctx.pen.d
    for i in range(count):
        rx = hash01(seed, i, 1) * SW * 1.2
        phase = hash01(seed, i, 2)
        span = SH * (band[1] - band[0])
        sp = speed * (0.7 + hash01(seed, i, 3) * 0.8)
        if upward:
            yy = SH * band[1] - ((phase * span + t * sp) % span)
        else:
            yy = SH * band[0] + ((phase * span + t * sp) % span)
        sl = slant * (1 if upward else -1)
        x0 = (rx - t * 40) % (SW * 1.2) - SW * 0.1
        a = 0.35 + 0.5 * hash01(seed, i, 4)
        col = tuple(int(v * a) for v in color)
        d.line([(x0, yy), (x0 + slant * length * SS, yy + (-length if upward else length) * SS)],
               fill=col, width=int(1.6 * SS))


def dust(ctx, count=40, seed=11, color=C["cyan"], spread=1.0, speed=1.0):
    d = ctx.pen.d
    for i in range(count):
        px = (hash01(seed, i, 1) * SW + math.sin(ctx.t * 0.7 * speed + i) * 30 * SS) % SW
        py = (hash01(seed, i, 2) * SH - ctx.t * 26 * speed * (0.4 + hash01(seed, i, 3))) % SH
        r = (1.0 + hash01(seed, i, 4) * 2.4) * SS * spread
        a = 0.25 + 0.5 * hash01(seed, i, 5)
        d.ellipse([px - r, py - r, px + r, py + r], fill=tuple(int(v * a) for v in color))


def bird(pen, x, y, s, flap, col=C["ink"], dirn=-1):
    """simple two-stroke bird; dirn=-1 means flying backwards (left)"""
    a = flap
    for side in (-1, 1):
        wx = x + dirn * side * 13 * s
        wy = y - (14 * s if a > 0 else 7 * s) * (1 if side == 1 else 1)
        pen.line([(x - dirn * 2 * s, y), (wx, wy)], fill=col, w=3.2 * s)
    pen.circle(x, y + 1.5 * s, 2.6 * s, fill=col)


def chicken(pen, x, y, s, flap=0.0, rot=0.0, col=None):
    """the rock->chicken payoff. s = world scale multiplier."""
    col = col or C["white"]
    ink = C["ink"]

    def R(px, py):
        c, sn = math.cos(rot), math.sin(rot)
        return (x + (px * c - py * sn) * s, y + (px * sn + py * c) * s)

    body = [R(-16, -2), R(-6, -14), R(8, -14), R(17, -4), R(14, 8), R(-8, 9), R(-17, 4)]
    pen.poly(body, fill=col, outline=ink, w=1.6 * s)
    pen.circle(*R(15, -12), 7.4 * s, fill=col, outline=ink, w=1.6 * s)
    pen.poly([R(21, -14), R(28, -11), R(21, -9)], fill=C["amber"], outline=ink, w=1.0 * s)
    pen.circle(*R(17, -14), 1.7 * s, fill=ink)
    pen.line([R(-14, -6), R(-24, -18 + flap * 14)], fill=col, w=4.4 * s)
    pen.line([R(-16, 2), R(-27, 8 - flap * 10)], fill=col, w=3.4 * s)
    for i, a in enumerate((0, 120, 240)):
        pen.line([R(12 + 5 * math.cos(math.radians(a)), 2 + 5 * math.sin(math.radians(a))),
                  R(16 + 9 * math.cos(math.radians(a)), 6 + 9 * math.sin(math.radians(a)))],
                 fill=C["magenta"], w=2.0 * s)


def carton(pen, x, y, w, h, col=C["milk"], label=None, face_pen=None, tilt=0.0):
    ink = C["ink"]
    hw, hh = w / 2, h / 2
    pen.rrect(x - hw, y - hh, w, h, 3, fill=col, outline=ink, lw=2.2)
    pen.poly([(x - hw, y - hh), (x - hw * 0.35, y - hh - h * 0.22),
              (x + hw * 0.35, y - hh - h * 0.22), (x + hw, y - hh)],
             fill=col, outline=ink, w=2.2)
    pen.poly([(x + hw * 0.35, y - hh - h * 0.22), (x + hw, y - hh),
              (x + hw * 0.78, y - hh - h * 0.05)],
             fill=C["cyan_lo"], outline=None)
    if label:
        f = font("Inter-Black.ttf", max(11, int(h * 0.16)))
        pen.text(x, y + h * 0.02, label, f, C["night"], anchor="mm")
    return (x, y - hh - h * 0.05)


def door_frame(pen, x, y, w, h, depth=26, col=(24, 20, 40), out=C["cyan_lo"]):
    """a doorway standing alone in the world (source of the impossible view)"""
    pen.poly([(x - w / 2, y), (x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y)],
             fill=col, outline=out, w=3.0)


def panel(ctx, x, y, w, h, title, sub=None, col=C["cyan"], alpha=1.0,
          title_scale=1.0, sub_scale=1.0, glow=True):
    """holographic system panel (used for REALITY UPDATE FAILED etc.)"""
    c = ctx.cam
    d = ctx.pen.d
    px, py = c.pt(x, y)
    pw, ph = w * c.zoom, h * c.zoom
    if glow:
        g = radial_glow(int(400), col, 2.2).resize((int(pw * 1.9), int(ph * 1.9)))
        ctx.ghost(g, px, py, alpha=0.28 * alpha)
    d.rectangle([px - pw / 2, py - ph / 2, px + pw / 2, py + ph / 2],
                fill=tuple(int(v * 0.22) for v in col), outline=col, width=int(3 * SS))
    # corner ticks
    t = 26 * SS
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        ex, ey = px + sx * pw / 2, py + sy * ph / 2
        d.line([(ex, ey), (ex - sx * t, ey)], fill=C["white"], width=int(3 * SS))
        d.line([(ex, ey), (ex, ey - sy * t)], fill=C["white"], width=int(3 * SS))
    f1 = font("BebasNeue-Regular.ttf", int(ph * 0.30 * title_scale))
    d.text((px, py - (ph * 0.11 if sub else 0)), title, font=f1, fill=C["white"], anchor="mm")
    if sub:
        f2 = font("JetBrainsMono-Bold.ttf", int(ph * 0.13 * sub_scale))
        d.text((px, py + ph * 0.22), sub, font=f2, fill=col, anchor="mm")


# the timer lands on the line "99 days, 23 hours, 59 minutes." and ticks from there
COUNTDOWN_T0 = 84.0      # absolute seconds in the film
COUNTDOWN_RATE = 1.0 / 1.5   # displayed minutes per real second


def countdown_state(elapsed):
    """recurring series clock: starts at 99d 23h 59m when it appears and ticks down"""
    ticks = int(max(0.0, elapsed - COUNTDOWN_T0) * COUNTDOWN_RATE)
    total = 99 * 24 * 60 + 23 * 60 + 59 - ticks
    return total // (24 * 60), (total // 60) % 24, total % 60


def countdown(ctx, x, y, days, hours, minutes, scale=1.0, alpha=1.0, col=C["red"]):
    c = ctx.cam
    d = ctx.pen.d
    px, py = c.pt(x, y)
    s = c.zoom * scale
    w, h = 300 * s, 120 * s
    g = radial_glow(int(420), col, 2.0).resize((int(w * 1.5), int(h * 2.0)))
    ctx.ghost(g, px, py, alpha=0.30 * alpha)
    d.rectangle([px - w / 2, py - h / 2, px + w / 2, py + h / 2],
                fill=(18, 6, 14), outline=col, width=int(3 * SS))
    cells = [(f"{days:02d}", "DAYS"), (f"{hours:02d}", "HOURS"), (f"{minutes:02d}", "MIN")]
    cw = w / 3
    for i, (val, lab) in enumerate(cells):
        cxp = px - w / 2 + cw * (i + 0.5)
        f1 = font("JetBrainsMono-Bold.ttf", int(h * 0.42))
        d.text((cxp, py - h * 0.06), val, font=f1, fill=C["white"], anchor="mm")
        f2 = font("Inter-Bold.ttf", int(h * 0.15))
        d.text((cxp, py + h * 0.28), lab, font=f2, fill=col, anchor="mm")
        if i < 2:
            d.line([(cxp + cw / 2, py - h * 0.22), (cxp + cw / 2, py + h * 0.22)],
                   fill=(70, 40, 50), width=int(1.5 * SS))


def glitch_pixels(ctx, x, y, w, h, t, progress, seed=0, col=C["magenta"]):
    """character break-up: deterministic pixel shards that fly apart"""
    d = ctx.pen.d
    c = ctx.cam
    n = 150
    for i in range(n):
        px0 = x + (hash01(seed, i, 1) - 0.5) * w
        py0 = y + (hash01(seed, i, 2) - 0.5) * h
        dirx = (hash01(seed, i, 3) - 0.5) * 2
        diry = (hash01(seed, i, 4) - 0.5) * 2 - 0.35
        sp = (0.4 + hash01(seed, i, 5) * 1.6) * lerp(0.0, 1.0, progress)
        px, py = c.pt(px0 + dirx * sp * 60, py0 + diry * sp * 54)
        sz = max(1.5, (3 + hash01(seed, i, 6) * 9) * c.zoom * 0.28 * (1 - progress * 0.7))
        cc = col if hash01(seed, i, 7) > 0.45 else C["cyan"]
        if hash01(seed, i, 8) > 0.5:
            d.rectangle([px, py, px + sz * SS, py + sz * SS * 0.8], fill=cc)
        else:
            d.rectangle([px, py, px + sz * SS * 2.4, py + sz * SS * 0.35], fill=cc)

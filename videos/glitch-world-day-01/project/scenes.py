"""
scenes.py — every shot in Day 1, drawn procedurally.

Each scene is a function (ctx, params) that paints the supersampled canvas for
one instant. Timing inside a scene is expressed as a fraction of the shot
(ctx.p) so the edit can be retimed against the real voiceover without
re-animating anything.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

import engine as E
import world as Wd
from engine import (C, SS, SH, SW, W, Cam, clamp, ease, font, hash01, inv, kf, kf_list,
                    lerp, pulse, radial_glow, vgrad)
from rig import POSES, blend, draw_stickman, pose, seq

F_UI, F_BLACK, F_MONO, F_DISPLAY = E.F_UI, E.F_BLACK, E.F_MONO, E.F_DISPLAY
REGISTRY = {}


def scene(name):
    def deco(fn):
        REGISTRY[name] = fn
        return fn
    return deco


# ------------------------------------------------------------------ helpers ---
def set_cam(ctx, cx, cy, zoom, roll=0.0):
    ctx.cam = Cam(cx, cy, zoom, shake=ctx.cam.shake, roll=roll)
    ctx.pen.cam = ctx.cam


def char(ctx, x, y, s, p, **kw):
    kw.setdefault("lw", 6.2)
    return draw_stickman(ctx.pen, x, y, s, p, **kw)


def walk(ctx, t, t0, t1, x0, x1, y, s, base=None, rim=C["cyan"], rate=2.2, **kw):
    """walk cycle helper: returns (x, pose)"""
    base = base or POSES["idle"]
    f = inv(t0, t1, t)
    if f <= 0.0:
        return x0, base
    if f >= 1.0:
        return x1, base
    e = ease(f, "inout")
    x = lerp(x0, x1, e)
    ph = ((t - t0) * rate * 1.35) % 1.0
    a, b = POSES["walk_a"], POSES["walk_b"]
    pp = blend(a, b, ph * 2 if ph < 0.5 else (ph - 0.5) * 2)
    pp["bob"] = math.sin(ph * 2 * math.pi) * 1.6
    return x, pp


def view_panel(ctx, x0, y0, x1, y1, fn):
    """paint a self-contained mini-scene (window/doorway view) into a world rect"""
    (sx0, sy0), (sx1, sy1) = ctx.cam.pt(x0, y0), ctx.cam.pt(x1, y1)
    w, h = int(sx1 - sx0), int(sy1 - sy0)
    if w <= 2 or h <= 2:
        return
    im = fn(w, h)
    ctx.canvas.paste(im, (int(sx0), int(sy0)))


def ocean_view(t, seed=0):
    def draw(w, h):
        img = vgrad(w, h, ((0.0, (255, 208, 150)), (0.30, (255, 150, 170)),
                           (0.52, (140, 120, 220)), (0.55, (30, 90, 190)),
                           (1.0, (8, 30, 90))))
        d = ImageDraw.Draw(img)
        hz = int(h * 0.55)
        # sun
        sr = h * 0.16
        d.ellipse([w * 0.62 - sr, hz - sr * 1.15, w * 0.62 + sr, hz + sr * 0.85],
                  fill=(255, 236, 190))
        # waves
        for i in range(9):
            y = hz + (i ** 1.5) * h * 0.012
            amp = h * 0.004 * (1 + i * 0.5)
            pts = [(x, y + math.sin(x / (26 + i * 9) + t * 1.6 + i) * amp) for x in range(0, w + 12, 12)]
            d.line(pts, fill=(235, 245, 255, 255), width=max(1, int(h * 0.0025 * (1 + i * 0.2))))
        for i in range(14):
            xx = (hash01(seed, i, 1) * w + t * 18 * (0.4 + hash01(seed, i, 2))) % w
            yy = hz + hash01(seed, i, 3) * (h - hz) * 0.6
            d.line([(xx, yy), (xx + w * 0.05, yy)], fill=(180, 210, 255), width=max(1, int(h * 0.002)))
        return img
    return draw


def store_view(t):
    def draw(w, h):
        img = Image.new("RGB", (w, h), (238, 244, 252))
        d = ImageDraw.Draw(img)
        for i in range(6):  # ceiling lamps
            y = h * (0.06 + i * 0.03)
            d.rectangle([w * 0.1, y, w * 0.9, y + h * 0.012], fill=(255, 255, 240))
        # aisle perspective
        vpx, vpy = w * 0.5, h * 0.42
        for i in range(-6, 7):
            x = w * 0.5 + i * w * 0.09
            d.line([(vpx + i * w * 0.012, vpy), (x, h)], fill=(206, 214, 228), width=max(1, int(h * 0.004)))
        d.rectangle([0, vpy, w, vpy + h * 0.012], fill=(198, 206, 222))
        # shelves
        for side in (-1, 1):
            for row in range(4):
                y = vpy + h * (0.06 + row * 0.13)
                d.rectangle([w * (0.5 + side * 0.42) - (w * 0.16 if side > 0 else 0), y,
                             w * (0.5 + side * 0.42) + (w * 0.16 if side < 0 else 0), y + h * 0.018],
                            fill=(178, 186, 202))
        return img
    return draw


def window_view(t, bird_x=None, rain_up=False):
    def draw(w, h):
        img = vgrad(w, h, ((0.0, (46, 58, 120)), (0.45, (128, 118, 200)),
                           (0.72, (232, 168, 190)), (1.0, (255, 214, 178))))
        d = ImageDraw.Draw(img)
        # moon
        mr = h * 0.13
        d.ellipse([w * 0.66 - mr, h * 0.22 - mr, w * 0.66 + mr, h * 0.22 + mr], fill=(250, 246, 226))
        # clouds
        for i in range(4):
            cx = (hash01(7, i, 1) * w + t * 6) % (w * 1.2) - w * 0.1
            cy = h * (0.10 + hash01(7, i, 2) * 0.35)
            cw = w * (0.16 + hash01(7, i, 3) * 0.2)
            d.ellipse([cx, cy, cx + cw, cy + cw * 0.34], fill=(240, 220, 235))
        # rooftops
        base = h * 0.86
        d.rectangle([0, base, w, h], fill=(24, 22, 44))
        for i in range(7):
            bw = w * (0.1 + hash01(3, i, 1) * 0.12)
            bh = h * (0.05 + hash01(3, i, 2) * 0.12)
            bx = hash01(3, i, 3) * w
            d.rectangle([bx, base - bh, bx + bw, base], fill=(30, 28, 56))
        if bird_x is not None:
            for k in range(3):
                bx = (bird_x + k * 46) % (w + 60) - 30
                by = h * (0.32 + 0.06 * k) + math.sin(t * 3 + k) * 4
                sc = h * 0.006
                for sgn in (-1, 1):
                    d.line([(bx, by), (bx - 14 * sc, by - 9 * sc * (1 if math.sin(t * 8 + k) > 0 else 0.4))],
                           fill=(20, 18, 34), width=max(2, int(3 * sc)))
        if rain_up:
            for i in range(60):
                rx = hash01(11, i, 1) * w
                span = h * 0.85
                ry = h - ((hash01(11, i, 2) * span + t * (260 + hash01(11, i, 3) * 200)) % span)
                d.line([(rx, ry), (rx + 2, ry - h * 0.03)], fill=(200, 230, 255),
                       width=max(1, int(h * 0.004)))
        return img
    return draw


def city_view(ctx, t, freeze=0.0, tint=(1, 1, 1)):
    d = ctx.pen.d
    c = ctx.cam
    Wd.skyline(ctx, c.pt(0, 60)[1], seed=21, color=(16, 16, 38), hmin=0.08, hmax=0.30,
               windows=True, win_color=C["cyan"], depth=1.0, t=t)
    Wd.skyline(ctx, c.pt(0, 70)[1], seed=22, color=(9, 9, 24), hmin=0.04, hmax=0.20,
               windows=True, win_color=C["amber"], depth=0.6, t=t)


# =============================================================== 1. BEDROOM ===
@scene("bedroom")
def s_bedroom(ctx, prm):
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    Wd.sky(ctx, ((0.0, (16, 17, 44)), (0.42, (30, 26, 68)), (1.0, (13, 12, 32))))
    floor_y = 70

    # ---- room shell ------------------------------------------------------
    pen.poly([(-900, floor_y), (-900, -700), (900, -700), (900, floor_y)],
             fill=(32, 27, 66), outline=None)
    for i in range(-9, 15):
        x = i * 52
        pen.poly([(x, floor_y), (x, -700), (x + 24, -700), (x + 24, floor_y)],
                 fill=(36, 30, 74), outline=None)
    pen.poly([(-900, floor_y - 8), (900, floor_y - 8), (900, floor_y), (-900, floor_y)],
             fill=(64, 50, 110), outline=None)
    Wd.ground(ctx, floor_y, color=(17, 14, 34), top_line=(84, 66, 132))
    for i in range(-16, 17):
        pen.line([(i * 46, floor_y), (i * 92, floor_y + 300)], fill=(25, 21, 46), w=1.3)
    for k in range(1, 8):
        pen.line([(-900, floor_y + k * k * 4.4), (900, floor_y + k * k * 4.4)],
                 fill=(25, 21, 46), w=1.1)
    # rug
    pen.ellipse(60, floor_y + 46, 210, 46, fill=(40, 28, 74), outline=(72, 52, 120), w=2)
    # ceiling + bulb
    pen.poly([(-900, -700), (900, -700), (900, -430), (-900, -430)], fill=(19, 16, 40), outline=None)
    pen.line([(40, -430), (40, -352)], fill=(70, 58, 112), w=3)
    pen.circle(40, -344, 12, fill=(255, 226, 168), outline=None)
    ctx.ghost(radial_glow(420, (255, 205, 140), 1.4), *cam.pt(40, -344), alpha=0.42)

    # ---- wall clock (upper right, above the bed) -------------------------
    clx, cly, clr = 132, -212, 34
    pen.circle(clx, cly, clr + 6, fill=(22, 19, 46), outline=(124, 106, 178), w=3)
    pen.circle(clx, cly, clr, fill=(232, 236, 250), outline=None)
    for k in range(12):
        a = k * math.pi / 6
        pen.line([(clx + math.sin(a) * (clr - 15), cly - math.cos(a) * (clr - 15)),
                  (clx + math.sin(a) * (clr - 9), cly - math.cos(a) * (clr - 9))],
                 fill=(32, 30, 58), w=2.0)
    back = p > 0.74
    spin = t * (-8.0 if back else 1.1)
    for hand, ln, wd in ((0, 0.66, 3.4), (1, 0.46, 2.4), (2, 0.32, 1.8)):
        a = spin * (1.0 if hand == 0 else 0.7) + hand * 2.1
        pen.line([(clx, cly), (clx + math.sin(a) * clr * ln, cly - math.cos(a) * clr * ln)],
                 fill=C["red"] if hand == 0 else (32, 30, 58), w=wd)

    # ---- window (upper left) --------------------------------------------
    wx0, wy0, wx1, wy1 = -152, -274, -12, -140
    bird_x = None
    if p > 0.53:
        bird_x = lerp(1.1, -0.35, ease(inv(0.53, 0.68, p))) * (wx1 - wx0)
    view_panel(ctx, wx0, wy0, wx1, wy1,
               window_view(t, bird_x=bird_x, rain_up=p > 0.72))
    pen = ctx.pen
    pen.rrect(wx0 - 10, wy0 - 10, (wx1 - wx0) + 20, (wy1 - wy0) + 20, 5,
              outline=(104, 88, 158), lw=5.0)
    pen.line([((wx0 + wx1) / 2, wy0), ((wx0 + wx1) / 2, wy1)], fill=(104, 88, 158), w=3.4)
    pen.line([(wx0, (wy0 + wy1) / 2), (wx1, (wy0 + wy1) / 2)], fill=(104, 88, 158), w=3.4)
    ctx.ghost(radial_glow(380, (110, 150, 255), 1.7),
              *cam.pt((wx0 + wx1) / 2, (wy0 + wy1) / 2), alpha=0.4)
    # light shaft onto the floor
    pen.poly([(wx0, wy1), (wx1, wy1), (wx1 + 150, floor_y + 40), (wx0 - 40, floor_y + 40)],
             fill=(38, 44, 92), outline=None)

    # ---- bed -------------------------------------------------------------
    bx0, bx1 = 130, 392
    pen.rrect(bx0, -18, bx1 - bx0, 30, 9, fill=(214, 222, 244), outline=(148, 154, 190), lw=2.5)
    pen.poly([(bx0 - 4, 12), (bx1 + 8, 12), (bx1 + 8, floor_y - 2), (bx0 - 4, floor_y - 2)],
             fill=(70, 54, 126), outline=None)
    for i in range(6):
        pen.line([(bx0, 18 + i * 9), (bx1, 18 + i * 9)], fill=(86, 66, 148), w=1.8)
    pen.rrect(bx1 - 6, -60, 16, 60, 5, fill=(52, 40, 92), outline=(96, 78, 152), lw=2)
    pen.rrect(bx1 - 96, -26, 74, 22, 8, fill=(236, 240, 252), outline=(160, 166, 198), lw=2)  # pillow
    pen.line([(bx0, -18), (bx0, -34)], fill=(96, 78, 152), w=4)

    # ---- alarm clock on the mattress -------------------------------------
    acx, acy = 118, -34
    ringing = p < 0.13
    pen.rrect(acx - 13, acy - 11, 26, 22, 4, fill=(236, 240, 252), outline=(40, 36, 66), lw=2)
    pen.circle(acx, acy, 6, outline=(40, 36, 66), w=1.6)
    pen.line([(acx, acy), (acx + 3, acy - 5)], fill=C["red"], w=1.6)
    if ringing:
        for k in range(3):
            r = 18 + k * 8 + (t * 20 % 4)
            pen.arc(acx, acy, r, -55, 55, fill=C["magenta"], w=1.8)
            pen.arc(acx, acy, r, 125, 235, fill=C["magenta"], w=1.8)

    # ---- lamp on a nightstand (right, decor) -----------------------------
    pen.rrect(410, 26, 54, 44, 4, fill=(46, 36, 78), outline=None)
    pen.line([(437, 26), (437, 2)], fill=(72, 60, 112), w=3)
    pen.poly([(422, 2), (452, 2), (447, -16), (427, -16)], fill=(255, 214, 150), outline=(24, 20, 44), w=1.4)
    if p < 0.30:
        ctx.ghost(radial_glow(320, (255, 196, 120), 1.5), *cam.pt(437, 0),
                  alpha=0.5 * (1 - inv(0.16, 0.30, p)))

    # ---- poster ----------------------------------------------------------
    pen.rrect(-330, -250, 90, 120, 3, fill=(46, 34, 84), outline=(120, 96, 176), lw=2)
    pen.line([(-318, -200), (-300, -226), (-282, -204), (-262, -238)], fill=C["magenta"], w=2.4)
    pen.circle(-262, -238, 5, fill=C["amber"])

    # ---- character -------------------------------------------------------
    floor_hip = floor_y - 66
    idle = POSES["idle2"] if int(t * 2) % 2 else POSES["idle"]
    sit_p = dict(POSES["sit"])
    sit_p.update(flip=-1, face="deadpan")

    if p < 0.115:
        x, y, pp = 170, -16, sit_p
    elif p < 0.20:
        x, y = 170, -16
        pp = seq(t, [
            (0.115 * ctx.dur, sit_p),
            (0.145 * ctx.dur, pose(flip=-1, torso=-6, ra_u=-92, ra_f=-104, ll_u=88, ll_f=-6,
                                   rl_u=84, rl_f=-8, bob=12, face="deadpan")),
            (0.175 * ctx.dur, pose(flip=-1, torso=4, ra_u=-30, ra_f=-16, ll_u=88, ll_f=-6,
                                   rl_u=84, rl_f=-8, bob=12, face="confused")),
            (0.205 * ctx.dur, pose(flip=-1, torso=-2, la_u=14, ra_u=-16, ll_u=86, ll_f=-10,
                                   rl_u=82, rl_f=-12, bob=12, face="wide")),
        ])
    elif p < 0.47:
        xm, _ = walk(ctx, t, 0.20 * ctx.dur, 0.44 * ctx.dur, 140, -54, 0, 1.0, rate=2.3)
        _, pp = walk(ctx, t, 0.20 * ctx.dur, 0.44 * ctx.dur, 0, 1, 0, 1.0, rate=2.3)
        x, y = xm, floor_hip
        if p < 0.22:
            pp = blend(dict(POSES["sit"], flip=-1), POSES["idle"], inv(0.20, 0.235, p))
    else:
        x = lerp(-54, -66, ease(inv(0.47, 0.58, p)))
        y = floor_hip
        pp = seq(t, [
            (0.44 * ctx.dur, pose(head=-8, look=1, face="wide", torso=-2)),
            (0.53 * ctx.dur, pose(head=-18, look=1, face="wide", torso=-5, la_u=12, ra_u=-12)),
            (0.58 * ctx.dur, POSES["startle"]),
            (0.63 * ctx.dur, POSES["shock"]),
            (0.70 * ctx.dur, pose(head=-14, look=1, face="scared", la_u=26, la_f=34, ra_u=-26, ra_f=-34)),
            (0.76 * ctx.dur, pose(head=-4, face="confused", la_u=10, ra_u=-16, ra_f=-30)),
            (0.84 * ctx.dur, pose(head=-16, look=1, face="scared", torso=-4, la_u=30, la_f=40,
                                  ra_u=-32, ra_f=-42)),
            (1.01 * ctx.dur, pose(head=-6, face="scared", torso=-2, la_u=34, la_f=46,
                                  ra_u=-36, ra_f=-48)),
        ])
    anchors = char(ctx, x, y, 1.0, pp, ground=floor_y, shadow=True,
                   shadow_col=(13, 11, 28))

    # stress marks
    if p > 0.78:
        for k in range(3):
            sx = x + 26 + k * 11
            sy = y - 118 - ((t * 4 + k * 0.4) % 1) * 24
            pen.line([(sx, sy), (sx + 3, sy + 12)], fill=C["cyan"], w=2.2)
    Wd.dust(ctx, count=30, seed=9, color=(150, 180, 255), speed=0.12)

    ctx.fx["vignette"] = 0.6
    ctx.fx["grain"] = 4.0
    ctx.fx["scanlines"] = 0.2
    if p > 0.72:
        g = inv(0.72, 1.0, p)
        ctx.fx["rgb_split"] = 2.2 * g
        ctx.fx["blocks"] = int(1 + 3 * g)
        ctx.fx["block_strength"] = 24 + 34 * g
        ctx.fx["tint"] = (1.0 + 0.04 * g, 1.0 - 0.03 * g, 1.0 + 0.03 * g)


# ========================================================= 2. FROZEN NEIGHBOUR ===
@scene("hallway")
def s_hallway(ctx, prm):
    """the frozen neighbour — one leg inside the wall. mode='neighbour'"""
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 70
    Wd.sky(ctx, ((0.0, (14, 16, 40)), (0.5, (22, 20, 54)), (1.0, (10, 10, 26))))

    # ---- corridor shell ---------------------------------------------------
    pen.poly([(-120, FY), (200, FY), (120, -250), (-40, -250)], fill=(20, 18, 46), outline=None)
    pen.rrect(-14, -250, 84, 150, 3, fill=(28, 24, 56), outline=(70, 58, 116), lw=2)
    ctx.ghost(radial_glow(320, (150, 190, 255), 1.7), *cam.pt(28, -200), alpha=0.30)
    pen.poly([(-620, 300), (-250, FY), (-60, -252), (-380, -430)], fill=(30, 25, 64), outline=None)
    pen.poly([(620, 300), (250, FY), (140, -252), (420, -430)], fill=(26, 21, 58), outline=None)
    for (xa, ya, xb, yb) in ((-250, FY, -60, -252), (250, FY, 140, -252)):
        pen.line([(xa, ya), (xb, yb)], fill=(104, 84, 156), w=3.0)
    for k in range(1, 5):
        f = k / 5.0
        pen.line([(lerp(-620, -250, f), lerp(300, FY, f)), (lerp(-380, -60, f), lerp(-430, -252, f))],
                 fill=(34, 28, 70), w=1.4)
        pen.line([(lerp(620, 250, f), lerp(300, FY, f)), (lerp(420, 140, f), lerp(-430, -252, f))],
                 fill=(32, 26, 66), w=1.4)
    pen.poly([(-380, -430), (420, -430), (140, -252), (-60, -252)], fill=(18, 16, 42), outline=None)
    for i in range(3):
        f = 0.25 + i * 0.22
        pen.line([(lerp(-330, -60, f), lerp(-410, -270, f)), (lerp(370, 140, f), lerp(-410, -270, f))],
                 fill=(200, 225, 255), w=5)
        ctx.ghost(radial_glow(260, (130, 180, 255), 1.6),
                  *cam.pt(lerp(-330 + 350, -60 + 100, f), lerp(-400, -260, f)), alpha=0.28)
    Wd.ground(ctx, FY, color=(15, 13, 32), top_line=(92, 74, 140))
    for i in range(-8, 9):
        pen.line([(i * 90, FY), (i * 190, FY + 320)], fill=(24, 20, 46), w=1.4)
    for k in range(1, 6):
        pen.line([(-620, FY + k * k * 5.5), (620, FY + k * k * 5.5)], fill=(24, 20, 46), w=1.2)
    for (dx, dy, dw, dh) in ((-200, FY, 70, 150), (340, FY, 78, 156)):
        pen.poly([(dx - dw / 2, dy), (dx - dw / 2, dy - dh), (dx + dw / 2, dy - dh - 12),
                  (dx + dw / 2, dy - 6)], fill=(30, 25, 62), outline=(88, 70, 140), w=2.4)
        pen.circle(dx + dw * 0.28, dy - dh * 0.5, 3.2, fill=(210, 186, 120))

    # ---- the neighbour, half swallowed by the wall ------------------------
    nx, ny = 286, FY - 62
    fp = dict(POSES["frozen"])
    fp.update(ll_u=3, rl_u=-4, face="blank")
    char(ctx, nx, ny, 1.0, fp, rim=(96, 116, 168), shadow=True, shadow_col=(12, 11, 28))
    pen.poly([(nx + 14, ny + 96), (nx + 14, ny - 158), (420, -430), (620, 300), (nx + 24, ny + 96)],
             fill=(26, 21, 58), outline=None)
    pen.line([(nx + 14, ny - 158), (nx + 14, ny + 96)], fill=(104, 84, 156), w=2.2)
    for k in range(5):
        pen.line([(nx + 14, ny - 130 + k * 48), (nx + 34 + k * 5, ny - 108 + k * 48)],
                 fill=(116, 96, 172), w=1.5)
    # the leg that went through the wall, drawn on the visible side
    pen.line([(nx - 2, ny + 4), (nx - 2, ny + 40)], fill=(120, 140, 190), w=3.2)
    pen.circle(nx + 30, ny - 74, 8, fill=(226, 232, 248), outline=(40, 36, 66), w=1.4)
    pen.rrect(nx + 22, ny - 74, 16, 18, 2, fill=(226, 232, 248), outline=(40, 36, 66), lw=1.4)
    if 0.30 < p < 0.55:
        pen.line([(nx + 30, ny - 56), (nx + 30, ny - 44 - 5 * math.sin(t * 5))],
                 fill=(180, 220, 255), w=2)

    # ---- protagonist: stares, checks, then starts to doubt himself --------
    hip = FY - 62
    x = lerp(-176, -150, ease(inv(0.0, 0.35, p)))
    pp = seq(t, [
        (0.00 * ctx.dur, pose(face="wide", head=-4, look=1, torso=2)),
        (0.16 * ctx.dur, pose(face="wide", head=-6, look=1, torso=3, la_u=26, ra_u=-26)),
        (0.30 * ctx.dur, pose(face="confused", head=7, look=1, torso=2, la_u=28, la_f=36)),
        (0.44 * ctx.dur, pose(face="confused", head=-8, look=1, torso=4, la_u=32, la_f=44,
                              ra_u=-22, ra_f=-30)),
        (0.56 * ctx.dur, POSES["wave"]),
        (0.64 * ctx.dur, POSES["wave2"]),
        (0.72 * ctx.dur, pose(face="confused", head=6, la_u=30, la_f=90, ra_u=-30, ra_f=-92)),
        (0.82 * ctx.dur, pose(face="deadpan", head=10, torso=6, la_u=22, ra_u=-22)),
        (0.92 * ctx.dur, pose(face="scared", head=6, torso=4, la_u=26, ra_u=-30, ra_f=-44)),
        (1.01 * ctx.dur, pose(face="confused", head=-4, torso=2, la_u=24, ra_u=-24)),
    ])
    char(ctx, x, hip, 1.0, pp, ground=FY, shadow=True, shadow_col=(12, 11, 28))

    # poke the neighbour (physical comedy beat)
    if 0.60 <= p <= 0.70:
        pen.line([(x + 26, hip - 102), (nx - 20, hip - 106)], fill=C["cyan"], w=2.2)
        for k in range(2):
            rr = 12 + k * 9 + ((t * 26) % 8)
            pen.arc(nx - 20, hip - 106, rr, -62, 62, fill=C["cyan"], w=1.8)

    Wd.dust(ctx, count=22, seed=17, color=(150, 190, 255), speed=0.04)
    ctx.fx["vignette"] = 0.62
    ctx.fx["scanlines"] = 0.24
    ctx.fx["tint"] = (0.97, 1.0, 1.04)
    if p > 0.90:
        g = inv(0.90, 1.0, p)
        ctx.fx["rgb_split"] = 2.2 * g


# ============================================================ 3. THE DOOR ===
@scene("door")
def s_door(ctx, prm):
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 76
    Wd.sky(ctx, ((0.0, (16, 15, 42)), (0.5, (26, 22, 58)), (1.0, (11, 10, 28))))
    pen.poly([(-900, FY), (-900, -600), (900, -600), (900, FY)], fill=(30, 26, 62), outline=None)
    for i in range(-10, 12):
        pen.line([(i * 64, FY), (i * 64, -600)], fill=(34, 29, 70), w=7)
    pen.poly([(-900, FY - 7), (900, FY - 7), (900, FY), (-900, FY)], fill=(70, 56, 118), outline=None)
    Wd.ground(ctx, FY, color=(17, 14, 34), top_line=(96, 78, 144))
    for i in range(-10, 11):
        pen.line([(i * 70, FY), (i * 130, FY + 330)], fill=(26, 22, 50), w=1.3)
    # pendant lamp
    pen.line([(318, -600), (318, -384)], fill=(64, 54, 104), w=3)
    pen.poly([(296, -384), (340, -384), (330, -352), (306, -352)], fill=(255, 222, 162), outline=(24, 20, 46), w=1.5)
    ctx.ghost(radial_glow(420, (255, 200, 130), 1.5), *cam.pt(318, -350), alpha=0.34)

    dx0, dx1 = -46, 104
    dy0, dy1 = FY - 208, FY
    # reveal timing: 1st open (ocean) -> slam -> 2nd open (store)
    if p < 0.44:
        open_amt = ease(inv(0.09, 0.30, p))
    elif p < 0.50:
        open_amt = 1.0 - ease(inv(0.44, 0.49, p))
    else:
        open_amt = ease(inv(0.52, 0.64, p))
    which2 = p >= 0.50

    pen.poly([(dx0 - 14, dy1), (dx0 - 14, dy0 - 14), (dx1 + 14, dy0 - 14), (dx1 + 14, dy1)],
             fill=(104, 84, 162), outline=None)
    if open_amt > 0.03:
        if which2:
            view_panel(ctx, dx0, dy0, dx1, dy1, store_view(t))
        else:
            view_panel(ctx, dx0, dy0, dx1, dy1, ocean_view(t))
    else:
        pen.poly([(dx0, dy0), (dx1, dy0), (dx1, dy1), (dx0, dy1)], fill=(9, 8, 20), outline=None)

    # ---- light spill ------------------------------------------------------
    if open_amt > 0.05:
        col = (200, 236, 255) if which2 else (255, 196, 158)
        ctx.ghost(radial_glow(460, col, 1.9), *cam.pt((dx0 + dx1) / 2, dy0 + 90),
                  alpha=0.42 * open_amt)
        w = (dx1 - dx0) * open_amt
        pen.poly([(dx0, dy1), (dx1, dy1), (dx1 + w * 0.9, dy1 + 86), (dx0 - w * 0.5, dy1 + 86)],
                 fill=tuple(int(c * 0.17) for c in col), outline=None)

    # ---- door leaf: hinged left, swings toward the viewer ------------------
    leaf_w = (dx1 - dx0) * (1 - 0.86 * open_amt)
    pen.poly([(dx0, dy1), (dx0, dy0), (dx0 + leaf_w, dy0 + 7 * (1 - open_amt)),
              (dx0 + leaf_w, dy1 - 5 * (1 - open_amt))],
             fill=(44, 36, 82), outline=(146, 126, 206), w=3)
    if open_amt > 0.35:
        # thin lit edge of the leaf catching the light from the other side
        pen.line([(dx0 + leaf_w, dy0 + 7 * (1 - open_amt)), (dx0 + leaf_w, dy1 - 5 * (1 - open_amt))],
                 fill=(210, 230, 255), w=2.2)
    pen.circle(dx0 + leaf_w - 14, (dy0 + dy1) / 2, 4, fill=(224, 200, 132))
    pen.line([(dx0 - 6, dy1), (dx0 - 6, dy0 - 6), (dx1 + 6, dy0 - 6), (dx1 + 6, dy1)],
             fill=C["cyan_lo"], w=2.8)
    # doormat
    pen.poly([(-70, FY + 6), (210, FY + 6), (232, FY + 44), (-92, FY + 44)],
             fill=(46, 34, 78), outline=(84, 66, 132), w=1.6)

    # ---- protagonist ------------------------------------------------------
    hip = FY - 66
    if p < 0.07:
        x, _ = walk(ctx, t, 0.0, 0.05 * ctx.dur, -250, -132, 0, 1.0)
        _, pp = walk(ctx, t, 0.0, 0.05 * ctx.dur, 0, 1, 0, 1.0)
    else:
        x = -132
        pp = seq(t, [
            (0.05 * ctx.dur, POSES["idle"]),
            (0.09 * ctx.dur, pose(la_u=84, la_f=90, face="neutral", torso=6)),
            (0.18 * ctx.dur, pose(la_u=90, la_f=96, face="wide", torso=7, head=-8)),
            (0.28 * ctx.dur, pose(la_u=92, la_f=104, face="shock", torso=2, head=-12, ra_u=-40, ra_f=-52)),
            (0.40 * ctx.dur, pose(la_u=92, la_f=104, face="shock", torso=4, head=-10, ra_u=-44, ra_f=-56)),
            (0.45 * ctx.dur, pose(la_u=74, la_f=96, ra_u=-74, ra_f=-96, face="scared", torso=-6, bob=-3)),
            (0.51 * ctx.dur, pose(la_u=32, la_f=44, ra_u=-32, ra_f=-44, face="wide", torso=2)),
            (0.58 * ctx.dur, pose(la_u=86, la_f=94, face="wide", torso=6)),
            (0.66 * ctx.dur, pose(la_u=118, ra_u=-30, ra_f=-38, face="confused", torso=-2, head=7)),
            (0.78 * ctx.dur, pose(la_u=150, la_f=158, face="confused", head=-9, torso=4)),
            (0.90 * ctx.dur, pose(face="deadpan", head=2, torso=7, la_u=44, ra_u=-24, ra_f=-30)),
            (1.01 * ctx.dur, pose(face="deadpan", head=3, torso=9, la_u=64, ra_u=-26, ra_f=-34)),
        ])
    char(ctx, x, hip, 1.0, pp, ground=FY, shadow=True, shadow_col=(12, 10, 26))

    ctx.fx["vignette"] = 0.52
    ctx.fx["scanlines"] = 0.18
    if 0.43 <= p <= 0.52:
        ctx.fx["flash"] = 0.30 * max(0.0, 1 - abs(p - 0.465) / 0.018)
        ctx.fx["flash_color"] = (255, 242, 225)
        ctx.fx["blocks"] = 2
    if p > 0.82:
        g = inv(0.82, 1.0, p)
        ctx.fx["rgb_split"] = 1.8 * g




# ================================================================= 4. STORE ===
def shelf(ctx, x, y, w, h, rows=4, cols=5, seed=1, t=0.0, face_label=True):
    """a shelving unit stocked with cartons that all wear the protagonist's face"""
    pen = ctx.pen
    pen.rrect(x, y - h, w, h, 4, fill=(226, 222, 236), outline=(150, 146, 168), lw=2.4)
    for r in range(rows):
        ry = y - h + h * (r + 1) / rows
        pen.rrect(x - 6, ry - 7, w + 12, 9, 2, fill=(178, 174, 196), outline=(140, 136, 160), lw=1.2)
        for c in range(cols):
            cw = w / cols
            bw = cw * (0.52 + hash01(seed, r, c) * 0.26)
            bh = (h / rows) * (0.5 + hash01(seed, r, c, 1) * 0.22)
            bx = x + cw * (c + 0.5) - bw / 2
            by = ry - bh - 8
            pal = [(252, 250, 244), (255, 214, 120), (170, 235, 205), (255, 176, 168),
                   (190, 210, 255), (236, 226, 255)][int(hash01(seed, r, c, 2) * 6) % 6]
            pen.rrect(bx, by, bw, bh, 2, fill=pal, outline=(70, 66, 92), lw=1.4)
            if face_label:
                hx, hy = bx + bw / 2, by + bh * 0.52
                hr = min(bw, bh) * 0.2
                pen.circle(hx, hy, hr, fill=(14, 12, 26))
                pen.circle(hx - hr * 0.35, hy - hr * 0.1, hr * 0.2, fill=C["white"])
                pen.circle(hx + hr * 0.35, hy - hr * 0.1, hr * 0.2, fill=C["white"])
                pen.line([(hx - hr * 0.35, hy + hr * 0.45), (hx + hr * 0.35, hy + hr * 0.45)],
                         fill=C["white"], w=max(0.8, hr * 0.16))


@scene("store")
def s_store(ctx, prm):
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 74
    base = vgrad(SW, SH, ((0.0, (150, 168, 190)), (0.22, (240, 242, 248)),
                          (0.62, (246, 246, 250)), (1.0, (196, 202, 218))))
    ctx.canvas.paste(base, (0, 0))
    vpx = 40
    # ---- ceiling band ----------------------------------------------------
    pen.poly([(-900, -352), (900, -352), (900, -420), (-900, -420)], fill=(206, 214, 228), outline=None)
    for i in range(4):
        lx = -170 + i * 130
        pen.rrect(lx, -392, 92, 9, 4, fill=(255, 252, 216), outline=(224, 220, 186), lw=1.2)
        ctx.ghost(radial_glow(300, (255, 250, 210), 1.6), *cam.pt(lx + 46, -386), alpha=0.30)
    # aisle sign
    pen.rrect(-92, -344, 176, 40, 6, fill=(96, 198, 186), outline=(46, 138, 130), lw=2.4)
    pen.wtext(-4, -324, "AISLE 9", 17, (10, 44, 42), font_name=E.F_DISPLAY)
    pen.wtext(120, -330, "DAIRY", 13, (60, 70, 96), font_name=E.F_UI)

    # ---- back wall -------------------------------------------------------
    pen.poly([(-900, FY), (-900, -352), (900, -352), (900, FY)], fill=(238, 238, 244), outline=None)
    for i in range(-6, 7):
        pen.line([(i * 96, FY), (i * 96, -352)], fill=(228, 228, 238), w=1.4)
    # promo posters on the back wall
    for i, px in enumerate((-236, 226)):
        pen.rrect(px - 44, -300, 88, 116, 4, fill=(255, 236, 246) if i else (226, 244, 255),
                  outline=(196, 176, 200) if i else (170, 196, 216), lw=2)
        pen.circle(px, -262, 20, fill=(16, 14, 28))
        pen.circle(px - 7, -265, 4.4, fill=C["white"])
        pen.circle(px + 7, -265, 4.4, fill=C["white"])
        pen.wtext(px, -224, "NIX" if i else "MILK", 15, (40, 34, 62), font_name=E.F_DISPLAY)

    # ---- the absurd hero product (dead centre, on its own stand) ---------
    reveal = inv(0.07, 0.21, p)
    cx = lerp(20, 24, ease(reveal))
    cy = lerp(FY - 74, -96, ease(reveal))
    scale = lerp(0.62, 1.18, ease(reveal))
    h, w = 146 * scale, 98 * scale
    # display plinth
    pen.poly([(cx - 34, FY), (cx + 34, FY), (cx + 26, -34), (cx - 26, -34)],
             fill=(228, 230, 240), outline=(176, 180, 196), w=2)
    pen.ellipse(cx, -34, 26, 6, fill=(244, 246, 252), outline=(176, 180, 196), w=1.6)
    Wd.carton(pen, cx, cy, w, h, col=(252, 252, 252), label=None)
    fr = w * 0.17
    fx, fy = cx, cy + h * 0.03
    pen.circle(fx, fy, fr, fill=(14, 12, 26))
    pen.circle(fx - fr * 0.36, fy - fr * 0.12, fr * 0.22, fill=C["white"])
    pen.circle(fx + fr * 0.36, fy - fr * 0.12, fr * 0.22, fill=C["white"])
    pen.line([(fx - fr * 0.30, fy + fr * 0.52), (fx + fr * 0.30, fy + fr * 0.44)],
             fill=C["white"], w=max(1.0, fr * 0.15))
    pen.wtext(cx, cy - h * 0.30, "NIX", 15 * scale, (26, 22, 44), font_name=E.F_DISPLAY)
    pen.wtext(cx, cy + h * 0.33, "MILK  ·  1 L", 7 * scale, (96, 92, 116))
    if reveal > 0.55:
        pen.rrect(cx - w * 0.75, cy - h * 0.75, w * 1.5, h * 1.5, 6,
                  outline=C["magenta"], lw=2.6)
    ctx.ghost(radial_glow(340, (255, 120, 210), 1.7), *cam.pt(cx, cy), alpha=0.16 * reveal)

    # ---- shelving --------------------------------------------------------
    for side in (-1, 1):
        for i in range(3):
            d = i / 3.0
            w_ = lerp(150, 92, d)
            h_ = lerp(210, 150, d)
            x = vpx + side * lerp(190, 96, d) - (w_ if side < 0 else 0)
            y = FY + 10 - i * 10
            shelf(ctx, x, y, w_, h_, rows=3, cols=2 if d > 0.5 else 3, seed=30 + i + side * 3, t=t)
    shelf(ctx, -150, FY, 128, 150, rows=3, cols=2, seed=41, t=t)

    # ---- floor -----------------------------------------------------------
    Wd.ground(ctx, FY, color=(198, 204, 220), top_line=(170, 178, 198))
    for i in range(-9, 10):
        pen.line([(i * 66, FY), (i * 132, FY + 330)], fill=(184, 190, 208), w=1.5)
    for k in range(1, 7):
        pen.line([(-900, FY + k * k * 5.5), (900, FY + k * k * 5.5)], fill=(184, 190, 208), w=1.3)
    # carton reflection
    pen.poly([(cx - w * 0.42, FY - 2), (cx + w * 0.42, FY - 2),
              (cx + w * 0.30, FY + 34), (cx - w * 0.30, FY + 34)],
             fill=(228, 228, 240), outline=None)

    # ---- frozen shopper --------------------------------------------------
    fp = dict(POSES["frozen"])
    fp.update(ll_u=24, rl_u=-20, la_u=52, ra_u=-44)
    char(ctx, 186, FY - 38, 0.58, fp, ground=FY, rim=(178, 178, 200),
         shadow=True, shadow_col=(178, 182, 198))

    # ---- character -------------------------------------------------------
    hip = FY - 62
    if p < 0.26:
        x, _ = walk(ctx, t, 0.02 * ctx.dur, 0.24 * ctx.dur, -230, -130, 0, 1.0, rate=2.5)
        _, pp = walk(ctx, t, 0.02 * ctx.dur, 0.24 * ctx.dur, 0, 1, 0, 1.0, rate=2.5)
    elif p < 0.70:
        x = -130
        pp = seq(t, [
            (0.26 * ctx.dur, pose(face="wide", look=1, torso=-2)),
            (0.34 * ctx.dur, pose(la_u=88, la_f=100, face="wide", torso=6, head=-6)),
            (0.44 * ctx.dur, pose(la_u=98, la_f=114, face="shock", torso=4, head=-10)),
            (0.54 * ctx.dur, pose(la_u=94, la_f=122, face="shock", torso=2, head=4)),
            (0.62 * ctx.dur, pose(la_u=42, la_f=62, face="confused", torso=-2)),
            (0.70 * ctx.dur, pose(la_u=34, la_f=88, ra_u=-34, ra_f=-88, face="shrug", head=-4)),
        ])
    else:
        x = -130
        pp = seq(t, [
            (0.70 * ctx.dur, pose(la_u=34, la_f=88, ra_u=-34, ra_f=-88, face="shrug", head=-4)),
            (0.78 * ctx.dur, pose(la_u=26, la_f=32, ra_u=-26, ra_f=-32, face="deadpan", head=5)),
            (0.84 * ctx.dur, pose(la_u=30, la_f=124, ra_u=-150, ra_f=-186, face="deadpan", head=9)),
            (1.01 * ctx.dur, pose(la_u=32, la_f=126, ra_u=-152, ra_f=-188, face="scared", head=11)),
        ])
    char(ctx, x, hip, 1.02, pp, ground=FY, shadow=True, shadow_col=(150, 154, 172),
         rim=C["violet"])

    ctx.fx["vignette"] = 0.42
    ctx.fx["scanlines"] = 0.14
    ctx.fx["grain"] = 3.4
    ctx.fx["contrast"] = 1.02
    if p > 0.74:
        g = inv(0.74, 1.0, p)
        ctx.fx["rgb_split"] = 2.2 * g
        ctx.fx["blocks"] = int(2 * g)
        ctx.fx["tint"] = (1.0 + 0.03 * g, 0.98, 1.0 + 0.05 * g)


# ========================================================= 5. REALITY FAILS ===
@scene("cityfail")
def s_cityfail(ctx, prm):
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 84
    # sky shifts colour as reality fails
    shift = ease(inv(0.06, 0.40, p))
    stops = (
        (0.0, (int(lerp(16, 34, shift)), int(lerp(14, 96, shift)), int(lerp(44, 176, shift)))),
        (0.42, (int(lerp(34, 92, shift)), int(lerp(26, 182, shift)), int(lerp(74, 232, shift)))),
        (0.72, (int(lerp(92, 178, shift)), int(lerp(40, 236, shift)), int(lerp(96, 255, shift)))),
        (1.0, (int(lerp(18, 26, shift)), int(lerp(16, 88, shift)), int(lerp(40, 150, shift)))),
    )
    Wd.sky(ctx, stops)
    Wd.stars(ctx, 60, seed=8, dim=0.8 + 0.2 * shift, y_max=0.5)

    Wd.skyline(ctx, cam.pt(0, FY - 20)[1], seed=31, color=(10, 9, 24), hmin=0.10, hmax=0.40,
               windows=True, win_color=C["magenta"], depth=1.0, t=t)
    Wd.skyline(ctx, cam.pt(0, FY - 10)[1], seed=33, color=(6, 6, 16), hmin=0.04, hmax=0.22,
               windows=True, win_color=C["cyan"], depth=0.6, t=t)
    Wd.ground(ctx, FY, color=(10, 9, 22), top_line=(84, 40, 92))
    for i in range(-10, 11):
        pen.line([(i * 60, FY), (i * 120, FY + 340)], fill=(20, 16, 40), w=1.4)
    # crossing + lamp post
    for k in range(6):
        pen.rrect(-260 + k * 96, FY + 12, 48, 10, 2, fill=(150, 150, 170), outline=None)
    pen.line([(250, FY), (250, -150)], fill=(60, 54, 90), w=5)
    pen.line([(250, -150), (206, -158)], fill=(60, 54, 90), w=5)
    ctx.ghost(radial_glow(360, (255, 210, 150), 1.5), *cam.pt(206, -150), alpha=0.5)
    Wd.lamp(ctx, 206, -152, color=C["amber"], size=1.1)

    # frozen traffic
    for i, (cx, cy, col) in enumerate(((-150, FY - 6, C["red"]), (54, FY - 4, C["cyan"]), (176, FY - 8, C["magenta"]))):
        pen.rrect(cx - 34, cy - 26, 68, 26, 8, fill=col, outline=(14, 12, 28), lw=2)
        pen.rrect(cx - 14, cy - 42, 30, 18, 6, fill=(210, 226, 255), outline=(14, 12, 28), lw=1.6)
        pen.circle(cx - 20, cy + 1, 6, fill=(20, 18, 34))
        pen.circle(cx + 20, cy + 1, 6, fill=(20, 18, 34))
    # frozen birds hanging in the sky
    for i in range(5):
        bx = -180 + i * 92
        by = -220 - (i % 3) * 46
        Wd.bird(pen, bx, by, 1.1, flap=1.0, col=(12, 10, 26), dirn=-1)
    # frozen pedestrians
    for i, px in enumerate((-250, 330)):
        fp = dict(POSES["frozen"])
        fp.update(ll_u=28 if i else -24, rl_u=-26 if i else 22, la_u=34, ra_u=-30, face="blank")
        char(ctx, px, FY - 44, 0.68, fp, rim=(120, 90, 150), shadow=True, shadow_col=(8, 7, 18))

    # ---- the protagonist --------------------------------------------------
    hip = FY - 62
    x = lerp(-60, -30, ease(p))
    pp = seq(t, [
        (0.0, pose(face="wide", head=-10, look=1, torso=-3, la_u=26, ra_u=-26)),
        (0.18 * ctx.dur, pose(face="shock", head=-16, look=1, torso=-5, la_u=40, la_f=48, ra_u=-40, ra_f=-48)),
        (0.34 * ctx.dur, pose(face="shock", head=-18, look=1, torso=-4, la_u=54, la_f=64, ra_u=-54, ra_f=-64)),
        (0.56 * ctx.dur, pose(face="scared", head=-12, look=1, torso=-2, la_u=44, ra_u=-44)),
        (0.74 * ctx.dur, pose(face="shock", head=-20, look=1, torso=-4, la_u=60, la_f=74, ra_u=-60, ra_f=-74)),
        (0.88 * ctx.dur, pose(face="wide", head=-14, look=1, torso=-2, la_u=34, ra_u=-34)),
        (1.01 * ctx.dur, pose(face="scared", head=-8, look=1, torso=0, la_u=28, ra_u=-28)),
    ])
    char(ctx, x, hip, 0.92, pp, ground=FY, shadow=True, shadow_col=(8, 7, 18), rim=C["magenta"])

    # ---- holographic system error ---------------------------------------
    a1 = inv(0.42, 0.49, p) * (1 - inv(0.61, 0.66, p))
    if a1 > 0.01:
        jitter = 3.0 * math.sin(t * 60)
        Wd.panel(ctx, x + jitter, -206, 300, 92, "REALITY UPDATE FAILED", col=C["magenta"],
                 alpha=a1, title_scale=0.92)
    a2 = inv(0.61, 0.68, p)
    if a2 > 0.01:
        Wd.panel(ctx, x, -206, 300, 92, "RESTARTING IN 100 DAYS", col=C["red"],
                 alpha=a2, title_scale=0.80)
    # scan sweep across the panel


    ctx.fx["vignette"] = 0.56
    ctx.fx["scanlines"] = 0.3
    if p > 0.06:
        g = clamp(shift)
        ctx.fx["rgb_split"] = 1.2 + 3.2 * g * (0.5 + 0.5 * math.sin(t * 9))
        ctx.fx["blocks"] = int(2 + 5 * g)
        ctx.fx["block_strength"] = 28 + 36 * g
    if 0.40 < p < 0.46 or 0.60 < p < 0.66:
        ctx.fx["flash"] = 0.10
        ctx.fx["flash_color"] = (200, 250, 255)
    # the freeze: a shockwave at "everyone froze", then the city's lights die
    if 0.70 < p < 0.95:
        fr = clamp((p - 0.70) / 0.22)
        rr = 60 + fr * 420
        col = tuple(int(c * (1 - fr)) for c in C["cyan"])
        pen.ellipse(x, FY - 2, rr, rr * 0.16, outline=col, w=2.4)
        pen.ellipse(x, FY - 2, rr * 0.62, rr * 0.10, outline=col, w=1.6)


# ============================================================= 6. THE CHICKEN ==
def police_officer(ctx, x, y, t):
    """frozen officer: cap, high-vis band, badge — still a stickman"""
    pen = ctx.pen
    fp = dict(POSES["frozen"])
    fp.update(ll_u=18, rl_u=-14, la_u=44, ra_u=-8, face="blank")
    anchors = char(ctx, x, y, 1.0, fp, rim=(70, 96, 150), shadow=True,
                   shadow_col=(9, 8, 20))
    hx, hy = anchors["head"]
    hr = anchors["head_r"]
    pen.poly([(hx - hr * 1.15, hy - hr * 0.55), (hx - hr * 0.85, hy - hr * 1.15),
              (hx + hr * 0.9, hy - hr * 1.1), (hx + hr * 1.2, hy - hr * 0.5)],
             fill=(30, 54, 110), outline=(16, 26, 60), w=2)
    pen.poly([(hx - hr * 1.25, hy - hr * 0.56), (hx + hr * 1.3, hy - hr * 0.52),
              (hx + hr * 1.3, hy - hr * 0.34), (hx - hr * 1.25, hy - hr * 0.40)],
             fill=(18, 32, 74), outline=None)
    # hi-vis chevron on the chest
    sx, sy = anchors["shoulder"]
    pen.line([(sx - 8, sy + 12), (sx + 8, sy + 24)], fill=C["amber"], w=3.0)
    pen.line([(sx + 8, sy + 12), (sx - 8, sy + 24)], fill=C["amber"], w=3.0)
    pen.circle(sx - 6, sy + 30, 2.6, fill=C["amber"])


def _city_street(ctx, t, FY, seed=51, win=C["cyan"]):
    pen, cam = ctx.pen, ctx.cam
    Wd.skyline(ctx, cam.pt(0, FY - 24)[1], seed=seed, color=(11, 10, 26), hmin=0.08,
               hmax=0.30, windows=True, win_color=win, depth=1.0, t=t)
    Wd.ground(ctx, FY, color=(13, 12, 28), top_line=(96, 62, 130))
    for i in range(-10, 11):
        pen.line([(i * 66, FY), (i * 132, FY + 330)], fill=(22, 18, 44), w=1.3)
    pen.poly([(-900, FY), (900, FY), (900, FY + 8), (-900, FY + 8)], fill=(120, 86, 156), outline=None)
    for k in range(5):
        pen.rrect(-420 + k * 190, FY + 46, 96, 9, 3, fill=(90, 76, 130), outline=None)


@scene("chicken")
def s_chicken(ctx, prm):
    """frozen officer -> the rock that becomes a chicken"""
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 84
    THROW = float(prm.get("throw", 0.62))
    HATCH = float(prm.get("hatch", 0.74))
    Wd.sky(ctx, ((0.0, (12, 14, 38)), (0.40, (44, 34, 92)), (0.74, (128, 62, 140)),
                 (1.0, (16, 12, 34))))
    Wd.stars(ctx, 50, seed=12, dim=0.7, y_max=0.45)
    _city_street(ctx, t, FY, seed=51)
    # street lamp
    pen.line([(-250, FY), (-250, -210)], fill=(58, 50, 88), w=5)
    pen.line([(-250, -210), (-206, -218)], fill=(58, 50, 88), w=5)
    ctx.ghost(radial_glow(360, (255, 208, 150), 1.5), *cam.pt(-206, -212), alpha=0.45)
    Wd.lamp(ctx, -206, -214, color=C["amber"], size=1.1)
    # the car he aims at
    pen.rrect(162, FY - 46, 96, 34, 8, fill=C["magenta"], outline=(14, 12, 28), lw=2)
    pen.rrect(178, FY - 66, 50, 22, 6, fill=(210, 226, 255), outline=(14, 12, 28), lw=1.6)
    pen.circle(182, FY - 8, 8, fill=(20, 18, 34))
    pen.circle(238, FY - 8, 8, fill=(20, 18, 34))
    # bin
    pen.rrect(-330, FY - 54, 54, 54, 6, fill=(40, 44, 66), outline=(78, 84, 110), lw=2.4)

    # ---- frozen officer --------------------------------------------------
    police_officer(ctx, 26, FY - 62, t)

    hip = FY - 62
    px = -140
    if THROW <= p <= 0.90:
        f = inv(THROW, 0.90, p)
        rx = lerp(px + 26, 208, f)
        ry = hip - 96 - math.sin(f * math.pi) * 74 + f * 20
        spin = f * 14
    else:
        rx, ry, spin = px + 26, hip - 100, 0.0

    pp = seq(t, [
        (0.00 * ctx.dur, pose(face="wide", head=4, look=1, la_u=26, ra_u=-26)),
        (0.10 * ctx.dur, pose(face="confused", head=4, look=1, la_u=40, la_f=52)),
        (0.20 * ctx.dur, POSES["wave"]),          # wave at the officer
        (0.30 * ctx.dur, POSES["wave2"]),
        (0.38 * ctx.dur, pose(face="deadpan", head=3, look=1, la_u=26, ra_u=-26)),
        (0.46 * ctx.dur, pose(face="deadpan", torso=18, la_u=40, la_f=52, ra_u=-8, ra_f=-4,
                              ll_u=30, ll_f=-46, rl_u=-18, rl_f=36, bob=12)),
        (0.52 * ctx.dur, pose(face="deadpan", torso=-6, ra_u=-26, ra_f=-18, la_u=20, la_f=26,
                              ll_u=-12, rl_u=8, bob=2)),
        (THROW * ctx.dur, POSES["throw"]),
        ((THROW + 0.05) * ctx.dur, pose(face="wide", torso=8, ra_u=-96, ra_f=-80, la_u=-30, la_f=-20)),
        (HATCH * ctx.dur, pose(face="shock", head=-14, look=1, torso=-4, la_u=52, la_f=64,
                               ra_u=-52, ra_f=-64)),
        ((HATCH + 0.08) * ctx.dur, pose(face="shock", head=-6, look=1, torso=0, la_u=40, ra_u=-40)),
        (0.90 * ctx.dur, pose(face="wide", head=6, look=1, torso=6, la_u=30, ra_u=-30)),
        (1.01 * ctx.dur, POSES["deadpan"]),
    ])
    char(ctx, px, hip, 0.98, pp, ground=FY, shadow=True, shadow_col=(10, 9, 22), rim=C["cyan"])

    # ---- rock -> chicken -------------------------------------------------
    if p < HATCH:
        if p >= THROW:
            pen.poly([(rx + math.cos(spin + k * 2.1) * 10, ry + math.sin(spin + k * 2.1) * 10)
                      for k in range(5)], fill=(146, 150, 168), outline=(58, 58, 78), w=2.0)
            for k in range(4):
                pen.circle(rx - 14 - k * 9, ry + 2 + k * 1.5, 3.5 - k * 0.6,
                           fill=(120, 124, 146), outline=None)
        elif p > THROW - 0.04:
            pen.circle(rx, ry, 6.5, fill=(146, 150, 168), outline=(58, 58, 78), w=1.8)
    else:
        fk = inv(THROW, 0.90, p)
        cxw = lerp(px + 26, 208, fk)
        cyw = hip - 96 - math.sin(fk * math.pi) * 74 + fk * 20
        Wd.glitch_pixels(ctx, cxw, cyw, 44, 40, t, inv(HATCH, HATCH + 0.06, p), seed=5)
        air = 1 - inv(HATCH, 0.90, p)
        flap = math.sin(t * 24) * air
        Wd.chicken(pen, cxw, cyw - 6 * air, 1.05, flap=flap, rot=0.2 * air)
        if 0.88 < p < 0.96:
            rr = inv(0.88, 0.96, p)
            pen.ellipse(208, FY - 6, 26 + rr * 44, (26 + rr * 44) * 0.3, outline=C["magenta"], w=2.2)
    if HATCH - 0.02 < p < HATCH + 0.10:
        for k in range(3):
            a = -0.6 + k * 0.55
            r0 = 54 + (t * 40 % 12)
            pen.line([(px + math.cos(a) * r0, hip - 100 + math.sin(a) * r0),
                      (px + math.cos(a) * (r0 + 18), hip - 100 + math.sin(a) * (r0 + 18))],
                     fill=C["cyan"], w=2.0)

    ctx.fx["vignette"] = 0.55
    ctx.fx["scanlines"] = 0.22
    if HATCH - 0.02 < p < HATCH + 0.05:
        g = 1 - abs(p - HATCH - 0.01) / 0.035
        ctx.fx["rgb_split"] = 5.0 * max(0, g)
        ctx.fx["blocks"] = int(5 * max(0, g))
        ctx.fx["flash"] = 0.10 * max(0, g)
        ctx.fx["flash_color"] = (255, 200, 255)


@scene("celebrate")
def s_celebrate(ctx, prm):
    """'world's most powerful idiot' — until he notices someone across the street"""
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 84
    Wd.sky(ctx, ((0.0, (14, 16, 42)), (0.40, (52, 36, 100)), (0.74, (140, 66, 138)),
                 (1.0, (18, 13, 36))))
    Wd.stars(ctx, 50, seed=13, dim=0.7, y_max=0.45)
    _city_street(ctx, t, FY, seed=52)
    pen.rrect(162, FY - 46, 96, 34, 8, fill=C["magenta"], outline=(14, 12, 28), lw=2)
    pen.circle(182, FY - 8, 8, fill=(20, 18, 34))

    hip = FY - 62
    # a little victory dance, then the double-take
    if p < 0.30:
        ph = (t * 3.4) % 1.0
        pp = pose(torso=-4 + math.sin(ph * 2 * math.pi) * 6, head=-10,
                  la_u=120 + math.sin(ph * 2 * math.pi) * 24, la_f=150,
                  ra_u=-120 - math.sin(ph * 2 * math.pi) * 24, ra_f=-150,
                  ll_u=14 * math.sin(ph * 2 * math.pi), rl_u=-14 * math.sin(ph * 2 * math.pi),
                  bob=abs(math.sin(ph * math.pi)) * -6, face="wide")
    elif p < 0.52:
        pp = seq(t, [
            (0.30 * ctx.dur, pose(torso=-6, head=-12, la_u=124, la_f=152, ra_u=-124, ra_f=-152,
                                  face="wide", bob=-6)),
            (0.40 * ctx.dur, pose(torso=-8, head=-16, la_u=150, la_f=168, ra_u=-150, ra_f=-168,
                                  face="wide", bob=-9)),
            (0.52 * ctx.dur, pose(torso=0, head=-6, la_u=40, la_f=52, ra_u=-40, ra_f=-52,
                                  face="wide", bob=0)),
        ])
    else:
        pp = seq(t, [
            (0.52 * ctx.dur, pose(torso=0, head=-6, la_u=40, la_f=52, ra_u=-40, ra_f=-52,
                                  face="wide", bob=0)),
            (0.64 * ctx.dur, pose(torso=-2, head=-10, look=1, la_u=32, ra_u=-32, face="wide")),
            (0.74 * ctx.dur, pose(torso=-4, head=-14, look=1, la_u=44, la_f=54, ra_u=-44,
                                  ra_f=-54, face="shock")),
            (0.86 * ctx.dur, pose(torso=-3, head=-12, look=1, la_u=38, ra_u=-38, face="wide")),
            (1.01 * ctx.dur, pose(torso=-2, head=-10, look=1, la_u=34, ra_u=-34, face="confused")),
        ])
    char(ctx, -70, hip, 1.0, pp, ground=FY, shadow=True, shadow_col=(10, 9, 22), rim=C["cyan"])

    # confetti-ish pixel sparks while celebrating
    if p < 0.34:
        for i in range(26):
            a = hash01(7, i, 1) * 6.28
            r = 30 + hash01(7, i, 2) * 60
            px_ = -70 + math.cos(a) * r
            py_ = hip - 90 + math.sin(a) * r * 0.7 - (t * 40 % 40)
            col = [C["cyan"], C["magenta"], C["amber"]][i % 3]
            pen.circle(px_, py_, 2.6, fill=col)
    # the silhouette appearing across the street
    if p > 0.60:
        a = ease(inv(0.60, 0.78, p))
        other = dict(POSES["frozen"])
        other.update(ll_u=2, rl_u=-2, la_u=6, ra_u=-6, face="blank")
        ox = lerp(320, 276, a)
        char(ctx, ox, FY - 60, 0.86, other, rim=C["magenta"], shadow=False)
        # a hint of glow so he reads as "someone else" at distance
        ctx.ghost(radial_glow(200, (255, 60, 190), 1.8), *cam.pt(ox, FY - 100),
                  alpha=0.18 * a)

    ctx.fx["vignette"] = 0.55
    ctx.fx["scanlines"] = 0.22


def draw_at(ctx, x, y, alpha, p_):
    """fade a figure in via a thin rim pass (keeps it ghostly at low alpha)"""
    from rig import draw_stickman
    rim = tuple(int(c * alpha) for c in C["magenta"])
    draw_stickman(ctx.pen, x, y, 0.9, p_, rim=rim, rim_w=1.0, shadow=False)


# ============================================================ 7. THE STRANGER ==
@scene("stranger")
def s_stranger(ctx, prm):
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 90
    POINT = float(prm.get("point", 0.30))
    PANEL = prm.get("panel", (0.72, 0.88))
    VANISH = float(prm.get("vanish", 0.86))
    Wd.sky(ctx, ((0.0, (10, 12, 34)), (0.38, (30, 26, 78)), (0.66, (96, 48, 118)),
                 (1.0, (12, 10, 28))))
    Wd.stars(ctx, 80, seed=22, dim=0.9, y_max=0.5)
    ctx.ghost(radial_glow(600, (180, 150, 255), 1.5), *cam.pt(268, -336), alpha=0.26)
    pen.circle(268, -336, 74, fill=(226, 212, 255), outline=None)
    pen.circle(248, -358, 62, fill=(14, 12, 34), outline=None)
    Wd.skyline(ctx, cam.pt(0, FY - 20)[1], seed=61, color=(9, 8, 22), hmin=0.06, hmax=0.26,
               windows=True, win_color=C["violet"], depth=1.0, t=t)
    Wd.ground(ctx, FY, color=(11, 10, 26), top_line=(92, 66, 140))
    for i in range(-10, 11):
        pen.line([(i * 70, FY), (i * 140, FY + 330)], fill=(20, 16, 42), w=1.3)
    pen.poly([(-900, FY - 2), (900, FY - 2), (900, FY + 10), (-900, FY + 10)],
             fill=(126, 92, 168), outline=None)

    sx_, sy_ = 96, FY - 168
    pen.line([(96, FY), (96, sy_ + 66)], fill=(58, 50, 92), w=5)
    pen.line([(96, sy_ + 66), (150, sy_ + 58)], fill=(58, 50, 92), w=4)

    vanish = inv(VANISH, min(1.0, VANISH + 0.10), p)
    if True:
        if p < POINT:
            other = dict(POSES["frozen"])
            other.update(torso=-8, head=6, la_u=6, ra_u=-6, ll_u=2, rl_u=-2, face="blank")
            # tiny idle sway so the audience sees he is *moving*
            other["head"] = 6 + math.sin(t * 2.2) * 3
            other["torso"] = -8 + math.sin(t * 1.7) * 2
        else:
            other = pose(torso=-4, head=-14, look=1, ra_u=-166, ra_f=-176, la_u=18, la_f=24,
                         face="blank")
            other["head"] = -14 + math.sin(t * 2.0) * 2
        char(ctx, sx_, sy_, 0.86, other, rim=C["magenta"], shadow=False)
    if vanish > 0.02:
        Wd.glitch_pixels(ctx, sx_, sy_ - 40, 70, 170, t, vanish, seed=9, col=C["magenta"])
        ctx.fx["blocks"] = int(6 * vanish)
        ctx.fx["rgb_split"] = 5.0 * vanish
    if POINT <= p < POINT + 0.10:
        rr = inv(POINT, POINT + 0.10, p)
        pen.circle(sx_, sy_ - 40, 40 + rr * 90, outline=C["magenta"], w=2.0)

    a = inv(PANEL[0], PANEL[0] + 0.05, p) * (1 - inv(PANEL[1], PANEL[1] + 0.05, p))
    if a > 0.01:
        jx = 2.5 * math.sin(t * 40)
        Wd.panel(ctx, sx_ + jx, sy_ - 150, 190, 62, "YOU'RE NOT REAL", col=C["magenta"],
                 alpha=a, title_scale=1.42, sub=None)

    hip = FY - 62
    x = lerp(-210, -168, ease(p))
    pp = seq(t, [
        (0.00 * ctx.dur, pose(face="wide", head=-6, look=1, torso=-2)),
        (0.10 * ctx.dur, pose(face="wide", head=-10, look=1, torso=-3, la_u=28, ra_u=-28)),
        (0.20 * ctx.dur, pose(face="shock", head=-14, look=1, torso=-4, la_u=44, la_f=54,
                              ra_u=-44, ra_f=-54)),
        (0.36 * ctx.dur, pose(face="shock", head=-16, look=1, torso=-6, la_u=56, la_f=68,
                              ra_u=-56, ra_f=-68)),
        (0.52 * ctx.dur, pose(face="scared", head=-12, look=1, torso=-4, la_u=48, ra_u=-48)),
        (0.70 * ctx.dur, pose(face="scared", head=-10, look=1, torso=-2, la_u=40, ra_u=-40)),
        (0.82 * ctx.dur, pose(face="wide", head=-6, look=1, torso=2, la_u=26, ra_u=-26)),
        (1.01 * ctx.dur, pose(face="confused", head=-2, torso=4, la_u=22, ra_u=-22)),
    ])
    char(ctx, x, hip, 0.98, pp, ground=FY, shadow=True, shadow_col=(9, 8, 20), rim=C["cyan"])

    ctx.fx["vignette"] = 0.64
    ctx.fx["scanlines"] = 0.26
    if p > 0.10:
        ctx.fx["tint"] = (1.0, 0.99, 1.03)


# ============================================================= 8. COUNTDOWN ===
@scene("countdown")
def s_countdown(ctx, prm):
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 96
    Wd.sky(ctx, ((0.0, (18, 16, 44)), (0.32, (52, 26, 84)), (0.60, (128, 40, 92)),
                 (0.78, (72, 26, 62)), (1.0, (16, 10, 28))))
    Wd.stars(ctx, 90, seed=31, dim=1.0, y_max=0.42)
    # warm haze on the horizon so the set never reads as a black frame
    horizon = cam.pt(0, FY - 40)[1]
    ctx.ghost(radial_glow(700, (255, 90, 120), 1.4), SW / 2, horizon, alpha=0.22)
    Wd.skyline(ctx, cam.pt(0, FY - 20)[1], seed=71, color=(14, 11, 28), hmin=0.10, hmax=0.34,
               windows=True, win_color=C["red"], depth=1.0, t=t)
    Wd.ground(ctx, FY, color=(20, 16, 34), top_line=(120, 54, 92))
    for i in range(-10, 11):
        pen.line([(i * 70, FY), (i * 140, FY + 330)], fill=(30, 20, 46), w=1.3)
    # a pool of cold light where he stands, so the silhouette reads
    ctx.ghost(radial_glow(420, (120, 90, 170), 1.6), *cam.pt(0, FY - 30), alpha=0.30)
    # ominous light shafts rising off the city (additive, so they glow)
    for k, bx in enumerate((-250, 250)):
        for j in range(14):
            f = j / 13.0
            py = FY - f * 330
            px = bx + math.sin(t * 0.5 + k + f * 2) * 26 * f
            ctx.ghost(radial_glow(150, (255, 60, 90), 2.0), *cam.pt(px, py),
                      alpha=0.05 * (1 - f * 0.6))

    days, hours, minutes = Wd.countdown_state(ctx.t0 + ctx.lt)
    app = ease(inv(0.10, 0.34, p))
    if app > 0.02:
        sc = lerp(0.72, 1.0, app)
        Wd.countdown(ctx, 0, -196, days, hours, minutes, scale=sc, alpha=app)
        # the timer's own light
        ctx.ghost(radial_glow(560, (255, 60, 90), 2.0), *cam.pt(0, -196), alpha=0.28 * app)

    # ---- protagonist -----------------------------------------------------
    hip = FY - 62
    x = lerp(-16, -4, ease(p))
    pp = seq(t, [
        (0.0, pose(face="wide", head=-4, torso=0, la_u=22, ra_u=-22)),
        (0.20 * ctx.dur, pose(face="wide", head=-16, look=1, torso=-3)),
        (0.38 * ctx.dur, pose(face="shock", head=-26, look=1, torso=-6, la_u=30, ra_u=-30)),
        (0.52 * ctx.dur, pose(face="shock", head=-28, look=1, torso=-5, la_u=38, ra_u=-38)),
        (0.70 * ctx.dur, pose(face="scared", head=-22, look=1, torso=-4, la_u=30, ra_u=-30)),
        (0.86 * ctx.dur, pose(face="scared", head=-16, look=1, torso=-2, la_u=26, ra_u=-26)),
        (1.01 * ctx.dur, pose(face="wide", head=-12, look=1, torso=0, la_u=24, ra_u=-24)),
    ])
    char(ctx, x, hip, 1.0, pp, ground=FY, shadow=True, shadow_col=(8, 7, 18), rim=C["red"])

    # environment distortion: subtle horizontal band drift
    ctx.fx["vignette"] = 0.66
    ctx.fx["scanlines"] = 0.3
    ctx.fx["contrast"] = 1.04
    ctx.fx["tint"] = (1.03, 0.97, 1.0)
    if 0.10 < p < 0.20:
        g = 1 - abs(p - 0.15) / 0.05
        ctx.fx["blocks"] = int(4 * max(0, g))
        ctx.fx["rgb_split"] = 4.0 * max(0, g)
        ctx.fx["flash"] = 0.08 * max(0, g)
        ctx.fx["flash_color"] = (255, 120, 140)


# =============================================================== 9. THE CHOICE ==
@scene("choice")
def s_choice(ctx, prm):
    """
    Two beats share this set:
      * cards=False -> a wide, slow push between the building and the rift
      * cards=True  -> a game-style choice screen (A / B) with the timer overhead
    """
    p, t = ctx.p, ctx.lt
    pen, cam = ctx.pen, ctx.cam
    FY = 74
    show_cards = bool(prm.get("cards", False))

    # ---- option A: the industrial building -------------------------------
    bx0, bx1 = -188, -70
    pen.poly([(bx0, FY), (bx0, -226), (bx1, -226), (bx1, FY)],
             fill=(26, 23, 42), outline=(104, 76, 116), w=3)
    for i in range(3):
        pen.rrect(bx0 + 22 + i * 40, -246, 20, 20, 2, fill=(34, 30, 52),
                  outline=(92, 68, 104), lw=1.5)
        if hash01(4, i) > 0.3:
            ctx.ghost(radial_glow(130, (255, 90, 70), 1.8),
                      *cam.pt(bx0 + 32 + i * 40, -236), alpha=0.55)
    for sx_ in (bx0 + 32, bx0 + 86):
        pen.poly([(sx_ - 10, -248), (sx_ + 10, -248), (sx_ + 8, -348), (sx_ - 8, -348)],
                 fill=(30, 26, 46), outline=(96, 72, 108), w=2)
        ctx.ghost(radial_glow(170, (140, 110, 160), 1.6), *cam.pt(sx_, -356), alpha=0.30)
    dx = bx0 + 62
    pen.rrect(dx, FY - 86, 44, 86, 3, fill=(52, 24, 26), outline=C["red"], lw=2.8)
    pen.poly([(dx + 14, FY - 86), (dx + 24, FY - 86), (dx + 8, FY), (dx - 2, FY)],
             fill=(96, 32, 32), outline=None)
    for k in range(4):
        pen.line([(bx0 + 16 + k * 36, FY - 4), (bx0 + 28 + k * 36, FY - 20)],
                 fill=C["amber"], w=3)
    ctx.ghost(radial_glow(320, (255, 60, 60), 1.8), *cam.pt(dx + 22, FY - 62), alpha=0.30)

    # ---- option B: the rift where the stranger vanished -------------------
    rx_, ry_ = 132, FY - 108
    ctx.ghost(radial_glow(420, (255, 60, 190), 1.5), *cam.pt(rx_, ry_), alpha=0.42)
    for k in range(3):
        rr = 52 + k * 13 + math.sin(t * 2 + k) * 4
        pen.ellipse(rx_, ry_, rr * 0.52, rr, outline=C["magenta"] if k == 0 else C["violet"], w=2.8)
    pen.ellipse(rx_, ry_, 26, 58, fill=(58, 22, 78), outline=C["magenta"], w=2.2)
    Wd.glitch_pixels(ctx, rx_, ry_, 58, 128, t, 0.5 + 0.5 * math.sin(t * 3), seed=13,
                     col=C["cyan"])
    # a cold pool of light spilling out onto the road
    pen.ellipse(rx_, FY - 2, 70, 12, fill=(46, 24, 60), outline=(140, 70, 150), w=1.6)

    # ---- ground ----------------------------------------------------------
    Wd.ground(ctx, FY, color=(16, 14, 34), top_line=(112, 66, 110))
    for i in range(-9, 10):
        pen.line([(i * 40, FY), (i * 80, FY + 260)], fill=(23, 18, 44), w=1.3)
    for k in range(1, 7):
        pen.line([(-500, FY + k * k * 5.0), (500, FY + k * k * 5.0)], fill=(23, 18, 44), w=1.2)
    pen.poly([(bx0 - 4, FY), (bx1 + 4, FY), (bx1 + 30, FY + 92), (bx0 - 28, FY + 92)],
             fill=(62, 22, 26), outline=None)
    pen.poly([(rx_ - 44, FY), (rx_ + 44, FY), (rx_ + 58, FY + 88), (rx_ - 52, FY + 88)],
             fill=(56, 18, 62), outline=None)
    for k in range(3):
        pen.line([(rx_ - 34 + k * 12, FY + 8), (rx_ - 40 + k * 14, FY + 74)],
                 fill=(160, 54, 150), w=1.6)
    pen.poly([(-500, FY), (500, FY), (500, FY + 14), (-500, FY + 14)],
             fill=(54, 36, 76), outline=None)
    for fx_ in (-300, 300):
        pen.rrect(fx_ - 8, FY + 24, 16, 60, 4, fill=(30, 26, 52), outline=(72, 58, 98), lw=1.6)
        pen.circle(fx_, FY + 24, 4, fill=C["amber"])

    # ---- countdown overhead ---------------------------------------------
    cd_d, cd_h, cd_m = Wd.countdown_state(ctx.t0 + ctx.lt)   # absolute film time
    Wd.countdown(ctx, -34, -252, cd_d, cd_h, cd_m,
                 scale=0.78 if show_cards else 0.62, alpha=0.92)

    # ---- character between the two paths ---------------------------------
    hip = FY - 62
    pp = seq(t, [
        (0.0, pose(face="deadpan", head=2, torso=2, la_u=24, ra_u=-24)),
        (0.16 * ctx.dur, pose(face="wide", head=-4, look=-1, torso=-2, la_u=28, ra_u=-28)),
        (0.34 * ctx.dur, pose(face="wide", head=-2, look=1, torso=2, la_u=30, ra_u=-30)),
        (0.52 * ctx.dur, pose(face="confused", head=-6, look=1, torso=-2, la_u=34, ra_u=-34)),
        (0.68 * ctx.dur, pose(face="confused", head=4, look=-1, torso=2, la_u=30, ra_u=-30)),
        (0.84 * ctx.dur, pose(face="deadpan", head=0, torso=0, la_u=26, ra_u=-26)),
        (1.01 * ctx.dur, pose(face="deadpan", head=-2, torso=-1, la_u=25, ra_u=-25)),
    ])
    char(ctx, -22, hip, 1.0, pp, ground=FY, shadow=True, shadow_col=(7, 6, 16), rim=C["violet"])

    # ---- the choice screen ----------------------------------------------
    if show_cards:
        a_at = float(prm.get("a_at", ctx.t0 + 0.2 * ctx.dur))
        b_at = float(prm.get("b_at", ctx.t0 + 0.5 * ctx.dur))
        la = ease(clamp((ctx.t - a_at) / 0.30))
        lb = ease(clamp((ctx.t - b_at) / 0.30))
        # darken the set so the interface reads like a menu, not a caption
        if la > 0.01:
            ctx.fx["dim"] = 0.18 + 0.20 * max(la, lb)
        _option_card(ctx, 0, 1105, "A", "INVESTIGATE THE BUILDING", C["red"], la,
                     active=la > 0.5, glow=True)
        _option_card(ctx, 1, 1215, "B", "FIND THE MYSTERIOUS STICKMAN", C["magenta"], lb,
                     active=lb > 0.5, glow=True)
    else:
        # slow push between the two options (no labels yet)
        pass

    ctx.fx["vignette"] = 0.64
    ctx.fx["scanlines"] = 0.24
    if not show_cards:
        ctx.fx["contrast"] = 1.03


def _option_card(ctx, slot, y_px, letter, text, col, alpha, active=True, glow=True):
    """
    Screen-space option card: index number + label, with an accent bar and a
    bright/dim state so the viewer can tell which option is being described.
    """
    if alpha <= 0.02:
        return
    d = ctx.pen.d
    w, h = 880.0, 104.0
    x0 = (W - w) / 2.0
    y0 = y_px - h / 2.0
    # slide in from the outside
    slide = (1 - alpha) * 46.0 * (1 if slot == 0 else -1)
    x0 += slide
    fill = (14, 10, 24) if active else (10, 8, 18)
    edge = col if active else tuple(int(c * 0.45) for c in col)
    d.rectangle([x0 * SS, y0 * SS, (x0 + w) * SS, (y0 + h) * SS],
                fill=fill, outline=edge, width=int((2.6 if active else 1.6) * SS))
    d.rectangle([x0 * SS, y0 * SS, (x0 + 8) * SS, (y0 + h) * SS], fill=edge)
    if glow and active:
        g = E.radial_glow(300, col, 2.2).resize((int(w * 1.1), int(h * 3.0)))
        ctx.ghost(g, (x0 + w / 2) * SS, y_px * SS, alpha=0.10)
    f1 = font(E.F_DISPLAY, int(74 * SS))
    d.text(((x0 + 34) * SS, (y0 + h / 2) * SS), letter, font=f1, fill=edge, anchor="lm")
    f2 = font(E.F_UI, int(30 * SS))
    words = text.split()
    if len(words) >= 4:
        l1, l2 = " ".join(words[:2]), " ".join(words[2:])
        d.text(((x0 + 108) * SS, (y0 + h * 0.33) * SS), l1, font=f2,
               fill=C["white"] if active else (214, 216, 232), anchor="lm")
        d.text(((x0 + 108) * SS, (y0 + h * 0.69) * SS), l2, font=f2,
               fill=C["white"] if active else (214, 216, 232), anchor="lm")
    else:
        d.text(((x0 + 108) * SS, (y0 + h / 2) * SS), text, font=f2,
               fill=C["white"] if active else (214, 216, 232), anchor="lm")

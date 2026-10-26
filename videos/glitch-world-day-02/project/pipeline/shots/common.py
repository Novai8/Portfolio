"""Shared shot helpers."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease

def street_world(parallax=(0, 0, 0)):
    """Cached street environment with optional per-layer parallax offsets."""
    img = D.vgrad((C.W, C.H), world.SKY_STREET)
    layers = world.city_layers()
    shifts = (10, 26, 52)
    for i, l in enumerate(layers):
        img.alpha_composite(l, (int(parallax[i] * shifts[i]), 0))
    img.alpha_composite(world.street_ground())
    return img

def hero_tag(img, head_center, head_r, alpha=205):
    """Floating protagonist countdown — continuity with Day 1, never zero."""
    tag = world.head_countdown(alpha=alpha)
    x = int(head_center[0] - tag.width / 2)
    y = int(head_center[1] - head_r - tag.height - 26)
    img.alpha_composite(tag, (x, y))

def traffic_light(x=872, base=1480, phase=0.0):
    """Wrong-sequence traffic signal. phase in seconds."""
    img = D.layer(); d = ImageDraw.Draw(img)
    D.line(d, (x, base), (x, base - 620), (12, 14, 26), 12)
    bx0, bx1 = x - 34, x + 34
    d.rounded_rectangle([bx0, base - 760, bx1, base - 560], 16,
                        fill=(16, 18, 30), outline=(80, 92, 120, 180), width=3)
    seq = [0, 2, 1, 0, 1, 2]  # intentionally nonsensical order
    active = seq[int(phase / 0.9) % len(seq)]
    cols = [(214, 70, 84), (255, 196, 96), (96, 226, 150)]
    for i, col in enumerate(cols):
        cy = base - 720 + i * 66
        on = i == active
        d.ellipse([x - 20, cy - 20, x + 20, cy + 20],
                  fill=col + (255 if on else 42,))
        if on:
            img.alpha_composite(D.radial((C.W, C.H), (x, cy), 70, col, 90, 1.8))
    return img

def backward_cloud(t):
    img = D.layer(); d = ImageDraw.Draw(img)
    x = (C.W + 300 - t * 70) % (C.W + 600) - 300  # drifts right -> left
    y = 260 + 30 * math.sin(t * 0.5)
    for dx, dy, r in ((0, 0, 70), (60, 12, 52), (-64, 16, 46), (110, 22, 34)):
        d.ellipse([x + dx - r, y + dy - r * .55, x + dx + r, y + dy + r * .55],
                  fill=(170, 180, 220, 26))
    return img

def sign_glyphs(t, x=120, y=1380):
    """Storefront digital sign that briefly shows wrong symbols (kept above sub zone)."""
    img = D.layer(); d = ImageDraw.Draw(img)
    glitch = (5.6 < t < 6.05) or (8.8 < t < 9.2)
    f = D.font("display", 34, "Bold")
    txt = "?#%&@" if glitch else "OPEN"
    col = C.MAGENTA + (230,) if glitch else C.CYAN + (200,)
    d.rounded_rectangle([x - 20, y - 50, x + 220, y + 24], 8, fill=(10, 14, 30, 235),
                        outline=col, width=2)
    d.text((x, y - 40), txt, font=f, fill=col)
    return img

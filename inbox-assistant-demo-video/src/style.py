"""Design system: colors, fonts, easing, layout constants."""
import math, os
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 30
DURATION = 164.0                      # seconds (VO is 163.0 + resolve tail)
N_FRAMES = int(DURATION * FPS)
MARGIN = 0.08                         # title-safe margin
SAFE_X0, SAFE_X1 = int(W * MARGIN), int(W * (1 - MARGIN))   # 153.6 -> 153, 1766
SAFE_Y0, SAFE_Y1 = int(H * MARGIN), int(H * (1 - MARGIN))   # 86.4 -> 86, 993

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts", "inter41", "extras", "ttf")

def _fp(name):
    return os.path.join(FONT_DIR, f"Inter-{name}.ttf")

_fcache = {}
def F(weight, size):
    """Cached Inter font. weight in Regular/Medium/SemiBold/Bold/ExtraBold/Black"""
    key = (weight, size)
    if key not in _fcache:
        _fcache[key] = ImageFont.truetype(_fp(weight), size)
    return _fcache[key]

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# ---------- Section palettes ----------
PAL = {
    "A": dict(bg="#F7F4F0", text="#111827", sub="#6B7280", accent="#FF8A3D",
              warn="#EF5B5B", card="#FFFFFF", line="#E7E0D8", chipbg="#FFF1E6"),
    "B": dict(bg="#F6F9FF", text="#0F172A", sub="#5B6472", primary="#4C6FFF",
              secondary="#7C5CFC", success="#19B89D", card="#FFFFFF", line="#DDE6F7",
              chipbg="#EAF0FF"),
    "C": dict(bg="#FFF9ED", text="#1F1A10", sub="#7A6A4F", accent="#F5A524",
              card="#FFFFFF", line="#F0E2C4", chipbg="#FFF3D9", success="#19B89D",
              warn="#EF5B5B"),
    "D": dict(bg="#0B1220", text="#EAF2FF", sub="#93A4BF", accent="#46C7FF",
              success="#36D399", card="#121C30", line="#22314E", chipbg="#15233C"),
}
for k in PAL:
    PAL[k] = {kk: (hex2rgb(vv) if isinstance(vv, str) else vv) for kk, vv in PAL[k].items()}

# ---------- Easing ----------
def clamp01(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)

def linear(t): return clamp01(t)

def ease_out_expo(t):
    t = clamp01(t)
    return 1.0 if t >= 1 else 1 - math.pow(2, -10 * t)

def ease_in_cubic(t):
    t = clamp01(t); return t * t * t

def ease_out_cubic(t):
    t = clamp01(t); return 1 - (1 - t) ** 3

def ease_in_out_cubic(t):
    t = clamp01(t)
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

def ease_out_back(t, c1=0.9):
    """Small overshoot (~2-4%)."""
    t = clamp01(t); c3 = c1 + 1
    return 1 + c3 * pow(t - 1, 3) + c1 * pow(t - 1, 2)

def anim(t, start, dur, ease=ease_out_expo):
    """Progress 0..1 of an animation starting at `start`, lasting `dur`."""
    if dur <= 0: return 1.0 if t >= start else 0.0
    return ease((t - start) / dur)

def seg_anim(t, start, dur, hold, ease_in=ease_out_expo, ease_out=ease_in_cubic):
    """Enter over dur, hold, then exit. Returns (presence 0..1, exit_progress)."""
    if t < start: return 0.0
    if t < start + dur: return ease_in((t - start) / dur)
    if t < start + dur + hold: return 1.0
    e = (t - start - dur - hold) / max(dur * 0.7, 0.25)
    if e >= 1: return 0.0
    return 1.0 - ease_out(e)

def lerp(a, b, p): return a + (b - a) * p

def mix_rgb(c1, c2, p):
    return tuple(int(round(lerp(c1[i], c2[i], p))) for i in range(3))

"""Easing functions and small interpolation helpers."""
import math
from PIL import Image

def linear(t): return t
def in_quad(t): return t * t
def out_quad(t): return 1 - (1 - t) ** 2
def in_out_quad(t): return 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2
def in_cubic(t): return t ** 3
def out_cubic(t): return 1 - (1 - t) ** 3
def in_out_cubic(t): return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def out_quart(t): return 1 - (1 - t) ** 4
def in_out_quart(t): return 8 * t ** 4 if t < .5 else 1 - (-2 * t + 2) ** 4 / 2
def out_quint(t): return 1 - (1 - t) ** 5
def in_out_sine(t): return -(math.cos(math.pi * t) - 1) / 2
def out_back(t):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2
def out_elastic(t):
    if t in (0, 1): return t
    return math.pow(2, -10 * t) * math.sin((t * 10 - .75) * (2 * math.pi / 3)) + 1
def hold(t): return 0.0 if t < 1 else 1.0

def clamp01(t): return max(0.0, min(1.0, t))

def maprange(t, a, b):
    """map t in [a,b] -> [0,1] clamped."""
    if b == a: return 0.0
    return clamp01((t - a) / (b - a))

def lerp(a, b, t): return a + (b - a) * t

def mix_pose(p1, p2, t):
    out = dict(p1)
    for k, v in p2.items():
        out[k] = lerp(p1.get(k, 0.0), v, t) if isinstance(v, (int, float)) else v
    return out

def pulse(t, period, duty=0.5):
    """0/1 square-ish pulse with smooth edges."""
    ph = (t % period) / period
    if ph < duty:
        return in_out_quad(maprange(ph, 0, min(.08, duty / 2))) if ph < .08 else 1.0
    return 0.0

def pose_at(keyframes, t, easing=in_out_cubic):
    """Interpolate numeric pose fields across (time, dict) keyframes.

    Non-numeric values (eye/mouth strings) are held from the latest keyframe.
    """
    if t <= keyframes[0][0]:
        return dict(keyframes[0][1])
    if t >= keyframes[-1][0]:
        return dict(keyframes[-1][1])
    for i in range(1, len(keyframes)):
        t1, p1 = keyframes[i]
        if t <= t1:
            t0, p0 = keyframes[i - 1]
            u = easing(clamp01((t - t0) / max(1e-6, t1 - t0)))
            out = dict(p0)
            for k, v in p1.items():
                if isinstance(v, (int, float)) and isinstance(p0.get(k), (int, float)):
                    out[k] = lerp(p0[k], v, u)
                else:
                    out[k] = v if u >= 1.0 else p0.get(k, v)
            return out
    return dict(keyframes[-1][1])

def camera_push(t, dur, amount=0.07, w=1080, h=1920):
    """Return (scale, dx, dy) for a slow push-in centered on the frame."""
    u = out_quart(maprange(t, 0, dur))
    s = 1.0 + amount * u
    return s, -w * (s - 1) / 2, -h * (s - 1) / 2

def place_camera(base, world, scale, dx, dy):
    if scale != 1.0:
        world = world.resize((int(world.width * scale), int(world.height * scale)), Image.BILINEAR)
    base.alpha_composite(world, (int(dx), int(dy)))
    return base

C_W = 1080

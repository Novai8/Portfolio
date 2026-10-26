"""
engine.py — a small cinematic 2D renderer built on Pillow + NumPy.

Everything in the film is drawn procedurally: vector shapes for the world and
the stickman, numpy passes for glitch/grade effects, Pillow for typography.
No external video, image or audio assets are required (fonts + the supplied
voiceover are the only inputs), which keeps the project fully reproducible.

Coordinate systems
------------------
* world units   : arbitrary; the stickman is ~190 world units tall
* canvas px     : world rendered through a Camera, supersampled by SS
* output px     : 1080x1920, after downscale + effects + typography
"""
from __future__ import annotations

import math
import os
import subprocess
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- constants ---
W, H = 1080, 1920          # output
FPS = 30
SS = 1.6                   # supersample factor for vector art
SW, SH = int(W * SS), int(H * SS)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.join(ROOT, "assets", "fonts")

C = {
    "ink":        (7, 5, 14),
    "ink_soft":   (18, 14, 32),
    "night":      (12, 14, 34),
    "deep":       (22, 18, 54),
    "violet":     (108, 62, 220),
    "violet_lo":  (58, 34, 128),
    "cyan":       (0, 232, 255),
    "cyan_lo":    (0, 130, 170),
    "magenta":    (255, 52, 184),
    "magenta_lo": (150, 24, 110),
    "red":        (255, 62, 74),
    "amber":      (255, 196, 72),
    "white":      (245, 248, 255),
    "milk":       (238, 240, 250),
    "orange":     (255, 138, 46),
}


# ------------------------------------------------------------------- maths ---
def clamp(x, lo=0.0, hi=1.0):
    return lo if x < lo else hi if x > hi else x


def lerp(a, b, t):
    return a + (b - a) * t


def inv(a, b, x):
    """normalised position of x in [a,b]"""
    if b == a:
        return 0.0
    return clamp((x - a) / (b - a))


def ease(t, kind="inout"):
    t = clamp(t)
    if kind == "linear":
        return t
    if kind == "in":
        return t * t * t
    if kind == "out":
        return 1 - (1 - t) ** 3
    if kind == "inout":
        return t * t * (3 - 2 * t)
    if kind == "sine":
        return 0.5 - 0.5 * math.cos(math.pi * t)
    if kind == "back":
        c = 1.70158
        return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2
    if kind == "elastic":
        if t <= 0 or t >= 1:
            return t
        return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi / 3)) + 1
    if kind == "expo":
        return 1 if t >= 1 else 1 - 2 ** (-10 * t)
    return t


def kf(t, keys, kind="inout"):
    """keyframe interpolation. keys = [(time, value), ...] with numeric values."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, ease(inv(t0, t1, t), kind))
    return keys[-1][1]


def kf_list(t, keys, kind="inout"):
    """keyframes whose values are tuples."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            e = ease(inv(t0, t1, t), kind)
            return tuple(lerp(a, b, e) for a, b in zip(v0, v1))
    return keys[-1][1]


def pulse(t, freq, lo=0.0, hi=1.0, phase=0.0):
    return lerp(lo, hi, 0.5 + 0.5 * math.sin(2 * math.pi * freq * t + phase))


def hash01(*args):
    """deterministic pseudo-random in [0,1)"""
    h = 2166136261
    for a in args:
        h ^= int((a * 1e6) if isinstance(a, float) else a) & 0xFFFFFFFF
        h = (h * 16777619) & 0xFFFFFFFF
    return (h % 100000) / 100000.0


# ----------------------------------------------------------------- colormap ---
@lru_cache(maxsize=64)
def vgrad(w, h, stops):
    """vertical gradient. stops = ((pos, (r,g,b)), ...)"""
    ys = np.linspace(0, 1, h)
    arr = np.zeros((h, w, 3), dtype=np.float32)
    for i in range(len(stops) - 1):
        p0, c0 = stops[i]
        p1, c1 = stops[i + 1]
        m = (ys >= p0) & (ys <= p1)
        if not m.any():
            continue
        f = ((ys[m] - p0) / max(1e-6, p1 - p0))[:, None, None]
        arr[m] = np.array(c0)[None, None, :] * (1 - f) + np.array(c1)[None, None, :] * f
    return Image.fromarray(arr.astype(np.uint8), "RGB")


@lru_cache(maxsize=32)
def radial_glow(size, color, hardness=2.0):
    """soft round glow sprite (RGBA) used for lights, halos, particles."""
    s = int(size)
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    d = np.sqrt((xx - s / 2) ** 2 + (yy - s / 2) ** 2) / (s / 2)
    a = np.clip(1 - d, 0, 1) ** hardness
    rgba = np.zeros((s, s, 4), dtype=np.uint8)
    rgba[..., 0], rgba[..., 1], rgba[..., 2] = color
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


# -------------------------------------------------------------------- fonts ---
@lru_cache(maxsize=128)
def font(name, px):
    path = os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, int(px))


F_SUB = "Inter-ExtraBold.ttf"
F_UI = "Inter-Bold.ttf"
F_BLACK = "Inter-Black.ttf"
F_MONO = "JetBrainsMono-Bold.ttf"
F_DISPLAY = "BebasNeue-Regular.ttf"


# ------------------------------------------------------------------- camera ---
class Cam:
    """world -> supersampled canvas transform"""

    def __init__(self, cx=0.0, cy=0.0, zoom=8.0, shake=(0.0, 0.0), roll=0.0):
        self.cx, self.cy, self.zoom = cx, cy, zoom
        self.shake = shake
        self.roll = roll

    def pt(self, x, y):
        sx = (x - self.cx) * self.zoom + SW / 2 + self.shake[0]
        sy = (y - self.cy) * self.zoom + SH / 2 + self.shake[1]
        if self.roll:
            c, s = math.cos(self.roll), math.sin(self.roll)
            dx, dy = sx - SW / 2, sy - SH / 2
            sx, sy = SW / 2 + dx * c - dy * s, SH / 2 + dx * s + dy * c
        return sx, sy

    def xy(self, x, y):
        return self.pt(x, y)

    def sc(self, v):
        return v * self.zoom


def shake_offset(t, amp=6.0, freq=26.0, seed=0):
    if amp <= 0:
        return (0.0, 0.0)
    a = hash01(seed, int(t * freq))
    b = hash01(seed + 7, int(t * freq))
    return ((a - 0.5) * 2 * amp * SS, (b - 0.5) * 2 * amp * SS)


# ---------------------------------------------------------------------- pen ---
class Pen:
    """thin drawing wrapper: everything goes through the camera."""

    def __init__(self, draw: ImageDraw.ImageDraw, cam: Cam):
        self.d = draw
        self.cam = cam

    # -- primitives ---------------------------------------------------------
    def line(self, pts, fill=(0, 0, 0), w=2.0, cap=True):
        sp = [self.cam.pt(x, y) for x, y in pts]
        lw = max(1, int(round(w * self.cam.zoom)))
        self.d.line(sp, fill=fill, width=lw, joint="curve" if len(sp) > 2 else None)
        if cap:
            r = lw / 2.0
            for (x, y) in (sp[0], sp[-1]):
                self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def circle(self, x, y, r, fill=None, outline=None, w=2.0):
        sx, sy = self.cam.pt(x, y)
        rr = r * self.cam.zoom
        lw = max(1, int(round(w * self.cam.zoom)))
        self.d.ellipse([sx - rr, sy - rr, sx + rr, sy + rr], fill=fill,
                       outline=outline, width=lw)

    def ellipse(self, x, y, rx, ry, fill=None, outline=None, w=2.0):
        sx, sy = self.cam.pt(x, y)
        self.d.ellipse([sx - rx * self.cam.zoom, sy - ry * self.cam.zoom,
                        sx + rx * self.cam.zoom, sy + ry * self.cam.zoom],
                       fill=fill, outline=outline,
                       width=max(1, int(round(w * self.cam.zoom))))

    def poly(self, pts, fill=None, outline=None, w=2.0):
        sp = [self.cam.pt(x, y) for x, y in pts]
        self.d.polygon(sp, fill=fill, outline=outline,
                       width=max(1, int(round(w * self.cam.zoom))))

    def rrect(self, x, y, w_, h_, r, fill=None, outline=None, lw=2.0):
        x0, y0 = self.cam.pt(x, y)
        x1, y1 = self.cam.pt(x + w_, y + h_)
        rr = r * self.cam.zoom
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=rr, fill=fill,
                                 outline=outline,
                                 width=max(1, int(round(lw * self.cam.zoom))))

    def arc(self, x, y, r, a0, a1, fill=(0, 0, 0), w=2.0):
        sx, sy = self.cam.pt(x, y)
        rr = r * self.cam.zoom
        self.d.arc([sx - rr, sy - rr, sx + rr, sy + rr], a0, a1, fill=fill,
                   width=max(1, int(round(w * self.cam.zoom))))

    def wtext(self, x, y, s, world_px, fill, anchor="mm", font_name=None):
        """world-space text: scales with the camera like everything else"""
        sx, sy = self.cam.pt(x, y)
        px = max(6, int(world_px * self.cam.zoom))
        fnt = font(font_name or F_UI, px)
        self.d.text((sx, sy), s, font=fnt, fill=fill, anchor=anchor)

    # -- screen-space helpers (typography, UI) ------------------------------
    def text(self, x, y, s, fnt, fill, anchor="mm", alpha=255, outline=None,
             ow=0, spacing=0):
        if alpha < 255:
            fill = tuple(fill) + (int(alpha),) if len(fill) == 3 else fill
        if outline is not None and ow:
            self.d.text((x, y), s, font=fnt, fill=outline, anchor=anchor,
                        stroke_width=int(ow), stroke_fill=outline, spacing=spacing)
        self.d.text((x, y), s, font=fnt, fill=fill, anchor=anchor, spacing=spacing)


def text_w(fnt, s):
    return fnt.getbbox(s)[2]


def wrap(s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(fnt, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------ effects ---
@lru_cache(maxsize=4)
def vignette_mask(strength=0.55, power=2.2):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dx = (xx - W / 2) / (W / 2)
    dy = (yy - H / 2) / (H / 2)
    d = np.sqrt(dx ** 2 + dy ** 2) / math.sqrt(2)
    m = 1.0 - strength * np.clip(d, 0, 1) ** power
    return m[..., None].astype(np.float32)


def fx_rgb_split(arr, px, a=1.0):
    if px <= 0:
        return arr
    p = int(round(px))
    if p < 1:
        return arr
    a = clamp(a)
    r, g, b = arr[..., 0].astype(np.int16), arr[..., 1].astype(np.int16), arr[..., 2].astype(np.int16)
    r2 = np.roll(r, p, axis=1)
    b2 = np.roll(b, -p, axis=1)
    r = (r * (1 - a) + r2 * a)
    b = (b * (1 - a) + b2 * a)
    out = np.stack([r, g, b], axis=-1).clip(0, 255).astype(np.uint8)
    return out


def fx_blocks(arr, count, strength, seed, rng_scale=1.0):
    """displaced horizontal slabs — very cheap, reads as a hard glitch"""
    if count <= 0:
        return arr
    out = arr.copy()
    h, w, _ = arr.shape
    for i in range(int(count)):
        y0 = int(hash01(seed, i, 1) * h)
        hh = int((0.004 + hash01(seed, i, 2) * 0.05) * h * rng_scale) + 2
        off = int((hash01(seed, i, 3) - 0.5) * 2 * strength)
        y1 = min(h, y0 + hh)
        out[y0:y1] = np.roll(arr[y0:y1], off, axis=1)
    return out


@lru_cache(maxsize=2)
def _scanline_cache(freq=3):
    y = np.arange(H)
    return (1.0 - 0.10 * (0.5 + 0.5 * np.cos(y * freq * 2 * math.pi / H)))[:, None, None].astype(np.float32)


def fx_scanlines(arr, amount=1.0):
    m = _scanline_cache()
    m2 = 1.0 - (1.0 - m) * clamp(amount)
    return (arr.astype(np.float32) * m2).clip(0, 255).astype(np.uint8)


def fx_grain(arr, amount=7.0, rng=None):
    if amount <= 0:
        return arr
    rng = rng or np.random.default_rng(0)
    n = rng.normal(0, amount, (H // 2, W // 2, 1)).astype(np.float32)
    n = np.repeat(np.repeat(n, 2, axis=0), 2, axis=1)
    return (arr.astype(np.float32) + n).clip(0, 255).astype(np.uint8)


def fx_vignette(arr, strength=0.55):
    m = vignette_mask(round(strength, 2))
    return (arr.astype(np.float32) * m).clip(0, 255).astype(np.uint8)


def grade(arr, tint=(1.0, 1.0, 1.0), lift=0.0, contrast=1.0):
    a = arr.astype(np.float32)
    a *= np.array(tint, dtype=np.float32)
    a = (a - 128.0) * contrast + 128.0 + lift
    return a.clip(0, 255).astype(np.uint8)


def chroma_sweep(arr, t, amp=0.35, height=0.06, color=(0, 232, 255)):
    """a bright band sliding down the frame (transition energy)"""
    band_y = int(((t * 0.9) % 1.0) * H)
    hh = int(height * H)
    y0, y1 = max(0, band_y - hh // 2), min(H, band_y + hh // 2)
    if y1 <= y0:
        return arr
    out = arr.astype(np.float32)
    grad = np.linspace(0, 1, y1 - y0)[:, None, None]
    grad = np.sin(grad * math.pi) * amp
    out[y0:y1] = out[y0:y1] * (1 - grad) + np.array(color, dtype=np.float32)[None, None, :] * grad
    return out.clip(0, 255).astype(np.uint8)


# --------------------------------------------------------------- compositing ---
def new_canvas(bg=(10, 8, 20)):
    return Image.new("RGB", (SW, SH), bg)


def paste_glow(canvas: Image.Image, glow: Image.Image, strength=1.0):
    """additive composite of a glow layer drawn at canvas resolution"""
    base = np.asarray(canvas, dtype=np.float32)
    g = np.asarray(glow, dtype=np.float32) * strength
    return Image.fromarray(np.clip(base + g, 0, 255).astype(np.uint8), "RGB")


def glow_layer():
    return Image.new("RGB", (SW, SH), (0, 0, 0))


def blur(img: Image.Image, radius: float):
    return img.filter(ImageFilter.GaussianBlur(radius))


def downscale(canvas: Image.Image) -> Image.Image:
    return canvas.resize((W, H), Image.LANCZOS)


# ----------------------------------------------------------------- ffmpeg io ---
def ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


class VideoWriter:
    def __init__(self, path, audio=None, fps=FPS, crf=19, preset="medium", total=None):
        self.path = path
        cmd = [ffmpeg_exe(), "-y", "-hide_banner", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
               "-r", str(fps), "-i", "pipe:0"]
        if audio:
            cmd += ["-i", audio]
        cmd += ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
                "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                "-profile:v", "high", "-level", "4.2",
                "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                "-g", str(fps * 2), "-pix_fmt", "yuv420p"]
        if audio:
            cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
                    "-shortest", "-movflags", "+faststart"]
        cmd += [path]
        self.cmd = cmd
        self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        self.n = 0
        self.total = total

    def write(self, img: Image.Image):
        self.proc.stdin.write(img.tobytes())
        self.n += 1

    def close(self):
        self.proc.stdin.close()
        return self.proc.wait()


def probe(path) -> dict:
    out = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr
    info = {}
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            info["duration"] = int(h) * 3600 + int(m) * 60 + float(s)
        if line.startswith("Stream #"):
            if "Video:" in line:
                info["video"] = line.split("Video:")[1].strip()
            elif "Audio:" in line:
                info["audio"] = line.split("Audio:")[1].strip()
    return info

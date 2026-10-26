"""Glitch, fracture and interference effects (numpy, frame-accurate)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from . import config as C
from . import draw as D

def rgb_split(img, r=(4, 0), b=(-4, 0)):
    """Translate red/blue channels; keeps alpha."""
    arr = np.array(img)
    out = arr.copy()
    h, w = arr.shape[:2]
    def shift(ch, dx, dy):
        src = arr[..., ch]
        canvas = np.zeros_like(src)
        ys0, ys1 = max(0, dy), min(h, h + dy)
        xs0, xs1 = max(0, dx), min(w, w + dx)
        sy0, sy1 = max(0, -dy), min(h, h - dy)
        sx0, sx1 = max(0, -dx), min(w, w - dx)
        if ys1 > ys0 and xs1 > xs0:
            canvas[ys0:ys1, xs0:xs1] = src[sy0:sy1, sx0:sx1]
        return canvas
    out[..., 0] = shift(0, r[0], r[1])
    out[..., 2] = shift(2, b[0], b[1])
    return Image.fromarray(out, "RGBA")

def _rint(rng, lo, hi):
    """Works with both random.Random and numpy.random.Generator."""
    if hasattr(rng, "randint"):
        return rng.randint(lo, hi)
    return int(rng.integers(lo, hi + 1))

def _rfloat(rng, lo, hi):
    if hasattr(rng, "uniform"):
        return rng.uniform(lo, hi)
    return float(rng.uniform(lo, hi))

def slice_tear(img, rng, count=6, max_shift=46, band=(8, 60), tint=None):
    """Horizontal displaced bands — the signature digital tear.

    Pure pixel displacement with a faint 1px chromatic edge, never solid bars.
    """
    arr = np.array(img)
    h, w = arr.shape[:2]
    for _ in range(count):
        bh = _rint(rng, *band)
        y = _rint(rng, 0, max(0, h - bh - 1))
        dx = _rint(rng, -max_shift, max_shift)
        arr[y:y + bh] = np.roll(arr[y:y + bh].copy(), dx, axis=1)
        # thin chromatic seam at the band edge only
        edge = arr[y:y + 2, :, :3].astype(np.int16)
        seam = np.clip(edge + np.array((tint or (90, 30, 70))) * 0.35, 0, 255)
        arr[y:y + 2, :, :3] = seam.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def one_frame_flicker(img, rng, prob=0.5):
    if rng.random() > prob: return img
    arr = np.array(img)
    k = rng.choice([0.82, 1.12, 0.9]) if hasattr(rng, "choice") else \
        __import__("random").choice([0.82, 1.12, 0.9])
    arr[..., :3] = np.clip(arr[..., :3].astype(np.float32) * k, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def scan_artifacts(img, rng, n=3, color=C.CYAN):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for _ in range(n):
        y = _rint(rng, 0, h - 1)
        x0 = _rint(rng, 0, w // 2)
        x1 = w - _rint(rng, 0, w // 4)
        d.rectangle([x0, y, x1, y + _rint(rng, 2, 6)], fill=color + (_rint(rng, 40, 110),))
    return img

# ------------------------------------------------------------- sky fracture
class SkyFracture:
    """Near-vertical digital cracks confined to the sky (never a humanoid shape)."""
    def __init__(self, seed=7):
        rng = random.Random(seed)
        self.trunks = []
        self.fragments = []
        for _ in range(3):
            x = rng.uniform(0.18, 0.82) * C.W
            pts = [(x, rng.uniform(0, 50))]
            for i in range(rng.randint(5, 6)):
                x += rng.uniform(-46, 46)          # mostly vertical zigzag
                pts.append((x, pts[-1][1] + rng.uniform(105, 160)))
            branches = []
            for p in pts[1:-1]:
                if rng.random() < 0.65:
                    bx = p[0] + rng.choice((-1, 1)) * rng.uniform(70, 150)
                    branches.append([p, (bx, p[1] + rng.uniform(26, 70))])
            self.trunks.append((pts, branches))
            # displaced rectangular sky fragments
            for _ in range(2):
                fx = rng.uniform(0.15, 0.85) * C.W
                fy = rng.uniform(80, 700)
                self.fragments.append([fx, fy, fx + rng.uniform(50, 110),
                                       fy + rng.uniform(36, 70)])

    def draw(self, img, grow, offset_px=0, rng=None, y_max=900):
        """grow 0..1; cracks are clipped to the sky region above y_max."""
        d = ImageDraw.Draw(img)
        total = sum(len(p) + len(b) for p, b in self.trunks)
        budget = max(1, grow * total)
        seen = 0
        def clip(p):
            return (p[0], min(p[1], y_max))
        for pts, branches in self.trunks:
            for i in range(1, len(pts)):
                if seen >= budget: break
                if pts[i - 1][1] >= y_max and pts[i][1] >= y_max:
                    seen += 1; continue
                a = clip((pts[i - 1][0] + offset_px, pts[i - 1][1]))
                b = clip((pts[i][0] - offset_px * 0.6, pts[i][1]))
                D.line(d, a, b, (3, 5, 16, 240), width=12)
                D.line(d, a, b, C.CYAN + (225,), width=2)
                seen += 1
            for br in branches:
                if seen >= budget: break
                a, b = br
                if a[1] >= y_max:
                    seen += 1; continue
                D.line(d, clip(a), clip((b[0] + offset_px, b[1])),
                       (4, 6, 18, 190), width=5)
                D.line(d, clip(a), clip((b[0] + offset_px, b[1])),
                       C.MAGENTA + (140,), width=1)
                seen += 1
        # displaced sky fragments (subtle wireframe rectangles)
        if grow > 0.55:
            fa = int(120 * (grow - 0.55) / 0.45)
            for box in self.fragments:
                if box[1] >= y_max: continue
                d.rectangle([int(v) for v in box], outline=(120, 180, 210, min(fa, 130)), width=2)

def wireframe_box(d, box, alpha=110, color=C.CYAN):
    x0, y0, x1, y1 = box
    col = color + (alpha,)
    d.rectangle(box, outline=col, width=2)
    for i in range(1, 4):
        x = x0 + (x1 - x0) * i / 4
        d.line([(x, y0), (x, y1)], fill=color + (alpha // 2,), width=1)
    for i in range(1, 6):
        y = y0 + (y1 - y0) * i / 6
        d.line([(x0, y), (x1, y)], fill=color + (alpha // 2,), width=1)

def double_silhouette(img, pose_layers, split, color=C.CYAN):
    """split 0..1: draw a second offset silhouette briefly (scene 16)."""
    if split <= 0: return img
    arr = np.array(img)
    shift = int(10 * split)
    dup = np.roll(arr, (shift, -shift), axis=(0, 1))
    mask = (dup[..., 3] > 0) & (arr[..., 3] == 0)
    arr[mask] = dup[mask]
    return Image.fromarray(arr, "RGBA")

def letter_gate(img, t_open, color=(5, 7, 16)):
    """Vertical split gate for transitions (unused helper, kept for edits)."""
    d = ImageDraw.Draw(img)
    w = int(C.W * (1 - t_open) / 2)
    d.rectangle([0, 0, w, C.H], fill=color)
    d.rectangle([C.W - w, 0, C.W, C.H], fill=color)
    return img

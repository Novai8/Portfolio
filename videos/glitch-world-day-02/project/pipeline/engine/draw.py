"""Canvas, shape, text and grade helpers (PIL + numpy)."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from . import config as C

_font_cache = {}

def font(kind="sans", size=48, weight="Bold"):
    path = C.PATHS["font_display" if kind == "display" else "font_sans"]
    key = (path, size, weight)
    if key not in _font_cache:
        f = ImageFont.truetype(path, size)
        try:
            names = [n.decode() for n in f.get_variation_names()]
            pick = weight if weight in names else ("Bold" if "Bold" in names else names[len(names) // 2])
            f.set_variation_by_name(pick)
        except Exception:
            pass
        _font_cache[key] = f
    return _font_cache[key]

def layer(size=None):
    return Image.new("RGBA", size or (C.W, C.H), (0, 0, 0, 0))

def vgrad(size, stops):
    """Vertical linear gradient. stops: list of (pos 0..1, rgb)."""
    w, h = size
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    xs = np.linspace(0, 1, h)
    cols = np.array([s[1] for s in stops], dtype=float)
    pos = np.array([s[0] for s in stops])
    for ci in range(3):
        arr[:, :, ci] = np.interp(xs, pos, cols[:, ci])[:, None].astype(np.uint8)
    arr[:, :, 3] = 255
    return Image.fromarray(arr, "RGBA")

def radial(size, center, radius, color, alpha=180, falloff=2.0):
    """Soft radial glow on its own layer. RGB is zeroed wherever alpha is zero."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt((xx - center[0]) ** 2 + (yy - center[1]) ** 2) / radius
    a = (np.clip(1 - d ** falloff, 0, 1) * alpha).astype(np.uint8)
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    mask = a >= 8          # near-transparent pixels stay fully empty (no RGB ghost)
    arr[mask, 0], arr[mask, 1], arr[mask, 2] = color
    arr[..., 3] = np.where(mask, a, 0)
    return Image.fromarray(arr, "RGBA")

def q(p):
    return (int(round(p[0])), int(round(p[1])))

def line(d, p1, p2, fill, width=10, joint="curve"):
    p1, p2 = q(p1), q(p2); width=max(1,int(round(width)))
    d.line([p1, p2], fill=fill, width=width, joint=joint)
    r = width / 2
    d.ellipse([p1[0] - r, p1[1] - r, p1[0] + r, p1[1] + r], fill=fill)
    d.ellipse([p2[0] - r, p2[1] - r, p2[0] + r, p2[1] + r], fill=fill)

def polyline(d, pts, fill, width=10):
    pts = [q(p) for p in pts]
    if len(pts) == 1:
        r = width / 2
        d.ellipse([pts[0][0]-r, pts[0][1]-r, pts[0][0]+r, pts[0][1]+r], fill=fill)
        return
    d.line(pts, fill=fill, width=max(1,int(round(width))), joint="curve")
    r = width / 2
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=fill)

def circle(d, c, r, fill=None, outline=None, width=4):
    c = q(c); r = int(round(r))
    d.ellipse([c[0]-r, c[1]-r, c[0]+r, c[1]+r], fill=fill, outline=outline, width=width)

def rrect(d, box, radius, fill=None, outline=None, width=3):
    box = [int(round(v)) for v in box]
    d.rounded_rectangle(box, radius=int(radius), fill=fill, outline=outline, width=width)

def polygon(d, pts, fill=None, outline=None, width=3):
    pts = [q(p) for p in pts]
    d.polygon(pts, fill=fill)
    if outline:
        d.line(pts + [pts[0]], fill=outline, width=max(1,int(round(width))), joint="curve")

def text_size(s, f, spacing=4):
    box = f.getbbox(s)
    # multiline measurement
    tmp = Image.new("RGB", (10, 10))
    td = ImageDraw.Draw(tmp)
    b = td.multiline_textbbox((0, 0), s, font=f, spacing=spacing)
    return b[2] - b[0], b[3] - b[1]

def wrap_text(s, f, max_w):
    words = s.split()
    lines, cur = [], ""
    d = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def draw_text(img, xy, s, size=46, kind="sans", weight="SemiBold", fill=C.WHITE,
              anchor="mm", outline=(6, 8, 16), outline_w=4, shadow=True,
              max_width=None, line_spacing=1.18, align="center"):
    f = font(kind, size, weight)
    lines = wrap_text(s, f, max_width) if max_width else s.split("\n")
    s2 = "\n".join(lines)
    d = ImageDraw.Draw(img)
    lh = int(size * line_spacing)
    tmp = d.multiline_textbbox((0, 0), s2, font=f, spacing=lh - size, align=align)
    tw, th = tmp[2] - tmp[0], tmp[3] - tmp[1]
    x, y = xy
    if anchor == "mm":
        pos = (x - tw / 2 - tmp[0], y - th / 2 - tmp[1])
    elif anchor == "lm":
        pos = (x, y - th / 2 - tmp[1])
    elif anchor == "rm":
        pos = (x - tw - tmp[0], y - th / 2 - tmp[1])
    else:
        pos = (x, y)
    if shadow:
        d.multiline_text((pos[0] + 3, pos[1] + 4), s2, font=f, fill=(0, 0, 0, 170),
                         spacing=lh - size, align=align)
    if outline_w:
        d.multiline_text(pos, s2, font=f, fill=fill, stroke_width=outline_w,
                         stroke_fill=outline, spacing=lh - size, align=align)
    else:
        d.multiline_text(pos, s2, font=f, fill=fill, spacing=lh - size, align=align)
    return (pos[0], pos[1], pos[0] + tw, pos[1] + th)

def grain(arr, amount=7, seed=0):
    rng = np.random.default_rng(seed)
    n = rng.integers(-amount, amount + 1, arr.shape[:2], dtype=np.int16)
    a = arr.astype(np.int16)
    a[..., :3] = np.clip(a[..., :3] + n[..., None], 0, 255)
    return a.astype(np.uint8)

def vignette(img, strength=150, inner=0.45):
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = np.clip((d - inner) / (1.05 - inner), 0, 1) ** 1.6 * strength
    arr = np.array(img).astype(np.int16)
    arr[..., :3] = np.clip(arr[..., :3] - a[..., None].astype(np.int16), 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

def bloom_layer(img, radius=14, threshold=170):
    arr = np.array(img.convert("RGB"))
    m = arr.max(axis=2) > threshold
    glow = np.zeros_like(arr)
    glow[m] = arr[m]
    return Image.fromarray(glow).filter(ImageFilter.GaussianBlur(radius))

def comp(base, over, pos=(0, 0)):
    if over.mode != "RGBA": over = over.convert("RGBA")
    base.alpha_composite(over, pos)
    return base

def camera_apply(base, world, scale=1.0, dx=0.0, dy=0.0):
    """Composite world layer onto base with virtual camera zoom/pan (scale about center)."""
    if scale != 1.0:
        nw, nh = int(world.width * scale), int(world.height * scale)
        world = world.resize((nw, nh), Image.BILINEAR)
    base.alpha_composite(world, (int(dx), int(dy)))
    return base

def jitter_points(pts, amp, rng):
    return [(x + rng.uniform(-amp, amp), y + rng.uniform(-amp, amp)) for x, y in pts]

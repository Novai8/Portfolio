"""UI drawing toolkit: cached text sprites, soft shadows, cards, chips,
checkmarks, cursors, ripples, counters. Every text draw is measured; any
potential overflow is logged to OVERFLOWS (QA asserts it stays empty)."""
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, math
from style import F, clamp01, lerp

OVERFLOWS = []
DRAWN = set()   # every on-screen string, for the spellcheck QA pass

# ---------------- sprite helpers ----------------
_text_cache = {}

def text_sprite(text, font, fill, stroke=0, stroke_fill=None):
    key = (text, font.path, font.size, fill, stroke, stroke_fill)
    sp = _text_cache.get(key)
    if sp is None:
        d = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
        bb = d.textbbox((0, 0), text, font=font, stroke_width=stroke)
        asc, desc = font.getmetrics()
        # horizontal: tight; vertical: full ascent..descent box so words share a baseline
        top = -stroke; bottom = asc + desc + stroke
        w = max(1, bb[2] - bb[0] + 4); h = max(1, bottom - top + 4)
        sp = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sp).text((2 - bb[0], 2 - top), text, font=font, fill=fill,
                                stroke_width=stroke, stroke_fill=stroke_fill)
        _text_cache[key] = sp
    return sp

def text_size(text, font):
    sp = text_sprite(text, font, (0, 0, 0, 255))
    return sp.size[0] - 4, sp.size[1] - 4

_ANCHORS = {  # (dx_frac, dy_frac) applied to sprite size
    "lt": (0.0, 0.0), "mt": (0.5, 0.0), "rt": (1.0, 0.0),
    "lm": (0.0, 0.5), "mm": (0.5, 0.5), "rm": (1.0, 0.5),
    "lb": (0.0, 1.0), "mb": (0.5, 1.0), "rb": (1.0, 1.0),
}

def put_sprite(img, sp, xy, alpha=1.0, anchor="lt", scale=1.0):
    if alpha <= 0.003: return
    if scale != 1.0:
        nw, nh = max(1, int(sp.size[0] * scale)), max(1, int(sp.size[1] * scale))
        sp = sp.resize((nw, nh), Image.LANCZOS)
    if alpha < 0.999:
        a = np.array(sp)
        a[:, :, 3] = (a[:, :, 3].astype(np.float32) * alpha).astype(np.uint8)
        sp = Image.fromarray(a)
    dx, dy = _ANCHORS[anchor]
    px = int(round(xy[0] - dx * sp.size[0])); py = int(round(xy[1] - dy * sp.size[1]))
    img.alpha_composite(sp, (px, py))

def text(img, xy, s, font, fill, alpha=1.0, anchor="lt", scale=1.0, maxw=None, tag=""):
    """Draw text; if maxw given, shrink font until it fits (never overflow)."""
    if alpha > 0.02:
        DRAWN.add(s)
    if maxw is not None:
        w, _ = text_size(s, font)
        if w > maxw:
            size = font.size
            while w > maxw and size > 10:
                size -= 1
                font = F(font.path.split("Inter-")[1][:-4], size)
                w, _ = text_size(s, font)
            if w > maxw:
                OVERFLOWS.append((tag or s, maxw, w))
    sp = text_sprite(s, font, fill)
    put_sprite(img, sp, xy, alpha=alpha, anchor=anchor, scale=scale)
    return font

def wrap_lines(s, font, maxw):
    words = s.split(" "); lines = []; cur = ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if text_size(t, font)[0] <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

# ---------------- shadows & cards ----------------
_shadow_cache = {}

def _shadow_sprite(w, h, r, blur=16, alpha=60, dy=10):
    key = (w // 4 * 4, h // 4 * 4, r, blur, alpha, dy)
    sp = _shadow_cache.get(key)
    m = blur * 3
    if sp is None:
        w, h = key[0], key[1]
        sp = Image.new("RGBA", (w + 2 * m, h + 2 * m), (0, 0, 0, 0))
        d = ImageDraw.Draw(sp)
        d.rounded_rectangle([m, m + dy, m + w, m + h + dy], radius=r, fill=(15, 23, 42, alpha))
        sp = sp.filter(ImageFilter.GaussianBlur(blur))
        _shadow_cache[key] = sp
    return sp, key[0], key[1], m

def card(img, x, y, w, h, r=20, fill=(255, 255, 255, 255), alpha=1.0,
         shadow=True, shadow_alpha=60, border=None, border_w=2, scale=1.0,
         dark_shadow=False):
    """Rounded card with cached soft shadow. x,y = top-left (pre-scale)."""
    if alpha <= 0.003: return
    w, h = int(w), int(h)
    if scale != 1.0:
        cx, cy = x + w / 2, y + h / 2
        w, h = max(2, int(w * scale)), max(2, int(h * scale))
        x, y = int(cx - w / 2), int(cy - h / 2)
    if shadow and alpha > 0.05:
        sp, sw, sh, m = _shadow_sprite(w, h, min(r, min(w, h) // 2), 16,
                                       int(shadow_alpha * min(1, alpha)), 10)
        put_sprite(img, sp, (x - m, y - m), alpha=1.0)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = tuple(fill[:3]) + (int(255 * clamp01(alpha)),)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=min(r, min(w, h) // 2), fill=f)
    if border:
        b = tuple(border[:3]) + (int(255 * clamp01(alpha)),)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=min(r, min(w, h) // 2),
                            outline=b, width=border_w)
    img.alpha_composite(layer, (x, y))

def rrect_layer(img, x, y, w, h, r, fill=None, outline=None, width=2, alpha=1.0):
    if alpha <= 0.003: return
    layer = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = tuple(fill[:3]) + (int(255 * alpha),) if fill else None
    o = tuple(outline[:3]) + (int(255 * alpha),) if outline else None
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=min(r, min(w, h) // 2), fill=f, outline=o, width=width)
    img.alpha_composite(layer, (int(x), int(y)))

# ---------------- chips ----------------
def chip(img, cx, cy, s, font, fg, bg, pad_x=22, pad_h=None, alpha=1.0, scale=1.0,
         border=None, anchor="mm", maxw=None):
    """Pill chip centered at (cx,cy) by default. Returns (w,h)."""
    if alpha <= 0.003: return (0, 0)
    DRAWN.add(s)
    tw, th = text_size(s, font)
    if maxw is not None and tw > maxw:
        OVERFLOWS.append((s, maxw, tw))
    px = pad_x; hgt = pad_h or (th + 26)
    w = tw + 2 * px
    sp = text_sprite(s, font, fg)
    layer = Image.new("RGBA", (int(w), int(hgt)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    f = tuple(bg[:3]) + (255,)
    d.rounded_rectangle([0, 0, w - 1, hgt - 1], radius=hgt // 2, fill=f,
                        outline=(tuple(border[:3]) + (255,)) if border else None, width=2)
    layer.alpha_composite(sp, (int(px) + 2 - (sp.size[0] - tw) // 2,
                               int((hgt - (sp.size[1] - 2)) // 2)))
    put_sprite(img, layer, (cx, cy), alpha=alpha, anchor=anchor, scale=scale)
    return w, hgt

# ---------------- icons ----------------
def checkmark(img, cx, cy, r, color, p, width=6, bg=None, alpha=1.0):
    """Circle-draw + check stroke animation, p in 0..1.5 (>1 draws check)."""
    if alpha <= 0.003 or p <= 0: return
    layer = Image.new("RGBA", (int(4 * r), int(4 * r)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = (2 * r, 2 * r); col = tuple(color[:3]) + (int(255 * alpha),)
    if bg:
        bcol = tuple(bg[:3]) + (int(255 * alpha),)
        d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=bcol)
    circ_p = clamp01(p / 0.6)
    if circ_p > 0:
        d.arc([c[0] - r, c[1] - r, c[0] + r, c[1] + r], start=-90,
              end=-90 + 360 * circ_p, fill=col, width=width)
    if p > 0.6:
        cp = clamp01((p - 0.6) / 0.4)
        x1, y1 = c[0] - r * 0.45, c[1] + r * 0.02
        x2, y2 = c[0] - r * 0.08, c[1] + r * 0.40
        x3, y3 = c[0] + r * 0.50, c[1] - r * 0.38
        pts = [(x1, y1), (x2, y2), (x3, y3)]
        # partial polyline
        if cp <= 0.45:
            q = cp / 0.45
            pts = [(x1, y1), (lerp(x1, x2, q), lerp(y1, y2, q))]
        else:
            q = (cp - 0.45) / 0.55
            pts = [(x1, y1), (x2, y2), (lerp(x2, x3, q), lerp(y2, y3, q))]
        d.line(pts, fill=col, width=width, joint="curve")
    img.alpha_composite(layer, (int(cx - 2 * r), int(cy - 2 * r)))

def arrow_icon(img, x, y, s, color, alpha=1.0, rot=0):
    if alpha <= 0.003: return
    layer = Image.new("RGBA", (int(s * 2), int(s * 2)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    col = tuple(color[:3]) + (int(255 * alpha),)
    # simple right arrow
    d.line([(s * 0.3, s), (s * 1.6, s)], fill=col, width=max(2, int(s * 0.14)))
    d.polygon([(s * 1.35, s * 0.6), (s * 1.85, s), (s * 1.35, s * 1.4)], fill=col)
    if rot:
        layer = layer.rotate(rot, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(layer, (int(x - layer.size[0] / 2), int(y - layer.size[1] / 2)))

# ---------------- cursor ----------------
_cursor_cache = {}

def cursor_sprite(size=34, color=(17, 24, 39)):
    key = (size, color)
    sp = _cursor_cache.get(key)
    if sp is None:
        m = 8
        sp = Image.new("RGBA", (size + 2 * m, size + 2 * m), (0, 0, 0, 0))
        d = ImageDraw.Draw(sp)
        s = size
        pts = [(m, m), (m, m + s * 0.92), (m + s * 0.22, m + s * 0.70),
               (m + s * 0.36, m + s * 1.02), (m + s * 0.50, m + s * 0.96),
               (m + s * 0.36, m + s * 0.64), (m + s * 0.66, m + s * 0.62)]
        d.polygon(pts, fill=color + (255,), outline=(255, 255, 255, 255))
        d.line(pts + [pts[0]], fill=(255, 255, 255, 255), width=2)
        _cursor_cache[key] = sp
    return sp

def cursor(img, x, y, alpha=1.0, press=0.0, size=34, color=(17, 24, 39)):
    sp = cursor_sprite(size, color)
    sc = 1.0 - 0.03 * press if press else 1.0
    put_sprite(img, sp, (x - 8, y - 8), alpha=alpha, anchor="lt", scale=sc)

def ripple(img, x, y, p, color, r_max=70, alpha=1.0):
    if p <= 0 or p >= 1 or alpha <= 0.01: return
    r = r_max * p
    a = alpha * (1 - p)
    layer = Image.new("RGBA", (int(2 * r_max + 4),) * 2, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([r_max + 2 - r, r_max + 2 - r, r_max + 2 + r, r_max + 2 + r],
              outline=tuple(color[:3]) + (int(160 * a),), width=3)
    img.alpha_composite(layer, (int(x - r_max - 2), int(y - r_max - 2)))

# ---------------- misc ----------------
def hline(img, x0, x1, y, color, width=2, alpha=1.0):
    if alpha <= 0.003: return
    d = ImageDraw.Draw(img)
    d.line([(x0, y), (x1, y)], fill=tuple(color[:3]) + (int(255 * alpha),), width=width)

_dots_cache = {}
def dots_pattern(img, x0, y0, x1, y1, step=48, color=(0, 0, 0), alpha=18, r=2):
    key = (int(x1 - x0), int(y1 - y0), step, tuple(color[:3]), alpha, r)
    layer = _dots_cache.get(key)
    if layer is None:
        layer = Image.new("RGBA", (key[0], key[1]), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        c = tuple(color[:3]) + (alpha,)
        for yy in range(step // 2, key[1], step):
            for xx in range(step // 2, key[0], step):
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=c)
        _dots_cache[key] = layer
    img.alpha_composite(layer, (int(x0), int(y0)))

def strike(img, x0, x1, y, color, p, width=4):
    if p <= 0: return
    d = ImageDraw.Draw(img)
    d.line([(x0, y), (lerp(x0, x1, clamp01(p)), y)], fill=color + (255,), width=width)

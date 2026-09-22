"""Frame compositor: scene switching, transitions, camera push, subtitles."""
import sys, os, json, math
from PIL import Image, ImageDraw, ImageFilter
from style import *
from ui import text, text_size, OVERFLOWS, DRAWN, rrect_layer
import beats as B
import scenes as S

SCENE_LIST = B.SCENES
XF = 0.40   # generic cross-dissolve length

def scene_frame(name, t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    S.SCENE_FN[name](img, t)
    if name in S.PUSH:
        t0, t1, amt = S.PUSH[name]
        img = S.push_in(img, t, t0, t1, amt)
    return img

def scene_index(t):
    for i, (n, a, b) in enumerate(SCENE_LIST):
        if a <= t < b: return i
    return len(SCENE_LIST) - 1

def zoom_blur(img, p, zmax=1.12, bmax=10):
    """Zoom-through + blur ramp. p 0..1 intensity."""
    if p <= 0.001: return img
    z = 1 + (zmax - 1) * p
    cw, ch = int(W / z), int(H / z)
    x0, y0 = (W - cw) // 2, (H - ch) // 2
    out = img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR)
    if bmax * p > 0.5:
        out = out.filter(ImageFilter.GaussianBlur(bmax * p))
    return out

def compose(t):
    i = scene_index(t)
    name, a, b = SCENE_LIST[i]
    # --- pivot title card (53.18 - 54.6) sits between S4b and S6
    if 53.18 <= t < 54.6:
        img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        S.title_card(img, t)
        # blur-in from S4b during first 0.3s
        if t < 53.5:
            p = 1 - (t - 53.18) / 0.32
            prev = scene_frame("S4b_wall", t).filter(ImageFilter.GaussianBlur(8 * (1 - p) + 0.01))
            img = Image.blend(img, prev, clamp01(p))
        if t >= 54.3:
            p = (t - 54.3) / 0.3
            nxt = scene_frame("S6_conv", t)
            img = Image.blend(img, nxt, ease_in_out_cubic(p))
        return img
    img = scene_frame(name, t)
    # --- section transitions
    for tt, kind in B.TRANSITIONS:
        if kind == "zoomblur" and tt - 0.35 <= t < tt + 0.35:
            # outgoing zoom+blur, incoming settle
            if t < tt:
                p = (t - (tt - 0.35)) / 0.35
                img = zoom_blur(img, ease_in_cubic(p))
            else:
                p = 1 - (t - tt) / 0.35
                img = zoom_blur(img, ease_out_cubic(p) , zmax=0.94 + 0.06, bmax=8)
                # incoming from slightly zoomed-out: handled by darkening fade
                dark = Image.new("RGBA", (W, H), (11, 18, 32, int(255 * ease_out_cubic(p) * 0.6)))
                img.alpha_composite(dark)
            return img
        if kind == "slide" and tt - 0.25 <= t < tt + 0.35:
            # parallax slide: outgoing left (bg slower), incoming from right
            p = ease_in_out_cubic((t - (tt - 0.25)) / 0.6)
            prev_name = SCENE_LIST[scene_index(tt - 0.01)][0]
            next_name = SCENE_LIST[scene_index(tt + 0.01)][0]
            prev = scene_frame(prev_name, min(t, tt - 0.01))
            nxt = scene_frame(next_name, max(t, tt + 0.01))
            canvas = Image.new("RGBA", (W, H), tuple(PAL["C"]["bg"]) + (255,))
            canvas.alpha_composite(prev, (int(-W * p * 0.55), 0))
            canvas.alpha_composite(nxt, (int(W * (1 - p)), 0))
            if 0.15 < p < 0.85:
                canvas = canvas.filter(ImageFilter.GaussianBlur(2.5 * math.sin((p - 0.15) / 0.7 * math.pi)))
            return canvas
    # --- generic cross-dissolve at intra-section scene changes
    if t - a < XF and i > 0 and not any(abs(a - tt) < 0.01 for tt, _ in B.TRANSITIONS) and a != 54.6:
        p = ease_in_out_cubic((t - a) / XF)
        prev_name = SCENE_LIST[i - 1][0]
        prev = scene_frame(prev_name, a - 0.001)
        # match-cut style: previous drifts up 2%, new settles from 1.5% down
        prev = prev.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, 22 * p), Image.BILINEAR)
        img2 = img.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -16 * (1 - p)), Image.BILINEAR)
        img = Image.blend(prev, img2, p)
    return img

# ---------------- subtitles ----------------
_subs = None
def load_subs():
    global _subs
    if _subs is None:
        p = os.path.join(os.path.dirname(__file__), "..", "subs.json")
        _subs = json.load(open(p)) if os.path.exists(p) else []
    return _subs

def draw_subs(img, t):
    for s in load_subs():
        if s["start"] <= t < s["end"]:
            a = min(anim(t, s["start"], 0.2, ease_out_cubic), 1 - anim(t, s["end"] - 0.15, 0.15, ease_in_cubic))
            lines = s["lines"]
            f = F("SemiBold", 30)
            y = SAFE_Y1 - 12 - 44 * len(lines)
            for ln in lines:
                w, h = text_size(ln, f)
                rrect_layer(img, W // 2 - w // 2 - 18, y - 6, w + 36, 46, 12, fill=(0, 0, 0), alpha=0.62 * a)
                text(img, (W // 2, y + 17), ln, f, (255, 255, 255), alpha=a, anchor="mm", maxw=1500, tag="sub")
                y += 44
            break
    return img

def frame(t, subs=False):
    img = compose(t)
    if subs: draw_subs(img, t)
    return img.convert("RGB")

if __name__ == "__main__":
    # usage: render.py start_frame end_frame outdir [subs]
    sf, ef, outdir = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    subs = len(sys.argv) > 4 and sys.argv[4] == "subs"
    os.makedirs(outdir, exist_ok=True)
    for fi in range(sf, ef):
        t = fi / FPS
        frame(t, subs).save(os.path.join(outdir, f"f{fi:06d}.jpg"), quality=93, subsampling=0)
    if OVERFLOWS:
        with open(os.path.join(outdir, f"overflow_{sf}.txt"), "w") as fh:
            for o in OVERFLOWS: fh.write(repr(o) + "\n")
    with open(os.path.join(outdir, f"drawn_{sf}.txt"), "w") as fh:
        for s in sorted(DRAWN): fh.write(s + "\n")

"""Procedural stickman rig with interpolatable numeric poses.

Anchor convention: pose['x'], pose['y'] is the pelvis centre in screen pixels.
All limb angles in degrees, 0 = pointing straight down, + = counter-clockwise
(screen space, y grows downward, so +angle swings to the screen-left).
"""
import math, random
from PIL import Image, ImageDraw
from . import draw as D
from . import config as C

def v(angle_deg, length):
    a = math.radians(angle_deg)
    # screen space: down is +y
    return (-math.sin(a) * length, math.cos(a) * length)

def add(p, vec): return (p[0] + vec[0], p[1] + vec[1])

# pose parameter defaults
DEFAULTS = dict(
    x=540, y=1100, h=420, lean=0, head_tilt=0, head_dx=0,
    arm_l=14, arm_r=-14, elbow_l=8, elbow_r=8,
    leg_l=-10, leg_r=10, knee_l=6, knee_r=6,
    eye="normal", mouth=None, body_swing=0,
)

def _geom(p):
    h = p["h"]
    pelvis = (p["x"], p["y"])
    torso = h * 0.34
    lean = math.radians(p["lean"])
    neck = add(pelvis, (-math.sin(lean) * torso, -math.cos(lean) * torso))
    head_r = h * 0.105
    head_c = add(neck, (p.get("head_dx", 0), -head_r * 0.55))
    head_c = (head_c[0], head_c[1])
    head_c = (head_c[0] + math.sin(math.radians(p["head_tilt"])) * head_r * 0.4,
              head_c[1])
    uarm, farm = h * 0.205, h * 0.175
    uleg, lleg = h * 0.235, h * 0.235
    sw = p.get("body_swing", 0)
    # shoulders share neck point
    sl = sr = neck
    # arms
    def arm(ang, bend, side):
        e = add(sr, v(ang + sw * side, uarm))
        hand = add(e, v(ang + bend + sw * side, farm))
        return e, hand
    el, hand_l = arm(p["arm_l"], p["elbow_l"], 1)
    er, hand_r = arm(p["arm_r"], p["elbow_r"], -1)
    # legs
    def leg(ang, bend, side):
        k = add(pelvis, v(ang - sw * side, uleg))
        foot = add(k, v(ang + bend - sw * side, lleg))
        return k, foot
    kl, foot_l = leg(p["leg_l"], p["knee_l"], 1)
    kr, foot_r = leg(p["leg_r"], p["knee_r"], -1)
    return dict(pelvis=pelvis, neck=neck, head_c=head_c, head_r=head_r,
                elbow_l=el, hand_l=hand_l, elbow_r=er, hand_r=hand_r,
                knee_l=kl, foot_l=foot_l, knee_r=kr, foot_r=foot_r,
                width=max(7, h * 0.026))

def _eyes(d, head_c, r, kind, tilt=0):
    cx, cy = head_c
    dx = r * 0.36; ey = -r * 0.12
    w = r * 0.30; hh = r * 0.13
    if kind == "wide":
        w, hh = r * 0.34, r * 0.26
    if kind == "shut":
        for s in (-1, 1):
            D.line(d, (cx + s * dx - w, cy + ey), (cx + s * dx + w, cy + ey),
                   (235, 240, 248, 255), width=max(3, r * 0.07))
        return
    if kind == "squint":
        hh = r * 0.08
    for s in (-1, 1):
        d.rounded_rectangle([cx + s * dx - w, cy + ey - hh, cx + s * dx + w, cy + ey + hh],
                            radius=hh, fill=(235, 240, 248, 255))

def _mouth(d, head_c, r, kind):
    if not kind: return
    cx, cy = head_c
    if kind == "o":
        d.ellipse([cx - r * 0.16, cy + r * 0.34, cx + r * 0.16, cy + r * 0.62],
                  fill=(235, 240, 248, 230))
    elif kind == "flat":
        D.line(d, (cx - r * 0.26, cy + r * 0.48), (cx + r * 0.26, cy + r * 0.48),
               (235, 240, 248, 255), width=max(3, r * 0.06))
    elif kind == "frown":
        d.arc([cx - r * 0.28, cy + r * 0.42, cx + r * 0.28, cy + r * 0.8],
              200, 340, fill=(235, 240, 248, 255), width=max(3, r * 0.06))

def draw_stickman(img, pose, style="hero", t=0.0, rng=None, alpha=255, rim_strength=0.0):
    p = dict(DEFAULTS); p.update(pose)
    g = _geom(p)
    w = g["width"]
    ink = C.INK + (alpha,)
    d = ImageDraw.Draw(img)
    rim = style == "mystery"
    if rim:
        rim_strength = max(rim_strength, 1.0)
    if rim_strength > 0:
        # rim layer: mystery = electric cyan, hero = dim pale cool edge
        rim_rgb = C.RIM_CYAN if rim else (130, 160, 196)
        rim_col = rim_rgb + (int(150 * min(1.0, rim_strength)),)
        rw = w + 5
        off = 3
        def rline(a, b): D.line(d, (a[0] + off, a[1] - off), (b[0] + off, b[1] - off), rim_col, rw)
        rline(g["pelvis"], g["neck"])
        rline(g["neck"], g["elbow_l"]); rline(g["elbow_l"], g["hand_l"])
        rline(g["neck"], g["elbow_r"]); rline(g["elbow_r"], g["hand_r"])
        rline(g["pelvis"], g["knee_l"]); rline(g["knee_l"], g["foot_l"])
        rline(g["pelvis"], g["knee_r"]); rline(g["knee_r"], g["foot_r"])
        d.ellipse([g["head_c"][0] - g["head_r"] + off, g["head_c"][1] - g["head_r"] - off,
                   g["head_c"][0] + g["head_r"] + off, g["head_c"][1] + g["head_r"] - off],
                  outline=rim_col, width=5)
    # subtle outline distortion for the mystery figure
    def jpt(pt):
        if rim and rng is not None:
            return (pt[0] + rng.uniform(-1.6, 1.6), pt[1] + rng.uniform(-1.6, 1.6))
        return pt
    # far limbs first (right arm / left leg behind torso by draw order)
    D.polyline(d, [jpt(g["neck"]), jpt(g["elbow_r"]), jpt(g["hand_r"])], ink, w)
    D.polyline(d, [jpt(g["pelvis"]), jpt(g["knee_l"]), jpt(g["foot_l"])], ink, w)
    D.line(d, jpt(g["pelvis"]), jpt(g["neck"]), ink, int(w * 1.15))
    D.polyline(d, [jpt(g["neck"]), jpt(g["elbow_l"]), jpt(g["hand_l"])], ink, w)
    D.polyline(d, [jpt(g["pelvis"]), jpt(g["knee_r"]), jpt(g["foot_r"])], ink, w)
    d.ellipse([g["head_c"][0] - g["head_r"], g["head_c"][1] - g["head_r"],
               g["head_c"][0] + g["head_r"], g["head_c"][1] + g["head_r"]], fill=ink)
    if p.get("face") != "back":
        _eyes(d, g["head_c"], g["head_r"], p["eye"], p["head_tilt"])
        _mouth(d, g["head_c"], g["head_r"], p.get("mouth"))
    return g

# ----------------------------------------------------------------- presets
def standing(**kw):
    p = dict(DEFAULTS); p.update(kw); return p

def walk_pose(phase, speed=1.0, **kw):
    s = math.sin(phase * speed)
    p = dict(DEFAULTS)
    p.update(dict(
        arm_l=14 - 26 * s, arm_r=-14 + 26 * s,
        elbow_l=18, elbow_r=18,
        leg_l=-22 * s, leg_r=22 * s,
        knee_l=10 + max(0, s) * 26, knee_r=10 + max(0, -s) * 26,
        lean=6, body_swing=3 * s,
    ))
    p.update(kw); return p

def run_pose(phase, **kw):
    s = math.sin(phase)
    p = dict(DEFAULTS)
    p.update(dict(
        arm_l=40 - 55 * s, arm_r=-40 + 55 * s,
        elbow_l=55, elbow_r=55,
        leg_l=-42 * s, leg_r=42 * s,
        knee_l=18 + max(0, s) * 48, knee_r=18 + max(0, -s) * 48,
        lean=16, body_swing=6 * s, eye="normal",
    ))
    p.update(kw); return p

def citizen(kind, turn=0.0, **kw):
    """Frozen citizens; turn 0..1 rotates only the head toward rooftop."""
    p = dict(DEFAULTS)
    presets = dict(
        step=dict(leg_l=-26, leg_r=30, knee_r=24, arm_l=20, arm_r=-18, lean=8),
        cup=dict(arm_l=118, elbow_l=70, arm_r=-10, leg_l=-8, leg_r=8),
        cyclist=dict(lean=34, leg_l=-40, knee_l=50, leg_r=44, knee_r=52,
                     arm_l=62, arm_r=-62, elbow_l=30, elbow_r=30),
        reach=dict(arm_l=78, arm_r=70, elbow_l=24, elbow_r=20, leg_l=-12, leg_r=14),
        phone=dict(arm_l=104, elbow_l=46, head_tilt=12, leg_l=-7, leg_r=7),
    )
    p.update(presets.get(kind, {}))
    p["head_tilt"] = p.get("head_tilt", 0) + turn * 38
    p.update(kw)
    return p

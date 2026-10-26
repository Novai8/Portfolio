"""
rig.py — the protagonist rig ("NIX", series character) and reusable figures.

The character is a black stick figure: round head, clean silhouette, five
segments per limb pair, and a face made of a handful of expressive strokes.
Poses are plain dicts of joint angles, so any two poses can be blended to make
an unlimited number of inbetween frames. This is the piece that gets reused in
every episode.
"""
from __future__ import annotations

import math

from engine import C, clamp, ease, lerp

# --------------------------------------------------------------- proportions ---
P = dict(
    head_r=15.5,
    neck=5.0,
    torso=50.0,
    upper_arm=26.0,
    fore_arm=24.0,
    thigh=34.0,
    shin=32.0,
    foot=9.0,
    shoulder=9.5,
    hip=6.0,
)

DEFAULT = dict(
    torso=0.0, head=0.0,
    la_u=20.0, la_f=26.0, ra_u=-20.0, ra_f=-26.0,
    ll_u=5.0, ll_f=-3.0, rl_u=-5.0, rl_f=3.0,
    bob=0.0, squash=1.0, face="neutral", look=0.0, flip=1,
)


def pose(**kw):
    p = dict(DEFAULT)
    p.update(kw)
    return p


def blend(a, b, t):
    e = ease(clamp(t), "inout")
    out = {}
    for k, v in a.items():
        bv = b.get(k, v)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[k] = lerp(float(v), float(bv), e)
        else:
            out[k] = bv if t >= 0.5 else v
    return out


def seq(t, keys, kind="inout"):
    """keys = [(time, pose), ...] -> blended pose"""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, p0), (t1, p1) in zip(keys, keys[1:]):
        if t <= t1:
            if kind == "cut":
                return p1 if t >= (t0 + t1) / 2 else p0
            return blend(p0, p1, (t - t0) / max(1e-6, t1 - t0))
    return keys[-1][1]


# ------------------------------------------------------------------- poses ---
POSES = {
    "idle":      pose(),
    "idle2":     pose(la_u=23, la_f=30, ra_u=-23, ra_f=-29, bob=1.2, head=-1),
    "walk_a":    pose(ll_u=26, ll_f=-14, rl_u=-24, rl_f=16, la_u=-26, la_f=6, ra_u=34, ra_f=-34, bob=-1.5),
    "walk_b":    pose(ll_u=-24, ll_f=16, rl_u=26, rl_f=-14, la_u=34, la_f=-34, ra_u=-26, ra_f=6, bob=1.5),
    "run_a":     pose(torso=12, ll_u=42, ll_f=-40, rl_u=-38, rl_f=34, la_u=-52, la_f=-30, ra_u=48, ra_f=36, bob=-2),
    "run_b":     pose(torso=12, ll_u=-38, ll_f=34, rl_u=42, rl_f=-40, la_u=48, la_f=36, ra_u=-52, ra_f=-30, bob=2),
    "shock":     pose(la_u=138, la_f=156, ra_u=-138, ra_f=-156, ll_u=12, rl_u=-12, torso=-6, head=2, face="shock", bob=-6),
    "startle":   pose(la_u=120, la_f=95, ra_u=-124, ra_f=-100, ll_u=8, rl_u=-10, torso=-4, face="wide", bob=-4),
    "confused":  pose(la_u=22, la_f=30, ra_u=-142, ra_f=-158, torso=4, head=-10, face="confused"),
    "deadpan":   pose(la_u=21, la_f=27, ra_u=-21, ra_f=-27, face="deadpan", head=3),
    "point":     pose(ra_u=-88, ra_f=-92, la_u=22, la_f=30, torso=-3, face="neutral", flip=1),
    "point_up":  pose(ra_u=-158, ra_f=-172, la_u=24, la_f=32, torso=-6, head=-8, face="wide", look=1),
    "shrug":     pose(la_u=38, la_f=118, ra_u=-38, ra_f=-118, face="shrug", head=-2),
    "wave":      pose(ra_u=-152, ra_f=-138, la_u=23, la_f=30, face="neutral"),
    "wave2":     pose(ra_u=-166, ra_f=-112, la_u=23, la_f=30, face="neutral"),
    "throw_back":pose(torso=-10, ra_u=-52, ra_f=-44, la_u=34, la_f=44, face="deadpan", ll_u=-14, rl_u=10),
    "throw":     pose(torso=16, ra_u=-120, ra_f=-70, la_u=-60, la_f=-30, face="deadpan", ll_u=20, rl_u=-16),
    "reach":     pose(ra_u=-86, ra_f=-90, la_u=22, la_f=28, torso=6, face="wide"),
    "facepalm":  pose(ra_u=-146, ra_f=-184, torso=3, head=6, face="deadpan", la_u=20, la_f=26),
    "crouch":    pose(torso=18, ll_u=44, ll_f=-64, rl_u=-30, rl_f=52, la_u=20, la_f=30, ra_u=-30, ra_f=-20, bob=8, face="wide"),
    "sit":       pose(torso=8, ll_u=88, ll_f=-6, rl_u=84, rl_f=-8, la_u=-30, la_f=-20, ra_u=26, ra_f=18, bob=12),
    "frozen":    pose(torso=0, la_u=4, la_f=2, ra_u=-4, ra_f=-2, ll_u=0, ll_f=0, rl_u=0, rl_f=0, face="blank"),
    "scared":    pose(la_u=52, la_f=70, ra_u=-56, ra_f=-74, ll_u=10, rl_u=-8, torso=-3, face="scared", bob=-2),
    "look_up":   pose(torso=-3, head=-16, look=2, face="wide"),
    "slump":     pose(torso=16, head=20, la_u=16, la_f=14, ra_u=-16, ra_f=-14, ll_u=6, rl_u=-6, bob=4, face="deadpan"),
}


def skeleton(p):
    """forward kinematics -> named points in local space (y down, origin=hip)"""
    tr = math.radians(p["torso"])
    up = (math.sin(tr), -math.cos(tr))
    side = (math.cos(tr), math.sin(tr))          # torso right-hand normal
    hip = (0.0, 0.0)
    sh = (hip[0] + up[0] * P["torso"], hip[1] + up[1] * P["torso"])
    head_c = (sh[0] + up[0] * (P["neck"] + P["head_r"]),
              sh[1] + up[1] * (P["neck"] + P["head_r"]))
    sh_l = (sh[0] + side[0] * P["shoulder"], sh[1] + side[1] * P["shoulder"])
    sh_r = (sh[0] - side[0] * P["shoulder"], sh[1] - side[1] * P["shoulder"])
    hip_l = (hip[0] + side[0] * P["hip"], hip[1] + side[1] * P["hip"])
    hip_r = (hip[0] - side[0] * P["hip"], hip[1] - side[1] * P["hip"])

    def limb(origin, a_u, a_f, l1, l2):
        au = math.radians(a_u)
        mid = (origin[0] + math.sin(au) * l1, origin[1] + math.cos(au) * l1)
        af = math.radians(a_f)
        end = (mid[0] + math.sin(af) * l2, mid[1] + math.cos(af) * l2)
        return mid, end

    le, lh = limb(sh_l, p["la_u"], p["la_f"], P["upper_arm"], P["fore_arm"])
    re, rh = limb(sh_r, p["ra_u"], p["ra_f"], P["upper_arm"], P["fore_arm"])
    lk, lf = limb(hip_l, p["ll_u"], p["ll_f"], P["thigh"], P["shin"])
    rk, rf = limb(hip_r, p["rl_u"], p["rl_f"], P["thigh"], P["shin"])
    return dict(hip=hip, shoulder=sh, head=head_c, sh_l=sh_l, sh_r=sh_r,
                hip_l=hip_l, hip_r=hip_r, neck=sh,
                l_elbow=le, l_hand=lh, r_elbow=re, r_hand=rh,
                l_knee=lk, l_foot=lf, r_knee=rk, r_foot=rf,
                side=side)


def draw_stickman(pen, x, y, s, p, rim=(0, 150, 190), lw=6.2, face=True,
                  rim_w=1.05, rim_alpha=200, shadow=False, ground=None,
                  shadow_col=(0, 0, 0), rim_cols=None):
    """
    Draw the character. (x,y) is the *hip* in world coords; s scales world units.
    Returns anchor points in world space for attaching effects.
    """
    J = skeleton(p)
    bob = p.get("bob", 0.0)
    flip = p.get("flip", 1)

    def T(pt):
        return (x + pt[0] * s * flip, y + (pt[1] + bob) * s)

    if shadow:
        gy = ground if ground is not None else y + (P["thigh"] + P["shin"]) * s * 0.98
        pen.ellipse(x, gy, 34 * s, 6.5 * s, fill=shadow_col, outline=None)

    hip, sho, head = T(J["hip"]), T(J["shoulder"]), T(J["head"])
    shl, shr = T(J["sh_l"]), T(J["sh_r"])
    hr = P["head_r"] * s
    arm_l = (shl, T(J["l_elbow"]), T(J["l_hand"]))
    arm_r = (shr, T(J["r_elbow"]), T(J["r_hand"]))
    leg_l = (T(J["hip_l"]), T(J["l_knee"]), T(J["l_foot"]))
    leg_r = (T(J["hip_r"]), T(J["r_knee"]), T(J["r_foot"]))

    rc = rim_cols or rim

    def seg(pts, w, col, cap=True):
        pen.line(list(pts), fill=col, w=w, cap=cap)

    # ---- rim pass (a hair fatter, drawn behind) ---------------------------
    rw = lw + rim_w * 2.2
    for chain in (leg_r, leg_l, arm_r, arm_l):
        seg(chain, rw, rc)
    seg((shl, shr), rw, rc, cap=True)
    seg((hip, sho), rw, rc)
    pen.circle(head[0], head[1], hr + rim_w, fill=rc)

    # ---- body -------------------------------------------------------------
    back = tuple(int(c * 0.62) for c in C["ink"])
    seg(leg_r, lw * 0.96, back)
    seg(arm_r, lw * 0.92, back)
    seg((T(J["hip_r"]), hip), lw * 0.9, back)
    seg((T(J["hip_l"]), hip), lw, C["ink"])
    seg(leg_l, lw, C["ink"])
    seg((hip, sho), lw * 1.18, C["ink"])
    seg((shl, shr), lw * 0.92, C["ink"], cap=True)
    pen.circle(head[0], head[1], hr, fill=C["ink"])
    seg(arm_l, lw, C["ink"])

    if face:
        draw_face(pen, head, hr, p, rim)

    return dict(hip=(x, y), shoulder=sho, head=head, head_r=hr,
                hand_l=arm_l[2], hand_r=arm_r[2], foot_l=leg_l[2], foot_r=leg_r[2])


def draw_face(pen, head, hr, p, rim, ink=None):
    fx, fy = head
    f = p.get("face", "neutral")
    flip = p.get("flip", 1)
    look = p.get("look", 0.0)
    tr = math.radians(p.get("head", 0.0))
    # face frame: rotate feature offsets by head tilt; face sits slightly forward
    c, s_ = math.cos(tr), math.sin(tr)

    def F(dx, dy):
        # dx forward (+), dy down (+); forward is +x when flip=1
        dx, dy = dx * flip, dy
        return (fx + (dx * c - dy * s_) , fy + (dx * s_ + dy * c))

    eye_w = 0.34 * hr
    eye_y = -0.10 * hr
    fwd = 0.30 * hr
    ink = ink or C["ink"]
    white = C["white"]

    def eyes(kind, gap=1.0):
        for side in (-1, 1):
            ex, ey = F(fwd + side * gap * 0.30 * hr + look * 0.12 * hr, eye_y)
            if kind == "dot":
                pen.circle(ex, ey, 0.115 * hr, fill=white)
            elif kind == "wide":
                pen.circle(ex, ey, 0.20 * hr, fill=white)
                pen.circle(ex, ey, 0.085 * hr, fill=ink)
            elif kind == "shock":
                pen.circle(ex, ey, 0.235 * hr, fill=white)
                pen.circle(ex, ey + 0.02 * hr, 0.055 * hr, fill=ink)
            elif kind == "line":
                pen.line([(ex - 0.17 * hr, ey), (ex + 0.17 * hr, ey)], fill=white, w=0.085 * hr)
            elif kind == "x":
                d = 0.13 * hr
                pen.line([(ex - d, ey - d), (ex + d, ey + d)], fill=white, w=0.075 * hr)
                pen.line([(ex - d, ey + d), (ex + d, ey - d)], fill=white, w=0.075 * hr)
            elif kind == "squint":
                pen.line([(ex - 0.16 * hr, ey - 0.03 * hr), (ex + 0.16 * hr, ey + 0.05 * hr)],
                         fill=white, w=0.08 * hr)
            elif kind == "small":
                pen.circle(ex, ey, 0.075 * hr, fill=white)

    mx, my = F(fwd + 0.12 * hr, 0.40 * hr)
    if f == "neutral":
        eyes("dot")
        pen.line([(mx - 0.16 * hr, my), (mx + 0.16 * hr, my)], fill=white, w=0.07 * hr)
    elif f == "wide":
        eyes("wide")
        pen.circle(mx, my + 0.02 * hr, 0.10 * hr, fill=white)
    elif f == "shock":
        eyes("shock")
        pen.circle(mx, my + 0.03 * hr, 0.15 * hr, fill=white)
    elif f == "confused":
        # one wide eye, one squint + wavy mouth
        for i, side in enumerate((-1, 1)):
            ex, ey = F(fwd + side * 0.30 * hr + look * 0.12 * hr, eye_y)
            if i == 0:
                pen.circle(ex, ey, 0.19 * hr, fill=white)
                pen.circle(ex, ey, 0.08 * hr, fill=ink)
            else:
                pen.line([(ex - 0.16 * hr, ey - 0.04 * hr), (ex + 0.16 * hr, ey + 0.06 * hr)],
                         fill=white, w=0.08 * hr)
        pts = []
        for i in range(7):
            xx = mx - 0.2 * hr + i * 0.065 * hr
            pts.append((xx, my + (0.05 * hr if i % 2 else -0.02 * hr)))
        pen.line(pts, fill=white, w=0.065 * hr)
    elif f == "deadpan":
        eyes("line")
        pen.line([(mx - 0.14 * hr, my), (mx + 0.14 * hr, my)], fill=white, w=0.07 * hr)
    elif f == "scared":
        eyes("wide")
        pts = []
        for i in range(7):
            xx = mx - 0.22 * hr + i * 0.072 * hr
            pts.append((xx, my + (0.045 * hr if i % 2 else -0.045 * hr)))
        pen.line(pts, fill=white, w=0.06 * hr)
    elif f == "shrug":
        eyes("squint")
        pen.arc(mx, my + 0.06 * hr, 0.13 * hr, 20, 160, fill=white, w=0.06 * hr)
    elif f == "blank":
        eyes("dot")
        pen.line([(mx - 0.13 * hr, my), (mx + 0.13 * hr, my)], fill=white, w=0.06 * hr)
    elif f == "x":
        eyes("x")
    else:
        eyes("dot")

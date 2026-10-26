"""Environments and reusable props, rendered as cached RGBA layers."""
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from . import config as C
from . import draw as D

CACHE = {}

def cached(key, builder):
    if key not in CACHE:
        CACHE[key] = builder()
    return CACHE[key]

# ----------------------------------------------------------------- sky
def sky_layer(stops, seed=0, haze=0.25):
    def build():
        img = D.vgrad((C.W, C.H), stops)
        d = ImageDraw.Draw(img)
        rng = random.Random(seed)
        # faint drifting cloud bands
        for _ in range(7):
            y = rng.randint(120, 1100)
            x = rng.randint(-200, C.W)
            w = rng.randint(300, 700)
            d.rounded_rectangle([x, y, x + w, y + rng.randint(26, 60)],
                                radius=40, fill=(180, 190, 230, 14))
        img = img.filter(ImageFilter.GaussianBlur(18))
        # haze band near horizon
        haze_l = D.radial((C.W, C.H), (C.W / 2, C.H * 0.62), C.H * 0.75,
                          (150, 160, 210), int(70 * haze), 1.7)
        img.alpha_composite(haze_l)
        return img
    return build

SKY_STREET = [(0, (16, 20, 46)), (0.45, (26, 28, 64)), (0.8, (38, 32, 72)), (1, (18, 18, 38))]
SKY_ROOF = [(0, (10, 14, 36)), (0.5, (22, 26, 60)), (1, (34, 28, 66))]

# ------------------------------------------------------- building generator
def _building(d, x, base, w, h, color, rng, lit=0.18, glitch_windows=False):
    d.rectangle([x, base - h, x + w, base], fill=color)
    # roof detail
    d.rectangle([x + w * 0.2, base - h - 14, x + w * 0.8, base - h], fill=color)
    cols, rows = max(2, int(w / 46)), max(3, int(h / 58))
    for r in range(rows):
        for c in range(cols):
            wx = x + 10 + c * (w - 20) / cols
            wy = base - h + 18 + r * (h - 30) / rows
            ww, wh = (w - 20) / cols * 0.45, 20
            if rng.random() < lit:
                col = (120, 200, 220, 150) if rng.random() < .75 else (255, 196, 120, 120)
                if glitch_windows and rng.random() < .12:
                    d.rectangle([wx, wy + 6, wx + ww, wy + wh], fill=(214, 48, 142, 120))
                else:
                    d.rounded_rectangle([wx, wy, wx + ww, wy + wh], 3, fill=col)
            else:
                d.rounded_rectangle([wx, wy, wx + ww, wy + wh], 3, fill=(8, 10, 24, 200))

def city_layers(seed=11, far_base=1180, mid_base=1320):
    """Three parallax depth layers of skyline, each its own transparent image."""
    def build(which):
        rng = random.Random(seed + which)
        img = D.layer()
        d = ImageDraw.Draw(img)
        if which == 0:  # distant
            x = -40
            while x < C.W + 40:
                w = rng.randint(90, 170); h = rng.randint(380, 760)
                _building(d, x, far_base, w, h, (24, 28, 58, 235), rng, lit=0.10)
                x += w + rng.randint(8, 30)
        elif which == 1:  # mid
            x = -60
            while x < C.W + 60:
                w = rng.randint(150, 260); h = rng.randint(520, 1000)
                _building(d, x, mid_base, w, h, (16, 19, 42, 248), rng, lit=0.16)
                x += w + rng.randint(14, 44)
        else:  # near street blocks (upper portion only; road drawn separately)
            x = -80
            while x < C.W + 80:
                w = rng.randint(230, 360); h = rng.randint(700, 1250)
                _building(d, x, C.H, w, h, (10, 12, 28, 255), rng, lit=0.14,
                          glitch_windows=True)
                # abstract storefront sign
                d.rounded_rectangle([x + 24, C.H - 240, x + w - 24, C.H - 170], 8,
                                    fill=(20, 26, 50), outline=(64, 224, 232, 70), width=2)
                x += w + rng.randint(20, 60)
        return img
    return [cached(f"city{seed}-{i}", lambda i=i: build(i)) for i in range(3)]

def street_ground():
    def build():
        img = D.layer(); d = ImageDraw.Draw(img)
        d.polygon([(0, 1300), (C.W, 1300), (C.W, C.H), (0, C.H)], fill=(14, 15, 26, 255))
        # sidewalk edge glow
        d.line([(0, 1300), (C.W, 1300)], fill=(64, 224, 232, 60), width=3)
        vp = (C.W / 2, 1230)
        # perspective lane markings
        for i in range(9):
            t0, t1 = i / 9, (i + .55) / 9
            y0 = 1300 + t0 * (C.H - 1300); y1 = 1300 + t1 * (C.H - 1300)
            w0 = 14 + t0 * 40; w1 = 14 + t1 * 40
            d.polygon([(vp[0] - w0 / 2, y0), (vp[0] + w0 / 2, y0),
                       (vp[0] + w1 / 2, y1), (vp[0] - w1 / 2, y1)],
                      fill=(196, 214, 232, 120))
        # side converging lines
        for s in (-1, 1):
            d.line([(vp[0] + s * 60, vp[1]), (C.W / 2 + s * 760, C.H)],
                   fill=(96, 108, 132, 90), width=3)
        # abandoned object: small box
        d.rectangle([180, 1620, 260, 1690], fill=(24, 28, 48), outline=(64, 224, 232, 50), width=2)
        return img
    return cached("street_ground", build)

def streetlight(x=180, base=1500, h=760, glow=1.0, flicker=1.0):
    img = D.layer(); d = ImageDraw.Draw(img)
    D.line(d, (x, base), (x, base - h), (12, 14, 26, 255), 14)
    D.line(d, (x, base - h), (x + 120, base - h), (12, 14, 26, 255), 12)
    lx, ly = x + 120, base - h
    if flicker > 0.05:
        img.alpha_composite(D.radial(img.size, (lx, ly + 20), 200 * glow,
                                     (255, 226, 160), int(70 * flicker), 1.9))
        d.ellipse([lx - 16, ly - 10, lx + 16, ly + 14], fill=(255, 240, 200, int(235 * flicker)))
        d.ellipse([lx - 22, ly - 14, lx + 22, ly + 18], outline=C.CYAN + (int(110 * flicker),), width=3)
    else:
        d.ellipse([lx - 14, ly - 8, lx + 14, ly + 12], fill=(40, 44, 60, 255))
    return img

# ----------------------------------------------------------------- alley
def alley_static():
    def build():
        img = D.layer(); d = ImageDraw.Draw(img)
        # end wall with vertical tonal gradient feel (stacked polys)
        d.polygon([(150, 360), (930, 360), (880, 1500), (200, 1500)], fill=(34, 33, 46, 255))
        d.polygon([(150, 360), (930, 360), (905, 760), (175, 760)], fill=(42, 40, 56, 255))
        # side walls, slightly different values for depth
        d.polygon([(0, 0), (150, 360), (200, 1500), (0, C.H)], fill=(20, 20, 32, 255))
        d.polygon([(C.W, 0), (930, 360), (880, 1500), (C.W, C.H)], fill=(15, 15, 25, 255))
        # perspective edges
        D.line(d, (150, 360), (200, 1500), (64, 224, 232, 55), 3)
        D.line(d, (930, 360), (880, 1500), (64, 224, 232, 40), 3)
        rng = random.Random(21)
        # stains / pitting on end wall
        for _ in range(60):
            x, y = rng.randint(220, 860), rng.randint(420, 1450)
            d.ellipse([x, y, x + rng.randint(8, 40), y + rng.randint(6, 30)],
                      fill=(18, 17, 26, rng.randint(40, 100)))
        # horizontal concrete seams
        for sy in (560, 900, 1240):
            d.line([(185, sy), (895, sy + 10)], fill=(16, 15, 24, 160), width=3)
        # posters
        for px, py in ((250, 520), (720, 620), (300, 1280)):
            d.rectangle([px, py, px + 90, py + 130], fill=(48, 44, 64),
                        outline=(110, 120, 150, 140), width=2)
            for i in range(3):
                d.line([(px + 12, py + 24 + i * 26), (px + 78, py + 24 + i * 26)],
                       fill=(130, 136, 162, 100), width=3)
        # exposed cables
        d.arc([-160, 180, C.W + 160, 560], 205, 335, fill=(8, 8, 14, 255), width=6)
        d.arc([120, 300, 900, 620], 200, 340, fill=(64, 224, 232, 45), width=2)
        # dim overhead fixture, tight pool only
        d.rounded_rectangle([490, 330, 590, 372], 8, fill=(26, 28, 44),
                            outline=(120, 132, 160, 150), width=2)
        img.alpha_composite(D.radial((C.W, C.H), (540, 360), 170, (200, 212, 240), 16, 1.7))
        # floor with perspective lines and debris
        d.polygon([(200, 1500), (880, 1500), (C.W, C.H), (0, C.H)], fill=(15, 15, 24, 255))
        vp = (540, 1480)
        for s in (-1, 1):
            D.line(d, vp, (C.W / 2 + s * 820, C.H), (90, 100, 130, 70), 3)
        for _ in range(14):
            x, y = rng.randint(120, 960), rng.randint(1560, 1880)
            d.rectangle([x, y, x + rng.randint(6, 22), y + rng.randint(4, 12)],
                        fill=(40, 42, 58, rng.randint(80, 160)))
        return img
    return cached("alley", build)

def carved_text(lines, appear=1.0, seed=3, y0=720):
    """Physically-carved lettering; appear 0..1 reveals letters sequentially."""
    img = D.layer(); d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    total_chars = sum(len(ln) for ln in lines)
    budget = max(0.0, appear) * total_chars
    y = y0
    for li, line in enumerate(lines):
        # auto-fit font to safe width
        size = 104
        while size > 40:
            f = D.font("display", size, "ExtraBold")
            if d.textlength(line, font=f) <= C.W - 2 * C.SAFE_X - 40:
                break
            size -= 4
        f = D.font("display", size, "ExtraBold")
        tw = d.textlength(line, font=f)
        x = (C.W - tw) / 2
        before = sum(len(ln) for ln in lines[:li])
        n_show = max(0, min(len(line), int(budget - before + 0.6)))
        cut = line[:n_show]
        if cut:
            cw = d.textlength(cut, font=f)
            # groove: tight dark recess, bright stone face, chipped top edge
            d.text((x + 3, y + 4), cut, font=f, fill=(0, 0, 0, 255))
            d.text((x, y), cut, font=f, fill=(208, 210, 228, 255))
            d.text((x, y - 2), cut, font=f, fill=(238, 240, 250, 240))
            d.text((x - 1, y - 1), cut, font=f, fill=(120, 118, 140, 140))
            # small cracks radiating off the grooves
            for _ in range(int(10 * appear)):
                cx = rng.uniform(x, x + cw); cy = y + rng.uniform(-6, size + 10)
                d.line([(cx, cy), (cx + rng.uniform(4, 14), cy + rng.uniform(-5, 5))],
                       fill=(20, 19, 26, 200), width=2)
            # concrete dust below the line
            for _ in range(int(46 * appear)):
                cx = rng.uniform(x, x + cw); cy = y + size + rng.uniform(8, 30)
                rr = rng.uniform(2, 7)
                d.ellipse([cx, cy, cx + rr, cy + rr * .7],
                          fill=(118, 112, 126, rng.randint(50, 150)))
        y += int(size * 1.42)
    return img

# ---------------------------------------------------------------- corridor
def corridor_static(number="7B"):
    def build():
        img = D.layer(); d = ImageDraw.Draw(img)
        vp = (C.W / 2, 980)
        # walls/floor/ceiling
        d.polygon([(0, 0), (vp[0], vp[1]), (0, C.H)], fill=(20, 22, 36, 255))
        d.polygon([(C.W, 0), (vp[0], vp[1]), (C.W, C.H)], fill=(15, 17, 28, 255))
        d.polygon([(0, C.H), (vp[0], vp[1]), (C.W, C.H)], fill=(12, 13, 22, 255))
        d.polygon([(0, 0), (vp[0], vp[1]), (C.W, 0)], fill=(24, 26, 42, 255))
        f = D.font("display", 40, "Bold")
        for i in range(8):
            t = (i + 1) / 9
            w = 150 + t * 760
            top = 300 + t * 560
            bot = top + 260 + t * 520
            for s in (-1, 1):
                cx = vp[0] + s * w / 2
                dw = 70 + t * 90
                d.rounded_rectangle([cx - dw / 2, top, cx + dw / 2, bot], 8,
                                    fill=(10, 11, 20, 255), outline=(64, 224, 232, 80), width=2)
                tw = d.textlength(number, font=f)
                d.text((cx - tw / 2, top + 12), number, font=f, fill=C.CYAN + (160,))
        # vanishing door
        d.rectangle([vp[0] - 26, vp[1] - 60, vp[0] + 26, vp[1] + 70], fill=(6, 7, 14))
        return img
    return cached("corridor" + number, build)

# ---------------------------------------------------------------- stairwell
def stairwell_flight(steps=8, run=118, rise=54, x0=70, y0=1560, rail_h=210):
    """One solid flight of stairs ascending to the right. Returns (layer, top_anchor)."""
    img = D.layer(); d = ImageDraw.Draw(img)
    # zigzag tread/riser profile
    prof = [(x0, y0)]
    for i in range(steps):
        x = x0 + (i + 1) * run
        prof.append((x, y0 - i * rise))       # tread
        prof.append((x, y0 - (i + 1) * rise)) # riser
    top_x, top_y = prof[-1]
    body = [(x0 - 30, y0 + 560)] + prof + [(top_x + 30, top_y + 560)]
    d.polygon(body, fill=(52, 56, 76, 255))
    # tread highlights + riser shadows
    for i in range(steps):
        x = x0 + i * run; y = y0 - i * rise
        D.line(d, (x, y), (x + run, y), (128, 138, 168, 200), 4)
        d.line([(x + run, y), (x + run, y - rise)], fill=(30, 33, 50, 230), width=3)
    # railing: posts + sloping handrail
    for i in range(0, steps + 1, 2):
        x = x0 + i * run; y = y0 - i * rise
        D.line(d, (x + 14, y - 6), (x + 14, y - rail_h), (96, 108, 138, 235), 6)
    D.line(d, (x0 + 14, y0 - rail_h), (top_x + 14, top_y - rail_h),
           (132, 146, 176, 255), 9)
    return img, (top_x, top_y)

def stairwell_room():
    def build():
        img = D.layer(); d = ImageDraw.Draw(img)
        d.rectangle([0, 0, C.W, C.H], fill=(20, 22, 38, 255))
        for y in range(0, C.H, 120):
            d.line([(0, y), (C.W, y)], fill=(40, 44, 66, 80), width=2)
        # impossible-perspective windows
        for wx in (150, 740):
            d.rectangle([wx, 250, wx + 190, 430], fill=(12, 28, 50),
                        outline=(64, 224, 232, 95), width=3)
            d.line([(wx + 95, 250), (wx + 95, 430)], fill=(64, 224, 232, 60), width=2)
            d.line([(wx, 340), (wx + 190, 340)], fill=(64, 224, 232, 45), width=2)
        for lx in (280, 760):
            img.alpha_composite(D.radial((C.W, C.H), (lx, 150), 200, (220, 232, 248), 70, 1.7))
            d.ellipse([lx - 30, 132, lx + 30, 158], fill=(226, 234, 248, 220))
        return img
    return cached("stair_room", build)

# ---------------------------------------------------------------- rooftop
def rooftop_static():
    def build():
        img = D.layer(); d = ImageDraw.Draw(img)
        # distant city below parapet gap
        rng = random.Random(51)
        x = -30
        while x < C.W + 30:
            w = rng.randint(80, 150); h = rng.randint(180, 420)
            d.rectangle([x, 980 - h, x + w, 980], fill=(20, 24, 48, 235))
            x += w + 10
        # floor
        d.polygon([(0, 980), (C.W, 980), (C.W, C.H), (0, C.H)], fill=(26, 28, 42, 255))
        for i in range(1, 8):
            y = 980 + i * 130
            d.line([(0, y), (C.W, y)], fill=(60, 66, 92, 70), width=2)
        for i in range(-4, 5):
            d.line([(C.W / 2, 980), (C.W / 2 + i * 260, C.H)], fill=(60, 66, 92, 55), width=2)
        # parapet
        d.rectangle([0, 930, C.W, 985], fill=(16, 18, 30, 255))
        D.line(d, (0, 932), (C.W, 932), C.CYAN + (50,), 3)
        # access door
        d.rounded_rectangle([120, 1180, 300, 1560], 10, fill=(12, 14, 24),
                            outline=(96, 108, 132, 150), width=4)
        d.ellipse([268, 1370, 282, 1384], fill=(150, 160, 180))
        # ventilation units
        for vx, vy in ((760, 1240), (860, 1480), (220, 1700)):
            d.rounded_rectangle([vx, vy, vx + 130, vy + 110], 10, fill=(36, 40, 60),
                                outline=(80, 90, 120, 160), width=3)
            d.ellipse([vx + 30, vy + 25, vx + 100, vy + 85], outline=(120, 132, 160, 180), width=4)
        # antenna
        D.line(d, (900, 930), (900, 620), (10, 12, 22, 255), 6)
        d.ellipse([886, 606, 914, 634], outline=C.CYAN + (120,), width=3)
        # loose cable
        d.arc([600, 1080, 820, 1260], 200, 350, fill=(8, 10, 18, 255), width=5)
        return img
    return cached("rooftop", build)

# ------------------------------------------------------- impossible building
def impossible_building(seed=4, trace=0.0):
    img = D.layer(); d = ImageDraw.Draw(img)
    rng = random.Random(seed)
    bx0, bx1, top, base = 300, 780, 300, 1180
    d.polygon([(bx0, top), (bx1, top + 18), (bx1 + 24, base), (bx0 - 12, base)],
              fill=(13, 16, 34, 255))
    d.polygon([(bx0, top), (bx1, top + 18), (bx1, top + 60), (bx0, top + 44)],
              fill=(22, 26, 52, 255))
    # roof slab the figure can stand on
    d.rectangle([bx0 - 24, top - 14, bx1 + 24, top + 8], fill=(30, 34, 62, 255),
                outline=C.CYAN + (90,), width=2)
    floors = 11
    for i in range(floors):
        fy = top + 70 + i * (base - top - 100) / floors
        fh = (base - top - 110) / floors
        mis = rng.choice((-14, 0, 12))
        for c in range(4):
            wx = bx0 + 28 + c * 108 + mis
            d.rounded_rectangle([wx, fy, wx + 72, fy + fh * 0.55], 4,
                                fill=(8, 12, 28), outline=(64, 224, 232, 60), width=1)
            if rng.random() < .25:
                d.rectangle([wx, fy, wx + 72, fy + fh * .55], fill=(64, 224, 232, 90))
    # antenna bends slightly with no wind
    D.line(d, ((bx0 + bx1) // 2, top - 14), ((bx0 + bx1) // 2 + 14, top - 104),
           (10, 12, 22), 6)
    if trace > 0:
        d.line([(bx0, top), (bx0 - 12, base)], fill=C.CYAN + (int(200 * trace),), width=3)
        d.line([(bx1, top + 18), (bx1 + 24, base)], fill=C.CYAN + (int(120 * trace),), width=2)
    return img

# ---------------------------------------------------------------- props
def clock_face(r=200, eleven_eleven=True, glow=0.0):
    """Analog wall clock fixed at 11:11."""
    img = Image.new("RGBA", (r * 2 + 40, r * 2 + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = (img.width / 2, img.height / 2)
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=(14, 18, 34, 255),
              outline=C.CYAN + (180,), width=5)
    for i in range(12):
        a = math.radians(i * 30)
        p1 = (c[0] + math.sin(a) * r * .82, c[1] - math.cos(a) * r * .82)
        p2 = (c[0] + math.sin(a) * r * .92, c[1] - math.cos(a) * r * .92)
        D.line(d, p1, p2, (150, 170, 200, 200), 4)
    if eleven_eleven:
        for ang in (-30, 30):  # both hands near 11 and 1
            a = math.radians(ang)
            D.line(d, c, (c[0] + math.sin(a) * r * .6, c[1] - math.cos(a) * r * .6),
                   (236, 240, 248, 255), max(5, r // 18))
        d.ellipse([c[0] - 9, c[1] - 9, c[0] + 9, c[1] + 9], fill=C.MAGENTA + (255,))
    if glow:
        img.alpha_composite(D.radial(img.size, c, r * 1.5, C.CYAN, int(60 * glow), 1.8))
    return img

def digital_clock(text="11:11", scramble=0.0, size=120):
    f = D.font("display", size, "Bold")
    tmp = ImageDraw.Draw(D.layer())
    tw = tmp.textlength("00:00", font=f)
    img = Image.new("RGBA", (int(tw + 60), int(size * 1.7)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, img.width - 1, img.height - 1], 18,
                        fill=(6, 10, 22, 245), outline=C.CYAN + (170,), width=3)
    if scramble > 0:
        rng = random.Random(int(scramble * 999))
        text = "".join(rng.choice("0123456789:") for _ in text)
    d.text((30, size * .18), text, font=f, fill=C.CYAN + (255,))
    return img

def wrist_display(value="00:00:00", glitch=0.0, size=1.0):
    w, h = int(470 * size), int(200 * size)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 22, fill=(4, 8, 16, 245),
                        outline=C.CYAN + (200,), width=3)
    f = D.font("display", int(76 * size), "Bold")
    tw = d.textlength(value, font=f)
    d.text(((w - tw) / 2 + (glitch * 6), h * 0.16), value, font=f, fill=C.CYAN + (255,))
    # magenta fault line
    d.line([(w * .12, h * .72), (w * .88, h * .72 + glitch * 4)], fill=C.MAGENTA + (220,), width=3)
    if glitch > 0:
        rng = np.random.default_rng(90)
        for _ in range(int(glitch * 6)):
            y = int(rng.integers(10, h - 10))
            dx = int(rng.integers(-14, 14))
            img.paste(img.crop((0, y, w, y + 6)).transform((w, 6), Image.AFFINE, (1, 0, dx, 0, 1, 0)),
                      (0, y))
    return img

def head_countdown(value="98D 11:42:06", alpha=210):
    f = D.font("display", 34, "SemiBold")
    tmp = ImageDraw.Draw(D.layer())
    tw = tmp.textlength(value, font=f)
    w, h = int(tw + 44), 64
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 12, fill=(6, 10, 22, alpha),
                        outline=C.CYAN + (150,), width=2)
    d.text((22, 12), value, font=f, fill=(150, 235, 240, 255))
    return img

def key_prop(glint=0.0, scale=1.0, angle=0.0):
    """Small hand-held key drawn around its own centre; rotate/scale for hand shots."""
    w, h = int(340 * scale), int(150 * scale)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cx, cy = w / 2, h / 2
    metal = (196, 206, 224, 255)
    kw = max(3, int(9 * scale))
    # bow (ring)
    r = 42 * scale
    d.ellipse([cx - 130 * scale - r, cy - r, cx - 130 * scale + r, cy + r],
              outline=metal, width=kw)
    # shaft
    D.line(d, (cx - 130 * scale + r * .7, cy), (cx + 130 * scale, cy), metal, kw)
    # impossible geometric teeth
    for i, (tw, th) in enumerate(((22, 34), (30, 22), (16, 42))):
        x = cx + (40 + i * 30) * scale
        d.rectangle([x, cy, x + tw * scale, cy + th * scale], fill=metal)
    # cyan fault line along the shaft
    D.line(d, (cx - 120 * scale, cy - kw * .7), (cx + 120 * scale, cy - kw * .7),
           C.CYAN + (190,), max(2, int(3 * scale)))
    if glint > 0:
        img.alpha_composite(D.radial(img.size, (cx + 90 * scale, cy - 20 * scale),
                                     90 * scale, C.CYAN, int(150 * glint), 1.6))
    if angle:
        img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    return img

def choice_card(letter, title, symbol, accent, pulse=0.0, w=860, h=236):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], 24, fill=(10, 14, 30, 215),
                        outline=accent + (int(150 + 90 * pulse),), width=4)
    # travelling pulse edge (kept inside the card)
    if pulse > 0:
        span = h - 24
        py = 12 + int((pulse * span) % span)
        d.rounded_rectangle([6, py, w - 7, py + 5], 3, fill=accent + (220,))
    # letter badge
    d.ellipse([34, h / 2 - 44, 122, h / 2 + 44], outline=accent + (255,), width=5)
    fl = D.font("display", 52, "ExtraBold")
    tw = d.textlength(letter, font=fl)
    d.text((78 - tw / 2, h / 2 - 38), letter, font=fl, fill=accent + (255,))
    # symbol
    if symbol == "door":
        d.rectangle([w - 150, 56, w - 86, h - 56], outline=accent + (220,), width=5)
        d.ellipse([w - 104, h / 2 - 6, w - 92, h / 2 + 6], fill=accent + (220,))
    else:  # eye + watching silhouettes
        d.arc([w - 158, 70, w - 78, h - 70], 200, 340, fill=accent + (220,), width=5)
        d.arc([w - 158, 70, w - 78, h - 70], 20, 160, fill=accent + (220,), width=5)
        d.ellipse([w - 130, h / 2 - 18, w - 106, h / 2 + 18], outline=accent + (220,), width=4)
    f = D.font("sans", 38, "Bold")
    lines = D.wrap_text(title, f, w - 330)
    yy = h / 2 - (len(lines) - 1) * 26
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.text((150, yy - 26), ln, font=f, fill=C.WHITE + (255,))
        yy += 52
    return img

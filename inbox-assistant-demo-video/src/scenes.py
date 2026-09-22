"""All scenes. Every draw function receives the global time t (seconds) and
draws onto an RGBA canvas. Beats reference the VO word timings in beats.py."""
from PIL import Image, ImageDraw, ImageFilter
import math
from style import *
from ui import *
import beats as B

A, Bp, C, D = PAL["A"], PAL["B"], PAL["C"], PAL["D"]
WHITE = (255, 255, 255)

# ------------------------------------------------------------------ helpers
def bg_fill(img, col):
    ImageDraw.Draw(img).rectangle([0, 0, W, H], fill=tuple(col) + (255,))

def top_bar(img, pal, t, t0, dark=False):
    """Project chrome: three consistent chips inside the safe area."""
    a = anim(t, t0, 0.45)
    if a <= 0: return
    y = SAFE_Y0 + 24
    x = SAFE_X0 + int((1 - a) * -40)
    f = F("SemiBold", 22); f2 = F("Medium", 22)
    accent = pal.get("accent", pal.get("primary"))
    dotc = accent
    # project name with dot
    d = ImageDraw.Draw(img)
    d.ellipse([x, y - 7, x + 14, y + 7], fill=tuple(dotc) + (int(255 * a),))
    text(img, (x + 26, y), B.PROJECT, f, pal["text"], alpha=a, anchor="lm")
    px = x + 26 + text_size(B.PROJECT, f)[0] + 40
    sep = pal["sub"]
    for s in (B.CLIENT, B.ROLE):
        text(img, (px, y), "\u2022", f2, sep, alpha=a * 0.6, anchor="lm")
        px += 26
        text(img, (px, y), s, f2, pal["sub"], alpha=a, anchor="lm")
        px += text_size(s, f2)[0] + 40

def headline(img, x, y, words, t0, font, color, gap=0.09, maxw=None, alpha=1.0, anchor_center=False):
    """Word-by-word headline build (fade + 18px rise). words: str or list.
    Draws as one line; caller guarantees width fits via maxw check."""
    if isinstance(words, str): words = words.split(" ")
    full = " ".join(words)
    tw, th = text_size(full, font)
    if maxw is not None and tw > maxw:
        OVERFLOWS.append((full, maxw, tw))
    DRAWN.add(full)
    if anchor_center: x = x - tw // 2
    cx = x
    sw = text_size(" ", font)[0]
    for i, w_ in enumerate(words):
        a = anim(t, t0 + i * gap, 0.45) if False else None  # placeholder (t bound below)
    return cx, sw, th

def headline_t(img, t, x, y, words, t0, font, color, gap=0.09, maxw=None, alpha=1.0, center=False):
    if isinstance(words, str): words = words.split(" ")
    full = " ".join(words)
    tw, th = text_size(full, font)
    if maxw is not None and tw > maxw:
        OVERFLOWS.append((full, maxw, tw))
    if alpha > 0.02: DRAWN.add(full)
    if center: x = x - tw // 2
    sw = text_size(" ", font)[0]
    cx = x
    for i, w_ in enumerate(words):
        a = anim(t, t0 + i * gap, 0.5)
        if a > 0:
            put_sprite(img, text_sprite(w_, font, color), (cx, y + int((1 - a) * 18)),
                       alpha=a * alpha, anchor="lt")
        cx += text_size(w_, font)[0] + sw
    return tw, th

def tag(img, x, y, s, color, bg, t, t0, font=None, anchor="lm", dur=0.45):
    a = anim(t, t0, dur, ease_out_back)
    if a <= 0: return 0
    f = font or F("SemiBold", 20)
    w, h = chip(img, x, y, s, f, color, bg, pad_x=16, alpha=min(1, a * 1.5), scale=lerp(0.9, 1.0, a), anchor=anchor)
    return w

def avatar(img, cx, cy, r, initials, col, alpha=1.0):
    if alpha <= 0.01: return
    layer = Image.new("RGBA", (int(2 * r + 2),) * 2, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([0, 0, 2 * r, 2 * r], fill=tuple(col) + (255,))
    layer_t = text_sprite(initials, F("Bold", int(r * 0.9)), WHITE)
    layer.alpha_composite(layer_t, (int(r - (layer_t.size[0]) / 2 + 1), int(r - layer_t.size[1] / 2 + 1)))
    put_sprite(img, layer, (cx, cy), alpha=alpha, anchor="mm")

PEOPLE_COL = {"P": (124, 92, 252), "J": (25, 184, 157), "A": (255, 138, 61)}

def thread_card(img, x, y, w, pal, t, a=1.0, scale=1.0, rows=None, badge=None, sel=False, msg_count=None):
    """The locked thread card. rows: list of (initial, name_role, snippet)."""
    if a <= 0.01: return 0
    rows = rows if rows is not None else [
        ("P", B.PEOPLE["priya_r"], B.SNIP["times"]),
        ("J", B.PEOPLE["jordan_r"], B.SNIP["confirm"]),
    ]
    h = 118 + 78 * len(rows)
    border = pal.get("primary", pal.get("accent")) if sel else None
    card(img, x, y, w, h, r=22, fill=pal["card"], alpha=a, scale=scale, border=border, border_w=3)
    if scale != 1.0:
        return h  # skip inner text while scaling (kept sharp when settled)
    ix, iy = x + 32, y + 30
    text(img, (ix, iy), B.SUBJECT, F("Bold", 28), pal["text"], alpha=a, anchor="lt", maxw=w - 64 - 170, tag="subject")
    if msg_count is not None:
        chip(img, x + w - 32, iy + 16, f"{msg_count} messages", F("SemiBold", 18), pal["sub"], pal["chipbg"], pad_x=14, alpha=a, anchor="rm")
    text(img, (ix, iy + 44), f"{B.CLIENT}  \u2022  {B.ROLE}", F("Medium", 20), pal["sub"], alpha=a, anchor="lt", maxw=w - 64)
    hline(img, ix, x + w - 32, iy + 82, pal["line"], 2, a)
    ry = iy + 108
    for ini, name, snip in rows:
        avatar(img, ix + 22, ry + 14, 22, ini, PEOPLE_COL[ini], a)
        text(img, (ix + 62, ry - 2), name, F("SemiBold", 21), pal["text"], alpha=a, anchor="lt", maxw=w - 130)
        text(img, (ix + 62, ry + 26), snip, F("Regular", 20), pal["sub"], alpha=a, anchor="lt", maxw=w - 130, tag="snip")
        ry += 78
    if badge:
        chip(img, x + w - 32, y + h - 30, badge[0], F("SemiBold", 18), WHITE, badge[1], pad_x=14, alpha=a, anchor="rm")
    return h

def push_in(img, t, t0, t1, amount=0.04):
    """Slow camera push-in 100% -> 100+amount% between t0 and t1 (sharp)."""
    p = clamp01((t - t0) / max(0.01, t1 - t0))
    s = 1 + amount * ease_in_out_cubic(p) if p < 1 else 1 + amount
    if s <= 1.0005: return img
    cw, ch = int(W / s), int(H / s)
    x0, y0 = (W - cw) // 2, (H - ch) // 2
    return img.crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BICUBIC)

# ------------------------------------------------------------------ SCENE 1
def s1_hook(img, t):
    pal = A
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["text"], 10)
    top_bar(img, pal, t, 0.3)
    # thread card (right) lands at 2.12 ("opened a ... thread")
    a = anim(t, 2.05, 0.55)
    cx, cw = 1010, 756
    # duplicate stack at 11.7 (whole project)
    dup = anim(t, 11.55, 0.6)
    for k in (2, 1):
        if dup > 0:
            off = int(dup * 26 * k); sc = 1 - 0.03 * k * dup
            card(img, cx + int(off * 0.6), 300 + 118 * 0 - off, cw, 274, r=22, fill=pal["card"], alpha=dup * (0.9 - 0.2 * k), scale=sc, shadow_alpha=30)
    ya = 300 + int((1 - a) * 40)
    thread_card(img, cx, ya, cw, pal, t, a=a, msg_count=3)
    # "What's the latest here?" thought chip (5.78)
    tag(img, cx + cw - 20, ya - 22, "What\u2019s the latest here?", WHITE, pal["accent"], t, 5.75, font=F("SemiBold", 22), anchor="rm")
    # left headline builds (7.5 "Because in search, the inbox...")
    hf = F("ExtraBold", 76)
    headline_t(img, t, SAFE_X0, 330, ["Your", "inbox"], 7.5, hf, pal["text"], maxw=760)
    headline_t(img, t, SAFE_X0, 420, ["is", "the", "search"], 8.5, hf, pal["accent"], maxw=760)
    # sub-line at 10.84 "It's the whole project."
    sa = anim(t, 10.85, 0.5)
    text(img, (SAFE_X0, 540 + int((1 - sa) * 14)), "Not just email. The whole project.", F("Medium", 30), pal["sub"], alpha=sa, maxw=760)
    # small pulse ring around card on 10.9
    pp = anim(t, 10.9, 0.9, linear)
    if 0 < pp < 1:
        ripple(img, cx + cw // 2, ya + 137, pp, pal["accent"], r_max=420, alpha=0.5)

# ------------------------------------------------------------------ SCENE 2
def s2_overload(img, t):
    pal = A
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["text"], 10)
    top_bar(img, pal, t, -1)
    # left: category chips 2 rows x 3, pop in on words
    hf = F("ExtraBold", 54)
    headline_t(img, t, SAFE_X0, 200, "Everything lives in threads", 12.9, hf, pal["text"], maxw=760)
    positions = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2)]
    for (label, t0), (col, row) in zip(B.CAT_CHIPS, positions):
        a = anim(t, t0, 0.45, ease_out_back)
        if a <= 0: continue
        x = SAFE_X0 + col * 360; y = 320 + row * 78
        chip(img, x, y, label, F("SemiBold", 24), pal["text"], pal["card"], pad_x=22, pad_h=56, alpha=min(1, a * 1.4), scale=lerp(0.92, 1, a), anchor="lm", border=pal["line"])
    # 19.9 "all buried inside long threads": caption
    ba = anim(t, 19.95, 0.5)
    text(img, (SAFE_X0, 590 + int((1 - ba) * 12)), "Buried inside long threads", F("Medium", 30), pal["sub"], alpha=ba, maxw=760)
    # right: long thread stack
    cx, cw = 980, 786
    a = anim(t, 12.9, 0.55)
    n_rows_pre = 3 if t < 20.5 else 3 + int(min(8, (t - 20.5) / 4.0 * 8))
    ch_now = int(lerp(150 + 3 * 70, 700, clamp01((min(n_rows_pre, 8) - 3) / 5)))
    card(img, cx, 200, cw, ch_now, r=22, fill=pal["card"], alpha=a)
    if a > 0.5:
        # subject with Re: prefix growing (22.12, 22.98, 23.62)
        n_re = sum(1 for tt in (22.05, 22.95, 23.6) if t >= tt)
        prefix = "Re: " * n_re
        text(img, (cx + 32, 232), prefix + B.SUBJECT, F("Bold", 26), pal["text"], alpha=a, maxw=cw - 64 - 210, tag="re-subject")
        # counter
        cnt = 3
        if t >= 21.25: cnt = int(round(lerp(3, 12, ease_out_cubic((t - 21.25) / 0.7))))
        if t >= 23.05: cnt = int(round(lerp(12, 27, ease_out_cubic((t - 23.05) / 0.8))))
        bump = 1 + 0.04 * max(0, math.sin(clamp01((t - 21.25) / 0.3) * math.pi)) + 0.04 * max(0, math.sin(clamp01((t - 23.05) / 0.3) * math.pi))
        chip(img, cx + cw - 32, 248, f"Messages: {cnt}", F("Bold", 20), WHITE, pal["accent"] if cnt < 20 else pal["warn"], pad_x=16, alpha=a, anchor="rm", scale=bump)
        hline(img, cx + 32, cx + cw - 32, 282, pal["line"], 2, a)
        # rows: grow from 3 to many between 20.5 and 24.5
        n_rows = 3
        if t >= 20.5: n_rows = 3 + int(min(8, (t - 20.5) / 4.0 * 8))
        senders = [("A", B.PEOPLE["alex_r"], B.SNIP["friday"]), ("P", B.PEOPLE["priya_r"], B.SNIP["times"]),
                   ("J", B.PEOPLE["jordan_r"], B.SNIP["confirm"]), ("P", B.PEOPLE["priya_r"], B.SNIP["feedback"]),
                   ("A", B.PEOPLE["alex_r"], "Re: " + B.SNIP["friday"]), ("J", B.PEOPLE["jordan_r"], "Re: " + B.SNIP["times"]),
                   ("P", B.PEOPLE["priya_r"], "Re: " + B.SNIP["confirm"]), ("A", B.PEOPLE["alex_r"], "Re: " + B.SNIP["feedback"]),
                   ("J", B.PEOPLE["jordan_r"], "Re: Re: " + B.SNIP["times"]), ("P", B.PEOPLE["priya_r"], "Re: Re: " + B.SNIP["friday"]),
                   ("A", B.PEOPLE["alex_r"], "Re: Re: " + B.SNIP["confirm"])]
        ry = 318
        for i in range(min(n_rows, 7)):
            ini, name, snip = senders[i]
            ra = anim(t, 20.5 + (i - 3) * 0.5, 0.35) if i >= 3 else a
            indent = min(i, 4) * 18
            if ra <= 0: continue
            avatar(img, cx + 54 + indent, ry + 16, 18, ini, PEOPLE_COL[ini], ra)
            text(img, (cx + 86 + indent, ry), name, F("SemiBold", 20), pal["text"], alpha=ra, maxw=cw - 150 - indent)
            text(img, (cx + 86 + indent, ry + 26), snip, F("Regular", 19), pal["sub"], alpha=ra, maxw=cw - 150 - indent, tag="row-snip")
            ry += 70
        # fade at bottom to suggest more
        if n_rows >= 8:
            more = anim(t, 23.6, 0.4)
            text(img, (cx + cw // 2, 862), f"+ {cnt - 7} more replies", F("Medium", 19), pal["sub"], alpha=more, anchor="mm")

# ------------------------------------------------------------------ SCENE 3
def s3_timeline(img, t):
    pal = A
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["text"], 10)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 56)
    a0 = anim(t, 26.2, 0.5)
    text(img, (SAFE_X0, 190 + int((1 - a0) * 14)), "The real work isn\u2019t reading one email", F("Medium", 30), pal["sub"], alpha=a0, maxw=1400)
    headline_t(img, t, SAFE_X0, 240, "Reconstructing the timeline", 28.6, hf, pal["text"], maxw=1400)
    # timeline strip card
    ca = anim(t, 28.7, 0.55)
    x, y, w, h = SAFE_X0, 380, SAFE_X1 - SAFE_X0, 380
    card(img, x, y, w, h, r=22, fill=pal["card"], alpha=ca)
    nodes = [("Mon 9:14", B.PEOPLE["alex"], "Shortlist request", None),
             ("Mon 11:02", B.PEOPLE["priya"], "Times proposed", None),
             ("Tue 8:30", B.PEOPLE["jordan"], "Wed 11am confirmed", "Decided"),
             ("Tue 14:45", B.PEOPLE["priya"], "Feedback shared", None),
             ("Wed 10:05", B.PEOPLE["alex"], "Enterprise examples", "Pending")]
    n = len(nodes); lx0, lx1 = x + 110, x + w - 110; ly = y + 150
    la = anim(t, 28.9, 1.2, ease_out_cubic)
    if la > 0:
        hline(img, lx0, int(lerp(lx0, lx1, la)), ly, pal["line"], 6, ca)
    for i, (ts, who, what, note) in enumerate(nodes):
        nx = int(lerp(lx0, lx1, i / (n - 1)))
        na = anim(t, 29.0 + i * 0.28, 0.45, ease_out_back)
        if na <= 0: continue
        d = ImageDraw.Draw(img)
        r = int(14 * lerp(0.6, 1, na))
        d.ellipse([nx - r, ly - r, nx + r, ly + r], fill=tuple(pal["accent"]) + (255,), outline=(255, 255, 255, 255), width=4)
        text(img, (nx, ly - 46), ts, F("Bold", 22), pal["text"], alpha=na, anchor="mm")
        text(img, (nx, ly + 46), who, F("SemiBold", 20), pal["sub"], alpha=na, anchor="mm")
        text(img, (nx, ly + 76), what, F("Regular", 20), pal["sub"], alpha=na, anchor="mm", maxw=260)
        if note:
            t0 = 31.85 if note == "Decided" else 33.15
            col = (25, 184, 157) if note == "Decided" else pal["accent"]
            tag(img, nx, ly + 128, note, WHITE, col, t, t0, font=F("Bold", 21), anchor="mm")
    # cursor scrubs 31.0 -> 33.9 across strip
    cp = clamp01((t - 30.9) / 3.0)
    if 0 < cp < 1 or (t >= 33.9 and t < 35.1):
        p = ease_in_out_cubic(cp)
        cxp = lerp(lx0, lx1, p)
        # scrub head
        d = ImageDraw.Draw(img)
        d.line([(cxp, y + 60), (cxp, y + h - 40)], fill=tuple(pal["text"]) + (70,), width=2)
        cursor(img, cxp + 6, ly + 8, alpha=1.0)
    # counter of notes
    n1 = anim(t, 31.9, 0.3); n2 = anim(t, 33.2, 0.3)
    text(img, (SAFE_X1, 190), "Decided: " + str(int(n1 >= 1)) + "   Pending: " + str(int(n2 >= 1)), F("SemiBold", 22), pal["sub"], alpha=ca, anchor="rt")

# ------------------------------------------------------------------ SCENE 4
def s4_slip(img, t):
    pal = A
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["text"], 10)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 60)
    headline_t(img, t, W // 2, 190, "That\u2019s where things slip", 35.3, hf, pal["text"], center=True, maxw=1400)
    cards = [("Missed updates", "Updated shortlist requested", 37.05, "Client"),
             ("Unconfirmed availability", "Candidate replied: Wed 11am", 40.25, "Candidate"),
             ("Feedback not logged", B.SNIP["feedback"], 44.15, "Stakeholder")]
    cw, ch, gap = 500, 300, 40
    total = 3 * cw + 2 * gap; x0 = (W - total) // 2; y = 380
    for i, (title, sub, t0, who) in enumerate(cards):
        a = anim(t, t0, 0.5, ease_out_back)
        if a <= 0: continue
        x = x0 + i * (cw + gap)
        card(img, x, y + int((1 - a) * 30), cw, ch, r=22, fill=pal["card"], alpha=min(1, a * 1.5), scale=lerp(0.96, 1, a))
        if a >= 0.999:
            # coral accent bar
            rrect_layer(img, x + 32, y + 36, 8, 60, 4, fill=pal["warn"])
            text(img, (x + 60, y + 36), who, F("SemiBold", 20), pal["warn"])
            text(img, (x + 60, y + 66), title, F("Bold", 30), pal["text"], maxw=cw - 92, tag="slipcard")
            lines = wrap_lines(sub, F("Regular", 22), cw - 92)
            for li, ln in enumerate(lines[:2]):
                text(img, (x + 60, y + 130 + li * 32), ln, F("Regular", 22), pal["sub"], maxw=cw - 92)
            # x mark
            d = ImageDraw.Draw(img)
            mx, my = x + cw - 60, y + ch - 56
            d.ellipse([mx - 20, my - 20, mx + 20, my + 20], fill=(255, 236, 236, 255))
            d.line([(mx - 8, my - 8), (mx + 8, my + 8)], fill=tuple(pal["warn"]) + (255,), width=4)
            d.line([(mx - 8, my + 8), (mx + 8, my - 8)], fill=tuple(pal["warn"]) + (255,), width=4)

# ------------------------------------------------------------------ SCENE 4b
def s4b_wall(img, t):
    pal = A
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["text"], 10)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 56)
    a0 = anim(t, 47.1, 0.5)
    text(img, (SAFE_X0, 190 + int((1 - a0) * 12)), "Not because anyone is careless", F("Medium", 30), pal["sub"], alpha=a0, maxw=760)
    headline_t(img, t, SAFE_X0, 240, "The next action gets buried", 48.8, hf, pal["text"], maxw=800)
    # wall of text: card with grey lines
    x, y, w, h = 1000, 200, 766, 700
    ca = anim(t, 47.15, 0.6)
    card(img, x, y, w, h, r=22, fill=pal["card"], alpha=ca)
    if ca > 0.3:
        d = ImageDraw.Draw(img)
        import random
        rnd = random.Random(7)
        ly = y + 44
        hi_row = 11
        row = 0
        while ly < y + h - 40:
            la = anim(t, 47.3 + row * 0.06, 0.3)
            lw = rnd.randint(int(w * 0.45), int(w - 80))
            if row % 6 == 0: lw = int(w * 0.35)
            col = (226, 220, 212) if row % 6 else (200, 192, 184)
            if la > 0:
                d.rounded_rectangle([x + 40, ly, x + 40 + int(lw * la), ly + 14], radius=7, fill=col + (255,))
            if row == hi_row:
                # the buried next action line
                fa = anim(t, 50.2, 0.5)
                if fa > 0:
                    chip(img, x + 40, ly + 7, "Next action: confirm Wed 11am", F("SemiBold", 20), WHITE, pal["accent"], pad_x=14, alpha=fa, anchor="lm")
                    # fade back into wall after 51.8
                    fb = anim(t, 51.7, 0.9, linear)
                    if fb > 0:
                        rrect_layer(img, x + 24, ly - 14, w - 48, 44, 10, fill=pal["card"], alpha=fb * 0.85)
            ly += 30; row += 1
        text(img, (x + w - 32, y + h - 30), "Wall of text", F("SemiBold", 18), pal["sub"], anchor="rb", alpha=ca * 0.8)
    # caption
    ba = anim(t, 51.0, 0.5)
    text(img, (SAFE_X0, 340 + int((1 - ba) * 10)), "Too easy to lose in a wall of text", F("Medium", 28), pal["sub"], alpha=ba, maxw=780)

# ------------------------------------------------------------------ TITLE CARD (pivot)
def title_card(img, t):
    # gradient sweep warm -> cool between 53.18 and 54.6
    p = clamp01((t - 53.18) / 1.3)
    bgc = mix_rgb(A["bg"], Bp["bg"], ease_in_out_cubic(p))
    bg_fill(img, bgc)
    # sweeping band
    sweep = ease_in_out_cubic(clamp01((t - 53.18) / 1.0))
    band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(band)
    bx = int(lerp(-500, W + 200, sweep))
    for i in range(0, 400, 8):
        al = int(90 * (1 - i / 400))
        d.rectangle([bx - i, 0, bx - i + 8, H], fill=tuple(Bp["primary"]) + (al,))
    img.alpha_composite(band)
    a = anim(t, 53.3, 0.55)
    out = 1 - anim(t, 54.35, 0.35, ease_in_cubic)
    al = a * out
    if al > 0:
        text(img, (W // 2, 470 + int((1 - a) * 20)), "Thread summary + next actions", F("ExtraBold", 68), Bp["text"], alpha=al, anchor="mm", maxw=1500)
        text(img, (W // 2, 560), "Here\u2019s the cleaner way", F("Medium", 30), Bp["primary"], alpha=al, anchor="mm")

# ------------------------------------------------------------------ SCENE 6
def s6_conv(img, t):
    pal = Bp
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["primary"], 14)
    top_bar(img, pal, t, 54.6)
    hf = F("ExtraBold", 50)
    headline_t(img, t, SAFE_X0, 190, "Processes threads at the conversation level", 57.1, hf, pal["text"], maxw=1500)
    # left: inbox list panel (watching)
    x, y, w, h = SAFE_X0, 300, 620, 560
    ca = anim(t, 54.9, 0.55)
    card(img, x + int((1 - ca) * -40), y, w, h, r=22, fill=pal["card"], alpha=ca)
    if ca > 0.9:
        text(img, (x + 32, y + 30), "Search inbox", F("Bold", 24), pal["text"])
        # watching indicator pulse
        pulse = 0.5 + 0.5 * math.sin((t - 55.3) * 4)
        wa = anim(t, 55.25, 0.4)
        d = ImageDraw.Draw(img)
        d.ellipse([x + w - 150, y + 36, x + w - 138, y + 48], fill=tuple(pal["success"]) + (int(255 * wa * (0.6 + 0.4 * pulse)),))
        text(img, (x + w - 128, y + 42), "Watching", F("SemiBold", 20), pal["success"], alpha=wa, anchor="lm")
        hline(img, x + 32, x + w - 32, y + 80, pal["line"], 2)
        threads = [(B.SUBJECT, B.PEOPLE["jordan_r"], True),
                   ("Shortlist update \u2014 Northstar", B.PEOPLE["priya_r"], False),
                   ("Reference check \u2014 timing", B.PEOPLE["alex_r"], False)]
        ry = y + 104
        for subj, who, sel in threads:
            if sel:
                rrect_layer(img, x + 20, ry - 12, w - 40, 96, 14, fill=pal["chipbg"])
                rrect_layer(img, x + 20, ry - 12, 6, 96, 3, fill=pal["primary"])
            text(img, (x + 44, ry), subj, F("SemiBold", 22), pal["text"], maxw=w - 100)
            text(img, (x + 44, ry + 32), who, F("Regular", 20), pal["sub"], maxw=w - 100)
            if sel:
                chip(img, x + w - 40, ry + 24, "Selected", F("SemiBold", 16), WHITE, pal["primary"], pad_x=12, anchor="rm")
            ry += 120
    # right: messages collapse into conversation card at 57.8
    rx, rw = 830, 936
    col_p = anim(t, 57.75, 0.7)
    msgs = [B.SNIP["friday"], B.SNIP["times"], B.SNIP["confirm"], B.SNIP["feedback"], "Re: " + B.SNIP["confirm"]]
    # stacked message rows (before collapse)
    for i, m in enumerate(msgs):
        ma = anim(t, 55.4 + i * 0.12, 0.4)
        if ma <= 0: continue
        ty = 300 + i * 96
        cy = 300 + 60  # collapse target
        yy = int(lerp(ty, cy, col_p)); al = ma * (1 - col_p)
        if al > 0.01:
            card(img, rx, yy, rw, 80, r=16, fill=pal["card"], alpha=al, shadow_alpha=30)
            text(img, (rx + 28, yy + 40), "Message " + str(i + 1), F("SemiBold", 20), pal["sub"], alpha=al, anchor="lm")
            text(img, (rx + 170, yy + 40), m, F("Regular", 20), pal["text"], alpha=al, anchor="lm", maxw=rw - 200)
    # conversation card
    ca2 = anim(t, 58.05, 0.5)
    if ca2 > 0:
        cy = 300
        chh = 400
        card(img, rx, cy, rw, chh, r=22, fill=pal["card"], alpha=ca2, border=pal["primary"], border_w=2)
        text(img, (rx + 32, cy + 30), "Conversation", F("Bold", 26), pal["text"], alpha=ca2)
        tag(img, rx + rw - 32, cy + 46, "Thread ID tracked", WHITE, pal["secondary"], t, 58.55, font=F("SemiBold", 19), anchor="rm")
        text(img, (rx + 32, cy + 72), B.SUBJECT, F("SemiBold", 22), pal["sub"], alpha=ca2, maxw=rw - 64)
        hline(img, rx + 32, rx + rw - 32, cy + 112, pal["line"], 2, ca2)
        stats = [("Messages", "27"), ("Participants", "3"), ("Last update", "Wed 10:05")]
        for i, (k, v) in enumerate(stats):
            sa = anim(t, 58.9 + i * 0.15, 0.4)
            sx = rx + 32 + i * 290
            text(img, (sx, cy + 140), k, F("Medium", 19), pal["sub"], alpha=sa)
            text(img, (sx, cy + 166), v, F("Bold", 30), pal["text"], alpha=sa)
        # participants row
        pa = anim(t, 59.4, 0.4)
        py = cy + 250
        for i, (ini, nm) in enumerate([("P", B.PEOPLE["priya_r"]), ("J", B.PEOPLE["jordan_r"]), ("A", B.PEOPLE["alex_r"])]):
            px = rx + 32 + i * 300
            avatar(img, px + 18, py + 14, 18, ini, PEOPLE_COL[ini], pa)
            text(img, (px + 46, py + 14), nm, F("Medium", 19), pal["text"], alpha=pa, anchor="lm", maxw=240)
        # 59.92: not just individual messages
        na = anim(t, 59.95, 0.5)
        text(img, (rx + 32, cy + chh - 60), "Whole conversation, not individual messages", F("SemiBold", 20), pal["primary"], alpha=na, maxw=rw - 64)
        # data ticks (subtle progress dots) bottom right
        for i in range(5):
            on = ((t * 6) % 5) > i
            d = ImageDraw.Draw(img)
            d.ellipse([rx + rw - 40 - i * 16, cy + chh - 36, rx + rw - 32 - i * 16, cy + chh - 28],
                      fill=tuple(pal["primary"]) + (int(ca2 * (200 if on else 60)),))

# ------------------------------------------------------------------ SCENE 7
def s7_summary(img, t):
    pal = Bp
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["primary"], 14)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 50)
    # 62.3 "When something changes in a thread" -> conversation card w/ update dot; 64.6 morph into summary
    m = anim(t, 64.55, 0.6, ease_in_out_cubic)
    # geometry: conversation (right) -> summary (center-left bigger)
    x0, y0, w0, h0 = 830, 300, 936, 400
    x1, y1, w1, h1 = SAFE_X0 + 120, 250, 1380, 600
    x, y, w, h = int(lerp(x0, x1, m)), int(lerp(y0, y1, m)), int(lerp(w0, w1, m)), int(lerp(h0, h1, m))
    headline_t(img, t, SAFE_X0, 180, "A concise summary when a thread changes", 64.1, hf, pal["text"], maxw=1500)
    if m < 1:
        card(img, x, y, w, h, r=22, fill=pal["card"], alpha=1, border=pal["primary"], border_w=2)
    if m <= 0.05:
        text(img, (x + 32, y + 30), "Conversation", F("Bold", 26), pal["text"])
        text(img, (x + 32, y + 72), B.SUBJECT, F("SemiBold", 22), pal["sub"], maxw=w - 64)
        hline(img, x + 32, x + w - 32, y + 112, pal["line"], 2)
        # update pulse at 62.75
        ua = anim(t, 62.7, 0.4, ease_out_back)
        if ua > 0:
            chip(img, x + w - 32, y + 46, "Updated", F("SemiBold", 19), WHITE, pal["success"], pad_x=14, anchor="rm", scale=lerp(0.9, 1, ua), alpha=min(1, ua * 1.5))
            rp = ((t - 62.7) / 1.2) % 1
            ripple(img, x + w - 80, y + 46, rp, pal["success"], r_max=60, alpha=0.7)
        text(img, (x + 32, y + 140), "New message from " + B.PEOPLE["jordan"], F("Medium", 20), pal["sub"])
        text(img, (x + 32, y + 172), "\u201c" + B.SNIP["confirm"] + "\u201d", F("SemiBold", 22), pal["text"], maxw=w - 64)
        # left: inbox mini card static
        card(img, SAFE_X0, 300, 620, 400, r=22, fill=pal["card"], alpha=0.9)
        text(img, (SAFE_X0 + 32, 330), "Search inbox", F("Bold", 24), pal["text"])
        rrect_layer(img, SAFE_X0 + 20, 392, 580, 96, 14, fill=pal["chipbg"])
        rrect_layer(img, SAFE_X0 + 20, 392, 6, 96, 3, fill=pal["primary"])
        text(img, (SAFE_X0 + 44, 404), B.SUBJECT, F("SemiBold", 22), pal["text"], maxw=520)
        text(img, (SAFE_X0 + 44, 436), B.PEOPLE["jordan_r"], F("Regular", 20), pal["sub"])
    if m >= 1:
        card(img, x1, y1, w1, h1, r=24, fill=pal["card"], alpha=1)
        text(img, (x1 + 40, y1 + 36), "Summary", F("Bold", 30), pal["text"])
        chip(img, x1 + w1 - 40, y1 + 54, "Auto-generated", F("SemiBold", 18), pal["primary"], pal["chipbg"], pad_x=14, anchor="rm")
        text(img, (x1 + 40, y1 + 82), B.SUBJECT, F("SemiBold", 22), pal["sub"], maxw=w1 - 80)
        hline(img, x1 + 40, x1 + w1 - 40, y1 + 124, pal["line"], 2)
        icons = [pal["primary"], pal["success"], (245, 165, 36)]
        for i, (label, val, t0) in enumerate(B.SUMMARY_LINES):
            la = anim(t, t0 - 0.05, 0.45)
            if la <= 0: continue
            ry = y1 + 160 + i * 140
            # icon
            d = ImageDraw.Draw(img)
            ic = icons[i]
            d.rounded_rectangle([x1 + 40, ry, x1 + 96, ry + 56], radius=16, fill=tuple(ic) + (int(255 * la),))
            if i == 0:  # spark
                d.ellipse([x1 + 60, ry + 20, x1 + 76, ry + 36], fill=(255, 255, 255, int(255 * la)))
            elif i == 1:
                checkmark(img, x1 + 68, ry + 28, 14, WHITE, la * 1.0 + 0.001, width=4)
            else:
                d.ellipse([x1 + 58, ry + 18, x1 + 78, ry + 38], outline=(255, 255, 255, int(255 * la)), width=3)
                d.line([(x1 + 68, ry + 22), (x1 + 68, ry + 29), (x1 + 73, ry + 32)], fill=(255, 255, 255, int(255 * la)), width=3)
            text(img, (x1 + 120, ry - 2), label, F("Bold", 26), pal["text"], alpha=la)
            # type-on for the short value line
            tp = clamp01((t - t0) / 0.6)
            nchars = int(len(val) * tp)
            if nchars > 0:
                text(img, (x1 + 120, ry + 32), val[:nchars] + ("|" if tp < 1 and int(t * 8) % 2 == 0 else ""), F("Regular", 24), pal["sub"], maxw=w1 - 180, tag="sumval")
            # confidence mini chip on right
            conf = ["From message 27", "From message 12", "From message 19"][i]
            tag(img, x1 + w1 - 40, ry + 28, conf, pal["sub"], pal["chipbg"], t, t0 + 0.4, font=F("Medium", 17), anchor="rm")

# ------------------------------------------------------------------ SCENE 8
def s8_actions(img, t):
    pal = Bp
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["primary"], 14)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 50)
    headline_t(img, t, SAFE_X0, 180, "Next actions become a simple task list", 70.1, hf, pal["text"], maxw=1500)
    # floating chips (pop in) then snap into list at 78.72
    snap = anim(t, 78.7, 0.6, ease_in_out_cubic)
    # list panel
    px, py, pw, ph = SAFE_X0, 300, SAFE_X1 - SAFE_X0, 560
    la = anim(t, 77.9, 0.5)
    card(img, px, py + int((1 - la) * 30), pw, ph, r=22, fill=pal["card"], alpha=la)
    if la > 0.9:
        text(img, (px + 32, py + 30), "Task list", F("Bold", 26), pal["text"])
        text(img, (px + 32, py + 68), B.SUBJECT, F("Medium", 20), pal["sub"])
        hline(img, px + 32, px + pw - 32, py + 104, pal["line"], 2)
        # column headers
        oa = anim(t, 80.2, 0.4); da = anim(t, 81.1, 0.4)
        text(img, (px + 32, py + 124), "Action", F("SemiBold", 18), pal["sub"])
        text(img, (px + 900, py + 124), "Owner", F("SemiBold", 18), pal["sub"], alpha=oa)
        text(img, (px + 1200, py + 124), "Due", F("SemiBold", 18), pal["sub"], alpha=da)
        text(img, (px + pw - 32, py + 124), "Status", F("SemiBold", 18), pal["sub"], anchor="rt")
    # tasks created check at 81.8
    tc = anim(t, 81.75, 0.5, ease_out_back)
    if tc > 0 and la > 0.9:
        checkmark(img, px + pw - 74, py + 50, 16, pal["success"], tc * 1.0, width=4)
        text(img, (px + pw - 100, py + 50), "Tasks created", F("SemiBold", 20), pal["success"], alpha=tc, anchor="rm")
    for i, act in enumerate(B.ACTIONS):
        t0 = B.ACTION_SPEAK[act]
        a = anim(t, t0 - 0.05, 0.5, ease_out_back)
        if a <= 0: continue
        # floating position (row of chips, centered)
        fx = 340 + i * 330 + 150; fy = 520 + (i % 2) * 40
        # list target
        ly = py + 172 + i * 96; lx = px + 32
        ex, ey = int(lerp(fx, lx, snap)), int(lerp(fy, ly + 24, snap))
        f = F("SemiBold", 26)
        if snap < 1:
            anch = "mm" if snap == 0 else "lm"
            chip(img, ex if snap else fx, ey, act, f, WHITE if snap < 0.5 else pal["text"], pal["primary"] if snap < 0.5 else pal["chipbg"],
                 pad_x=26, pad_h=60, alpha=min(1, a * 1.5), scale=lerp(0.9, 1, a), anchor=anch)
        else:
            # settled row
            ra = anim(t, 78.85 + i * 0.2, 0.3, ease_out_back)
            if i % 2 == 1:
                rrect_layer(img, px + 20, ly - 8, pw - 40, 76, 12, fill=(250, 251, 255))
            # checkbox
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([lx, ly + 8, lx + 30, ly + 38], radius=8, outline=tuple(pal["primary"]) + (255,), width=2)
            text(img, (lx + 48, ly + 24), act, f, pal["text"], anchor="lm", scale=lerp(0.97, 1, ra))
            owner, due = B.ACTION_OWNER[act]
            oa = anim(t, 80.2 + i * 0.08, 0.4); da = anim(t, 81.1 + i * 0.08, 0.4)
            avatar(img, px + 918, ly + 24, 16, owner[0], PEOPLE_COL[owner[0]], oa)
            text(img, (px + 946, ly + 24), owner, F("Medium", 22), pal["text"], alpha=oa, anchor="lm")
            chip(img, px + 1200, ly + 24, due, F("SemiBold", 19), pal["primary"], pal["chipbg"], pad_x=14, alpha=da, anchor="lm")
            chip(img, px + pw - 32, ly + 24, "Open", F("SemiBold", 18), pal["sub"], (240, 243, 250), pad_x=14, alpha=ra, anchor="rm")
    # extracted label near chips before snap
    ea = anim(t, 71.3, 0.4) * (1 - snap)
    text(img, (W // 2, 440), "Extracted from the thread", F("Medium", 24), pal["sub"], alpha=ea, anchor="mm")

# ------------------------------------------------------------------ SCENE 10 (tracker)
def s10_tracker(img, t):
    pal = Bp
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["primary"], 14)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 50)
    headline_t(img, t, SAFE_X0, 180, "No rewriting. No manual copy paste.", 82.4, hf, pal["text"], maxw=1500)
    # struck chips
    for i, (s, t0) in enumerate([("Rewriting", 82.65), ("Copy paste", 84.25)]):
        a = anim(t, t0 - 0.2, 0.4)
        if a <= 0: continue
        x = SAFE_X0 + i * 260
        w, h = chip(img, x, 290, s, F("SemiBold", 22), pal["sub"], pal["card"], pad_x=20, anchor="lm", alpha=a, border=pal["line"])
        sp = anim(t, t0 + 0.05, 0.3, ease_out_cubic)
        strike(img, x + 10, x + w - 10, 290, pal["sub"], sp, width=3)
    # tracker panel
    x, y, w, h = SAFE_X0, 360, SAFE_X1 - SAFE_X0, 460
    ca = anim(t, 82.9, 0.5)
    card(img, x, y + int((1 - ca) * 30), w, h, r=22, fill=pal["card"], alpha=ca)
    if ca > 0.9:
        text(img, (x + 32, y + 30), "Search tracker", F("Bold", 26), pal["text"])
        text(img, (x + 32, y + 68), B.PROJECT + "  \u2022  " + B.CLIENT, F("Medium", 20), pal["sub"])
        hline(img, x + 32, x + w - 32, y + 104, pal["line"], 2)
        cols = [("Candidate", 32), ("Role", 420), ("Owner", 900), ("Status", 1160)]
        for label, cx in cols:
            text(img, (x + cx, y + 124), label, F("SemiBold", 18), pal["sub"])
        rows = [(B.PEOPLE["jordan"], B.ROLE, "Alex R.", "Interview scheduled"),
                ("Morgan Lee", B.ROLE, "Alex R.", "Shortlisted"),
                ("Sam Okafor", B.ROLE, "Alex R.", "Awaiting CV")]
        for i, (cand, role, own, status) in enumerate(rows):
            ry = y + 176 + i * 90
            if i == 0:
                up = anim(t, 84.9, 0.5)
                rrect_layer(img, x + 20, ry - 12, w - 40, 72, 12, fill=pal["chipbg"], alpha=up)
            text(img, (x + 32, ry + 24), cand, F("SemiBold", 24), pal["text"], anchor="lm")
            text(img, (x + 420, ry + 24), role, F("Regular", 22), pal["sub"], anchor="lm", maxw=440)
            avatar(img, x + 916, ry + 24, 16, "A", PEOPLE_COL["A"])
            text(img, (x + 944, ry + 24), own, F("Medium", 22), pal["text"], anchor="lm")
            if i == 0:
                up = anim(t, 84.9, 0.45, ease_out_back)
                if up < 0.5:
                    chip(img, x + 1160, ry + 24, "Availability pending", F("SemiBold", 19), pal["sub"], (240, 243, 250), pad_x=14, anchor="lm", alpha=1 - up * 2)
                else:
                    chip(img, x + 1160, ry + 24, status, F("SemiBold", 19), WHITE, pal["success"], pad_x=14, anchor="lm", scale=lerp(0.95, 1, up), alpha=min(1, (up - 0.5) * 3))
            else:
                chip(img, x + 1160, ry + 24, status, F("SemiBold", 19), pal["sub"], (240, 243, 250), pad_x=14, anchor="lm")
        tu = anim(t, 85.3, 0.45, ease_out_back)
        if tu > 0:
            checkmark(img, x + w - 74, y + 50, 16, pal["success"], tu, width=4)
            text(img, (x + w - 100, y + 50), "Tracker updated", F("SemiBold", 20), pal["success"], alpha=tu, anchor="rm")

# ------------------------------------------------------------------ SCENE 11 (draft)
def draft_card(img, pal, x, y, w, t, t_in, type_start=None, typed_all=False, edit_line=None, edit_p=0.0, alpha=1.0, buttons=None, hover=None, press=None, approved=0.0):
    a = anim(t, t_in, 0.5) * alpha
    if a <= 0: return
    h = 420 if buttons else 340
    card(img, x, y + int((1 - a) * 24), w, h, r=22, fill=pal["card"], alpha=a)
    if a < 0.95: return
    text(img, (x + 36, y + 32), "Reply to " + B.PEOPLE["jordan"], F("Bold", 26), pal["text"])
    # badge
    ac = pal.get("accent", (245, 165, 36))
    chip(img, x + w - 36, y + 50, "Draft (not sent)", F("Bold", 19), (120, 74, 0), (255, 236, 196), pad_x=16, anchor="rm", border=(245, 165, 36))
    text(img, (x + 36, y + 70), "Subject: " + B.SUBJECT, F("Medium", 20), pal["sub"], maxw=w - 72)
    hline(img, x + 36, x + w - 36, y + 106, pal["line"], 2)
    lines = list(B.DRAFT_LINES)
    if edit_line is not None:
        old = lines[2]; new = "Invite and prep notes coming today."
        # typing replace: delete then type
        if edit_p < 0.4:
            k = int(len(old) * (1 - edit_p / 0.4)); lines[2] = old[:k]
        else:
            k = int(len(new) * ((edit_p - 0.4) / 0.6)); lines[2] = new[:k]
    total = sum(len(l) for l in lines)
    if type_start is not None and not typed_all:
        tp = clamp01((t - type_start) / 2.6)
        budget = int(total * tp)
    else:
        budget = total
    ly = y + 130
    f = F("Regular", 24)
    for i, ln in enumerate(lines):
        if budget <= 0: break
        show = ln[:budget]; budget -= len(ln)
        if i == 2 and edit_line is not None and 0 < edit_p < 1:
            rrect_layer(img, x + 28, ly - 6, min(w - 56, text_size(show, f)[0] + 20), 40, 8, fill=(255, 243, 217))
            show = show + ("|" if int(t * 8) % 2 == 0 else "")
        elif type_start and not typed_all and budget <= 0 and tp < 1:
            show = show + ("|" if int(t * 8) % 2 == 0 else "")
        text(img, (x + 36, ly), show, f, pal["text"], maxw=w - 72, tag="draft")
        ly += 40
    if buttons:
        by = y + h - 72
        labels = [("Approve", (25, 184, 157), WHITE), ("Edit", pal["card"], pal["text"]), ("Reject", pal["card"], (239, 91, 91))]
        bx = x + 36
        for i, (lab, bgc, fg) in enumerate(labels):
            bw = 170
            hv = hover == lab; pr = press == lab
            sc = 1.03 if hv else (0.975 if pr else 1.0)
            card(img, bx, by, bw, 56, r=14, fill=bgc, shadow_alpha=80 if hv else 40, scale=sc,
                 border=pal["line"] if i > 0 else None, border_w=2)
            if approved > 0 and lab == "Approve":
                checkmark(img, bx + 36, by + 28, 12, WHITE, approved, width=3)
                text(img, (bx + 58, by + 28), "Approved", F("Bold", 21), fg, anchor="lm")
            else:
                text(img, (bx + bw // 2, by + 28), lab, F("Bold", 21), fg, anchor="mm")
            bx += bw + 20

def s11_draft(img, t):
    pal = Bp
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["primary"], 14)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 50)
    headline_t(img, t, SAFE_X0, 180, "Drafts the next reply for you", 86.3, hf, pal["text"], maxw=1500)
    # left: quality chips at 88.8/89.12/90.06
    for i, (s, t0) in enumerate([("Short", 88.75), ("Professional", 89.1), ("Grounded in the thread", 90.05)]):
        a = anim(t, t0, 0.45, ease_out_back)
        if a <= 0: continue
        y = 330 + i * 76
        checkmark(img, SAFE_X0 + 18, y, 16, pal["success"], a, width=4)
        text(img, (SAFE_X0 + 50, y), s, F("SemiBold", 26), pal["text"], anchor="lm", alpha=min(1, a * 1.5), maxw=460)
    # 92.08 "not starting from a blank screen"
    ba = anim(t, 92.1, 0.5)
    if ba > 0:
        card(img, SAFE_X0, 590, 460, 150, r=18, fill=pal["card"], alpha=ba * 0.9, shadow_alpha=25)
        text(img, (SAFE_X0 + 28, 620), "Blank screen", F("SemiBold", 22), pal["sub"], alpha=ba)
        strike(img, SAFE_X0 + 24, SAFE_X0 + 190, 632, pal["sub"], anim(t, 92.9, 0.35, ease_out_cubic), width=3)
        text(img, (SAFE_X0 + 28, 660), "Start from context, not zero", F("Regular", 21), pal["sub"], alpha=ba, maxw=400)
    draft_card(img, pal, 700, 300, 1066, t, 86.6, type_start=88.85)

# ------------------------------------------------------------------ SCENE 12 (control, amber)
def s12_control(img, t):
    pal = C
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["accent"], 16)
    top_bar(img, pal, t, 95.1)
    hf = F("ExtraBold", 54)
    headline_t(img, t, SAFE_X0, 180, "Nothing is sent without you", 95.3, hf, pal["text"], maxw=1500)
    ca = anim(t, 97.25, 0.45)
    text(img, (SAFE_X0, 262 + int((1 - ca) * 10)), "You stay in control", F("Medium", 28), (150, 96, 10), alpha=ca)
    draft_card(img, pal, SAFE_X0, 330, 1100, t, 95.4, typed_all=True, buttons=(t >= 97.85))
    # side note
    na = anim(t, 96.2, 0.5)
    if na > 0:
        x = 1310
        card(img, x, 330, 456, 200, r=20, fill=pal["card"], alpha=na)
        d = ImageDraw.Draw(img)
        rrect_layer(img, x + 28, 358, 8, 44, 4, fill=pal["accent"])
        text(img, (x + 52, 356), "Human review", F("Bold", 24), pal["text"], alpha=na)
        text(img, (x + 52, 392), "Default: review first", F("Regular", 21), pal["sub"], alpha=na, maxw=360)
        text(img, (x + 52, 424), "Auto-send: off", F("Regular", 21), pal["sub"], alpha=na, maxw=360)
        # toggle off
        rrect_layer(img, x + 52, 464, 60, 30, 15, fill=(226, 220, 205))
        d.ellipse([x + 56, 468, x + 78, 490], fill=(255, 255, 255, 255))

# ------------------------------------------------------------------ SCENE 13 (flag)
def s13_flag(img, t):
    pal = C
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["accent"], 16)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 52)
    headline_t(img, t, SAFE_X0, 180, "Uncertain? It flags, it doesn\u2019t guess", 98.9, hf, pal["text"], maxw=1500)
    # conflict card
    x, y, w, h = SAFE_X0, 300, 900, 380
    ca = anim(t, 99.0, 0.5)
    card(img, x, y + int((1 - ca) * 24), w, h, r=22, fill=pal["card"], alpha=ca)
    if ca > 0.9:
        text(img, (x + 32, y + 30), B.SUBJECT, F("Bold", 24), pal["text"], maxw=w - 300)
        tag(img, x + w - 32, y + 46, "Uncertain \u2014 needs review", (120, 74, 0), (255, 236, 196), t, 99.65, font=F("Bold", 19), anchor="rm")
        hline(img, x + 32, x + w - 32, y + 80, pal["line"], 2)
        # two conflicting times
        ta = anim(t, 101.65, 0.45, ease_out_back)
        tb = anim(t, 102.15, 0.45, ease_out_back)
        for i, (who, tm, a) in enumerate([(B.PEOPLE["priya_r"], "Tue 2pm", ta), (B.PEOPLE["jordan_r"], "Tue 3pm", tb)]):
            if a <= 0: continue
            bx = x + 32 + i * 420
            card(img, bx, y + 110, 400, 130, r=16, fill=pal["chipbg"], alpha=min(1, a * 1.5), scale=lerp(0.95, 1, a), shadow=False)
            if a > 0.9:
                text(img, (bx + 24, y + 132), who, F("SemiBold", 20), pal["sub"], maxw=350)
                text(img, (bx + 24, y + 168), tm, F("ExtraBold", 40), pal["text"])
        va = min(ta, tb)
        if va > 0.9:
            text(img, (x + 32 + 400 + 10, y + 175), "vs", F("Bold", 20), pal["sub"], anchor="mm")
        # reasons chips
        rs = [("Mixed intent", 100.75), ("Conflicting dates", 101.7), ("Unclear feedback", 102.8)]
        rx = x + 32
        for s, t0 in rs:
            a = anim(t, t0, 0.45, ease_out_back)
            if a <= 0: continue
            wch, _ = chip(img, rx, y + 300, s, F("SemiBold", 20), (120, 74, 0), (255, 243, 217), pad_x=16, anchor="lm", alpha=min(1, a * 1.5), scale=lerp(0.92, 1, a))
            rx += wch + 14
        text(img, (x + 32, y + 254), "Flag reasons", F("SemiBold", 18), pal["sub"])
    # human review queue at 104.4
    qa = anim(t, 104.35, 0.5)
    if qa > 0:
        qx, qy, qw, qh = 1090, 300, 676, 380
        card(img, qx + int((1 - qa) * 30), qy, qw, qh, r=22, fill=pal["card"], alpha=qa)
        if qa > 0.9:
            text(img, (qx + 32, qy + 30), "Human review", F("Bold", 24), pal["text"])
            chip(img, qx + qw - 32, qy + 46, "1 flagged", F("SemiBold", 18), WHITE, pal["accent"], pad_x=14, anchor="rm")
            hline(img, qx + 32, qx + qw - 32, qy + 80, pal["line"], 2)
            rrect_layer(img, qx + 20, qy + 100, qw - 40, 92, 14, fill=pal["chipbg"])
            rrect_layer(img, qx + 20, qy + 100, 6, 92, 3, fill=pal["accent"])
            text(img, (qx + 44, qy + 114), B.SUBJECT, F("SemiBold", 22), pal["text"], maxw=qw - 90)
            text(img, (qx + 44, qy + 148), "Conflicting dates \u2022 needs a human decision", F("Regular", 19), pal["sub"], maxw=qw - 90)
            ga = anim(t, 106.35, 0.45)
            text(img, (qx + 32, qy + 230), "Instead of guessing", F("Bold", 26), pal["text"], alpha=ga)
            text(img, (qx + 32, qy + 268), "No assumptions. Routed to you.", F("Regular", 21), pal["sub"], alpha=ga, maxw=qw - 64)
            # cursor moves to review at 105.5
            cp = ease_in_out_cubic(clamp01((t - 105.3) / 0.8))
            if t >= 105.0 and t < 107.7:
                cursor(img, lerp(qx + 300, qx + 140, cp), lerp(qy + 330, qy + 150, cp))

# ------------------------------------------------------------------ SCENE 12b (approve flow)
def s12b_approve(img, t):
    pal = C
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["accent"], 16)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 54)
    headline_t(img, t, SAFE_X0, 180, "You approve, edit, or reject", 107.8, hf, pal["text"], maxw=1500)
    # timeline of interaction
    hover = None; press = None; edit_p = 0.0; approved = 0.0
    x, y, w = SAFE_X0, 300, 1100
    by = y + 420 - 72 + 28
    b_edit = (x + 36 + 190 + 85, by); b_appr = (x + 36 + 85, by)
    # cursor path: start (900,760) -> Edit by 108.0; press 108.2; -> line 108.6; -> Approve 109.3; press 109.45
    if t < 108.0:
        p = ease_in_out_cubic(clamp01((t - 107.7) / 0.3)); cx = lerp(1000, b_edit[0], p); cy = lerp(800, b_edit[1], p)
    elif t < 108.45:
        cx, cy = b_edit
    elif t < 108.7:
        p = ease_in_out_cubic(clamp01((t - 108.45) / 0.25)); cx = lerp(b_edit[0], x + 420, p); cy = lerp(b_edit[1], y + 130 + 80 + 12, p)
    elif t < 109.35:
        p = ease_in_out_cubic(clamp01((t - 109.1) / 0.25)); cx = lerp(x + 420, b_appr[0], p); cy = lerp(y + 222, b_appr[1], p)
    else:
        cx, cy = b_appr
    if 107.95 <= t < 108.45: hover = "Edit"
    if 108.18 <= t < 108.32: press = "Edit"; hover = None
    if 108.6 <= t: edit_p = clamp01((t - 108.6) / 0.7)
    if 109.25 <= t: hover = "Approve"
    if 109.43 <= t < 109.57: press = "Approve"; hover = None
    if t >= 109.7: approved = anim(t, 109.7, 0.5, ease_out_back); hover = None
    draft_card(img, pal, x, y, w, t, 107.6, typed_all=True, buttons=True, edit_line=2 if t >= 108.3 else None, edit_p=edit_p, hover=hover, press=press, approved=approved)
    # ripples
    ripple(img, b_edit[0], b_edit[1], clamp01((t - 108.2) / 0.5), pal["accent"], r_max=60)
    ripple(img, b_appr[0], b_appr[1], clamp01((t - 109.45) / 0.5), (25, 184, 157), r_max=60)
    cursor(img, cx, cy, press=1.0 if press else 0.0)
    # side: step list
    sx = 1310
    sa = anim(t, 107.9, 0.5)
    if sa > 0:
        card(img, sx, 300, 456, 300, r=20, fill=pal["card"], alpha=sa)
        steps = [("Edit one line", 108.3), ("Approve", 109.5), ("Logged", 110.1)]
        for i, (s, t0) in enumerate(steps):
            yy = 340 + i * 64
            p = anim(t, t0, 0.5, ease_out_back)
            checkmark(img, sx + 46, yy + 14, 15, pal["success"] if p > 0 else pal["line"], p if p > 0 else 0.001, width=4)
            text(img, (sx + 78, yy + 14), s, F("SemiBold", 24), pal["text"] if p > 0 else pal["sub"], anchor="lm", alpha=sa)
        chip(img, sx + 32, 300 + 300 - 44, "Sent only after approval", F("SemiBold", 17), (120, 74, 0), (255, 243, 217), pad_x=14, anchor="lm", alpha=sa)

# ------------------------------------------------------------------ SCENE 15 (audit)
def s15_audit(img, t):
    pal = C
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["accent"], 16)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 54)
    headline_t(img, t, SAFE_X0, 180, "Everything is logged", 110.9, hf, pal["text"], maxw=1500)
    sa = anim(t, 112.4, 0.5)
    text(img, (SAFE_X0, 262 + int((1 - sa) * 10)), "A clear audit trail of what was summarized and why", F("Medium", 28), pal["sub"], alpha=sa, maxw=1400)
    x, y, w, h = SAFE_X0, 330, SAFE_X1 - SAFE_X0, 540
    ca = anim(t, 111.0, 0.5)
    card(img, x, y + int((1 - ca) * 24), w, h, r=22, fill=(31, 26, 16), alpha=ca, shadow_alpha=90)
    if ca > 0.9:
        # terminal-style header
        d = ImageDraw.Draw(img)
        for i, c in enumerate([(239, 91, 91), (245, 165, 36), (54, 211, 153)]):
            d.ellipse([x + 32 + i * 26, y + 28, x + 46 + i * 26, y + 42], fill=c + (255,))
        text(img, (x + w - 32, y + 35), "Audit log \u2022 " + B.SUBJECT, F("Medium", 19), (200, 190, 170), anchor="rm", maxw=w - 200)
        hline(img, x + 32, x + w - 32, y + 66, (70, 60, 44), 2)
        times = ["Wed 10:05", "Wed 10:05", "Wed 10:06", "Wed 10:06", "Wed 10:12"]
        why = ["new message from " + B.PEOPLE["jordan"], "3 lines: new, decided, pending", "4 actions with owners and due dates",
               "grounded in messages 12, 19, 27", "edited 1 line, then approved"]
        ff = F("Medium", 24); fw = F("Regular", 21)
        for i, line in enumerate(B.AUDIT_LINES):
            t0 = 111.6 + i * 0.72
            tp = clamp01((t - t0) / 0.45)
            if tp <= 0: break
            ly = y + 96 + i * 86
            n = int(len(line) * tp)
            text(img, (x + 32, ly), times[i], F("Medium", 20), (150, 140, 120))
            col = (54, 211, 153) if i == len(B.AUDIT_LINES) - 1 else (255, 236, 196)
            text(img, (x + 190, ly - 2), line[:n] + ("_" if tp < 1 and int(t * 10) % 2 == 0 else ""), ff, col)
            if tp >= 1:
                wa = anim(t, t0 + 0.4, 0.3)
                text(img, (x + 190, ly + 34), "why: " + why[i], fw, (170, 160, 140), alpha=wa, maxw=w - 260)
            # arrow to next
            if i < len(B.AUDIT_LINES) - 1 and tp >= 1:
                aa = anim(t, t0 + 0.55, 0.2)
                text(img, (x + 100, ly + 52), "\u2193", F("Bold", 22), (120, 110, 90), alpha=aa, anchor="mm")

# ------------------------------------------------------------------ SCENE 14 (evidence)
def s14_evidence(img, t):
    pal = C
    bg_fill(img, pal["bg"]); dots_pattern(img, 0, 0, W, H, 56, pal["accent"], 16)
    top_bar(img, pal, t, -1)
    hf = F("ExtraBold", 52)
    ia = anim(t, 116.65, 0.45)
    text(img, (SAFE_X0, 180 + int((1 - ia) * 10)), "And this is important", F("Medium", 28), (150, 96, 10), alpha=ia)
    h1a = 1 - anim(t, 120.5, 0.3, ease_in_cubic)
    if h1a > 0:
        headline_t(img, t, SAFE_X0, 226, "Job-related and evidence-based", 117.95, hf, pal["text"], maxw=1500, alpha=h1a)
    if t >= 120.5:
        headline_t(img, t, SAFE_X0, 226, "Summarizes what\u2019s in the thread", 120.6, hf, pal["text"], maxw=1500)
    # evidence card
    x, y, w, h = SAFE_X0, 330, SAFE_X1 - SAFE_X0, 570
    ca = anim(t, 118.2, 0.5)
    card(img, x, y + int((1 - ca) * 24), w, h, r=22, fill=pal["card"], alpha=ca)
    if ca > 0.9:
        text(img, (x + 32, y + 30), "Extracted fields", F("Bold", 26), pal["text"])
        text(img, (x + 32, y + 68), B.SUBJECT, F("Medium", 20), pal["sub"])
        hline(img, x + 32, x + w - 32, y + 104, pal["line"], 2)
        rows = [("Interview time", "Wed 11am", "From message 19", 118.6, True),
                ("Client feedback", "Wants enterprise examples", "From message 12", 119.3, True),
                ("Salary expectation", "Not stated", None, 123.9, False),
                ("Start date", "Not stated", None, 124.5, False)]
        for i, (k, v, src, t0, ok) in enumerate(rows):
            a = anim(t, t0, 0.45)
            if a <= 0: continue
            ry = y + 136 + i * 92
            if i % 2 == 1: rrect_layer(img, x + 20, ry - 12, w - 40, 76, 12, fill=(253, 250, 243), alpha=a)
            text(img, (x + 32, ry + 24), k, F("SemiBold", 24), pal["text"], anchor="lm", alpha=a)
            if ok:
                text(img, (x + 520, ry + 24), v, F("Medium", 24), pal["text"], anchor="lm", alpha=a)
                chip(img, x + 1100, ry + 24, src, F("SemiBold", 18), (10, 120, 100), (223, 246, 240), pad_x=14, anchor="lm", alpha=a)
                checkmark(img, x + w - 60, ry + 24, 14, pal["success"], a * 1.0, width=4)
            else:
                chip(img, x + 520, ry + 24, v, F("SemiBold", 20), (100, 100, 110), (236, 236, 240), pad_x=16, anchor="lm", alpha=a)
                text(img, (x + 1100, ry + 24), "Not inferred", F("Medium", 20), pal["sub"], anchor="lm", alpha=a)
        # footer rule
        fa = anim(t, 121.6, 0.5)
        text(img, (x + 32, y + h - 48), "Only what\u2019s actually in the thread. Nothing invented.", F("SemiBold", 21), (150, 96, 10), alpha=fa, anchor="lm", maxw=w - 64)

# ------------------------------------------------------------------ SCENE 17 (math, dark)
def s17_math(img, t):
    pal = D
    bg_fill(img, pal["bg"])
    # subtle glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W // 2 - 700, -300, W // 2 + 700, 500], fill=(70, 199, 255, 26))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    top_bar(img, pal, t, 126.2)
    hf = F("ExtraBold", 52)
    headline_t(img, t, SAFE_X0, 180, "Quick estimate", 126.1, hf, pal["text"], maxw=800)
    tag(img, SAFE_X0 + text_size("Quick estimate", hf)[0] + 30, 180 + 34, "Illustrative assumptions", (11, 18, 32), pal["accent"], t, 127.15, font=F("Bold", 20), anchor="lm")
    cards = [("Manual", "3", "min/thread", 129.6, "read, interpret, update notes"),
             ("Review", "1", "min/thread", 135.45, "with the workflow"),
             ("Saved", "2", "min/thread", 137.9, "3 \u2212 1"),
             ("Volume", "200", "threads/month", 140.2, "assumed")]
    cw, gap = 370, 28; total = 4 * cw + 3 * gap; x0 = (W - total) // 2; y = 300
    for i, (label, num, unit, t0, sub) in enumerate(cards):
        a = anim(t, t0, 0.5, ease_out_back)
        if a <= 0: continue
        x = x0 + i * (cw + gap)
        col = pal["success"] if label == "Saved" else pal["accent"]
        card(img, x, y + int((1 - a) * 24), cw, 250, r=22, fill=pal["card"], alpha=min(1, a * 1.5), scale=lerp(0.96, 1, a), shadow_alpha=110, border=pal["line"], border_w=1)
        if a > 0.95:
            text(img, (x + 32, y + 30), label, F("SemiBold", 22), pal["sub"])
            # roll number
            rp = ease_out_cubic(clamp01((t - t0) / 0.7))
            shown = str(int(round(int(num) * rp))) if num != "3" else str(int(round(3 * rp)))
            text(img, (x + 32, y + 70), shown, F("ExtraBold", 84), col)
            text(img, (x + 32 + text_size(shown, F("ExtraBold", 84))[0] + 14, y + 128), unit, F("Medium", 22), pal["sub"])
            text(img, (x + 32, y + 196), sub, F("Regular", 20), pal["sub"], maxw=cw - 64)
    # equation line 142.3
    ea = anim(t, 142.2, 0.5)
    if ea > 0:
        ey = 620
        rp = ease_out_cubic(clamp01((t - 142.3) / 0.9))
        mins = int(round(400 * rp))
        eq = f"(3 \u2212 1) \u00d7 200 = {mins} min"
        text(img, (W // 2, ey), eq, F("Bold", 48), pal["text"], alpha=ea, anchor="mm", maxw=1500)
    ha = anim(t, 144.55, 0.5, ease_out_back)
    if ha > 0:
        rp = ease_out_cubic(clamp01((t - 144.6) / 0.8))
        hrs = 6.7 * rp
        s = f"\u2248 {hrs:.1f} hours/month"
        text(img, (W // 2, 720), s, F("ExtraBold", 72), pal["success"], alpha=min(1, ha * 1.5), anchor="mm", scale=lerp(0.96, 1, ha), maxw=1500)
    fa = anim(t, 146.85, 0.5)
    text(img, (W // 2, 830), "Assumptions, not a guaranteed result", F("Medium", 26), pal["sub"], alpha=fa, anchor="mm")
    tb = anim(t, 137.2, 0.4)
    text(img, (W // 2, 580), "About 2 minutes saved per thread", F("Medium", 24), pal["sub"], alpha=tb * (1 - ea), anchor="mm")

# ------------------------------------------------------------------ SCENE 18 (close)
def s18_close(img, t):
    pal = D
    bg_fill(img, pal["bg"])
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W // 2 - 600, 700, W // 2 + 600, 1400], fill=(54, 211, 153, 22))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(120)))
    top_bar(img, pal, t, -1)
    # trust chips
    items = [("Independent portfolio prototype", 150.05), ("Fictional data", 152.15), ("Results vary", 153.3)]
    cx = SAFE_X0
    yv = 300
    head_in = anim(t, 155.95, 0.5)
    y_chip = int(lerp(yv, 250, ease_in_out_cubic(head_in)))
    for s, t0 in items:
        a = anim(t, t0, 0.45, ease_out_back)
        if a <= 0: continue
        w, _ = chip(img, cx, y_chip, s, F("SemiBold", 24), pal["text"], pal["chipbg"], pad_x=22, pad_h=58, anchor="lm", alpha=min(1, a * 1.5), scale=lerp(0.94, 1, a), border=pal["line"])
        cx += w + 18
    ba = anim(t, 154.4, 0.5) * (1 - head_in)
    text(img, (SAFE_X0, 400), "But the benefit is real", F("Medium", 30), pal["accent"], alpha=ba)
    # final headline
    hf = F("ExtraBold", 92)
    headline_t(img, t, SAFE_X0, 400, "Fewer misses.", 156.0, hf, pal["text"], maxw=1500)
    headline_t(img, t, SAFE_X0, 510, "Cleaner handoffs.", 157.55, hf, pal["success"], maxw=1500)
    sa = anim(t, 159.0, 0.5)
    text(img, (SAFE_X0, 660 + int((1 - sa) * 12)), "An organized search system, not a memory test", F("Medium", 34), pal["sub"], alpha=sa, maxw=1500)
    # bottom summary row
    fa = anim(t, 160.3, 0.5)
    if fa > 0:
        for i, s in enumerate(["Thread summary", "Next actions", "Draft reply", "Audit log"]):
            xx = SAFE_X0 + i * 320
            checkmark(img, xx + 16, 800, 14, pal["success"], fa * 1.0, width=4)
            text(img, (xx + 44, 800), s, F("SemiBold", 24), pal["text"], anchor="lm", alpha=fa)

SCENE_FN = {
    "S1_hook": s1_hook, "S2_overload": s2_overload, "S3_timeline": s3_timeline,
    "S4_slip": s4_slip, "S4b_wall": s4b_wall, "S6_conv": s6_conv, "S7_summary": s7_summary,
    "S8_actions": s8_actions, "S10_tracker": s10_tracker, "S11_draft": s11_draft,
    "S12_control": s12_control, "S13_flag": s13_flag, "S12b_approve": s12b_approve,
    "S15_audit": s15_audit, "S14_evidence": s14_evidence, "S17_math": s17_math, "S18_close": s18_close,
}
PUSH = {  # slow camera push-ins on reading moments (t0, t1, amount)
    "S7_summary": (65.5, 69.8, 0.035), "S17_math": (142.0, 149.0, 0.035),
    "S15_audit": (111.5, 116.5, 0.03), "S3_timeline": (29.0, 35.0, 0.03),
}

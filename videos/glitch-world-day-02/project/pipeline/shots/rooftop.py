"""Scenes 7-17 — Rooftop confrontation through disappearance (cues 16-33)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register

MYST = dict(x=540, y=1230, h=420)
HERO = dict(x=540, y=1640, h=430)

@register
class Rooftop(Scene):
    name = "06_rooftop"
    start = 63.50
    end = 109.80

    def setup(self):
        self.rng = random.Random(606)
        self.fracture = effects.SkyFracture(seed=17)
        self.base = D.layer()
        self.base.alpha_composite(D.vgrad((C.W, C.H), world.SKY_ROOF))
        self.base.alpha_composite(world.rooftop_static())

    # ----------------------------------------------------------- citizens
    def _city_turn(self, t):
        """Cue 29 cutaway: the whole city turns its head as one system."""
        c = self.cues[29]
        turn_t = c["start"] + 0.55 - self.start
        turned = ease.in_out_cubic(ease.maprange(t, turn_t, turn_t + 0.18))
        sub = (t - (c["start"] - self.start)) / (c["end"] - c["start"])
        img = common_street_base()
        wide = [
            ("step", 140, 1650, 400), ("cup", 360, 1660, 390),
            ("cyclist", 590, 1660, 390), ("phone", 800, 1650, 400),
            ("reach", 980, 1500, 300),
        ]
        if sub < 0.40 or sub >= 0.70:
            specs = wide                       # synchronized wide row dominates
        elif sub < 0.55:
            specs = [("cup", 540, 1580, 620)]  # close-up: cup holder
        else:
            specs = [("cyclist", 540, 1540, 660)]  # close-up: cyclist
        for kind, x, y, h in specs:
            pose = rig.citizen(kind, turn=turned, x=x, y=y, h=h)
            rig.draw_stickman(img, pose, rng=self.rng, rim_strength=0.4)
        # synchronized head-turn flash on every wide-row head
        if turned > 0 and (sub < 0.40 or sub >= 0.70):
            dd = ImageDraw.Draw(img)
            for _, x, y, h in specs:
                hy = y - h * 0.34 * 2 - h * 0.105
                dd.ellipse([x - 8, hy - 8, x + 8, hy + 8],
                           fill=C.CYAN + (int(150 * turned),))
        # rooftop beacon pulling every gaze upward
        img.alpha_composite(D.radial((C.W, C.H), (540, 170), 540, C.CYAN,
                                     int(60 * turned), 1.7))
        return D.vignette(img, 108)

    # ----------------------------------------------------------- main stage
    def render(self, t, frame):
        g = t + self.start
        c16, c19, c20, c24, c25, c28, c29, c30, c31, c32, c33 = (
            self.cues[i] for i in (16, 19, 20, 24, 25, 28, 29, 30, 31, 32, 33))

        if c29["start"] - self.start <= t <= c29["end"] - self.start + 0.15:
            return self._city_turn(t)

        stage = self.base.copy()
        # --- sky fracture growth from cue 25 onward ---
        if g >= c25["start"]:
            grow = ease.in_out_quart(ease.maprange(g, c25["start"], c25["start"] + 4.5))
            grow = min(1.0, grow)
            fl = D.layer()
            self.fracture.draw(fl, grow, offset_px=3 * math.sin(t * 1.7), rng=self.rng)
            stage.alpha_composite(fl)
            # a distant building briefly exposes wireframe
            if int(t * 2.2) % 7 == 0:
                dd = ImageDraw.Draw(stage)
                effects.wireframe_box(dd, (180, 700, 360, 900), alpha=120)

        # --- room-with-no-door subliminal outline (cue 31) ---
        if c31["start"] <= g <= c31["end"]:
            dd = ImageDraw.Draw(stage)
            a = int(150 * math.sin(ease.maprange(g, c31["start"], c31["end"]) * math.pi))
            dd.rectangle([700, 760, 800, 900], outline=(140, 230, 240, a), width=3)

        # --- mystery figure on its own layer (for glitch/vanish isolation) ---
        myst_layer = D.layer()
        myst_pose = self._mystery_pose(t, g)
        gm = rig.draw_stickman(myst_layer, myst_pose, style="mystery",
                               rng=self.rng) if myst_pose.get("visible", True) else None
        # warning double-image (cue 32)
        if c32["start"] <= g <= c32["end"] and int(t * 10) % 6 == 0:
            myst_layer = effects.double_silhouette(myst_layer, None, 1.0)

        # --- hero on his own layer ---
        hero_layer = D.layer()
        hero_pose = self._hero_pose(t, g)
        hero_rim = 0.55
        if c28["start"] <= g <= c28["end"] + 0.5:  # cyan system flicker at "YOU do"
            hero_rim = 0.55 + 0.45 * (1 if int(t * 12) % 3 == 0 else 0)
        gh = rig.draw_stickman(hero_layer, hero_pose, rng=self.rng,
                               rim_strength=hero_rim)

        # --- wrist countdown close-up (cues 20-24) ---
        wrist_close = c20["start"] + 1.4 <= g <= c24["end"] + 0.3
        vanishing = g >= c33["start"]
        if not vanishing:
            stage.alpha_composite(myst_layer)
        stage.alpha_composite(hero_layer)

        if wrist_close:
            disp_glitch = 0.9 if g < c24["start"] else 0.15
            disp = world.wrist_display("00:00:00", glitch=disp_glitch *
                                       (0.6 + 0.4 * math.sin(t * 13)))
            # extreme close-up: magnify the mystery figure's wrist region
            wx = gm["hand_r"][0] if gm else 560
            wy = (gm["elbow_r"][1] + gm["hand_r"][1]) / 2 if gm else 1060
            cx, cy = int(wx), int(wy)
            region = stage.crop((max(0, cx - 300), max(0, cy - 300),
                                 min(C.W, cx + 300), min(C.H, cy + 300))).resize(
                (C.W, C.W), Image.BICUBIC)
            zoom = D.layer()
            zoom.alpha_composite(region, (0, 380))
            zoom.alpha_composite(disp, (C.W // 2 - disp.width // 2, 780))
            stage = D.vignette(zoom, 90)
        else:
            # wrist display stays visible on mystery's raised arm during cue 20-24 wide
            if c20["start"] <= g <= c24["end"] and gm:
                disp = world.wrist_display("00:00:00", glitch=0.5, size=0.42)
                wx = (gm["elbow_r"][0] + gm["hand_r"][0]) / 2
                wy = (gm["elbow_r"][1] + gm["hand_r"][1]) / 2
                stage.alpha_composite(disp, (int(wx - disp.width / 2),
                                             int(wy - disp.height / 2)))

        # --- key transfer (cue 30) ---
        if c30["start"] <= g <= c30["end"] + 0.4:
            self._key_transfer(stage, t, g, c30, gm, gh)

        # --- disappearance segmentation (cue 33) ---
        if c33["start"] <= g:
            u = ease.in_out_cubic(ease.maprange(g, c33["start"] + 0.25, c33["start"] + 1.0))
            if u < 1.0:
                stage = self._segment_vanish(stage, myst_layer, MYST, u, t)
            # hero reaches into the empty space
            if g > c33["start"] + 0.9:
                dd = ImageDraw.Draw(stage)
                D.line(dd, gh["hand_l"], (gh["hand_l"][0] + 60, gh["hand_l"][1] - 120),
                       C.INK + (255,), max(7, int(HERO["h"] * 0.026)))

        # --- camera language per phase ---
        scale, dx, dy = 1.0, 0.0, 0.0
        if g < c19["start"]:
            scale, dx, dy = ease.camera_push(t, c19["start"] - self.start, 0.05)
        elif c19["start"] <= g <= c19["end"]:
            scale = 1.08  # stable framing on the revelation
        elif c25["start"] <= g <= c28["end"]:
            scale, dx, dy = ease.camera_push(g - c25["start"], 9.0, 0.06)
            dy -= 40
        elif c32["start"] <= g <= c32["end"]:
            scale, dx, dy = ease.camera_push(g - c32["start"], c32["end"] - c32["start"], 0.08)
        out = ease.place_camera(D.layer(), stage, scale, dx, dy)
        return D.vignette(out, 96)

    # ------------------------------------------------------------- poses
    def _mystery_pose(self, t, g):
        c19, c20, c32 = self.cues[19], self.cues[20], self.cues[32]
        p = dict(MYST)
        if g < c19["start"] - 0.8:
            p.update(face="back", arm_l=10, arm_r=-10)            # waiting, back turned
        elif g < c19["start"]:
            u = ease.in_out_cubic(ease.maprange(g, c19["start"] - 0.8, c19["start"]))
            p.update(face="back" if u < 0.5 else "normal",
                     head_tilt=-14 * u, lean=2 * u)
        else:
            p.update(face="normal", eye="flat", head_tilt=4)
            if c20["start"] <= g <= self.cues[24]["end"]:
                # slow arm raise toward the protagonist
                u = ease.out_cubic(ease.maprange(g, c20["start"], c20["start"] + 1.1))
                p.update(arm_r=-20 - 110 * u, elbow_r=18, head_tilt=0)
            if c32["start"] <= g <= c32["end"]:
                p.update(head_tilt=-8, lean=-3, arm_l=24, elbow_l=14)
        return p

    def _hero_pose(self, t, g):
        c18, c19, c24, c28, c30, c33 = (self.cues[i] for i in (18, 19, 24, 28, 30, 33))
        p = dict(HERO)
        if g < c18["start"]:
            u = ease.maprange(g, self.start, c18["start"])
            p.update(lean=12 - 8 * u, arm_l=30, arm_r=-24, eye="squint",
                     head_tilt=6 * math.sin(t * 2))                     # catching breath
        elif g < c19["start"]:
            p.update(arm_l=96, elbow_l=40, lean=6, eye="wide", head_tilt=-6)  # question gesture
        elif g <= c19["end"] + 0.6:
            u = ease.out_back(ease.maprange(g, c19["start"], c19["start"] + 0.8))
            p.update(lean=-10 * u, head_tilt=10 * u, eye="wide", mouth="o",
                     arm_l=20, arm_r=-18)                                # recoil
        elif g <= c24["end"] + 0.3:
            p.update(lean=6, head_tilt=-8, eye="squint", arm_l=70, elbow_l=30)
        elif g <= c28["end"]:
            p.update(eye="wide", mouth="o", lean=-4, arm_l=50, arm_r=-46)
            if g >= c28["start"]:
                u = ease.in_out_cubic(ease.maprange(g, c28["start"], c28["end"] + 0.4))
                p.update(lean=-12 - 6 * u, head_tilt=14, mouth="flat",
                         arm_l=18, arm_r=-14)                            # confidence collapses
        elif g < c30["start"]:
            p.update(eye="normal", lean=3, head_tilt=2)
        elif g <= c30["end"] + 0.4:
            u = ease.in_out_quad(ease.maprange(g, c30["start"], c30["start"] + 1.2))
            p.update(arm_l=80 + 30 * u, elbow_l=36, eye="squint")       # reaching for key
        elif g < c33["start"]:
            p.update(head_tilt=8, eye="squint", arm_l=40, arm_r=-30,
                     mouth="flat")
        else:
            p.update(eye="wide", mouth="o", lean=-4)
        return p

    def _key_transfer(self, stage, t, g, c30, gm, gh):
        u = ease.in_out_quad(ease.maprange(g, c30["start"], c30["start"] + 1.3))
        key = world.key_prop(glint=0.5 + 0.5 * math.sin(t * 6), scale=0.9)
        if gm and gh:
            x = gm["hand_l"][0] + (gh["hand_l"][0] - gm["hand_l"][0]) * u
            y = gm["hand_l"][1] + (gh["hand_l"][1] - gm["hand_l"][1]) * u
            stage.alpha_composite(key, (int(x - key.width / 2), int(y - key.height / 2)))
        if g > c30["end"] - 0.8:  # brief macro glint of the key in his palm
            gl = world.key_prop(glint=1.0, scale=2.2)
            stage.alpha_composite(gl, (C.W // 2 - gl.width // 2, 1260))

    def _segment_vanish(self, stage, myst_layer, anchor, u, t):
        # horizontal segmentation confined to the mystery figure's own bounds
        x0, x1 = int(anchor["x"] - 200), int(anchor["x"] + 200)
        y0, y1 = int(anchor["y"] - 330), int(anchor["y"] + 90)
        region = myst_layer.crop((x0, y0, x1, y1))
        out = D.layer()
        strips = 6
        rh = region.height // strips
        for i in range(strips):
            band = region.crop((0, i * rh, region.width,
                                min(region.height, (i + 1) * rh)))
            shift = int(math.sin(t * 20 + i * 1.9) * 26 * u)
            alpha = max(0, 1 - u * 1.25)
            if alpha > 0:
                band.putalpha(band.getchannel("A").point(lambda a: int(a * alpha)))
            out.alpha_composite(band, (x0 + shift, y0 + i * rh))
        stage.alpha_composite(out)
        return stage

def common_street_base():
    from .common import street_world
    return street_world()

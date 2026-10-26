"""Scene 2 — Six Hours of Searching (cues 4-7, 16.36s - 34.01s)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register
from . import common

A_END = 10.19      # streetlight sub-shot ends (global 26.55)
B_END = 12.59      # clocks sub-shot ends   (global 28.95)

@register
class Montage(Scene):
    name = "02_montage"
    start = 16.36
    end = 34.01

    def setup(self):
        self.rng = random.Random(202)
        self.lamp_x = 268

    # ----------------------------------------------------------- A: streetlight
    def _streetlight_shot(self, t):
        img = common.street_world()
        # lamp flicker windows (local seconds)
        flick = 1.0
        for a, b in ((6.35, 6.62), (7.05, 7.30), (9.45, 9.72)):
            if a <= t <= b:
                flick = 0.15 if int((t - a) * 18) % 2 == 0 else 1.0
        img.alpha_composite(world.streetlight(x=self.lamp_x, base=1560, h=780,
                                              flicker=flick))
        if flick < 0.5:
            d = ImageDraw.Draw(img)
            d.ellipse([self.lamp_x + 96, 762, self.lamp_x + 146, 800],
                      outline=C.CYAN + (220,), width=4)
        # hero blocking
        if t < 7.4:
            x = ease.out_quart(ease.maprange(t, 0.4, 6.6)) * (self.lamp_x + 120 - 980) + 980
            pose = rig.walk_pose(t * 6.2, x=x, y=1580, h=420, head_tilt=4)
        elif t < 8.3:  # skid stop + cautious back step
            u = ease.in_out_quad(ease.maprange(t, 7.4, 8.3))
            pose = rig.walk_pose(t * 6.2, x=self.lamp_x + 150 - 70 * u, y=1580, h=420,
                                 lean=10, eye="squint")
        elif t < 9.4:  # test step forward
            u = ease.in_out_quad(ease.maprange(t, 8.4, 9.4))
            pose = rig.standing(x=self.lamp_x + 80 + 60 * u, y=1580, h=420,
                                lean=7, eye="squint", head_tilt=6)
        else:          # annoyed, then wide detour toward foreground
            u = ease.in_out_quad(ease.maprange(t, 9.7, A_END))
            pose = rig.standing(x=self.lamp_x + 120 + 320 * u, y=1580 + 70 * u,
                                h=420 + 50 * u, head_tilt=14, eye="squint",
                                mouth="flat", arm_l=46, arm_r=-30)
        img.alpha_composite(D.radial((C.W, C.H), (pose["x"], 1590), 380, (120, 150, 200), 60, 1.8))
        g = rig.draw_stickman(img, pose, rng=self.rng, rim_strength=0.5)
        common.hero_tag(img, g["head_c"], g["head_r"], 180)
        return D.vignette(img, 88)

    # ----------------------------------------------------------- B: clocks 11:11
    def _clocks_shot(self, t):
        u = ease.maprange(t, A_END, B_END)
        cut = int(u * 5)  # 0..4
        img = D.vgrad((C.W, C.H), world.SKY_STREET)
        d = ImageDraw.Draw(img)
        if cut == 0:  # shop window wall clock
            d.rounded_rectangle([140, 520, 940, 1300], 18, fill=(12, 16, 32),
                                outline=C.CYAN + (120,), width=4)
            clk = world.clock_face(250)
            img.alpha_composite(clk, (C.W // 2 - clk.width // 2, 640))
        elif cut == 1:  # frozen pedestrian mid-sip, watch on the raised wrist
            cit = rig.citizen("cup", x=540, y=1500, h=560)
            rig.draw_stickman(img, cit, rng=self.rng, rim_strength=0.4)
            # close-up watch inset on the raised wrist
            d.ellipse([628, 980, 772, 1124], fill=(10, 14, 28),
                      outline=C.CYAN + (210,), width=5)
            small = world.clock_face(58)
            img.alpha_composite(small, (642, 994))
        elif cut == 2:  # digital display scramble -> 11:11
            d.rounded_rectangle([120, 620, 960, 1080], 20, fill=(10, 14, 30),
                                outline=(80, 92, 120, 200), width=4)
            scramble = 1.0 - ease.in_out_cubic(ease.maprange(t, A_END + 0.96, A_END + 1.44))
            dc = world.digital_clock("11:11", scramble=max(0, scramble), size=150)
            img.alpha_composite(dc, (C.W // 2 - dc.width // 2, 720))
        elif cut == 3:  # big building clock
            layers = world.city_layers()
            img.alpha_composite(layers[1])
            clk = world.clock_face(300, glow=0.5 + 0.5 * math.sin(t * 8))
            img.alpha_composite(clk, (C.W // 2 - clk.width // 2, 360))
        else:  # hero checks his own watch, then head tilt
            img.alpha_composite(common.street_world())
            d = ImageDraw.Draw(img)
            # raised forearm close-up
            D.line(d, (300, 1500), (560, 1080), C.INK, 46)
            d.rounded_rectangle([520, 980, 800, 1160], 22, fill=(6, 10, 22),
                                outline=C.CYAN + (220,), width=4)
            dc = world.digital_clock("11:11", size=96)
            img.alpha_composite(dc, (540, 1010))
            head_pose = rig.standing(x=240, y=1560, h=420, head_tilt=20, eye="squint",
                                     arm_l=96, elbow_l=60, mouth="flat")
            g = rig.draw_stickman(img, head_pose, rng=self.rng, rim_strength=0.5)
            common.hero_tag(img, g["head_c"], g["head_r"], 160)
        return D.vignette(img, 96)

    # ----------------------------------------------------------- C: impossible doors
    def _corridor_shot(self, t):
        u = ease.in_out_quart(ease.maprange(t, B_END, self.end))
        scale = 1.0 + 0.20 * u
        room = D.layer()
        room.alpha_composite(world.corridor_static("7B"))
        d = ImageDraw.Draw(room)
        # the vanishing door recedes impossibly
        rec = ease.maprange(t, B_END + 1.2, self.end - 0.6)
        d.rectangle([540 - 26, 920 - 60 - 60 * rec, 540 + 26, 920 + 70 - 60 * rec],
                    fill=(6, 7, 14))
        d.rectangle([540 - 30, 920 - 64 - 60 * rec, 540 + 30, 920 + 74 - 60 * rec],
                    outline=C.MAGENTA + (int(140 * rec),), width=2)
        # hero peeks from the left, then retreats
        if t < self.end - 1.6:
            pu = ease.out_cubic(ease.maprange(t, B_END + 0.3, B_END + 1.6))
            px = 60 + 200 * pu
            pose = rig.standing(x=px, y=1620, h=380, lean=10, head_tilt=12, eye="wide")
            rig.draw_stickman(room, pose, rng=self.rng, rim_strength=0.45)
        else:
            ru = ease.in_cubic(ease.maprange(t, self.end - 1.6, self.end))
            pose = rig.standing(x=260 - 320 * ru, y=1620, h=380, lean=-8, head_tilt=-10,
                                eye="wide", mouth="o")
            rig.draw_stickman(room, pose, rng=self.rng, rim_strength=0.45)
        img = ease.place_camera(D.layer(), room, scale, -C.W * (scale - 1) / 2,
                                -C.H * (scale - 1) / 2)
        if t > self.end - 0.35:  # digital error before alley
            img = effects.slice_tear(img, self.rng, count=7, max_shift=54,
                                     band=(6, 36), tint=C.MAGENTA)
        return D.vignette(img, 100)

    def render(self, t, frame):
        if t < A_END:
            return self._streetlight_shot(t)
        if t < B_END:
            return self._clocks_shot(t)
        return self._corridor_shot(t)

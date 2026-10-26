"""Scenes 3-4 — The First Warning + Look Up (cues 8-13, 34.01s - 50.79s)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register

L1 = "STOP LOOKING FOR ME"
L2 = "LOOK UP"
REST_APPEAR = len(L1) / (len(L1) + len(L2))

@register
class Alley(Scene):
    name = "03_alley_messages"
    start = 34.01
    end = 50.79

    def setup(self):
        self.rng = random.Random(303)
        self.kf = [
            (0.00, dict(x=560, y=1760, h=360, lean=6, head_tilt=0, arm_l=20, arm_r=-16,
                        eye="normal")),                                    # entering
            (2.40, dict(x=470, y=1660, h=400, lean=4)),                    # approach wall
            (3.40, dict(x=470, y=1650, h=400, lean=4)),
            (4.70, dict(x=470, y=1650, h=400, lean=10, head_tilt=8,
                        arm_l=86, elbow_l=40)),                            # reach out
            (5.30, dict(arm_l=70, elbow_l=34, eye="wide")),               # stop short
            (6.40, dict(head_tilt=-22, head_dx=-8, arm_l=24, elbow_l=12,
                        eye="squint")),                                    # read left
            (7.40, dict(head_tilt=18, head_dx=8)),                         # read right
            (8.40, dict(head_tilt=-30, head_dx=-10, lean=-6,
                        arm_r=60, elbow_r=26)),                            # over shoulder
            (9.40, dict(head_tilt=0, head_dx=0, lean=8, eye="normal",
                        arm_r=-16, elbow_r=10)),
            (10.60, dict(x=470, y=1660, h=400, lean=-4, arm_l=34, arm_r=-30,
                         mouth="flat")),                                   # passive-aggressive beat
            (12.20, dict(x=470, y=1660, h=400, lean=-6, arm_l=24, arm_r=-22)),
            (12.90, dict(x=470, y=1660, h=400, lean=10, head_tilt=12,
                         eye="wide")),                                     # turns back
            (14.20, dict(head_tilt=12, eye="wide", mouth="o")),
            (15.30, dict(head_tilt=-6, lean=-2)),                          # head begins to rise
            (16.78, dict(head_tilt=-34, head_dx=-6, eye="wide", mouth="o",
                         lean=-8)),                                        # looking up
        ]

    def render(self, t, frame):
        g = t + self.start
        img = D.layer()
        img.alpha_composite(world.alley_static())
        # soft dark plate behind the carved-text zone for phone-readability
        plate = D.layer(); pd = ImageDraw.Draw(plate)
        pd.rounded_rectangle([150, 600, 930, 1000], 26, fill=(6, 7, 16, 150))
        plate = plate.filter(ImageFilter.GaussianBlur(20))
        img.alpha_composite(plate)
        # message carving progress
        c12 = self.cues[12]
        if g < c12["start"]:
            appear = REST_APPEAR
        elif g <= c12["end"]:
            u = ease.in_out_cubic(ease.maprange(g, c12["start"], c12["end"]))
            appear = REST_APPEAR + (1 - REST_APPEAR) * u
        else:
            appear = 1.0
        img.alpha_composite(world.carved_text([L1, L2], appear=appear, y0=700))
        # falling concrete dust while carving
        if c12["start"] <= g <= c12["end"] + 0.8:
            d = ImageDraw.Draw(img)
            for i in range(26):
                seed = (frame * 7 + i * 13) % 900
                dx = (seed * 37 % 640) + 220
                dy = 880 + ((frame * 9 + i * 53) % 220)
                a = 120 - (dy - 880) // 3
                d.ellipse([dx, dy, dx + 4, dy + 3], fill=(150, 146, 160, max(0, a)))
        # camera push during reading, then tilt-up at LOOK UP
        push = ease.out_quart(ease.maprange(t, 0.6, 6.0)) * 0.10
        tilt = ease.in_out_cubic(ease.maprange(g, 48.5, 50.79)) * -470
        scale = 1.0 + push
        img = ease.place_camera(D.layer(), img, scale,
                                -C.W * (scale - 1) / 2,
                                -C.H * (scale - 1) / 2 + tilt)
        # hero (composited after camera so his scale stays readable during tilt)
        pose = ease.pose_at(self.kf, t)
        if g > 48.6:  # drift him toward lower frame edge during tilt
            pose["y"] = pose.get("y", 1660) + ease.maprange(g, 48.6, 50.79) * 260
        rig.draw_stickman(img, pose, rng=self.rng, rim_strength=0.45)
        # one-frame cyan artifact when the final letter lands
        if c12["end"] - 0.08 <= g <= c12["end"] + 0.12:
            img = effects.one_frame_flicker(img, self.rng, prob=1.0)
            dd = ImageDraw.Draw(img)
            dd.rectangle([200, 850, 880, 858], fill=C.CYAN + (160,))
        return D.vignette(img, 104)

"""Scene 6 — The Impossible Staircase (cue 15, 57.43s - 63.50s)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register

STEPS, RUN, RISE, X0, Y0 = 7, 104, 54, 70, 1560

@register
class Staircase(Scene):
    name = "05_impossible_staircase"
    start = 57.43
    end = 63.50

    def setup(self):
        self.rng = random.Random(505)
        self.flight_a, _ = world.stairwell_flight(STEPS, RUN, RISE, X0, Y0)
        # second flight begins on the mid landing (kept short so rotations stay on screen)
        self.b_origin = (520, 1188)
        self.flight_b, _ = world.stairwell_flight(4, 88, 44, self.b_origin[0],
                                                   self.b_origin[1], rail_h=180)
        self.landing = (430, 1140, 1080, 1218)

    def _step_anchor(self, i):
        return (X0 + i * RUN + 34, Y0 - i * RISE)

    def render(self, t, frame):
        img = D.layer()
        img.alpha_composite(world.stairwell_room())
        img.alpha_composite(self.flight_a)
        d = ImageDraw.Draw(img)
        d.rectangle(self.landing, fill=(46, 50, 68, 255),
                    outline=(110, 122, 152, 200), width=3)

        # --- flight B rotations (the reality failure) ---
        rot = 0.0
        if 1.7 <= t < 2.5:      # first impossible shift
            rot = 80 * ease.in_out_cubic(ease.maprange(t, 1.7, 2.5))
        elif 3.5 <= t < 4.3:    # second shift, railing ends up above him
            rot = 80 + 55 * ease.in_out_cubic(ease.maprange(t, 3.5, 4.3))
        elif 4.3 <= t < 4.9:    # snaps back to a stable configuration
            rot = 135 * (1 - ease.in_out_cubic(ease.maprange(t, 4.3, 4.9)))
        if rot > 0.5:
            rotated = self.flight_b.rotate(rot, center=self.b_origin,
                                           resample=Image.BICUBIC)
            img.alpha_composite(rotated)
        else:
            img.alpha_composite(self.flight_b)

        handheld_x = int(math.sin(t * 9.0) * 5)
        handheld_y = int(math.cos(t * 7.3) * 4)

        # --- hero performance ---
        if t < 1.7:  # run up flight A
            u = ease.in_out_quad(ease.maprange(t, 0.15, 1.7))
            i = u * (STEPS - 1)
            i0 = int(i); frac = i - i0
            a = self._step_anchor(i0)
            b = self._step_anchor(min(STEPS - 1, i0 + 1))
            x = a[0] + (b[0] - a[0]) * frac
            y = a[1] + (b[1] - a[1]) * frac - 168
            pose = rig.run_pose(t * 11, x=x, y=y, h=360)
        elif t < 2.6:  # skid stop on the landing, leaning forward
            u = ease.out_back(ease.maprange(t, 1.7, 2.6))
            pose = rig.run_pose(t * 11, x=560 + 40 * u, y=1010, h=360,
                                lean=20, eye="wide", mouth="o")
        elif t < 3.5:  # cautious test steps
            u = ease.in_out_quad(ease.maprange(t, 2.6, 3.5))
            pose = rig.standing(x=560 + 70 * u, y=1010, h=360, lean=9,
                                head_tilt=10, eye="squint",
                                leg_l=24 * u, knee_l=12)
        elif t < 4.6:  # railing above: hanging gag
            u = ease.in_out_cubic(ease.maprange(t, 3.5, 4.0))
            pose = rig.standing(x=610, y=980 + 26 * u, h=360, lean=-14,
                                arm_l=152, arm_r=-152, elbow_l=26, elbow_r=26,
                                leg_l=12, leg_r=-10, knee_l=44, knee_r=40,
                                eye="wide", mouth="o")
        elif t < 5.3:  # pulls himself back, lands on feet
            u = ease.out_back(ease.maprange(t, 4.6, 5.3))
            pose = rig.standing(x=610 - 30 * u, y=1010, h=360, lean=8 * (1 - u),
                                arm_l=120 - 60 * u, arm_r=-120 + 60 * u,
                                eye="squint", mouth="flat")
        else:  # exhausted look straight to camera
            pose = rig.standing(x=580, y=1010, h=360, head_tilt=12,
                                eye="squint", mouth="flat",
                                arm_l=58, elbow_l=32, arm_r=-58, elbow_r=32)
        rig.draw_stickman(img, pose, rng=self.rng, rim_strength=0.55)

        # glitch flash at each rotation
        if 1.65 < t < 1.85 or 3.45 < t < 3.65:
            img = effects.rgb_split(img, (5, 0), (-5, 0))
        img = D.vignette(img, 104)
        if handheld_x or handheld_y:
            frame_img = D.layer()
            frame_img.alpha_composite(img, (handheld_x, handheld_y))
            return frame_img
        return img

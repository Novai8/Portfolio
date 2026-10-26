"""Scene 5 — The Building That Did Not Exist (cue 14, 50.79s - 57.43s)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register
from . import common

@register
class BuildingReveal(Scene):
    name = "04_building_reveal"
    start = 50.79
    end = 57.43

    def setup(self):
        self.rng = random.Random(404)

    def render(self, t, frame):
        g = t + self.start
        img = common.street_world()
        d = ImageDraw.Draw(img)
        # the impossible building materializes: wireframe -> solid
        solid = ease.in_out_cubic(ease.maprange(t, 0.15, 1.7))
        wire = max(0.0, 1.0 - solid * 1.4)
        if wire > 0:
            wf = world.impossible_building(trace=1.0)
            wf.putalpha(int(200 * wire))
            img.alpha_composite(wf)
        if solid > 0:
            bd = world.impossible_building(trace=0.6 + 0.4 * math.sin(t * 3))
            bd.putalpha(int(255 * solid))
            img.alpha_composite(bd)
        # rooftop silhouette: mystery figure standing ON the roof slab
        if t > 1.0:
            u = ease.out_cubic(ease.maprange(t, 1.0, 2.2))
            fig = rig.standing(x=540, y=268, h=int(110 + 50 * u), eye="flat")
            rig.draw_stickman(img, fig, style="mystery", rng=self.rng, alpha=int(255 * u))
        # hero reaction from the street
        if t < 2.6:
            pose = rig.standing(x=540, y=1620, h=420, head_tilt=-26, head_dx=-8,
                                eye="squint", lean=-4)
        elif t < 4.2:  # points up, checks the street, looks again
            pose = rig.standing(x=540, y=1620, h=420, head_tilt=-30, arm_l=128,
                                elbow_l=44, eye="wide", mouth="o")
        else:          # determination sets in
            pose = rig.standing(x=540, y=1620, h=420, head_tilt=-12, lean=5,
                                arm_l=30, arm_r=-26, eye="normal", mouth="flat")
        img.alpha_composite(D.radial((C.W, C.H), (540, 1620), 400, (120, 150, 200), 60, 1.8))
        gg = rig.draw_stickman(img, pose, rng=self.rng, rim_strength=0.5)
        common.hero_tag(img, gg["head_c"], gg["head_r"], 180)
        # low-angle push toward the silhouette
        scale, dx, dy = ease.camera_push(t, self.end, amount=0.09)
        img = ease.place_camera(D.layer(), img, scale, dx, dy - 30)
        # intermittent cyan trace flicker along the building edge
        if int(t * 6) % 5 == 0:
            dd = ImageDraw.Draw(img)
            dd.line([(358, 300), (346, 1180)], fill=C.CYAN + (130,), width=3)
        return D.vignette(img, 100)

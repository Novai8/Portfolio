"""Scene 1 — The Search Begins (cues 0-3, 0.0s - 16.36s)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register
from . import common

@register
class StreetSearch(Scene):
    name = "01_search_begins"
    start = 0.0
    end = 16.36

    def setup(self):
        self.rng = random.Random(101)
        # hero performance keyframes (local time = global here)
        self.kf = [
            (0.00, dict(head_tilt=0, lean=0, arm_l=14, arm_r=-14, elbow_l=8, elbow_r=8,
                        eye="normal", mouth=None)),
            (0.80, dict(head_tilt=0, lean=0, arm_l=14, arm_r=-14, elbow_l=8, elbow_r=8)),
            (2.00, dict(head_tilt=-26, head_dx=-10, lean=-4, eye="squint")),
            (3.10, dict(head_tilt=26, head_dx=10, lean=4)),
            (4.10, dict(head_tilt=14, head_dx=6, lean=8, arm_r=30, elbow_r=24)),
            (4.55, dict(head_tilt=14, arm_l=108, elbow_l=78, arm_r=-10, mouth="flat")),  # scratch
            (5.30, dict(head_tilt=0, head_dx=0, lean=2, arm_l=20, elbow_l=16,
                        arm_r=-16, elbow_r=10, mouth=None)),
            (6.40, dict(head_tilt=-18, head_dx=-7, eye="squint")),
            (8.20, dict(head_tilt=16, head_dx=7)),
            (10.30, dict(head_tilt=0, head_dx=0, lean=-3, eye="normal")),
            (11.60, dict(lean=-6, arm_l=40, arm_r=-42, elbow_l=18, elbow_r=18)),
            (12.70, dict(lean=0, arm_l=14, arm_r=-14, elbow_l=8, elbow_r=8)),
            (13.40, dict(head_tilt=-12, arm_l=64, arm_r=-64, elbow_l=30, elbow_r=30,
                         mouth="flat")),  # uncertain shrug
            (14.40, dict(head_tilt=8, arm_l=30, arm_r=-24, elbow_l=14, elbow_r=12)),
            (16.36, dict(head_tilt=0, lean=3, arm_l=20, arm_r=-18)),
        ]

    def render(self, t, frame):
        # camera: slow push-in + small gaze pan
        scale, dx, dy = ease.camera_push(t, self.end, amount=0.06)
        gaze = math.sin(t * 0.9) * 10
        world_img = common.street_world(parallax=(gaze * 0.25, gaze * 0.5, gaze))
        world_img.alpha_composite(common.backward_cloud(t))
        world_img.alpha_composite(common.traffic_light(phase=t))
        world_img.alpha_composite(common.sign_glyphs(t))
        # window arrangement flicker on the near block
        if (5.9 < t < 6.15) or (9.6 < t < 9.8):
            fd = ImageDraw.Draw(world_img)
            fd.rectangle([760, 1180, 830, 1240], fill=C.MAGENTA + (180,))
            fd.rectangle([760, 1180, 830, 1240], outline=C.CYAN + (220,), width=3)
        # ground light pool + hero
        world_img.alpha_composite(D.radial((C.W, C.H), (540, 1580), 430, (120, 150, 200), 66, 1.8))
        pose = ease.pose_at(self.kf, t)
        pose.update(x=540, y=1580, h=430)
        g = rig.draw_stickman(world_img, pose, rng=self.rng, rim_strength=0.5)
        common.hero_tag(world_img, g["head_c"], g["head_r"], alpha=190)
        world_img = D.vignette(world_img, 92)
        world_img = ease.place_camera(D.layer(), world_img, scale, dx, dy)
        # closing horizontal digital tear into the montage
        if t > 15.95:
            u = ease.maprange(t, 15.95, 16.36)
            world_img = effects.slice_tear(world_img, self.rng, count=int(4 + u * 8),
                                           max_shift=int(20 + u * 60), band=(6, 40))
        return world_img

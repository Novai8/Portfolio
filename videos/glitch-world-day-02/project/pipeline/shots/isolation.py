"""Scene 18 — The City Is Still Watching (cue 34, 109.80s - 118.35s)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register

@register
class Isolation(Scene):
    name = "07_isolation"
    start = 109.80
    end = 118.35

    def setup(self):
        self.rng = random.Random(707)
        self.fracture = effects.SkyFracture(seed=17)
        self.base = D.layer()
        self.base.alpha_composite(D.vgrad((C.W, C.H), world.SKY_ROOF))
        self.base.alpha_composite(world.rooftop_static())
        fl = D.layer()
        self.fracture.draw(fl, 0.85, offset_px=2)
        self.base.alpha_composite(fl)

    def render(self, t, frame):
        # slow pull-back: the hero shrinks against the city
        scale = 1.06 - 0.16 * ease.in_out_quad(ease.maprange(t, 0, self.end - self.start))
        stage = self.base.copy()
        # key-turning micro animation
        turn = math.sin(t * 2.2) * 12
        pose = rig.standing(x=540, y=1580, h=430, head_tilt=6 * math.sin(t * 1.3),
                            eye="squint", mouth="flat",
                            arm_l=76 + turn * 0.3, elbow_l=42, arm_r=-24)
        g = rig.draw_stickman(stage, pose, rng=self.rng, rim_strength=0.55)
        key = world.key_prop(glint=0.35 + 0.3 * math.sin(t * 3), scale=0.8,
                             angle=turn * 0.4)
        stage.alpha_composite(key, (int(g["hand_l"][0] - key.width / 2),
                                    int(g["hand_l"][1] - key.height / 2)))
        # watching citizens far below the parapet: tiny heads oriented upward
        d = ImageDraw.Draw(stage)
        for i, x in enumerate(range(120, 1000, 130)):
            d.ellipse([x, 1010 + (i % 2) * 8, x + 22, 1032 + (i % 2) * 8],
                      fill=(8, 9, 16, 255), outline=C.CYAN + (90,), width=2)
        # uncertain gesture near the end
        if t > 6.4:
            u = ease.in_out_quad(ease.maprange(t, 6.4, 7.6))
            d2 = ImageDraw.Draw(stage)
            hx, hy = g["hand_r"]
            D.line(d2, (hx, hy), (hx + 40 * u, hy - 70 * u), C.INK + (255,), 11)
        out = ease.place_camera(D.layer(), stage, scale,
                                -C.W * (scale - 1) / 2, -C.H * (scale - 1) / 2)
        return D.vignette(out, 108)

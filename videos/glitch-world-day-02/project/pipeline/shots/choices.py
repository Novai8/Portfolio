"""Scene 19 — The Next Decision (cues 35-38, 118.35s - 130.04s)."""
import math, random
from PIL import Image, ImageDraw
from engine import config as C
from engine import draw as D
from engine import world, rig, ease, effects
from engine.scene import Scene, register
from .common import street_world, hero_tag

@register
class Choices(Scene):
    name = "08_choices"
    start = 118.35
    end = 130.04

    subtitle_y = 1296  # keep cue 35/38 captions above the choice cards

    def setup(self):
        self.rng = random.Random(808)
        self.fracture = effects.SkyFracture(seed=17)
        self.base = D.layer()
        self.base.alpha_composite(D.vgrad((C.W, C.H), world.SKY_ROOF))
        # impossible building rises behind
        bd = world.impossible_building(trace=0.5)
        bd.putalpha(150)
        self.base.alpha_composite(bd, (0, -180))
        fl = D.layer()
        self.fracture.draw(fl, 0.9, offset_px=2)
        self.base.alpha_composite(fl)
        self.base.alpha_composite(world.rooftop_static())
        self.card_a = world.choice_card("A", "SEARCH FOR THE ROOM WITH NO DOOR",
                                        "door", C.CYAN)
        self.card_b = world.choice_card("B", "FIND OUT WHY EVERYONE IS WATCHING ME",
                                        "eye", C.MAGENTA)

    def render(self, t, frame):
        g = t + self.start
        c36, c37, c38 = self.cues[36], self.cues[37], self.cues[38]
        stage = self.base.copy()
        # watching silhouettes
        d = ImageDraw.Draw(stage)
        for i, x in enumerate(range(110, 1000, 120)):
            d.ellipse([x, 1008 + (i % 2) * 8, x + 24, 1032 + (i % 2) * 8],
                      fill=(8, 9, 16, 255), outline=C.CYAN + (80,), width=2)
        # hero holding the key, glances toward each card
        look_a = c36["start"] <= g <= c36["end"]
        look_b = c37["start"] <= g <= c37["end"]
        pose = rig.standing(x=540, y=1330, h=360,
                            head_tilt=-10 if look_a else (12 if look_b else 4),
                            eye="squint", mouth="flat",
                            arm_l=70, elbow_l=38, arm_r=-26)
        gg = rig.draw_stickman(stage, pose, rng=self.rng, rim_strength=0.55)
        hero_tag(stage, gg["head_c"], gg["head_r"], 170)
        key = world.key_prop(glint=0.4, scale=0.75)
        stage.alpha_composite(key, (int(gg["hand_l"][0] - key.width / 2),
                                    int(gg["hand_l"][1] - key.height / 2)))

        # choice cards slide/pulse in, inside safe margins (h=200)
        ay, by = 1430, 1670
        ua = ease.out_back(ease.maprange(g, c36["start"] - 0.25, c36["start"] + 0.45))
        ub = ease.out_back(ease.maprange(g, c37["start"] - 0.25, c37["start"] + 0.45))
        if ua > 0:
            pulse = 0.5 + 0.5 * math.sin(t * 5)
            stage.alpha_composite(world.choice_card(
                "A", "SEARCH FOR THE ROOM WITH NO DOOR", "door", C.CYAN, pulse,
                w=860, h=200), (110, int(ay + (1 - ua) * 80)))
        if ub > 0:
            pulse = 0.5 + 0.5 * math.sin(t * 5 + 1.6)
            stage.alpha_composite(world.choice_card(
                "B", "FIND OUT WHY EVERYONE IS WATCHING ME", "eye", C.MAGENTA, pulse,
                w=860, h=200), (110, int(by + (1 - ub) * 80)))

        # final restrained glitch that SETTLES: no fade-to-black, hold the cards
        if c38["end"] - 0.40 < g < c38["end"] - 0.10:
            stage = effects.slice_tear(stage, self.rng, count=5, max_shift=34, band=(6, 30))
        if c38["end"] - 0.22 < g < c38["end"] - 0.06:
            stage = effects.rgb_split(stage, (5, 0), (-5, 0))
        # from c38 end onward: clean, stable, fully visible end frame (no black)
        return D.vignette(stage, 100)

    def _fade_card(self, card, u):
        out = card.copy()
        out.putalpha(out.getchannel("A").point(lambda a: int(a * min(1, u * 1.4))))
        return out

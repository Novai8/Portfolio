"""Scene base class and the render registry."""
from PIL import Image
from . import config as C
from . import draw as D

class Scene:
    name = "scene"
    start = 0.0
    end = 1.0

    def __init__(self, timing):
        self.timing = timing
        self.cues = timing["sentences"]
        self.setup()

    def setup(self):
        """Pre-render static layers once."""

    def cue(self, i):
        return self.cues[i]

    def cue_t(self, i, t):
        """Local-time progress (0..1) inside cue i, else -1/1 clamped."""
        c = self.cues[i]
        if t < c["start"] - self.start:
            return -1.0
        if t > c["end"] - self.start:
            return 1.0
        span = max(0.01, c["end"] - c["start"])
        return (t - (c["start"] - self.start)) / span

    def base(self):
        return D.layer()

    def render(self, t, frame):
        """t = seconds since scene start. Return RGBA image."""
        raise NotImplementedError

REGISTRY = []

def register(cls):
    REGISTRY.append(cls)
    return cls

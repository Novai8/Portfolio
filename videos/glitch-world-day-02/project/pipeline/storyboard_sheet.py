#!/usr/bin/env python3
"""Build the canonical one-page storyboard contact sheet (two key frames per scene)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
from render import Renderer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# (time s, scene label, beat label)
SHOTS = [
    (8.0,   "1 Search Begins",  "hunting the vanished figure"),
    (14.5,  "1 Search Begins",  "magenta after-image tears away"),
    (20.0,  "2 Montage",        "six-hour glitch search"),
    (27.4,  "2 Montage",        "every clock reads 11:11"),
    (37.6,  "3 First Warning",  "STOP LOOKING FOR ME carved"),
    (47.3,  "3 First Warning",  "LOOK UP"),
    (53.2,  "4 Impossible Bldg","figure on the roofline"),
    (60.6,  "5 Staircase",      "stairs change direction"),
    (70.0,  "6 Rooftop",        "I'm the reason you're alive"),
    (83.6,  "6 Rooftop",        "his wrist reads 00:00:00"),
    (90.5,  "6 Rooftop",        "sky fractures above the roof"),
    (97.6,  "6 Rooftop",        "the whole city turns at once"),
    (103.6, "6 Rooftop",        "the key to the room with no door"),
    (109.3, "6 Rooftop",        "he disappears"),
    (114.0, "7 Isolation",      "a key that opens nothing"),
    (123.8, "8 The Choice",     "A / B branching end cards"),
]

def main():
    r = Renderer()
    tw, th, pad = 270, 480, 34
    cols = 4
    rows = (len(SHOTS) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows * (th + pad)), (8, 10, 20))
    dd = ImageDraw.Draw(sheet)
    for i, (t, scene, beat) in enumerate(SHOTS):
        img = r.frame(t, int(t * 30))
        img.thumbnail((tw, th), Image.LANCZOS)
        x, y = (i % cols) * tw, (i // cols) * (th + pad)
        sheet.paste(img, (x, y))
        dd.text((x + 8, y + th + 3), f"{t:6.2f}s  {scene}", fill=(150, 235, 240))
        dd.text((x + 8, y + th + 18), beat, fill=(170, 178, 200))
    out = os.path.join(ROOT, "preview", "storyboard-contact-sheet.png")
    sheet.save(out)
    print("saved", out, sheet.size)

if __name__ == "__main__":
    main()

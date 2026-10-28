#!/usr/bin/env python3
# Writes the RGB test pattern (1920x1080) the BT.709 clip is made from.
#
# Top half: 10 flat bars: saturated colours, a grey, black and white. A wrong YUV->RGB matrix shows
# clearly in the colours and chroma subsampling does not matter in the bar interiors. Black and
# white (0 and 255) are the ends of the range: in limited range video they are Y=16 and Y=235, so
# they check that the luma is mapped to the whole RGB range (and clamped there). Bottom half: ramps.
#
# Usage: make_pattern.py OUTPUT.png      (needs numpy and Pillow)
import sys

import numpy as np
from PIL import Image

W, H = 1920, 1080

BARS = [
    ("red", (255, 0, 0)),
    ("green", (0, 255, 0)),
    ("blue", (0, 0, 255)),
    ("yellow", (255, 255, 0)),
    ("cyan", (0, 255, 255)),
    ("magenta", (255, 0, 255)),
    ("orange", (255, 128, 0)),
    ("grey", (128, 128, 128)),
    ("black", (0, 0, 0)),
    ("white", (255, 255, 255)),
]

rgb = np.zeros((H, W, 3), np.uint8)
bar_w = W // len(BARS)
for i, (_, color) in enumerate(BARS):
    rgb[:H // 2, i * bar_w:(i + 1) * bar_w] = color
ramp = np.linspace(0, 255, W, dtype=np.uint8)
rgb[H // 2:3 * H // 4, :, 0] = ramp  # red ramp
rgb[3 * H // 4:, :, 1] = ramp        # green ramp
rgb[H // 2:, :, 2] = 90              # constant blue under both ramps

Image.fromarray(rgb, "RGB").save(sys.argv[1], optimize=True)

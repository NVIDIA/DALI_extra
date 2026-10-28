#!/usr/bin/env python3
# Wraps a raw rgb24 frame written by ffmpeg (-f rawvideo -pix_fmt rgb24) into a (H, W, 3) uint8 .npy.
#
# Usage: raw_to_npy.py INPUT.rgb OUTPUT.npy WIDTH HEIGHT
import sys

import numpy as np

src, dst, w, h = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
np.save(dst, np.fromfile(src, np.uint8).reshape(h, w, 3))

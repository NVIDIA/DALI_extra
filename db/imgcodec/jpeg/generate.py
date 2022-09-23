#!/bin/python3

# Copyright (c) 2019-2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from PIL import Image
import numpy as np

def save_reference(filename, angle, flip_x, flip_y):
	img = Image.open(filename + '.jpg').rotate(angle, expand=True)
	if flip_x:
		img = img.transpose(Image.FLIP_LEFT_RIGHT)
	if flip_y:
		img = img.transpose(Image.FLIP_TOP_BOTTOM)
	np.save(filename, np.asarray(img))

save_reference('orientation/padlock-406986_640_horizontal', 0, False, False)
save_reference('orientation/padlock-406986_640_mirror_horizontal_rotate_270', 90, True, False)
save_reference('orientation/padlock-406986_640_mirror_vertical', 0, False, True)
save_reference('orientation/padlock-406986_640_no_orientation', 0, False, False)
save_reference('orientation/padlock-406986_640_rotate_270', 90, False, False)
save_reference('orientation/padlock-406986_640_mirror_horizontal', 0, True, False)
save_reference('orientation/padlock-406986_640_mirror_horizontal_rotate_90', 270, True, False)
save_reference('orientation/padlock-406986_640_no_exif', 0, False, False)
save_reference('orientation/padlock-406986_640_rotate_180', 180, False, False)
save_reference('orientation/padlock-406986_640_rotate_90', 270, False, False)

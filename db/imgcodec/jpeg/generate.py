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

def save_reference(filename):
	img = Image.open(filename + '.jpg')
	np.save(filename, np.asarray(img))

save_reference('orientation/padlock-406986_640_horizontal')
save_reference('orientation/padlock-406986_640_mirror_horizontal_rotate_270')
save_reference('orientation/padlock-406986_640_mirror_vertical')
save_reference('orientation/padlock-406986_640_no_orientation')
save_reference('orientation/padlock-406986_640_rotate_270')
save_reference('orientation/padlock-406986_640_mirror_horizontal')
save_reference('orientation/padlock-406986_640_mirror_horizontal_rotate_90')
save_reference('orientation/padlock-406986_640_no_exif')
save_reference('orientation/padlock-406986_640_rotate_180')
save_reference('orientation/padlock-406986_640_rotate_90')

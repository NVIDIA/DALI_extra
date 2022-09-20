#!/bin/python3

# Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

img = Image.open('../../jpeg/134/site-1534685_1280.jpg')
np.save('site-1534685_1280', np.asarray(img))

cropped = img.crop((20, 5, 1000, 800))
np.save('site-1534685_1280_roi', np.asarray(cropped))

# https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion
def rgb_to_ycbcr(rgb):
    ycbcr_weights = np.asarray([[ 0.257,  0.504,  0.098],
                                [-0.148, -0.291,  0.439],
                                [ 0.439, -0.368, -0.071]]).T
    ycbcr = np.matmul(rgb, ycbcr_weights) + np.asarray([0.0625, 0.5, 0.5])
    return ycbcr

def to_uint8(float_image):
    return np.round((float_image * 255) + 1).astype('uint8')

def get_ycbcr(image):
    rgb = np.asarray(img).astype('float32') / 255
    ycbcr = rgb_to_ycbcr(rgb)
    return to_uint8(ycbcr)

np.save('site-1534685_1280_ycbcr', get_ycbcr(img))

# Few more images
np.save('swan-3584559_640', np.asarray(Image.open('../../jpeg/100/swan-3584559_640.jpg')))
np.save('snail-4291306_1280', np.asarray(Image.open('../../jpeg/113/snail-4291306_1280.jpg')))

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
import cv2

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
    rgb = np.asarray(image).astype('float32') / 255
    ycbcr = rgb_to_ycbcr(rgb)
    return to_uint8(ycbcr)

def hwc_to_chw(image):
    return np.transpose(image, (2, 0, 1))

def save(path, arr):
    np.save(path, arr)
    np.save(path + "_chw", hwc_to_chw(arr))

img0_path = '../../jpeg/134/site-1534685_1280.jpg'
img0 = Image.open(img0_path)
img0_gray = cv2.imread(img0_path, cv2.IMREAD_GRAYSCALE)
cropped = img0.crop((20, 5, 1000, 800))
save('site-1534685_1280', np.asarray(img0))
save('site-1534685_1280_gray', np.expand_dims(img0_gray, -1))
save('site-1534685_1280_roi', np.asarray(cropped))
save('site-1534685_1280_ycbcr', get_ycbcr(img0))

# Few more images
img1_path = '../../jpeg/100/swan-3584559_640.jpg'
img1 = Image.open(img1_path)
img1_gray = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
save('swan-3584559_640', np.asarray(img1))
save('swan-3584559_640_gray', np.expand_dims(img1_gray, -1))
save('swan-3584559_640_ycbcr', get_ycbcr(img1))

img2_path = '../../jpeg/113/snail-4291306_1280.jpg'
img2 = Image.open(img2_path)
img2_gray = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
save('snail-4291306_1280', np.asarray(img2))
save('snail-4291306_1280_gray', np.expand_dims(img2_gray, -1))
save('snail-4291306_1280_ycbcr', get_ycbcr(img2))

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

def hwc_to_chw(image):
    return np.transpose(image, (2, 0, 1))

def save(path, arr):
    np.save(path, arr)
    np.save(path + "_chw", hwc_to_chw(arr))

def gen_reference(name):
    img = Image.open('../../jpeg2k/' + name + '.jp2')
    save(name, np.asarray(img))

def gen_reference_roi(name, roi):
    img = Image.open('../../jpeg2k/' + name + '.jp2')
    img = img.crop(roi)
    save(name + '_roi', np.asarray(img))

def gen_reference_ycbcr(name):
    img = Image.open('../../jpeg2k/' + name + '.jp2')
    rgb = np.asarray(img).astype('float32') / 255
    ycbcr = rgb_to_ycbcr(rgb)
    save(name + '_ycbcr', to_uint8(ycbcr))

def gen_reference_gray(name):
    img_gray = cv2.imread('../../jpeg2k/' + name + '.jp2', cv2.IMREAD_GRAYSCALE)
    gray = np.expand_dims(img_gray, -1)
    save(name + '_gray', gray)

gen_reference('0/cat-1245673_640')
gen_reference_roi('0/cat-1245673_640', (33, 17, 489, 276))
gen_reference_ycbcr('0/cat-1245673_640')
gen_reference_gray('0/cat-1245673_640')
gen_reference('0/cat-2184682_640')
gen_reference_ycbcr('0/cat-2184682_640')
gen_reference_gray('0/cat-2184682_640')
gen_reference('0/cat-300572_640')
gen_reference_ycbcr('0/cat-300572_640')
gen_reference_gray('0/cat-300572_640')
gen_reference('0/cat-3113513_640')
gen_reference_ycbcr('0/cat-3113513_640')
gen_reference_gray('0/cat-3113513_640')
gen_reference_roi('2/tiled-cat-1046544_640', (220, 178, 290, 456))
gen_reference_roi('2/tiled-cat-111793_640', (317, 9, 325, 58))
gen_reference_roi('2/tiled-cat-3113513_640', (1, 2, 600, 200))

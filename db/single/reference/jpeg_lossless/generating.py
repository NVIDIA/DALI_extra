#!/bin/python3

# Copyright (c) 2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import os
import numpy as np
import cv2

def convert_to_jpeg_lossless(output_path, image_path, precision=16, psv=1):
    # cjpeg from libjpeg-turbo (use dev branch until Lossless is supported (release 2.2?)
    os.system(f'cjpeg -grayscale -precision {precision} -lossless {psv} {image_path} > {output_path}')


def generate_reference_grayscale(ref_path, img_path, precision=16, dtype=np.uint16):
    gray = np.asarray(cv2.imread(img_path, cv2.IMREAD_GRAYSCALE))
    gray = np.expand_dims(gray, axis=-1)
    gray = (gray.astype(np.float64) * (2**precision - 1) / 255.0).astype(dtype)
    print(f"Saving {ref_path} : {gray.shape}")
    np.save(ref_path, gray)

def generate_jpegs():
    convert_to_jpeg_lossless('../../jpeg_lossless/0/cat-1245673_640_grayscale_16bit.jpg',
                             '../../pnm/0/cat-1245673_640.pgm',
                             precision=16)
    convert_to_jpeg_lossless('../../jpeg_lossless/0/cat-3449999_640_grayscale_16bit.jpg',
                             '../../pnm/0/cat-3449999_640.pgm',
                             precision=16)
    convert_to_jpeg_lossless('../../jpeg_lossless/0/cat-3449999_640_grayscale_12bit.jpg',
                             '../../pnm/0/cat-3449999_640.pgm',
                             precision=12)
    convert_to_jpeg_lossless('../../jpeg_lossless/0/cat-3449999_640_grayscale_8bit.jpg',
                             '../../pnm/0/cat-3449999_640.pgm',
                             precision=8)

def generate_reference():
    generate_reference_grayscale('cat-1245673_640_grayscale_16bit', '../../pnm/0/cat-1245673_640.pgm',
                                 precision=16, dtype=np.uint16)
    generate_reference_grayscale('cat-3449999_640_grayscale_16bit', '../../pnm/0/cat-3449999_640.pgm',
                                 precision=16, dtype=np.uint16)
    generate_reference_grayscale('cat-3449999_640_grayscale_12bit', '../../pnm/0/cat-3449999_640.pgm',
                                 precision=12, dtype=np.uint16)
    generate_reference_grayscale('cat-3449999_640_grayscale_8bit', '../../pnm/0/cat-3449999_640.pgm',
                                 precision=8, dtype=np.uint8)


generate_jpegs()
generate_reference()

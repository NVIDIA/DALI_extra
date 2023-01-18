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
import tempfile

def tool(tool_name):
    # JPEG_TOOL_PREFIX=''
    # cjpeg from libjpeg-turbo (use dev branch until Lossless is supported (release 2.2?)
    JPEG_TOOL_PREFIX='LD_LIBRARY_PATH=~/git/lossless_libjpeg-turbo/install/lib ~/git/lossless_libjpeg-turbo/install/bin/'
    return f'{JPEG_TOOL_PREFIX}{tool_name}'

def convert_to_jpeg_lossless(output_path, image_path, precision=16, psv=1):
    cjpeg = tool('cjpeg')
    os.system(f'{cjpeg} -grayscale -precision {precision} -lossless {psv} {image_path} > {output_path}')

def convert_jpeg_lossless_to_pnm(output_path, image_path):
    djpeg = tool('djpeg')
    os.system(f'{djpeg} -pnm {image_path} > {output_path}')

def generate_reference_grayscale(ref_path, img_path, precision=16, dtype=np.uint16):
    with tempfile.NamedTemporaryFile() as tmp:
        convert_jpeg_lossless_to_pnm(tmp.name, img_path)
        gray = np.asarray(cv2.imread(tmp.name, cv2.IMREAD_GRAYSCALE | cv2.IMREAD_ANYDEPTH))
        gray = np.expand_dims(gray, axis=-1)
        print(f"Saving {ref_path} : {gray.shape}")
        np.save(ref_path, gray)

def generate_sample(img_source, jpeg_target, npy_target, precision=16, dtype=np.uint16):
    convert_to_jpeg_lossless(jpeg_target, img_source, precision=precision)
    generate_reference_grayscale(npy_target, jpeg_target, precision=precision, dtype=dtype)

def generate():
    generate_sample(
        img_source='../../pnm/0/cat-1245673_640.pgm',
        jpeg_target='../../jpeg_lossless/0/cat-1245673_640_grayscale_16bit.jpg',
        npy_target='cat-1245673_640_grayscale_16bit',
        precision=16, dtype=np.uint16)

    for (precision, dtype) in [(16, np.uint16), (12, np.uint16), (8, np.uint8)]:
        generate_sample(
            img_source='../../pnm/0/cat-3449999_640.pgm',
            jpeg_target=f'../../jpeg_lossless/0/cat-3449999_640_grayscale_{precision}bit.jpg',
            npy_target=f'cat-3449999_640_grayscale_{precision}bit',
            precision=precision, dtype=dtype)

generate()

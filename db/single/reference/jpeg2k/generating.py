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

def gen_reference(name):
	img = Image.open('../../jpeg2k/0/' + name + '.jp2')
	np.save(name, np.asarray(img))

gen_reference('cat-1245673_640')
gen_reference('cat-2184682_640')
gen_reference('cat-300572_640')
gen_reference('cat-3113513_640')


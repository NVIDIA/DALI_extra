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

img = img.crop((20, 5, 1000, 800))
np.save('site-1534685_1280_roi', np.asarray(img))


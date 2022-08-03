#!/bin/python3

from PIL import Image
import numpy as np

img = Image.open('../../jpeg/134/site-1534685_1280.jpg')
np.save('site-1534685_1280', np.asarray(img))

img = img.crop((20, 5, 1000, 800))
np.save('site-1534685_1280_roi', np.asarray(img))


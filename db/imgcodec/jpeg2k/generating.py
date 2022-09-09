#!/bin/python3

from os import system
from PIL import Image
import numpy as np
import cv2

# Bitdepth conversion is done via ImageMagick
def convert_bitdepth(name, bitdepth):
	input = '../../single/jpeg2k/' + name
	output = name + f'-{bitdepth}bit'
	system(f'convert {input}.jp2 -depth {bitdepth} {output}.jp2')
	return output

def gen_reference(name):
	np.save(name, cv2.imread(name + '.jp2', mode='RGB'))

gen_reference(convert_bitdepth('0/cat-1245673_640', 5))
gen_reference(convert_bitdepth('0/cat-1245673_640', 12))

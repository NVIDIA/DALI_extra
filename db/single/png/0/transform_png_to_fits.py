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

from PIL import Image
import os
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from astropy.io import fits
from astropy.visualization import astropy_mpl_style


if not os.path.exists('fits'):
    os.makedirs('fits')

if not os.path.exists('jpeg'):
    os.makedirs('jpeg')

current_directory = os.getcwd()

target_jpeg_directory = os.path.join(current_directory,'jpeg')
target_fits_directory = os.path.join(current_directory,'fits')

# iterating over all files
for files in os.listdir(current_directory):
    if files.endswith('.png'):
        im1 = Image.open('./' + files)
        files = files.replace(".png", ".jpeg")
        print(files)
        dirPath2 = os.path.join(target_jpeg_directory,files)
        print(dirPath2)
        im1.save(dirPath2)
    else:
        continue


"""
=====================================================
Convert a 3-color image (JPG) to separate FITS images
=====================================================

This example opens an RGB JPEG image and writes out each channel as a separate
FITS (image) file.

This example uses `pillow <https://python-pillow.org>`_ to read the image,
`matplotlib.pyplot` to display the image, and `astropy.io.fits` to save FITS files.


*By: Erik Bray, Adrian Price-Whelan*

*License: BSD*


"""

##############################################################################
# Set up matplotlib and use a nicer set of plot parameters

plt.style.use(astropy_mpl_style)

##############################################################################
# Load and display the original 3-color jpeg image:
for files in os.listdir(target_jpeg_directory):
    if files.endswith('.jpeg'):
        image = Image.open('./jpeg/' + files)
        xsize, ysize = image.size
        print(f"Image size: {ysize} x {xsize}")
        print(f"Image bands: {image.getbands()}")
        ax = plt.imshow(image)

        ##############################################################################
        # Split the three channels (RGB) and get the data as Numpy arrays. The arrays
        # are flattened, so they are 1-dimensional:

        r, g, b = image.split()
        r_data = np.array(r.getdata()) # data is now an array of length ysize*xsize
        g_data = np.array(g.getdata())
        b_data = np.array(b.getdata())
        print(r_data.shape)

        ##############################################################################
        # Reshape the image arrays to be 2-dimensional:

        r_data = r_data.reshape(ysize, xsize) # data is now a matrix (ysize, xsize)
        g_data = g_data.reshape(ysize, xsize)
        b_data = b_data.reshape(ysize, xsize)
        print(r_data.shape)

        ##############################################################################
        # Write out the channels as separate FITS images.
        # Add and visualize header info
        files = files.replace(".jpeg", "")

        red = fits.PrimaryHDU(data=r_data)
        red.header['LATOBS'] = "32:11:56" # add spurious header info
        red.header['LONGOBS'] = "110:56"
        red.writeto('./fits/'+files+'_red.fits')

        green = fits.PrimaryHDU(data=g_data)
        green.header['LATOBS'] = "32:11:56"
        green.header['LONGOBS'] = "110:56"
        green.writeto('./fits/'+files+'_green.fits')

        blue = fits.PrimaryHDU(data=b_data)
        blue.header['LATOBS'] = "32:11:56"
        blue.header['LONGOBS'] = "110:56"
        blue.writeto('./fits/'+files+'_blue.fits')

        from pprint import pprint

        pprint(red.header)
    else:
        continue    
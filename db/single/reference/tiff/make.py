import os
import tifffile
import matplotlib.pyplot as plt
import numpy as np
import cv2

# https://en.wikipedia.org/wiki/YCbCr#ITU-R_BT.601_conversion
def rgb_to_ycbcr(rgb):
    ycbcr_weights = np.asarray([[ 0.257,  0.504,  0.098],
                                [-0.148, -0.291,  0.439],
                                [ 0.439, -0.368, -0.071]]).T
    ycbcr = np.matmul(rgb, ycbcr_weights) + np.asarray([0.0625, 0.5, 0.5])
    return ycbcr

def rgb_to_gray(rgb):
    gray_weights = np.asarray([0.299, 0.587, 0.114])
    gray = np.dot(rgb, gray_weights)
    return np.expand_dims(gray, axis=-1)

def to_uint8(float_image):
    return np.round((float_image * 255) + 1).astype('uint8')

def get_ycbcr(image):
    rgb = np.asarray(image).astype('float32') / 255
    ycbcr = rgb_to_ycbcr(rgb)
    return to_uint8(ycbcr)

def read_rgb(path):
    return plt.imread(path).astype('uint8')

def read_gray(path):
    arr = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    return np.expand_dims(arr, -1)

dali_extra_path = os.environ['DALI_EXTRA_PATH']
tiff_path = os.path.join(dali_extra_path, 'db/single/tiff')
tiff_ref_path = os.path.join(dali_extra_path, 'db/single/reference/tiff')

path0 = os.path.join(tiff_path, '0/cat-111793_640.tiff')
img0 = read_rgb(path0).astype('uint8')
np.save(os.path.join(tiff_ref_path, '0/cat-111793_640.tiff.npy'), img0)

gray0 = read_gray(path0)
tifffile.imwrite(os.path.join(tiff_path, '0/cat-111793_640_gray.tiff'), gray0)
np.save(os.path.join(tiff_ref_path, '0/cat-111793_640_gray.tiff.npy'), gray0)
ycbcr0 = get_ycbcr(img0)
np.save(os.path.join(tiff_ref_path, '0/cat-111793_640_ycbcr.tiff.npy'), ycbcr0)

path1 = os.path.join(tiff_path, '0/cat-3449999_640.tiff')
img1 = read_rgb(path1).astype('uint8')
np.save(os.path.join(tiff_ref_path, '0/cat-3449999_640.tiff.npy'), img1)
gray1 = read_gray(path1)
tifffile.imwrite(os.path.join(tiff_path, '0/cat-3449999_640_gray.tiff'), gray1)
np.save(os.path.join(tiff_ref_path, '0/cat-3449999_640_gray.tiff.npy'), gray1)
ycbcr1 = get_ycbcr(img1)
np.save(os.path.join(tiff_ref_path, '0/cat-3449999_640_ycbcr.tiff.npy'), ycbcr1)

path2 = os.path.join(tiff_path, '0/cat-3504008_640.tiff')
img2 = plt.imread(path2).astype('uint8')
np.save(os.path.join(tiff_ref_path, '0/cat-3504008_640.tiff.npy'), img2)
gray2 = read_gray(path2)
tifffile.imwrite(os.path.join(tiff_path, '0/cat-3504008_640_gray.tiff'), gray2)
np.save(os.path.join(tiff_ref_path, '0/cat-3504008_640_gray.tiff.npy'), gray2)
ycbcr2 = get_ycbcr(img2)
np.save(os.path.join(tiff_ref_path, '0/cat-3504008_640_ycbcr.tiff.npy'), ycbcr2)

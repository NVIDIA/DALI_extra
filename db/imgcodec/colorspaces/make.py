import os
import numpy as np
from matplotlib import pyplot as plt


def to_uint8(float_image):
    return np.round(float_image * 255).astype('uint8')


def save(name, float_image):
    float_image = float_image.astype('float32')
    uint8_image = to_uint8(float_image)
    np.save(f'{output_path}/cat-111793_640_{name}_float.npy', float_image)
    np.save(f'{output_path}/cat-111793_640_{name}_uint8.npy', uint8_image)


def ycbcr_to_rgb(ycbcr):
    ycbcr -= np.asarray([0.0625, 0.5, 0.5])
    ycbcr *= np.asarray([1.164, 1, 1])
    rgb = np.matmul(ycbcr, np.asarray([[1, 0, 1.596],
                                       [1, -0.392, -0.813],
                                       [1, 2.017, 0]]).T)
    return rgb


def rgb_to_ycbcr(rgb):
    ycbcr_weights = np.asarray([[0.257, 0.504, 0.098],
                                [-0.148, -0.291, 0.439],
                                [0.439, -0.368, -0.071]]).T
    ycbcr = np.matmul(rgb, ycbcr_weights) + np.asarray([0.0625, 0.5, 0.5])
    return ycbcr


def rgb_to_gray(rgb):
    gray_weights = np.asarray([0.299, 0.587, 0.114])
    gray = np.dot(rgb, gray_weights)
    return np.expand_dims(gray, axis=-1)


def gray_to_ycbcr(gray):
    chroma = np.full_like(gray, 0.5)
    y = gray * (0.257 + 0.504 + 0.098) + 0.0625
    return np.dstack([y, chroma, chroma])


def rgb_to_bgr(rgb):
    return np.flip(rgb, axis=2)


def gray_to_rgb(gray):
    return np.dstack([gray, gray, gray])

dali_extra_path = os.environ['DALI_EXTRA_PATH']
output_path = os.path.join(dali_extra_path, 'db/imgcodec/colorspaces/')
tiff = plt.imread(os.path.join(dali_extra_path, 'db/single/tiff/0/cat-111793_640.tiff'))

rgb = tiff.astype('float32')/255
ycbcr = rgb_to_ycbcr(rgb)
gray = rgb_to_gray(rgb)
bgr = rgb_to_bgr(rgb)

save('rgb', rgb)
save('ycbcr', ycbcr)
save('gray', gray)
save('bgr', bgr)

save('rgb_from_gray', gray_to_rgb(gray))
save('ycbcr_from_gray', gray_to_ycbcr(gray))
save('bgr_from_gray', rgb_to_bgr(gray_to_rgb(gray)))

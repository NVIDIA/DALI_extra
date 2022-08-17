import os
import tifffile
import numpy as np

dali_extra_path = os.environ['DALI_EXTRA_PATH']
tiff_path = os.path.join(dali_extra_path, 'db/imgcodec/tiff/bitdepths')
ref_path = os.path.join(dali_extra_path, 'db/imgcodec/tiff/bitdepths/reference')

h, w = 123, 321
hgrad = np.tile(np.linspace(0., 1., w), (h, 1))
vgrad = np.tile(np.linspace(0., 1., h), (w, 1)).T
image = np.dstack([hgrad, vgrad, 1. - hgrad])  # RGB gradient

def filename(bits):
    return os.path.join(tiff_path, f'rgb_{bits}bit.tiff')

def ref_filename(bits):
    return os.path.join(ref_path, f'rgb_{bits}bit.tiff.npy')

for bits in (8, 16, 32):
    uint_image = (image * (2**bits - 1)).astype(f'uint{bits}')
    tifffile.imwrite(filename(bits), uint_image)
    np.save(ref_filename(bits), uint_image)
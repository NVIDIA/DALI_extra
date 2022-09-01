import os
import tifffile
import numpy as np
import tempfile

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

def ref_float_filename(bits):
    return os.path.join(ref_path, f'rgb_{bits}bit_float.tiff.npy')

standard_bitdepths = [8, 16, 32]

for bits in range(1, 32+1):
    ref = np.round(image * (2**bits - 1)) / (2**bits - 1)
    np.save(ref_float_filename(bits), ref)
    if bits in standard_bitdepths:
        # For standard bit-depths it's possible to test for exact match
        np.save(ref_filename(bits), (image * (2**bits - 1)).astype(f'uint{bits}'))

    if bits in standard_bitdepths:
        # For images in standard bit-depths save the image as is
        tifffile.imwrite(filename(bits), (image * (2**bits - 1)).astype(f'uint{bits}'))
    else:
        # For non-standard bit-depths make a 32-bit image and convert it.
        tmp = tempfile.NamedTemporaryFile()
        tifffile.imwrite(tmp, (ref * (2**32 - 1)).astype('uint32'))
        os.system(f'convert -type TrueColor -define tiff:bits-per-sample={bits} -depth {bits} {tmp.name} {filename(bits)}')

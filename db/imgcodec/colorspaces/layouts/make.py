import os
import tifffile
import matplotlib.pyplot as plt
import numpy as np

dali_extra_path = os.environ['DALI_EXTRA_PATH']
source_path = os.path.join(dali_extra_path, 'db/imgcodec/colorspaces/cat-111793_640_rgb_float.npy')

def output_path(color_format, layout):
    output_directory = os.path.join(dali_extra_path, 'db/imgcodec/colorspaces/layouts')
    return os.path.join(output_directory, f'cat-111793_640_{color_format}_float_{layout}.npy')

def rgb_to_ycbcr(rgb):
    ycbcr_weights = np.asarray([[0.257, 0.504, 0.098],
                                [-0.148, -0.291, 0.439],
                                [0.439, -0.368, -0.071]]).T
    ycbcr = np.matmul(rgb, ycbcr_weights) + np.asarray([0.0625, 0.5, 0.5])
    return ycbcr.astype('float32')


dir_path = os.path.join(dali_extra_path, 'db/imgcodec/colorspaces/')

hwc_rgb = np.load(source_path).astype('float32')
hwc_ycbcr = rgb_to_ycbcr(hwc_rgb)

np.save(output_path('rgb', 'hwc'), hwc_rgb)
np.save(output_path('rgb', 'hcw'), hwc_rgb.transpose(0,2,1))
np.save(output_path('rgb', 'chw'), hwc_rgb.transpose(2,0,1))

np.save(output_path('ycbcr', 'hwc'), hwc_ycbcr)
np.save(output_path('ycbcr', 'hcw'), hwc_ycbcr.transpose(0,2,1))
np.save(output_path('ycbcr', 'chw'), hwc_ycbcr.transpose(2,0,1))

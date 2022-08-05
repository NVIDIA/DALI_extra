import os
import tifffile
import matplotlib.pyplot as plt
import numpy as np

def rgb_to_gray(rgb):
    gray_weights = np.asarray([0.299, 0.587, 0.114])
    gray = np.dot(rgb, gray_weights)
    return np.expand_dims(gray, axis=-1)

dali_extra_path = os.environ['DALI_EXTRA_PATH']
tiff_path = os.path.join(dali_extra_path, 'db/single/tiff')
tiff_ref_path = os.path.join(dali_extra_path, 'db/single/reference/tiff')

img = plt.imread(os.path.join(tiff_path, '0/cat-111793_640.tiff')).astype('uint8')
np.save(os.path.join(tiff_ref_path, '0/cat-111793_640.tiff.npy'), img)

gray = rgb_to_gray(img).astype('uint8')
tifffile.imwrite(os.path.join(tiff_path, '0/cat-111793_640_gray.tiff'), gray)
np.save(os.path.join(tiff_ref_path, '0/cat-111793_640_gray.tiff.npy'), gray)
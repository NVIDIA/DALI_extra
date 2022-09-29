import numpy as np
from matplotlib import pyplot as plt
import os

DALI_EXTRA = os.environ['DALI_EXTRA_PATH']

cat = plt.imread(os.path.join(DALI_EXTRA, 'db/single/tiff/0/kitty-2948404_640.tiff'))

images = [
    ('horizontal', cat),
    ('mirror_horizontal', np.flip(cat, axis=1)),
    ('rotate_180', np.rot90(cat, 2)),
    ('mirror_vertical', np.flip(cat, axis=0)),
    ('mirror_horizontal_rotate_270', np.rot90(np.flip(cat, axis=1))),
    ('rotate_90', np.rot90(cat)),
    ('mirror_horizontal_rotate_90', np.rot90(np.flip(cat, axis=1), 3)),
    ('rotate_270', np.rot90(cat, 3)),
]

for name, img in images:
    path = os.path.join(DALI_EXTRA, f'db/imgcodec/orientation/kitty-2948404_640_{name}.npy')
    np.save(path, img.astype('uint8'))

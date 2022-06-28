## large_tiled_tiff_grayscale.tiff:

Large tiled TIFF synthetically generated for test purposes.
It was generated as:
```python

import cv2
import numpy as np
a = np.zeros([1024 * 65, 1024 * 64], dtype=np.uint8)
for i in range(65 * 2):
    for j in range(64 * 2):
        a[i*512:(i+1)*512, j*512:(j+1)*512, :] = 97 * i + j

cv2.imwrite('tiles.tiff', a)
```

Then, transcoded with
```
./magick convert tiles.tiff -define tiff:tile-geometry=1024x1024 -compress lzw large_tiled_tiff_grayscale.tiff
```

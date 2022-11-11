import numpy as np

np.random.seed(123456)

# Only crop
def test():
    shapes = [(10, 22, 3), (30, 20, 3), (100, 5, 3)]
    dtype = np.uint8
    arrays = [np.array(np.random.rand(*sh) * 255, dtype=dtype) for sh in shapes]

    for i, arr in enumerate(arrays):
        np.save(f"./input{i}.npy", arr)

    start = [(2, 8, 0), (22, 2, 0), (55, 4, 0)]
    end = [(8, 19, 3), (28, 4, 3), (100, 5, 3)]
    flip = [(False, True), (True, True), (False, False)]

    mean = [255 * np.array([0.485, 0.456, 0.406], dtype=np.float32),
            255 * np.array([0.455, 0.436, 0.416], dtype=np.float32),
            255 * np.array([0.495, 0.466, 0.396], dtype=np.float32)]
    stddev = [255 * np.array([0.229, 0.224, 0.225], dtype=np.float32),
              255 * np.array([0.225, 0.224, 0.221], dtype=np.float32),
              255 * np.array([0.226, 0.229, 0.222], dtype=np.float32)]
    for i, arr in enumerate(arrays):
        y0, x0, c0 = start[i]
        y1, x1, c1 = end[i]
        arr = arr.astype(np.float32)
        arr = (arr - mean[i]) / stddev[i]
        arr = arr[y0:y1, x0:x1, c0:c1]
        flip_y, flip_x = flip[i]
        if flip_y:
            arr = np.flip(arr, axis=0)
        if flip_x:
            arr = np.flip(arr, axis=1)
        arr = np.transpose(arr, (2, 0, 1))

        np.save(f"./output{i}.npy", arr)

test()

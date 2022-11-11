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
    for i, arr in enumerate(arrays):
        y0, x0, c0 = start[i]
        y1, x1, c1 = end[i]
        arr = arr[y0:y1, x0:x1, c0:c1]
        np.save(f"./output{i}.npy", arr)

test()

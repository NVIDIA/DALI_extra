import numpy as np

np.random.seed(123456)

shapes = [(10, 22, 3), (30, 20, 3), (100, 5, 3)]
dtype = np.uint8
arrays = [np.array(np.random.rand(*sh) * 255, dtype=dtype) for sh in shapes]

for i, arr in enumerate(arrays):
    np.save(f"./input{i}.npy", arr)

def gen_crop():
    start = [(2, 8, 0), (22, 2, 0), (55, 4, 0)]
    end = [(8, 19, 3), (28, 4, 3), (100, 5, 3)]
    for i, arr in enumerate(arrays):
        y0, x0, c0 = start[i]
        y1, x1, c1 = end[i]
        arr = arr[y0:y1, x0:x1, c0:c1]
        np.save(f"./output{i}_c.npy", arr)

def gen_crop_mirror():
    start = [(2, 8, 0), (22, 2, 0), (55, 4, 0)]
    end = [(8, 19, 3), (28, 4, 3), (100, 5, 3)]
    flip = [(False, True), (True, True), (False, False)]
    for i, arr in enumerate(arrays):
        y0, x0, c0 = start[i]
        y1, x1, c1 = end[i]
        arr = arr[y0:y1, x0:x1, c0:c1]
        flip_y, flip_x = flip[i]
        if flip_y:
            arr = np.flip(arr, axis=0)
        if flip_x:
            arr = np.flip(arr, axis=1)
        np.save(f"./output{i}_cm.npy", arr)

def gen_crop_mirror_normalize():
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
        np.save(f"./output{i}_cmn.npy", arr)

def gen_crop_mirror_normalize_transpose():
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

        np.save(f"./output{i}_cmnt.npy", arr)

def gen_pad_normalize():
    start = np.array([[-2, 0, 0], [0, -4, 0], [0, 0, 0]])
    end = np.array([[8, 19, 4], [28, 4, 4], [120, 5, 4]])

    mean = [255 * np.array([0.485, 0.456, 0.406], dtype=np.float32),
            255 * np.array([0.455, 0.436, 0.416], dtype=np.float32),
            255 * np.array([0.495, 0.466, 0.396], dtype=np.float32)]
    stddev = [255 * np.array([0.229, 0.224, 0.225], dtype=np.float32),
              255 * np.array([0.225, 0.224, 0.221], dtype=np.float32),
              255 * np.array([0.226, 0.229, 0.222], dtype=np.float32)]
    # Padding channels too
    fill_values = [np.array([255.0, 128.0, 64.0, 32.0], dtype=np.float32) + np.float32(i) for i in range(3)]

    out_sh = end - start
    out0 = np.zeros(out_sh[0], dtype=np.float32)
    out0 = out0 + fill_values[0]
    out0[2:10, :, :3] = (arrays[0][0:8, :19, :3].astype(np.float32) - mean[0]) / stddev[0]
    np.save(f"./output0_pn.npy", out0)

    out1 = np.zeros(out_sh[1], dtype=np.float32)
    out1 = out1 + fill_values[1]
    out1[:, 4:8, :3] = (arrays[1][:28, :4, :3].astype(np.float32) - mean[1]) / stddev[1]
    np.save(f"./output1_pn.npy", out1)

    out2 = np.zeros(out_sh[2], dtype=np.float32)
    out2 = out2 + fill_values[2]
    out2[:100, :, :3] = (arrays[2][:100, :5, :3].astype(np.float32) - mean[2]) / stddev[2]
    np.save(f"./output2_pn.npy", out2)


def generate():
    gen_crop()
    gen_crop_mirror()
    gen_crop_mirror_normalize()
    gen_crop_mirror_normalize_transpose()
    gen_pad_normalize()


generate()

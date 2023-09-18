TFRecord dataset with 1000 tensors with 10 elements each. All elements in one tensor are the same. Consecutive samples have elements with increasing values. For examples first 5 samples in this datasets are:
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    [4, 4, 4, 4, 4, 4, 4, 4, 4, 4]

This dataset can be used to test framework iterators in various scenarios with sharding and batching.


"""
    def write_tfrecords():
        path = 'sequential.tfrecord'
        
        writer = tf.io.TFRecordWriter(path)
        for index in range(1000):
            tensor = np.full(shape=(10), fill_value=index, dtype=np.int32)

            example = serialize_example(tensor)
            writer.write(example)

    write_tfrecords()
"""
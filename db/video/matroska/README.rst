Matroska copy of an H.264 test clip with B-frames. Matroska stores only the presentation timestamp
(pts) of each block, here in milliseconds, and FFmpeg's Matroska demuxer seeks to the keyframes by
pts (with the Cues, the index of the keyframes at the end of the file). There are no decoding
timestamps (dts) in the file: once libavformat has probed the stream (``avformat_find_stream_info``,
as PyAV and ffprobe do), it derives them from the pts and the reordering of the stream, and
otherwise the packets have none. With B-frames, the dts of a keyframe is below its pts, so a seek
to the dts of a keyframe lands on the keyframe before.

Not in ``../containers/mkv``: the tests of the legacy video reader read every file there.

Files:

- ``test_1.mkv``: ``../cfr/test_1.mp4`` (H.264, High profile, 1280x720, 60 fps, 50 frames) copied
  without re-encoding: the same packets in the same order, with the avcC of the source as the
  CodecPrivate. The keyframes (IDR pictures) are the packets 0, 10, 18, 28, 38 and 48 in the
  decoding order, each at the start of a cluster, and there are B-frames. The pts are those of the
  source in milliseconds, rounded (the frames are 16 or 17 ms apart, so the frame rate looks
  variable): the keyframes are at 0, 167, 300, 467, 633 and 800 ms. Once the stream is probed, each
  keyframe after the first has a dts two frames (33 or 34 ms) below its pts, so a seek to its dts
  lands on the keyframe before. The frames are those of the source.
- ``generate.py``: regenerates the file and checks it (the packets, their key flags and the avcC
  the same as in the source, the pts of the source in milliseconds, some reordered frames, the
  SeekHead and the Cues pointing to the elements and to the keyframes they name, a seek to the pts
  of each keyframe landing on it and a seek to its dts on the keyframe before, the decoded frames
  the same as those of the source). It writes the Matroska file itself, so the output does not
  depend on the FFmpeg version. Needs Python 3, PyAV 14 or newer (``pip install "av>=14"``) and the
  real file ``../cfr/test_1.mp4`` (not a Git LFS pointer). The committed file was checked with PyAV
  14.1 (FFmpeg 7.1):

.. code-block:: bash

  python3 generate.py
  # or, with the source file somewhere else:
  python3 generate.py --video-dir /path/to/db/video


Test data for an H.264 stream whose timestamps do not fit in a signed 32-bit integer. MPEG-TS
timestamps have 33 bits, and a capture (e.g. a recording of a broadcast) may start above 2^31 in the
90 kHz time base, that is after about 6.6 hours. A decoder that keeps a timestamp in a signed 32-bit
integer cannot match the decoded pictures to the frames of this stream. All the timestamps are below
2^32, so an unsigned 32-bit integer still holds them.

Files:

- ``h264_large_pts.ts``: 65 frames, 1280x720, 24 fps, H.264 (High profile), YUV 4:2:0, MPEG-TS.
  The packets are the first 65 packets in the decoding order (frames 0-64) of
  ``../sintel/video_files/sintel_trailer-720p_0.mp4``, copied without re-encoding: the slices are
  unchanged, and the MPEG-TS muxer adds an access unit delimiter to every packet and the SPS and PPS
  before the IDR picture. The timestamps all move 30000 s later. The time base is 1/90000 and a
  frame lasts 3750. Frame ``k`` has the pts ``2700000000 + k * 3750``, from 2700000000 to
  2700240000, and the first dts is 2699992500. The decoded frames are the same as the first 65
  frames of the source. Only the first packet is flagged as a keyframe.
- ``generate.py``: regenerates the file and checks it (65 packets and 65 decoded frames, only the
  first packet flagged as a keyframe, the timestamps of the source moved by the offset, every
  timestamp above 2^31 and below 2^33, the decoded frames the same as those of the source). Needs
  Python 3, PyAV 14 or newer (``pip install "av>=14"``) and the real ``sintel_trailer-720p_0.mp4``
  (not a Git LFS pointer). The committed file was generated with PyAV 14.1 (FFmpeg 7.1); other
  versions may write a different but equivalent MPEG-TS file:

.. code-block:: bash

  python3 generate.py
  # or, with the source file somewhere else:
  python3 generate.py --src /path/to/sintel_trailer-720p_0.mp4

The video is from the Sintel trailer, (c) copyright Blender Foundation | durian.blender.org,
licensed under the Creative Commons Attribution 3.0 license.

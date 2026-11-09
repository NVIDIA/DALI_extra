
Test data for an H.264 stream in which two consecutive frames share a timestamp and one of them is a
non-reference picture. A decoder that matches the decoded pictures to the frames by their
timestamps has to cope with this stream, for example when it reads a frame whose pts is the same as
the pts of the frame before it, which it only skips.

Files:

- ``h264_nonref_dup_pts.ts``: 65 frames, 1280x720, 24 fps, H.264 (High profile), YUV 4:2:0,
  MPEG-TS. The packets are the first 65 packets in the decoding order (frames 0-64) of
  ``../sintel/video_files/sintel_trailer-720p_0.mp4``, copied without re-encoding. Only the
  timestamps change:

  - every non-reference picture (``nal_ref_idc`` 0) takes the pts of the frame shown right before it
    in the source,
  - every dts moves one frame earlier, so that pts >= dts still holds,
  - all timestamps move 3 frames later, so that dts >= 0.

  The time base is 1/90000 and a frame lasts 3750. Frame ``k`` (in the display order of the source)
  has the pts ``(k + 3) * 3750``, except for the non-reference pictures, which have the pts of frame
  ``k - 1``. The non-reference pictures are frames 13, 16, 19, 21, 24, 26, 28, 31, 34, 37, 39, 42,
  44, 46, 48, 50, 52, 54, 57, 59, 61 and 63, so 22 pairs of frames share a pts: (12, 13), (15, 16),
  (18, 19), (20, 21), (23, 24), (25, 26), (27, 28), (30, 31), (33, 34), (36, 37), (38, 39),
  (41, 42), (43, 44), (45, 46), (47, 48), (49, 50), (51, 52), (53, 54), (56, 57), (58, 59),
  (60, 61) and (62, 63). The frame shown before each non-reference picture is a reference picture.
  Only the first picture is an IDR picture and only the first packet is flagged as a keyframe. The
  packets are in the Annex B format and start with an access unit delimiter.

  The clip is MPEG-TS because MPEG-TS stores the pts and dts of every packet as they are given, so
  the shared timestamps reach the demuxer unchanged.
- ``generate.py``: regenerates the file and checks it (65 packets and 65 decoded frames, dts
  strictly increasing, pts >= dts, the frame pairs above sharing a pts, Annex B packets). Needs
  Python 3 and PyAV (``pip install av``) and the real ``sintel_trailer-720p_0.mp4`` (not a Git LFS
  pointer). The committed file was generated with PyAV 14.1 (FFmpeg 7.1); other versions may write
  a different but equivalent MPEG-TS file:

.. code-block:: bash

  python3 generate.py
  # or, with the source file somewhere else:
  python3 generate.py --src /path/to/sintel_trailer-720p_0.mp4

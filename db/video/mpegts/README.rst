
MPEG-TS copies of test clips, with the timestamps they need to test. MPEG-TS stores H.264 and HEVC
in the Annex B format, and FFmpeg's MPEG-TS demuxer seeks by decoding timestamp (dts), on any
packet. With B-frames a keyframe's dts is lower than its pts, so a seek to the keyframe's pts lands
after the keyframe. The time base is 1/90000.

Each file is a clip copied without re-encoding: the slices are unchanged, and the muxer adds an
access unit delimiter to every packet and the parameter sets before every IDR (H.264) or IRAP (HEVC)
picture. The frames are those of the source. Only the timestamps differ:

- ``test_1.ts``: ``../cfr/test_1.mp4`` (H.264, 1280x720, 60 fps, 50 frames, B-frames). IDR pictures
  at the packets 0, 10, 18, 28, 38 and 48 in the decoding order.
- ``test_2_hevc.ts``: ``../cfr/test_2_hevc.mp4`` (HEVC, 800x600, 60 fps, 60 frames, B-frames). An IDR
  picture at the packet 0 and a CRA picture at 40.
- ``open_gop_h264.ts``: ``../non_idr_keyframes/open_gop_h264.mp4`` (H.264, 128x96, 64 frames, open
  GOPs). Only the packet 0 is an IDR picture, but the demuxer also flags the non-IDR I-pictures after
  a recovery point SEI (packets 10, 24, 35, 48 and 57) as keyframes.
- ``test_1_mid_gop.ts``: ``test_1.mp4`` without its first 8 packets, as a capture that starts in the
  middle of a GOP: its first packet is shown after the second one, and the first keyframe is the
  packet 2. Only for indexing: the first pictures refer to pictures that are not in the file.

In these four, every timestamp moves by the same amount, so that the first dts is 0. The other two
are the first 65 frames of ``../sintel/video_files/sintel_trailer-720p_0.mp4`` (H.264, 1280x720,
24 fps):

- ``../duplicate_pts/h264_nonref_dup_pts.ts``: every non-reference picture (``nal_ref_idc`` 0) takes
  the pts of the frame shown right before it, so 22 pairs of frames share a pts. Every dts moves one
  frame earlier so that pts >= dts, and all timestamps move 3 frames later so that dts >= 0.
- ``../large_pts/h264_large_pts.ts``: every timestamp 30000 s later, between 2^31 and 2^33 ticks
  (MPEG-TS timestamps have 33 bits), so they do not fit in a signed 32-bit integer.

``generate.py`` regenerates all of them and checks them: the packets and key flags of the source, the
expected timestamps with the dts strictly increasing, Annex B packets, some reordered frames, and the
decoded frames the same as those of the source (for ``test_1_mid_gop.ts``, a first packet shown after
the second one). It needs Python 3, PyAV 14 or newer (``pip install "av>=14"``) and the real source
clips, not Git LFS pointers. The files were generated with PyAV 14.1 (FFmpeg 7.1); other versions may
write different but equivalent MPEG-TS files:

.. code-block:: bash

  python3 generate.py
  # or, with the source files somewhere else:
  python3 generate.py --video-dir /path/to/db/video

The video of ``../duplicate_pts`` and ``../large_pts`` is from the Sintel trailer, (c) copyright
Blender Foundation | durian.blender.org, licensed under the Creative Commons Attribution 3.0 license.

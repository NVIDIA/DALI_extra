
MPEG-TS copies of test clips. MPEG-TS stores H.264 and HEVC in the Annex B format (the NAL units
follow start codes, not their length, as in MP4), and FFmpeg's MPEG-TS demuxer seeks by decoding
timestamp (dts), on any packet, not by presentation timestamp (pts) on the keyframes, as its MP4
demuxer does. With B-frames, a keyframe's dts is lower than its pts, so a seek to the keyframe's pts
lands after the keyframe. The key flags of the packets come from FFmpeg's H.264/HEVC parser, which
also flags H.264 I-pictures with a recovery point, that decoding cannot always start from.

Files:

- ``test_1.ts``: ``../cfr/test_1.mp4`` (H.264, High profile, 1280x720, 60 fps, 50 frames). The key
  packets (IDR pictures) are the packets 0, 10, 18, 28, 38 and 48 in the decoding order, and there
  are B-frames. The frames are those of the source, so its ground truth applies
  (``../cfr/frames_1_vp9``).
- ``test_2_hevc.ts``: ``../cfr/test_2_hevc.mp4`` (HEVC, Main profile, 800x600, 60 fps, 60 frames).
  The key packets are the packets 0 (an IDR picture) and 40 (a CRA picture) in the decoding order,
  and there are B-frames. The frames are those of the source, so its ground truth applies
  (``../cfr/frames_2_vp9``).
- ``open_gop_h264.ts``: ``../non_idr_keyframes/open_gop_h264.mp4`` (H.264, High profile, 128x96,
  25 fps, 64 frames, B-frames and open GOPs). Only the first picture is an IDR picture, but the
  packets 0, 10, 24, 35, 48 and 57 in the decoding order are flagged as keyframes: the others are
  non-IDR I-pictures with a recovery point. The frames are those of the source.
- ``test_1_mid_gop.ts``: ``../cfr/test_1.mp4`` without its first 8 packets: it starts in the middle
  of a GOP, as a capture can. Its first packet is shown after the second one (frame 0), and the
  first keyframe (an IDR picture) is its packet 2. 42 frames. Only for the index of the file: the
  pictures before the first keyframe refer to pictures that are not in the file.

  In all of them, the packets are those of the source, copied without re-encoding, and only the
  timestamps change: they all move by the same amount, so that the first dts is 0. The time base is
  1/90000.
- ``generate.py``: regenerates the files and checks them (the packets, their order and key flags,
  and the timestamps of the source moved by the offset, dts strictly increasing, Annex B packets,
  some reordered frames, the IDR/IRAP pictures flagged as keyframes, the decoded frames the same as
  those of the source, or, for ``test_1_mid_gop.ts``, a first packet that is not a keyframe and is
  shown after the second one). Needs Python 3 and PyAV (``pip install av``) and the real files in
  ``../cfr`` and ``../non_idr_keyframes`` (not Git LFS pointers). The committed files were
  generated with PyAV 14.1 (FFmpeg 7.1); other versions may write different but equivalent MPEG-TS
  files:

.. code-block:: bash

  python3 generate.py
  # or, with the source files somewhere else:
  python3 generate.py --video-dir /path/to/db/video

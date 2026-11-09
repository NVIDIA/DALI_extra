
MPEG-TS copies of CFR test clips. MPEG-TS stores H.264 and HEVC in the Annex B format (the NAL units
follow start codes, not their length, as in MP4), and FFmpeg's MPEG-TS demuxer seeks by decoding
timestamp (dts), on any packet, not by presentation timestamp (pts) on the keyframes, as its MP4
demuxer does. With B-frames, a keyframe's dts is lower than its pts, so a seek to the keyframe's pts
lands after the keyframe. The decoded frames are the same as those of the clips they were copied
from, so the ground truth of those clips applies (``../cfr/frames_1_vp9``, ``../cfr/frames_2_vp9``).

Files:

- ``test_1.ts``: ``../cfr/test_1.mp4`` (H.264, High profile, 1280x720, 60 fps, 50 frames), copied
  to MPEG-TS without re-encoding. The key packets (IDR pictures) are the packets 0, 10, 18, 28, 38
  and 48 in the decoding order, and there are B-frames.
- ``test_2_hevc.ts``: ``../cfr/test_2_hevc.mp4`` (HEVC, Main profile, 800x600, 60 fps, 60 frames),
  copied to MPEG-TS without re-encoding. The key packets are the packets 0 (an IDR picture) and 40
  (a CRA picture) in the decoding order, and there are B-frames.

  In both, only the timestamps change: they all move by the same amount, so that the first dts is
  0. The time base is 1/90000, and the first pts is 3000.
- ``generate.py``: regenerates the files and checks them (the packets, their order and key flags,
  and the timestamps of the source moved by the offset, dts strictly increasing, Annex B packets,
  some reordered frames, the decoded frames the same as those of the source). Needs Python 3 and
  PyAV (``pip install av``) and the real files in ``../cfr`` (not Git LFS pointers). The committed
  files were generated with PyAV 14.1 (FFmpeg 7.1); other versions may write different but
  equivalent MPEG-TS files:

.. code-block:: bash

  python3 generate.py
  # or, with the source files somewhere else:
  python3 generate.py --src-dir /path/to/cfr

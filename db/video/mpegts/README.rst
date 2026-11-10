
MPEG-TS copies of test clips. MPEG-TS stores H.264 and HEVC in the Annex B format (the NAL units
follow start codes, not their length, as in MP4), and FFmpeg's MPEG-TS demuxer seeks by decoding
timestamp (dts), on any packet, while its MP4 demuxer seeks only to the keyframes (it searches them
by dts, offset by the edit list). With B-frames, a keyframe's dts is lower than its pts, so in
MPEG-TS a seek to the keyframe's pts lands after the keyframe. The key flags of the packets come
from FFmpeg's H.264/HEVC parser, which also flags the H.264 pictures that follow a recovery point
SEI (in ``open_gop_h264.ts``, non-IDR I-pictures), that decoding cannot always start from.

Each file is a clip of ``../cfr`` or ``../non_idr_keyframes`` copied without re-encoding: the slices
are unchanged, and the MPEG-TS muxer adds an access unit delimiter to every packet and the
parameter sets of the source before every IDR (H.264) or IRAP (HEVC) picture, for HEVC with the SEI
stored with them (x265's encoder settings). The timestamps all move by the same amount, so that the
first dts is 0. The time base is 1/90000.

Files:

- ``test_1.ts``: ``../cfr/test_1.mp4`` (H.264, High profile, 1280x720, 60 fps, 50 frames). The key
  packets (IDR pictures) are the packets 0, 10, 18, 28, 38 and 48 in the decoding order, and there
  are B-frames. The frames are those of the source, and DALI's tests compare them with
  ``../cfr/frames_1_vp9``, as they do for the source (the frames of ``test_1.mp4`` itself are in
  ``../cfr/frames_1``).
- ``test_2_hevc.ts``: ``../cfr/test_2_hevc.mp4`` (HEVC, Main profile, 800x600, 60 fps, 60 frames).
  The key packets are the packets 0 (an IDR picture) and 40 (a CRA picture) in the decoding order,
  and there are B-frames. The frames are those of the source, and DALI's tests compare them with
  ``../cfr/frames_2_vp9``, as they do for the source.
- ``open_gop_h264.ts``: ``../non_idr_keyframes/open_gop_h264.mp4`` (H.264, High profile, 128x96,
  25 fps, 64 frames, B-frames and open GOPs). Only the first picture is an IDR picture, but the
  packets 0, 10, 24, 35, 48 and 57 in the decoding order are flagged as keyframes: the others are
  non-IDR I-pictures after a recovery point SEI. The frames are those of the source.
- ``test_1_mid_gop.ts``: ``../cfr/test_1.mp4`` without its first 8 packets: it starts in the middle
  of a GOP, as a capture can. Its first packet is shown after the second one (frame 0), and the
  first keyframe (an IDR picture) is its packet 2. 42 frames. Only for the index of the file: the
  pictures before the first keyframe refer to pictures that are not in the file.
- ``generate.py``: regenerates the files and checks them (the number of packets, their key flags the
  same as in the source, the timestamps of the source moved by the offset, dts strictly increasing,
  Annex B packets, some reordered frames, the IDR/IRAP pictures flagged as keyframes, the decoded
  frames the same as those of the source, or, for ``test_1_mid_gop.ts``, a first packet that is not
  a keyframe and is shown after the second one). Needs Python 3, PyAV 14 or newer
  (``pip install "av>=14"``) and the real files in ``../cfr`` and ``../non_idr_keyframes`` (not Git
  LFS pointers). The committed files were generated with PyAV 14.1 (FFmpeg 7.1); other versions may
  write different but equivalent MPEG-TS files:

.. code-block:: bash

  python3 generate.py
  # or, with the source files somewhere else:
  python3 generate.py --video-dir /path/to/db/video

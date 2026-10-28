
Test data for the YUV -> RGB colour matrix of the video decoders. The clips are tagged as BT.709 /
limited range (what HD content normally uses), and the references are what ffmpeg produces for them.
A decoder that converts with BT.601 instead of the matrix in the stream gives visibly different
colours for saturated colours (e.g. pure red 255,0,0 comes out as ~234,0,3).

Files:

- ``bars.png``: the RGB source (ground truth). Top half: 8 flat bars (red, green, blue, yellow, cyan,
  magenta, orange, grey), bottom half: ramps.
- ``bt709_limited_1080p.mp4``: 8 frames, 1920x1080, H.264, YUV 4:2:0, BT.709, limited range.
- ``bt709_limited_1080p_vp9.mp4``: the same in VP9 (the CPU variant of the video reader supports
  only VP8/VP9).
- ``bt709_limited_1080p_ref.png``, ``bt709_limited_1080p_vp9_ref.png``: the first frame of each clip,
  decoded and converted to RGB by ffmpeg (which uses the matrix and range tagged in the stream).
- ``make_pattern.py``: writes ``bars.png``.
- ``generate.sh``: regenerates everything above (needs python3 with numpy and Pillow, and ffmpeg
  with libx264 and libvpx-vp9). The ffmpeg commands are:

.. code-block:: bash

  #!/bin/bash
  python3 make_pattern.py bars.png

  # Encode the pattern as BT.709, limited range, and tag the stream accordingly.
  ffmpeg -y -loop 1 -framerate 25 -i bars.png -frames:v 8 \
    -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv" \
    -c:v libx264 -preset veryslow -crf 10 -profile:v high -bf 0 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
    bt709_limited_1080p.mp4
  ffmpeg -y -loop 1 -framerate 25 -i bars.png -frames:v 8 \
    -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv" \
    -c:v libvpx-vp9 -crf 10 -b:v 0 \
    -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
    bt709_limited_1080p_vp9.mp4

  # The references: first frame decoded and converted to RGB by ffmpeg with default settings.
  ffmpeg -y -i bt709_limited_1080p.mp4 -frames:v 1 -update 1 -pix_fmt rgb24 bt709_limited_1080p_ref.png
  ffmpeg -y -c:v libvpx-vp9 -i bt709_limited_1080p_vp9.mp4 -frames:v 1 -update 1 -pix_fmt rgb24 bt709_limited_1080p_vp9_ref.png

All frames of a clip are identical, so any frame can be compared with the reference.

How to compare: the codec and the chroma subsampling make the values differ slightly from
``bars.png``, mostly near the edges of the bars. Compare the mean colour of the interior of each bar
(for example, columns ``i*240+40`` to ``(i+1)*240-40`` and rows 100 to 440 for bar ``i``). In those
areas the reference differs from ``bars.png`` by at most 2 (out of 255), while a BT.601 conversion of
these streams differs by up to 22.


Test data for H.264 and HEVC streams whose keyframes are not IDR pictures. A decoder that finds the
keyframes to seek to by looking for IDR pictures only, or that trusts the keyframe flag of the
container, has to cope with these streams (open GOPs).

Files:

- ``open_gop_h264.mp4``: 64 frames, 128x96, 25 fps, H.264 (High profile), YUV 4:2:0, B-frames and
  open GOPs with a keyframe interval of 12. Only the first picture is an IDR picture (NAL unit type
  5). The keyframes at frames 12, 24, 36, 48 and 60 are non-IDR I-pictures (NAL unit type 1) with a
  recovery point SEI, and the container flags them as keyframes. The B-pictures that follow them in
  the decoding order precede them in the display order and refer to the previous GOP, so decoding
  cannot start at them without losing those frames. The content (``testsrc2``) changes in every
  frame.
- ``open_gop_hevc.mp4``: the same for HEVC (Main profile), 64 frames, 256x192 (NVDEC decodes HEVC
  from 144x144). Only the first picture is an IDR picture (NAL unit type 20). The keyframes at
  frames 12, 24, 36, 48 and 60 are CRA pictures (NAL unit type 21) that the container flags as
  keyframes. The RASL pictures (NAL unit types 8 and 9) that follow a CRA picture in the decoding
  order precede it in the display order and refer to the previous GOP.
- ``generate.sh``: regenerates the files and checks the structure of the streams (needs ffmpeg with
  libx264 and libx265, and ffprobe). The ffmpeg commands are:

.. code-block:: bash

  ffmpeg -y -f lavfi -i "testsrc2=size=128x96:rate=25" -frames:v 64 -pix_fmt yuv420p \
    -c:v libx264 -preset slow -crf 18 -profile:v high \
    -x264-params keyint=12:min-keyint=12:scenecut=0:bframes=3:open-gop=1 \
    open_gop_h264.mp4
  ffmpeg -y -f lavfi -i "testsrc2=size=256x192:rate=25" -frames:v 64 -pix_fmt yuv420p \
    -c:v libx265 -preset slow -crf 18 \
    -x265-params keyint=12:min-keyint=12:scenecut=0:bframes=3:open-gop=1:log-level=none \
    open_gop_hevc.mp4

To list the NAL unit types of the stream:

.. code-block:: bash

  ffmpeg -i open_gop_h264.mp4 -c copy -bsf:v trace_headers -f null - 2>&1 | grep nal_unit_type
  ffmpeg -i open_gop_hevc.mp4 -c copy -bsf:v trace_headers -f null - 2>&1 | grep nal_unit_type

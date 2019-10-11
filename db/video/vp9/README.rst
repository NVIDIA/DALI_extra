
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  # Create a 3 second video at 60fps at constant frame rate.
  # 180 frames, with a time delta of 1/60ms. Duration 3s.
  # VP9 codec, profile 0.
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libvpx-vp9  -profile:v 0 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" vp9_0.mp4
  # Create a 3 second video at 60fps at constant frame rate.
  # 180 frames, with a time delta of 1/60ms. Duration 3s.
  # VP9 codec, profile 2.
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libvpx-vp9  -profile:v 2 -vf "format=pix_fmts=yuv420p10le, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" vp9_2.mp4

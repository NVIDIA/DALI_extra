
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  # Create a 3 second video at 60fps at constant frame rate.
  # 180 frames, with a time delta of 1/60ms. Duration 3s.
  # mjpeg codec
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v mjpeg  -vf "format=pix_fmts=yuv444p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" mjpeg.avi

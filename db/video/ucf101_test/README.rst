
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  # Create a 3 second video at 30fps at constant frame rate.
  # 90 frames, with a time delta of 1/30ms. Duration 3s.
  # Avi container with divx codec.
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=30 -c:v libxvid -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=30: text='%{frame_num}'" dali.avi
  # Transcode video with packed b-frames
  mencoder dali.avi -oac copy -ovc xvid -xvidencopts bitrate=-1:max_bframes=2:threads=4:packed -o packed_bframes_test.avi
  rm dali.avi


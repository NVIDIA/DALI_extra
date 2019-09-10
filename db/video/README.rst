
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  # Create a 3 second video at 60fps at constant frame rate.
  # 180 frames, with a time delta of 1/60ms. Duration 3s.
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" cfr_test.mp4
  # Create a 3 second video at 29.97(30000/1001)fps at constant frame rate.
  # 90 frames, with a time delta of 1001/30000ms. Duration 3s.
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=30000/1001 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=30000/1001: text='%{frame_num}'" cfr_ntsc_29_97_test.mp4
  # Transcode video to 25fps at variable frame rate.
  # 180 frames, time deltas spaced between 1/30ms and 1/20ms. Duration ~7s.
  ffmpeg -i cfr_test.mp4 -vsync vfr -vf setpts='N/(25*TB)' vfr_test.mp4

provided in the issue in the main DALI repository (https://github.com/NVIDIA/DALI/issues/1041).

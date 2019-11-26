
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  # Create a 256 second video at 1fps at constant frame rate.
  # This video has the property that luma = blue chroma = red chroma = frame timestamp = frame number
  ffmpeg -f lavfi  -i  "nullsrc='s=512x512:d=256:r=1',scale=out_range=full,geq='lum=N:cb=N:cr=N',format=yuv420p,drawtext=fontfile=Arial.ttf: text=%{n}: x=(w-tw)/2: y=h-(2*lh): fontsize=20: fontcolor=white: box=1: boxcolor=0x00000099" test.mp4
  # Create a 10 second video, at 25 fps constant frame rate.
  ffmpeg -f lavfi  -i  "nullsrc='s=512x512:d=10:r=25',scale=out_range=full,format=yuv420p,drawtext=fontfile=Arial.ttf: text=%{n}: x=(w-tw)/2: y=h-(2*lh): fontsize=20: fontcolor=white: box=1: boxcolor=0x00000099" test_25fps.mp4

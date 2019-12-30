
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  # Create a 3 second video at 10, 20 and 50 fps with
  ffmpeg -f lavfi -i testsrc=duration=3:size=512x512:rate=10 -pix_fmt yuv420p 10fps.mp4
  ffmpeg -f lavfi -i testsrc=duration=3:size=512x512:rate=20 -pix_fmt yuv420p 20fps.mp4
  ffmpeg -f lavfi -i testsrc=duration=3:size=512x512:rate=50 -pix_fmt yuv420p 50fps.mp4

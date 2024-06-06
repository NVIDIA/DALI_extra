10b video was generated using the regular one:

.. code-block:: bash

  #!/bin/bash
  ffmpeg  -i sintel_trailer-720p.mp4 -c:v libx265 -c:a copy -pix_fmt yuv420p10le sintel_trailer-720p_10b.mp4

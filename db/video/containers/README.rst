
Video files used for tests were generated with command below:

.. code-block:: bash

  #!/bin/bash
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" -f matroska cfr.mkv
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" -f avi cfr.avi
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" -f mov cfr.mov
  ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=64: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" -f mmpeg cfr.mpeg

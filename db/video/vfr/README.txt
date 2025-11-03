# Transcode file to VFR, add keyframes:
ffmpeg -i input.mp4 -vsync vfr -vf setpts='N/(25*TB)' -g 10 -keyint_min 10  output.mp4

Files in this directory were created based on files in cfr directory combining the command above with commands used for transcoding.

Frames has been generated following:

ffmpeg -i test_1.mp4 -vsync vfr -sws_flags bilinear+full_chroma_int+accurate_rnd frames_1/%03d.png

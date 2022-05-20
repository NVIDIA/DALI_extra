# Transcode file to VFR, add keyframes:
ffmpeg -i input.mp4 -vsync vfr -vf setpts='N/(25*TB)' -g 10 -keyint_min 10  output.mp4

Files in this directory were created based on files in cfr directory combining the command above with commands used for transcoding.

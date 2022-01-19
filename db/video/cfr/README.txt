Create video: 
ffmpeg -f lavfi -i color=c=blue:s=1280x720:d=3:r=60 -c:v libx264 -vf "format=pix_fmts=yuv420p, drawtext=fontsize=480: fontcolor=white: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" test.mp4

Get frames from video:
ffmpeg -i test.mp4 %03d.png

Build video from frames:
ffmpeg -r 60 -i %03d.png -c:v libx264 -g 10 -keyint_min 10 -vf fps=60 -pix_fmt yuv420p test.mp4

Avi files are transcoded mp4 files:
ffmpeg -i test.mp4 -q:a 0 -q:v 0 test.avi
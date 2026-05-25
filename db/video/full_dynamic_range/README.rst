# to create full color dynamic range video run (a single image copied multiple times has been used for the test video)
ffmpeg -r 25 -i %02d.jpg -c:v libx265 -x265-params keyint=1:min-keyint=1:range=full -dst_range 1 -pix_fmt yuvj420p -hide_banner -b:v 1.8M -maxrate 1.8M -y -colorspace bt470bg -color_primaries bt470bg -color_range 2 -movflags +faststart video.mp4

ffmpeg -i video.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -pix_fmt yuv420p -color_range pc -c:a libopus video_vp9.mp4

# the first frame was extracted using
ffmpeg -i video.mp4 %04d.png
ffmpeg -i video_vp9.mp4 %04d_vp9.png

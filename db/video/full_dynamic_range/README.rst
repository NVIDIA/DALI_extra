# to create full color dynamic range video run (a single image copied multiple times has been used for the test video)
ffmpeg -r 25 -i %02d.jpg -c:v libx265 -x265-params keyint=1:min-keyint=1:range=full -dst_range 1 -pix_fmt yuvj420p -hide_banner -b:v {rate}M -maxrate {rate}M -y -colorspace bt470bg -color_primaries bt470bg -color_range 2 -movflags +faststart video.mp4

# the first frame was extracted using
ffmpeg -i input.mp4 %04d.png

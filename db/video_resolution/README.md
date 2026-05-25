#### Video files were generated with command below:
```
# Create a 10 second, 30fps video of 1920x1080 resolution
ffmpeg -f lavfi -i testsrc=duration=10:size=1920x1080:rate=30 output.mp4

ffmpeg -i input.mp4 -c:v vp9 output_vp9.mp4
```

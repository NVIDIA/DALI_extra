#!/bin/bash
# Regenerates the files in this directory. Needs python3 (numpy, Pillow) and ffmpeg with libx264.
# Usage: ./generate.sh
set -e
cd "$(dirname "$0")"

# 1. The RGB pattern: the ground truth.
python3 make_pattern.py bars.png

# 2. An 8-frame 1080p H.264 clip with the pattern converted to YUV 4:2:0 using the BT.709 matrix,
#    limited (tv) range, and tagged as such in the stream (colour description in the VUI).
ffmpeg -y -loop 1 -framerate 25 -i bars.png -frames:v 8 \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv" \
  -c:v libx264 -preset veryslow -crf 10 -profile:v high -bf 0 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  bt709_limited_1080p.mp4

# 3. The same clip as VP9 (the CPU variant of the video reader decodes only VP8/VP9, not H.264).
ffmpeg -y -loop 1 -framerate 25 -i bars.png -frames:v 8 \
  -vf "scale=out_color_matrix=bt709:out_range=tv:flags=accurate_rnd+full_chroma_int,format=yuv420p,setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv" \
  -c:v libvpx-vp9 -crf 10 -b:v 0 \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv \
  bt709_limited_1080p_vp9.mp4

# 4. The references: the first frame of each clip decoded by ffmpeg, which converts to RGB using the
#    matrix and range tagged in the stream (BT.709, limited), with default settings. Saved as
#    (1080, 1920, 3) uint8 numpy arrays.
ffmpeg -y -i bt709_limited_1080p.mp4 -frames:v 1 -f rawvideo -pix_fmt rgb24 ref.rgb
python3 raw_to_npy.py ref.rgb bt709_limited_1080p_ref.npy 1920 1080
ffmpeg -y -c:v libvpx-vp9 -i bt709_limited_1080p_vp9.mp4 -frames:v 1 -f rawvideo -pix_fmt rgb24 ref.rgb
python3 raw_to_npy.py ref.rgb bt709_limited_1080p_vp9_ref.npy 1920 1080
rm ref.rgb

# Check the stream tags.
for f in bt709_limited_1080p.mp4 bt709_limited_1080p_vp9.mp4; do
  ffprobe -v error -select_streams v:0 \
    -show_entries stream=codec_name,profile,pix_fmt,width,height,nb_frames,color_space,color_range,color_primaries,color_transfer \
    -of default=nw=1 $f
done

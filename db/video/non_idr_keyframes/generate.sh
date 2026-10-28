#!/bin/bash
# Regenerates open_gop_h264.mp4. Needs ffmpeg (with libx264) and ffprobe.
# Usage: ./generate.sh
set -e
cd "$(dirname "$0")"

# 64 frames, 128x96, 25 fps, H.264 with a keyframe interval of 12, B-frames and open GOPs: only the
# first picture is an IDR picture, the later keyframes (frames 12, 24, 36, 48 and 60) are non-IDR
# I-pictures with a recovery point SEI, and the B-pictures that follow them in the decoding order
# precede them in the display order and refer to the previous GOP.
ffmpeg -y -f lavfi -i "testsrc2=size=128x96:rate=25" -frames:v 64 -pix_fmt yuv420p \
  -c:v libx264 -preset slow -crf 18 -profile:v high \
  -x264-params keyint=12:min-keyint=12:scenecut=0:bframes=3:open-gop=1 \
  open_gop_h264.mp4

# Check the stream: 64 frames, 6 packets flagged as keyframes, but only one IDR picture (NAL unit
# type 5) and 5 recovery points (SEI) at the other keyframes.
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,profile,pix_fmt,width,height,nb_frames \
  -of default=nw=1 open_gop_h264.mp4
echo "packets flagged as keyframes: $(ffprobe -v error -select_streams v:0 -show_entries packet=flags -of csv=p=0 open_gop_h264.mp4 | grep -c K)"
ffmpeg -hide_banner -i open_gop_h264.mp4 -c copy -bsf:v trace_headers -f null - 2>&1 > /dev/null \
  | grep -E "nal_unit_type +[01]+ = 5$|recovery_frame_cnt" | sed 's/^\[[^]]*\] //' | sort | uniq -c

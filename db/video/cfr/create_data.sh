#/bin/bash

mkdir -p frames_1
mkdir -p frames_2
mkdir -p frames_1_mpeg4
mkdir -p frames_2_mpeg4

# Create video 1
ffmpeg -f lavfi -i color=s=1280x720:d=3:r=60 -frames:v 50  -vf \
"geq=r='if(eq(trunc(N/10),0), 0,   if(eq(trunc(N/10),1), 0,   if(eq(trunc(N/10),2), 255, if(eq(trunc(N/10),3), 0,   255))))':\
     g='if(eq(trunc(N/10),0), 0,   if(eq(trunc(N/10),1), 255, if(eq(trunc(N/10),2), 0,   if(eq(trunc(N/10),3), 255, 0))))':\
     b='if(eq(trunc(N/10),0), 255, if(eq(trunc(N/10),1), 0,   if(eq(trunc(N/10),2), 0,   if(eq(trunc(N/10),3), 255, 255))))',\
drawtext=fontsize=480: fontcolor=white:\
font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" frames_1/%03d.png

# Convert frames to the video:
ffmpeg -pix_fmt yuv420p -framerate 60 -pattern_type glob -i 'frames_1/*.png' -c:v libx264 test_1.mp4

# List all files in the current folder and save their names, one per line, to frames_list.txt
pushd frames_1
ls -p | grep .png > frames_list.txt
popd

# Avi files are transcoded mp4 files:
ffmpeg -i test_1.mp4 -q:a 0 -q:v 0 test_1.avi

# HEVC files are transcoded .h264 files:
ffmpeg -i test_1.mp4 -c:v libx265 -vtag hvc1 test_1_hevc.mp4

# MPEG4 files are transcoded .h264 files:
ffmpeg -i test_1.mp4 -c:v mpeg4 test_1_mpeg4.mp4

# MPEG4 files are transcoded .h264 files and put in mkv container:
ffmpeg -i test_1.mp4 -c:v mpeg4 test_1_mpeg4.mkv

# Get the frames from mpeg4:
ffmpeg -i test_1_mpeg4.mp4 -sws_flags +full_chroma_int+accurate_rnd frames_1_mpeg4/%03d.png

# List all files in the current folder and save their names, one per line, to frames_list.txt
pushd frames_1_mpeg4
ls -p | grep .png > frames_list.txt
popd

# AV1 files are transcoded .h264 files:
ffmpeg -i test_1.mp4 -c:v libaom-av1 -aom-params lossless=1 test_1_av1.mp4

# RAW files are generated with:
ffmpeg -i test_1.mp4 -c:v libx264 -f rawvideo -bf 0 test_1.h264
ffmpeg -i test_1.mp4 -c:v libx265 -f rawvideo -bf 0 test_1.h265

# Create video 2
ffmpeg -f lavfi -i color=s=1280x720:d=3:r=60 -frames:v 60  -vf \
"geq=r='if(eq(trunc(N/10),0), 0,   if(eq(trunc(N/10),1), 0,   if(eq(trunc(N/10),2), 255, if(eq(trunc(N/10),3), 0,   if(eq(trunc(N/10),3), 255,   255)))))':\
     g='if(eq(trunc(N/10),0), 0,   if(eq(trunc(N/10),1), 255, if(eq(trunc(N/10),2), 0,   if(eq(trunc(N/10),3), 255, if(eq(trunc(N/10),3), 0,     255)))))':\
     b='if(eq(trunc(N/10),0), 255, if(eq(trunc(N/10),1), 0,   if(eq(trunc(N/10),2), 0,   if(eq(trunc(N/10),3), 255, if(eq(trunc(N/10),3), 255,   0)))))',\
drawtext=fontsize=480: fontcolor=black: font=monospace: x=(w-text_w)/2: y=(h-text_h)/2: r=60: text='%{frame_num}'" frames_2/%03d.png

# Convert frames to the video:
ffmpeg -framerate 60 -pattern_type glob -i 'frames_2/*.png' -c:v libx264 -pix_fmt yuv420p test_2.mp4

# List all files in the current folder and save their names, one per line, to frames_list.txt
pushd frames_2
ls -p | grep .png > frames_list.txt
popd

# Avi files are transcoded mp4 files:
ffmpeg -i test_2.mp4 -q:a 0 -q:v 0 test_2.avi

# HEVC files are transcoded .h264 files:
ffmpeg -i test_2.mp4 -c:v libx265 -vtag hvc1 test_2_hevc.mp4

# MPEG4 files are transcoded .h264 files:
ffmpeg -i test_2.mp4 -c:v mpeg4 test_2_mpeg4.mp4

# MPEG4 files are transcoded .h264 files and put in mkv container:
ffmpeg -i test_2.mp4 -c:v mpeg4 test_2_mpeg4.mkv

# Get the frames from mpeg4:
ffmpeg -i test_2_mpeg4.mp4 -sws_flags +full_chroma_int+accurate_rnd frames_2_mpeg4/%03d.png

# List all files in the current folder and save their names, one per line, to frames_list.txt
pushd frames_2_mpeg4
ls -p | grep .png > frames_list.txt
popd

# AV1 files are transcoded .h264 files:
ffmpeg -i test_2.mp4 -c:v libaom-av1 -aom-params lossless=1 test_2_av1.mp4

# RAW files are generated with:
ffmpeg -i test_2.mp4 -c:v libx264 -f rawvideo -bf 0 test_2.h264
ffmpeg -i test_2.mp4 -c:v libx265 -f rawvideo -bf 0 test_2.h265

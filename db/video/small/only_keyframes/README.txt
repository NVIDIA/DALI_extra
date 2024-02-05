Each frame in those videos is a keyframe, which makes seeking (and index
building) faster. Generated from videos in ../ with:

ffmpeg -i small$i.mp4 -keyint_min 1 -g 1 only_keyframes/small$i.mp4

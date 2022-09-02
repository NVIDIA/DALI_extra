#!/bin/bash
set -xe

CAT="cat-111793_640"
ORIG_CAT="$DALI_EXTRA_PATH/db/single/tiff/0/$CAT.tiff"

convert $ORIG_CAT -define tiff:tile-geometry=16x48 -compress lzw ${CAT}_tiled_16x48.tiff

convert $ORIG_CAT -define tiff:tile-geometry=1024x1024 -compress lzw ${CAT}_tiled_1024x1024.tiff

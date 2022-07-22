#!/bin/bash

# Script used to create all possible rotations encoded with EXIF

FILE="$1"
if [ ! -f "$FILE" ]; then
	echo "File '$FILE' does not exist."
	exit 0
fi

PREF="${FILE%.*}"

NAMES=( \
	"horizontal" \
	"mirror_horizontal" \
	"rotate_180" \
	"mirror_vertical" \
	"mirror_horizontal_rotate_270_cw" \
	"rotate_90_cw" \
	"mirror_horizontal_rotate_90_cw" \
	"rotate_270_cw" \
)

for ((i=1; i<=8; i++)); do
	CURRENT="${PREF}_${NAMES[i-1]}.webp"
	cp "$FILE" "$CURRENT"
	exiv2 -k -M"set Exif.Image.Orientation Short $i" "$CURRENT"
done

mv $FILE "${PREF}_original.webp"

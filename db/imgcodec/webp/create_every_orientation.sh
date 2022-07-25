#!/bin/bash

# Copyright (c) 2022, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script used to create all possible rotations encoded with EXIF
# Usage: ./create_every_possible_rotation filename

FILE="$1"
if [ ! -f "$FILE" ]; then
	echo "File '$FILE' does not exist."
	exit 0
fi

PREFIX="${FILE%.*}"
EXTENSION="${FILE#$PREFIX.}"

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
	CURRENT="${PREFIX}_${NAMES[i-1]}.${EXTENSION}"
	cp "$FILE" "$CURRENT"
	exiv2 -k -M"set Exif.Image.Orientation Short $i" "$CURRENT"
done

mv $FILE "${PREFIX}_original.${EXTENSION}"

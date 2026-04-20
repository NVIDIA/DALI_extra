# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

DALI_extra is a **data-only** repository containing sample datasets used by NVIDIA DALI's test suite. It has no build system or runnable code.

Large binary files (`.mp4`, `.avi`, `.mkv`, `.tar`, LMDB files, TFRecord files, etc.) are stored via **Git LFS**. Git LFS must be installed before cloning or the large files will be stubs.

```bash
# Requires Git LFS:
git lfs install
git clone https://github.com/NVIDIA/DALI_extra.git
```

## Usage in DALI tests

Set the `DALI_EXTRA_PATH` environment variable to point to this repository's root before running DALI tests:

```bash
export DALI_EXTRA_PATH=/path/to/DALI_extra
```

## Contributing data

Before adding new files:
- Verify no existing dataset can be used instead.
- Ensure data contains no personal information (no identifiable faces, license plates), no prominent trademarks, and no inappropriate content.
- Print, sign, and send `NVIDIA_CLA_v1.0.1.docx` to Dali-Team@nvidia.com before the contribution is accepted.

## Dataset structure

All datasets live under `db/`. Notable subdirectories: `single/` (individual images), `video/`, `audio/`, `lmdb/`, `tfrecord/`, `coco/`, `MNIST/`, `sequence/`, `imgcodec/`, `webdataset/`.

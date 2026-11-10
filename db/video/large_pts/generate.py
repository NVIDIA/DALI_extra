#!/usr/bin/env python3
"""Regenerates h264_large_pts.ts and checks it.

Needs Python 3 and PyAV 14 or newer (``pip install "av>=14"``).

The clip holds the first 65 packets in the decoding order (frames 0-64) of
../sintel/video_files/sintel_trailer-720p_0.mp4, copied to MPEG-TS without re-encoding: the slices
are unchanged, and the muxer adds an access unit delimiter to every packet and the SPS and PPS
before the IDR picture. The timestamps all move 30000 s later, so that every pts and dts is above
2^31 in the 90 kHz time base of MPEG-TS.

Usage: python3 generate.py [--src SINTEL_MP4] [--out OUT_TS]
"""
import argparse
import os
import sys
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, '..', 'sintel', 'video_files', 'sintel_trailer-720p_0.mp4')
DEFAULT_OUT = os.path.join(HERE, 'h264_large_pts.ts')
NUM_FRAMES = 65         # the first 65 packets in the decoding order are exactly frames 0-64
STEP = 512              # frame duration in the time base of the source (1/12288 s), 24 fps
OFFSET_S = 30000        # seconds added to every timestamp
TS_TIME_BASE = Fraction(1, 90000)


def read_source(path):
    with open(path, 'rb') as f:
        if f.read(7) == b'version':
            sys.exit(f'{path} is a Git LFS pointer, run "git lfs pull" or pass --src')
    src = av.open(path)
    st = src.streams.video[0]
    pkts = []
    for p in src.demux(st):
        if p.size == 0:
            continue
        pkts.append(dict(data=bytes(p), pts=p.pts, dts=p.dts, key=p.is_keyframe))
        if len(pkts) == NUM_FRAMES:
            break
    assert sorted(e['pts'] for e in pkts) == [f * STEP for f in range(NUM_FRAMES)]
    return src, st, pkts


def write(out_path, src_stream, pkts, offset):
    out = av.open(out_path, 'w', format='mpegts')
    ost = out.add_stream_from_template(src_stream)
    for e in pkts:
        p = av.Packet(e['data'])
        p.stream = ost
        p.time_base = src_stream.time_base
        p.pts = e['pts'] + offset
        p.dts = e['dts'] + offset
        p.duration = STEP
        if e['key']:
            p.is_keyframe = True
        out.mux(p)
    out.close()


def decode(path, count=None):
    c = av.open(path)
    frames = []
    for f in c.decode(video=0):
        frames.append(f.to_ndarray(format='yuv420p'))
        if count is not None and len(frames) == count:
            break
    c.close()
    return frames


def verify(out_path, src_path, pkts, offset, src_tb):
    c = av.open(out_path)
    st = c.streams.video[0]
    tb = st.time_base
    demuxed = [p for p in c.demux(st) if p.size]
    rows = [(p.pts, p.dts) for p in demuxed]
    keys = [p.is_keyframe for p in demuxed]
    c.close()
    assert tb == TS_TIME_BASE, tb
    assert len(rows) == NUM_FRAMES, f'{len(rows)} packets'
    dts = [r[1] for r in rows]
    assert all(b > a for a, b in zip(dts, dts[1:])), 'dts not strictly increasing'
    assert all(pts >= dts for pts, dts in rows), 'pts < dts'
    # the packets keep the decoding order and the timestamps of the source, moved by the offset
    for e, (pts, dts) in zip(pkts, rows):
        assert Fraction(pts) * tb == Fraction(e['pts'] + offset) * src_tb
        assert Fraction(dts) * tb == Fraction(e['dts'] + offset) * src_tb
    assert min(min(r) for r in rows) > 2**31, 'a timestamp fits in a signed 32-bit integer'
    assert max(max(r) for r in rows) < 2**33, 'a timestamp wraps around in MPEG-TS'
    assert keys == [True] + [False] * (NUM_FRAMES - 1), 'not only the first packet is a keyframe'

    frames = decode(out_path)
    assert len(frames) == NUM_FRAMES, f'{len(frames)} frames decoded'
    ref = decode(src_path, NUM_FRAMES)
    assert len(ref) == NUM_FRAMES, f'{len(ref)} frames decoded from the source'
    assert all((a == b).all() for a, b in zip(frames, ref)), 'frames differ from the source'
    return dict(time_base=tb, size=(frames[0].shape[1], frames[0].shape[0] * 2 // 3),
                first_pts=min(r[0] for r in rows), first_dts=min(r[1] for r in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--src', default=DEFAULT_SRC, help='sintel_trailer-720p_0.mp4')
    parser.add_argument('--out', default=DEFAULT_OUT, help='output MPEG-TS file')
    args = parser.parse_args()

    src, src_stream, pkts = read_source(args.src)
    src_tb = src_stream.time_base
    offset = OFFSET_S / src_tb
    assert offset.denominator == 1
    offset = int(offset)
    write(args.out, src_stream, pkts, offset)
    src.close()
    info = verify(args.out, args.src, pkts, offset, src_tb)
    print(f'{args.out}: {NUM_FRAMES} frames, {info["size"][0]}x{info["size"][1]}, '
          f'time base {info["time_base"]}, first pts {info["first_pts"]}, '
          f'first dts {info["first_dts"]}')


if __name__ == '__main__':
    main()

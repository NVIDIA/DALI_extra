#!/usr/bin/env python3
"""Regenerates the MPEG-TS copies of the CFR test clips and checks them.

Needs Python 3 and PyAV (``pip install av``).

Each clip is a clip of ../cfr copied to MPEG-TS without re-encoding (the H.264/HEVC packets are
converted to Annex B, as MPEG-TS stores them). Only the timestamps change: they all move by the
same amount, so that the first dts is 0.

Usage: python3 generate.py [--src-dir CFR_DIR] [--out-dir OUT_DIR]
"""
import argparse
import os
import sys
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC_DIR = os.path.join(HERE, '..', 'cfr')
# output name -> source name in ../cfr
CLIPS = {
    'test_1.ts': 'test_1.mp4',
    'test_2_hevc.ts': 'test_2_hevc.mp4',
}
TS_TIME_BASE = Fraction(1, 90000)


def read_source(path):
    with open(path, 'rb') as f:
        if f.read(7) == b'version':
            sys.exit(f'{path} is a Git LFS pointer, run "git lfs pull" or pass --src-dir')
    src = av.open(path)
    st = src.streams.video[0]
    pkts = [dict(data=bytes(p), pts=p.pts, dts=p.dts, key=p.is_keyframe, duration=p.duration)
            for p in src.demux(st) if p.size]
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
        p.duration = e['duration']
        if e['key']:
            p.is_keyframe = True
        out.mux(p)
    out.close()


def decode(path):
    c = av.open(path)
    frames = [f.to_ndarray(format='yuv420p') for f in c.decode(video=0)]
    c.close()
    return frames


def verify(out_path, src_path, pkts, offset, src_tb):
    c = av.open(out_path)
    st = c.streams.video[0]
    tb = st.time_base
    codec = st.codec_context.name
    rows = [(p.pts, p.dts, p.is_keyframe, bytes(p)) for p in c.demux(st) if p.size]
    c.close()
    assert tb == TS_TIME_BASE, tb
    assert len(rows) == len(pkts), f'{len(rows)} packets, {len(pkts)} in the source'
    dts = [r[1] for r in rows]
    assert dts[0] == 0, f'first dts {dts[0]}'
    assert all(b > a for a, b in zip(dts, dts[1:])), 'dts not strictly increasing'
    assert all(d.startswith((b'\0\0\1', b'\0\0\0\1')) for _, _, _, d in rows), 'not Annex B'
    # the packets keep the decoding order and the timestamps of the source, moved by the offset
    for e, (pts, dts, _, _) in zip(pkts, rows):
        assert Fraction(pts) * tb == Fraction(e['pts'] + offset) * src_tb
        assert Fraction(dts) * tb == Fraction(e['dts'] + offset) * src_tb
    keys = [i for i, r in enumerate(rows) if r[2]]
    assert keys == [i for i, e in enumerate(pkts) if e['key']], 'not the key packets of the source'
    reordered = sum(1 for a, b in zip(rows, rows[1:]) if b[0] < a[0])
    assert reordered > 0, 'no reordered frames'

    frames = decode(out_path)
    ref = decode(src_path)
    assert len(frames) == len(ref) == len(pkts), f'{len(frames)} frames, {len(ref)} in the source'
    assert all((a == b).all() for a, b in zip(frames, ref)), 'frames differ from the source'
    return dict(codec=codec, frames=len(frames), size=(frames[0].shape[1],
                frames[0].shape[0] * 2 // 3), keys=keys, reordered=reordered,
                first_pts=min(r[0] for r in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--src-dir', default=DEFAULT_SRC_DIR, help='directory of the CFR clips')
    parser.add_argument('--out-dir', default=HERE, help='output directory')
    args = parser.parse_args()

    for out_name, src_name in CLIPS.items():
        src_path = os.path.join(args.src_dir, src_name)
        out_path = os.path.join(args.out_dir, out_name)
        src, src_stream, pkts = read_source(src_path)
        src_tb = src_stream.time_base
        offset = -min(e['dts'] for e in pkts)
        write(out_path, src_stream, pkts, offset)
        src.close()
        info = verify(out_path, src_path, pkts, offset, src_tb)
        print(f'{out_path}: {info["codec"]}, {info["frames"]} frames, '
              f'{info["size"][0]}x{info["size"][1]}, first pts {info["first_pts"]}, key packets '
              f'(decoding order) {info["keys"]}, {info["reordered"]} packets with a pts lower '
              f'than the one before')


if __name__ == '__main__':
    main()

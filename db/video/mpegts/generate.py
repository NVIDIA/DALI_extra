#!/usr/bin/env python3
"""Regenerates the MPEG-TS copies of test clips and checks them.

Needs Python 3 and PyAV 14 or newer (``pip install "av>=14"``).

Each clip is a clip of ../cfr or ../non_idr_keyframes copied to MPEG-TS without re-encoding, from
its first packet or from a later one. The slices are unchanged: the muxer converts the H.264/HEVC
packets to Annex B, as MPEG-TS stores them, adds an access unit delimiter to every packet, and adds
the parameter sets of the source (for HEVC with the SEI stored with them) before every IDR (H.264)
or IRAP (HEVC) picture. The timestamps all move by the same amount, so that the first dts is 0.

Usage: python3 generate.py [--video-dir VIDEO_DIR] [--out-dir OUT_DIR]
"""
import argparse
import os
import sys
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VIDEO_DIR = os.path.join(HERE, '..')
# output name -> (source, relative to the video directory; packets of the source left out)
CLIPS = {
    'test_1.ts': ('cfr/test_1.mp4', 0),
    'test_2_hevc.ts': ('cfr/test_2_hevc.mp4', 0),
    'open_gop_h264.ts': ('non_idr_keyframes/open_gop_h264.mp4', 0),
    # starts in the middle of a GOP, two packets before the next keyframe
    'test_1_mid_gop.ts': ('cfr/test_1.mp4', 8),
}
TS_TIME_BASE = Fraction(1, 90000)


def read_source(path, skip):
    with open(path, 'rb') as f:
        if f.read(7) == b'version':
            sys.exit(f'{path} is a Git LFS pointer, run "git lfs pull" or pass --video-dir')
    src = av.open(path)
    st = src.streams.video[0]
    pkts = [dict(data=bytes(p), pts=p.pts, dts=p.dts, key=p.is_keyframe, duration=p.duration)
            for p in src.demux(st) if p.size]
    return src, st, pkts[skip:]


def write(out_path, src_stream, pkts, offset):
    out = av.open(out_path, 'w', format='mpegts')
    ost = out.add_stream_from_template(src_stream)
    if ost.codec_context.name == 'libx265':
        # add_stream_from_template gives the stream an encoder, opened on the first mux although
        # it encodes nothing: keep x265 from printing its banner and "encoded 0 frames"
        ost.codec_context.options = {'x265-params': 'log-level=none'}
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


def nal_types(data, codec):
    """The NAL unit types of an Annex B packet."""
    types = []
    i = 0
    while i + 3 < len(data):
        if data[i] == 0 and data[i + 1] == 0 and data[i + 2] == 1:
            header = data[i + 3]
            types.append(header & 0x1f if codec == 'h264' else (header >> 1) & 0x3f)
            i += 3
        else:
            i += 1
    return types


def verify(out_path, src_path, pkts, offset, src_tb, skip):
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
    reordered = sum(1 for a, b in zip(rows, rows[1:]) if b[0] < a[0])
    assert reordered > 0, 'no reordered frames'
    # The key flags come from FFmpeg's parser in MPEG-TS: the pictures that decoding can start from
    # (IDR, IRAP) are flagged, and so can be others (e.g. H.264 pictures after a recovery point SEI)
    keyframe_types = {5} if codec == 'h264' else set(range(16, 22))
    keys = [i for i, r in enumerate(rows) if r[2]]
    keyframes = [i for i, r in enumerate(rows) if keyframe_types & set(nal_types(r[3], codec))]
    assert keys == [i for i, e in enumerate(pkts) if e['key']], 'key flags differ from the source'
    assert set(keyframes) <= set(keys), 'a keyframe is not flagged'

    if skip == 0:
        frames = decode(out_path)
        ref = decode(src_path)
        assert len(frames) == len(ref) == len(pkts), (
            f'{len(frames)} frames, {len(ref)} in the source')
        assert all((a == b).all() for a, b in zip(frames, ref)), 'frames differ from the source'
    else:
        # The first packets refer to pictures left out: only the index of this file is of use
        assert keyframes and keyframes[0] > 1, 'not two packets before the first keyframe'
        assert rows[1][0] < rows[0][0], 'the first packet is not shown after the second one'
    return dict(codec=codec, packets=len(rows), keys=keys, keyframes=keyframes,
                reordered=reordered, first_pts=min(r[0] for r in rows))


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--video-dir', default=DEFAULT_VIDEO_DIR,
                        help='the db/video directory with the source clips')
    parser.add_argument('--out-dir', default=HERE, help='output directory')
    args = parser.parse_args()

    for out_name, (src_name, skip) in CLIPS.items():
        src_path = os.path.join(args.video_dir, src_name)
        out_path = os.path.join(args.out_dir, out_name)
        src, src_stream, pkts = read_source(src_path, skip)
        src_tb = src_stream.time_base
        offset = -min(e['dts'] for e in pkts)
        write(out_path, src_stream, pkts, offset)
        src.close()
        info = verify(out_path, src_path, pkts, offset, src_tb, skip)
        print(f'{out_path}: {info["codec"]}, {info["packets"]} packets, first pts '
              f'{info["first_pts"]}, key packets (decoding order) {info["keys"]}, of which '
              f'pictures that decoding can start from {info["keyframes"]}, {info["reordered"]} '
              f'packets with a pts lower than the one before')


if __name__ == '__main__':
    main()

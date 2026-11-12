#!/usr/bin/env python3
"""Regenerates the MPEG-TS clips of db/video and checks them.

Needs Python 3 and PyAV 14 or newer (``pip install "av>=14"``), and the source clips (``git lfs
pull``).

Each clip is a clip of ../cfr, ../non_idr_keyframes or ../sintel copied to MPEG-TS without
re-encoding, from its first packet or from a later one. The slices are unchanged: the muxer converts
the packets to Annex B, as MPEG-TS stores them, adds an access unit delimiter to every packet and
the parameter sets before every IDR (H.264) or IRAP (HEVC) picture. Only the timestamps differ, as
described in README.rst.

Usage: python3 generate.py [--video-dir VIDEO_DIR] [--out-dir OUT_DIR]
"""
import argparse
import itertools
import os
import sys
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
TS_TIME_BASE = Fraction(1, 90000)
SINTEL = 'sintel/video_files/sintel_trailer-720p_0.mp4'
SINTEL_FRAMES = 65  # the first 65 packets in the decoding order are exactly the frames 0-64
SINTEL_TIME_BASE = Fraction(1, 12288)
STEP = 512  # frame duration in the time base of the Sintel clip (24 fps)


def read_source(path, skip, count):
    with open(path, 'rb') as f:
        if f.read(7) == b'version':
            sys.exit(f'{path} is a Git LFS pointer, run "git lfs pull" or pass --video-dir')
    with av.open(path) as src:
        st = src.streams.video[0]
        pkts = [
            dict(data=bytes(p), pts=p.pts, dts=p.dts, key=p.is_keyframe, duration=p.duration)
            for p in src.demux(st)
            if p.size
        ]
        return st.time_base, bytes(st.codec_context.extradata), pkts[skip:][:count]


def ref_idc(data, len_size):
    """nal_ref_idc of the first slice of an H.264 packet with length-prefixed NAL units"""
    i = 0
    while i + len_size < len(data):
        header = data[i + len_size]
        if header & 0x1F in (1, 5):
            return header >> 5 & 3
        i += len_size + int.from_bytes(data[i : i + len_size], 'big')
    raise ValueError('no slice in the packet')


def same_timestamps(pkts, extradata):
    """The timestamps of the source, moved so that the first dts is 0"""
    offset = -min(e['dts'] for e in pkts)
    return [(e['pts'] + offset, e['dts'] + offset, e['duration']) for e in pkts]


def large_timestamps(pkts, extradata):
    """The timestamps of the source, 30000 s later: above 2^31 in the 90 kHz time base"""
    offset = 30000 * 12288
    stamps = [(e['pts'] + offset, e['dts'] + offset, STEP) for e in pkts]
    ticks = [Fraction(t) * SINTEL_TIME_BASE / TS_TIME_BASE for s in stamps for t in s[:2]]
    assert 2**31 < min(ticks) and max(ticks) < 2**33, 'not between 2^31 and 2^33'
    return stamps


def duplicate_timestamps(pkts, extradata):
    """Every non-reference picture takes the pts of the frame shown before it, every dts moves one
    frame earlier so that pts >= dts still holds, and all timestamps move 3 frames later so that
    dts >= 0"""
    assert extradata[0] == 1, 'expected avcC extradata'
    len_size = (extradata[4] & 3) + 1
    assert all(e['pts'] % STEP == 0 for e in pkts)
    frames = [e['pts'] // STEP for e in pkts]
    assert sorted(frames) == list(range(len(pkts)))
    nonref = {f for e, f in zip(pkts, frames) if ref_idc(e['data'], len_size) == 0}
    # the frame shown right before a non-reference picture is a reference one: the ties are pairs
    assert nonref and all(f - 1 not in nonref for f in nonref)
    shown = [(f - 1 if f in nonref else f) * STEP for f in frames]
    stamps = [(pts + 3 * STEP, e['dts'] - STEP + 3 * STEP, STEP) for pts, e in zip(shown, pkts)]
    assert len({s[0] for s in stamps}) == len(pkts) - len(nonref), 'not a pair for each one'
    return stamps


# output, relative to the video directory -> (source, packets of the source left out, number of
# packets, timestamps of the packets)
CLIPS = {
    'mpegts/test_1.ts': ('cfr/test_1.mp4', 0, None, same_timestamps),
    'mpegts/test_2_hevc.ts': ('cfr/test_2_hevc.mp4', 0, None, same_timestamps),
    'mpegts/open_gop_h264.ts': ('non_idr_keyframes/open_gop_h264.mp4', 0, None, same_timestamps),
    # starts in the middle of a GOP, two packets before the next keyframe
    'mpegts/test_1_mid_gop.ts': ('cfr/test_1.mp4', 8, None, same_timestamps),
    'duplicate_pts/h264_nonref_dup_pts.ts': (SINTEL, 0, SINTEL_FRAMES, duplicate_timestamps),
    'large_pts/h264_large_pts.ts': (SINTEL, 0, SINTEL_FRAMES, large_timestamps),
}


def write(out_path, src_path, skip, count, timestamps):
    src_tb, extradata, pkts = read_source(src_path, skip, count)
    stamps = timestamps(pkts, extradata)
    with av.open(src_path) as src, av.open(out_path, 'w', format='mpegts') as out:
        ost = out.add_stream_from_template(src.streams.video[0])
        if ost.codec_context.name == 'libx265':
            # the stream gets an encoder that encodes nothing: keep x265 from printing its banner
            ost.codec_context.options = {'x265-params': 'log-level=none'}
        for e, (pts, dts, duration) in zip(pkts, stamps):
            p = av.Packet(e['data'])
            p.stream = ost
            p.time_base = src_tb
            p.pts, p.dts, p.duration = pts, dts, duration
            if e['key']:
                p.is_keyframe = True
            out.mux(p)
    return src_tb, pkts, stamps


def decode(path, count=None):
    with av.open(path) as c:
        return [f.to_ndarray(format='yuv420p') for f in itertools.islice(c.decode(video=0), count)]


def verify(out_path, src_path, skip, src_tb, pkts, stamps):
    with av.open(out_path) as c:
        st = c.streams.video[0]
        assert st.time_base == TS_TIME_BASE, st.time_base
        rows = [(p.pts, p.dts, p.is_keyframe, bytes(p)) for p in c.demux(st) if p.size]
    assert len(rows) == len(pkts), f'{len(rows)} packets, {len(pkts)} in the source'
    dts = [r[1] for r in rows]
    assert all(b > a for a, b in zip(dts, dts[1:])), 'dts not strictly increasing'
    assert all(pts >= dts for pts, dts, _, _ in rows), 'pts < dts'
    assert all(d.startswith((b'\0\0\1', b'\0\0\0\1')) for _, _, _, d in rows), 'not Annex B'
    for (pts, dts, _, _), (want_pts, want_dts, _) in zip(rows, stamps):
        assert Fraction(pts) * TS_TIME_BASE == Fraction(want_pts) * src_tb, 'wrong pts'
        assert Fraction(dts) * TS_TIME_BASE == Fraction(want_dts) * src_tb, 'wrong dts'
    keys = [i for i, r in enumerate(rows) if r[2]]
    assert keys == [i for i, e in enumerate(pkts) if e['key']], 'key flags differ from the source'
    assert any(b[0] < a[0] for a, b in zip(rows, rows[1:])), 'no reordered frames'
    if skip:
        # The first packets refer to pictures left out: only the index of this file is of use
        assert keys[0] == 2 and rows[1][0] < rows[0][0], 'not a start in the middle of a GOP'
    else:
        frames = decode(out_path)
        ref = decode(src_path, len(pkts))
        assert len(frames) == len(ref) == len(pkts), f'{len(frames)} frames, {len(ref)} wanted'
        assert all((a == b).all() for a, b in zip(frames, ref)), 'frames differ from the source'
    return len(rows), keys


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument(
        '--video-dir', default=os.path.join(HERE, '..'), help='the db/video directory'
    )
    parser.add_argument('--out-dir', default=None, help='output directory (default: video-dir)')
    args = parser.parse_args()

    for name, (src_name, skip, count, timestamps) in CLIPS.items():
        src_path = os.path.join(args.video_dir, src_name)
        out_path = os.path.join(args.out_dir or args.video_dir, name)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        src_tb, pkts, stamps = write(out_path, src_path, skip, count, timestamps)
        packets, keys = verify(out_path, src_path, skip, src_tb, pkts, stamps)
        print(f'{out_path}: {packets} packets, key packets {keys}')


if __name__ == '__main__':
    main()

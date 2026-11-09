#!/usr/bin/env python3
"""Regenerates h264_nonref_dup_pts.ts and checks its structure.

Needs Python 3 and PyAV (``pip install av``).

The clip holds the first 65 packets in the decoding order (frames 0-64) of
../sintel/video_files/sintel_trailer-720p_0.mp4, copied to MPEG-TS without re-encoding. Only the
timestamps change:

- every H.264 non-reference picture (nal_ref_idc 0) takes the pts of the frame shown right before
  it,
- every dts moves one frame earlier, so that pts >= dts still holds,
- all timestamps move 3 frames later, so that dts >= 0.

Usage: python3 generate.py [--src SINTEL_MP4] [--out OUT_TS]
"""
import argparse
import os
import sys
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(HERE, '..', 'sintel', 'video_files', 'sintel_trailer-720p_0.mp4')
DEFAULT_OUT = os.path.join(HERE, 'h264_nonref_dup_pts.ts')
NUM_FRAMES = 65    # the first 65 packets in the decoding order are exactly frames 0-64
STEP = 512         # frame duration in the time base of the source (1/12288 s), 24 fps
OFFSET = 3 * STEP  # keeps every dts >= 0 after moving it one frame earlier


def nal_headers(data, len_size):
    """First bytes of the NAL units in a packet: length-prefixed if len_size is set, else Annex
    B."""
    out = []
    if len_size is None:
        i = 0
        while i + 3 < len(data):
            if data[i] == 0 and data[i + 1] == 0 and data[i + 2] == 1:
                out.append(data[i + 3])
                i += 3
            else:
                i += 1
        return out
    i = 0
    while i + len_size <= len(data):
        n = int.from_bytes(data[i:i + len_size], 'big')
        i += len_size
        if n == 0 or i + n > len(data):
            break
        out.append(data[i])
        i += n
    return out


def slice_ref_idc(data, len_size):
    """nal_ref_idc of the first slice NAL unit (type 1 or 5) of a packet."""
    for h in nal_headers(data, len_size):
        if h & 0x1f in (1, 5):
            return (h >> 5) & 3
    raise ValueError('no slice NAL unit in the packet')


def read_source(path):
    with open(path, 'rb') as f:
        if f.read(7) == b'version':
            sys.exit(f'{path} is a Git LFS pointer, run "git lfs pull" or pass --src')
    src = av.open(path)
    st = src.streams.video[0]
    extradata = st.codec_context.extradata
    assert extradata[0] == 1, 'expected avcC extradata'
    len_size = (extradata[4] & 3) + 1
    pkts = []
    for p in src.demux(st):
        if p.size == 0:
            continue
        data = bytes(p)
        pkts.append(dict(data=data, pts=p.pts, dts=p.dts, key=p.is_keyframe,
                         ref=slice_ref_idc(data, len_size)))
        if len(pkts) == NUM_FRAMES:
            break
    order = sorted(range(NUM_FRAMES), key=lambda i: pkts[i]['pts'])
    assert [pkts[i]['pts'] for i in order] == [f * STEP for f in range(NUM_FRAMES)]
    for frame, i in enumerate(order):
        pkts[i]['frame'] = frame
    return src, st, pkts


def write(out_path, src_stream, pkts, nonref):
    out = av.open(out_path, 'w', format='mpegts')
    ost = out.add_stream_from_template(src_stream)
    for e in pkts:
        frame = e['frame'] - 1 if e['frame'] in nonref else e['frame']
        pts = frame * STEP
        dts = e['dts'] - STEP
        assert pts >= dts
        p = av.Packet(e['data'])
        p.stream = ost
        p.time_base = src_stream.time_base
        p.pts = pts + OFFSET
        p.dts = dts + OFFSET
        p.duration = STEP
        if e['key']:
            p.is_keyframe = True
        out.mux(p)
    out.close()


def verify(out_path, pkts, nonref, src_tb):
    c = av.open(out_path)
    st = c.streams.video[0]
    tb = st.time_base
    rows = [(p.pts, p.dts, bytes(p)) for p in c.demux(st) if p.size]
    c.close()
    assert len(rows) == NUM_FRAMES, f'{len(rows)} packets'
    dts = [r[1] for r in rows]
    assert dts[0] >= 0 and all(b > a for a, b in zip(dts, dts[1:])), 'dts not strictly increasing'
    assert all(pts >= dts for pts, dts, _ in rows), 'pts < dts'
    assert all(d.startswith((b'\0\0\1', b'\0\0\0\1')) for _, _, d in rows), 'not Annex B'
    # the packets keep the decoding order of the source
    assert {e['frame'] for e, r in zip(pkts, rows) if slice_ref_idc(r[2], None) == 0} == nonref
    for e, (pts, _, _) in zip(pkts, rows):
        frame = e['frame'] - 1 if e['frame'] in nonref else e['frame']
        assert Fraction(pts) * tb == Fraction(frame * STEP + OFFSET) * src_tb
    by_pts = {}
    for e, (pts, _, _) in zip(pkts, rows):
        by_pts.setdefault(pts, []).append(e['frame'])
    ties = sorted(tuple(sorted(v)) for v in by_pts.values() if len(v) > 1)
    assert ties == [(f - 1, f) for f in sorted(nonref)], ties

    c = av.open(out_path)
    frames = list(c.decode(video=0))
    c.close()
    assert len(frames) == NUM_FRAMES, f'{len(frames)} frames decoded'
    first_nal = rows[0][2][4] & 0x1f if rows[0][2].startswith(b'\0\0\0\1') else rows[0][2][3] & 0x1f
    return dict(time_base=tb, size=(frames[0].width, frames[0].height),
                first_pts=min(r[0] for r in rows), ties=ties, first_nal_type=first_nal)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--src', default=DEFAULT_SRC, help='sintel_trailer-720p_0.mp4')
    parser.add_argument('--out', default=DEFAULT_OUT, help='output MPEG-TS file')
    args = parser.parse_args()

    src, src_stream, pkts = read_source(args.src)
    nonref = {e['frame'] for e in pkts if e['ref'] == 0}
    # a frame shown right before a non-reference picture is a reference picture, so ties are pairs
    assert all(f - 1 not in nonref for f in nonref)
    write(args.out, src_stream, pkts, nonref)
    src_tb = src_stream.time_base
    src.close()
    info = verify(args.out, pkts, nonref, src_tb)
    print(f'{args.out}: {NUM_FRAMES} frames, {info["size"][0]}x{info["size"][1]}, '
          f'time base {info["time_base"]}, first pts {info["first_pts"]}, '
          f'first NAL unit type {info["first_nal_type"]}')
    print('non-reference frames:', sorted(nonref))
    print(f'{len(info["ties"])} frame pairs sharing a pts:', info['ties'])


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Regenerates h264_nonref_dup_pts.ts and checks its structure.

Needs Python 3 and PyAV 14 or newer (``pip install "av>=14"``).

The clip holds the first 65 packets in the decoding order (frames 0-64) of
../sintel/video_files/sintel_trailer-720p_0.mp4, copied to MPEG-TS without re-encoding: the slices
are unchanged, and the muxer adds an access unit delimiter to every packet and the SPS and PPS
before the IDR picture. The timestamps change:

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
MUXER_NAL_TYPES = (7, 8, 9)  # SPS, PPS and access unit delimiter, added by the MPEG-TS muxer


def nal_units(data, len_size):
    """The NAL units of a packet: length-prefixed if len_size is set, else Annex B."""
    if len_size is None:
        starts = []
        i = 0
        while i + 3 < len(data):
            if data[i] == 0 and data[i + 1] == 0 and data[i + 2] == 1:
                starts.append(i + 3)
                i += 3
            else:
                i += 1
        ends = [s - 3 for s in starts[1:]] + [len(data)]
        # a NAL unit does not end with a zero byte: the zero byte of a 4-byte start code is not part
        # of the NAL unit before it
        return [data[s:e].rstrip(b'\0') for s, e in zip(starts, ends)]
    out = []
    i = 0
    while i + len_size <= len(data):
        n = int.from_bytes(data[i:i + len_size], 'big')
        i += len_size
        if n == 0 or i + n > len(data):
            break
        out.append(data[i:i + n])
        i += n
    return out


def nal_type(nal):
    return nal[0] & 0x1f


def slice_ref_idc(nals):
    """nal_ref_idc of the first slice NAL unit (type 1 or 5) of a packet."""
    for n in nals:
        if nal_type(n) in (1, 5):
            return (n[0] >> 5) & 3
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
        nals = nal_units(data, len_size)
        pkts.append(dict(data=data, pts=p.pts, dts=p.dts, key=p.is_keyframe, nals=nals,
                         ref=slice_ref_idc(nals)))
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


def decode(path, count=None):
    c = av.open(path)
    frames = []
    for f in c.decode(video=0):
        frames.append(f.to_ndarray(format='yuv420p'))
        if count is not None and len(frames) == count:
            break
    c.close()
    return frames


def verify(out_path, src_path, pkts, nonref, src_tb):
    c = av.open(out_path)
    st = c.streams.video[0]
    tb = st.time_base
    rows = [(p.pts, p.dts, bytes(p), p.is_keyframe) for p in c.demux(st) if p.size]
    c.close()
    assert len(rows) == NUM_FRAMES, f'{len(rows)} packets'
    dts = [r[1] for r in rows]
    assert dts[0] >= 0 and all(b > a for a, b in zip(dts, dts[1:])), 'dts not strictly increasing'
    assert all(pts >= dts for pts, dts, _, _ in rows), 'pts < dts'
    assert all(d.startswith((b'\0\0\1', b'\0\0\0\1')) for _, _, d, _ in rows), 'not Annex B'
    nals = [nal_units(d, None) for _, _, d, _ in rows]
    types = [[nal_type(n) for n in u] for u in nals]
    first_only = [True] + [False] * (NUM_FRAMES - 1)
    assert all(t[0] == 9 for t in types), 'a packet does not start with an access unit delimiter'
    assert [5 in t for t in types] == first_only, 'not only the first picture is an IDR picture'
    assert [r[3] for r in rows] == first_only, 'not only the first packet is a keyframe'
    # the packets are those of the source, in its decoding order: the same NAL units, apart from
    # those that the muxer adds
    for i, (e, u) in enumerate(zip(pkts, nals)):
        out_nals = [n for n in u if nal_type(n) not in MUXER_NAL_TYPES]
        src_nals = [n for n in e['nals'] if nal_type(n) not in MUXER_NAL_TYPES]
        assert out_nals == src_nals, f'packet {i} differs from the source'
    for e, (pts, _, _, _) in zip(pkts, rows):
        frame = e['frame'] - 1 if e['frame'] in nonref else e['frame']
        assert Fraction(pts) * tb == Fraction(frame * STEP + OFFSET) * src_tb
    by_pts = {}
    for e, (pts, _, _, _) in zip(pkts, rows):
        by_pts.setdefault(pts, []).append(e['frame'])
    ties = sorted(tuple(sorted(v)) for v in by_pts.values() if len(v) > 1)
    assert ties == [(f - 1, f) for f in sorted(nonref)], ties

    frames = decode(out_path)
    assert len(frames) == NUM_FRAMES, f'{len(frames)} frames decoded'
    ref = decode(src_path, NUM_FRAMES)
    assert len(ref) == NUM_FRAMES, f'{len(ref)} frames decoded from the source'
    assert all((a == b).all() for a, b in zip(frames, ref)), 'frames differ from the source'
    return dict(time_base=tb, size=(frames[0].shape[1], frames[0].shape[0] * 2 // 3),
                first_pts=min(r[0] for r in rows), ties=ties, first_nal_type=types[0][0])


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
    info = verify(args.out, args.src, pkts, nonref, src_tb)
    print(f'{args.out}: {NUM_FRAMES} frames, {info["size"][0]}x{info["size"][1]}, '
          f'time base {info["time_base"]}, first pts {info["first_pts"]}, '
          f'first NAL unit type {info["first_nal_type"]}')
    print('non-reference frames:', sorted(nonref))
    print(f'{len(info["ties"])} frame pairs sharing a pts:', info['ties'])


if __name__ == '__main__':
    main()

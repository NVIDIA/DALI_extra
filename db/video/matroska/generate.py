#!/usr/bin/env python3
"""Regenerates the Matroska copy of cfr/test_1.mp4 and checks it.

Needs Python 3 and PyAV 14 or newer (``pip install "av>=14"``), to read the source and to check the
copy. The Matroska file itself is written here, not by FFmpeg's muxer, so it does not depend on the
FFmpeg build.

The packets of the source (H.264 with B-frames) are copied without re-encoding, in the decoding
order: the CodecPrivate of the track is the avcC of the source, and each packet is a SimpleBlock
with the key flag of the source and its pts in milliseconds (Matroska stores no dts). Each keyframe
starts a cluster, and the Cues at the end of the file give the position of each keyframe, which a
SeekHead at the start points to, as in a file of FFmpeg's Matroska muxer.

Usage: python3 generate.py [--video-dir VIDEO_DIR] [--out-dir OUT_DIR]
"""

import argparse
import math
import os
import struct
import sys
from fractions import Fraction

import av

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VIDEO_DIR = os.path.join(HERE, '..')
# output name -> source, relative to the video directory
CLIPS = {
    'test_1.mkv': 'cfr/test_1.mp4',
}
APP = 'DALI_extra db/video/matroska/generate.py'
TIMESTAMP_SCALE_NS = 1000000  # the block timestamps are in ms
ELEMENT_IDS = {
    'EBML': 0x1A45DFA3,
    'EBMLVersion': 0x4286,
    'EBMLReadVersion': 0x42F7,
    'EBMLMaxIDLength': 0x42F2,
    'EBMLMaxSizeLength': 0x42F3,
    'DocType': 0x4282,
    'DocTypeVersion': 0x4287,
    'DocTypeReadVersion': 0x4285,
    'Segment': 0x18538067,
    'SeekHead': 0x114D9B74,
    'Seek': 0x4DBB,
    'SeekID': 0x53AB,
    'SeekPosition': 0x53AC,
    'Info': 0x1549A966,
    'TimestampScale': 0x2AD7B1,
    'Duration': 0x4489,
    'MuxingApp': 0x4D80,
    'WritingApp': 0x5741,
    'Tracks': 0x1654AE6B,
    'TrackEntry': 0xAE,
    'TrackNumber': 0xD7,
    'TrackUID': 0x73C5,
    'TrackType': 0x83,
    'FlagLacing': 0x9C,
    'Language': 0x22B59C,
    'CodecID': 0x86,
    'CodecPrivate': 0x63A2,
    'DefaultDuration': 0x23E383,
    'Video': 0xE0,
    'PixelWidth': 0xB0,
    'PixelHeight': 0xBA,
    'Cluster': 0x1F43B675,
    'Timestamp': 0xE7,
    'SimpleBlock': 0xA3,
    'Cues': 0x1C53BB6B,
    'CuePoint': 0xBB,
    'CueTime': 0xB3,
    'CueTrackPositions': 0xB7,
    'CueTrack': 0xF7,
    'CueClusterPosition': 0xF1,
    'CueRelativePosition': 0xF0,
}


def id_bytes(name):
    element_id = ELEMENT_IDS[name]
    return element_id.to_bytes((element_id.bit_length() + 7) // 8, 'big')


def element(name, payload):
    """An EBML element, with its data size in the 8 byte form"""
    return id_bytes(name) + b'\x01' + len(payload).to_bytes(7, 'big') + payload


def uint(name, value, width=None):
    width = width or max(1, (value.bit_length() + 7) // 8)
    return element(name, value.to_bytes(width, 'big'))


def string(name, value):
    return element(name, value.encode('ascii'))


def to_ms(ts, time_base):
    """A timestamp in milliseconds, rounded to the nearest one (as av_rescale_q)"""
    return math.floor(Fraction(ts) * time_base * 1000 + Fraction(1, 2))


def read_source(path):
    with open(path, 'rb') as f:
        if f.read(7) == b'version':
            sys.exit(f'{path} is a Git LFS pointer, run "git lfs pull" or pass --video-dir')
    with av.open(path) as src:
        st = src.streams.video[0]
        codec = st.codec_context
        assert codec.name == 'h264', codec.name
        pkts = [
            dict(data=bytes(p), pts=p.pts, dts=p.dts, key=p.is_keyframe, duration=p.duration)
            for p in src.demux(st)
            if p.size
        ]
        return dict(
            time_base=st.time_base,
            extradata=bytes(codec.extradata),
            width=codec.width,
            height=codec.height,
            pkts=pkts,
        )


def write(out_path, source):
    tb = source['time_base']
    pkts = source['pkts']
    durations = {e['duration'] for e in pkts}
    assert len(durations) == 1, f'not a constant frame duration: {durations}'
    frame_ns = math.floor(Fraction(durations.pop()) * tb * 10**9 + Fraction(1, 2))
    end_ms = float(Fraction(max(e['pts'] + e['duration'] for e in pkts)) * tb * 1000)

    ebml_header = element(
        'EBML',
        uint('EBMLVersion', 1)
        + uint('EBMLReadVersion', 1)
        + uint('EBMLMaxIDLength', 4)
        + uint('EBMLMaxSizeLength', 8)
        + string('DocType', 'matroska')
        + uint('DocTypeVersion', 4)
        + uint('DocTypeReadVersion', 2),
    )
    info = element(
        'Info',
        uint('TimestampScale', TIMESTAMP_SCALE_NS)
        + element('Duration', struct.pack('>d', end_ms))
        + string('MuxingApp', APP)
        + string('WritingApp', APP),
    )
    tracks = element(
        'Tracks',
        element(
            'TrackEntry',
            uint('TrackNumber', 1)
            + uint('TrackUID', 1)
            + uint('TrackType', 1)  # video
            + uint('FlagLacing', 0)
            + string('Language', 'und')
            + string('CodecID', 'V_MPEG4/ISO/AVC')
            + element('CodecPrivate', source['extradata'])
            + uint('DefaultDuration', frame_ns)
            + element(
                'Video', uint('PixelWidth', source['width']) + uint('PixelHeight', source['height'])
            ),
        ),
    )

    # A cluster for each GOP, from its keyframe on; the block timestamps are relative to the
    # cluster's, the pts of its first block
    clusters, cue_points = [], []  # cue points: (pts, cluster, position of the block in it)
    for e in pkts:
        ts = to_ms(e['pts'], tb)
        if e['key'] or not clusters:
            clusters.append((ts, uint('Timestamp', ts)))
        cluster_ts, payload = clusters[-1]
        if e['key']:
            cue_points.append((ts, len(clusters) - 1, len(payload)))
        flags = 0x80 if e['key'] else 0
        block = (
            b'\x81' + (ts - cluster_ts).to_bytes(2, 'big', signed=True) + bytes([flags]) + e['data']
        )
        clusters[-1] = (cluster_ts, payload + element('SimpleBlock', block))
    clusters = [element('Cluster', payload) for _, payload in clusters]

    # The positions are relative to the start of the data of the segment. A SeekPosition takes
    # 8 bytes, so that the size of the SeekHead does not depend on the positions.
    def seek_head(positions):
        return element(
            'SeekHead',
            b''.join(
                element('Seek', element('SeekID', id_bytes(name)) + uint('SeekPosition', pos, 8))
                for name, pos in positions.items()
            ),
        )

    info_pos = len(seek_head({'Info': 0, 'Tracks': 0, 'Cues': 0}))
    tracks_pos = info_pos + len(info)
    cluster_pos = [tracks_pos + len(tracks)]
    for c in clusters:
        cluster_pos.append(cluster_pos[-1] + len(c))
    cues_pos = cluster_pos.pop()
    cues = element(
        'Cues',
        b''.join(
            element(
                'CuePoint',
                uint('CueTime', ts)
                + element(
                    'CueTrackPositions',
                    uint('CueTrack', 1)
                    + uint('CueClusterPosition', cluster_pos[cluster])
                    + uint('CueRelativePosition', rel),
                ),
            )
            for ts, cluster, rel in cue_points
        ),
    )
    head = seek_head({'Info': info_pos, 'Tracks': tracks_pos, 'Cues': cues_pos})
    assert len(head) == info_pos
    segment = element('Segment', head + info + tracks + b''.join(clusters) + cues)
    with open(out_path, 'wb') as f:
        f.write(ebml_header + segment)


def decode(path):
    with av.open(path) as c:
        return [f.to_ndarray(format='yuv420p') for f in c.decode(video=0)]


def seek_landing(container, stream, ts):
    """The pts of the first packet after a seek to `ts`, as DALI seeks"""
    container.seek(ts, backward=True, any_frame=False, stream=stream)
    for p in container.demux(stream):
        if p.size:
            return p.pts
    return None


def verify(out_path, src_path, source):
    tb = source['time_base']
    pkts = source['pkts']
    with av.open(out_path) as c:
        st = c.streams.video[0]
        assert c.format.name == 'matroska,webm', c.format.name
        assert st.time_base == Fraction(1, 1000), st.time_base
        assert st.codec_context.name == 'h264', st.codec_context.name
        assert (
            bytes(st.codec_context.extradata) == source['extradata']
        ), 'not the avcC of the source'
        rows = [(p.pts, p.dts, p.is_keyframe, bytes(p)) for p in c.demux(st) if p.size]
    assert len(rows) == len(pkts), f'{len(rows)} packets, {len(pkts)} in the source'
    for i, (e, (pts, _, key, data)) in enumerate(zip(pkts, rows)):
        assert data == e['data'], f'packet {i} differs from the source'
        assert key == e['key'], f'packet {i}: not the key flag of the source'
        assert pts == to_ms(e['pts'], tb), f'packet {i}: pts {pts}, not the one of the source'
    reordered = sum(1 for a, b in zip(rows, rows[1:]) if b[0] < a[0])
    assert reordered > 0, 'no reordered frames'
    keys = [i for i, r in enumerate(rows) if r[2]]
    key_pts = [rows[i][0] for i in keys]
    # Matroska has no dts: libavformat derives them once it has probed the stream (PyAV does when
    # it opens the file). The dts of each keyframe after the first is below its pts (B-frames), and
    # a seek to it lands on the keyframe before.
    key_dts = [rows[i][1] for i in keys]
    assert all(dts < pts for pts, dts in zip(key_pts[1:], key_dts[1:])), 'a keyframe dts >= pts'

    with av.open(out_path) as c:
        st = c.streams.video[0]
        by_pts = [seek_landing(c, st, pts) for pts in key_pts]
        by_dts = [seek_landing(c, st, dts) for dts in key_dts[1:]]
    assert by_pts == key_pts, f'seeks to the keyframes pts {key_pts} land on {by_pts}'
    assert by_dts == key_pts[:-1], f'seeks to the keyframes dts {key_dts[1:]} land on {by_dts}'

    frames = decode(out_path)
    ref = decode(src_path)
    assert len(frames) == len(ref) == len(pkts), f'{len(frames)} frames, {len(ref)} in the source'
    assert all((a == b).all() for a, b in zip(frames, ref)), 'frames differ from the source'
    return dict(packets=len(rows), keys=keys, key_pts=key_pts, key_dts=key_dts, reordered=reordered)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument(
        '--video-dir',
        default=DEFAULT_VIDEO_DIR,
        help='the db/video directory with the source clips',
    )
    parser.add_argument('--out-dir', default=HERE, help='output directory')
    args = parser.parse_args()

    for out_name, src_name in CLIPS.items():
        src_path = os.path.join(args.video_dir, src_name)
        out_path = os.path.join(args.out_dir, out_name)
        source = read_source(src_path)
        write(out_path, source)
        info = verify(out_path, src_path, source)
        print(
            f'{out_path}: {info["packets"]} packets, keyframes (decoding order) {info["keys"]} '
            f'with the pts {info["key_pts"]} and the dts {info["key_dts"]} (ms), '
            f'{info["reordered"]} packets with a pts lower than the one before'
        )


if __name__ == '__main__':
    main()

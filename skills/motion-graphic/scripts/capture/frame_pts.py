#!/usr/bin/env python3
"""frame_pts.py: list a recording's real frame timestamps and the gaps between them.

Usage:
  frame_pts.py <video> [--gap 0.1] [--from 0] [--to 1e9] [--all]

Reads every frame's presentation time (ffprobe frame=pts_time) from the RAW, variable-frame-rate recording
(before vfr_to_cfr.sh). Prints a summary (frames, span, median interval) and every gap longer than --gap seconds.
--all prints every timestamp in the window instead.

What the gaps mean: a VFR screen recorder writes a frame only when pixels change. A long gap is a still screen:
either nothing was happening (fine) or the app stalled (a debug build freezing on Save, a slow network call).
The frame right after a stall gap is usually the app popping its new state in at once. That is where to cut the
stall out of the edit and lay a short crossfade bridge over the pop (see Bridge in the template's clips.tsx).
Exact pts also give the frame where the app reacted to a tap, to time the film's pointer to.
"""
import argparse, statistics, subprocess, sys


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('--gap', type=float, default=0.1)
    ap.add_argument('--from', dest='t0', type=float, default=0.0); ap.add_argument('--to', dest='t1', type=float, default=1e9)
    ap.add_argument('--all', action='store_true')
    a = ap.parse_args()
    out = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'frame=pts_time', '-of', 'csv=p=0', a.video], text=True)
    ts = sorted(float(x.strip().rstrip(',')) for x in out.split() if x.strip().rstrip(',') not in ('', 'N/A'))
    if len(ts) < 2:
        print('fewer than 2 frames'); return 1
    iv = [b - x for x, b in zip(ts, ts[1:])]
    print(f'{a.video}: {len(ts)} frames, {ts[0]:.3f}-{ts[-1]:.3f} s, median interval {statistics.median(iv) * 1000:.1f} ms'
          f' ({1 / statistics.median(iv):.1f} fps), longest gap {max(iv):.3f} s')
    for x, b in zip(ts, ts[1:]):
        if a.t0 <= x <= a.t1 and (a.all or b - x > a.gap):
            print(f'{x:9.3f} -> {b:9.3f}  gap {b - x:6.3f} s' if not a.all else f'{x:9.3f}  (+{(b - x) * 1000:.1f} ms)')


if __name__ == '__main__':
    sys.exit(main())

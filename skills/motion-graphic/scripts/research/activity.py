#!/usr/bin/env python3
"""activity.py: where and when a screen recording changes, per second and per horizontal band.

Usage:
  activity.py <video> [--bands 0,0.25,0.85,1] [--names top,mid,bottom] [--min 0.02]
  activity.py public/rec/take3.mp4 --bands 0,0.12,0.8,1 --names status,content,composer

The frame is split into horizontal bands (fractions of the height). For each second it prints the summed
mean pixel change per band (frames sampled at 10 fps, scaled to 110 px wide, greyscale), skipping quiet
seconds below --min. Use it on a long take to find the seconds worth cutting to: when the result lands
(content band), when the user types (composer band), when nothing happens (an app stall: every band near 0).
Needs ffmpeg and numpy.
"""
import argparse, json, subprocess, sys
import numpy as np


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('--bands', default='0,0.25,0.85,1'); ap.add_argument('--names', default='')
    ap.add_argument('--min', type=float, default=0.02)
    a = ap.parse_args()
    edges = [float(x) for x in a.bands.split(',')]
    names = a.names.split(',') if a.names else [f'b{i}' for i in range(len(edges) - 1)]
    p = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', a.video]))
    sw, sh = p['streams'][0]['width'], p['streams'][0]['height']
    w = 110; h = int(round(w * sh / sw / 2)) * 2
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', a.video, '-vf', f'fps=10,scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)
    d = np.abs(np.diff(fr, axis=0))
    d = np.concatenate([np.zeros_like(d[:1]), d])  # d[i] = change INTO frame i, so a change at 2.0 s prints at 2.0
    rows = [(int(edges[i] * h), int(edges[i + 1] * h)) for i in range(len(edges) - 1)]
    per = [d[:, r0:r1].mean(axis=(1, 2)) for r0, r1 in rows]
    print(a.video, f'{sw}x{sh}', 'bands', dict(zip(names, edges[1:])))
    for s in range(0, len(d), 10):
        vals = [float(b[s:s + 10].sum()) for b in per]
        if sum(vals) > a.min:
            print(f'{s / 10:6.1f}s ' + ' '.join(f'{n} {v:6.2f}' for n, v in zip(names, vals)))


if __name__ == '__main__':
    sys.exit(main())

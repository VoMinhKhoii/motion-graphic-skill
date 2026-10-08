#!/usr/bin/env python3
"""review_sheet.py: a labelled frame grid of one film, to check the automatic classes by eye.

Usage:
  review_sheet.py <out_dir> <stem> [--fps 4] [--from S] [--to S] [--h 200] [--cols 8] [--out sheet.jpg]
  review_sheet.py refs/corpus @Figma__IfwwyhTIJms --fps 4 --from 0 --to 12

Each frame is stamped with its time, the text class of the nearest 2 fps sample (demo, card, over, logo,
other, trans) and the camera state of its 0.5 s window. A frame that is the first one after a transition starts
gets a coloured bar and the transition's type and length. Writes <out_dir>/films/<stem>/review_<from>-<to>.jpg
unless --out is given. Downscale before reading it in an agent session (sips -Z 1000 or Pillow).
Needs ffmpeg and Pillow; reads meta.json, transitions.json and text.json written by run_corpus.py.
"""
import argparse, io, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

COL = {'cut': (20, 20, 20), 'dissolve': (26, 163, 154), 'push': (58, 154, 58), 'zoom_in': (214, 69, 69), 'zoom_out': (138, 92, 214), 'other': (150, 150, 150)}
SHORT = {'demo': 'demo', 'text_card': 'card', 'text_over': 'over', 'logo': 'logo', 'other': 'other', 'transition': 'trans'}


def font(size):
    for f in ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out_dir'); ap.add_argument('stem'); ap.add_argument('--fps', type=float, default=4)
    ap.add_argument('--from', dest='t0', type=float, default=0); ap.add_argument('--to', dest='t1', type=float)
    ap.add_argument('--h', type=int, default=200); ap.add_argument('--cols', type=int, default=8); ap.add_argument('--out')
    a = ap.parse_args()
    d = os.path.join(a.out_dir, 'films', a.stem)
    meta = json.load(open(os.path.join(d, 'meta.json'))); tr = json.load(open(os.path.join(d, 'transitions.json')))
    tx = json.load(open(os.path.join(d, 'text.json')))
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import text_frames
    text_frames.reclassify(tx, [r['t'] for r in tr['transitions']])
    t1 = min(a.t1 or meta['duration'], meta['duration'])
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a.t0), '-to', str(t1), '-i', meta['video'], '-vf', f'fps={a.fps},scale=-2:{a.h}',
                          '-f', 'image2pipe', '-vcodec', 'mjpeg', '-q:v', '4', '-'], capture_output=True).stdout
    frames = [Image.open(io.BytesIO(b'\xff\xd8' + p)).convert('RGB') for p in raw.split(b'\xff\xd8')[1:]]
    if not frames:
        raise SystemExit('no frames decoded')
    w = frames[0].width; cols = a.cols; rows = (len(frames) + cols - 1) // cols
    S = Image.new('RGB', (cols * (w + 4) + 4, rows * (a.h + 56) + 4), (240, 238, 233)); dr = ImageDraw.Draw(S); f = font(12)
    step = 1 / a.fps
    for i, im in enumerate(frames):
        t = a.t0 + i * step
        x = 4 + (i % cols) * (w + 4); y = 4 + (i // cols) * (a.h + 56)
        S.paste(im, (x, y + 8))
        smp = min(tx['samples'], key=lambda s: abs(s['t'] - t)) if tx['samples'] else None
        win = next((v for v in tr['windows'] if v['t'] <= t < v['t'] + 0.5), None)
        dr.text((x + 2, y + a.h + 10), f"{t:.2f}s {SHORT.get(smp['cls'], '?') if smp else '-'}", fill=(20, 20, 19), font=f)
        dr.text((x + 2, y + a.h + 24), f"cam {win['state'] if win else '-'}", fill=(90, 90, 90), font=f)
        hit = [r for r in tr['transitions'] if t - step < r['t'] + (0.034 if r['dur'] == 0 else 0) <= t]
        if hit:
            r = hit[0]; dr.rectangle([x, y, x + w, y + 7], fill=COL[r['type']])
            dr.text((x + 2, y + a.h + 38), f"> {r['type']} {r['dur']:g}s", fill=COL[r['type']], font=f)
    out = a.out or os.path.join(d, f'review_{a.t0:g}-{t1:g}.jpg')
    S.save(out, quality=85)
    print(out, S.size)


if __name__ == '__main__':
    main()

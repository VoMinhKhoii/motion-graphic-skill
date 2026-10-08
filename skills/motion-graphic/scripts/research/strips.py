#!/usr/bin/env python3
"""strips.py: one timestamped strip of frames from a film, at the moments you choose.

Usage:
  strips.py <video> <out.jpg> <t> [<t> ...] [--h 360] [--max-w 1600]
  strips.py vids/film.mp4 strips/hook.jpg 0.4 1.2 2.1 3.0

Each frame is scaled to --h px tall and stamped with its time in a dark tag; frames sit side by side and the
strip is shrunk to --max-w if wider. Use it to show a technique (a hook, a transition, an ending) as evidence on a
technique card, or to compare the same beat across films. For an even overview use analyze_video.py's sheet.
Needs ffmpeg and Pillow.
"""
import argparse, io, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont


def font(size):
    for f in ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('out'); ap.add_argument('times', nargs='+', type=float)
    ap.add_argument('--h', type=int, default=360); ap.add_argument('--max-w', type=int, default=1600)
    a = ap.parse_args()
    ims = []
    for t in a.times:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', a.video, '-frames:v', '1', '-vf', f'scale=-2:{a.h}',
                              '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True).stdout
        if not raw:
            print(f'no frame at {t}s (past the end?)', file=sys.stderr); continue
        ims.append((t, Image.open(io.BytesIO(raw)).convert('RGB')))
    if not ims:
        return 1
    gap = 8; W = sum(i.width for _, i in ims) + gap * (len(ims) - 1)
    S = Image.new('RGB', (W, a.h), (240, 238, 233)); d = ImageDraw.Draw(S); f = font(max(14, a.h // 18)); x = 0
    for t, im in ims:
        S.paste(im, (x, 0)); tag = f'{t:.1f}s'; tw = d.textlength(tag, font=f)
        d.rectangle([x, a.h - f.size - 12, x + tw + 16, a.h], fill=(20, 20, 19)); d.text((x + 8, a.h - f.size - 8), tag, fill='white', font=f)
        x += im.width + gap
    if W > a.max_w:
        S = S.resize((a.max_w, int(a.h * a.max_w / W)))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    S.save(a.out, quality=80)
    print(a.out, S.size, round(os.path.getsize(a.out) / 1024), 'KB')


if __name__ == '__main__':
    sys.exit(main())

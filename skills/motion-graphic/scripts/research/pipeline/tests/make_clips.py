#!/usr/bin/env python3
"""make_clips.py: build three synthetic test films with known transitions, camera moves and text, plus truth.json.

Usage:
  make_clips.py <out_dir>

Writes 1280x720, 30 fps:
  cuts_fades.mp4  scene A 2 s | cut | B 2 s, crossfading over 0.6 s into C | C 2 s | cut | D 2 s
  moves.mp4       A slides left into B over 0.5 s | B pans right 2 s | B zooms through into C over 0.6 s |
                  C zooms in slowly 2 s | cut | D still 1.5 s
  text.mp4        a dense UI-like screen 3 s | cut | a 4-word text card 2.5 s | cut | the UI 2 s | cut | a
                  one-word end mark 1.5 s
  hard.mp4        harder cases: a panning shot crossfades over 0.5 s into a zooming shot | cut | a 3-word card on
                  a soft gradient with film grain 2.5 s | cut | a still scene 1.5 s
  truth.json      the transitions, camera states and text classes each clip should produce
Scenes are drawn with Pillow (textured blobs and stripes) so no third-party media is involved. Needs ffmpeg,
numpy and Pillow.
"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1280, 720, 30


def font(size, bold=False):
    names = ['/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for n in names:
        if os.path.exists(n):
            return ImageFont.truetype(n, size)
    return ImageFont.load_default(size=size)


def scene(seed, w=W, h=H):
    """A textured scene: smooth colour noise, then stripes and blobs so every 40 px block has detail."""
    rng = np.random.default_rng(seed)
    small = (rng.random((h // 40, w // 40, 3)) * 255).astype(np.uint8)
    im = Image.fromarray(small).resize((w, h), Image.BICUBIC)
    d = ImageDraw.Draw(im)
    for _ in range(140):
        x, y = rng.integers(0, w), rng.integers(0, h); r = int(rng.integers(8, 60))
        c = tuple(int(v) for v in rng.integers(0, 255, 3))
        (d.ellipse if rng.random() < 0.5 else d.rectangle)([x - r, y - r, x + r, y + r], fill=c)
    return im.filter(ImageFilter.GaussianBlur(1))


def ui_screen():
    im = Image.new('RGB', (W, H), (246, 246, 248)); d = ImageDraw.Draw(im); f = font(18); fb = font(22, True)
    d.rectangle([0, 0, 240, H], fill=(232, 233, 238))
    for i, item in enumerate(['Inbox', 'Today', 'Upcoming', 'Projects', 'Reports', 'Settings', 'Team', 'Archive']):
        d.text((28, 40 + i * 42), item, font=f, fill=(40, 40, 50))
    d.text((280, 30), 'Weekly overview', font=fb, fill=(20, 20, 30))
    rows = ['Design review moved to Thursday', 'Ship the onboarding fix', 'Write the release notes',
            'Check the export on Android', 'Reply to the pricing thread', 'Update the changelog draft',
            'Prepare the demo account', 'Record the screen capture', 'Fix the chart legend colour',
            'Sync with the support queue', 'Review open pull requests', 'Plan next week']
    for i, r in enumerate(rows):
        y = 90 + i * 48
        d.rounded_rectangle([280, y, 1240, y + 40], 8, fill=(255, 255, 255), outline=(220, 220, 226))
        d.text((300, y + 10), r, font=f, fill=(40, 40, 50)); d.text((1120, y + 10), f'{i + 3}:00', font=f, fill=(120, 120, 130))
    return im


def card(text, size, bg=(18, 18, 22), fg=(245, 245, 240)):
    im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im); f = font(size, True)
    lines = text.split('\n')
    hs = [d.textbbox((0, 0), ln, font=f) for ln in lines]
    total = sum(b[3] - b[1] for b in hs) + 20 * (len(lines) - 1); y = (H - total) // 2
    for ln, b in zip(lines, hs):
        d.text(((W - (b[2] - b[0])) // 2 - b[0], y - b[1]), ln, font=f, fill=fg); y += b[3] - b[1] + 20
    return im


def gradient_card(text):
    y = np.linspace(0, 1, H)[:, None, None]
    top, bot = np.array([40, 60, 140]), np.array([200, 120, 170])
    im = Image.fromarray(np.broadcast_to(top + (bot - top) * y, (H, W, 3)).astype(np.uint8))
    d = ImageDraw.Draw(im); f = font(96, True); b = d.textbbox((0, 0), text, font=f)
    d.text(((W - (b[2] - b[0])) // 2 - b[0], (H - (b[3] - b[1])) // 2 - b[1]), text, font=f, fill=(255, 255, 255))
    return im


def ff(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def still(png, secs, out, vf=''):
    ff(['-loop', '1', '-t', str(secs), '-i', png, '-vf', (vf + ',' if vf else '') + f'fps={FPS},format=yuv420p,setsar=1',
        '-c:v', 'libx264', '-crf', '18', out])


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else 'synthetic'
    tmp = os.path.join(out, 'src'); os.makedirs(tmp, exist_ok=True)
    P = lambda n: os.path.join(tmp, n)
    for i, s in enumerate('ABCD'):
        scene(i + 1).save(P(f'{s}.png'))
    scene(9, W * 2, H).save(P('wide.png'))
    ui_screen().save(P('ui.png')); card('Built for\nevery launch', 110).save(P('card.png')); card('Acme', 90).save(P('end.png'))

    # 1. cuts_fades: A | cut | B xfade(fade 0.6 @ offset 2.0 of B) C | cut | D
    for s, secs in [('A', 2), ('B', 2.6), ('C', 2.6), ('D', 2)]:
        still(P(f'{s}.png'), secs, P(f'{s}.mp4'))
    ff(['-i', P('B.mp4'), '-i', P('C.mp4'), '-filter_complex', 'xfade=transition=fade:duration=0.6:offset=2.0', '-c:v', 'libx264', '-crf', '18', P('BC.mp4')])
    ff(['-i', P('A.mp4'), '-i', P('BC.mp4'), '-i', P('D.mp4'), '-filter_complex', '[0][1][2]concat=n=3:v=1', '-c:v', 'libx264', '-crf', '18',
        os.path.join(out, 'cuts_fades.mp4')])

    # 2. moves: A slideleft 0.5 -> B(pan right over a wide image) zoomin 0.6 -> C (slow zoom in) | cut | D
    still(P('A.png'), 1.5, P('mA.mp4'))
    # B: a 1280 window panning across the 2560-wide image at 200 px/s, 3.1 s long (0.5 s inside the slide)
    still(P('wide.png'), 3.1, P('mB.mp4'), vf="crop=1280:720:x='min(t*200,1280)':y=0")
    # C: slow zoom in, 10%/s, 2.6 s
    still(P('C.png'), 2.6, P('mC.mp4'), vf="scale=w='trunc(1280*(1+0.1*t)/2)*2':h='trunc(720*(1+0.1*t)/2)*2':eval=frame,crop=1280:720")
    still(P('D.png'), 1.5, P('mD.mp4'))
    ff(['-i', P('mA.mp4'), '-i', P('mB.mp4'), '-filter_complex', 'xfade=transition=slideleft:duration=0.5:offset=1.0', '-c:v', 'libx264', '-crf', '18', P('AB.mp4')])
    ff(['-i', P('AB.mp4'), '-i', P('mC.mp4'), '-filter_complex', 'xfade=transition=zoomin:duration=0.6:offset=3.0', '-c:v', 'libx264', '-crf', '18', P('ABC.mp4')])
    ff(['-i', P('ABC.mp4'), '-i', P('mD.mp4'), '-filter_complex', '[0][1]concat=n=2:v=1', '-c:v', 'libx264', '-crf', '18', os.path.join(out, 'moves.mp4')])

    # 3. text: ui 3 | card 2.5 | ui 2 | end 1.5
    for name, png, secs in [('t1', 'ui.png', 3), ('t2', 'card.png', 2.5), ('t3', 'ui.png', 2), ('t4', 'end.png', 1.5)]:
        still(P(png), secs, P(f'{name}.mp4'))
    ff(['-i', P('t1.mp4'), '-i', P('t2.mp4'), '-i', P('t3.mp4'), '-i', P('t4.mp4'), '-filter_complex', '[0][1][2][3]concat=n=4:v=1',
        '-c:v', 'libx264', '-crf', '18', os.path.join(out, 'text.mp4')])

    # 4. hard: pan B (wide) crossfade 0.5 into zooming C | cut | gradient card with grain | cut | D
    gradient_card('Made for teams').save(P('grad.png'))
    still(P('wide.png'), 2.5, P('hB.mp4'), vf="crop=1280:720:x='t*200':y=0")
    still(P('C.png'), 2.5, P('hC.mp4'), vf="scale=w='trunc(1280*(1+0.1*t)/2)*2':h='trunc(720*(1+0.1*t)/2)*2':eval=frame,crop=1280:720")
    still(P('grad.png'), 2.5, P('hG.mp4'), vf='noise=alls=12:allf=t')
    still(P('D.png'), 1.5, P('hD.mp4'))
    ff(['-i', P('hB.mp4'), '-i', P('hC.mp4'), '-filter_complex', 'xfade=transition=fade:duration=0.5:offset=2.0', '-c:v', 'libx264', '-crf', '18', P('hBC.mp4')])
    ff(['-i', P('hBC.mp4'), '-i', P('hG.mp4'), '-i', P('hD.mp4'), '-filter_complex', '[0][1][2]concat=n=3:v=1', '-c:v', 'libx264', '-crf', '18',
        os.path.join(out, 'hard.mp4')])

    truth = {
        'cuts_fades.mp4': {'transitions': [['cut', 2.0, 0], ['dissolve', 4.0, 0.6], ['cut', 6.6, 0]],
                           'camera': [[0, 8.6, 'still']]},
        'moves.mp4': {'transitions': [['push', 1.0, 0.5], ['zoom_in', 3.0, 0.6], ['cut', 5.6, 0]],
                      'camera': [[1.6, 3.0, 'pan'], [3.7, 5.5, 'zoom_in'], [5.7, 7.1, 'still']]},
        'text.mp4': {'transitions': [['cut', 3.0, 0], ['cut', 5.5, 0], ['cut', 7.5, 0]],
                     'classes': [[0, 3.0, 'demo'], [3.0, 5.5, 'text_card'], [5.5, 7.5, 'demo'], [7.5, 9.0, 'logo']],
                     'card': {'words': 4, 'lines': 2, 'hold': 2.5}},
        'hard.mp4': {'transitions': [['dissolve', 2.0, 0.5], ['cut', 4.5, 0], ['cut', 7.0, 0]],
                     'camera': [[0, 2.0, 'pan'], [2.5, 4.5, 'zoom_in'], [7.0, 8.5, 'still']],
                     'classes': [[4.5, 7.0, 'text_card']], 'card': {'words': 3, 'lines': 1, 'hold': 2.5}},
    }
    json.dump(truth, open(os.path.join(out, 'truth.json'), 'w'), indent=1)
    print('clips ->', out)


if __name__ == '__main__':
    main()

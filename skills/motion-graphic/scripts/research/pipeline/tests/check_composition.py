#!/usr/bin/env python3
"""check_composition.py: draw synthetic frames with known coverage, empty region, subject box, edge bleed, element
count and text boxes, and check what composition.py and check_frames.py measure.

Usage:
  check_composition.py [work_dir]      (default: a new temporary folder, deleted afterwards)

Frames are 1280x720 and drawn with Pillow (no third-party media):
  lone        a 20% x 40% block centred on a flat cream ground: coverage 8%, 1 element, no bleed, empty 40%
  gradient    the same block on a soft two-axis gradient with film grain: the gradient is background too
  bleed       a block from 30% to 70% across and 50% down to the bottom edge, its lowest strip flat: coverage 20%,
              bleed bottom only (the flat strip touching the edge is not ground: its colour is not the ground's)
  two         two blocks far apart: 2 elements
  outline     a 50% x 50% outlined (not filled) panel: the enclosed flat inside counts as content (25%)
  texture     colour noise over the whole frame: coverage 100%, bleed on all four edges, empty 0%
  phone       a phone outline from 35% to 65% across and 20% down, running off the bottom edge, its flat screen the
              same cream as the ground: the screen is content (coverage 24%), bleed bottom. Version 1 read the
              screen as ground because it touches the border; the corner rule keeps it.
  card        a text card (known OCR line boxes, no OCR engine needed): text area, cap height, 3 x 3 cells, and an
              icon beside the line counted as one floating object
Then check_frames.judge on hand-made measures with the default limits: a pill on a void read as a text card is
flagged for its small type; a card with an icon passes; a five-line card is flagged; a sparse full-screen
UI (text rows only, no floating object) passes; a small window in the middle of a demo frame is too far away.
Then check_frames.py runs on lone (--role other, expect FLAG and "lone object") and texture (expect PASS), with
--ocr none, and their exit codes are checked. Tolerance: 2 percentage points for areas and boxes.
Prints one line per check; exit 1 if any fails. Needs numpy and Pillow.
"""
import os, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import composition  # noqa: E402

W, H = 1280, 720
CREAM, INK = (248, 247, 244), (60, 50, 40)
TOL = 2.0
bad = 0


def check(name, ok, got=''):
    global bad
    print(('ok    ' if ok else 'FAIL  ') + name + ('' if ok else f'  (got {got})'))
    bad += not ok


def near(a, b, tol=TOL):
    return abs(a - b) <= tol


def block(im, x0, y0, x1, y1, fill=INK):
    """A block from fractions of the frame, with some inner texture so it reads as a picture, not a flat card."""
    d = ImageDraw.Draw(im)
    d.rectangle([x0 * W, y0 * H, x1 * W - 1, y1 * H - 1], fill=fill)
    for k in range(6):
        y = y0 * H + (k + 1) * (y1 - y0) * H / 7
        d.line([x0 * W + 8, y, x1 * W - 9, y], fill=(200, 180, 120), width=3)
    return im


def glyphs(im, x0, y0, x1, y1, ink=INK):
    """Glyph-like strokes filling a line box (fractions of the frame), where OCR would put the line."""
    d = ImageDraw.Draw(im); x = x0 * W
    while x + 0.012 * W <= x1 * W:
        d.rectangle([x, y0 * H, x + 0.012 * W, y1 * H], fill=ink); x += 0.02 * W
    return im


def gradient():
    yy, xx = np.mgrid[0:H, 0:W]
    a = np.stack([235 + 15 * xx / W, 215 + 20 * yy / H, 240 - 25 * xx / W], axis=2)
    a += np.random.default_rng(1).normal(0, 4, a.shape)  # film grain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def main():
    work = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='composition_')
    os.makedirs(work, exist_ok=True)

    m = composition.measure(block(Image.new('RGB', (W, H), CREAM), 0.4, 0.3, 0.6, 0.7))
    check('lone: coverage 8%', near(m['coverage'], 8), m['coverage'])
    check('lone: 1 element, no bleed', m['elements'] == 1 and m['bleed'] == [], (m['elements'], m['bleed']))
    check('lone: subject box 40,30 20x40', all(near(a, b) for a, b in zip(m['subject']['box'], [40, 30, 20, 40])), m['subject'])
    check('lone: largest empty region 40% (the side band)', near(m['empty'], 40), m['empty'])

    g = composition.measure(block(gradient(), 0.4, 0.3, 0.6, 0.7))
    check('gradient + grain: same coverage and empty region as flat', near(g['coverage'], 8) and near(g['empty'], 40), (g['coverage'], g['empty']))

    m = composition.measure(block(Image.new('RGB', (W, H), CREAM), 0.3, 0.5, 0.7, 1.0))
    check('bleed: coverage 20%, bleed bottom only', near(m['coverage'], 20) and m['bleed'] == ['bottom'], (m['coverage'], m['bleed']))
    check('bleed: empty region 50% (the top half)', near(m['empty'], 50), m['empty'])

    im = block(block(Image.new('RGB', (W, H), CREAM), 0.1, 0.2, 0.3, 0.5), 0.6, 0.5, 0.85, 0.8)
    m = composition.measure(im)
    check('two: 2 elements, coverage 13.5%', m['elements'] == 2 and near(m['coverage'], 13.5), (m['elements'], m['coverage']))

    im = Image.new('RGB', (W, H), CREAM)
    ImageDraw.Draw(im).rectangle([0.25 * W, 0.25 * H, 0.75 * W - 1, 0.75 * H - 1], outline=INK, width=6)
    m = composition.measure(im)
    check('outline: the enclosed flat panel is content (25%)', near(m['coverage'], 25), m['coverage'])

    rng = np.random.default_rng(2)
    tex = Image.fromarray((rng.random((H // 8, W // 8, 3)) * 255).astype(np.uint8)).resize((W, H), Image.NEAREST)
    m = composition.measure(tex)
    check('texture: coverage 100%, bleed on 4 edges, empty 0%',
          near(m['coverage'], 100) and len(m['bleed']) == 4 and near(m['empty'], 0), (m['coverage'], m['bleed'], m['empty']))

    im = Image.new('RGB', (W, H), CREAM)
    ImageDraw.Draw(im).rounded_rectangle([0.35 * W, 0.2 * H, 0.65 * W, H + 40], radius=30, outline=INK, width=8)
    m = composition.measure(im)
    check('phone: the screen inside a bezel that runs off the bottom is content (24%)', near(m['coverage'], 24, 3), m['coverage'])
    check('phone: bleed bottom only', m['bleed'] == ['bottom'], m['bleed'])

    # card: a line of "text" (a dark bar where OCR would put its box) and an icon beside it
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    for k in range(12):  # glyph-like strokes inside the line box 20%..80% across, 45%..53% down
        x = 0.2 * W + k * 0.05 * W
        d.rectangle([x, 0.45 * H, x + 0.03 * W, 0.53 * H], fill=INK)
    d.ellipse([0.86 * W, 0.15 * H, 0.94 * W, 0.15 * H + 0.08 * W], fill=(210, 90, 40))
    lines = [{'text': 'A line of type here', 'conf': 0.95, 'box': [0.2, 0.45, 0.6, 0.08]}]
    t = composition.text_measures(lines, W / H)
    check('card: text area 4.8%', near(t['text_pct'], 4.8, 0.5), t['text_pct'])
    check('card: cap 6% (0.75 x 8%)', near(t['cap_pct'], 6, 0.1), t['cap_pct'])
    check('card: the line sits in the centre cell (4)', t['cells'] == [4], t['cells'])
    m = composition.measure(im)
    n, fl, fa = composition.objects(m['masses'], t['boxes'])
    check('card: 2 elements, 1 non-text object, floating', m['elements'] == 2 and n == 1 and fl == 1, (m['elements'], n, fl))
    check('card: the icon is smaller than the line', 0 < fa < t['text_pct'], (fa, t['text_pct']))

    # the rules, on hand-made measures
    import check_frames as cf
    th = cf.thresholds(None)
    base = {'coverage': 10.0, 'empty': 40.0, 'elements': 1, 'bleed': [], 'masses': [], 'subject': None, 'text_pct': 2.0,
            'cap_pct': 6.0, 'n_lines': 1, 'words': 4, 'objects': 0, 'floating': 0, 'floating_area': 0.0}
    pill = dict(base, floating=1, objects=1, floating_area=12.0, cap_pct=3.0, subject={'box': [10, 45, 80, 10], 'area': 8})
    check('rules: a pill on a void read as a card is flagged for its small type', any('card type small' in r for r in cf.judge(pill, 'text_card', th)), cf.judge(pill, 'text_card', th))
    icon = dict(base, floating=1, objects=1, floating_area=1.0)
    check('rules: a card with an icon beside the line passes', cf.judge(icon, 'text_card', th) == [], cf.judge(icon, 'text_card', th))
    five = dict(base, n_lines=5, words=12)
    check('rules: a five-line card is flagged', any('5 lines' in r for r in cf.judge(five, 'text_card', th)), cf.judge(five, 'text_card', th))
    ui = dict(base, coverage=15.0, elements=6, masses=[[5, 5, 60, 4], [5, 20, 70, 4], [5, 35, 50, 4]], subject={'box': [5, 20, 70, 4], 'area': 3})
    check('rules: a sparse full-screen UI (text rows only) passes', cf.judge(ui, 'demo', th) == [], cf.judge(ui, 'demo', th))
    far = dict(base, coverage=40.0, bleed=['bottom'], subject={'box': [40, 40, 20, 18], 'area': 3})
    check('rules: a small window in the middle of a demo frame is too far away', any('too far' in r for r in cf.judge(far, 'demo', th)), cf.judge(far, 'demo', th))

    # the rules on drawn stills with known OCR lines, the way check_frames.py measures a still
    def still(im, lines, role=None):
        m, pic, raw, aspect = cf.frame_measures(im, lines)
        role = role or cf.role_of(pic, raw, aspect, m)
        return m, role, cf.judge(m, role, th)

    card = Image.new('RGB', (W, H), (255, 255, 255)); words = 'one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen'.split()
    lines = []
    for k in range(4):  # four centred lines of four words, 7% tall, 2% apart
        y = 0.33 + k * 0.09; lines.append({'text': ' '.join(words[4 * k:4 * k + 4]), 'conf': 0.95, 'box': [0.2, y, 0.6, 0.07]})
        glyphs(card, 0.2, y, 0.8, y + 0.07)
    m, role, why = still(card, lines)
    check('long card: a plain 4-line, 16-word card reads as a text card, not a dense UI', role == 'text_card', role)
    check('long card: flagged for its 4 lines and 16 words', any('4 lines' in r for r in why) and any('16 words' in r for r in why), why)

    for name, ground, ink in (('light', (255, 255, 255), (40, 40, 40)), ('dark', (18, 18, 20), (230, 230, 230))):
        ui = Image.new('RGB', (W, H), ground); rows = []
        for k, w in enumerate([0.22, 0.3, 0.18, 0.26, 0.2]):  # five short UI rows, 3% tall, far apart
            y = 0.1 + k * 0.18; rows.append({'text': 'Row label here', 'conf': 0.95, 'box': [0.08, y, w, 0.03]})
            glyphs(ui, 0.08, y, 0.08 + w, y + 0.03, ink)
        m, role, why = still(ui, rows)
        check(f'sparse UI ({name}): text rows only, no object, not a card, passes (no "too far away")',
              m['objects'] == 0 and role != 'text_card' and why == [], (m['objects'], role, why, m['subject']))

    pill = Image.new('RGB', (W, H), CREAM)
    ImageDraw.Draw(pill).rounded_rectangle([0.4 * W, 0.46 * H, 0.6 * W, 0.54 * H], radius=0.04 * H, fill=(225, 220, 210), outline=INK, width=2)
    glyphs(pill, 0.43, 0.485, 0.57, 0.515)
    m, _, why = still(pill, [{'text': 'Add meal', 'conf': 0.95, 'box': [0.43, 0.485, 0.14, 0.03]}], 'demo')
    check('pill: a labelled pill on a void is an object, and a lone object', m['objects'] == 1 and any('lone object' in r for r in why), (m['objects'], why))

    para = Image.new('RGB', (W, H), CREAM); plines = []
    for k, w in enumerate([0.7, 0.25, 0.6, 0.2]):  # a ragged paragraph: line boxes cover under half its box
        y = 0.3 + k * 0.07; plines.append({'text': 'words ' * 4, 'conf': 0.95, 'box': [0.15, y, w, 0.05]})
        glyphs(para, 0.15, y, 0.15 + w, y + 0.05)
    m, _, _ = still(para, plines, 'demo')
    check('paragraph: a ragged 4-line paragraph is text, not an object', m['elements'] >= 1 and m['objects'] == 0, (m['elements'], m['objects'], m['masses']))

    lone = block(Image.new('RGB', (W, H), CREAM), 0.4, 0.3, 0.6, 0.7)
    for name, box in (('letterbox', [0, 0, W, 0.1 * H - 1, 0, 0.9 * H, W, H]), ('pillarbox', [0, 0, 0.125 * W - 1, H, 0.875 * W, 0, W, H])):
        im = lone.copy(); d = ImageDraw.Draw(im); d.rectangle(box[:4], fill=(0, 0, 0)); d.rectangle(box[4:], fill=(0, 0, 0))
        m, _, why = still(im, None, 'other')
        check(f'{name}: the bars are cut (pad {m["pad"]}) and the centred lone object is still flagged',
              any(m['pad']) and m['coverage'] < 15 and any('lone object' in r for r in why), (m['pad'], m['coverage'], why))
    m, _, _ = still(block(Image.new('RGB', (W, H), CREAM), 0.2, 0.35, 0.8, 0.65), None, 'other')
    check('padding: the flat ground around a 60%-wide block is not padding', not any(m['pad']), m['pad'])
    im = Image.new('RGB', (W, H), CREAM)
    ImageDraw.Draw(im).rectangle([0.35 * W, -10, 0.65 * W, H + 10], fill=(30, 30, 36), outline=INK, width=6)
    m, _, _ = still(im, None, 'other')
    check('padding: the flat sides of a full-height phone are not padding (0.53:1 inside is no standard shape)', not any(m['pad']), m['pad'])

    # check_frames end to end, no OCR, run as an executable (the docs call it directly)
    cf = os.path.join(HERE, 'check_frames.py')
    check('check_frames.py is executable', os.access(cf, os.X_OK))
    lone = os.path.join(work, 'lone.png'); block(Image.new('RGB', (W, H), CREAM), 0.4, 0.3, 0.6, 0.7).save(lone)
    full = os.path.join(work, 'texture.png'); tex.save(full)
    r = subprocess.run([cf, lone, '--role', 'other', '--ocr', 'none'], capture_output=True, text=True)
    check('check_frames: lone object flagged, exit 1', r.returncode == 1 and 'FLAG' in r.stdout and 'lone object' in r.stdout, r.stdout[-300:])
    r = subprocess.run([cf, full, '--role', 'other', '--ocr', 'none'], capture_output=True, text=True)
    check('check_frames: full-bleed texture passes, exit 0', r.returncode == 0 and 'PASS' in r.stdout, r.stdout[-300:])
    roles = os.path.join(work, 'roles.csv'); open(roles, 'w').write('file,role\nlone.png,logo\n')
    r = subprocess.run([cf, lone, '--roles', roles, '--ocr', 'none'], capture_output=True, text=True)
    check('check_frames: --roles sets a frame\'s role (lone.png as logo: not checked, exit 0)', r.returncode == 0 and ' logo ' in r.stdout, r.stdout[-300:])

    if len(sys.argv) < 2:
        shutil.rmtree(work, ignore_errors=True)
    print('all checks passed' if not bad else f'{bad} checks FAILED')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

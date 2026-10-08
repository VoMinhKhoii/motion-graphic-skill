#!/usr/bin/env python3
"""check_frames.py: score storyboard stills (or any frames) for composition, and flag the frames a viewer would call
empty: a lone object on a void, a subject seen from too far away, a text card with small type or too much copy.

Usage:
  check_frames.py <frames dir or images...> [--baseline corpus/corpus.json] [--role auto|card|demo|logo|other|text_over]
                  [--roles roles.json|roles.csv] [--ocr auto|vision|tesseract|none] [--json out.json] [--debug DIR]

Per frame it prints the role, the measures (composition.py) and PASS or FLAG with reasons. Exit 1 if any frame is
flagged. A FLAG needs a fix or a reason written next to the frame (for example "logo end card, plain on purpose").
--debug writes each frame's background mask (magenta = background) to DIR, to see what the numbers saw.
Letterbox or pillarbox bars in a still are cut off before measuring (composition.find_pad) and the line says so.

Role. A storyboard knows each beat's role, so pass it: --roles names a file that maps frame file names to roles,
JSON {"03_card.png": "card", "07_end.png": "logo"} or CSV rows "03_card.png,card" (a "file,role" header is fine).
Frames it does not name take --role (default auto). --role auto reads the text with OCR: a frame that is only text
set at card size (no non-text element, text covers at least TEXT_DOMINANT of the content, lines of card height
hold at least half the line area) is a text card however many words it has; any other frame takes
text_frames.classify (text_card, text_over, demo or other). The classifier alone calls 12 or more words a dense UI,
so a long card would escape the card limits. Auto cannot tell a card set in small type from a sparse UI page: pass
the role. Auto never reads logo, because a still has no position in the film. With no OCR engine, auto falls back
to "other", the type checks are skipped and every element counts as an object (OCR is what tells a line of type
from an object).

The rules (the owner's: full bleed, the subject fills the frame and runs off its edges; empty space only around one
line of type alone on its ground):
  lone object on a void   demo, text_over, other. All three must hold:
                          - nothing runs off the frame (no edge bleed);
                          - at least one non-text object touches no edge (a card, a pill, a device, a cut-out);
                          - content covers less than LONE_COV of the frame (the subject does not fill it).
                          Type alone on its ground never trips it, nor does a sparse full-screen UI whose own white
                          surface reads as background (its rows are text, not objects).
  too far away            demo: the subject (largest element) is not text, touches no edge and is both shorter
                          than FAR_H and narrower than FAR_W: a device or a window seen from across the room. A
                          subject that is a line or a paragraph of type is not checked (a sparse UI's rows).
  text card               text_card: cap height below CARD_CAP, more than CARD_LINES lines, or more than CARD_WORDS
                          words. A card may be mostly ground; an icon beside the line is fine (a third of the lab's
                          cards carry one, so a floating object is not checked on a card). A UI pill or a small card
                          read as a text card (its label is its only text) trips CARD_CAP: UI type is smaller than
                          card type.
  logo                    reported, not checked.
  Not checked any more: coverage and the largest empty region on their own (a minimal style is sparse by design; the
  lab's demo frames have a median of 50% content), and the UI line height (small UI type is natural in a whole-phone
  shot; on a phone-sized screen it is the cut-in that has to be readable, which a still cannot tell).

Limits. With --baseline, each comes from the corpus (overall.composition.by_role), with a margin; without one, or
when a role has fewer than MIN_SAMPLES samples from MIN_FILMS films, the default (the lab corpus, 83 films, rounded):
  LONE_COV    demo coverage p25 x 1.0     default 25%   a frame sparser than three quarters of the reference
                                                        demo frames; the bound only spares a centred subject that
                                                        fills the frame (a 90%-tall photo inside its margin)
  FAR_H       demo subject_h p10 x 0.8    default 23%   well below the shortest tenth of reference subjects
  FAR_W       demo subject_w p10 x 0.8    default 37%
  CARD_CAP    text_card cap_pct p10 x 0.9 default 3.9%  smaller type than nine in ten reference cards, with 10% for OCR
                                                        box error (about +-15% across typefaces)
  CARD_LINES  text_card n_lines p90       default 3     more lines than nine in ten reference cards
  CARD_WORDS  text_card words p90 x 1.5   default 13    the lab's p90 is 9 words; the margin lets a two-line sentence
                                                        through (the approved v9 board's 10-word card passes)
Validation (references/measuring.md): the lab corpus flags about 1 frame in 10, mostly its own lone objects.
Needs numpy and Pillow; swiftc (macOS) or tesseract for --role auto and the type checks.
"""
import argparse, csv, glob, json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import composition, text_frames  # noqa: E402

# name: (baseline role, measure, quantile, factor, default)
LIMITS = {'lone_cov': ('demo', 'coverage', 'p25', 1.0, 25.0), 'far_h': ('demo', 'subject_h', 'p10', 0.8, 23.0),
          'far_w': ('demo', 'subject_w', 'p10', 0.8, 37.0), 'card_cap': ('text_card', 'cap_pct', 'p10', 0.9, 3.9),
          'card_lines': ('text_card', 'n_lines', 'p90', 1.0, 3), 'card_words': ('text_card', 'words', 'p90', 1.5, 13)}
MIN_SAMPLES, MIN_FILMS = 30, 3
ROLE_ALIAS = {'card': 'text_card'}
ROLES = ('text_card', 'demo', 'logo', 'other', 'text_over')
TEXT_DOMINANT = 0.5  # a text-only frame: OCR line boxes cover at least this share of the content
IMG_EXTS = ('.png', '.jpg', '.jpeg', '.webp')


def thresholds(baseline):
    """{limit: (value, source)}. Source is 'default' or e.g. 'corpus demo coverage p25 x 1.0'."""
    roles = (((baseline or {}).get('overall') or {}).get('composition') or {}).get('by_role', {})
    out = {}
    for name, (role, key, q, factor, default) in LIMITS.items():
        r = roles.get(role) or {}
        v = (r.get(key) or {}).get(q) if r.get('samples', 0) >= MIN_SAMPLES and r.get('films', 0) >= MIN_FILMS else None
        out[name] = (round(v * factor, 2), f'corpus {role} {key} {q} x {factor:g}') if v is not None else (default, 'default')
    return out


def read_text(paths, engine):
    """OCR every still once: {path: raw lines}, or {} with no engine."""
    if engine == 'vision':
        return text_frames.ocr_vision(text_frames.vision_binary(), paths, False)
    if engine == 'tesseract':
        return text_frames.ocr_tesseract(paths)
    return {}


def read_roles(path):
    """--roles: a JSON file {"file name": role} or a CSV file of "file name,role" rows -> {base name: role}."""
    if not path:
        return {}
    txt = open(path).read()
    rows = json.loads(txt).items() if txt.lstrip().startswith('{') else [r[:2] for r in csv.reader(txt.splitlines()) if len(r) >= 2]
    out = {}
    for f, r in rows:
        f, r = os.path.basename(f.strip()), ROLE_ALIAS.get(r.strip(), r.strip())
        if f.startswith('#') or (f, r) == ('file', 'role'):
            continue
        if r not in ROLES:
            sys.exit(f"error: --roles {path}: unknown role {r!r} for {f} (use {', '.join(ROLES)} or card)")
        out[f] = r
    return out


def text_only_card(m, lines):
    """True for a frame that is only text set at card size: no non-text element (every mass is text), OCR line boxes
    cover at least TEXT_DOMINANT of the content, and lines at least text_frames.CARD_MIN_H tall hold at least half of
    the line area. Such a frame is a text card however many words it has: text_frames.classify reads 12 or more words
    as a dense UI before it looks for a card, so a long card would otherwise escape the card limits. A sparse
    full-screen UI is text only too, but its rows are UI-sized (one large title among small rows stays a UI)."""
    if not lines or m.get('objects') != 0 or m['text_pct'] < TEXT_DOMINANT * m['coverage']:
        return False
    area = lambda ls: sum(l['box'][2] * l['box'][3] for l in ls)
    return area([l for l in lines if l['box'][3] * 100 >= text_frames.CARD_MIN_H]) >= 0.5 * area(lines)


def role_of(pic, raw, aspect, m):
    """The auto role of a still: text_card when text_only_card, else text_frames.classify. pic: the picture (padding cut)."""
    lines = composition.kept_lines(raw, aspect)
    if text_only_card(m, lines):
        return 'text_card'
    marks = [l for l in raw if l not in lines]
    edge, centred = text_frames.edge_share(pic, [l['box'] for l in raw if l['conf'] >= 0.3])
    return text_frames.classify(lines, edge, centred, 0.0, 1e9, marks)


def touches_edge(box):
    x, y, w, h = box
    return x <= 0.5 or y <= 0.5 or x + w >= 99.5 or y + h >= 99.5


def judge(m, role, th):
    """Reasons to flag a frame (empty list = PASS). m: composition.measure (+ text_measures and objects when OCR ran)."""
    reasons = []
    lim = lambda k: th[k][0]
    say = lambda k: f"{th[k][1]} = {lim(k):g}"
    ocr = 'floating' in m
    floating = m['floating'] if ocr else sum(not touches_edge(b) for b in m['masses'])
    if role in ('demo', 'text_over', 'other') and not m['bleed'] and floating and m['coverage'] < lim('lone_cov'):
        reasons.append(f"lone object on a void: {floating} object{'s touch' if floating > 1 else ' touches'} no edge, nothing runs off the frame, "
                       f"content {m['coverage']:g}% (limit {say('lone_cov')}%)")
    s = m['subject']
    thing = s and (not ocr or composition.object_masses([s['box']], m.get('boxes', []), m.get('aspect', 16 / 9)))  # the subject is not text
    if role == 'demo' and thing and not touches_edge(s['box']) and s['box'][3] < lim('far_h') and s['box'][2] < lim('far_w'):
        reasons.append(f"too far away: subject {s['box'][2]:g} x {s['box'][3]:g}% touches no edge (limits {say('far_w')}% wide, {say('far_h')}% tall)")
    if role == 'text_card' and ocr and m.get('n_lines'):
        if m['cap_pct'] < lim('card_cap'):
            reasons.append(f"card type small: cap {m['cap_pct']:g}% (floor {say('card_cap')}%)")
        if m['n_lines'] > lim('card_lines'):
            reasons.append(f"card has {m['n_lines']} lines (ceiling {say('card_lines')})")
        if m['words'] > lim('card_words'):
            reasons.append(f"card has {m['words']} words (ceiling {say('card_words')})")
    return reasons


def frame_measures(im, raw):
    """One still -> (measures, picture, OCR lines, picture aspect). Letterbox or pillarbox bars (composition.find_pad)
    are cut off first and recorded as m['pad'] (% of the frame, top/right/bottom/left); everything else is measured on
    the picture inside them. raw: the OCR lines in fractions of the full frame, or None when OCR did not run (then
    there are no text measures and no objects)."""
    im = im.convert('RGB')
    pad = composition.find_pad([composition.pad_size(im)])
    pic = composition.crop(im, pad); aspect = pic.width / pic.height
    m = composition.measure(pic); m['pad'] = [round(100 * x, 1) for x in pad]
    if raw is None:
        return m, pic, [], aspect
    raw = composition.crop_lines(raw, pad)
    m.update(composition.text_measures(raw, aspect))
    m['aspect'] = round(aspect, 4)
    m['objects'], m['floating'], m['floating_area'] = composition.objects(m['masses'], m['boxes'], aspect)
    return m, pic, raw, aspect


def debug_image(pic, path, out_dir):
    a = composition.small(pic); _, _, bg = composition.masks(a)
    vis = a.copy(); vis[bg] = vis[bg] * 0.35 + np.array([255, 0, 200]) * 0.65
    Image.fromarray(vis.astype(np.uint8)).resize((480, round(480 * a.shape[0] / a.shape[1])), Image.NEAREST).save(
        os.path.join(out_dir, os.path.splitext(os.path.basename(path))[0] + '_mask.png'))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('inputs', nargs='+'); ap.add_argument('--baseline')
    ap.add_argument('--role', default='auto', choices=['auto', 'card', *ROLES])
    ap.add_argument('--roles')
    ap.add_argument('--ocr', default='auto', choices=['auto', 'vision', 'tesseract', 'none'])
    ap.add_argument('--json'); ap.add_argument('--debug')
    a = ap.parse_args()
    paths = []
    for p in a.inputs:
        paths += sorted(q for q in glob.glob(os.path.join(p, '*')) if q.lower().endswith(IMG_EXTS)) if os.path.isdir(p) else [p]
    if not paths:
        sys.exit('error: no images found')
    baseline = json.load(open(a.baseline)) if a.baseline else None
    roles = read_roles(a.roles)
    stray = sorted(set(roles) - {os.path.basename(p) for p in paths})
    if stray:
        print(f"warning: --roles names {len(stray)} file(s) not among the frames: {', '.join(stray[:5])}", file=sys.stderr)
    try:
        engine = text_frames.resolve_engine(a.ocr)
        texts = read_text(paths, engine)
    except (RuntimeError, text_frames.OcrError) as e:
        sys.exit(f'error: {e}')
    if a.debug:
        os.makedirs(a.debug, exist_ok=True)
    print(f"{len(paths)} frames · OCR {engine} · limits: {'corpus ' + a.baseline if baseline else 'defaults from the lab corpus (no --baseline)'}")
    th = thresholds(baseline)
    results, flagged = [], 0
    for p in paths:
        m, pic, raw, aspect = frame_measures(Image.open(p), [l for l in texts.get(p, []) if l['text'].strip()] if engine != 'none' else None)
        role = roles.get(os.path.basename(p)) or ROLE_ALIAS.get(a.role, a.role)
        if role == 'auto':
            role = role_of(pic, raw, aspect, m) if engine != 'none' else 'other'
        reasons = judge(m, role, th)
        flagged += bool(reasons)
        sb = m['subject']['box'] if m['subject'] else None
        print(f"{os.path.basename(p):28s} {role:9s} {'FLAG' if reasons else 'PASS'}  content {m['coverage']:g}% · empty {m['empty']:g}% · "
              f"{m['elements']} el · bleed {','.join(m['bleed']) or 'none'} · subject {f'{sb[2]:g}x{sb[3]:g}%' if sb else 'none'}"
              + (f" · cap {m['cap_pct']:g}% · {m['n_lines']} lines · floating {m['floating']}" if 'cap_pct' in m else '')
              + (f" · padding cut {'/'.join(f'{x:g}' for x in m['pad'])}% (top/right/bottom/left)" if any(m['pad']) else ''))
        for r in reasons:
            print(f'    - {r}')
        results.append({'file': p, 'role': role, 'role_from': 'roles' if os.path.basename(p) in roles else 'role' if a.role != 'auto' else 'auto', 'flag': bool(reasons), 'reasons': reasons, **m,
                        'limits': {k: {'value': v, 'from': s} for k, (v, s) in th.items()}})
        if a.debug:
            debug_image(pic, p, a.debug)
    print(f'{flagged} of {len(paths)} frames flagged' + ('' if baseline else ' (default limits)'))
    if a.json:
        json.dump(results, open(a.json, 'w'), indent=1)
    sys.exit(1 if flagged else 0)


if __name__ == '__main__':
    main()

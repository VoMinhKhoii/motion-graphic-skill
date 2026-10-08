#!/usr/bin/env python3
"""text_frames.py: read the text in a film at 2 fps and sort every sample into demo, text card, text over demo,
logo or end, and other. Then group the text cards and measure them.

Usage:
  text_frames.py <video> [--out text.json] [--fps 2] [--ocr auto|vision|tesseract|none] [--fast] [--keep-frames DIR]

OCR engines, in the order "auto" tries them:
  vision     macOS Vision through ocr_frames.swift, compiled with swiftc on first use into
             ~/.cache/motion-graphic/ (or $XDG_CACHE_HOME). Best quality.
  tesseract  the tesseract CLI (Linux, or macOS without Xcode tools). Weaker on stylised type.
  none       no OCR: every sample is "other" and there are no cards. aggregate.py then reports the text and demo
             shares as unavailable (null), not 0. A named engine that is missing is an error, not a fallback.
An engine that runs but fails (a non-zero exit, an unreadable frame, no result for a frame) does not count as
"no text": the film's text is marked unavailable ("ocr_status": "failed", with "ocr_error"), every sample reads
"other", aggregate.py treats it like "none", run_corpus.py re-measures it on the next run, and this script exits 2.

Output (JSON):
  {"ocr", "ocr_status" (ok | none | failed), "ocr_error" (when failed), "settings": {"fps", "fast"}, "fps", "duration",
   "samples": [{"t", "cls", "words", "lines", "line_h_pct", "top", "edge", "centred_edges", "text",
                "raw": [{"text", "conf", "box"}]}],      raw = every OCR line, before the filters below
   "cards":   [{"t", "hold", "words", "lines", "cap_pct", "text"}]}
  line_h_pct  the tallest OCR line box as a % of frame height (ascender to descender)
  cap_pct     estimated cap height as a % of frame height = 0.75 x line box height (Arial-like faces;
              about +-15% across typefaces)
  edge        share of edge pixels outside the text boxes, at 320 px wide (plain backgrounds < EDGE_PLAIN)
  hold        seconds the card stays up, in 1/fps steps

Classes (thresholds below):
  logo       in the last LOGO_TAIL of the film: at most 2 words, centred; or no text and one centred mark on a
             plain background (centred edges, or a centred low-confidence OCR read)
  text_over  a headline (line box >= HEADLINE % of height) over a busy picture or a UI
  demo       UI-dense: >= DEMO_WORDS words, or >= DEMO_LINES lines of small text
  text_card  1 to CARD_MAX_WORDS words on a plain background (edge < EDGE_PLAIN), tallest line >= CARD_MIN_H
             (smaller text on a plain background is a sparse UI: demo with 2+ lines, else other)
  other      everything else: imagery, footage, a UI with almost no text, empty frames
Failure modes: a UI with little text (a camera view, a chart, a map) reads as other; a stylised or very thin
display face can be missed by OCR and the card reads as other or logo; a text card over a photo reads as
text_over. Confirm the films you rely on by watching.
Needs ffmpeg, numpy, Pillow; swiftc (macOS) or tesseract for text.
"""
import argparse, json, os, re, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frames import probe  # noqa: E402

MIN_CONF = 0.4        # drop OCR lines below this confidence (Vision gives 0.3 to shapes it reads as text)
MIN_LINE_H = 0.9      # % of height: drop OCR lines shorter than this (noise, tiny UI labels still pass)
EDGE_STEP = 12        # luma step between neighbouring pixels (at 320 px wide) that counts as an edge; low enough
                      # to see the faint borders of a dark UI, high enough to ignore gradients
EDGE_PLAIN = 0.025    # edge share outside text below which a background counts as plain
DEMO_WORDS = 12
DEMO_LINES = 5
CARD_MAX_WORDS = 20
CARD_MIN_H = 3.2      # % of height: a text card's tallest line is at least this tall (captions are ~2.5-3%)
HEADLINE = 4.0        # % of height: a line this tall is headline-size
LOGO_TAIL = 2.5       # s, or 12% of the film if longer
CAP_RATIO = 0.75


def cache_dir():
    d = os.path.join(os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache')), 'motion-graphic')
    os.makedirs(d, exist_ok=True)
    return d


def vision_binary():
    if sys.platform != 'darwin' or not shutil.which('swiftc'):
        return None
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ocr_frames.swift')
    exe = os.path.join(cache_dir(), 'ocr_frames')
    if not os.path.exists(exe) or os.path.getmtime(exe) < os.path.getmtime(src):
        r = subprocess.run(['swiftc', '-O', src, '-o', exe], capture_output=True, text=True)
        if r.returncode:
            print('swiftc failed, falling back:', r.stderr[-300:], file=sys.stderr)
            return None
    return exe


def resolve_engine(ocr):
    """The OCR engine that will run for --ocr `ocr`. A named engine that is not available is an error, never a
    silent 'none': with no OCR every sample reads as 'other' and the text and demo shares mean nothing.
    'auto' with nothing available returns 'none'; the shares are then marked unavailable downstream."""
    if ocr == 'none':
        return 'none'
    if ocr in ('auto', 'vision') and vision_binary():
        return 'vision'
    if ocr == 'vision':
        raise RuntimeError('--ocr vision needs macOS with swiftc (xcode-select --install); use --ocr tesseract or auto')
    if shutil.which('tesseract'):
        return 'tesseract'
    if ocr == 'tesseract':
        raise RuntimeError('--ocr tesseract: the tesseract CLI is not on PATH (brew install tesseract / apt install tesseract-ocr)')
    return 'none'


class OcrError(RuntimeError):
    """The OCR engine ran but did not read every frame. The film's text is then unavailable, never 0."""


def ocr_vision(exe, paths, fast):
    r = subprocess.run([exe] + (['--fast'] if fast else []), input='\n'.join(paths), capture_output=True, text=True)
    if r.returncode:
        raise OcrError(f'Vision OCR exited {r.returncode}: {r.stderr.strip()[-300:]}')
    res = {}
    for line in r.stdout.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            raise OcrError(f'Vision OCR printed a line that is not JSON: {line[:120]!r}')
        if 'error' in d:
            raise OcrError(f"Vision OCR could not read {os.path.basename(d.get('image', '?'))}: {d['error']}")
        res[d['image']] = [{'text': l['text'], 'conf': l['conf'], 'box': l['box']} for l in d.get('lines', [])]
    missing = [p for p in paths if p not in res]
    if missing:
        raise OcrError(f'Vision OCR returned nothing for {len(missing)} of {len(paths)} frames')
    return res


def ocr_tesseract(paths):
    res = {}
    for p in paths:
        W, H = Image.open(p).size
        r = subprocess.run(['tesseract', p, '-', '--psm', '11', 'tsv'], capture_output=True, text=True)
        if r.returncode or not r.stdout.strip():  # a frame with no text still prints the TSV header
            raise OcrError(f'tesseract exited {r.returncode} on {os.path.basename(p)}: {r.stderr.strip()[-300:] or "no output"}')
        tsv = r.stdout.splitlines()
        lines = {}
        for row in tsv[1:]:
            c = row.split('\t')
            if len(c) < 12 or not c[11].strip() or float(c[10]) < 50:
                continue
            key = (c[2], c[3], c[4]); x, y, w, h = map(int, c[6:10])
            L = lines.setdefault(key, {'words': [], 'x0': x, 'y0': y, 'x1': x + w, 'y1': y + h, 'conf': []})
            L['words'].append(c[11]); L['conf'].append(float(c[10]) / 100)
            L['x0'] = min(L['x0'], x); L['y0'] = min(L['y0'], y); L['x1'] = max(L['x1'], x + w); L['y1'] = max(L['y1'], y + h)
        res[p] = [{'text': ' '.join(L['words']), 'conf': round(sum(L['conf']) / len(L['conf']), 2),
                   'box': [L['x0'] / W, L['y0'] / H, (L['x1'] - L['x0']) / W, (L['y1'] - L['y0']) / H]} for L in lines.values()]
    return res


def edge_share(path, boxes):
    """path: an image file or a PIL image (check_frames.py passes the picture inside any padding)."""
    im = (path if isinstance(path, Image.Image) else Image.open(path)).convert('L'); W = 320; H = max(1, round(im.height * W / im.width))
    g = np.asarray(im.resize((W, H), Image.BILINEAR), np.float32)
    mag = np.zeros_like(g); mag[:, 1:] += np.abs(np.diff(g, axis=1)); mag[1:, :] += np.abs(np.diff(g, axis=0))
    edges = mag > EDGE_STEP
    keep = np.ones_like(edges)
    for x, y, w, h in boxes:
        keep[max(0, int((y - 0.01) * H)):int((y + h + 0.01) * H) + 1, max(0, int((x - 0.01) * W)):int((x + w + 0.01) * W) + 1] = False
    e = edges & keep
    centre = e[H // 4:3 * H // 4, W // 4:3 * W // 4].sum()
    return float(e.sum() / max(1, keep.sum())), float(centre / max(1, e.sum()))


def classify(lines, edge, centred_edges, t, dur, marks=()):
    words = sum(len(l['text'].split()) for l in lines)
    hs = sorted(l['box'][3] * 100 for l in lines)
    big = hs[-1] if hs else 0.0
    small = [h for h in hs if h < HEADLINE]
    tail = t >= dur - max(LOGO_TAIL, 0.12 * dur)
    plain = edge < EDGE_PLAIN
    centred = all(abs(l['box'][0] + l['box'][2] / 2 - 0.5) < 0.15 for l in lines)
    mark = (edge > 0.002 and centred_edges > 0.8) or (marks and all(abs(l['box'][0] + l['box'][2] / 2 - 0.5) < 0.15 for l in marks))
    if tail and ((0 < words <= 2 and centred) or (words == 0 and plain and mark)):
        return 'logo'
    dense = words >= DEMO_WORDS or len(small) >= DEMO_LINES
    if dense:
        return 'text_over' if big >= HEADLINE and big >= 2.5 * float(np.median(hs)) else 'demo'
    if 0 < words <= CARD_MAX_WORDS and plain:
        if big >= CARD_MIN_H:
            return 'text_card'
        return 'demo' if len(lines) >= 2 else 'other'  # small labels on a flat UI
    if big >= HEADLINE and words <= CARD_MAX_WORDS:
        return 'text_over'
    return 'other'


def norm_words(s):
    return set(re.findall(r'\w+', s.lower()))


def group_cards(samples, step, bounds=()):
    """Merge consecutive text-card samples into cards. Two samples are one card when no shot boundary lies
    between them and either the words overlap (same text, or text typed on/off) or the tallest line sits in the
    same place at the same size (a counter or a word that changes in place)."""
    cards = []
    for s in samples:
        if s['cls'] != 'text_card':
            continue
        w = norm_words(s['text'])
        c = cards[-1] if cards else None
        if c and abs(s['t'] - c['_end']) < step * 1.5 and not any(c['_end'] < b <= s['t'] for b in bounds):
            cw = norm_words(c['text'])
            same_words = w and cw and (len(w & cw) / len(w | cw) >= 0.5 or w <= cw or cw <= w)
            same_place = abs(s['top'] - c['_top']) < 0.03 and abs(s['line_h_pct'] - c['_h']) < 0.2 * max(c['_h'], 0.1)
            if same_words or same_place:
                c['_end'] = s['t']; c['_n'] += 1
                if s['words'] > c['words']:
                    c.update(words=s['words'], lines=s['lines'], text=s['text'])
                c['cap_pct'] = max(c['cap_pct'], round(CAP_RATIO * s['line_h_pct'], 1))
                continue
        cards.append({'t': s['t'], '_end': s['t'], '_n': 1, '_top': s['top'], '_h': s['line_h_pct'], 'words': s['words'],
                      'lines': s['lines'], 'cap_pct': round(CAP_RATIO * s['line_h_pct'], 1), 'text': s['text']})
    for c in cards:
        c['hold'] = round(c.pop('_n') * step, 2)
        for k in ('_end', '_top', '_h'):
            c.pop(k)
    return cards


def analyze(video, fps=2, ocr='auto', fast=False, keep=None):
    engine = resolve_engine(ocr)  # before any work: a missing named engine fails at once
    info = probe(video); dur = info['duration']
    tmp = keep or tempfile.mkdtemp(prefix='textframes_')
    os.makedirs(tmp, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f"fps={fps},scale='if(gt(iw,ih),-2,720)':'if(gt(iw,ih),720,-2)'",
                    '-q:v', '3', os.path.join(tmp, 'f%05d.jpg')], check=True)
    paths = sorted(os.path.join(tmp, p) for p in os.listdir(tmp) if p.endswith('.jpg'))
    res, status, error = {}, ('none' if engine == 'none' else 'ok'), None
    try:
        if not paths and engine != 'none':
            raise OcrError('ffmpeg extracted no frames')
        if engine == 'vision':
            exe = vision_binary()
            if not exe:
                raise OcrError('the Vision helper could not be built')
            res = ocr_vision(exe, paths, fast)
        elif engine == 'tesseract':
            res = ocr_tesseract(paths)
    except OcrError as e:  # the text is unavailable for this film: never read it as "no text"
        res, status, error = {}, 'failed', str(e)
        print(f'WARNING: {os.path.basename(video)}: OCR failed, text unavailable: {error}', file=sys.stderr)
    samples = []
    for k, p in enumerate(paths):
        raw = [{'text': l['text'], 'conf': l['conf'], 'box': [round(v, 4) for v in l['box']]} for l in res.get(p, []) if l['text'].strip()]
        edge, centred = edge_share(p, [l['box'] for l in raw if l['conf'] >= 0.3])
        samples.append({'t': round(k / fps, 2), 'edge': round(edge, 4), 'centred_edges': round(centred, 3), 'raw': raw})
    if not keep:
        shutil.rmtree(tmp, ignore_errors=True)
    tx = {'ocr': engine, 'ocr_status': status, 'settings': {'fps': fps, 'fast': bool(fast)}, 'fps': fps,
          'duration': round(dur, 2), 'aspect': round(info['w'] / info['h'], 4), 'samples': samples}
    if error:
        tx['ocr_error'] = error
    return reclassify(tx)


def has_text(tx):
    """True when the film's text was measured: an engine ran and read every frame. Older text.json files have no
    ocr_status; theirs is taken from the engine name."""
    return tx['ocr'] != 'none' and tx.get('ocr_status', 'ok') == 'ok'


def reclassify(tx, bounds=()):
    """Fill each sample's class and text measures from its raw OCR lines, and group the cards. Cheap, so
    aggregate.py calls it again with the film's shot boundaries and the current thresholds."""
    ar = tx.get('aspect', 16 / 9)
    measured = has_text(tx)
    for s in tx['samples']:
        lines = [l for l in s['raw'] if l['conf'] >= MIN_CONF and l['box'][3] * 100 >= MIN_LINE_H
                 and not (len(l['text']) >= 3 and l['box'][3] > 1.5 * l['box'][2] * ar)]  # vertical text (a rotated disclaimer)
        marks = [l for l in s['raw'] if l not in lines]  # low-confidence reads: often a logo mark or stylised word
        s.update(cls=classify(lines, s['edge'], s['centred_edges'], s['t'], tx['duration'], marks) if measured else 'other',
                 words=sum(len(l['text'].split()) for l in lines), lines=len(lines),
                 line_h_pct=round(max((l['box'][3] * 100 for l in lines), default=0.0), 1),
                 top=round(max(lines, key=lambda l: l['box'][3])['box'][1], 3) if lines else 0.0,
                 text=' / '.join(l['text'] for l in lines)[:200])
    tx['cards'] = group_cards(tx['samples'], 1 / tx['fps'], bounds) if measured else []
    return tx


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('--out'); ap.add_argument('--fps', type=float, default=2)
    ap.add_argument('--ocr', default='auto', choices=['auto', 'vision', 'tesseract', 'none'])
    ap.add_argument('--fast', action='store_true'); ap.add_argument('--keep-frames')
    a = ap.parse_args()
    r = analyze(a.video, a.fps, a.ocr, a.fast, a.keep_frames)
    if a.out:
        json.dump(r, open(a.out, 'w'), ensure_ascii=False)
    mix = {}
    for s in r['samples']:
        mix[s['cls']] = mix.get(s['cls'], 0) + 1
    print(f"{os.path.basename(a.video)}: ocr={r['ocr']} ({r['ocr_status']}) {mix} cards={len(r['cards'])}")
    if r['ocr_status'] == 'failed':
        sys.exit(2)


if __name__ == '__main__':
    main()

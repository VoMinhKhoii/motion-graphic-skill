#!/usr/bin/env python3
"""check_clips.py: run transitions.py and text_frames.py on the synthetic clips and score them against truth.json.

Usage:
  make_clips.py /tmp/synthetic && check_clips.py /tmp/synthetic [--ocr auto|vision|tesseract]

Prints, per clip, each expected transition with what was found (type, start, length), the share of camera
windows and text samples that match, and a final line with transition precision and recall. Exit code 1 if any
expected transition is missed or mislabelled.
Matching: a found transition matches an expected one if the type is the same and the start is within 0.15 s.
Camera and text samples within 0.25 s of a boundary are not scored (they straddle two shots).
"""
import json, os, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import text_frames, transitions  # noqa: E402


def main():
    d = sys.argv[1]; ocr = sys.argv[sys.argv.index('--ocr') + 1] if '--ocr' in sys.argv else 'auto'
    truth = json.load(open(os.path.join(d, 'truth.json')))
    tp = fp = fn = 0; bad = False
    for clip, t in truth.items():
        v = os.path.join(d, clip)
        r = transitions.analyze(v)
        found = list(r['transitions'])
        print(f'== {clip}')
        for kind, t0, dur in t['transitions']:
            m = next((x for x in found if x['type'] == kind and abs(x['t'] - t0) <= 0.15), None)
            near = min(found, key=lambda x: abs(x['t'] - t0), default=None)
            if m:
                tp += 1; found.remove(m)
                print(f'  ok    {kind:9s} at {t0:4.1f}s len {dur:.2f}  -> {m["t"]:.2f}s len {m["dur"]:.2f} (score {m["score"]})')
            else:
                fn += 1; bad = True
                print(f'  MISS  {kind:9s} at {t0:4.1f}s len {dur:.2f}  -> nearest: {near and (near["type"], near["t"], near["dur"])}')
        for x in found:
            fp += 1; print(f'  EXTRA {x["type"]} at {x["t"]}s len {x["dur"]}')
        bounds = [b[1] for b in t['transitions']] + [b[1] + b[2] for b in t['transitions']]
        clear = lambda a, b: all(not (a - 0.25 < x < b + 0.25) for x in bounds)
        if 'camera' in t:
            hit = tot = 0
            for a, b, state in t['camera']:
                for w in r['windows']:
                    if a <= w['t'] and w['t'] + 0.5 <= b and clear(w['t'], w['t'] + 0.5):
                        tot += 1; hit += w['state'] == state
            print(f'  camera windows correct: {hit}/{tot}')
        if 'classes' in t:
            x = text_frames.analyze(v, ocr=ocr)
            hit = tot = 0
            for a, b, cls in t['classes']:
                for s in x['samples']:
                    if a <= s['t'] < b and clear(s['t'], s['t']):
                        tot += 1; hit += s['cls'] == cls
            print(f'  text samples correct ({x["ocr"]}): {hit}/{tot}; cards: {[(c["words"], c["lines"], c["hold"], c["cap_pct"]) for c in x["cards"]]}'
                  f' expected {t["card"]}')
    prec = tp / max(1, tp + fp); rec = tp / max(1, tp + fn)
    print(f'transitions: precision {prec:.2f}, recall {rec:.2f} ({tp} matched, {fp} extra, {fn} missed)')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

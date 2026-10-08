#!/usr/bin/env python3
"""aggregate.py: merge every film's measurements into corpus.json, with medians per account and overall.

Usage:
  aggregate.py <out_dir> [--include-history]
      reads <out_dir>/films/<id>/{meta,transitions,text,stats,composition}.json, writes <out_dir>/corpus.json

Which films: only the ids run_corpus.py's last run lists as succeeded in <out_dir>/run.json (the run manifest).
Film folders left by earlier runs, and films that failed this run, are not in the numbers; corpus.json lists them
under "inclusion". --include-history aggregates every complete film folder instead (say, to pool several runs
with different --only selections); the report then says so. With no manifest, it stops unless --include-history.

Per film:
  timeline       one category per 0.5 s: demo, text_card, text_over, logo, other, transition
                 (the text class of the sample, replaced by "transition" where a dissolve/push/zoom/other
                 transition covers at least half of the slot)
  share          share of runtime per category (the "where the seconds go" table). Without OCR (text.json
                 "ocr": "none", or "ocr_status": "failed") only "transition" is measured: the other shares are null, the timeline slots are
                 "unmeasured", and demo_beat_s and n_cards are null. Medians skip nulls, so they cover OCR'd films only.
  cuts_per_min   shot boundaries of any type per minute; hard_cuts_per_min counts cuts only;
                 ffmpeg_cuts_per_min is analyze_video.py's scene-detect number, for comparison
  median_shot_s  median time between boundaries
  demo_beat_s    median length of an unbroken demo stretch (split by any boundary)
  cards          text cards with hold, words, lines, cap height; card_* fields are their medians
  mix            transitions per type: count and median length
  camera         share of 0.5 s windows per camera state
  composition    from composition.json (null when missing): each sample tagged with its timeline category as its
                 role (transition samples are left out: they are blends of two pictures), and the per-role medians
Per account and overall: the median of each per-film number (shares included), and the transition mix pooled
over all films (share of all transitions, median length per type). camera_pooled is the share of all 0.5 s
windows: a state that every film uses a little (a zoom, a pan) has a median of 0 but shows up there. Medians, because one long film should not
outweigh five short ones.
composition (per account and overall): by_role (all, demo, text_card, text_over, logo, other) gives samples, films and
p10 / p25 / median / p90 of each COMP_KEYS measure, weighting every film equally within a role (a 5-minute film does not
outweigh a 20 s one); padded (films whose letterbox or pillarbox bars composition.py cut off); coverage_hist and
empty_hist (share of samples per 10% bin, all roles); text_grid (share of OCR lines whose centre falls in each cell of
a 3 x 3 grid, row-major from the top left, by role). check_frames.py reads overall.composition.by_role as its baseline.
"""
import argparse, json, os, statistics, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_frames  # noqa: E402

CATS = ['demo', 'text_card', 'text_over', 'logo', 'other', 'transition']
TTYPES = ['cut', 'dissolve', 'push', 'zoom_in', 'zoom_out', 'other']
CAMS = ['still', 'inframe', 'pan', 'zoom_in', 'zoom_out', 'transition']
ROLES = ['all', 'demo', 'text_card', 'text_over', 'logo', 'other']
COMP_KEYS = ['coverage', 'empty', 'elements', 'bleed_n', 'subject_area', 'subject_w', 'subject_h', 'text_pct', 'cap_pct', 'line_h_med',
             'n_lines', 'words', 'floating', 'floating_area']


def med(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 2) if xs else None


def load(p):
    return json.load(open(p)) if os.path.exists(p) else None


def wpct(vals, q):
    """Weighted percentile of [(value, weight)]."""
    vals = sorted(vals); tot = sum(w for _, w in vals); acc = 0.0
    for v, w in vals:
        acc += w
        if acc >= q * tot - 1e-9:
            return round(v, 2)
    return round(vals[-1][0], 2)


def comp_rows(cp, timeline, measured):
    """One compact row per composition sample, tagged with the sample's timeline category as its role."""
    rows = []
    for k, s in enumerate(cp['samples']):
        cat = timeline[k] if k < len(timeline) else None
        if cat == 'transition':
            continue
        sb = s.get('subject') or {}
        rows.append({'role': cat if measured else None, 'coverage': s['coverage'], 'empty': s['empty'], 'elements': s['elements'],
                     'bleed_n': len(s['bleed']), 'subject_area': sb.get('area', 0.0), 'subject_w': (sb.get('box') or [0, 0, 0, 0])[2],
                     'subject_h': (sb.get('box') or [0, 0, 0, 0])[3],
                     'text_pct': s.get('text_pct'), 'cap_pct': s.get('cap_pct') or None, 'line_h_med': s.get('line_h_med'),
                     'n_lines': s.get('n_lines'), 'words': s.get('words'),
                     'floating': s.get('floating'), 'floating_area': s.get('floating_area'), 'cells': s.get('cells') or []})
    return rows


def comp_summary(films):
    """by_role percentiles (each film weighted 1 within a role), histograms and the 3 x 3 text grid."""
    films = [f for f in films if f.get('composition')]
    if not films:
        return None
    by_role, grid = {}, {}
    for role in ROLES:
        per = [[r for r in f['composition']['samples'] if role == 'all' or r['role'] == role] for f in films]
        per = [rs for rs in per if rs]
        if not per:
            continue
        out = {'samples': sum(len(rs) for rs in per), 'films': len(per)}
        for k in COMP_KEYS:
            vals = [(r[k], 1 / len(rs)) for rs in per for r in rs if r[k] is not None]
            out[k] = {q: wpct(vals, p) for q, p in (('p10', 0.1), ('p25', 0.25), ('median', 0.5), ('p90', 0.9))} if vals else None
        out['bleed_share'] = round(sum(sum(r['bleed_n'] > 0 for r in rs) / len(rs) for rs in per) / len(per), 3)
        by_role[role] = out
        cells = [c for rs in per for r in rs for c in r['cells']]
        grid[role] = [round(cells.count(i) / len(cells), 3) for i in range(9)] if cells else None
    rows = [r for f in films for r in f['composition']['samples']]
    hist = lambda k: [round(sum(min(int(r[k] // 10), 9) == b for r in rows) / len(rows), 3) for b in range(10)]
    return {'films': len(films), 'padded': sum(any(f['composition'].get('pad') or []) for f in films), 'by_role': by_role, 'coverage_hist': hist('coverage'), 'empty_hist': hist('empty'), 'text_grid': grid}


def film_record(d):
    meta = load(os.path.join(d, 'meta.json')); tr = load(os.path.join(d, 'transitions.json')); tx = load(os.path.join(d, 'text.json'))
    if not (meta and tr and tx):
        return None
    st = load(os.path.join(d, 'stats.json')) or {}
    dur = meta['duration']
    trans = tr['transitions']
    text_frames.reclassify(tx, [t['t'] for t in trans])  # current thresholds; cards split at shot boundaries
    spans = [(t['t'], t['t'] + t['dur']) for t in trans if t['dur'] > 0]
    timeline = []
    for s in tx['samples']:
        t0, t1 = s['t'], min(dur, s['t'] + 1 / tx['fps'])
        cover = sum(max(0, min(t1, b) - max(t0, a)) for a, b in spans)
        timeline.append('transition' if t1 > t0 and cover >= 0.5 * (t1 - t0) else s['cls'])
    n = max(1, len(timeline))
    share = {c: round(timeline.count(c) / n, 3) for c in CATS}
    ocr = text_frames.has_text(tx)
    if not ocr:  # no OCR: only transitions were measured; the text classes are unknown, not 0
        timeline = [c if c == 'transition' else 'unmeasured' for c in timeline]
        share = {c: (share[c] if c == 'transition' else None) for c in CATS}
    bounds = sorted(t['t'] + t['dur'] / 2 for t in trans)
    edges = [0.0] + bounds + [dur]
    shots = [b - a for a, b in zip(edges, edges[1:]) if b - a > 0.05]
    # demo beat: unbroken demo stretches, split at every boundary
    step = 1 / tx['fps']; beats, run, last = [], 0.0, None
    for i, c in enumerate(timeline):
        t = i * step
        crossed = last is not None and any(last < b <= t for b in bounds)
        if c == 'demo' and not crossed:
            run += step
        else:
            if run:
                beats.append(run)
            run = step if c == 'demo' else 0.0
        last = t
    if run:
        beats.append(run)
    mix = {}
    for k in TTYPES:
        ds = [t['dur'] for t in trans if t['type'] == k]
        if ds:
            mix[k] = {'n': len(ds), 'median_dur': med(ds)}
    wins = [w['state'] for w in tr['windows']]
    camera = {c: round(wins.count(c) / max(1, len(wins)), 3) for c in CAMS}
    cards = tx['cards']
    cp = load(os.path.join(d, 'composition.json'))
    comp = None
    if cp:
        rows = comp_rows(cp, timeline, ocr)
        by_role = {}
        for role in ROLES:
            rs = [r for r in rows if role == 'all' or r['role'] == role]
            if rs:
                by_role[role] = {'samples': len(rs), **{k: med([r[k] for r in rs]) for k in COMP_KEYS}}
        comp = {'by_role': by_role, 'pad': cp.get('pad'), 'samples': rows}
    return {**meta, 'timeline': timeline, 'timeline_step': step, 'share': share,
            'cuts_per_min': round(len(trans) / dur * 60, 2) if dur else None,
            'hard_cuts_per_min': round(sum(t['type'] == 'cut' for t in trans) / dur * 60, 2) if dur else None,
            'ffmpeg_cuts_per_min': st.get('cuts_per_min'), 'median_shot_s': med(shots), 'demo_beat_s': med(beats) if ocr else None,
            'n_cards': len(cards) if ocr else None, 'card_hold_s': med([c['hold'] for c in cards]), 'card_words': med([c['words'] for c in cards]),
            'card_lines': med([c['lines'] for c in cards]), 'card_cap_pct': med([c['cap_pct'] for c in cards]),
            'cards': cards, 'mix': mix, 'camera': camera, 'camera_per_s': tr['camera_per_s'],
            'transitions': [{k: t[k] for k in ('type', 't', 'dur', 'score')} for t in trans],
            'ocr': tx['ocr'] if ocr else ('failed' if tx.get('ocr_status') == 'failed' else 'none'), 'text_measured': ocr,
            'composition': comp}


def summary(films):
    out = {'films': len(films), 'films_with_ocr': sum(f['text_measured'] for f in films), 'duration_s': med([f['duration'] for f in films])}
    for k in ('cuts_per_min', 'hard_cuts_per_min', 'ffmpeg_cuts_per_min', 'median_shot_s', 'demo_beat_s',
              'card_hold_s', 'card_words', 'card_lines', 'card_cap_pct'):
        out[k] = med([f[k] for f in films])
    out['share'] = {c: med([f['share'][c] for f in films]) for c in CATS}
    out['camera'] = {c: med([f['camera'][c] for f in films]) for c in CAMS}
    tot = sum(f['duration'] for f in films) or 1  # pooled: share of all windows, so minority states still show
    out['camera_pooled'] = {c: round(sum(f['camera'][c] * f['duration'] for f in films) / tot, 3) for c in CAMS}
    total = sum(m['n'] for f in films for m in f['mix'].values())
    out['transitions'] = total
    out['mix'] = {}
    for k in TTYPES:
        ds = [t['dur'] for f in films for t in f['transitions'] if t['type'] == k]
        if ds:
            out['mix'][k] = {'n': len(ds), 'share': round(len(ds) / total, 3), 'median_dur': med(ds)}
    out['composition'] = comp_summary(films)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out_dir'); ap.add_argument('--include-history', action='store_true')
    a = ap.parse_args()
    out_dir = a.out_dir
    root = os.path.join(out_dir, 'films')
    present = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))) if os.path.isdir(root) else []
    run = load(os.path.join(out_dir, 'run.json'))  # the run manifest: selected, succeeded, failed, ocr_failed, ocr
    if a.include_history:
        ids, mode = present, 'history'
    elif run and 'succeeded' in run and isinstance(run['succeeded'], list):
        ids, mode = run['succeeded'], 'run'
    else:
        sys.exit(f'error: no run manifest in {out_dir}/run.json (run_corpus.py writes it). Re-run run_corpus.py, or pass '
                 '--include-history to aggregate every film folder, earlier runs included.')
    records = {d: film_record(os.path.join(root, d)) for d in ids}
    films = [r for r in records.values() if r]
    inclusion = {'mode': mode, 'included': [d for d in ids if records[d]],
                 'incomplete': [d for d in ids if not records[d]],  # listed, but a measurement file is missing
                 'not_included': [d for d in present if d not in ids]}
    accounts = {}
    for f in films:
        accounts.setdefault(f['account'], []).append(f)
    corpus = {'generated': time.strftime('%Y-%m-%d %H:%M'), 'run': run, 'inclusion': inclusion, 'overall': summary(films),
              'accounts': {a: summary(fs) for a, fs in sorted(accounts.items())}, 'films': films}
    json.dump(corpus, open(os.path.join(out_dir, 'corpus.json'), 'w'), ensure_ascii=False)
    o = corpus['overall']
    print(f"corpus.json: {len(films)} films ({o['films_with_ocr']} with OCR), {len(accounts)} accounts; demo {o['share']['demo']}, text card {o['share']['text_card']}, "
          f"cuts/min {o['cuts_per_min']}, transitions {o['transitions']}")
    print(f"included: {'the last run' if mode == 'run' else 'every film folder (--include-history)'}; "
          f"{len(inclusion['not_included'])} other film folders not included, {len(inclusion['incomplete'])} incomplete")


if __name__ == '__main__':
    main()

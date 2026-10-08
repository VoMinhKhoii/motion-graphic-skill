#!/usr/bin/env python3
"""report.py: a static HTML board of the corpus measurements, for a local browser. Private: nothing is uploaded.

Usage:
  report.py <out_dir> [--top 4] [--no-strips]
  open <out_dir>/index.html

Reads <out_dir>/corpus.json (from aggregate.py) and writes <out_dir>/index.html. Images are referenced relatively
(films/<stem>/strip.jpg, sheet.jpg, curves.png, strips/*.jpg), so keep the folder together and never publish it:
the strips and sheets are frames of third-party films.

Sections:
  1. Overall and per-account tables: pace, shot length, demo beat, text cards, plus stacked bars for where the
     seconds go, the transition mix (share and median length) and the camera states.
  2. Top transitions: for each type, the --top highest-scoring examples as 10 fps strips (via ../strips.py),
     from 0.2 s before to 0.2 s after. These are the ones to check by eye first.
  3. Composition: per role (all, demo, text_card, text_over, logo, other) the p10 / median / p90 of content coverage
     and the largest empty region, elements, edge bleed, subject size, cap height and floating objects; histograms
     of coverage and empty region; where text sits on a 3 x 3 grid; and one row per account. These are the
     numbers check_frames.py holds storyboard stills to.
  4. Per film: a to-scale timeline coloured by category, transitions as ticks above it (cuts as lines, gradual
     ones as spans coloured by type), the camera row below, the film's thumbnail strip, and its text cards.
"""
import argparse, html, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRIPS = os.path.join(os.path.dirname(HERE), 'strips.py')
CAT_COL = {'demo': '#3d7be0', 'text_card': '#e3a321', 'text_over': '#e3672b', 'logo': '#8a5cd6', 'other': '#a3a3a3', 'transition': '#e05595',
           'unmeasured': 'repeating-linear-gradient(45deg,#cfcfcf 0 3px,transparent 3px 6px)'}
SVG_COL = {'unmeasured': '#e2e2e2'}  # SVG fills take no CSS gradients
TR_COL = {'cut': 'var(--fg)', 'dissolve': '#1aa39a', 'push': '#3a9a3a', 'zoom_in': '#d64545', 'zoom_out': '#8a5cd6', 'other': '#9a9a9a'}
CAM_COL = {'still': '#d9d9d9', 'inframe': '#9cc3f0', 'pan': '#3a9a3a', 'zoom_in': '#d64545', 'zoom_out': '#8a5cd6', 'transition': '#e05595'}
E = html.escape

CSS = """
:root{--bg:#f7f6f3;--fg:#1d1d1b;--mut:#6b6a66;--line:#dedcd6;--card:#fff}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ecebe7;--mut:#9b9a95;--line:#34332f;--card:#1f1f1d}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 -apple-system,system-ui,sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px 80px}h1{font-size:24px;margin:0 0 4px}h2{font-size:18px;margin:36px 0 10px}
h3{font-size:15px;margin:0}.mut{color:var(--mut)}a{color:inherit}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
th{font-weight:600;font-size:12px;color:var(--mut)}.scroll{overflow-x:auto}
.bar{display:flex;height:14px;min-width:180px;border-radius:3px;overflow:hidden}.bar span{display:block;height:100%}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;margin:6px 0}.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:-1px}
.film{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:14px;margin:12px 0}
.film svg{width:100%;height:auto;display:block}.film img.strip{width:100%;display:block;margin-top:4px;border-radius:3px}
.tr{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;align-items:start}.tr figure{min-width:0;margin:0;background:var(--card);border:1px solid var(--line);border-radius:8px;padding:8px}
.tr img{max-width:100%;height:auto;display:block}figcaption{font-size:12px;color:var(--mut);margin-top:4px}
.note{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:12px 0}
details summary{cursor:pointer;color:var(--mut);font-size:12px;margin-top:6px}
.hist{display:flex;align-items:flex-end;gap:3px;height:90px;max-width:420px;border-bottom:1px solid var(--line)}.hist div{flex:1;background:#3d7be0;min-height:1px}
.hlab{display:flex;gap:3px;max-width:420px;font-size:10px;color:var(--mut)}.hlab span{flex:1;text-align:center}
.g3{display:grid;grid-template-columns:repeat(3,44px);grid-template-rows:repeat(3,25px);gap:2px;margin:4px 0}.g3 div{border:1px solid var(--line);font-size:10px;display:flex;align-items:center;justify-content:center}
.cols{display:flex;flex-wrap:wrap;gap:16px 36px;align-items:flex-start}
"""


def bar(parts, colors, labels=None):
    tot = 1 if None in parts.values() else (sum(v or 0 for v in parts.values()) or 1)  # unmeasured parts stay blank
    segs = ''.join(f'<span style="width:{100 * (v or 0) / tot:.2f}%;background:{colors[k]}" title="{E(k)} {labels[k] if labels else f"{100 * (v or 0) / tot:.0f}%"}"></span>'
                   for k, v in parts.items() if v)
    return f'<div class="bar">{segs}</div>'


def legend(colors, labels=None):
    return '<div class="legend">' + ''.join(f'<span><i style="background:{c}"></i>{E(labels.get(k, k) if labels else k)}</span>' for k, c in colors.items()) + '</div>'


def fmt(v, suf=''):
    return '–' if v is None else f'{v:g}{suf}'


def pct(v):
    return '–' if v is None else f'{100 * v:.0f}%'


def summary_rows(groups):
    rows = []
    for name, s in groups:
        mix_lbl = {k: f"{100 * m['share']:.0f}%, {m['median_dur']:g}s" for k, m in s['mix'].items()}
        rows.append(f"<tr><td><b>{E(name)}</b><div class='mut'>{s['films']} film{'s' if s['films'] != 1 else ''}, median {fmt(s['duration_s'], ' s')}</div></td>"
                    f"<td>{fmt(s['cuts_per_min'])}<div class='mut'>cuts only {fmt(s['hard_cuts_per_min'])}</div></td>"
                    f"<td>{fmt(s['median_shot_s'], ' s')}</td><td>{fmt(s['demo_beat_s'], ' s')}</td>"
                    f"<td>{pct(s['share']['demo'])} / {pct(s['share']['text_card'])} / {pct(s['share']['logo'])}{bar(s['share'], CAT_COL)}</td>"
                    f"<td>{fmt(s['card_hold_s'], ' s')} · {fmt(s['card_words'])} w · {fmt(s['card_cap_pct'], '%')}</td>"
                    f"<td>{s['transitions']}{bar({k: m['n'] for k, m in s['mix'].items()}, TR_COL, mix_lbl)}</td>"
                    f"<td>{pct(s['camera_pooled']['still'])} still · {pct(s['camera_pooled']['pan'] + s['camera_pooled']['zoom_in'] + s['camera_pooled']['zoom_out'])} moving"
                    f"{bar(s['camera_pooled'], CAM_COL)}</td></tr>")
    head = ('<tr><th>group</th><th>boundaries / min</th><th>median shot</th><th>demo beat</th><th>demo / card / logo</th>'
            '<th>text card: hold · words · cap</th><th>transitions</th><th>camera (all windows)</th></tr>')
    return f'<div class="scroll"><table>{head}{"".join(rows)}</table></div>'


def mix_table(s):
    rows = ''.join(f"<tr><td><i style='display:inline-block;width:10px;height:10px;background:{TR_COL[k]};margin-right:6px'></i>{k}</td>"
                   f"<td>{m['n']}</td><td>{100 * m['share']:.0f}%</td><td>{m['median_dur']:g} s</td></tr>" for k, m in s['mix'].items())
    return f'<table style="max-width:520px"><tr><th>type</th><th>count</th><th>share</th><th>median length</th></tr>{rows}</table>'


def run_note(c):
    """Which films these numbers cover, from corpus.json's own inclusion record, plus the last run's failures and
    the OCR engine. Shown first, so partial or pooled results never pass for the run's full corpus."""
    r, o, inc = c.get('run'), c['overall'], c.get('inclusion') or {}
    engines = sorted({f['ocr'] for f in c['films']})
    lines = []
    if inc.get('mode') == 'history':
        lines.append(f"<b>These numbers pool every measured film folder ({len(inc['included'])} films), earlier runs included "
                     f"(aggregate.py --include-history).</b>")
    elif inc.get('mode') == 'run':
        lines.append(f"These numbers cover the last run's {len(inc['included'])} succeeded films"
                     + (f" ({r['when']}, OCR {E(r['ocr'])})" if r else '') + '.')
    if r and isinstance(r.get('selected'), list):
        lines.append(f"Last run: {len(r['selected'])} films selected, {len(r['succeeded'])} succeeded, {len(r['failed'])} failed"
                     + (f" · --only {E(r['only'])}" if r.get('only') else ''))
        if r['failed']:
            in_numbers = [f for f in r['failed'] if f in inc.get('included', [])]
            lines.append(f"<b>Failed in the last run ({'not' if not in_numbers else 'but still'} in these numbers):</b> "
                         + ', '.join(E(f) for f in r['failed']))
        if r.get('ocr_failed'):
            lines.append('<b>OCR failed (text unavailable, shown as –):</b> ' + ', '.join(E(f) for f in r['ocr_failed']))
    if inc.get('not_included'):
        lines.append(f"Not in these numbers: {len(inc['not_included'])} other film folders in films/ (earlier runs or other selections).")
    if inc.get('incomplete'):
        lines.append('<b>Listed but incomplete (a measurement file is missing; not in these numbers):</b> '
                     + ', '.join(E(f) for f in inc['incomplete']))
    lines.append(f"OCR engine per film: {', '.join(E(e) for e in engines) or 'none'} · {o.get('films_with_ocr', 0)} of {o['films']} films have text measures")
    if o.get('films_with_ocr', 0) < o['films']:
        lines.append('<b>Films without OCR, or whose OCR failed, have no demo, text card, text-over, logo or other share: shown as – (unavailable), never 0.</b>')
    warn = (r and (r.get('failed') or r.get('ocr_failed'))) or inc.get('incomplete') or inc.get('mode') == 'history' \
        or o.get('films_with_ocr', 0) < o['films']
    return f"<div class='note' style=\"{'border-color:#d64545' if warn else ''}\">{'<br>'.join(lines)}</div>"


def timeline_svg(f):
    W, dur = 1000.0, max(f['duration'], 0.1)
    X = lambda t: W * t / dur
    step = f['timeline_step']; out = []
    for i, c in enumerate(f['timeline']):
        out.append(f'<rect x="{X(i * step):.2f}" y="22" width="{X(step) + 0.6:.2f}" height="26" fill="{SVG_COL.get(c, CAT_COL.get(c))}"><title>{i * step:.1f}s {c}</title></rect>')
    for t in f['transitions']:
        col = TR_COL[t['type']]
        if t['dur'] == 0:
            out.append(f'<line x1="{X(t["t"]):.2f}" x2="{X(t["t"]):.2f}" y1="2" y2="20" stroke="{col}" stroke-width="1.5"><title>{t["t"]}s cut</title></line>')
        else:
            out.append(f'<rect x="{X(t["t"]):.2f}" y="6" width="{max(2, X(t["dur"])):.2f}" height="12" rx="2" fill="{col}"><title>{t["t"]}s {t["type"]} {t["dur"]}s</title></rect>')
    for s, c in enumerate(f['camera_per_s']):
        out.append(f'<rect x="{X(s):.2f}" y="52" width="{X(min(1, dur - s)) + 0.4:.2f}" height="7" fill="{CAM_COL[c]}"><title>{s}s camera {c}</title></rect>')
    tick = 1 if dur <= 15 else 5 if dur <= 90 else 30
    for s in range(0, int(dur) + 1, tick):
        out.append(f'<text x="{X(s):.1f}" y="74" font-size="10" fill="currentColor" opacity=".6">{s}s</text>')
    return f'<svg viewBox="0 0 {W:.0f} 78" role="img" aria-label="timeline">{"".join(out)}</svg>'


def q3(d, suf='%'):
    return '–' if not d else f"{d['p10']:g} / <b>{d['median']:g}</b> / {d['p90']:g}{suf}"


def hist(vals, label):
    bars = ''.join(f"<div style='height:{100 * v / (max(vals) or 1):.0f}%' title='{10 * i}-{10 * i + 10}%: {100 * v:.0f}% of samples'></div>" for i, v in enumerate(vals))
    labs = ''.join(f'<span>{10 * i}</span>' for i in range(10))
    return f"<div><b>{label}</b><div class='hist'>{bars}</div><div class='hlab'>{labs}</div></div>"


def grid3(g, role):
    if not g:
        return ''
    cells = ''.join(f"<div style='background:rgba(227,163,33,{min(1, 2.5 * v):.2f})'>{100 * v:.0f}%</div>" for v in g)
    return f"<div><b>{E(role)}</b><div class='g3'>{cells}</div></div>"


def comp_section(c):
    """The composition numbers: per role, histograms, text positions, per account."""
    o = c['overall'].get('composition')
    if not o:
        return '<div class="note">No composition.json in these films: re-run run_corpus.py to measure composition.</div>'
    head = ('<tr><th>role</th><th>samples · films</th><th>content % p10 / med / p90</th><th>largest empty %</th><th>elements</th>'
            '<th>edge bleed</th><th>subject area %</th><th>cap % (with text)</th><th>floating objects</th></tr>')
    rows = ''.join(f"<tr><td><b>{E(role)}</b></td><td>{r['samples']} · {r['films']}</td><td>{q3(r['coverage'])}</td><td>{q3(r['empty'])}</td>"
                   f"<td>{q3(r['elements'], '')}</td><td>{pct(r['bleed_share'])} of samples</td><td>{q3(r['subject_area'])}</td>"
                   f"<td>{q3(r['cap_pct'])}</td><td>{q3(r['floating'], '')}</td></tr>" for role, r in o['by_role'].items())
    acc = ''.join(f"<tr><td>{E(name)}</td><td>{q3((s['composition'] or {}).get('by_role', {}).get('all', {}).get('coverage'))}</td>"
                  f"<td>{q3((s['composition'] or {}).get('by_role', {}).get('all', {}).get('empty'))}</td>"
                  f"<td>{pct((s['composition'] or {}).get('by_role', {}).get('all', {}).get('bleed_share'))}</td></tr>"
                  for name, s in c['accounts'].items() if s.get('composition'))
    grids = ''.join(grid3(o['text_grid'].get(r), r) for r in ('all', 'text_card', 'text_over', 'demo', 'logo'))
    return (f"<div class='mut'>Measured per 2 fps sample (composition.py); transition samples left out; each film weighs the same within a role. "
            f"Content = not background (background = smooth area connected to the frame edge). Largest empty = the biggest rectangle of background. "
            f"Floating = non-text elements that touch no edge.</div>"
            f"<div class='scroll'><table>{head}{rows}</table></div>"
            f"<div class='cols' style='margin-top:14px'>{hist(o['coverage_hist'], 'content coverage, % of samples per 10% bin')}"
            f"{hist(o['empty_hist'], 'largest empty region, % of samples per 10% bin')}</div>"
            f"<h3 style='margin-top:18px'>Where text sits (share of OCR lines per third of the frame)</h3><div class='cols'>{grids}</div>"
            f"<h3 style='margin-top:18px'>Per account, all samples</h3><div class='scroll'><table style='max-width:760px'><tr><th>account</th>"
            f"<th>content % p10 / med / p90</th><th>largest empty %</th><th>edge bleed</th></tr>{acc}</table></div>")


def film_block(f):
    st = f"films/{E(f['stem'])}"
    link = f"<a href='{E(f['url'])}'>{E(f['title'])}</a>" if f.get('url') else E(f['title'])
    ncards = '–' if f.get('n_cards') is None else len(f['cards'])
    cards = ''.join(f"<li>{c['t']:g}s, {c['hold']:g} s, {c['words']} words, {c['lines']} lines, cap {c['cap_pct']:g}%: “{E(c['text'][:90])}”</li>" for c in f['cards'])
    mix = ', '.join(f"{k} {m['n']} ({m['median_dur']:g}s)" for k, m in f['mix'].items()) or 'none'
    extra = ''.join(f"<a href='{st}/{n}'>{n}</a> " for n in ('sheet.jpg', 'curves.png') if os.path.exists(os.path.join(OUT, 'films', f['stem'], n)))
    return (f"<div class='film' id='{E(f['stem'])}'><h3>{E(f['account'])} · {link}</h3>"
            f"<div class='mut'>{f['duration']:g} s · {fmt(f['cuts_per_min'])} boundaries/min · demo {pct(f['share']['demo'])} · "
            f"card {pct(f['share']['text_card'])} · logo {pct(f['share']['logo'])} · demo beat {fmt(f['demo_beat_s'], ' s')} · "
            f"transitions: {mix} · ocr {f['ocr']}{comp_line(f)}</div>{timeline_svg(f)}"
            f"<img class='strip' loading='lazy' src='{st}/strip.jpg' alt='thumbnails across the film'>"
            f"<details><summary>{ncards} text cards · {extra}</summary><ul>{cards}</ul></details></div>")


def comp_line(f):
    a = ((f.get('composition') or {}).get('by_role') or {}).get('all')
    return f" · content {fmt(a['coverage'], '%')}, largest empty {fmt(a['empty'], '%')} (medians)" if a else ''


def top_transitions(films, top, make):
    os.makedirs(os.path.join(OUT, 'strips'), exist_ok=True)
    blocks = []
    for kind in ['cut', 'dissolve', 'push', 'zoom_in', 'zoom_out', 'other']:
        cands = [(t, f) for f in films for t in f['transitions'] if t['type'] == kind]
        key = (lambda tf: tf[0]['score']) if kind != 'other' else (lambda tf: tf[0]['dur'])
        cands.sort(key=key, reverse=True)
        picked = []
        for scope in ('account', 'stem'):  # spread the examples: one per account first, then one per film
            for t, f in cands:
                if len(picked) == top:
                    break
                if all(f[scope] != g[scope] for _, g in picked) and all(t is not u for u, _ in picked):
                    picked.append((t, f))
        if not picked:
            continue
        figs = []
        for i, (t, f) in enumerate(picked):
            name = f"strips/{kind}__{f['stem'].lstrip('@')}__{t['t']:g}.jpg"
            t0 = max(0, t['t'] - 0.2); t1 = min(f['duration'] - 0.05, t['t'] + t['dur'] + 0.2)
            times = [round(t0 + k * 0.1, 2) for k in range(int((t1 - t0) / 0.1) + 1)][:16]
            if make and not os.path.exists(os.path.join(OUT, name)) and os.path.exists(STRIPS):
                subprocess.run([sys.executable, STRIPS, f['video'], os.path.join(OUT, name), *map(str, times), '--h', '150', '--max-w', '1800'],
                               capture_output=True)
            if os.path.exists(os.path.join(OUT, name)):
                figs.append(f"<figure><img loading='lazy' src='{name}' alt='{kind} strip'><figcaption>{E(f['account'])} · "
                            f"<a href='#{E(f['stem'])}'>{E(f['title'][:60])}</a> · {t['t']:g}s, {t['dur']:g}s, score {t['score']:g}</figcaption></figure>")
        blocks.append(f"<h3 style='margin-top:18px'>{kind} <span class='mut'>({len(cands)} found)</span></h3><div class='tr'>{''.join(figs)}</div>")
    return ''.join(blocks)


def main():
    global OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('out_dir'); ap.add_argument('--top', type=int, default=4); ap.add_argument('--no-strips', action='store_true')
    a = ap.parse_args(); OUT = a.out_dir
    c = json.load(open(os.path.join(OUT, 'corpus.json')))
    films = sorted(c['films'], key=lambda f: (f['account'].lower(), f['duration']))
    groups = [('all films', c['overall'])] + list(c['accounts'].items())
    body = f"""<main><h1>Reference corpus</h1>
<div class="mut">{c['overall']['films']} films · {len(c['accounts'])} accounts · generated {E(c['generated'])} · private: frames of third-party films, do not publish</div>
{run_note(c)}
<div class="note">These classes are a first pass, measured from pixels and OCR. Confirm the 15 to 30 films you will lean on by watching them,
starting with the top-transition strips below. "boundaries / min" counts every shot boundary (cuts and gradual transitions);
"demo beat" is the median unbroken demo stretch; "cap" is the estimated cap height as a % of frame height.</div>
<h2>Where the seconds go, pace, text and camera</h2>
{legend(CAT_COL)}{legend(TR_COL)}{legend({f'cam {k}': v for k, v in CAM_COL.items()})}
{summary_rows(groups)}
<h2>Transition mix, all films</h2>{mix_table(c['overall'])}
<h2>Top transitions</h2><div class="mut">10 fps, from 0.2 s before to 0.2 s after each one. Highest score first, spread over accounts. A cut's score is the size of its jump, so end cards come first.</div>
{top_transitions(films, a.top, not a.no_strips)}
<h2>Composition</h2>{comp_section(c)}
<h2>Films</h2><div class="mut">Top row: transitions (lines = cuts, spans = gradual, coloured by type). Middle: category per 0.5 s. Bottom: camera per second.</div>
{''.join(film_block(f) for f in films)}</main>"""
    page = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Reference corpus</title><style>{CSS}</style></head><body>{body}</body></html>'
    open(os.path.join(OUT, 'index.html'), 'w').write(page)
    print('report ->', os.path.join(OUT, 'index.html'))


if __name__ == '__main__':
    main()

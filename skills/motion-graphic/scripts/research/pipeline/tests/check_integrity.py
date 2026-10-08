#!/usr/bin/env python3
"""check_integrity.py: check that the corpus numbers cover exactly the films they claim, and that a failed OCR
reads as "unavailable", never as 0.

Usage:
  check_integrity.py [work_dir]        (default: a new temporary folder, deleted afterwards)

Builds two 2 s synthetic clips with ffmpeg, puts a stub `tesseract` first on PATH, and runs run_corpus.py:
  1. an earlier run measures old.mp4 into the out folder (--ocr none);
  2. a new run measures only a.mp4 with a tesseract that exits 1: the run exits 1 and lists a under ocr_failed,
     a's text.json says "ocr_status": "failed", corpus.json has a only (old is listed as not included), a's demo
     share is null, and the report names the OCR failure;
  3. aggregate.py --include-history pools both films and the report says so; with no run.json it refuses;
  4. with a working tesseract and no --force, a's text is re-measured (a failed OCR is never cached);
  5. --ocr none re-measures it again (another engine), then a repeat run leaves it up to date;
  6. text_frames.py exits 2 on the failing stub, and ocr_vision raises on a helper that exits 1 or prints
     nothing.
Prints one line per check and exits 1 if any fails. Needs ffmpeg, numpy and Pillow; no OCR engine needed.
"""
import json, os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import text_frames  # noqa: E402

FAIL_STUB = '#!/bin/sh\necho "stub tesseract: simulated crash" >&2\nexit 1\n'
OK_STUB = ('#!/bin/sh\nprintf "level\\tpage_num\\tblock_num\\tpar_num\\tline_num\\tword_num\\tleft\\ttop\\twidth'
           '\\theight\\tconf\\ttext\\n"\n')
bad = 0


def check(name, ok, got=''):
    global bad
    print(('ok    ' if ok else 'FAIL  ') + name + (f'  ({got})' if got and not ok else ''))
    bad += not ok


def stub(bin_dir, body):
    p = os.path.join(bin_dir, 'tesseract')
    open(p, 'w').write(body); os.chmod(p, 0o755)


def run(args, env):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, env=env)
    return r.returncode, r.stdout + r.stderr


def clip(path, colour):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c={colour}:s=320x240:d=2:r=30',
                    '-pix_fmt', 'yuv420p', path], check=True)


def main():
    work = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='integrity_')
    keep = len(sys.argv) > 1
    vids_old, vids_new, out, bin_dir = (os.path.join(work, d) for d in ('vids_old', 'vids_new', 'out', 'bin'))
    for d in (vids_old, vids_new, bin_dir):
        os.makedirs(d, exist_ok=True)
    clip(os.path.join(vids_old, 'old.mp4'), 'gray'); clip(os.path.join(vids_new, 'a.mp4'), 'navy')
    env = {**os.environ, 'PATH': bin_dir + os.pathsep + os.environ['PATH']}
    rc_ = os.path.join(HERE, 'run_corpus.py'); agg = os.path.join(HERE, 'aggregate.py'); rep = os.path.join(HERE, 'report.py')
    film = lambda f, n: json.load(open(os.path.join(out, 'films', f, n)))

    # 1. an earlier run leaves old/ in the out folder
    rc, log = run([rc_, vids_old, out, '--ocr', 'none', '--no-report', '--jobs', '1'], env)
    check('earlier run (old.mp4, --ocr none) succeeds', rc == 0, log[-300:])

    # 2. the new run: only a.mp4, OCR crashes
    stub(bin_dir, FAIL_STUB)
    rc, log = run([rc_, vids_new, out, '--ocr', 'tesseract', '--jobs', '1'], env)
    man = json.load(open(os.path.join(out, 'run.json')))
    check('failing OCR: run exits 1', rc == 1, rc)
    check('manifest: selected and succeeded are [a], ocr_failed is [a]',
          man['selected'] == ['a'] and man['succeeded'] == ['a'] and man['ocr_failed'] == ['a'], man)
    check('manifest records the engine and its settings', man['ocr'] == 'tesseract' and man['ocr_settings'] == {'fps': 2, 'fast': False}, man)
    tx = film('a', 'text.json')
    check('text.json: ocr_status failed, with the error', tx['ocr_status'] == 'failed' and 'simulated crash' in tx.get('ocr_error', ''), tx.get('ocr_status'))
    c = json.load(open(os.path.join(out, 'corpus.json')))
    ids = [f['stem'] for f in c['films']]
    check('corpus: only a, not the stale old', ids == ['a'] and c['inclusion']['not_included'] == ['old'], (ids, c['inclusion']))
    fa = c['films'][0]
    check('corpus: a demo share is null (unavailable), not 0', fa['share']['demo'] is None and fa['ocr'] == 'failed', fa['share'])
    check('corpus: films_with_ocr is 0', c['overall']['films_with_ocr'] == 0, c['overall']['films_with_ocr'])
    html = open(os.path.join(out, 'index.html')).read()
    check('report: says the numbers cover the last run and names the OCR failure',
          "last run's 1 succeeded films" in html and 'OCR failed' in html and '1 other film folders' in html)

    # 3. history on purpose, and no manifest at all
    rc, log = run([agg, out, '--include-history'], env); run([rep, out], env)
    c = json.load(open(os.path.join(out, 'corpus.json')))
    check('--include-history pools old and a', rc == 0 and sorted(f['stem'] for f in c['films']) == ['a', 'old'], log[-300:])
    check('report says the numbers pool earlier runs', 'earlier runs included' in open(os.path.join(out, 'index.html')).read())
    os.rename(os.path.join(out, 'run.json'), os.path.join(out, 'run.json.bak'))
    rc, log = run([agg, out], env)
    check('no run.json and no --include-history: aggregate refuses', rc != 0 and 'run manifest' in log, log[-200:])
    os.rename(os.path.join(out, 'run.json.bak'), os.path.join(out, 'run.json'))

    # 4. a working OCR, no --force: the failed text is re-measured
    stub(bin_dir, OK_STUB)
    rc, log = run([rc_, vids_new, out, '--ocr', 'tesseract', '--jobs', '1', '--no-report'], env)
    tx = film('a', 'text.json')
    check('working OCR: exit 0 and a failed text.json is re-measured', rc == 0 and 'a: text' in log and tx['ocr_status'] == 'ok', log[-300:])

    # 5. another engine re-measures; the same engine does not
    rc, log = run([rc_, vids_new, out, '--ocr', 'none', '--jobs', '1', '--no-report'], env)
    check('--ocr none after tesseract re-measures text', rc == 0 and film('a', 'text.json')['ocr'] == 'none' and 'a: text' in log, log[-300:])
    rc, log = run([rc_, vids_new, out, '--ocr', 'none', '--jobs', '1', '--no-report'], env)
    check('same engine again: up to date', rc == 0 and 'up to date' in log, log[-300:])

    # 6. the OCR wrappers themselves
    stub(bin_dir, FAIL_STUB)
    rc, log = run([os.path.join(HERE, 'text_frames.py'), os.path.join(vids_new, 'a.mp4'), '--ocr', 'tesseract'], env)
    check('text_frames.py exits 2 when OCR fails', rc == 2 and 'OCR failed' in log, (rc, log[-200:]))
    img = os.path.join(work, 'f.jpg')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=white:s=64x64', '-frames:v', '1', img], check=True)
    for name, body in (('exits 1', '#!/bin/sh\nexit 1\n'), ('prints nothing', '#!/bin/sh\ncat >/dev/null\n')):
        exe = os.path.join(bin_dir, 'fake_vision'); open(exe, 'w').write(body); os.chmod(exe, 0o755)
        try:
            text_frames.ocr_vision(exe, [img], False); raised = False
        except text_frames.OcrError:
            raised = True
        check(f'ocr_vision raises when the helper {name}', raised)

    if not keep:
        shutil.rmtree(work, ignore_errors=True)
    print('all checks passed' if not bad else f'{bad} checks FAILED')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

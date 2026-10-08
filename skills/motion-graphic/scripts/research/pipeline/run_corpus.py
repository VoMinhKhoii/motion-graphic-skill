#!/usr/bin/env python3
"""run_corpus.py: run the whole automatic analysis over a folder of films. Resumable: finished steps are skipped.

Usage:
  run_corpus.py <videos_dir> <out_dir> [--account-from-filename] [--jobs 2] [--only REGEX] [--force]
                [--ocr auto|vision|tesseract|none] [--no-report]
  run_corpus.py refs/vids refs/corpus --account-from-filename --jobs 3

Per film (stem = file name without extension) it writes <out_dir>/films/<stem>/:
  meta.json          account, title, url, upload date, views, duration, source path
  stats.json, cuts.json, curves.json, sheet.jpg, curves.png
                     from ../analyze_video.py (cuts, contact sheet, motion and loudness), if that script exists
  transitions.json   transitions.py: every shot boundary with type and length, camera state per 0.5 s and per second
  text.json          text_frames.py: OCR at 2 fps, class per sample, text cards
  composition.json   composition.py: per 2 fps sample, content coverage, largest empty region, subject box, edge
                     bleed, element count, text area and positions (from text.json's OCR boxes)
  strip.jpg          one row of 16 thumbnails across the film, for the timeline on the board
Then it writes the run manifest <out_dir>/run.json and runs aggregate.py (-> <out_dir>/corpus.json) and
report.py (-> <out_dir>/index.html) unless --no-report. The manifest lists the film ids (stems) this run
selected, the ones that succeeded, the ones that failed, the ones whose OCR failed (measured, text unavailable),
the resolved OCR engine and its settings. aggregate.py includes only the succeeded films: a film left in
<out_dir>/films/ by an earlier run, or one that failed late (say at the strip), is not in the numbers.

Resuming: a finished step is skipped when its output is newer than the video. text.json is also re-measured
when it was made with another OCR engine or other settings (so installing tesseract and re-running with
--ocr tesseract re-reads text that was "none"), or when its OCR failed. composition.json is re-measured when it is
older than text.json or was made with other composition.SETTINGS. --force redoes every step.

Failures are loud. A film that fails does not stop the others, but the run ends with the failed list and exit
code 1, and the report's header names them. --ocr vision or tesseract stops at once if that engine is missing.
--ocr auto with no engine warns, and the text and demo shares come out as null (unavailable), never 0.
A film whose OCR engine fails mid-run keeps its other measures, but its text is unavailable (null), it is listed
under "OCR FAILED", and the run exits 1.
Decide with the owner before going on with partial results.

Account: with --account-from-filename, the part of the stem before "__" (a leading "@" dropped), which is what
../download.sh writes (<uploader>__<id>.mp4). Otherwise the .info.json's uploader_id, uploader or channel.
Timing on an Apple M2, one job: about 1 s of work per second of film (OCR 0.6, transitions 0.25,
analyze_video 0.12, composition 0.04). The 25-film test corpus (13 minutes of film) took about 3.5 minutes with --jobs 3.
"""
import argparse, json, os, re, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import composition  # noqa: E402
ANALYZE = os.path.join(os.path.dirname(HERE), 'analyze_video.py')
EXTS = ('.mp4', '.mov', '.m4v', '.webm', '.mkv')


def account_of(stem, info, from_filename):
    if from_filename and '__' in stem:
        return stem.split('__')[0].lstrip('@')
    for k in ('uploader_id', 'uploader', 'channel'):
        if info.get(k):
            return str(info[k]).lstrip('@')
    return 'unknown'


def fresh(path, src):
    return os.path.exists(path) and os.path.getmtime(path) >= os.path.getmtime(src)


def strip(video, dur, out, n=16):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-vf', f'fps={n / max(dur, 0.1):.5f},scale=-2:90,tile={n}x1',
                    '-frames:v', '1', '-q:v', '4', out], check=True)


TEXT_SETTINGS = {'fps': 2, 'fast': False}  # text_frames.analyze settings; part of text.json's cache key


def text_fresh(path, video, engine):
    """text.json is reusable only if newer than the video, made by the same engine with the same settings, and
    its OCR did not fail."""
    if not fresh(path, video):
        return False
    try:
        tx = json.load(open(path))
    except (OSError, ValueError):
        return False
    return tx.get('ocr') == engine and tx.get('settings') == TEXT_SETTINGS and tx.get('ocr_status', 'ok') != 'failed'


def comp_fresh(path, video, text_path):
    """composition.json is reusable only if newer than the video and the film's text.json, with the same settings."""
    if not fresh(path, video) or (os.path.exists(text_path) and os.path.getmtime(path) < os.path.getmtime(text_path)):
        return False
    try:
        return json.load(open(path)).get('settings') == composition.SETTINGS
    except (OSError, ValueError):
        return False


def run_film(video, out_dir, from_filename, engine, force):
    from frames import probe
    import text_frames, transitions
    stem = os.path.splitext(os.path.basename(video))[0]
    od = os.path.join(out_dir, 'films', stem); os.makedirs(od, exist_ok=True)
    t0 = time.time(); done = []
    info_path = os.path.splitext(video)[0] + '.info.json'
    info = json.load(open(info_path)) if os.path.exists(info_path) else {}
    p = probe(video)
    meta = {'stem': stem, 'account': account_of(stem, info, from_filename), 'video': os.path.abspath(video),
            'title': info.get('title') or info.get('description', '')[:80] or stem, 'url': info.get('webpage_url'),
            'upload_date': info.get('upload_date'), 'views': info.get('view_count'), 'duration': round(p['duration'], 2),
            'w': p['w'], 'h': p['h'], 'description': (info.get('description') or '')[:500]}
    json.dump(meta, open(os.path.join(od, 'meta.json'), 'w'), ensure_ascii=False, indent=1)
    if os.path.exists(ANALYZE) and (force or not fresh(os.path.join(od, 'stats.json'), video)):
        subprocess.run([sys.executable, ANALYZE, video, '--out', os.path.join(out_dir, 'films')], check=True, capture_output=True)
        done.append('analyze')
    tp = os.path.join(od, 'transitions.json')
    if force or not fresh(tp, video):
        json.dump(transitions.analyze(video), open(tp, 'w')); done.append('transitions')
    xp = os.path.join(od, 'text.json')
    if force or not text_fresh(xp, video, engine):
        json.dump(text_frames.analyze(video, ocr=engine, **TEXT_SETTINGS), open(xp, 'w'), ensure_ascii=False); done.append('text')
    tx = json.load(open(xp)); status = tx.get('ocr_status', 'ok')
    cp = os.path.join(od, 'composition.json')
    if force or not comp_fresh(cp, video, xp):
        json.dump(composition.analyze(video, tx, TEXT_SETTINGS['fps']), open(cp, 'w')); done.append('composition')
    sp = os.path.join(od, 'strip.jpg')
    if force or not fresh(sp, video):
        strip(video, p['duration'], sp); done.append('strip')
    note = ' [OCR FAILED: text unavailable]' if status == 'failed' else ''
    return stem, status, f"{stem}: {', '.join(done) or 'up to date'}{note} ({time.time() - t0:.0f}s)"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('videos_dir'); ap.add_argument('out_dir')
    ap.add_argument('--account-from-filename', action='store_true')
    ap.add_argument('--jobs', type=int, default=2); ap.add_argument('--only', default='')
    ap.add_argument('--force', action='store_true'); ap.add_argument('--no-report', action='store_true')
    ap.add_argument('--ocr', default='auto', choices=['auto', 'vision', 'tesseract', 'none'])
    a = ap.parse_args()
    vids = sorted(os.path.join(a.videos_dir, f) for f in os.listdir(a.videos_dir)
                  if f.lower().endswith(EXTS) and (not a.only or re.search(a.only, f)))
    if not os.path.exists(ANALYZE):
        print('note: analyze_video.py not found; cuts, sheets and loudness are skipped', file=sys.stderr)
    import text_frames
    try:  # compiles the Vision helper once before the workers start; a named engine that is missing stops here
        engine = text_frames.resolve_engine(a.ocr)
    except RuntimeError as e:
        sys.exit(f'error: {e}')
    if engine == 'none':
        print('WARNING: no OCR engine (macOS swiftc or tesseract). Text, demo and logo shares will be unavailable (null), '
              'not 0; only cuts, transitions and camera are measured.', file=sys.stderr)
    print(f'OCR engine: {engine}', flush=True)
    os.makedirs(a.out_dir, exist_ok=True)
    t0 = time.time(); failed, succeeded, ocr_failed = [], [], []
    stem = lambda v: os.path.splitext(os.path.basename(v))[0]
    with ProcessPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        futs = {ex.submit(run_film, v, a.out_dir, a.account_from_filename, engine, a.force): v for v in vids}
        for i, fu in enumerate(as_completed(futs), 1):
            try:
                film, status, msg = fu.result()
                succeeded.append(film)
                if status == 'failed':
                    ocr_failed.append(film)
                print(f'[{i}/{len(vids)}] {msg}', flush=True)
            except Exception as e:  # keep going with the others; the film is retried on the next run
                failed.append(stem(futs[fu])); print(f'[{i}/{len(vids)}] FAIL {failed[-1]}: {e}', flush=True)
    print(f'{len(vids)} films attempted, {len(succeeded)} succeeded, {len(failed)} failed, OCR {engine} '
          f'({len(ocr_failed)} with OCR failed), {time.time() - t0:.0f}s', flush=True)
    manifest = {'selected': sorted(stem(v) for v in vids), 'succeeded': sorted(succeeded), 'failed': sorted(failed),
                'ocr_failed': sorted(ocr_failed), 'ocr': engine, 'ocr_settings': TEXT_SETTINGS,
                'composition_settings': composition.SETTINGS, 'only': a.only or None,
                'when': time.strftime('%Y-%m-%d %H:%M')}
    json.dump(manifest, open(os.path.join(a.out_dir, 'run.json'), 'w'), indent=1)
    if not a.no_report:
        subprocess.run([sys.executable, os.path.join(HERE, 'aggregate.py'), a.out_dir], check=True)
        subprocess.run([sys.executable, os.path.join(HERE, 'report.py'), a.out_dir], check=True)
    if ocr_failed:
        print('OCR FAILED (measured, but their text and demo shares are unavailable; re-run to retry):\n  '
              + '\n  '.join(sorted(ocr_failed)), file=sys.stderr)
    if failed:
        print('FAILED films (not in corpus.json; fix and re-run, finished steps are skipped):\n  ' + '\n  '.join(sorted(failed)),
              file=sys.stderr)
    if failed or ocr_failed:
        sys.exit(1)


if __name__ == '__main__':
    main()

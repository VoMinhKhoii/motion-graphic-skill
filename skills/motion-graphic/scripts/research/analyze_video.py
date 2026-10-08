#!/usr/bin/env python3
"""analyze_video.py: measure reference films, so a direction rests on numbers rather than impressions.

Usage:
  analyze_video.py <video> [<video> ...] [--out an] [--thresh 0.3] [--n 24]

For each film it writes <out>/<stem>/ (stem = the video's file name without extension). This CLI and these
files and keys are a stable interface: other tools call this script and read them.
  stats.json        {"duration": s, "w": px, "h": px, "fps": float, "audio": bool, "cuts": int,
                     "cuts_per_min": float, "median_shot_s": float, "mean_shot_s": float,
                     "integrated_lufs": float|null (null without audio), "thresh": float}
  cuts.json         [s, ...]  cut times, seconds (ffmpeg scene score > --thresh; 0.3 suits UI films, 0.4 live action)
  curves.json       {"motion_per_s": [...], "loudness_dbfs_per_0.25s": [...] ([] without audio)}
                    motion: mean luma change between frames 0.1 s apart, averaged over each second (0-255
                    scale: a held frame reads 0, moving UI about 1-5, a second that holds a hard cut 5+)
  sheet.jpg         --n frames, evenly spaced, each stamped with its time; the first frame after each cut gets a
                    red bar on top
  curves.png        motion (blue) and loudness (orange) over time, cuts as pink ticks
  spectrogram.png   ffmpeg showspectrumpic of the soundtrack (only if the film has audio)
It prints one summary line per film to stdout. Exit code 0 on success.
Needs ffmpeg/ffprobe, python3 with numpy and Pillow.

Reading the numbers: cuts per minute separates the fast end of a corpus (14-17/min) from the slow (about 4/min);
the motion curve shows move-then-hold (spikes, then flat); the loudness curve shows where the music hits land.
"""
import argparse, json, os, re, statistics, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def probe(path):
    p = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate',
                                            '-of', 'json', path]))
    v = next(s for s in p['streams'] if s['codec_type'] == 'video')
    n, d = v['r_frame_rate'].split('/')
    return {'duration': float(p['format']['duration']), 'w': v['width'], 'h': v['height'], 'fps': round(float(n) / float(d), 3),
            'audio': any(s['codec_type'] == 'audio' for s in p['streams'])}


def cut_times(path, thresh):
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-an', '-vf', f"select='gt(scene,{thresh})',showinfo", '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    return [round(float(m.group(1)), 3) for m in re.finditer(r'pts_time:([0-9.]+)', err)]


def motion_per_second(path, dur):
    w, h = 64, 64
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps=10,scale={w}:{h},format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, h, w).astype(np.int16)
    if len(fr) < 2:
        return []
    d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))  # mean luma change per 0.1 s step, 0..255
    d = np.concatenate([[0.0], d])  # d[i] = change INTO frame i, so a cut at 3.0 s counts in second 3
    secs = int(np.ceil(dur))
    return [round(float(d[i * 10:(i + 1) * 10].mean()), 2) if i * 10 < len(d) else 0.0 for i in range(secs)]


def loudness(path):
    sr = 16000
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    if len(x) == 0:
        return [], None
    hop = sr // 4
    rms = [float(np.sqrt(np.mean(x[i:i + hop] ** 2)) + 1e-9) for i in range(0, len(x), hop)]
    curve = [round(20 * np.log10(r), 1) for r in rms]
    err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-vn', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.findall(r'I:\s+(-?[0-9.]+) LUFS', err)
    return curve, (float(m[-1]) if m else None)


def font(size):
    for f in ['/System/Library/Fonts/Supplemental/Arial.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


def grab(path, t, h):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', path, '-frames:v', '1', '-vf', f'scale=-2:{h}', '-f', 'image2pipe', '-vcodec', 'png', '-'],
                         capture_output=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert('RGB') if raw else None


def sheet(path, info, cuts, n, out):
    dur = info['duration']; th = 300 if info['h'] > info['w'] else 180
    ts = [dur * (i + 0.5) / n for i in range(n)]
    ims = [(t, grab(path, t, th)) for t in ts]
    ims = [(t, im) for t, im in ims if im]
    if not ims:
        return
    tw = ims[0][1].width; cols = 8 if info['h'] > info['w'] else 6
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * (tw + 6) + 6, rows * (th + 30) + 40), (240, 238, 233)); d = ImageDraw.Draw(S); f = font(16)
    d.text((8, 10), f"{os.path.basename(path)}  {dur:.1f}s  {info['w']}x{info['h']}  cuts {len(cuts)}", fill=(20, 20, 19), font=f)
    for i, (t, im) in enumerate(ims):
        x = 6 + (i % cols) * (tw + 6); y = 40 + (i // cols) * (th + 30)
        S.paste(im, (x, y)); d.text((x + 2, y + th + 6), f'{t:.1f}s', fill=(20, 20, 19), font=f)
        if any(c <= t < c + dur / n for c in cuts):  # the first sampled frame after a cut
            d.rectangle([x, y, x + tw, y + 6], fill=(224, 72, 72))
    S.save(out, quality=82)


def curves_png(motion, loud, cuts, dur, out):
    W, H, pad = 1200, 360, 40
    S = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(S); f = font(14)
    X = lambda t: pad + (W - 2 * pad) * t / max(dur, 1e-6)
    for c in cuts:
        d.line([X(c), pad, X(c), H - pad], fill=(230, 200, 200))
    if motion:
        mx = max(max(motion), 1e-6)
        d.line([(X(i + 0.5), H / 2 - (H / 2 - pad) * m / mx) for i, m in enumerate(motion)], fill=(60, 90, 200), width=2)
    if loud:
        lo = -60
        d.line([(X(i * 0.25), H - pad - (H / 2 - pad) * (max(l, lo) - lo) / -lo) for i, l in enumerate(loud)], fill=(220, 110, 40), width=2)
    d.text((pad, 8), 'motion energy (blue, top half)   loudness dBFS -60..0 (orange, bottom half)   cuts (pink)', fill='black', font=f)
    for s in range(0, int(dur) + 1, max(1, int(dur // 12) or 1)):
        d.text((X(s) - 6, H - pad + 8), f'{s}s', fill='black', font=f)
    S.save(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('videos', nargs='+'); ap.add_argument('--out', default='an')
    ap.add_argument('--thresh', type=float, default=0.3); ap.add_argument('--n', type=int, default=24)
    a = ap.parse_args()
    for v in a.videos:
        stem = os.path.splitext(os.path.basename(v))[0]; od = os.path.join(a.out, stem); os.makedirs(od, exist_ok=True)
        info = probe(v); dur = info['duration']
        cuts = cut_times(v, a.thresh)
        bounds = [0.0] + cuts + [dur]
        shots = [b - a_ for a_, b in zip(bounds, bounds[1:]) if b - a_ > 1e-3]
        motion = motion_per_second(v, dur)
        loud, lufs = loudness(v) if info['audio'] else ([], None)
        stats = {**info, 'cuts': len(cuts), 'cuts_per_min': round(len(cuts) / dur * 60, 2) if dur else 0,
                 'median_shot_s': round(statistics.median(shots), 2), 'mean_shot_s': round(statistics.mean(shots), 2),
                 'integrated_lufs': lufs, 'thresh': a.thresh}
        json.dump(stats, open(os.path.join(od, 'stats.json'), 'w'), indent=1)
        json.dump(cuts, open(os.path.join(od, 'cuts.json'), 'w'))
        json.dump({'motion_per_s': motion, 'loudness_dbfs_per_0.25s': loud}, open(os.path.join(od, 'curves.json'), 'w'))
        sheet(v, info, cuts, a.n, os.path.join(od, 'sheet.jpg'))
        curves_png(motion, loud, cuts, dur, os.path.join(od, 'curves.png'))
        if info['audio']:
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', v, '-lavfi', 'showspectrumpic=s=1200x400:legend=1', os.path.join(od, 'spectrogram.png')])
        print(f"{stem}: {dur:.1f}s {info['w']}x{info['h']} cuts {len(cuts)} ({stats['cuts_per_min']}/min) median shot {stats['median_shot_s']}s"
              f" LUFS {lufs} -> {od}")


if __name__ == '__main__':
    sys.exit(main())

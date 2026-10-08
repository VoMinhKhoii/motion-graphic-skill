#!/usr/bin/env python3
"""sfx_mix.py: build a film's sound from a JSON cue sheet: SFX on every on-screen event, plus an optional music
track aligned so one chosen hit lands on one chosen film moment.

Usage:
  sfx_mix.py <cues.json> [--out mix.wav] [--no-music] [--sfx-dir DIR] [--music FILE] [--check]
  --check     validate the sheet and list missing sound files; writes nothing (exit 1 on an invalid sheet)
  --sfx-dir   use this folder instead of the sheet's sfx_dir; --music likewise for the music file

Cue sheet (paths are relative to the cue sheet's folder):
  {
    "duration": 14.6,                  film length in seconds (the mix is exactly this long)
    "sfx_dir": "sfx",                  folder with the sound files
    "scenes": {"demo": 2.5},           optional: scene start times, so events can use scene-local times
    "music": "music/track.mp3",        optional
    "music_hit_at": 79.4,              the track time (s) of the hit you want to land...
    "hit_lands_at": 12.98,             ...on this film time (s). The track is offset to make that true.
    "music_db": -6,                    music level under the SFX (default -6)
    "music_fade_in": 0.25, "music_fade_out": 0.5,   seconds (defaults)
    "music_fade_power": 1,             fade-out curve: 1 linear, 1.5 holds the end in near-silence longer
    "peak_db": -1,                     peak normalisation target when there is no "loudness" (default -1 dBFS)
    "loudness": {"I": -16, "TP": -1.5, "LRA": 11},   optional: two-pass EBU R128 loudness normalisation
    "out": "mix.wav",                  default output path
    "events": [
      {"t": 0.9, "sound": "click.wav", "db": -8, "pan": 0.0, "note": "the Send tap"},
      {"scene": "demo", "t": 1.2, "sound": "typing.wav", "db": -13, "dur": 1.45, "offset": 0.3, "trim": false},
      ...]
  }
Event fields: t (s, film time, or scene-local when "scene" is given), sound (file in sfx_dir), db (gain, default
0), pan (-1 left .. 1 right, default 0, equal-power), dur (cut the sound to this length, with a `fade` s fade,
default 0.03; for beds like typing), offset (start this many seconds into the file), trim (default true: start
the sound at its onset, the first sample above 8% of its peak minus 4 ms, so the hit lands on the frame; set
false for beds), note (free text: what happens on screen). Keys starting with "_" are comments.

Levels: with "loudness", the summed mix is normalised in two ffmpeg loudnorm passes (measure, then apply with
the measured values, linear) to integrated loudness I (LUFS), true peak TP (dBTP) and loudness range LRA. Use it
for a film of 30 s or more; the worked example's film used I -16, TP -1.5, LRA 11. Without it the mix is
peak-normalised to peak_db, which is what the worked example's 10-12 s teaser used (-1 dBFS; it measured
-13 LUFS). Either way the script prints the result's integrated loudness and true peak. Measure again on the
delivered MP4 after AAC encoding (`ffmpeg -i film.mp4 -af ebur128=peak=true -f null -`): the encoder can add
a little true peak.

Output: 48 kHz stereo 16-bit WAV. Feed it to render/master.sh as the mix.
Times come from the film code (scene starts and the moments inside each scene); keep the two in step.
Needs ffmpeg and numpy.
"""
import argparse, json, os, re, subprocess, sys, tempfile, wave
import numpy as np

SR = 48000
EVENT_KEYS = {'t', 'sound', 'db', 'pan', 'dur', 'offset', 'trim', 'scene', 'fade', 'note'}


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True).stdout
    if not raw:
        sys.exit(f'cannot decode {path}')
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def onset_trim(x):
    env = np.abs(x).max(1)
    on = int(np.argmax(env > env.max() * 0.08))
    return x[max(0, on - int(0.004 * SR)):]


def write_wav(path, x):
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
        wf.writeframes((np.clip(x, -1, 1) * 32767).astype('<i2').tobytes())


def ebur128(path):
    """Integrated loudness (LUFS) and true peak (dBTP) of a file, from ffmpeg's ebur128 summary."""
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    summ = err[err.rfind('Summary:'):]
    i = re.search(r'I:\s+(-?[\d.]+|-inf) LUFS', summ); p = re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS', summ)
    return (float(i.group(1)) if i else None), (float(p.group(1)) if p else None)


def loudnorm(src, dst, L):
    """Two-pass loudnorm: measure, then normalise with the measured values (linear mode keeps the dynamics)."""
    target = f"I={L.get('I', -16)}:TP={L.get('TP', -1.5)}:LRA={L.get('LRA', 11)}"
    err = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', src, '-af', f'loudnorm={target}:print_format=json', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    m = json.loads(err[err.rfind('{'):err.rfind('}') + 1])
    meas = (f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
            f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-af', f'loudnorm={target}:{meas}', '-ar', str(SR), '-c:a', 'pcm_s16le', dst], check=True)
    return m


def check(cue, sfx_dir, music):
    """Validate the sheet's structure; return (errors, missing files)."""
    errs, missing = [], set()
    if not isinstance(cue.get('duration'), (int, float)) or cue['duration'] <= 0:
        errs.append('duration must be a positive number')
    scenes = cue.get('scenes', {})
    for i, e in enumerate(cue.get('events', [])):
        where = f"event {i} ({e.get('note') or e.get('sound')})"
        extra = {k for k in e if not k.startswith('_')} - EVENT_KEYS
        if extra:
            errs.append(f'{where}: unknown keys {sorted(extra)}')
        if not isinstance(e.get('t'), (int, float)) or not isinstance(e.get('sound'), str):
            errs.append(f'{where}: needs a numeric "t" and a "sound"'); continue
        if 'scene' in e and e['scene'] not in scenes:
            errs.append(f"{where}: scene {e['scene']!r} is not in scenes")
        t = e['t'] + scenes.get(e.get('scene'), 0.0)
        if not 0 <= t < cue.get('duration', 0):
            errs.append(f'{where}: film time {t:.3f} s is outside 0..duration')
        if not os.path.exists(os.path.join(sfx_dir, e['sound'])):
            missing.add(e['sound'])
    if not cue.get('events'):
        errs.append('no events')
    if cue.get('loudness') is not None and not isinstance(cue['loudness'], dict):
        errs.append('loudness must be an object like {"I": -16, "TP": -1.5, "LRA": 11}')
    if music and not os.path.exists(music):
        missing.add(music)
    return errs, sorted(missing)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cues'); ap.add_argument('--out'); ap.add_argument('--no-music', action='store_true')
    ap.add_argument('--sfx-dir'); ap.add_argument('--music'); ap.add_argument('--check', action='store_true')
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.cues))
    cue = json.load(open(a.cues))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    sfx_dir = os.path.abspath(a.sfx_dir) if a.sfx_dir else rel(cue['sfx_dir'])
    music = None if a.no_music else (os.path.abspath(a.music) if a.music else (rel(cue['music']) if cue.get('music') else None))
    if a.check:
        errs, missing = check(cue, sfx_dir, music)
        for e in errs:
            print('ERROR', e)
        print(f"{a.cues}: {len(cue.get('events', []))} events, {cue.get('duration')} s, "
              f"{'valid' if not errs else f'{len(errs)} errors'}; {len(missing)} files not found" + (f": {', '.join(missing)}" if missing else ''))
        return 1 if errs else 0

    dur = float(cue['duration']); N = int(round(dur * SR))
    mix = np.zeros((N, 2))
    scenes = cue.get('scenes', {})
    cache = {}

    def place(x, t, db=0.0, pan=0.0):
        i = int(round(t * SR))
        if i >= N or i + len(x) <= 0:
            return
        if i < 0:
            x = x[-i:]; i = 0
        x = x[: N - i] * (10 ** (db / 20))
        l, r = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2), np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
        mix[i:i + len(x), 0] += x[:, 0] * l
        mix[i:i + len(x), 1] += x[:, 1] * r

    for e in cue['events']:
        t = float(e['t']) + (scenes[e['scene']] if 'scene' in e else 0.0)
        path = os.path.join(sfx_dir, e['sound'])
        trim = e.get('trim', True)
        if (path, trim) not in cache:
            x = load(path)
            cache[(path, trim)] = onset_trim(x) if trim else x
        x = cache[(path, trim)][int(e.get('offset', 0) * SR):].copy()
        if 'dur' in e:
            x = x[: int(e['dur'] * SR)]
            f = min(len(x), int(e.get('fade', 0.03) * SR))
            if f:
                x[-f:] *= np.linspace(1, 0, f)[:, None]
        place(x, t, e.get('db', 0.0), e.get('pan', 0.0))
        print(f"{t:7.3f}s  {e['sound']:<44} {e.get('db', 0):+5.1f} dB  pan {e.get('pan', 0):+.2f}  {e.get('note', '')}")

    if music:
        m = load(music)
        off = float(cue.get('music_hit_at', 0.0)) - float(cue.get('hit_lands_at', 0.0))  # track time at film 0
        if off < 0:  # the hit is earlier in the track than in the film: pad the track's start with silence
            m = np.concatenate([np.zeros((int(-off * SR), 2)), m]); off = 0.0
        m = m[int(off * SR): int(off * SR) + N].copy()
        fi, fo = int(cue.get('music_fade_in', 0.25) * SR), int(cue.get('music_fade_out', 0.5) * SR)
        if fi and len(m) > fi:
            m[:fi] *= np.linspace(0, 1, fi)[:, None]
        if fo and len(m) > fo:
            m[-fo:] *= (np.linspace(1, 0, fo) ** cue.get('music_fade_power', 1.0))[:, None]
        place(m, 0.0, cue.get('music_db', -6.0))
        print(f"music {os.path.basename(music)}: track {off:.3f}s at film 0, hit {cue.get('music_hit_at')}s -> film {cue.get('hit_lands_at')}s")

    out = a.out or rel(cue.get('out', 'mix.wav'))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    peak = np.abs(mix).max()
    L = cue.get('loudness')
    if L:
        # sum, bring the peak to 0.95 so nothing clips in the 16-bit intermediate, then two-pass loudnorm
        with tempfile.TemporaryDirectory() as td:
            raw = os.path.join(td, 'raw.wav')
            write_wav(raw, mix * (0.95 / peak if peak > 0 else 1))
            m = loudnorm(raw, out, L)
        how = f"loudnorm I {L.get('I', -16)} TP {L.get('TP', -1.5)} LRA {L.get('LRA', 11)} (input measured {m['input_i']} LUFS, {m['input_tp']} dBTP)"
    else:
        target = 10 ** (cue.get('peak_db', -1.0) / 20)
        write_wav(out, mix * (target / peak if peak > 0 else 1))
        how = f"peak-normalised to {cue.get('peak_db', -1.0)} dBFS"
    I, TP = ebur128(out)
    print(f'wrote {out}: {dur:.2f} s, {len(cue["events"])} events, {how}')
    print(f'measured: integrated {I} LUFS, true peak {TP} dBTP (measure again on the delivered MP4 after AAC encoding)')


if __name__ == '__main__':
    sys.exit(main())

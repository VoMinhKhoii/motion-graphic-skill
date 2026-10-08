#!/usr/bin/env python3
"""transitions.py: find every shot boundary in a film, say what kind it is and how long it takes, and label the
camera for every 0.5 s.

Usage:
  transitions.py <video> [--out transitions.json] [--fps 15] [--width 160]

Output (JSON):
  {"fps", "duration",
   "transitions": [{"type", "t", "dur", "score", ...measures}],   t = start (s), dur = length (s, 0 for a cut)
   "windows":     [{"t", "state", ...measures}],                  one per 0.5 s
   "camera_per_s": [state, ...]}                                  one per second

Transition types:
  cut        the frame difference spikes for one step (at 15 fps) and drops back; not a flash, not a fast move
  dissolve   the change is spread over 2+ steps and the middle frames are a blend of the frames either side
  push       the change is spread out and most steps are one global shift in a steady direction (push, slide,
             whip pan, a scroll that fills the frame)
  zoom_in / zoom_out   the change is spread out and most steps are one global scale in a steady direction
             (scale-into, scale-out, zoom-through)
  other      the picture changed into something new, but no single model explains the steps (morph, mask
             reveal, wipe, the app's own state change, a fast montage)
Window states: still, inframe (things move but the camera does not), pan, zoom_in, zoom_out, transition.
camera_per_s takes, per second, the busier of its two windows (transition > zoom > pan > inframe > still).

How it decides (thresholds below, on 0-255 luma at ~160 px wide):
1. d[i] = mean abs difference between frame i-1 and i. base[i] = its median over +-1.5 s.
2. Cut at i: d[i] >= CUT_MIN and d[i] >= CUT_RATIO x both neighbours, the frame after does not return to the
   frame before (that is a flash), and no global move explains it (that is a whip).
3. Active steps: d[i] > max(ACT_MIN, ACT_RATIO x base[i]). Runs of active steps (1-step gaps bridged, split at
   cuts, at most MAX_RUN s) are candidate transitions. A run is a boundary only if its two end frames differ by
   a new picture (coarse difference >= SCENE_MIN, histogram or coarse change large enough, and the new frame
   does not resemble any frame of the 1.5 s before; see is_new_picture) and one global move does not map one end
   onto the other (else it is a camera move). Runs that start within 2 steps after a cut are its tail, not a
   transition of their own.
   The run is trimmed to the stretch where the picture actually leaves the old frame and settles on the new one.
   A second pass (find_hidden) compares frames HIDDEN_SPAN apart after removing the best global move, and looks
   for a peak at least HIDDEN_RATIO x its local median: that finds a crossfade between two moving shots, where
   every single step is busy.
4. Inside a boundary run, three models compete; the best one that fits at least half of the steps names it:
   blend (each middle frame = a*before + (1-a)*after, a falling; retried with each end moved onto the middle
   frame when the shots are moving), shift (only a push if it travels PUSH_MIN of the frame), scale.
   None fits: other.
5. Each 0.5 s window compares its first and last frame (inside one shot): still if they differ by less than
   STILL_MAX, otherwise pan/zoom if one global move explains it (motion_model.fit), otherwise inframe.

Known failure modes (see PIPELINE.md for what they did on a real corpus):
- A crossfade between two moving shots fits the blend model badly and can come out as "other".
- A transition inside a long continuous move (the camera never settles) is not split out; it reads as camera.
- Flat backgrounds hide camera moves (fewer than 3 textured blocks): they read as inframe.
- A scroll or swipe that fills the frame reads as pan or push; a full-screen UI change reads as cut or other.
- Durations are measured from when the picture leaves the old frame to when it stops changing, at 1/15 s
  steps. An eased tail that keeps creeping counts as part of the transition.
Needs ffmpeg, numpy, Pillow.
"""
import argparse, json, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from frames import decode  # noqa: E402
from motion_model import fit, warp  # noqa: E402

CUT_MIN = 10.0     # luma levels: smallest one-step jump that can be a cut
CUT_RATIO = 2.5    # the jump must be this many times bigger than the steps either side
ACT_MIN = 1.2      # an active (changing) step, absolute floor
ACT_RATIO = 1.8    # an active step, relative to the local median
SCENE_MIN = 12.0   # the two ends of a run must differ by this much at 1/8 scale (coarse) to be a new picture
SCENE_SURE = 18.0  # ...and below this coarse difference the luma histogram must also move by HIST_MIN
HIST_MIN = 0.1     # share of pixels that changed luma bin (16 bins)
NOVELTY = 0.65     # the new picture must not resemble the 1.5 s before it (nor the old one the 1.5 s after)
NOVELTY_SKIP = 25.0  # coarse difference above which the novelty test is skipped
MAX_RUN = 2.5      # s: longer runs are camera/in-frame motion, not a transition
STILL_MAX = 1.0    # window: first vs last frame below this is still
PUSH_MIN = 0.2     # share of the frame a push must travel (summed over its steps)
SMALL_SCALES = [0.95, 0.985, 1.0, 1.015, 1.05]
MODEL_FIT = 0.5    # share of steps a model must explain to name the transition
TRIM = 0.06       # trim run ends that are within this share of the end-to-end change
BLEND_RES = 0.45   # blend residual / distance to the nearer end, per middle frame
HIDDEN_SPAN = 0.53  # s: frame gap for the second pass (find_hidden)
HIDDEN_RATIO = 2.0  # its change must be this many times the local median
PRIORITY = {'transition': 5, 'zoom_in': 4, 'zoom_out': 4, 'pan': 3, 'inframe': 2, 'still': 1}


def coarse(a, b, k=8):
    """Mean abs difference of k-times-downscaled frames: blind to small moves, sees a new picture."""
    h, w = a.shape; h2, w2 = h // k * k, w // k * k
    A = a[:h2, :w2].astype(np.float32).reshape(h2 // k, k, w2 // k, k).mean(axis=(1, 3))
    B = b[:h2, :w2].astype(np.float32).reshape(h2 // k, k, w2 // k, k).mean(axis=(1, 3))
    return float(np.abs(A - B).mean())


def hist_dist(a, b, bins=16):
    ha = np.histogram(a, bins=bins, range=(0, 256))[0] / a.size; hb = np.histogram(b, bins=bins, range=(0, 256))[0] / b.size
    return float(np.abs(ha - hb).sum() / 2)


def mad(a, b):
    return float(np.abs(a.astype(np.float32) - b.astype(np.float32)).mean())


def step_diffs(f):
    d = np.zeros(len(f), np.float32)
    for i in range(1, len(f)):
        d[i] = mad(f[i - 1], f[i])
    return d


def local_median(d, half):
    return np.array([np.median(d[max(1, i - half):i + half + 1]) for i in range(len(d))], np.float32)


def find_cuts(f, d):
    cuts = []
    for i in range(1, len(f)):
        nb = max(d[i - 1] if i > 1 else 0.0, d[i + 1] if i + 1 < len(d) else 0.0)
        if d[i] < CUT_MIN or d[i] < CUT_RATIO * nb:
            continue
        if i + 1 < len(f) and mad(f[i - 1], f[i + 1]) < 0.4 * d[i]:
            continue  # a one-frame flash, the picture comes back
        m = fit(f[i - 1], f[i])
        if m['global'] and m['err1'] < 0.35 * m['err0']:
            continue  # a whip: one big global move
        cuts.append(i)
    return cuts


def runs(active, cuts, fps):
    cutset, out, i, n = set(cuts), [], 1, len(active)
    while i < n:
        if not active[i] or i in cutset:
            i += 1; continue
        j = i
        while j + 1 < n and (j + 1) not in cutset and (active[j + 1] or (j + 2 < n and active[j + 2] and (j + 2) not in cutset)):
            j += 1
        while not active[j]:
            j -= 1
        out.append((i, j)); i = j + 1
    return [(a, b) for a, b in out if b > a and (b - a + 1) / fps <= MAX_RUN]


def trim(f, a, b):
    """Narrow [a, b] to where the picture leaves frame a-1 and settles on frame b."""
    P, Q = f[a - 1], f[b]
    E = mad(P, Q)
    lo, hi = a, b
    while lo < hi and mad(f[lo], P) < TRIM * E:
        lo += 1
    while hi > lo and mad(f[hi - 1], Q) < TRIM * E:
        hi -= 1
    return lo, hi, E


def blend_fit(f, a, b, compensate=False):
    """Share of middle frames that are a blend of the frames either side, with the blend weight falling.
    compensate=True first moves each end onto the middle frame with one global move, for a crossfade between
    two shots that are themselves panning or zooming."""
    P = f[a - 1].astype(np.float32); Q = f[b].astype(np.float32)
    good, alphas, n = 0, [], 0
    for j in range(a, b):
        X = f[j].astype(np.float32)
        if compensate:
            Pw, pm = warp(P, fit(P, X, SMALL_SCALES)); Qw, qm = warp(Q, fit(Q, X, SMALL_SCALES)); m = pm & qm
            if m.mean() < 0.4:
                continue
        else:
            Pw, Qw, m = P, Q, np.ones(X.shape, bool)
        x, p_, q_ = X[m], Pw[m], Qw[m]
        near = min(float(np.abs(x - p_).mean()), float(np.abs(x - q_).mean()))
        if near < 2.0:
            continue
        n += 1
        D = p_ - q_
        al = float(np.clip(np.dot(x - q_, D) / (np.dot(D, D) + 1e-6), 0, 1))
        res = float(np.abs(x - (al * p_ + (1 - al) * q_)).mean())
        alphas.append(al)
        good += res < BLEND_RES * near
    falling = all(x >= y - 0.15 for x, y in zip(alphas, alphas[1:]))
    return (good / n if n else 0.0) if falling else 0.0, n


def is_new_picture(f, a, b, fps):
    """Do frames a-1 and b show different pictures? Coarse difference and histogram, then novelty: talking heads,
    hands and bobbing UI change a lot between two frames, but the 'new' frame looks like one from a moment ago."""
    P, Q = f[a - 1], f[b]
    c = coarse(P, Q)
    if c < SCENE_MIN or (c < SCENE_SURE and hist_dist(P, Q) < HIST_MIN):
        return False
    if c >= NOVELTY_SKIP:
        return True  # a change this big is a new picture even if something similar shows up nearby
    W = int(1.5 * fps)
    back = min((coarse(f[j], Q) for j in range(max(0, a - 1 - W), a - 1)), default=c)
    fwd = min((coarse(P, f[j]) for j in range(b + 1, min(len(f), b + 1 + W))), default=c)
    return min(back, fwd) >= NOVELTY * c


def classify_run(f, a, b, fps):
    lo, hi, E = trim(f, a, b)
    if not is_new_picture(f, a, b, fps):
        return None
    ends = fit(f[a - 1], f[b])
    if ends['global'] and ends['err1'] < 0.4 * ends['err0']:
        return None  # same picture, moved: a camera move
    steps = [fit(f[j - 1], f[j]) for j in range(lo, hi + 1)]
    n = len(steps)
    shifts = [s for s in steps if s['global'] and s['scale'] == 1.0 and (s['dx'] or s['dy'])]
    zin = [s for s in steps if s['global'] and s['scale'] > 1.0]
    zout = [s for s in steps if s['global'] and s['scale'] < 1.0]
    sx = sum(s['dx'] for s in shifts); sy = sum(s['dy'] for s in shifts)
    steady = (abs(sx) + abs(sy)) >= 0.6 * sum(abs(s['dx']) + abs(s['dy']) for s in shifts) if shifts else False
    h, w = f[0].shape
    far = abs(sx) >= PUSH_MIN * w or abs(sy) >= PUSH_MIN * h  # a push moves the picture a long way; a pan drifts
    bscore, bn = blend_fit(f, lo, hi) if hi > lo else (0.0, 0)
    if bscore < MODEL_FIT and hi > lo and (zin or zout or shifts):
        bscore, bn = blend_fit(f, lo, hi, compensate=True)  # crossfade between moving shots
    scores = {'dissolve': bscore if bn >= 1 else 0.0,
              'push': len(shifts) / n if steady and far else 0.0,
              'zoom_in': len(zin) / n, 'zoom_out': len(zout) / n}
    kind, sc = max(scores.items(), key=lambda kv: kv[1])
    if sc < MODEL_FIT:
        kind = 'other'
    return {'steps': (lo, hi), 'type': kind, 't': round((lo - 1) / fps, 2), 'dur': round((hi - lo + 1) / fps, 2), 'score': round(sc, 2),
            'scores': {k: round(v, 2) for k, v in scores.items()}, 'end_diff': round(E, 1),
            'shift_pct': [round(100 * sx / w, 1), round(100 * sy / h, 1)] if shifts else None,
            'coarse': round(coarse(f[a - 1], f[b]), 1), 'hist': round(hist_dist(f[a - 1], f[b]), 2)}


def find_hidden(f, fps, taken):
    """Second pass for transitions hidden in continuous motion (a crossfade between two moving shots): after
    removing the best global move, the change between frames HIDDEN_SPAN apart peaks at the transition even when
    every single step is busy. Sampled every 2 frames."""
    k = max(2, round(HIDDEN_SPAN * fps / 2)); n = len(f)
    idx = list(range(k, n - k, 2))
    A = np.array([fit(f[i - k], f[i + k], SMALL_SCALES)['err1'] for i in idx], np.float32)
    Am = local_median(np.concatenate([[0.0], A]), int(0.75 * fps))[1:]
    out = []
    for m, i in enumerate(idx):
        if A[m] < SCENE_MIN or A[m] < HIDDEN_RATIO * Am[m] or A[m] < A[max(0, m - k // 2):m + k // 2 + 1].max():
            continue
        if any(abs(i - j) <= 2 * k for j in taken):
            continue
        r = classify_run(f, i - k + 1, i + k, fps)
        if r:
            out.append(r); taken.add(i)
    return out


def window_state(f, u, v):
    if v - u < 2:
        return {'state': 'transition'}
    e = mad(f[u], f[v])
    if e < STILL_MAX:
        return {'state': 'still', 'diff': round(e, 2)}
    m = fit(f[u], f[v])
    st = 'inframe'
    if m['global']:
        st = 'zoom_in' if m['scale'] > 1.01 else 'zoom_out' if m['scale'] < 0.99 else 'pan'
    return {'state': st, 'diff': round(e, 2), 'dx': m['dx'], 'dy': m['dy'], 'scale': m['scale']}


def analyze(video, fps=15, width=160):
    f, fps = decode(video, fps, width)
    n = len(f); dur = n / fps
    d = step_diffs(f)
    base = local_median(d, int(1.5 * fps))
    cuts = find_cuts(f, d)
    active = d > np.maximum(ACT_MIN, ACT_RATIO * base)
    trans = [{'type': 'cut', 't': round((i - 0.5) / fps, 2), 'dur': 0.0, 'score': round(float(d[i]), 1)} for i in cuts]
    spans = []
    for a, b in runs(active, cuts, fps):
        if any(0 <= a - c <= 2 for c in cuts):
            continue  # the tail of a cut (motion blur, a settling frame)
        r = classify_run(f, a, b, fps)
        if r:
            spans.append(r.pop('steps')); trans.append(r)
    taken = set(cuts) | {j for lo, hi in spans for j in range(lo, hi + 1)}
    for r in find_hidden(f, fps, taken):
        spans.append(r.pop('steps')); trans.append(r)
    trans.sort(key=lambda r: r['t'])
    blocked = set(cuts) | {j for lo, hi in spans for j in range(lo, hi + 1)}  # steps that belong to a transition
    windows = []
    for k in range(int(np.ceil(dur / 0.5))):
        u0 = int(np.ceil(k * 0.5 * fps - 1e-6)); v0 = min(n - 1, int(np.ceil((k + 1) * 0.5 * fps - 1e-6)) - 1)
        steps = range(u0 + 1, v0 + 1)
        if sum(j in blocked and j not in cuts for j in steps) >= 0.5 * max(1, len(steps)):
            windows.append({'t': k * 0.5, 'state': 'transition'}); continue
        best, u = (u0, u0), u0  # longest stretch of frames with no transition step inside
        for j in range(u0 + 1, v0 + 2):
            if j > v0 or j in blocked:
                if j - 1 - u > best[1] - best[0]:
                    best = (u, j - 1)
                u = j
        w = window_state(f, *best) if best[1] - best[0] >= 2 or not windows else {'state': windows[-1]['state']}
        windows.append({'t': k * 0.5, **w})
    per_s = []
    for s in range(int(np.ceil(dur))):
        ws = [w['state'] for w in windows if s <= w['t'] < s + 1]
        per_s.append(max(ws, key=lambda x: PRIORITY[x]) if ws else 'still')
    return {'fps': fps, 'duration': round(dur, 2), 'transitions': trans, 'windows': windows, 'camera_per_s': per_s,
            'step_diff': [round(float(x), 2) for x in d]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('--out'); ap.add_argument('--fps', type=int, default=15)
    ap.add_argument('--width', type=int, default=160)
    a = ap.parse_args()
    r = analyze(a.video, a.fps, a.width)
    if a.out:
        json.dump(r, open(a.out, 'w'))
    mix = {}
    for t in r['transitions']:
        mix[t['type']] = mix.get(t['type'], 0) + 1
    print(f"{os.path.basename(a.video)}: {r['duration']}s, {len(r['transitions'])} transitions {mix}")


if __name__ == '__main__':
    main()

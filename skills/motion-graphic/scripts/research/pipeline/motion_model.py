"""motion_model.py: does one global camera move (shift and/or zoom) explain the change between two small frames?

fit(a, b) -> {"dx", "dy" (px, + = content moved right/down), "scale" (>1 = content grew, a zoom in),
              "err0" (mean abs diff, no model), "err1" (after the best model), "peak" (phase-correlation peak),
              "moving_frac", "static_frac", "textured" (block vote, see below), "global" (bool)}

How it works, on gray frames about 160 px wide:
- For each scale in SCALES, magnify `a` about its centre, then find the shift to `b` by phase correlation (numpy FFT,
  Hann window). Keep the (scale, shift) with the lowest masked mean abs error against `b`.
- Block vote: split the frame into ~40 px blocks and keep the textured ones (luma std > TEX). A block votes "moving"
  if it changed (err0 > STATIC) and the model cuts its error by at least 30%; "static" if it did not change.
  The move counts as global (a camera move or a slide) only if at least 3 blocks are textured, at least half of
  them move with the model, and no more than a quarter stay put.
Why the vote: on the flat backgrounds of motion design, one object sliding over a plain colour also fits a pure
shift, because the plain background does not care where it is. The vote calls that in-frame motion. The cost:
on a frame with fewer than 3 textured blocks the tool cannot see a camera move at all, and says in-frame.
"""
import numpy as np
from PIL import Image

SCALES = [0.6, 0.7, 0.8, 0.87, 0.92, 0.95, 0.97, 0.985, 1.0, 1.015, 1.03, 1.05, 1.08, 1.15, 1.25, 1.43, 1.67]
TEX = 6.0      # luma std (0-255) for a block to count as textured
STATIC = 1.5   # block mean abs diff (0-255) below which a block did not change
BLOCK = 40     # block size in px at 160 px width

_win_cache = {}


def _hann(shape):
    if shape not in _win_cache:
        _win_cache[shape] = np.outer(np.hanning(shape[0]), np.hanning(shape[1])).astype(np.float32)
    return _win_cache[shape]


def phase_shift(a, b):
    """Shift (dy, dx) that moves a onto b, and the correlation peak (0..1; noise ~0.05, clean shift 0.3+)."""
    w = _hann(a.shape)
    A = np.fft.fft2((a - a.mean()) * w); B = np.fft.fft2((b - b.mean()) * w)
    R = B * np.conj(A); R /= np.abs(R) + 1e-6
    r = np.fft.ifft2(R).real
    iy, ix = np.unravel_index(np.argmax(r), r.shape)
    dy = iy - r.shape[0] if iy > r.shape[0] // 2 else iy
    dx = ix - r.shape[1] if ix > r.shape[1] // 2 else ix
    return int(dy), int(dx), float(r[iy, ix])


def scale_img(a, s):
    """Magnify a about its centre by s; returns (image, valid mask)."""
    if s == 1.0:
        return a, np.ones(a.shape, bool)
    h, w = a.shape; cy, cx = (h - 1) / 2, (w - 1) / 2
    im = Image.fromarray(a.astype(np.float32), mode='F')
    out = np.asarray(im.transform((w, h), Image.AFFINE, (1 / s, 0, cx - cx / s, 0, 1 / s, cy - cy / s), resample=Image.BILINEAR))
    yy, xx = np.mgrid[0:h, 0:w]
    sy = cy + (yy - cy) / s; sx = cx + (xx - cx) / s
    return out, (sy >= 0) & (sy <= h - 1) & (sx >= 0) & (sx <= w - 1)


def shift_img(a, mask, dy, dx):
    h, w = a.shape
    out = np.zeros_like(a); m = np.zeros_like(mask)
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]; m[yd, xd] = mask[ys, xs]
    return out, m


def _blocks(h, w):
    ny, nx = max(1, round(h / BLOCK)), max(1, round(w / BLOCK))
    ys = np.linspace(0, h, ny + 1).astype(int); xs = np.linspace(0, w, nx + 1).astype(int)
    return [(slice(ys[i], ys[i + 1]), slice(xs[j], xs[j + 1])) for i in range(ny) for j in range(nx)]


def warp(a, m):
    """Apply a fit() result to a: returns (image, valid mask) in b's frame."""
    sa, sm = scale_img(a.astype(np.float32), m['scale'])
    return shift_img(sa, sm, m['dy'], m['dx'])


def fit(a, b, scales=SCALES):
    a = a.astype(np.float32); b = b.astype(np.float32)
    h, w = a.shape
    err0 = float(np.abs(a - b).mean())
    best = (err0, 1.0, 0, 0, 0.0, a, np.ones(a.shape, bool))  # identity, kept if nothing beats it
    for s in scales:
        sa, sm = scale_img(a, s)
        dy, dx, pk = phase_shift(sa, b)
        if abs(dy) > h * 0.45 or abs(dx) > w * 0.45:
            continue
        wa, wm = shift_img(sa, sm, dy, dx)
        if wm.mean() < 0.3:
            continue
        e = float(np.abs(wa - b)[wm].mean())
        if e < best[0] - 0.02:
            best = (e, s, dy, dx, pk, wa, wm)
    e1, s, dy, dx, pk, wa, wm = best
    moving = static = textured = 0
    for blk in _blocks(h, w):
        if b[blk].std() < TEX and a[blk].std() < TEX:
            continue
        textured += 1
        e0b = float(np.abs(a[blk] - b[blk]).mean())
        mb = wm[blk]
        e1b = float(np.abs(wa[blk] - b[blk])[mb].mean()) if mb.mean() > 0.5 else e0b
        if e0b <= STATIC:
            static += 1
        elif e1b < 0.7 * e0b:
            moving += 1
    mf = moving / textured if textured else 0.0
    sf = static / textured if textured else 0.0
    is_move = (s != 1.0 or dx or dy) and e1 < 0.75 * err0
    return {'dx': dx, 'dy': dy, 'scale': s, 'err0': round(err0, 3), 'err1': round(e1, 3), 'peak': round(pk, 3),
            'moving_frac': round(mf, 2), 'static_frac': round(sf, 2), 'textured': textured,
            'global': bool(is_move and textured >= 3 and mf >= 0.5 and sf <= 0.25)}

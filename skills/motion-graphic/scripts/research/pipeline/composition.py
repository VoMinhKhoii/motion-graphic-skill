#!/usr/bin/env python3
"""composition.py: measure how each frame is filled: how much is content, how big the largest empty patch is, where
the main subject sits, whether it runs off the frame, how many separate things there are, and where the text sits.

Usage:
  composition.py <video> [--text text.json] [--out composition.json] [--fps 2]
  find_pad, crop, crop_lines, measure, text_measures and objects are also used by check_frames.py on stills.

How a frame is read (at about ANALYSIS_AREA pixels, aspect kept, area-averaged so film grain and JPEG noise wash out):
  0. padding  letterbox or pillarbox bars encoded into the file are cut off first (find_pad, at twice the analysis
              size): a pair of flat bands of one colour, top and bottom or left and right, 2-40% thick, that end at a
              straight edge, the same across the film's samples. Everything below is measured on the picture inside,
              and the OCR boxes are moved into it. Without this the bars fill every corner, become the ground, and
              the picture's own empty ground inside them reads as content: a centred object measured 81% content
              and bled off both sides instead of 9%.
  1. detail   a pixel whose colour steps by more than DETAIL_STEP (max of R, G, B) to its right or lower
              neighbour. Text, outlines, photo texture and UI are detail; a flat fill or a soft gradient is not.
  2. masses   the detail mask closed (dilated, then eroded) by CLOSE_R of the short side, so the lines of a
              paragraph, the rows of a UI and the parts of an object merge into one mass. Gaps wider than about
              2 x CLOSE_R stay open: a headline and a phone 6% apart stay two masses.
  3. background  the smooth (non-mass) area that reaches a corner of the frame and shares the ground's colours:
              the largest smooth region reaching a corner square (CORNER of the short side) is the ground; another
              one reaching a corner joins it when its median colour sits inside the ground's colour range
              (GROUND_MARGIN wider). So a gradient cut in two by a tall subject is all background, and a flat bezel
              running off the edge is content.
  4. content  everything else: the masses plus any smooth area they enclose (a flat card inside its outline,
              a phone screen inside its bezel, also when the bezel runs off the frame).
Why this background estimate: a flat colour and a soft gradient (an aurora, a vignette) both have small local
steps, so one rule covers both, with no colour model to fit. Connectivity is what separates a backdrop from a flat
surface drawn inside an outline; the colour test keeps a flat object that runs off the edge (a phone bezel, a solid
block) out of the background. Why corners and not the whole border: a phone or a window cut by the frame edge
leaves its flat screen touching the border, but only between the two sides of its own outline; the ground runs
around the subject into a corner. Version 1 used the whole border and read the screen of every phone that runs
off the bottom as background (a full-height phone on a photo measured 57% content instead of 99%). Rejected:
similarity to the border's dominant colour (fails on gradients and vignettes, where the border holds several
colours); a heavily blurred frame as the background (the inside of every large flat shape then reads as
background, enclosed or not).

Measures per frame (all in % of the frame):
  coverage    content area
  empty       the largest axis-aligned rectangle of background
  elements    masses of at least MIN_ELEMENT of the frame
  subject     the largest mass: box [x, y, w, h] (top-left origin), area, centroid [cx, cy]
  bleed       the edges (top, right, bottom, left) where content covers at least BLEED_MIN of the edge
  masses      the boxes [x, y, w, h] of the elements, largest first (at most 12)
  text        from OCR line boxes (text.json "raw", same filters as text_frames.reclassify): text_pct (union of
              line boxes), cap_pct (0.75 x the tallest line), line_h_med (median line height of every confident
              line, small UI labels included: how readable a UI is), n_lines and words (of the kept lines), boxes
              [cx, cy, w, h] and cells (3 x 3 grid, row-major: 0 = top left, 4 = centre)
  objects     elements that are not text: OCR text covers under TEXT_SHARE of the element's box, or spans under
              TEXT_FILL of its height or width (a pill's label leaves a margin above and below). The lines of one
              paragraph merge into one block first (leading and a ragged right edge count as text), and each block
              grows by one analysis pixel (the blur around glyphs that the mass has and the OCR box has not);
  floating    those objects that touch no frame edge (a cut-out, a button, an avatar parked on the ground);
              floating_area is their summed box area
  cls         the sample's text class from text.json (demo, text_card, text_over, logo, other), or null; it is read
              on the full frame, padding included
  pad         (per film) the padding cut off, [top, right, bottom, left] in % of the full frame

Failure modes (seen on the worked example's storyboard stills):
  - A smooth subject that fills the frame (a soft close-up, a sky, a blurred photo) reads as background.
  - A soft-focus photo backdrop reads partly as background, partly as content.
  - A full-screen UI (the frame is the app: a white chat, a document, a terminal) has no outline inside the frame,
    so its own flat surface reaches the corners and reads as background; only its text and controls are content.
    Coverage then says "sparse page", not "small subject". check_frames.py does not use coverage alone for demo
    frames for this reason: a lone object also needs a non-text object that touches no edge.
  - A window or a phone that runs off a corner (its screen reaches the corner square) reads as background, as in v1.
  - The largest empty rectangle saturates near 30-40% around one centred object (the void splits into bands).
  - Heavy noise or a busy texture reads as content everywhere (coverage near 100%), which is right for footage.
  - Padding is cut only when it holds across the film: a caption burned into a bar on more than a fifth of the
    samples, or bars on part of the film only, leave the bars in, and the old error comes back for that film.
Output: {"settings", "fps", "duration", "aspect" (of the picture inside any padding), "pad", "text": bool,
"samples": [{"t", ...measures}]}.
Needs ffmpeg, numpy, Pillow.
"""
import argparse, json, math, os, statistics, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import text_frames  # noqa: E402
from frames import decode, probe  # noqa: E402

ANALYSIS_AREA = 160 * 90  # pixels per analysed frame (160 x 90 for 16:9)
DETAIL_STEP = 6           # 0-255 colour step to a neighbour that counts as detail; a soft gradient steps 0-2
CLOSE_R = 0.03            # of the short side (about 3 px at 160 x 90)
MIN_ELEMENT = 0.005       # of the frame: smaller masses (specks, a caret, a stray icon) are not elements
BLEED_MIN = 0.05          # of an edge's length
GROUND_MARGIN = 12        # 0-255: how far outside the ground's colour range a border-touching region may sit and still be ground
CORNER = 0.06             # of the short side: the corner squares a ground region must reach (about 5 px at 160 x 90)
TEXT_SHARE = 0.5          # an element whose box is at least this much OCR text is text, not an object
TEXT_FILL = 0.7           # ... and whose height and width are at least this much spanned by that text
PAD_MIN = 0.02            # of the height (top, bottom) or width (left, right): a thinner flat edge is not padding
PAD_MAX = 0.4             # of the same: a 9:16 film inside a 16:9 frame leaves 34% a side
PAD_TOL = 10              # 0-255: how far a bar pixel may sit from the bar's colour (compression noise)
PAD_FLAT = 0.97           # share of a bar row (column) within PAD_TOL of the bar's colour
PAD_EDGE = 0.9            # share of the first row (column) past the bar that differs from it: the picture's straight edge
PAD_SEEN = 0.25           # a film: share of its samples that show that straight edge
PAD_KEEP = 0.8            # a film: share of its samples that are flat and the bar's colour over the whole bar
PAD_ASPECTS = (2.76, 2.39, 2.35, 2.2, 2.0, 1.9, 1.85, 1.78, 1.6, 1.5, 1.33, 1.0, 0.8, 0.75, 0.5625, 0.5, 0.462)
PAD_ASPECT_TOL = 0.02     # the picture inside the bars is one of PAD_ASPECTS (cinema, TV, photo, square, 4:5, 9:16, phone
                          # screen recordings) within 2%: padding exists to fit a picture of one standard shape into another
SETTINGS = {'area': ANALYSIS_AREA, 'step': DETAIL_STEP, 'close': CLOSE_R, 'min_el': MIN_ELEMENT, 'bleed': BLEED_MIN, 'ground': GROUND_MARGIN,
            'corner': CORNER, 'text_share': TEXT_SHARE, 'text_fill': TEXT_FILL, 'pad': [PAD_MIN, PAD_MAX, PAD_TOL, PAD_FLAT, PAD_EDGE, PAD_SEEN, PAD_KEEP, PAD_ASPECT_TOL], 'v': 3}
EDGES = ('top', 'right', 'bottom', 'left')


def analysis_size(w, h):
    s = math.sqrt(ANALYSIS_AREA / (w * h))
    return max(16, round(w * s)), max(16, round(h * s))


def small(img):
    """A PIL image or an HxWx3 uint8 array -> float32 HxWx3 at the analysis size."""
    im = img if isinstance(img, Image.Image) else Image.fromarray(np.asarray(img, np.uint8))
    im = im.convert('RGB')
    size = analysis_size(*im.size)
    if im.size != size:
        im = im.resize(size, Image.BOX)
    return np.asarray(im, np.float32)


def pad_size(img):
    """A PIL image or an RGB array -> float32 HxWx3 at twice the analysis size per side, where padding is found."""
    im = img if isinstance(img, Image.Image) else Image.fromarray(np.asarray(img, np.uint8))
    w, h = analysis_size(*im.size)
    return np.asarray(im.convert('RGB').resize((2 * w, 2 * h), Image.BOX), np.float32)


def _band(a):
    """The flat band at the top edge of a float RGB array: (rows that sit within PAD_TOL of the top row's median colour
    on at least PAD_FLAT of their width, that colour, the share of the next two rows that differs from it)."""
    c = np.median(a[0], axis=0)
    off = np.abs(a - c).max(axis=2) > PAD_TOL
    flat = off.mean(axis=1) <= 1 - PAD_FLAT
    n = len(flat) if flat.all() else int(np.argmin(flat))
    return n, c, float(off[n:n + 2].mean(axis=1).max()) if n < len(flat) else 0.0


def find_pad(frames):
    """Encoded padding: letterbox bars (top and bottom) or pillarbox bars (left and right). frames: the samples of one
    film (or one still), float or uint8 RGB arrays of one size. Returns [top, right, bottom, left] in fractions of the
    frame, each one row (column) past the bar so the blended boundary goes too; 0 where there is none.
    An edge is padded when its band is PAD_MIN to PAD_MAX thick, ends at a straight edge (the next row differs from
    the bar on PAD_EDGE of its width) in at least PAD_SEEN of the film's samples, and is flat and the bar's colour in
    PAD_KEEP of them. Blank samples (one flat colour: a fade, a black frame) are left out. Bars come in pairs of one
    colour: a flat ground above a full-width subject, with none below, is not padding. And the picture inside them
    has a standard shape (PAD_ASPECTS): a full-height phone on a flat ground also leaves a flat band ending at a
    straight edge on each side, but the phone is rarely exactly 1:1, 4:5 or 9:16. On the lab corpus this test
    rejected one such film (a light phone on beige, 1.21:1 inside the bands). Why the straight edge: a flat ground
    around a lone object is flat up to the object too, but the first row that meets the object differs from the
    ground only across the object's width. Failure modes: a caption burned into a bar on more than a fifth of the
    film keeps that bar (and its partner) in the picture; a film padded for only part of its length is not cropped."""
    H, W = frames[0].shape[:2]
    views = {'top': lambda a: a, 'bottom': lambda a: a[::-1], 'left': lambda a: a.transpose(1, 0, 2), 'right': lambda a: a.transpose(1, 0, 2)[::-1]}
    size = {'top': H, 'bottom': H, 'left': W, 'right': W}
    bands = {e: [_band(np.asarray(v(f), np.float32)) for f in frames] for e, v in views.items()}
    live = [k for k in range(len(frames)) if bands['top'][k][0] < H]
    found = {}
    for e, bs in bands.items():
        seen = [bs[k] for k in live if PAD_MIN * size[e] <= bs[k][0] <= PAD_MAX * size[e] and bs[k][2] >= PAD_EDGE]
        if not seen or len(seen) < PAD_SEEN * len(live):
            continue
        n = int(np.median([b[0] for b in seen])); c = np.median([b[1] for b in seen], axis=0)
        if sum(bs[k][0] >= n - 1 and np.abs(bs[k][1] - c).max() <= PAD_TOL for k in live) >= PAD_KEEP * len(live):
            found[e] = (n, c)
    pairs = [(a, b) for a, b in (('top', 'bottom'), ('left', 'right'))
             if a in found and b in found and np.abs(found[a][1] - found[b][1]).max() <= PAD_TOL]
    n = {e: found[e][0] if any(e in p for p in pairs) else 0 for e in EDGES}
    shape = (W - n['left'] - n['right']) / max(1, H - n['top'] - n['bottom'])
    if not pairs or min(abs(shape / r - 1) for r in PAD_ASPECTS) > PAD_ASPECT_TOL:
        return [0.0] * 4
    return [round((n[e] + 1) / size[e], 4) if n[e] else 0.0 for e in EDGES]


def crop(img, pad):
    """The picture inside the padding: a PIL image or an array, cut by find_pad's fractions."""
    if not any(pad):
        return img
    t, r, b, l = pad
    if isinstance(img, Image.Image):
        W, H = img.size
        return img.crop((round(l * W), round(t * H), W - round(r * W), H - round(b * H)))
    H, W = img.shape[:2]
    return img[round(t * H):H - round(b * H), round(l * W):W - round(r * W)]


def crop_lines(raw, pad):
    """OCR lines (boxes in fractions of the full frame) moved into the cropped picture's fractions. A line whose centre
    sits in the padding (a caption in the bar) is dropped; the others are clipped to the picture."""
    if not any(pad):
        return raw
    t, r, b, l = pad
    sw, sh = 1 - l - r, 1 - t - b; out = []
    for L in raw:
        x, y, w, h = L['box']
        if not (l <= x + w / 2 <= 1 - r and t <= y + h / 2 <= 1 - b):
            continue
        x0, y0, x1, y1 = max(x, l), max(y, t), min(x + w, 1 - r), min(y + h, 1 - b)
        out.append(dict(L, box=[(x0 - l) / sw, (y0 - t) / sh, (x1 - x0) / sw, (y1 - y0) / sh]))
    return out


def _grow(m, r, op):
    """Separable square max (dilate) or min (erode) of radius r, edges replicated."""
    for ax in (0, 1):
        p = np.pad(m, [(r, r) if a == ax else (0, 0) for a in (0, 1)], mode='edge')
        n = m.shape[ax]
        stack = [p.take(range(k, k + n), axis=ax) for k in range(2 * r + 1)]
        m = np.logical_or.reduce(stack) if op == 'max' else np.logical_and.reduce(stack)
    return m


def _label(mask):
    """4-connected components of a bool mask: (label array, 0 = outside the mask; number of components)."""
    H, W = mask.shape
    lab = np.zeros(mask.shape, np.int32); n = 0
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys.tolist(), xs.tolist()):
        if lab[y, x]:
            continue
        n += 1; lab[y, x] = n; stack = [(y, x)]
        while stack:
            cy, cx = stack.pop()
            for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                if 0 <= ny < H and 0 <= nx < W and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = n; stack.append((ny, nx))
    return lab, n


def _components(mask):
    """4-connected components as a list of (area, y0, x0, y1, x1, cy, cx), largest first."""
    lab, n = _label(mask); out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        out.append((len(ys), int(ys.min()), int(xs.min()), int(ys.max()) + 1, int(xs.max()) + 1, float(ys.mean()), float(xs.mean())))
    return sorted(out, reverse=True)


def _ground(a, free):
    """Background: the smooth regions that reach a corner of the frame and share the ground's colours. The ground is
    the largest smooth region reaching a corner; another such region joins it when its median colour lies inside
    the ground's colour range (2nd to 98th percentile per channel) widened by GROUND_MARGIN. A gradient split in
    two by a tall subject stays background; a flat dark bezel or a solid block that runs off the edge does not.
    The corner test: a phone or a window cut by the frame edge leaves its flat screen touching the border only
    between the two sides of its own outline, away from the corners; the ground runs around the subject into a
    corner. So a screen inside a bezel stays content even when the bezel runs off the frame."""
    lab, _ = _label(free)
    H, W = free.shape; c = max(1, round(CORNER * min(H, W)))
    ring = np.unique(np.concatenate([lab[:c, :c].ravel(), lab[:c, -c:].ravel(), lab[-c:, :c].ravel(), lab[-c:, -c:].ravel()]))
    ring = ring[ring > 0]
    if not len(ring):
        return np.zeros(free.shape, bool)
    sizes = {int(k): int((lab == k).sum()) for k in ring}
    g = max(sizes, key=sizes.get)
    px = a[lab == g]
    lo, hi = np.percentile(px, 2, axis=0) - GROUND_MARGIN, np.percentile(px, 98, axis=0) + GROUND_MARGIN
    keep = [k for k in sizes if k == g or ((np.median(a[lab == k], axis=0) >= lo) & (np.median(a[lab == k], axis=0) <= hi)).all()]
    return np.isin(lab, keep)


def _max_rect(mask):
    """Area in pixels of the largest axis-aligned all-True rectangle (histogram method)."""
    H, W = mask.shape
    h = [0] * W; best = 0
    for row in mask.tolist():
        h = [h[i] + 1 if row[i] else 0 for i in range(W)]
        stack = []
        for i in range(W + 1):
            cur = h[i] if i < W else 0
            start = i
            while stack and stack[-1][1] >= cur:
                start, hh = stack.pop()
                best = max(best, hh * (i - start))
            stack.append((start, cur))
    return best


def masks(a):
    """detail, content and background masks of an analysis-size float RGB frame."""
    d = np.zeros(a.shape[:2], bool)
    d[:, :-1] |= np.abs(np.diff(a, axis=1)).max(axis=2) > DETAIL_STEP
    d[:-1, :] |= np.abs(np.diff(a, axis=0)).max(axis=2) > DETAIL_STEP
    r = max(1, round(CLOSE_R * min(a.shape[:2])))
    mass = _grow(_grow(d, r, 'max'), r, 'min')
    bg = _ground(a, ~mass)
    return d, ~bg, bg


def measure(img):
    """Pixel measures of one frame (PIL image or RGB array). All numbers in % of the frame."""
    a = small(img); H, W = a.shape[:2]; N = H * W
    _, content, bg = masks(a)
    comps = [c for c in _components(content) if c[0] >= MIN_ELEMENT * N]
    edges = {'top': content[0, :], 'right': content[:, -1], 'bottom': content[-1, :], 'left': content[:, 0]}
    out = {'coverage': round(100 * content.mean(), 1), 'empty': round(100 * _max_rect(bg) / N, 1),
           'elements': len(comps), 'bleed': [k for k, e in edges.items() if e.mean() >= BLEED_MIN], 'subject': None,
           'masses': [[round(100 * x0 / W, 1), round(100 * y0 / H, 1), round(100 * (x1 - x0) / W, 1), round(100 * (y1 - y0) / H, 1)]
                      for _, y0, x0, y1, x1, _, _ in comps[:12]]}
    if comps:
        n, y0, x0, y1, x1, cy, cx = comps[0]
        out['subject'] = {'box': [round(100 * x0 / W, 1), round(100 * y0 / H, 1), round(100 * (x1 - x0) / W, 1), round(100 * (y1 - y0) / H, 1)],
                          'area': round(100 * n / N, 1), 'c': [round(100 * (cx + 0.5) / W, 1), round(100 * (cy + 0.5) / H, 1)]}
    return out


def kept_lines(raw, aspect):
    """The OCR lines text_frames.reclassify keeps for size measures (confident, not tiny, not vertical)."""
    return [l for l in raw if l['conf'] >= text_frames.MIN_CONF and l['box'][3] * 100 >= text_frames.MIN_LINE_H
            and not (len(l['text']) >= 3 and l['box'][3] > 1.5 * l['box'][2] * aspect)]


def text_measures(raw, aspect):
    lines = kept_lines(raw, aspect)
    conf = [l for l in raw if l['conf'] >= text_frames.MIN_CONF and l['text'].strip()]
    G = 200; m = np.zeros((G, G), bool); boxes, cells = [], []
    for l in lines:
        x, y, w, h = l['box']
        m[max(0, int(y * G)):int(math.ceil((y + h) * G)), max(0, int(x * G)):int(math.ceil((x + w) * G))] = True
        cx, cy = min(max(x + w / 2, 0), 0.999), min(max(y + h / 2, 0), 0.999)
        boxes.append([round(100 * cx, 1), round(100 * cy, 1), round(100 * w, 1), round(100 * h, 1)])
        cells.append(int(cy * 3) * 3 + int(cx * 3))
    return {'text_pct': round(100 * m.mean(), 2), 'cap_pct': round(text_frames.CAP_RATIO * max((l['box'][3] * 100 for l in lines), default=0), 2),
            'line_h_med': round(statistics.median(l['box'][3] * 100 for l in conf), 2) if conf else None,
            'n_lines': len(lines), 'words': sum(len(l['text'].split()) for l in lines),
            'boxes': boxes, 'cells': cells}


def text_blocks(boxes):
    """OCR line boxes [cx, cy, w, h] (% of the frame) -> blocks [x0, y0, x1, y1]. The lines of one paragraph (heights
    within 30%, stacked at most one line height apart, overlapping across at least half the narrower line) merge into
    the box around them, so the leading between lines and a ragged right edge count as text, not as an object."""
    rs = [[cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2] for cx, cy, w, h in boxes]
    group = list(range(len(rs)))
    root = lambda i: i if group[i] == i else root(group[i])
    for i, a in enumerate(rs):
        for j in range(i + 1, len(rs)):
            b = rs[j]; ha, hb = a[3] - a[1], b[3] - b[1]
            if (min(ha, hb) >= 0.7 * max(ha, hb) and max(b[1] - a[3], a[1] - b[3]) <= max(ha, hb)
                    and min(a[2], b[2]) - max(a[0], b[0]) >= 0.5 * min(a[2] - a[0], b[2] - b[0])):
                group[root(j)] = root(i)
    blocks = {}
    for i, r in enumerate(rs):
        g = blocks.setdefault(root(i), list(r))
        g[:] = [min(g[0], r[0]), min(g[1], r[1]), max(g[2], r[2]), max(g[3], r[3])]
    return list(blocks.values())


def object_masses(masses, boxes, aspect=16 / 9):
    """The elements that are not text: masses ([x, y, w, h], % of the frame, largest first) whose box is less than
    TEXT_SHARE covered by text blocks (text_blocks of the OCR line boxes [cx, cy, w, h]). Each block grows by one
    analysis pixel a side first (aspect: the picture's width / height): a mass is found at the analysis size, where
    the blur of a glyph's edge adds about a pixel around the line, while OCR boxes hug the glyphs. On a 3%-tall UI
    row that pixel is a third of the mass's height, and without it the row reads as an object. A mass is text only
    if the text also spans TEXT_FILL of its height and of its width: a pill or a button is mostly its label, but the
    label leaves a margin above and below that a line of type does not have."""
    G = 200; k = G / 100; t = np.zeros((G, G), bool)
    aw, ah = analysis_size(aspect, 1); mx, my = 100 / aw, 100 / ah
    for x0, y0, x1, y1 in text_blocks(boxes):
        t[max(0, int(k * (y0 - my))):int(math.ceil(k * (y1 + my))), max(0, int(k * (x0 - mx))):int(math.ceil(k * (x1 + mx)))] = True
    out = []
    for x, y, w, h in masses:
        y0, x0 = int(k * y), int(k * x)
        sub = t[y0:max(y0 + 1, int(math.ceil(k * (y + h)))), x0:max(x0 + 1, int(math.ceil(k * (x + w))))]
        if sub.mean() < TEXT_SHARE or sub.any(axis=1).mean() < TEXT_FILL or sub.any(axis=0).mean() < TEXT_FILL:
            out.append([x, y, w, h])
    return out


def objects(masses, boxes, aspect=16 / 9):
    """(objects, floating, floating_area): the elements that are not text (object_masses), those of them that touch no
    frame edge, and the floating ones' summed box area in % of the frame. A floating object is what a "lone object on
    a void" is made of: a cut-out, a card, a pill, a device. masses are [x, y, w, h] and boxes [cx, cy, w, h], in % of
    the frame."""
    obs = object_masses(masses, boxes, aspect)
    fl = [(w, h) for x, y, w, h in obs if x > 0.5 and y > 0.5 and x + w < 99.5 and y + h < 99.5]
    return len(obs), len(fl), round(sum(w * h / 100 for w, h in fl), 1)


def analyze(video, text=None, fps=2):
    """Measure every sample of a film at `fps` (the same instants as text_frames.py). `text` is the film's text.json
    dict; without it, or when its OCR did not run, the text measures and classes are null. The film's padding
    (find_pad over all its samples) is cut off every sample, and the OCR boxes are moved into the picture, before
    anything is measured."""
    info = probe(video)
    W, _ = analysis_size(info['w'], info['h'])
    frames, _ = decode(video, fps=fps, width=2 * W, gray=False)  # padding is found at twice the analysis size
    pad = find_pad(frames) if len(frames) else [0.0] * 4
    if not any(pad):  # unpadded: measure frames decoded at the analysis size, as version 2 did
        frames, _ = decode(video, fps=fps, width=W + W % 2, gray=False)
    aspect = info['w'] / info['h'] * (1 - pad[1] - pad[3]) / (1 - pad[0] - pad[2])
    tx = text if text and text_frames.has_text(text) else None
    tsamples = tx['samples'] if tx else []
    samples = []
    for k, f in enumerate(frames):
        s = {'t': round(k / fps, 2), **measure(crop(f, pad))}
        ts = tsamples[k] if k < len(tsamples) else None
        if ts is not None:
            s.update(text_measures(crop_lines(ts['raw'], pad), aspect), cls=ts.get('cls'))
            s['objects'], s['floating'], s['floating_area'] = objects(s['masses'], s['boxes'], aspect)
        else:
            s.update(text_pct=None, cap_pct=None, line_h_med=None, n_lines=None, words=None, boxes=[], cells=[], cls=None, objects=None, floating=None, floating_area=None)
        samples.append(s)
    return {'settings': SETTINGS, 'fps': fps, 'duration': round(info['duration'], 2), 'aspect': round(aspect, 4),
            'pad': [round(100 * p, 1) for p in pad], 'text': tx is not None, 'samples': samples}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('video'); ap.add_argument('--text'); ap.add_argument('--out'); ap.add_argument('--fps', type=float, default=2)
    a = ap.parse_args()
    tx = json.load(open(a.text)) if a.text else None
    if tx:
        text_frames.reclassify(tx)
    r = analyze(a.video, tx, a.fps)
    if a.out:
        json.dump(r, open(a.out, 'w'))
    S = r['samples']
    med = lambda k: statistics.median(s[k] for s in S) if S else None
    print(f"{os.path.basename(a.video)}: {len(S)} samples, coverage median {med('coverage')}%, empty median {med('empty')}%, "
          f"elements median {med('elements')}, padding {r['pad']}%, text {'measured' if r['text'] else 'unavailable'}")


if __name__ == '__main__':
    main()

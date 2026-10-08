# The quality bar

## The reference film

The worked example's final film: 83.1 s, 60 fps, real iOS and web UI, no voiceover, delivered in 16:9, 4:5 and 9:16. It is the final of nine versions, signed off by the owner as "the launch video, I want the best quality". This page describes it fully, so you can use the bar without the film. Watch it once: `examples/kallo-launch-film/assets/films/kallo_v9d_16x9_light.mp4`. Then measure your own film against the checklists below rather than against memory.

It is one style (calm, high-fidelity, motion design only). It shows the level of finish to reach, not the look to copy.

Its structure, as an example of a spine carrying many features (scene durations in seconds):

| Scene | s | What it does |
|---|---|---|
| Opening | 21.35 | "Introducing Kallo" → the product line → a careless meal typed, sent, morphing into the phone; its result → "Kallo pays attention to details that matter." → the same meal rewritten in detail → both cards side by side, "+245 kcal from the details" |
| From barcode scanning… | 1.45 | Line alone on the gradient |
| Barcode | 3.0 | Camera onto a real product's barcode, the result sheet rises |
| …to nutrition label reading | 1.45 | Line |
| Label | 4.8 | Camera onto a real label, shutter, the extracted nutrition |
| Web | 13.0 | Phone morphs into a browser; the camera rides the caret as a lunch is typed; two status words; rows land; Save; the gauge fills; zoom out to the feed |
| Belief | 3.05 | "At Kallo, we believe every journey works out better when we all feel supported. Especially dieting." in four quick lines |
| Circle | 6.5 | Friends' faces gather and fly into a feed that fills post by post; a like; the groups |
| Relog line + relog | 1.55 + 4.85 | The whole phone, then its lower two-thirds; "/" opens recent dishes; relogged instantly; Save |
| Share line + share | 1.5 + 12.8 | A pizza already read; Save; share; four friends join; the camera tightens on the split bar; drag your portion; Share, with confetti in place |
| Micronutrients | 3.8 | "Not just calories and macros." in a bedroom at night; the nutrient tiles burst out, hold, fly back into the phone |
| End | 4.0 | Home, the wordmark lifts from the header to centre; "Try it now / kallo.fit" |

Time of day moves from dawn to night through real-feeling rooms, with a hand-drawn clock top-left. Roughly three-quarters of the runtime is the product, about a sixth is standalone text, and the end card takes about 5%.

## Two checklists

Run both on every version before sending. Each item is checkable.
1. **Always:** product truth and technical quality. The same in every style and branch.
2. **This film's style checklist:** written from the approved brief, the chosen direction and the research. It changes per film.

### 1. Always

**Product truth**
- [ ] Every UI pixel is from a recording or screenshot of the real build, not re-implemented.
- [ ] Every number on screen came from a real run of the product.
- [ ] No leaked dev state: debug banners, wrong clock, test names, error toasts.
- [ ] The product's fonts, colours and voice throughout, or the approved provisional system, unless the owner chose a concept that changes them.
- [ ] Claims to avoid (from the brief) are absent from the film and the post copy.

**Picture**
- [ ] No frame-level jank: no freezes then pops, no mis-seeks, no flashes of a wrong segment. Step through each cut ±5 frames.
- [ ] Recorded typing in the product is letter-level: step through 10 frames of every typing shot.
- [ ] Cut-outs have one clean border at the app's real radius.
- [ ] Nothing important under platform UI: in 9:16, inside the safe band and clear of the right-hand button column (`delivery.md`); the proof moment never obscured.
- [ ] Every line of text is readable at phone size and stays up long enough to read.
- [ ] Zoom-check: dense frames viewed at 2× for overlaps and clipped edges.
- [ ] Frame composition checked: `check_frames.py` run on the storyboard stills against the corpus baseline; every FLAG fixed or answered on the board (`storyboard.md`).

**Sound**
- [ ] Loudness measured on the delivered file: integrated and true peak meet the target in `sound.md`.
- [ ] Speech, if any, is intelligible over the music; captions match it.

**Delivery**
- [ ] Every file probed: resolution, fps, duration, audio stream. Each meets the destination's spec (store previews: `branches.md`).
- [ ] The delivered duration equals the approved timeline; no seconds lost to a short mix.
- [ ] 4–6 frames sampled from each final file and looked at.
- [ ] Light copies made; file names say the cut and the ratio.
- [ ] Caption credits ready for any openly licensed imagery; music licence recorded.

**Process**
- [ ] The storyboard for this version was signed off before the full render.
- [ ] Every numbered ask from the last round is closed or answered.

### 2. This film's style checklist

Write it in `film/brief.md` after the concept is picked, and get it confirmed with the storyboard. Build each item from one of four sources, and name the source:
- **the brief:** pace, people, voiceover, captions, platforms;
- **the chosen direction's rules** (`distilling.md`), with their numbers;
- **the research medians** for this style (`measuring.md`): demo, text and logo shares, cut rate, text-card hold;
- **the owner's explicit asks** from each review round.

Start from the defaults in `SKILL.md` ("Defaults from the worked example") and keep, change or drop each one for this film. Every item must be checkable: a count, a duration, a yes or no per frame.

**Example: the worked example's style checklist.** Calm high-fidelity product film, motion design only, no voiceover.
- [ ] No frame has a lone object on an empty ground. Check the contact sheet.
- [ ] Every text card is 1–2 lines, at most about 8 words, and stands alone.
- [ ] No captions over the demo.
- [ ] Phone demos show about two-thirds of the phone; the whole phone only for a beat.
- [ ] Camera keys per demo scene: about one move per 1–2 s at most; zooms only on key clicks.
- [ ] At most two status or loading words per analysis shown. Count them from frames.
- [ ] Something changes every 2–3 s.
- [ ] Text cards hold about 2 s; a reveal holds about 1 s before the next move.
- [ ] Demo, text and logo shares and cut rate measured with the research pipeline, and compared with the research medians.
- [ ] A sound on every visible event; none on events off screen.
- [ ] The music's structure serves the story: a drop or silence before the key moment, the hit on the name.
- [ ] Film mix at about −16 LUFS integrated, −1.5 dB true peak; teaser about −1 dB peak.

**Example: a different brief.** A 30 s founder video for a web dashboard, captions on. Its list might read: the founder on screen at most 40% of the runtime; every product claim cut to real UI within 1 s; captions on every spoken line, 1–2 lines, inside the safe band; the browser window, never a phone; music at least 12 dB under the voice.

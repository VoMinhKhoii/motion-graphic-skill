# Measuring: turn watching into numbers

Frames tell you what a film looks like. Measurements tell you how it spends its time, which is what makes a film feel "high fidelity" or "slow". The breakthrough in the worked example came when the owner asked to study the distribution over time (demo vs text, transition types, morphing), not just frames. Do both passes.

## Pass A: measured, every film, automatic

Run the whole corpus with one command (`$SKILL/scripts/research/PIPELINE.md` has the full runbook):
```bash
"$SKILL/scripts/research/pipeline/run_corpus.py" film/research/vids film/research/corpus --account-from-filename --jobs 3
```
For one or a few films, the per-film analyser alone:
```bash
"$SKILL/scripts/research/analyze_video.py" film.mp4 [more.mp4 ...] --out an [--thresh 0.3] [--n 24]
```
Every positional argument is a video; the output folder goes after `--out` (default `an/`), one subfolder per film.

What each script samples, as the code does it:

| Measure | Script | Sampling |
|---|---|---|
| Cuts | `analyze_video.py` | ffmpeg scene score on every decoded frame, cut when above `--thresh` (0.3 suits UI films, 0.4 live action); cuts a minute and median shot in `stats.json` |
| Contact sheet | `analyze_video.py` | `--n` frames (default 24), evenly spaced, each stamped with its time |
| Motion energy | `analyze_video.py` | luma change between frames 0.1 s apart (10 fps), averaged per second. It separates "camera still, motion inside the frame" from "camera moving" |
| Loudness | `analyze_video.py` | RMS every 0.25 s, plus integrated LUFS (ffmpeg `ebur128`) and a spectrogram |
| Transitions, camera | `pipeline/transitions.py` | 15 fps at 160 px wide; type and length of every boundary; camera state per 0.5 s |
| Text classes | `pipeline/text_frames.py` | OCR at 2 fps; each sample is demo, text card, text over demo, logo or other |
| Composition | `pipeline/composition.py` | the same 2 fps samples at about 160 x 90 px; content coverage, largest empty region, subject box, edge bleed, elements, text area and position |
| Review sheets | `pipeline/review_sheet.py` | `--fps` you choose (4 is a good start) over a `--from`/`--to` window |
| Strips | `strips.py` | frames at the times you list; list times 0.1 s apart for a 10 fps strip |

The worked run measured 123 films with an earlier version of these tools at 4 fps; the numbers below come from it.

**Read the report's counts before the numbers.** The report states how many films were attempted, how many succeeded and how many failed. When OCR is missing or a step fails, the shares that depend on it show as unavailable, not as 0%. A "demo 0%" next to "OCR: none" is not a measurement. If any film failed or a measure is unavailable, tell the owner what is missing and get an explicit decision (re-run, accept the partial corpus, or count that measure in the watched pass) before you distil from it.

## Pass B: watched, by hand (5–30 films, by scope)

Log each film second by second in a table:

| t0 | t1 | on screen | text (words, lines, size as % of height) | transition into this shot (type, length) | camera | sound |
|---|---|---|---|---|---|---|

- **On screen categories:** demo (product on screen), text card, text over the demo, logo or end card, other (imagery, metaphor), transition.
- **Transition types:** hard cut, camera move, the app's own UI state change, push or slide, crossfade, scale-out, scale-into, morph (shape A becomes B), type-on or off, match cut, mask reveal, wipe. Log the length of each to 0.1 s using 10 fps strips.
- **Camera states:** still, motion inside the frame only, pan, zoom in, zoom out.
- **Sound:** bed, SFX on events, silence, the hit before the name.

Use 8–12 fps strips (`$SKILL/scripts/research/strips.py`, times listed 0.08–0.12 s apart) for any transition you want to reproduce; 13 frames at 10 fps covers 1.2 s.

## The tables to produce

1. **Where the seconds go:** per film and per account, the share of runtime for demo, text card, text over demo, logo, other. Median over films.
2. **Text:** the median length of a standalone card (seconds), words per card, lines, cap height as a percentage of frame height.
3. **Demo beat:** how long a demo shot runs before something changes.
4. **Cuts a minute, per account.** This is the pace dial.
5. **Transition mix:** share and median length per type.
6. **Camera:** share of time still, inside-frame motion, pan, zoom.
7. **What stays fixed across designed transitions:** for each exemplar move, name the element that holds its place (a headline, a bubble, the frame centre).
8. **Composition, per role:** content coverage (p10, median, p90), edge bleed share, subject size, card cap height, lines and words, and where text sits on a 3 x 3 grid. From the report's Composition section.

## Composition: how the frame is filled

Time measures say how a film spends its seconds. They say nothing about whether a frame is full or a small object parked on an empty ground. In the worked example the first concept frames were exactly that: food cut-outs and small cards floating on cream. The owner asked which reference film did that; none did. So measure the frame too, and hold the storyboard to it.

**What** (`pipeline/composition.py`, per 2 fps sample, every number a % of the frame):
- **content coverage:** the area that is not background;
- **largest empty region:** the biggest axis-aligned rectangle of background;
- **subject:** the box, area and centre of the largest mass;
- **edge bleed:** which edges the content runs off;
- **elements:** separate masses of at least 0.5% of the frame; **floating objects** are the ones that are not text and touch no edge;
- **text:** area, cap height, the median line height of UI text, lines and words, and the 3 x 3 cell of every OCR line;
- **role:** the sample's text class (demo, text card, text over, logo, other), so cards are compared with cards;
- **padding:** letterbox or pillarbox bars encoded into the file, cut off before anything else is measured.

**How.** First the padding goes. Bars fill every corner, so without this they become the ground and the picture's own empty ground inside them reads as content: a centred object on cream measured 81% content and bled off both sides instead of 9%. A film is padded when a pair of flat bands of one colour (top and bottom, or left and right, 2–40% thick) ends at a straight edge across 90% of the frame in a quarter of its samples, stays flat in 80% of them, and leaves a picture of a standard shape inside (2.39:1, 1.85:1, 4:3, 1:1, 4:5, 9:16 and so on, within 2%). The shape test is what keeps a full-height phone on a flat ground from reading as pillarboxed. Then each frame is shrunk to about 160 x 90 px. A pixel is detail when its colour steps by more than 6 levels to a neighbour. Details closer than about 6% of the short side merge into masses, so a paragraph or a phone screen is one mass. Background is the smooth area that reaches a corner of the frame and shares the ground's colours. That rule covers flat colour and soft gradients alike. It keeps a flat panel inside an outline (a card, a phone screen in its bezel) as content, also when the phone runs off the bottom of the frame: its screen touches the edge only between the two sides of its bezel, never in a corner. Version 1 accepted any edge and read those screens as background: a full-height phone on a photo measured 57% content instead of 99%.

**Failure modes** (seen on 42 lab frames sampled across coverage deciles and roles, and on our own boards, each with its background mask beside it):
- A full-screen UI (the frame is the app: a white chat, a document, a terminal) has no outline inside the frame. Its own surface reaches the corners and reads as background; only its text and controls count. Most of the lab's low-coverage demo frames are this (demo p10 is 15%). There, coverage means "sparse page", not "small subject", so the rules below never use coverage alone.
- A window or a phone that runs off a corner reads as background inside, as in version 1.
- A smooth subject that fills the frame (a soft close-up, a sky, a blurred photo) reads as background; a soft-focus photo backdrop reads partly as background.
- The largest empty rectangle saturates around 30–40% when one object sits in the middle: the void is split into bands.
- A sliver of contact counts as bleed: a composer pill whose shadow grazes the left edge "runs off the frame", while the same pill 1% further in floats.
- Objects close together merge into one mass: a row of five small mascots is one wide element.
- A single still has no film to confirm its padding. On 300 lab and 150 Google stills, 6 read as padded: 2 real letterboxes and 4 full-height panels or windows on a flat ground whose inside happened to be a standard shape. None changed a verdict: such a subject already runs off two edges.
- Bars on part of a film only, or with a caption burned into them on more than a fifth of the samples, are not cut.

**The rules** (`pipeline/check_frames.py`, by role). The target is the owner's rule: full bleed, the subject fills the frame and runs off its edges; empty space only around one line of type alone on its ground.
- **Lone object on a void** (demo, text over picture, other): nothing runs off the frame, at least one non-text object (a card, a pill, a device, a cut-out) touches no edge, and content covers less than the corpus demo p25 (25.2% in the lab corpus). Type alone on its ground never trips it, nor does a sparse full-screen UI.
- **Too far away** (demo): the subject is not text (a device, a window, a card, a cut-out), touches no edge and is both shorter and narrower than 0.8 x the corpus demo subject p10 (under 23.1% tall and 37.0% wide in the lab corpus). A subject that is a line or a paragraph of type is never too far away: a sparse UI's rows are not a distant device. A mass counts as text when OCR text covers half its box and spans 70% of its height and width; a pill's label leaves a margin above and below, so the pill stays an object.
- **Text card:** a frame that is only text set at card size is a card, however many words it has (without that rule the text classifier calls 12 or more words a dense UI, so a long card escaped the card limits). Cap height under 0.9 x the corpus card p10 (3.93%), more lines than the card p90 (3), or more words than 1.5 x the card p90 (13.5). A card may be mostly ground, and an icon beside the line is fine: about a third of the lab's cards carry one.
- **Logo:** reported, not checked.
- **Roles.** A storyboard knows each beat's role, so pass it: `--roles roles.csv` with rows like `03_card.png,card`. Without it the role is guessed from OCR, and the guess cannot tell a card set in small type from a sparse UI page.
- **Dropped:** the coverage floor and empty-region ceiling on their own, and the UI line-height floor. Small UI type is natural in a whole-phone shot: 17 of the 25 v9 frames flagged by the first version were that floor. On the same frames the old limits flagged 40 of 300 lab frames, 24 of 129 v9 frames and 7 of 26 round-2 frames.

**Validation** (lab corpus as the baseline; verdicts by eye from contact sheets of every flagged frame and every round-2 frame):

| Set | Frames | Flagged | By eye |
|---|---|---|---|
| Round 2, lone objects on a void | 9 | 8 | the miss: five small mascots in a row, one merged mass at 29% content (flagged with the Google or teaser baseline) |
| Round 2, text cards, logos, full-bleed frames | 12 | 1 | a four-line rotating-word card |
| Round 2, two devices beside a headline; half-frame photos | 5 | 0 | borderline; the lab films do the same (a phone and a desktop on a gradient) |
| Approved v9 board | 129 | 5 | avatars floating on an aurora (a fault the owner also caught) and four composer-pill close-ups read as cards with UI-size type; a fifth pill passes because its shadow touches the edge |
| Lab films, random | 300 | 28 (9.3%) | about 20 are the lab's own lone objects (illustrations, composer pills, a button on cream); about 8 are wrong (logo tiles read as 5 lines, a glow on black, UI frames read as cards) |
| Google films, random | 150 | 11 (7.3%) | not judged frame by frame |

Re-run after padding, the card rule and the text-subject rule were added (composition version 3, lab baseline 25.2 / 23.1 / 37.0%): the same frames are flagged in all four sets. Two round-2 frames changed role, both to text card and both right by eye (a wordmark with its tagline still passes; the four-line card is still flagged).

Over the whole lab corpus the lone-object rule fires on 419 of 5,295 samples (8%), and by eye most of those are real: minimal lab films do park an illustration or a composer on an empty ground now and then. A FLAG asks for a fix or a written reason; it is not a ban.

**Where baselines live.** `run_corpus.py` writes `films/<id>/composition.json`; `aggregate.py` puts the per-role p10, p25, median and p90 in `corpus.json` under `overall.composition.by_role` (and per account); the report shows them. `pipeline/check_frames.py --baseline corpus/corpus.json` holds storyboard stills to them (`storyboard.md`). Without a corpus it uses defaults rounded from the lab corpus and says so. The worked example's numbers by role are in `library/baselines.md` (Frame composition).

## Numbers from the worked run (high-fidelity labs)

These describe one taste (OpenAI, Claude, Manus and xAI launch films, 2025–26). Re-measure for yours.

| Metric | Value |
|---|---|
| Demo share of runtime | 67% median (24 films) |
| Standalone text | 11%; text over demo 0% |
| Logo / end | 7% |
| Text card | 2.6 s median (half between 2.0 and 3.4 s); about 6 words on 2 lines |
| Headline-size type | about 3 words, about 2.1 s on screen |
| Demo beat | 2.9 s median |
| Cuts a minute | Claude 16.5 · Manus 13.6 · OpenAI 5.7 · Google 3.7 · xAI 1.9 |
| Transitions | 298 logged. Hard cut 21% · camera move 14% (0.5 s) · app's own UI state change 11% (0.3 s) · push/slide 11% (0.4 s) · crossfade 9% (0.4 s) · scale-out 9% (0.4 s) · morph 8% (0.7 s) · type-on/off 6% (0.7 s) · scale-into 6% (0.4 s) · match cut 3% · mask reveal 2% (0.7 s) · wipe 1% (0.3 s) |
| Camera | Still 54% · inside-frame motion 23% · pan 6% · zoom in 4% · zoom out 4% |
| Fixed element | 11 of 12 exemplar transitions hold one element in place |

The write-up with the twelve exemplar moves is in `library/research/findings.md`, and the frame strips of each move in `library/research/boards/motion.html`. The same medians are in `$SKILL/library/baselines.md`.

## Turn numbers into rules

End the measuring phase with a short "N rules" board: each rule is one sentence, a concrete target for the film's length, and the number it rests on. They are rules for this film's style, not for every film. From the worked run:
1. Two-thirds of it is the product.
2. One text card, maybe two.
3. No captions over the demo.
4. Something changes every three seconds.
5. Fast is about eight cuts in 30 s.
6. Let the app animate itself.
7. Hold the camera still about half the time.
8. Keep one thing fixed through every designed transition.
9. Borrow the slow account's moves, not its pace.

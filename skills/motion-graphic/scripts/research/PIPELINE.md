# Reference pipeline: from "style X" to a measured, browsable corpus

This is the runbook for `references/reference-research.md` and `references/measuring.md`. It takes a chosen style, finds films in that style on several platforms, downloads them, measures them automatically, and builds a local board. A human watched pass then confirms the films the direction will rest on.

```
discover/   find accounts and films        youtube_search.sh, youtube_channel_filter.py, tiktok.sh,
                                           x_search.md + x_collect.js, threads_search.md + threads_collect.js,
                                           instagram.md, web_queries.md, style_seeds.md
download    ../download.sh (yt-dlp)        Threads: curl the video src (threads_search.md)
pipeline/   measure and report             run_corpus.py -> transitions.py, text_frames.py, composition.py,
                                           ../analyze_video.py; aggregate.py -> corpus.json, report.py -> index.html
                                           review_sheet.py for the watched pass; check_frames.py for storyboard
                                           stills; tests/ for the synthetic checks
```

Needs: `yt-dlp`, `ffmpeg`/`ffprobe`, `python3` with `numpy` and `Pillow`; for text, `swiftc` (macOS, Xcode command-line tools) or `tesseract`. Everything runs locally. Keep the corpus and its outputs private: they hold third-party frames.

## 1. Discover

Start from the owner's answer to the style question (`references/intake.md`).

1. **Seeds.** Take the owner's named accounts, then fill from `discover/style_seeds.md` (each entry needs a "still active" check).
2. **Web.** Run 3–6 queries from `discover/web_queries.md` for the style. Note accounts that come up twice.
3. **YouTube.** Search, or scan a channel and filter it:
   ```bash
   discover/youtube_search.sh "app launch video motion design" 40 --max-dur 120 --min-views 10000 --out lists/yt_search.jsonl
   scan_channel.sh raycastapp lists 200                       # ../scan_channel.sh
   discover/youtube_channel_filter.py lists/yt_raycastapp.jsonl --title 'introducing|launch|meet|new' --max-dur 120 --urls urls.txt
   ```
   Flat search returns no upload date; add `--full` (about 1–2 s per hit) when the date matters.
4. **X.** In the user's logged-in browser, open a search from `discover/x_search.md` (for example `from:<handle> filter:native_video`) and run `discover/x_collect.js` with the session's browser tool. It reads the page DOM only. Append the URLs to `urls.txt`.
5. **Threads.** Same route with `discover/threads_collect.js`; yt-dlp has no Threads extractor, so download each `video_src` with `curl` right away (`discover/threads_search.md`).
6. **TikTok.** `discover/tiktok.sh <handle> lists` lists a profile logged out; filter it with `youtube_channel_filter.py`. Hashtag and search extraction are unreliable.
7. **Instagram.** Single reel URLs only; see `discover/instagram.md`.

Films per account follow the agreed scope (`reference-research.md` §0): Quick 3–6 from each of 2–4 accounts, Standard 10–15 from each of 3–5, Full 20–35 from each of 4–8.

## 2. Download

```bash
../download.sh urls.txt vids/      # <uploader>__<id>.mp4 + .info.json, <=1080p, resumable
```

For Threads and Instagram files fetched by hand, name them `<handle>__<id>.mp4` and write a small `.info.json` (`title`, `uploader_id`, `webpage_url`, `description`).

## 3. Measure: run_corpus

```bash
pipeline/run_corpus.py vids/ corpus/ --account-from-filename --jobs 3
open corpus/index.html
```

Resumable: a step is skipped when its output is newer than the film and, for text, was measured with the same OCR engine and settings (changing `--ocr` re-measures text; `--force` redoes everything). `composition.json` is redone when `text.json` is newer or `composition.SETTINGS` changed. Re-run after adding films, or delete one film's `transitions.json`/`text.json` to redo that step. `aggregate.py` and `report.py` re-run at the end every time; both are fast (seconds), and `aggregate.py` re-applies the text thresholds from the stored OCR lines, so tuning `text_frames.py` constants needs no new OCR.

Per film it writes `corpus/films/<stem>/`: `meta.json`, `transitions.json`, `text.json`, `composition.json`, strip.jpg, and, from `../analyze_video.py`, `stats.json`, `cuts.json`, `curves.json`, sheet.jpg, curves.png, spectrogram.png.

**Timing** (Apple M2, one job): about 1 s of compute per second of film. OCR is 0.6 s of it (Vision, accurate mode), transitions 0.25 s, `analyze_video.py` 0.12 s, composition 0.04 s (a 73 s 1080p film took 2.5 s). The 25-film test corpus (13 minutes of film, one 5-minute film included) took about 3.5 minutes with `--jobs 3`. Use `--ocr tesseract` off macOS, or `--ocr none` to skip text entirely.

**Failures are loud.** A film that fails does not stop the others, but the run prints the failed list at the end and exits 1; `<out>/run.json` is the run manifest: the films selected, succeeded, failed and `ocr_failed`, the resolved OCR engine and the settings. `aggregate.py` pools only that run's succeeded films, so stale film folders from earlier runs are never counted; `--include-history` pools every complete folder on purpose, and the report says so. The report's header shows the counts. `--ocr vision` or `--ocr tesseract` stops at once if that engine is missing; an OCR call that crashes or returns nothing marks that film's text unavailable and the run exits 1. With `--ocr auto` and no engine (or `--ocr none`), the demo, text card, text-over, logo and other shares are null (shown as –, unavailable), never 0: only cuts, transitions and camera are measured. Tell the owner and decide together before going on with partial results.

## 4. Report

`corpus/index.html` is a static page; open it from disk. It shows:
- the overall and per-account table: boundaries per minute (and cuts only), median shot, demo beat, where the seconds go, text-card hold/words/cap height, the transition mix and the camera bar;
- the transition mix table (count, share, median length per type);
- **top transitions:** for each type, the highest-scoring examples spread over accounts, as 10 fps strips from 0.2 s before to 0.2 s after. Check these first: they show at a glance whether a class means what it says in this corpus;
- **composition:** per role (all, demo, text card, text over, logo, other), the p10 / median / p90 of content coverage, largest empty region, elements, subject area, card cap height and floating objects, the share of samples with edge bleed; histograms of coverage and empty region; a 3 x 3 heat map of where text sits; one row per account. `corpus.json` also holds p25, subject width, lines and words per role: `check_frames.py` takes its limits from there;
- per film: a to-scale timeline (category per 0.5 s), transition ticks above it (lines for cuts, coloured spans for gradual ones), the camera row below it, a 16-frame strip, and its text cards.

## 5. The watched pass (do not skip)

The automatic classes are a first pass. Confirm the films you will lean on by watching them: 5–8 for a Quick scope, 10–15 for Standard, 15–30 for Full (`reference-research.md` §0).

1. Pick the films: the ones closest to the chosen style, plus every film a direction will cite.
2. For each, make a labelled sheet and compare it with what you see:
   ```bash
   pipeline/review_sheet.py corpus/ <stem> --fps 4 --from 0 --to 12      # -> corpus/films/<stem>/review_0-12.jpg
   ```
   Every frame is stamped with its time, text class and camera state; a coloured bar marks the first frame after each transition, with its type and length. Downscale before reading it in an agent session (`sips -Z 1000`).
3. For any transition you may reproduce, take a 10 fps strip (`../strips.py`) and time it to 0.1 s.
4. Write the second-by-second table from `references/measuring.md` (Pass B). Where it disagrees with the automatic numbers, the watched table wins; note the disagreement, because it tells you which automatic numbers to trust for the rest of the corpus.

## 6. Check storyboard frames against the corpus

Once `corpus.json` exists, every storyboard's stills are checked for composition before the owner sees them (`references/storyboard.md`):
```bash
pipeline/check_frames.py film/engine/out/stills --baseline corpus/corpus.json --roles film/boards/roles.csv
pipeline/check_frames.py film/engine/out/stills --baseline corpus/corpus.json            # roles guessed by OCR
pipeline/check_frames.py stills/ --debug masks/                                          # default limits; masks to look at
```
Each frame prints PASS or FLAG with reasons ("lone object on a void: 2 objects touch no edge, nothing runs off the frame, content 17.5% (limit corpus demo coverage p25 x 1 = 25.2%)", "too far away: subject 20 x 18% touches no edge", "card type small: cap 3.38% (floor corpus text_card cap_pct p10 x 0.9 = 3.93%)"); exit code 1 if any frame is flagged. `--roles` maps file names to roles (CSV rows `03_card.png,card` or a JSON object); the storyboard knows each beat's role, so pass it. Without it the role is guessed: a frame that is only text at card size is a card, however many words it has, and the rest go through `text_frames.classify`. Letterbox and pillarbox bars are cut off before measuring, in stills as in films. The rules are by role and are described, with their validation, in `references/measuring.md` (Composition). A limit whose corpus role has fewer than 30 samples from 3 films falls back to its default (rounded from the worked example's lab corpus), and the reason says "default". `--json` writes every measure.

## How the outputs map to the tables in measuring.md

| measuring.md table | corpus.json field | Notes |
|---|---|---|
| 1. Where the seconds go | `share` (per film, median per account and overall): demo, text_card, text_over, logo, other, transition | From 2 fps OCR samples plus the gradual-transition spans. "other" includes imagery, footage, and UIs with almost no text. |
| 2. Text | `card_hold_s`, `card_words`, `card_lines`, `card_cap_pct`; the `cards` list | Hold is in 0.5 s steps. Cap height is 0.75 x the OCR line box (about +-15% across typefaces). |
| 3. Demo beat | `demo_beat_s` | Unbroken demo stretch, split at any boundary. Only as good as the demo class. |
| 4. Cuts a minute | `cuts_per_min` (all boundaries), `hard_cuts_per_min`, `ffmpeg_cuts_per_min` | The watched tables in the worked example counted cuts plus designed transitions, which is closest to `cuts_per_min`. |
| 5. Transition mix | `mix`: n, share, median_dur per type | Automatic types: cut, dissolve, push, zoom_in, zoom_out, other. See the mapping below. |
| 6. Camera | `camera_pooled` (share of all 0.5 s windows), `camera` (median per film), `camera_per_s` | still, inframe, pan, zoom_in, zoom_out, transition. |
| 7. What stays fixed | not measured | Watched pass only. |
| 8. Composition | `composition` (per film: per-role medians, the padding cut off as `pad`, and the samples; per account and overall: `by_role` p10 / p25 / median / p90, `padded` films, `coverage_hist`, `empty_hist`, `text_grid`) | Per 2 fps sample, transition samples left out, each film weighted equally within a role. Letterbox and pillarbox bars are cut off before measuring. See `composition.py`'s docstring for the method. |

Automatic type to watched type: **cut** = hard cut (and many match cuts). **dissolve** = crossfade. **push** = push or slide, and whip pans. **zoom_in / zoom_out** = scale-into, scale-out, zoom-throughs, and fast camera zooms that end on a new picture. **other** = morph, mask reveal, wipe, type-on or off, the app's own UI state change, fade through black, fast montages. The watched pass splits "other".

## Precision: what was measured

**Synthetic clips** (`pipeline/tests/make_clips.py` makes four clips with known truth; `pipeline/tests/check_clips.py` scores them):

```bash
pipeline/tests/make_clips.py /tmp/synthetic && pipeline/tests/check_clips.py /tmp/synthetic
```

| Case | Truth | Found |
|---|---|---|
| Hard cuts (7) | at 2.0, 6.6, 3.0, 5.5, 7.5, 4.5, 7.0 s | all 7, within 0.03 s |
| Crossfade, still shots | 4.0 s, 0.60 s | dissolve, 4.00 s, 0.60 s |
| Crossfade, panning shot into zooming shot | 2.0 s, 0.50 s | dissolve, 2.00 s, 0.53 s |
| Slide (push) | 1.0 s, 0.50 s | push, 1.00 s, 0.53 s |
| Zoom-through (zoom to a flat colour, then fade) | 3.0 s, 0.60 s | zoom_in, 2.93 s, **0.33 s** (stops at the flat midpoint) |
| Camera windows | pan, slow zoom in (10%/s), still | 22 of 22 windows right |
| Text classes | demo UI, 4-word card, one-word end mark, card on a gradient with grain | 19 of 19 samples right, with Vision and with tesseract |
| Card measures | 4 words, 2 lines, 2.5 s, cap 11.0% | 4, 2, 2.5 s, 10.8% |

Transitions: precision 1.00, recall 1.00 (12 of 12, no extras). Synthetic clips are clean; real films are not.

**Composition** (`pipeline/tests/check_composition.py` draws frames with known answers and also runs `check_frames.py` end to end): a centred block on flat cream and on a gradient with film grain (coverage 8%, empty region 40%, box within 2 points), a block running off the bottom edge (bleed bottom only), two blocks (2 elements), an outlined panel (its flat inside is content), full-frame texture (coverage 100%, 4 edges), a phone outline running off the bottom with a screen the colour of the ground (the screen is content: 25%; version 1 measured 3%), a text card with known OCR boxes (text area, cap height, grid cell, one floating icon smaller than the line), and the rules on hand-made measures (a pill read as a card, a card with an icon, a five-line card, a sparse full-screen UI, a small window in a demo frame), and drawn stills measured the way `check_frames.py` measures them: a plain 4-line, 16-word card (read as a card and flagged), five short UI rows on white and on black (text, not objects, not a card: they pass), a labelled pill on a void (an object, flagged), a ragged paragraph (text), a lone object letterboxed and pillarboxed (bars cut, still flagged), a wide block and a full-height phone on flat ground (not padding), and `check_frames.py` run as an executable with `--roles`. 36 of 36 checks pass.

**Composition on storyboard stills** (the worked example's own history, lab corpus as the baseline): 9 of 26 round-2 concept frames flagged, against 5 of 129 frames of the approved v9 board; 28 of 300 random lab frames (9.3%) and 11 of 150 random Google frames (7.3%). By eye, 8 of the 9 round-2 lone-object frames are caught and 1 of 17 other round-2 frames is flagged (a four-line card); the v9 flags are the floating avatars the owner also caught and four composer close-ups. The full table and the misses are in `references/measuring.md` (Composition, Validation).

**Real films** (25 teasers and launch films, 10 accounts; 5 films checked frame by frame with `review_sheet.py` at 2–5 fps: a dark hardware loop, a split-screen talking head with UI, a live-action montage, a dark-UI app teaser and a fast type-and-product teaser):
- Boundaries: 51 right, 3 false, 6 missed, so precision about 0.94 and recall about 0.89. The false ones were a product rotating and a pull-back inside one shot. The misses were two UI pop-ups inside one half of a split screen, a title sliding out, a colour change between two similar live-action shots, a panel swap, and a swap between two type patterns.
- Not counted above: 12 one-word swaps on a still black card (small white words, a few percent of the frame) were not detected at all. Count word swaps from the text samples, not from transitions.
- Hard cuts: no false cuts seen. In one dark hardware film, ffmpeg scene detection at 0.3 found 0 of 5 cuts; `transitions.py` found all 5.
- Gradual types (strips of the top examples): 4 of 6 right (three scale-outs and a crossfade); one camera push-in on live action was called a zoom transition, one hand leaving the frame was called other.
- Before the "new picture" test (`is_new_picture`), a talking head produced 8 false "other" transitions in one film; after it, none.
- Text: the feature-word cards at the end of a teaser were found; UIs shown at hero scale on a dark background read as text_over rather than demo; captions over live action read as text_over or demo; a sparse UI under a talking head reads as demo or other.
- Camera: a slow push-in on a title and a pull-back from a product were labelled zoom_in and zoom_out correctly; handheld live action reads as inframe; true pans were rare in this corpus.

So: trust cut counts and cut rate; treat the gradual-transition types and the demo/text split as a first pass to confirm by eye.

## Known failure modes

- **Flat backgrounds hide camera moves.** With fewer than 3 textured 40 px blocks, a pan cannot be told from an object sliding; the window reads inframe.
- **Busy films.** Thresholds are relative to the local median, so in a film that never stops moving a soft transition can drown. The second pass (`find_hidden`) catches crossfades between moving shots, not everything.
- **Duration of eased tails.** A transition runs until the picture stops changing, at 1/15 s steps. An ease that creeps on, or a zoom-through with a flat middle, shifts the length.
- **Text-only changes.** Small words swapped in place on a still background change too few pixels to register as a transition.
- **OCR.** Thin or stylised display faces can be missed; `--fast` misses more. Vision sometimes reads shapes as text at confidence 0.3; lines below 0.4 are ignored, and rotated text is dropped from size measures.
- **Live action.** The pipeline is built for motion design and UI films. People and handheld footage make "other" and "inframe" noisy.
- **Composition.** A full-screen UI's own white or black surface reads as background (there is no outline inside the frame), so its coverage is low; the rules use floating objects and edge bleed, not coverage alone. A smooth subject that fills the frame (a soft close-up, a sky, a blurred photo) reads as background. A sliver of contact counts as bleed, and objects close together merge into one mass. The largest empty rectangle saturates near 30–40% around a centred object.

## Thresholds

All constants sit at the top of each script with a comment, and each script's docstring says how it decides:
- `transitions.py`: `CUT_MIN`, `CUT_RATIO`, `ACT_MIN`, `ACT_RATIO`, `SCENE_MIN`, `SCENE_SURE`, `HIST_MIN`, `NOVELTY`, `NOVELTY_SKIP`, `MAX_RUN`, `STILL_MAX`, `MODEL_FIT`, `BLEND_RES`, `TRIM`, `PUSH_MIN`, `HIDDEN_SPAN`, `HIDDEN_RATIO`;
- `motion_model.py`: `TEX`, `STATIC`, `BLOCK`, `SCALES`;
- `text_frames.py`: `MIN_CONF`, `MIN_LINE_H`, `EDGE_STEP`, `EDGE_PLAIN`, `DEMO_WORDS`, `DEMO_LINES`, `CARD_MAX_WORDS`, `CARD_MIN_H`, `HEADLINE`, `LOGO_TAIL`, `CAP_RATIO`;
- `composition.py`: `ANALYSIS_AREA`, `DETAIL_STEP`, `CLOSE_R`, `MIN_ELEMENT`, `BLEED_MIN`, `GROUND_MARGIN`, `CORNER`, `TEXT_SHARE`, `TEXT_FILL`, and for padding `PAD_MIN`, `PAD_MAX`, `PAD_TOL`, `PAD_FLAT`, `PAD_EDGE`, `PAD_SEEN`, `PAD_KEEP` (all in `SETTINGS`, which is composition.json's cache key: change one and `run_corpus.py` re-measures composition only);
- `check_frames.py`: `LIMITS` (each limit's corpus role, measure, percentile, margin and default), `MIN_SAMPLES`, `MIN_FILMS`, `TEXT_DOMINANT`.

If you change one, re-run `tests/check_clips.py` (and `tests/check_composition.py` for composition) and re-check two films with `review_sheet.py` before trusting the new numbers.

# Baselines

Corpus-level numbers to compare a new film against. Each line names where it comes from. "Findings" is `research/findings.md` and "teaser study" is `examples/kallo-launch-film/04-teaser.md`. Numbers marked "recomputed" were recalculated from the per-film logs for this library and agree with the findings.

These come from four AI-lab accounts (OpenAI, Claude, xAI, Manus) plus Google, posted between August 2024 and September 2026. They describe high-fidelity product films. A playful or cinematic film will sit elsewhere. Measure your own style's films (Step 4 of `SKILL.md`) before you treat any of these as a target.

## The corpus

| Item | Value | Source |
|---|---|---|
| Launch films downloaded | 125 (OpenAI 32, Claude 31, xAI 31, Manus 31) | `launch-films.csv`, corpus.md |
| Kept under "motion design only" | 85 (OpenAI 21, Claude 23, xAI 17, Manus 24) | `launch-films.csv` column `kept_motion_design` |
| Left out (people or live action) | 40 | same |
| Techniques recorded / cards after merging | 267 / 92 | corpus.md, technique-cards.md |
| Google films measured / watched | 38 / 8 | `google-films.csv` |
| Teasers downloaded | 25 (10 broken down frame by frame) | `teasers.csv` |

## Length

| Measure | Value | Source |
|---|---|---|
| Kept launch film, median | 30.0 s | recomputed, `launch-films.csv` |
| Kept films of 30 s or less | 45 of 85 | same |
| Kept films of 60 s or less | 75 of 85 | same |
| Median by account (kept) | Claude 52.2 s, OpenAI 30.0 s, Manus 28.5 s, xAI 19.2 s | same |
| Teaser, median of all 25 | 13.3 s | recomputed, `teasers.csv` |
| Short teasers (15 s or less) | 15 of 25, median 11.9 s | same |

## Where the seconds go

From the watched pass: 24 lab films (6 per account) logged second by second, every segment and transition.

| Measure | Value | Source |
|---|---|---|
| Product on screen (demo) | 67% of runtime, median | findings; recomputed 66.5% |
| Standalone text | 11%, median | findings; recomputed 11.4% |
| Text laid over the demo | 0%, median | findings |
| Logo | 7%, median | findings; recomputed 7.2% |
| A standalone text card | 2.6 s, 6 words on 2 lines (median of 77 cards; half hold 2.0–3.4 s) | findings |
| Headline-size type | about 3 words, 2.1 s on screen | findings (measured pass, 123 films) |
| A demo beat (time before a cut, a camera move or the app's next state) | 2.9 s, median | findings |
| Demo share by account | Claude 71%, OpenAI 71%, Manus 65%, xAI 59%, Google 58% | findings; recomputed |

## Cutting rate

| Measure | Value | Source |
|---|---|---|
| Designed transitions of every kind | 16.4 a minute (median per film; 298 in 18.7 min = 16.0 pooled) | findings; recomputed |
| Hard cuts a minute, by account (measured pass, includes flash cuts) | Claude 16.5, Manus 13.6, OpenAI 5.7, Google 3.7, xAI 1.9 | findings |
| Camera time (measured, 85 lab films) | still 54%, in-frame motion 23%, pan 6%, zoom in 4%, zoom out 4% | findings |
| Short teasers with 0–1 cuts | 8 of the 10 studied closely; 12 of the 15 at 15 s or less | teaser study; recomputed |

The two cut counts differ on purpose. The watched pass logs designed transitions. The measured pass counts every hard change in the picture at 4 fps.

## The 298 transitions

All logged in the 24 lab films of the watched pass. Recomputed from the logs; matches findings.

| Transition | Count | Share | Median length |
|---|---|---|---|
| Hard cut | 64 | 21% | instant |
| Camera move | 41 | 14% | 0.5 s |
| The app's own UI state change | 32 | 11% | 0.3 s |
| Push / slide | 32 | 11% | 0.4 s |
| Crossfade | 27 | 9% | 0.35 s |
| Scale-out | 26 | 9% | 0.4 s |
| Morph (shape A becomes B) | 23 | 8% | 0.7 s |
| Type-on / type-off | 19 | 6% | 0.7 s |
| Scale-into | 18 | 6% | 0.4 s |
| Match cut | 8 | 3% | 0.1 s |
| Mask reveal | 6 | 2% | 0.7 s |
| Wipe | 2 | 1% | 0.25 s |

Per-film counts and mixes are in `launch-films.csv` (columns `transitions_logged`, `transition_mix`) and `google-films.csv`. Eleven of the twelve exemplar moves in findings hold one element fixed while the rest changes.

## Teasers

| Measure | Value | Source |
|---|---|---|
| Short teasers run | 6–14 s | teaser study |
| Where the one line of text lands (Samsung series) | 62–79% into the clip, 3–4 words | teaser study |
| Where the name or logo lands | the last 1–4 s | teaser study |
| Most-viewed teaser | Notion Mail, 354K views on X: a 2.6 s UI glimpse, then the wordmark | teaser study, `teasers.csv` |
| Reveal ladder | 1 mystery, 2 metaphor, 3 partial, 4 glimpse + name, 5 demo | teaser study, `teasers.csv` column `reveal_ladder_rung` |

## Frame composition

Measured by `scripts/research/pipeline/composition.py` (version 3: letterbox and pillarbox bars cut off first) on every 2 fps sample, transitions left out, each film weighted equally within a role. From each corpus's `corpus.json` (`overall.composition.by_role`), 8 October 2026. Every number is a % of the frame, given as p10 / median / p90. Content coverage is everything that is not background; background is the smooth area that reaches a frame corner in the ground's colours (`references/measuring.md`, Composition). So a full-screen UI's own white or black surface counts as background, and a phone screen inside its bezel counts as content. Edge bleed is the share of samples with content running off at least one edge. Role is the sample's text class; lines and words are OCR lines on the frame. Padded films: lab 3 of 83 (two xAI films with black letterbox bars, 3% and 13% a side, and one OpenAI film with 3% bars), Google 0 of 27, teasers 0 of 25. Cutting the bars moved the lab demo numbers a little: coverage p25 25.6 to 25.2% and median 49.5 to 47.7%, subject height p10 31.1 to 28.9%, subject width p10 48.1 to 46.2%. The Google and teaser numbers did not change.

Lab launch films (83 films, 5,295 samples; 3 padded):

| Role | Samples (films) | Content coverage | Edge bleed | Subject area | Subject height | Cap height | Lines | Words |
|---|---|---|---|---|---|---|---|---|
| demo | 2,411 (68) | 15.3 / 47.7 / 93.0 | 74% | 10.0 / 47.1 / 92.8 | 28.9 / 90.0 / 100 | 1.88 / 3.13 / 5.27 | 4 / 12 / 47 | 13 / 42 / 158 |
| text over picture | 924 (66) | 19.6 / 55.2 / 93.1 | 82% | 10.9 / 50.5 / 93.0 | 34.4 / 93.3 / 100 | 3.54 / 5.29 / 9.38 | 2 / 13 / 42 | 4 / 38 / 129 |
| text card | 1,145 (63) | 2.8 / 6.5 / 23.8 | 21% | 2.5 / 5.6 / 22.9 | 8.9 / 17.5 / 73.3 | 4.37 / 6.88 / 12.08 | 1 / 1 / 3 | 2 / 4 / 9 |
| logo | 375 (66) | 0.7 / 2.4 / 5.1 | 10% | 0.7 / 2.3 / 4.7 | 11.1 / 14.4 / 25.6 | 4.58 / 7.36 / 10.51 | 0 / 1 / 1 | 0 / 2 / 2 |
| other | 440 (64) | 0.1 / 3.5 / 59.8 | 31% | 0.0 / 2.5 / 56.6 | 0 / 21.5 / 100 | 1.25 / 2.08 / 2.71 | 0 / 0 / 1 | 0 / 0 / 3 |

Google launch films (27 films, 1,620 samples; 5 logo samples, too few to report):

| Role | Samples (films) | Content coverage | Edge bleed | Subject area | Subject height | Cap height | Lines | Words |
|---|---|---|---|---|---|---|---|---|
| demo | 959 (23) | 15.7 / 48.1 / 85.5 | 65% | 12.6 / 45.9 / 85.5 | 38.8 / 83.3 / 100 | 2.02 / 3.50 / 6.13 | 4 / 8 / 21 | 12 / 34 / 106 |
| text over picture | 215 (20) | 16.3 / 43.7 / 96.0 | 68% | 14.8 / 43.0 / 96.0 | 34.4 / 83.3 / 100 | 3.37 / 5.49 / 11.25 | 1 / 5 / 21 | 3 / 22 / 72 |
| text card | 287 (14) | 3.0 / 9.2 / 26.1 | 33% | 2.9 / 8.3 / 21.5 | 10.0 / 19.4 / 80.8 | 4.10 / 6.14 / 10.21 | 1 / 2 / 3 | 3 / 4 / 9 |
| other | 154 (13) | 0.0 / 16.8 / 65.2 | 39% | 0.0 / 15.9 / 65.2 | 0 / 66.7 / 100 | 1.25 / 1.67 / 2.40 | 0 / 1 / 4 | 0 / 1 / 9 |

Teasers (25 films, 10 accounts, 1,517 samples):

| Role | Samples (films) | Content coverage | Edge bleed | Subject area | Subject height | Cap height | Lines | Words |
|---|---|---|---|---|---|---|---|---|
| demo | 344 (11) | 19.8 / 75.0 / 96.6 | 87% | 9.1 / 74.9 / 96.4 | 36.9 / 89.4 / 100 | 1.40 / 1.99 / 4.33 | 4 / 6 / 42 | 9 / 16 / 132 |
| text over picture | 130 (18) | 20.5 / 56.5 / 92.3 | 70% | 20.5 / 53.4 / 92.2 | 36.9 / 76.9 / 100 | 3.13 / 3.92 / 11.87 | 1 / 2 / 4 | 1 / 4 / 10 |
| text card | 100 (13) | 2.3 / 11.0 / 30.0 | 19% | 1.5 / 9.4 / 29.4 | 6.8 / 22.3 / 58.8 | 3.36 / 5.88 / 17.29 | 1 / 2 / 3 | 2 / 3 / 5 |
| logo | 41 (15) | 1.0 / 2.9 / 4.1 | 7% | 1.0 / 2.9 / 4.1 | 5.6 / 5.6 / 17.8 | 3.41 / 3.41 / 11.25 | 0 / 1 / 1 | 0 / 1 / 2 |
| other | 902 (24) | 4.4 / 47.6 / 94.4 | 72% | 3.4 / 47.1 / 94.3 | 19.4 / 75.6 / 100 | 0.81 / 1.88 / 2.82 | 0 / 0 / 2 | 0 / 0 / 6 |

Demo coverage p25: lab 25.2%, Google 33.2%, teasers 36.8%. Demo subject width p10: lab 46.2%, Google 45.6%, teasers 63.3%. With the lab table, `check_frames.py` flags a lone object below 25.2% content, a demo subject (not text) under 23.1% tall and 37.0% wide, and a card under 3.93% cap, over 3 lines or over 13.5 words.

## Posting

Measured posting-time findings are in `posting.md`. In short: on TikTok only 06:00–09:00 local time beat the noise (1.21x engagement, 95% CI 1.03–1.58); on X no time band was reliably better; no weekday effect cleared the noise on any platform measured.

## Caveats

- Five accounts, one sector (AI tools), one period (August 2024 to September 2026).
- Views were read on 30 September 2026 (X) and 7 October 2026 (YouTube) and keep changing.
- The measured pass's per-film records were mostly lost; only 11 lab films keep a per-film `measured_cuts_per_min` in `launch-films.csv`. The account medians above were computed before the loss.

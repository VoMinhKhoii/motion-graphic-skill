# SFX catalogue

The 29 sound effects used in the worked example's launch film and teaser. The files are not in this repo: their
licences allow use in a film but not redistribution as standalone files. Fetch them yourself (`fetch_sfx.md`)
into a local `lib/sfx/` folder under the file names below; `sfx_mix.py` cue sheets refer to these names.

Licences, read at download time (check them again before you publish):
- **Mixkit Sound Effects Free License**: commercial use, including broadcast, no attribution. No redistribution
  of the files as such.
- **Pixabay Content License**: free, no attribution, may be modified. No selling or redistributing the files
  on their own.

Durations: file length / audible part. "Mixkit asset" means `https://assets.mixkit.co/active_storage/sfx/<id>/<id>.wav`
(all 15 ids answered HTTP 200/206 on 2026-10-07). Pixabay pages are `https://pixabay.com/sound-effects/<slug>/`;
the number at the end of the slug is the sound id.

## Taps and clicks

| File | Dur (s) | Source | Used for |
|---|---|---|---|
| `click_ui_3_modern_click_box_check.wav` | 0.24 / 0.08 | Mixkit asset 1120 (category: click) | Every phone tap: Log, Send, Save. The default tap, -6 to -10 dB. |
| `click_ui_1_tap_notification.mp3` | 0.16 / 0.05 | Pixabay `film-special-effects-tap-notification-180637` | Light ticks: a gauge filling (4 ticks 0.14 s apart), words lighting up in sequence, at -16 to -24 dB. |
| `click_ui_2_soft_ui_click.mp3` | 1.04 / 0.21 | Pixabay `film-special-effects-soft-ui-click-147352` | A softer spare tap. Not used in the final cut. |
| `click_mouse_1_mouse_click_close.wav` | 1.38 / 0.15 | Mixkit asset 1113 (category: click) | Web clicks (Send, Save meal) when the pointer is on a desktop page. |
| `click_mouse_2_clear_mouse_clicks.wav` | 1.05 / 0.22 | Mixkit asset 2997 (category: click) | A camera-shutter-like click: the label photo being taken. |

## Pops

| File | Dur (s) | Source | Used for |
|---|---|---|---|
| `pop_2_clean_minimal_pop.mp3` | 1.63 / 0.12 | Pixabay `clean-minimal-pop-467466` | Right after a Send tap (+0.03 s); feed posts dropping in one by one. |
| `pop_1_pop.mp3` | 1.97 / 0.08 | Pixabay `film-special-effects-pop-423717` | A card closing on its total; avatars appearing in a row (0.07 s apart, panned left to right); an end-card accent. |
| `pop_3_dry_pop_up.wav` | 0.30 / 0.20 | Mixkit asset 2356 (category: pop) | Result rows landing, at -15 to -17 dB, alternating pan ±0.15; a burst of tiles (9 pops 0.09 s apart). |

## Whooshes and swipes

| File | Dur (s) | Source | Used for |
|---|---|---|---|
| `whoosh_short_1_fast_whoosh.wav` | 1.76 / 0.53 | Mixkit asset 1490 (category: whoosh) | Small camera moves and scrolls, quiet (-16 to -21 dB). |
| `whoosh_short_2_fast_sweep.wav` | 1.00 / 0.46 | Mixkit asset 174 (category: swoosh) | A text line leaving; two cards parting. Bright. |
| `whoosh_short_3_swoosh_015.mp3` | 1.06 / 0.45 | Pixabay `film-special-effects-swoosh-015-383769` | A text screen arriving; a page pushing in. Warm. |
| `whoosh_long_1_air_woosh.wav` | 2.32 / 1.03 | Mixkit asset 1489 (category: whoosh) | A big camera pull-out; the fade into the end card. Deep. |
| `whoosh_long_2_cinematic_swoosh.wav` | 2.04 / 1.42 | Mixkit asset 1481 (category: swoosh) | The phone morphing into the browser; the wordmark travelling to centre. |
| `swipe_1_movement_swipe_whoosh.mp3` | 1.04 / 0.17 | Pixabay `film-special-effects-movement-swipe-whoosh-3-186577` | A phone brought up to an object (the scanner shots). |
| `swipe_2_quick_swipe.mp3` | 1.03 / 0.26 | Pixabay `film-special-effects-quick-swipe-405450` | Tab switches, a drag, a scroll; the first move of a demo. |

## Typing beds

Place these with `"trim": false`, an `offset` into the file and a `dur` equal to the on-screen typing time.

| File | Dur (s) | Source | Used for |
|---|---|---|---|
| `keyboard_1_smartphone_typing.wav` | 4.50 / 3.89 | Mixkit asset 1393 (category: type) | Phone typing; offset 0.3, -13 dB. |
| `keyboard_2_laptop_keyboard.wav` | 9.28 / 8.90 | Mixkit asset 2536 (category: keyboard) | Web typing and type-on titles; offset 0.6, -15 to -16 dB. |

## Confirmations

| File | Dur (s) | Source | Used for |
|---|---|---|---|
| `notify_1_soft_notification.mp3` | 1.41 / 0.38 | Pixabay `film-special-effects-soft-notification-146623` | Every "saved" moment, 0.1-0.15 s after the Save tap. |
| `notify_2_success_software_tone.wav` | 1.62 / 0.68 | Mixkit asset 2865 (category: notification) | A bigger success: a comparison resolving, a share sent. |
| `heart_like_2_click_melodic_tone.wav` | 0.46 / 0.26 | Mixkit asset 1129 | A "found it" moment (a barcode match) and a like. Melodic. |
| `heart_like_1_happy_pop.mp3` | 1.03 / 0.03 | Pixabay `film-special-effects-happy-pop-2-185287` | A spare like sound. Not used in the final cut. |

## Impacts

| File | Dur (s) | Source | Used for |
|---|---|---|---|
| `impact_1_sub_drop_short.mp3` | 3.32 / 2.79 | Pixabay `film-special-effects-sub-drop-short-232033` | Under the title's first beat (the name landing). Drop it when music carries the moment. |
| `impact_2_sub_bass_boom.mp3` | 3.76 / 2.55 | Pixabay `musical-sub-bass-boom-1-302682` | The wordmark landing on the end card, at -7 dB. |
| `impact_3_futuristic_bass_hit.wav` | 2.75 / 0.79 | Mixkit asset 2303 (category: bass) | A brand-belief line landing; the share's confetti. |

## Risers and glitches (downloaded, not used in the final cuts)

| File | Dur (s) | Source | Meant for |
|---|---|---|---|
| `riser_1_riser_3.mp3` | 2.32 / 2.16 | Pixabay `film-special-effects-riser-3-130954` | A build into a reveal; peaks at its end. |
| `riser_2_sharp_riser.mp3` | 1.88 / 1.85 | Pixabay `film-special-effects-sharp-riser-327342` | A brighter build. |
| `riser_3_cinematic_trailer_riser.wav` | 2.57 / 1.63 | Mixkit asset 790 (category: cinematic) | A trailer-style build; can feel too dramatic for a product film. |
| `glitch_or_stutter_1_glitch_fx_7.mp3` | 0.91 / 0.56 | Pixabay `film-special-effects-glitch-fx-transitions-7-373373` | A "wrong answer" or before/after contrast. |
| `glitch_or_stutter_2_digital_glitch_break.wav` | 1.07 / 0.57 | Mixkit asset 2951 (category: glitch) | Same, harsher. |

## Levels that worked

SFX sit between -6 dB (a key tap) and -24 dB (background ticks). Under music at -6 dB, taps at -6 to -8 dB still
read. Final mix: peak-normalised to -1 dBFS for a short social clip. Every sound is onset-trimmed so its attack
lands on the frame of the event; a 4 ms pre-roll keeps the attack intact.

# The real cue sheets

The worked example's sound, as `sfx_mix.py` cue sheets: every sound effect in the final film and the two teasers, with its time, gain, pan and a note on what happens on screen at that moment. No audio is included. The sound names are the catalogue names in `skills/motion-graphic/scripts/sound/sfx_catalog.md`; fetch the files yourself (`fetch_sfx.md`).

| File | What | Length | Events | Levels |
|---|---|---|---|---|
| `film_v9d_cues.json` | the final film, v9d | 83.1 s | 141 | loudness I −16 LUFS, TP −1.5 dBTP, LRA 11 |
| `teaser_en_cues.json` | the English teaser | 12.4 s | 13 | peak −1 dBFS |
| `teaser_vi_cues.json` | the Vietnamese teaser | 10.6 s | 12 | peak −1 dBFS |

They were ported event for event from the production mix scripts. Mixed with the same sound files and tracks, they reproduce the production mixes: normalised correlation 0.9999 for the film (against its mix before loudness normalisation) and 1.0 for both teasers.

## How to read them

```bash
python3 $SKILL/scripts/sound/sfx_mix.py film_v9d_cues.json --check                       # structure, missing files
python3 $SKILL/scripts/sound/sfx_mix.py film_v9d_cues.json --sfx-dir lib/sfx --no-music   # SFX only
```

- **Scene-local times.** In the film sheet each event names a `scene` and a `t` inside it; `scenes` holds every scene's start. Film time = `scenes[scene] + t`. A scene's times are copied from that scene's code (its pointer taps, its row landings), so retiming one scene means changing one start, not every event after it. The teasers are one scene each, so their times are film times.
- **Layering.** A product event is usually two sounds a few frames apart: a tap on the press, then the app's answer 0.03 to 0.15 s later (Send: tap, then a pop at +0.03 s; Save: tap, then the "saved" chime at +0.15 s). Camera moves get their own quiet whoosh under them, at −15 to −21 dB, so the taps stay on top.
- **Rows that land.** One pop per row, never one for the list. In the web scene the three rows land at 6.17, 7.62 and 8.97 s, each 1 dB louder (−17, −16, −15) and panned a little further right (0, 0.1, 0.2), then a different, louder pop when the card closes on its total (−12 dB at 9.05).
- **The gauge ticks rising.** Numbers that fill get light ticks: four `click_ui_1` ticks 0.14 s apart from web 10.7 s, at −22, −21, −20, −19 dB. The comparison's five lit words use the same pattern (−21 to −17).
- **Friend additions.** In the circle scene six avatar pops appear 0.07 s apart, panned from −0.4 to 0.4, then each friend docks with its own pop on its arrival time (1.15, 1.3, 1.55, 1.8, 2.05, 2.3 s, the same numbers as the animation), panned −0.3 to 0.3. In the share scene each friend added to the split is a tap plus a pop 0.05 s later, 0.65 s apart.
- **Staggered tiles.** The micronutrient burst is one long whoosh at 1.0 s, then nine pops 0.09 s apart from 1.08 s (one pop per two tiles: seventeen would blur), gains cycling −17, −16, −15 and pans sweeping −0.4 to 0.4, then a long whoosh at 2.8 s as the tiles fly home.
- **Typing beds** have `"trim": false`, an `offset` into the file and a `dur` equal to the on-screen typing time, with an 80 ms fade.
- **Music.** The film's track (the owner's pick) starts at film 0, so its 0.62 s downbeat lands on the product name at 0.62 s, on the same frame as the sub drop; it fades in over 0.2 s and out over the last 2.2 s with a curved fade (`music_fade_power` 1.5) so the end card holds in near-silence. The teaser's track is offset so its hit at 79.4 s lands on the wordmark, 0.38 s into the fade to black. Bring your own tracks: set `music` and `music_hit_at` to your track's hit.
- **Levels.** The film is loudness-normalised (it is long enough for an integrated target to mean something); the teasers are only peak-normalised. The production film used one-pass ffmpeg `loudnorm`; `sfx_mix.py` uses two passes, which lands closer to the target. See [05-sound.md](../05-sound.md) for the measured results.

These are one film's choices, made for its pictures. Use them to see how a finished mix lays sound against animation; time your own sheet from your own film's code.

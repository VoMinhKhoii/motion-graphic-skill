# Sound: SFX on every event, music the owner picks, hits on picture

Sound is half of "premium". In the worked example the owner liked the SFX from the first version, rejected the first music bed, picked the film's track from a shortlist, and supplied the teaser's track. Plan for that.

## SFX vocabulary

One sound per visible event, quiet enough to feel and loud enough to read on a phone speaker. Starting levels, as gain on each clip before the master normalise:

| Event | Sound family | Gain |
|---|---|---|
| Tap on a control | Short UI click | −6 to −10 dB |
| Typing | Phone keyboard bed, trimmed to the typing span | −13 dB |
| Send / submit | Click plus a short fast whoosh | −7 dB / −14 dB |
| A page push or morph | Short whoosh or swoosh | −14 to −18 dB |
| A row or card landing | Clean minimal pop, alternate slight left and right pan | −13 dB, −1 dB per extra row |
| A total settling | Dry pop | −12 dB |
| Scroll / swipe | Quick swipe | −18 dB |
| Saved / success | Soft notification plus a quiet success tone 0.35 s later | −9 dB / −16 dB |
| Fade to black | Long air whoosh | −18 dB |
| The name / wordmark | Sub drop or the music's hit, never both | −9 dB |
| Confetti / celebration | Happy pop | −10 dB |

Trim each SFX to its onset so the hit lands on its frame. `scripts/sound/sfx_mix.py` does it (onset = first sample above 8% of peak, minus 4 ms).

Sources: royalty-free libraries with commercial licences (Mixkit, Pixabay, or a paid library). Keep the files local; their licences usually forbid redistributing them as files. `scripts/sound/sfx_catalog.md` lists the 29 sounds used in the worked example by name and role.

To see how a finished mix lays these against animation, read the worked example's real cue sheets in `examples/kallo-launch-film/sound/` (the 83 s film, 141 events, and both teasers), with notes on each event: rows that step 1 dB and pan per row, gauge ticks that rise, friends docking on their arrival times, a staggered tile burst. Mixed with the same files they match the production mixes (correlation 0.9999 to 1.0). They are one film's choices: time your own sheet from your own film's code.

## Music

1. **Ask first.** Does the owner have a licence (Epidemic Sound, Artlist), or a track in mind?
2. **Otherwise shortlist 10–12 tracks** with links they can click and play. Note style, measured BPM, length, licence and a one-line character note. Cover 4–5 styles; for product films, 100–130 BPM, no lead vocals.
3. **The owner picks.** Taste in music is personal; the worked example's first bed (EDM with brass) was rejected even though the SFX were liked.
4. **Download it reliably.** Pixabay sits behind Cloudflare; a real browser session works where curl doesn't. Check the downloaded filename contains the sound id, because search pages list related sounds first.

## Syncing music to picture

Find the track's structure before cutting: loud sections, drops, hits.
```python
# loudness every 0.5 s and the strong rises (onsets)
db = 20*log10(rms(window)); onsets = where(diff(db) > 9 dB and level > -30 dB)
```
Then place the track so its structure serves the story:
- **The drop (near-silence) lands on the key action.** In the teaser it fell on the Save tap, so the gauge filled in suspense.
- **The hit lands on the name.** Offset the track so `track_time(hit) = film_time(wordmark)`: offset = 79.4 − (fade + 0.38) in the worked teaser.
- Fade in over 0.25 s and out over 0.5 s with the picture.
- Music at about −6 dB under the SFX for a trailer-style track; −15 dB for a light bed under a busy demo.

`scripts/sound/sfx_mix.py` takes a cue sheet with `music_hit_at` and `hit_lands_at` and does the offset.

## Silence

- Near-silence before the first result makes the result land.
- A drop-out before the name and silence on the name are the commonest endings in the lab films. Use one of them; don't stack a sub drop on a music hit.
- Teasers can go SFX-only; it reads more raw and honest. Offer both.

## Mixing and checking

Peak level alone is not enough. A sparse mix of short clicks can touch −1 dB and still sound quiet next to the films around it, and a sample peak of −1 dB can hide an inter-sample (true) peak above 0 dB that clips after encoding. Set and check two numbers: integrated loudness (LUFS, the average over the whole film) and true peak (dBTP).

- **Films (30 s and longer):** −16 LUFS integrated, −1.5 dBTP true peak, LRA 11. Put `"loudness": {"I": -16, "TP": -1.5, "LRA": 11}` in the cue sheet and `sfx_mix.py` runs a two-pass ffmpeg `loudnorm` (measure, then apply with the measured values). The worked film used these targets (with a one-pass `loudnorm`) and measured −15.3 LUFS, −1.5 dBFS on the delivered file. Social platforms normalise loudness on playback anyway (YouTube turns loud uploads down to about −14 LUFS); a film mastered near −16 to −14 neither gets turned down hard nor sounds weak.
- **Teasers and short feed clips (under about 15 s):** leave `loudness` out and peak-normalise to −1 dBFS (`"peak_db": -1`). An integrated target means little over 10 s. The worked teasers measured −12.9 and −13.4 LUFS this way.
- `sfx_mix.py` prints the mix's integrated loudness and true peak after writing it.
- **Measure again on the delivered MP4**, after AAC encoding: `ffmpeg -i out/film/name.mp4 -af ebur128=peak=true -f null -` and read `I:` and `Peak:` in the summary. AAC can move the true peak; if it goes above −1 dBTP, lower `TP` and re-mix.
- Print loudness every 0.5 s of the final mix and confirm the drop and the hit sit where the picture needs them.
- The picture sets the length: `render/master.sh` pads a short mix with silence, warns when the mix is longer than the picture, and fails if a delivered file is more than one frame off. Re-run `sfx_mix.py` with the film's current `duration` whenever scenes change length.
- Mux new audio without re-rendering the picture (`ffmpeg -map 0:v -map 1:a -c:v copy`) when only the sound changes.

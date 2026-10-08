# Sound

No voiceover was a rule from the brief. The soundtrack is licensed sound effects on every product event, plus a music bed the owner picked. This file covers the effects vocabulary, where each sound goes, the music decisions (including the rejected ones) and the final mix.

No audio files are included in this example. The effects and music are under the Mixkit and Pixabay licences, which allow use in a video but not redistribution as standalone files. The skill ships a catalogue and a downloader instead.

## The effects vocabulary

About 20 sounds, all from Mixkit (Sound Effects Free License) and Pixabay (Content License). Neither licence requires attribution in the video.

| Family | Sounds | Used for |
|---|---|---|
| Taps | a modern UI click; a lighter notification tick | every finger tap on the phone; fine ticks for small events |
| Clicks | two mouse clicks | every click on the web |
| Keys | smartphone typing; laptop keyboard | under typing, phone or web |
| Short whooshes | a fast whoosh, a fast sweep, a short swoosh | morphs, text lines entering, the camera's key moves |
| Long whooshes | an air whoosh, a cinematic swoosh | big transitions: phone to browser, the tile burst, the end card |
| Swipes | a quick swipe, a movement swipe | scrolls, drags, the scanner opening |
| Pops | a clean minimal pop, a plain pop, a dry pop | rows landing, a card closing, posts dropping in, tiles |
| Chimes | a soft notification, a success tone | a meal saved; a successful share |
| Like | a melodic click tone | a like in Circle; a barcode found |
| Impacts | a short sub drop, a futuristic bass hit, a sub bass boom | the name at the start, the end wordmark, the belief line's last word, the Share tap |

## Placement rules

The rule underneath all of them: **a sound is caused by something on screen.** Nothing plays for atmosphere. This is the reference films' own rule ("the product is the soundtrack", card S2) and it is what makes the effects read as the app rather than as decoration.

1. **Trim to the onset.** Each effect starts at the first sample above 8% of its peak, with a 4 ms pre-roll, so the transient lands on the frame of the event and not a few milliseconds later.
2. **Taps on every tap**, at about −8 dB (Save and Send slightly louder, −6 to −7 dB). The finger's press on screen and the tap sound share a frame.
3. **Keys under every typed line, for exactly as long as the typing.** Phone keys at −13 dB, laptop keys at −15 dB, with a 0.08 s fade-out so the bed does not click off. The first 0.3 s (phone) or 0.6 s (laptop) of the recording is skipped, because those files start with a pause.
4. **A whoosh on every morph.** Short whooshes at −13 to −18 dB for component morphs and text entering; long whooshes at −10 to −13 dB for the two or three biggest transitions. A whoosh is never placed on a plain cut.
5. **One pop per row.** When the result rows land, each gets its own pop, at −17 dB, stepping 1 dB per row, panned slightly left and right in turn (±0.1 to ±0.15), so a list of four rows sounds like four arrivals and not one blur. The card closing on its total gets a slightly louder, different pop.
6. **A chime on save.** The soft notification at −9 to −12 dB on "Meal saved", then the success tone 0.35 s later and quieter (−16 dB) as the gauge fills.
7. **Ticks for numbers that fill.** As the day's gauge rises, 4–5 light ticks 0.14 s apart, each 1 dB louder than the last.
8. **Hits on the name, and only there.** A short sub drop as "Kallo" lands at 0.62 s. A sub bass boom on the end wordmark. A bass hit on the last word of the belief line and on the Share tap (the one celebratory moment). Nowhere else.
9. **Groups spread in time and space.** Circle posts dropping in: six pops 0.07 s apart, panned from −0.4 to +0.4. Nutrient tiles bursting: nine pops 0.09 s apart, gains cycling over 3 dB.

The placement is a script that reads the scene table of the edit, so when a scene is retimed the sounds move with it. Every effect is given in scene-local time (`at('label', 1.85)`), never as an absolute time in the film.

## Music

### The journey

1. **v1 to v6: effects only.** The concept board offered "designed sound effects" or "a music bed under the effects"; effects were picked.
2. **v7: an EDM bed, rejected.** The owner asked for the energy of a reference app intro (about 126 BPM, electronic, loud, whooshes and clicks on the cuts). The film got Mixkit "Forbidden" (125 BPM, EDM with brass), placed so its drop landed on the wordmark at 1.0 s, with the beat grid every 0.479 s after it. The owner:
   > I like the sound effect, but not the music, can I have the music link to pick?
3. **A shortlist, not a choice.** A shortlist of 10–12 royalty-free tracks went to the owner as clickable page links: 100–130 BPM, at least 60 s or loopable, no lead vocals, licences that allow commercial use without attribution. The style brief was "tasteful (an Apple, Linear or Arc launch feel), not festival EDM, not cheesy corporate". The BPM of each was measured by onset autocorrelation, not taken from the page.
4. **A pick that could not be downloaded.** The owner first chose a track on Epidemic Sound. Downloading it needed a paid plan or a trial, and starting either is the owner's decision, not the agent's. v8 and v9 shipped with effects only while this was open.
5. **The final track.** The owner then picked Pixabay "Your Pulse" (Pixabay Content License) and downloaded it themselves, because Pixabay's bot protection blocks automated downloads.

**Lesson:** taste in music is the owner's call. Offer a shortlist with links that play in a browser, measured, licence-checked, and let them pick. Do not put an unrequested track under a film that is being reviewed for picture; it pulls the review toward the music.

### Placing the film's track

- The track is offset so a chosen downbeat lands on the "Kallo" wordmark at 0.62 s, the same frame as the sub drop.
- It sits at −6 dB under the effects.
- It fades in over 0.2 s and out over the last 2.2 s, with a curved (power 1.5) fade so the end card holds in near-silence.

### The teaser's track

The teaser used Pixabay "Trailer Suspense" (#415585), supplied by the owner. It has loud pulses until 76.5 s, a drop to near-silence, and a hit at 79.4 s. The track is offset so the hit lands on the wordmark (0.38 s into the fade to black), which puts the drop 0.27 s before the Save tap: the save and the gauge fill play in suspense, and the hit brings the name. Music at −6 dB, a 0.25 s fade in and a 0.5 s fade out. Full timing in [04-teaser.md](04-teaser.md).

## The mix

Both mixes are built in numpy at 48 kHz stereo, then encoded to AAC at 256 kb/s in the final MP4.

| | Film (83.1 s) | Teaser (12.4 s / 10.6 s) |
|---|---|---|
| Method | sum; peak-normalise to 0.95; then ffmpeg `loudnorm=I=-16:TP=-1.5:LRA=11` | sum; peak-normalise to 0.89 (about −1 dB) |
| Measured on the delivered file | −15.3 LUFS integrated, −1.5 dBFS peak | English −12.9 LUFS, Vietnamese −13.4 LUFS; −1.0 dBFS peak |

Why two methods: the film is long enough for an integrated loudness target to mean something, and −16 LUFS with −1.5 dB true peak is safe on every platform it went to. The teaser is a 10–12 s feed clip that plays between louder videos, so it is simply brought up to about −1 dB peak. The concept board's original target was −14 LUFS; the measured result is close to it for the teaser and 1.3 LU quieter for the film.

Measure the delivered file, not the mix you think you made: `ffmpeg -i film.mp4 -af ebur128=peak=true -f null -`.

# Motion craft: camera, pointer, typing, text, transitions

These are the craft decisions that separated "a screen recording with effects" from "a motion team's film" in the worked example. Each has a number you can start from. They are defaults for one calm, high-fidelity product film (see "Defaults from the worked example" in `SKILL.md`): re-tune them to the taste you researched and the approved brief. Product truth does not change: real UI, real numbers, no jank. Character and presenter films add their own timing (`branches.md`).

## Camera

- **Move, then hold.**
  - Moves are critically damped springs: no overshoot, settle in about 0.4–0.6 s.
  - Holds run 1–4 s.
  - Keep the camera still about half the time.
  - The engine's `camAt(keys, s, omega)` with omega 7.5–9 gives that feel.
- **Framing a phone demo:**
  - Show about two-thirds of the phone (scale k ≈ 0.6–0.68 of a 3000 px tall device at 1350 px frame height), "not just 1/2".
  - Keep the phone's side edges in frame.
  - The whole phone only for a beat; it is too small to read.
  - Anchor filler frames at the phone's top with no void below.
- **Framing a browser or desktop product:** no phone. Crop to the panel the story is about, keep one window edge in frame so it reads as an app, and let the camera ride the cursor. The engine's `browser` preset draws the window.
- **Store previews:** no device, no camera zoom; the frame is the app's own screen (`branches.md`).
- **Zoom on the click that matters:**
  - Punch in tight (k 0.8–1.2) on the control the story is about (Save, Share, the split bar), then back out.
  - Don't ping-pong on every tap. One busy version had 14 camera keys in 9 s and was "moving around too much".
- **Ride the pointer:**
  - On long moves (a drag, typing) the camera follows the pointer or the caret, keeping it just right of centre.
  - It lands tight on the control before the press.
  - For a typed line, frame the text very close (about 2.7–3.2×) and track the caret, with a swing back on line wraps.
- **Never chase.** Several big position changes in a row make the eye hunt. Keep the subject at the centre and move the world around it.

## Pointer

- A pointing hand, not a disc. Its fingertip is the hotspot.
- It glides between targets (about 0.36–0.42 s travel), dips on press (scale 0.9, a small down shift) and leaves a ripple ring at the fingertip.
- A tap lands on the frame where the app reacts (button highlight, sheet rising). Read that frame off the recording; never trust the action log's wall time.
- Move the pointer out of the way after a tap if it would cover what happens next, for example typed text.
- Show it on the web and on the phone alike. Hide it on pure text cards.

## Typing

- Letter by letter. Sped-up recordings stay letter-level as long as about one new letter lands per output frame. At 60 fps that is roughly 50–60 characters per second of film, so a 190-character sentence fits in about 3 s.
- Fresh letters may land in an accent colour and settle to ink (a type-on card), but in the product's own input, leave the product's styling alone.
- Default from the worked example: the status line after Send shows at most two words ("Connecting…", "Calculating…"). Cut past the rest, in every run shown. If the brief wants to show real speed, keep the wait honest instead and show a clock.

## Text cards

- 1–2 lines, about 3–6 words, held about 2 s. In the worked run each line came down to half its earlier hold.
- Alone on a calm ground (a moving gradient in the brand's colours), with no avatars or floating components beside it.
- Vary the treatment from line to line:
  - typed;
  - word by word with one accent word;
  - inline UI chips inside the sentence;
  - text above the live demo;
  - giant type;
  - text over a photo with a soft veil behind it.
- The result before the claim: show the outcome, then the line about it, then go back to it.
- No accent on plain words. Accent the one word that carries the idea.
- Check contrast on photo backgrounds. A line that is "invisible with the background" needs a veil.

## Transitions

From the measured mix: most designed transitions run 0.3–0.7 s, and about a fifth of changes are hard cuts.
- **Let the app animate itself:** sheets rising, rows landing, a gauge filling, confetti. These are the best transitions because they are true.
- **Component morphs:**
  - the input box flies into its place in the phone;
  - a result card lifts out of the phone, moves aside, and a second card surfaces beside it for a comparison;
  - tiles fly back into their screen;
  - the phone's screen widens into a browser window.
- **Keep one thing fixed** through every designed transition: the element the eye was on.
- **Cut-outs:** lift one component out of the recording (the composer, a card) and show it alone at hero scale.
  - Cut just inside the app's own border.
  - Measure its real corner radius.
  - Draw one clean border at that radius. A mismatched radius plus a doubled border reads as "the edge is off".
- **Bridges over stalls:** where a recording freezes and then pops (debug builds do this on save), cut the stall and dissolve the last good frame away over about 0.3 s while the camera moves.

## Composition

- Full frames. Backgrounds fill the frame:
  - a blurred photo of a place that fits the moment (a kitchen at dawn, a desk at noon, a dinner table);
  - or the brand gradient.
- A world that changes through the film carries a story without words. In the worked example the light changed from dawn to night across the day of meals, with a hand-drawn clock top-left: the `SceneClock` recipe (`engine.md`, Recipes), with each scene's time range and the film's timing.
- Show real things for real features: a real product's photo for barcode scanning, a real label for label reading. Openly licensed photos need a credit; better, shoot your own.
- Reveal incrementally: feed posts drop in one by one; never a static screen that must be read.
- After a full reveal (a wall of tiles), hold about a second before uniting it back.

## Pace

- Fast but readable: something changes every 2–3 s.
- If a section drags, cut holds and speed up waits; never speed up the hero interaction past legibility.
- "Don't worry about duration" early on: build long, then trim. The worked film ended at 83 s; the teaser at 10.6–12.4 s.

# Production branches and platform routes

Pick the branch right after the taste interview (Step 1). The branch decides what you research, what a concept must contain, how you capture and how you mix. Record it in `film/STATUS.md`. The worked example ran branch (a); the others are written from general production practice and are starting points, not measured results. Measure your own references before you trust any number here.

| Branch | Pick when | What changes from the main runbook |
|---|---|---|
| (a) Motion design / product film | Real UI is the hero; no people; music and SFX | Nothing: the runbook as written |
| (b) Character-led / playful | A mascot or brand primitives act; humour, bounce | A cast, character timing, comedic beats; research starts mostly fresh |
| (c) Presenter / founder / UGC | Someone speaks to camera | A script, a shot list, captions, a dialogue-first mix; UI becomes b-roll |
| (d) Hybrid | Two of the above, for example a founder intro into a product film | Each part follows its own branch; plan the hand-over shot |
| Voiceover (add-on) | Any branch, when the owner asks for narration | A script timed to picture, recording or TTS, captions |
| Store preview | App Store or Google Play listing video | Fixed specs and content rules (below); no social formats |

## Proof is not always a number

Every branch needs one proof moment. Pick the kind that fits the product:
- **a number** from a real run (the worked example: "+245 kcal from the details");
- **a before and after** of the same task;
- **a workflow completed**: start to done, in real time or honestly sped up with a visible clock;
- **a customer outcome**: a real customer's words or result, with their written permission.

## (b) Character-led / playful

**The cast.** In order of preference:
1. the brand's own mascot or illustration set (ask the design team for layered source files: SVG, Figma, After Effects, Lottie JSON);
2. characters built from the brand's primitives: its logo shapes, icon strokes, UI components with faces;
3. a commissioned illustrator, with the licence in writing;
4. never a stock character pack the brand did not choose.

**Building it.** In Remotion, draw each character as SVG parts (body, eyes, limbs) and animate their transforms with `spring()` and `interpolate()`. A rigged animation from After Effects or a Lottie file plays through `@remotion/lottie`; add it with `npm i @remotion/lottie` in `film/engine/`. Keep the real product UI as recorded footage: the cast points at it, reacts to it, or hands over to it.

**Timing, as starting points.**
- Anticipation before every big move: a small move the other way, 4–8 frames at 60 fps.
- Squash on landing, stretch in flight; keep the area constant (scale y 0.8 with scale x 1.25).
- Follow-through: parts that hang (ears, antennae) settle 3–6 frames after the body stops.
- A comedic beat is set-up, pause, payoff. The pause is what makes it land: hold 0.3–0.8 s before the payoff. Groups of three: the third breaks the pattern.

**Research.** The library names Duolingo, Notion and Headspace but holds no measurements for them, and the 12 playful films it does hold are AI-lab character shorts. Plan the research as new: measure cut rate, hold before each payoff, and how long the cast is on screen versus the product.

**Sound.** Cartoon SFX on every action (boing, pop, whoosh), a voice-like sound per character if they "speak", music with clear accents to land the gags on.

## (c) Presenter / founder / UGC

**Script first.** Speech runs at about 2.5 words a second, so a 30 s film holds about 75 spoken words. Write it, read it aloud against a timer, cut until it fits with room for one pause before the proof.

**Teleprompter lines.** One sentence per line, about 8–12 words, broken at natural pauses. Short words. No numbers the speaker has to parse; put them on screen instead.

**Shot list.** Number every shot: framing (wide, medium, close), what is said, the b-roll under it, and its length. Shoot each line two or three times. Record the room tone (10 s of silence) for edits.

**Recording.** A clip-on or shotgun microphone close to the speaker, a quiet room with soft furnishings, light from the front-side, the camera at eye level. Phone cameras are fine for UGC; lock exposure and focus. 30 fps is normal for live action; deliver at the frame rate it was shot at, or 60 fps if UI b-roll dominates.

**B-roll from the real UI.** Every product claim cuts to a real capture (`capture.md`). Same rules as branch (a): real build, real data, no leaked dev state.

**Captions for sound-off.** Most feed autoplay is muted. Burn in captions: 1–2 lines, at most about 42 characters a line, each caption on screen at least 1 s, timed to the speech, inside the 9:16 safe band. Write them from the final script, then correct them against the edit.

**The mix is dialogue-first.** Clean the voice (high-pass around 80 Hz, gentle noise reduction), then duck the music under it. `sfx_mix.py` has no dialogue track; mix the SFX and music first, then duck that bed under the voice with ffmpeg:
```bash
ffmpeg -i voice.wav -i bed.wav -filter_complex \
  "[1:a][0:a]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=400[duck];[duck][0:a]amix=inputs=2:normalize=0[out]" \
  -map "[out]" mix.wav
```
On a test tone this lowered the bed by about 14 dB while the voice spoke. Keep SFX sparse under speech; measure loudness on the delivered file (`sound.md`).

## (d) Hybrid

Plan each part in its own branch, then design the hand-over: the presenter points and the camera pushes into the screen; the mascot jumps into the UI; the voiceover's last word lands on the first frame of the demo. Put the hand-over on the storyboard as its own beat.

## Voiceover (any branch)

1. **Script to picture.** Write it after the storyboard is timed. About 2.5 words a second; leave 0.3–0.5 s of silence before each reveal so the picture lands first.
2. **Record or TTS.** A recorded voice (the founder, or a hired voice actor) sounds most trusted. TTS is fine for drafts and for fast iteration; for the final, check the provider's terms for commercial use and get the owner's approval of the exact voice.
3. **Timing.** Lay the voice on the timeline, then move picture cuts to the voice's phrase ends, not the other way round.
4. **Captions** from the script, as in branch (c).
5. **Mix** with the ducking recipe above.

## Store preview (App Store, Google Play)

Look the specs up again before each project; stores change them. These were read on 7 October 2026.

**Apple App Store.** From "App preview specifications" (App Store Connect Help) and "Show more with app previews" (Apple Developer):
- 15–30 s; up to three previews per device size and language; 500 MB maximum; the poster frame defaults to 5 s.
- H.264 (.mov, .m4v, .mp4) at 10–12 Mbps, or ProRes 422 HQ (.mov). **At most 30 fps.** Stereo AAC 256 kb/s at 44.1 or 48 kHz.
- Resolutions (portrait / landscape): iPhone with Dynamic Island or Face ID, 886×1920 / 1920×886; iPhone with Home button, large and 4", 1080×1920 / 1920×1080; medium, 750×1334 / 1334×750; iPad (13", 12.9", 11", 10.5"), 1200×1600 / 1600×1200; iPad 9.7", 900×1200 / 1200×900; Mac and Apple TV, 1920×1080 landscape only; Apple Vision Pro, 3840×2160 landscape only.
- Content (App Review Guideline 2.3.4): "previews may only use video screen captures of the app itself". Narration and video or text overlays are allowed. Apple's guidance adds: no people or fingers filmed interacting with a device; capture the native UI resolution rather than zooming in; no prices or dates; disclose in-app purchase, subscription or login; text on screen long enough to read, because previews play muted by default.

**Google Play.** From "Add preview assets to showcase your app" (Play Console Help):
- A YouTube URL of one video (not a playlist or channel, no timecode parameters); public or unlisted, embeddable, not age-restricted; monetisation off, so no ads play.
- Landscape or portrait, matching the app; no black bars beside a portrait video.
- Only the first 30 s autoplay, muted. Show the real app experience in the first 10 s; avoid long logos and cutscenes; no performance claims such as "Best" or "#1"; captions recommended.

**What changes in production.**
- No device frame, no camera zoom on the UI for Apple: the frame is the app's screen. Motion comes from the app itself and from cuts.
- Capture at the store's size and record at 30 fps, or convert to 30 fps CFR (`$SKILL/scripts/capture/vfr_to_cfr.sh in.mp4 out.mp4 30`).
- Render at 30 fps and the store's exact size with the starter's opt-in `Store-886x1920` composition (`src/film/Store.tsx`: full-screen capture, no device, no safe band) and `render/store.sh`, which encodes to Apple's spec and probes the result (`engine.md`, The store preview composition). Another device class is another composition at that size.
- Text overlays only to explain what the footage can't; keep them short and inside the screen.
- Make one preview per required device class; reuse the edit, re-capture on each device class.

**Validation checklist (Apple), per file:**
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,channels,sample_rate,bit_rate:format=duration,size -of default=nw=1 preview.mp4
```
- [ ] Duration 15.0–30.0 s; size under 500 MB.
- [ ] Width × height exactly one accepted size for the target device class.
- [ ] `r_frame_rate` ≤ 30; H.264 High profile or ProRes 422 HQ.
- [ ] Audio stereo AAC 256 kb/s at 44.1 or 48 kHz. If an upload is refused for a missing audio track, add a silent one (`-f lavfi -i anullsrc=r=48000:cl=stereo -shortest`).
- [ ] Every frame is the app's own screen; no hands, no device bezel.
- [ ] No prices, dates or "new" references; purchases and login disclosed.
- [ ] The poster frame (5 s by default) is a strong frame.

**Validation checklist (Google Play):** the YouTube video is public or unlisted, embeddable, not age-restricted, monetisation off; the first 10 s show the app; no "#1" or "Best"; the URL is a plain video URL.

## Platform routes

| Product runs on | Capture | Framing in the film |
|---|---|---|
| iOS | `capture.md`, iOS Simulator (`$SKILL/scripts/capture/ios_sim_record.py`) | device preset `iphone` |
| Android | `capture.md`, Android (`$SKILL/scripts/capture/android_record.py`) | device preset `android`; never an iPhone body around Android UI |
| Web app, B2B dashboard | `capture.md`, web (`$SKILL/scripts/capture/web_screencast.cjs`) | device preset `browser`; no phone; crop to the panel that matters |
| Desktop app | `capture.md`, user-recorded footage (a screen recording of the app window at 2× scale) | a window frame drawn from the `browser` preset, or no frame |
| Several | one capture per platform | show each truthfully; a morph between them (phone widens into a browser) is a designed transition, not a claim |

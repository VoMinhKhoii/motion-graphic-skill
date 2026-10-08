# Production notes

The practical problems of capturing a real app for a film, and how each was solved. Most of the production time went here, not into the edit. Kallo is a Flutter app on iOS plus a Next.js web app; the notes are written so they carry over to other stacks.

## The capture setup

- **iOS.** The app's development build ran in the iOS simulator (an iPhone 17 Pro Max), pointed at a local backend and the development database. Taps and typing were sent by `idb` (`idb ui tap --udid $SIM_UDID X Y`, `idb ui text --udid $SIM_UDID "c"`). The screen was recorded with `xcrun simctl io $SIM_UDID recordVideo --codec=h264`. A small wrapper started the recording, waited for "Recording started", and wrote every action to an event log as "seconds since start, label", so the edit could find each tap without scrubbing.
- **Web.** Playwright drove Chromium, and frames came from the Chrome DevTools Protocol screencast (`Page.startScreencast`). Each frame arrives with its own timestamp; the clip is rebuilt at true speed from those timestamps with an ffmpeg concat list (`duration` per frame).
- **Real numbers only.** Every meal on screen was a real run of the app's analysis on the development server. Totals were recorded as they came back, even when a re-run gave a different number (the same breakfast returned 436 and 506 kcal on two runs; the film used whichever take was recorded).

## iOS capture lessons

### Debug-build stalls

Flutter runs only debug builds in the iOS simulator, and a debug build stalls where a release build does not. On "Save meal" it froze for about 0.7 s, then the card fold, the new numbers and the "Meal saved" toast all appeared in the same frame. In the teaser this read as jank in the gauge.

Fix: cut the stall out of the clip, and bridge the jump by dissolving the last pre-save frame away over 0.3 s on top of the post-save footage. The ring fill that follows is the app's real 60 fps animation. Do not slow-motion or interpolate across a stall; it smears.

### The composer overlay swallowed taps

When the result card ended just above the "Save meal" button, the composer's overlay covered the lower part of the button, and taps there did nothing. Fix for the take: tap the button's top edge (its frame's y plus 5 points). This is a real app bug and was reported as one.

### Autocorrect off, and cut the flashes anyway

Before typing on camera, turn off auto-correction, auto-capitalisation, spell checking and smart punctuation in the simulator's keyboard settings. Even then, iOS sometimes flashes a text selection or an autocorrect bubble for a frame or two mid-word. Find those frames (a contact sheet at the typing's frame rate is enough) and cut them.

Type one letter at a time, with a small random delay (10–40 ms, longer after a comma). Typing whole words reads as fake on screen.

### idb cannot type diacritics

`idb ui text` cannot send Vietnamese characters such as "ư" or "ờ". Fix: add the simulator's Vietnamese Telex keyboard, remove the others for the take so it cannot switch, and send the Telex keystrokes letter by letter. A small converter turns the sentence into keys: each character is decomposed (NFD), the vowel shape becomes a doubled letter or a `w` ("â" is `aa`, "ơ" is `ow`, "ư" is `uw`), "đ" is `dd`, and the tone key goes right after its vowel (`s` acute, `f` grave, `r` hook, `x` tilde, `j` dot). "lườn" is typed `luwowfn`.

### Switch the app's language inside the app

The app's language and region are set in the app (Settings, then Region & language, then Save). The app writes its stored locale back when it launches, so editing the preference file from outside does not stick. Switch in the app before the take, and switch back afterwards.

### The greeting follows the device clock

The Home screen greets by time of day, from the device's hour. A teaser recorded at 1 a.m. said the wrong thing for a lunch scene. Fix: a film-only patch in a separate local checkout that pins the greeting to lunch. It was never committed. If your app has time-dependent copy, decide the story's clock first and patch the capture build, not the product.

### Time labels show the real clock

The chat-style log shows a time separator above each new message. Before saving it shows the device's current time ("1:12 AM"), and after saving the meal's time. Fix: cover the separator with an image of the app's own post-save label ("12:30"), cut from a later frame of the same recording, at the same position. For the web, Playwright's `page.clock.install` fixed the page's time at 12:40 so the labels were right from the start.

### Recordings are variable frame rate

The simulator recorder writes a frame only when the screen changes. So video time is not wall time, and a static screen (Home before the first tap) may never reach the file at all.

- Take a full-resolution screenshot for any still, and use it as the first frame.
- Read frame times from the raw file with `ffprobe -show_entries frame=pts_time`. Use those, not the event log, to place cuts.
- Convert to constant frame rate before the edit: `ffmpeg -i raw.mp4 -vf fps=60 -fps_mode cfr clip.mp4`. Remotion's `OffthreadVideo` mis-seeks on sparse variable-rate files.

### Cut-out UI: measure the real radius

When a component is lifted out of a recording (the composer box), cut just inside the app's own border, at the app's own corner radius, and draw at most one border. A cut at 58 px on a box with a 65 px radius, with a second border on top of the app's, read as "the edge is off".

### Check status text by OCR

The app cycles through several status words while it analyses. The film shows at most two per analysis. A small OCR tool (Apple Vision) printed the status line of each recording frame by frame, which made it easy to find and cut past the extras. The web run had shown five.

## Web capture lessons

### Twice the size, then a GPU

The screencast caps frames at CSS pixels and ignores the device pixel ratio. A 1440x900 window gives 1440x900 frames even with `deviceScaleFactor: 2`, and once the camera zoomed into the input it looked like 480p next to the phone footage.

Fix:
1. Open the page in a viewport of 2880x1800 at device pixel ratio 1.
2. After load, inject `html { zoom: 2 !important }`. The page lays out as if it were 1440x900 but paints every pixel at twice the size.
3. Ask the screencast for `maxWidth: 2880, maxHeight: 1800`.

Frame rate is the cost. In software rendering, 2x gave about 16–19 fps (14 in one take) and 3x about 9 fps, which showed up as components seeming to blink. Launching Chromium with GPU flags fixed it:

```
--use-angle=metal --enable-gpu-rasterization --ignore-gpu-blocklist --enable-gpu
```

With these, the 2x screencast ran at about 57 fps. The final web beat uses two takes: typing at 3x (only the input box needs to be sharp) and the analysis at 2x. No frame interpolation.

Hide development overlays (the framework's dev indicator, admin links) with injected CSS before recording.

### Logging in without typing a password

The browser session was created once from the backend's admin API (a magic link verified in a script, saved as Playwright storage state), so no password was typed and no login screen was recorded. Use your own stack's equivalent, and never commit the resulting state file.

## Data on the development server

- The film used a demo account on the development database, with friends, groups and photos added for the social scenes. Every change was backed up first and restored afterwards.
- To re-record a scene on a day that already had later meals logged, those meals were moved two days ahead for the take and moved back after, and the new test meal was deleted.
- The model provider returned 503 errors during one session. With the owner's approval, the backend was pointed at a different hosting of the same model for the demo, so the numbers kept coming from the real pipeline. With a preview model profile, a long meal escalated to a slower model and took 84 s, close to the point where the app gives up (about 90 s). The teaser takes used the production model settings.

## Rendering

- **Banding.** The soft gradients banded badly when frames were rendered as JPEG and encoded straight to x264. The fix was a two-step master: render PNG frames to ProRes 4444, then encode to x264 with `-tune grain` (CRF 14 for the master, CRF 22 for the "light" copy). The grain tuning keeps the encoder from flattening the gradient's dither.
- **Stills before video.** A small script renders stills at chosen times from the same bundle. Every storyboard from v9 on was made this way, at the edit's real timings, so the frames the owner signed off are the frames in the film.
- **Shell environment.** A `NODE_OPTIONS` preload from the terminal broke `npx` in this setup; renders ran with `env -u NODE_OPTIONS`.

## The /tmp purge, and how the project was recovered

For the first week the whole project lived in the agent session's scratch folder under `/private/tmp`. On 5–6 October, with the disk at 93%, macOS purged files in it that had not been touched for a few days: sources, the font files, the token file, the wordmark, recordings, the sound library and the browser login state.

Recovery:
- Remotion keeps its webpack bundles in the system temp folder (`/var/folders/.../T/remotion-webpack-bundle-*`). Each bundle holds a full copy of `public/` (recordings, images, audio), and its `.map` files contain the TypeScript sources in `sourcesContent`.
- Inlined JSON data can be pulled back out of `bundle.js`, but webpack renames its keys, so it needs mapping by hand.
- Shared files (fonts, tokens) came back from the app's repository; the rest from the session transcript.

Lessons:
- Keep a film project in a real folder under version control from day one, never in a temp or scratch folder.
- After a gap of days, check the project is intact before rendering.
- Commit recordings or keep them on a backed-up drive; they are the slowest thing to remake.

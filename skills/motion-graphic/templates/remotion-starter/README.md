# remotion-starter

A Remotion 4 project for product launch films built from real screen recordings. It has a small engine
(`src/engine/`, with five production recipes in `src/engine/recipes/`) and a 14.6 s example film
(`src/film/`) that renders out of the box in three formats and on three devices (iPhone, Android, browser).
The API and the reasoning behind each part are in `$SKILL/references/engine.md`.

## Quick start

Never edit the installed template. Copy it into the film workspace in the user's project, then work there:

```bash
mkdir -p film && cp -R "$SKILL/templates/remotion-starter" film/engine && cd film/engine
npm ci                                # exact versions from package-lock.json
bash scripts/make_sample_clip.sh      # placeholder recordings (phone + web) and photo (needs ffmpeg)
npx tsc --noEmit
npx remotion studio src/index.ts      # scrub the film and the recipe demos in the browser
SCALE=0.5 node render/stills.mjs out/stills 1.4 4.0 7.0 11.3   # COMP=Film-916 for another format
bash render/master.sh Film-45 acme_4x5 [public/audio/mix.wav]
```

If `npx` or `node` fails with a preload error, a shell has injected `NODE_OPTIONS`; prefix the command with
`env -u NODE_OPTIONS`.

If stills fail with `Failed to fetch ... disk space is low`, Chrome is refusing full-size video frames because
the disk is nearly full. Free space, or run `SCALE=0.5 bash scripts/make_sample_clip.sh` for a half-size clip.

## Compositions

| id | size | for |
|---|---|---|
| `Film-169` | 1920x1080 | YouTube, X, the website |
| `Film-45` | 1080x1350 | X, Threads and Instagram feeds |
| `Film-916` | 1080x1920 | TikTok, Reels, Shorts; content stays in the safe band y 140..1620 |
| `Recipes-169`, `Recipes-45`, `Recipes-916` | as above | the five recipe demos; not part of the film |
| `Store-886x1920` | 886x1920, 30 fps | opt-in App Store preview: the recording full-screen, no device, no safe band (`render/store.sh`) |

The film and recipe compositions run at 60 fps. The engine reads the rate from each composition, so a 30 fps
cut shows the same moments; scene code works in seconds. Each scene reads `c.P` (portrait) and `c.tall` (9:16) to
adapt its layout.

## Layout

```
src/engine/   the reusable parts (no product assumptions)
  time.ts       FILM_FPS, frameAt, easings, ramp, lerp, rand
  camera.ts     CamKey, camAt (spring camera), useCam, fitK, holdEdges
  clips.tsx     Seg, Patch, Clips, Bridge, segWindow (cutting real recordings)
  device.tsx    DeviceSpec, IPHONE/ANDROID/BROWSER presets, Device, At, onScreen, onRec, OnScreen, fromPoints
  cutout.tsx    CutOut (lift one component out of a recording)
  pointer.tsx   PtrEvent, pointerAt, clickAt, Pointer (hand cursor)
  type.tsx      Typed (letter by letter), Words (word by word, *accent)
  worlds.tsx    GradientWorld, PhotoWorld (full-bleed backgrounds)
  safe-band.tsx bandFor, Bleed (9:16 safe band)
  reel.tsx      Scene, Reel, timeline, durationInFrames (scenes array -> one Sequence each, at the comp's fps)
  end-card.tsx  EndCard
  theme.tsx     ThemeProvider (font, ink, accent)
  recipes/      container-morph, feed-dock, scanner, tile-burst, scene-clock (see engine.md, Recipes)
src/film/     the example: replace with your film
  config.ts     brand, placeholder palette, device PRESET, measured recording geometry
  Film.tsx      the scenes array
  scenes/       Title, Demo, Lift, End
  Recipes.tsx   the recipe demos' scenes array
  recipes/      MorphDemo, DockDemo, ScanDemo, TilesDemo, ClockDemo (generated media only)
  Store.tsx     the opt-in App Store preview (reuses the Demo scene's edit)
render/       stills.mjs, master.sh, store.sh
scripts/      make_sample_clip.sh
public/rec/   recordings (<clip>.mp4, constant 60 fps); the samples are sample.mp4 and sample_web.mp4
public/img/   images
```

## Making it yours

1. Record the product (see `$SKILL/references/capture.md` and `$SKILL/scripts/capture/`). Convert every clip to
   constant 60 fps (`capture/vfr_to_cfr.sh`) and put it in `public/rec/`.
2. In `src/film/config.ts`, set `PRESET` to `iphone`, `android` or `browser` (web-only and B2B products get the
   browser window, no phone), and the preset's `w`/`h`/`radius` to your recording's size.
3. Replace `WORLD` (a grey-blue placeholder) with the product's own gradients and colours from the brand
   inventory, and `BRAND`/`THEME` with its name and type. `THEME`'s accent, caret and tap ring are ink-grey
   placeholders: set `accent` and `accentSolid` from the brand inventory too.
4. Measure the rects you need (cards, buttons) on stills of the recording, in recording pixels, and put them in
   the recording's `ui`.
5. Write each scene's segments from the capture log: find the frame where the app reacts to each tap and cut there.
6. Fonts: the example uses the system font stack. For a brand font, add `@remotion/fonts`
   (`npm i -E @remotion/fonts@4.0.530`), call `loadFont({ family, url: staticFile('fonts/X.ttf'), weight })` behind
   `delayRender` in `Root.tsx`, and set `THEME.font`.
7. Render stills at the beats, look at them, then render the master. Delete `src/film/recipes/`, `Recipes.tsx`
   and the `Recipes-*` compositions once you have taken what you need.

The example uses only generated media. Do not commit third-party video, music or sound effects to a public repo.

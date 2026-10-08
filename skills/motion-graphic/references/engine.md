# The engine

How the Remotion engine in `templates/remotion-starter/` builds a product film from real screen recordings: its
API, the patterns it encodes, and the numbers that worked. Numbers marked "Kallo" come from the worked example's
final film (83 s, 14 scenes) and teaser (10.6 to 12.4 s); the rest were measured on the template.

Every frame of UI in the film is a real recording of the real build. The engine never redraws the product. It
cuts recordings, frames them with a camera, adds a pointer, type, and backgrounds around them.

## Coordinates and clocks

- **Seconds, not frames.** Every scene gets `c.s`, seconds since the scene started. The social compositions run
  at 60 fps (`FILM_FPS` in `time.ts`), but nothing in the engine assumes it: `Reel`, `Clips` and the scene clock
  read the rate from the composition (`useVideoConfig().fps`), so the same film renders the same moments at
  30 fps. Convert to frames only at a `<Sequence>` boundary, with `frameAt(t, fps)` (the first frame at or after
  `t`) and `durationInFrames(scenes, fps)`. Never time anything with `c.frame`: it counts composition frames.
  Tested: seven stills of the example film rendered at 60 and at 30 fps (same seconds, three of them on recording
  segments, one at 2x) were pixel-identical; a still at 30 fps frame 210 (7.0 s) differed, so the 30 fps render
  really ran at 30.
- **Recording px** are the recording's own pixels (1320x2868 for a 6.9" iPhone simulator capture; 2880x1800 for a
  2x browser capture). Measure every rect you need on a still of the recording.
- **Device px** are the CSS device's pixels: recording px plus the bezel, plus the top bar for a browser window
  (`onScreen(spec, x, y)`). The camera, `At` and the pointer all work in device px. When a recording is not the
  screen's size (the phone sample on the Android preset), `OnScreen` fits it to the screen's width and
  `onRec(spec, rec, x, y)` maps its points; with your own capture the two match and the fit is 1.
- **iOS points**: idb and XCUITest tap in points; a 3x screen has 3 recording px per point
  (`fromPoints(spec, x, y, 3)`). adb taps in pixels: `fromPoints(spec, x, y, 1)`.
- **Frame px**: the output frame. `useCam` returns `map(x, y)`, device px to frame px, for anything drawn on top
  of the device that must keep its size (pointer, callouts).

## Scenes (`reel.tsx`)

A film is an array of `{ id, dur, fadeIn?, C }`. `Reel` plays them in order, one `<Sequence>` each, so every
scene has its own clock starting at 0. Retiming one scene never shifts the timing inside another. `fadeIn`
starts a scene that many seconds early and dissolves it in over the previous one (0.3 to 0.4 s worked).
`timeline(scenes)` gives the start times, which the sound cue sheet mirrors. Scene boundaries are placed at the
composition's fps, and a scene whose start falls between frames gets a clock that still reads exact seconds.
`<Reel band={false}>` turns the 9:16 safe band off (the store preview: no platform draws over it).

When several beats must share one continuous camera (the Kallo opening: 21 s, two cards that must never jump),
make them one scene with internal time constants instead of separate scenes.

Each scene adapts to the format through `c.P` (portrait: 4:5 and 9:16) and `c.tall` (9:16 only), plus `c.W`
and `c.H`, which are the layout area (the safe band in 9:16).

## The camera (`camera.ts`)

`CamKey = { t, x, y, k, snap? }`: from scene second `t`, the camera wants device point (x, y) centred at scale
`k` (frame px per device px). `snap: true` jumps there (use it on the first key).

`camAt(keys, s, omega)` is a critically damped spring chasing a step target. It leaves each key at speed, eases
in, and never overshoots. Scale is sprung in log space, so a zoom from 0.4 to 1.2 feels even. The track is
integrated once in 1/60 s steps and cached, and sampled by seconds, so frames can render in any order and at
any composition fps. Time to cover 95% / 99% of a move:

| omega | 95% | 99% | use |
|---|---|---|---|
| 7.5 | 0.65 s | 0.95 s | calm follow (Kallo v7) |
| 8 | 0.62 s | 0.90 s | the Kallo teaser |
| 9 | 0.55 s | 0.80 s | default; Kallo final film ("brisker than v7") |
| 12 | 0.42 s | 0.62 s | snappy punch-ins |

**Move, then hold.** Keys are targets, not keyframes. Space them at least 0.6 s apart at omega 9 so each move
lands and the shot holds before the next one. Put a key 0.3 to 0.6 s before the action it frames, so the camera
has arrived when the app reacts. One subject per hold; the viewer should never chase.

Scales that worked on a 1470x3000 phone (Kallo): the whole phone at `H*0.9/3000` (about 0.41 in 4:5); content
at 0.72 to 0.86; tight on a control before a tap at 1.0 to 1.2. A browser capture at 2x ran at 1.3 to 2.15.
`useCam` multiplies every k by 0.84 in landscape: a 1080 px tall frame needs a slightly wider shot than a 1350
or 1920 px tall one to show the same UI. `fitK(c, h, frac)` gives the k that fits `h` device px into `frac` of
the layout height in any format; `fitBox(c, w, h, frac)` fits a whole box by whichever side binds (a wide
browser window in 4:5 or 9:16 is limited by width). `holdEdges(c, key, deviceH, m)` clamps a key's y so the device's top or
bottom edge never comes more than `m` px into the frame: no empty void under the phone on a close shot.

The owner's notes that shaped this: drastic camera chasing between positions read as janky; a Screen
Studio-style camera that rides the pointer, lands tight on the control and then holds read as premium.
Keep the phone's side edges in frame except for a brief punch-in; show the whole small phone only for a beat,
because at full-phone scale nothing is readable.

## Segments: cutting the recording (`clips.tsx`)

`Seg = { t0, t1, clip, src, rate }`: scene seconds [t0, t1) play `public/rec/<clip>.mp4` from source second
`src` at `rate`. A scene's segment list is an edit decision list over one or more takes:

```ts
{ t0: 0,    t1: 0.9,  clip: 'take', src: 1.0,  rate: 0 },    // hold a frame while the camera settles
{ t0: 1.2,  t1: 2.65, clip: 'take', src: 2.5,  rate: 2.0 },  // typing, 2x, still letter by letter
{ t0: 2.65, t1: 3.25, clip: 'take', src: 5.65, rate: 1 },    // the tap and the app's reaction, real speed
{ t0: 3.6,  t1: 5.8,  clip: 'take', src: 7.62, rate: 1 },    // the result lands, real speed
```

**Why the timeline is cut, not sped.** A real take is mostly waiting: network calls, the model thinking, the
hand moving. Speeding the whole take makes the parts that matter (a result landing, a sheet opening, a gauge
filling) fast and cheap-looking, and still leaves dead air. Cutting keeps every product animation at its real
speed and removes the waiting. Rules that held up in Kallo:

- Rate 1 for anything the product animates: results landing, cards closing, sheets, toasts, rings filling. The
  Kallo teaser shows the save and the rings filling at real 60 fps.
- Rate 0 to hold a frame: before a tap (the empty field while the window opens), after a result (a beat on the
  total). A hold can run under a camera move, so the shot never looks frozen.
- 2x to 8x for typing and scrolling (Kallo: 2.03, 2.18, 2.45, 4.5, 8.1). Kallo also used 16.9x and 26x for
  0.6 s runs through the label-reading flow: motion that says "time passes" without being watched.
- Cut waiting text down to a beat: "Connecting…" 0.5 s, "Calculating…" 0.5 s ("two words at most", teaser).
- Slow motion is rare: 0.3x on a gauge filling, once (Kallo web scene).
- Segments within one clip can jump backwards or forwards freely; the viewer sees continuous UI as long as the
  screen state matches at the cut.

`Clips` renders every segment as its own `<Sequence>` and `<OffthreadVideo>` and shows only the live one. Its
`offset` prop is for nested sub-timelines: if you pass `s = sceneSeconds - 3`, pass `offset={3}` so the
Sequences (which always run on the scene's clock) line up.

### Letter-level typing, and how far it can be sped

Type the take one character at a time (`capture/type_letters.py`, `capture/ios_sim_record.py type`), never a
word at a time: a word that appears in one frame cannot be made to look typed in the edit. Turn autocorrect,
auto-capitalisation and smart punctuation off, then check every take for a selection flash or a suggestion
bubble mid-word and cut around it.

A letter-level take can be sped up until letters arrive faster than frames. The measure is letters per second
on screen, not the rate: `letters/s on screen = raw letters/s x rate`, and the ceiling is 60 (one letter per frame
at 60 fps). What shipped in Kallo:

- Web: the capture script's 99-letter meal sentence, typed with a 45 ms key delay; 6.4 s of raw take played
  at 2.18x in 2.94 s: about 34 letters/s, 1.8 frames per letter. Reads as fast, clean typing.
- Phone, Vietnamese via Telex: a 41-character sentence over 9.9 s of raw take, played at 4.95x in 2.0 s:
  20 letters/s.
- Phone, English teaser: 52.4 s of raw take squeezed into 3.0 s (17.5x). The raw take was slow because every
  `idb ui text` call is a separate process, so letters arrived far apart; on screen it still reads as typing.

Aim for 20 to 35 letters/s, the range that shipped. Faster was not tested; past 60 letters skip in pairs. The template's sample
types one letter per 0.12 s and plays it at 2x: 16.7 letters/s.

## Patches (`Patch` in `clips.tsx`)

A `Patch` covers leaked UI while a clip is between source seconds `from` and `to`: a debug badge, the
simulator's real clock in a timestamp, a "Yesterday" that should read "Today", a notification. Cover it with an
image of the right pixels (`img`) or a flat `fill`. Kallo patched a 320x38 time label at (500, 788) with the
app's own post-save pixels, and a 230x54 "Today" label.

- Take a patch image from the same recording at a moment where the region shows the right thing, or from a
  screenshot of the right state. Never redraw it.
- Measure fill colours on a decoded frame or a rendered still, not from design tokens. The template's
  background is drawn as #F3F1EC and decodes as #F0EFEC after H.264.
- Pad the cover 4 to 6 px past the leak on every side. H.264's 4:2:0 chroma bleeds a saturated colour 1 to 2 px
  past its edge (more in a scaled-down file); an exact-size cover leaves a faint coloured outline (seen on the
  template's red badge, gone at 6 px).

## Crossfade bridges over app stalls (`Bridge`)

Debug builds and slow saves freeze the UI, then pop the new state in one frame. Kallo's teaser: the build
stalled about 0.7 s on Save, then the card fold, the new numbers and the toast appeared in a single frame. Fix:

1. Cut the stall down to a short hold (0.15 s, `rate: 0`).
2. Start the next segment just after the pop.
3. Lay `<Bridge t dur clip src>` over the cut: the last pre-pop frame, dissolving away over `dur` = 0.3 s.

The pop becomes a 0.3 s dissolve and everything after it (the rings filling) stays real 60 fps. Find the stall
and the pop with `capture/frame_pts.py` on the raw variable-rate recording: the stall is a long gap between
frame timestamps, the pop is the frame after it.

## Cut-outs (`cutout.tsx`)

`CutOut` lifts one component out of the recording and shows it alone, at hero scale, with the recording still
playing inside it: a card, an input box, a chart. Kallo used it for the composer (the input box as a component)
and for two meal cards side by side, which read much better than two whole phones.

The clean-edge trick: cut `edge` px inside the component's own border, then draw one fresh border of the same
width and colour with your own radius. Kallo's composer: box x 36, width 1248, bottom 2730, a 3 px border
rgb(231,218,200), outer radius 65. Cutting on or outside the border showed page background in the corners, a
doubled edge, and the app's square fill poking past the rounded top-right corner. If the component grows (the
composer's top moved 2464 → 2396 → 2326 as the typed sentence wrapped to 2 and 3 lines), pass its current rect
each frame as a function of the source time.

## The pointer (`pointer.tsx`)

`PtrEvent`: `at` (arrive), `tap`, `drag` (t to t1). `Pointer` draws a pointing hand, fingertip on the point, in
frame space through `map`, so it never scales with the camera. Timing, all from Kallo's final film:

- A move takes at most `travel` = 0.36 s before its event and arcs 10% sideways.
- A tap presses in over the 0.08 s before `t`, releases over 0.12 s after; the ring runs 0.5 s.
- It fades in 0.45 s before the first event and out 0.45 s after the last.
- Size 74 px in portrait formats, 64 px in 16:9.

**A tap lands on the frame where the app reacts**: the field focuses, the button darkens, the sheet starts to
move. Not when a finger "would" press. The capture log gives the time the command was sent; the screen reacts
0.1 to 0.4 s later, so find the reaction frame (`frame_pts.py`, `research/activity.py`, or stepping through
stills) and put `t` there. A pointer that clicks before or after the UI responds reads as fake at once.
Move the pointer out of the way of text being typed (an `at` event below the field).

The owner asked for a pointing hand rather than a disc, a visible click on every action, and the camera
landing tight on the control before the click.

## Type (`type.tsx`)

- `Typed`: letter by letter at `cps` letters/s (16 default; 26 for a two-word title), caret solid while typing,
  then blinking at 2.2 Hz until `caretUntil`.
- `Words`: word by word, each word rising 0.42 em out of a 9 px blur over 0.42 s (expo-out), 0.07 s apart.
  `*word` fills that word with the accent gradient. `exit` lifts the block out over 0.35 s.

One or two lines, three to six words, held about 2 s, is the rhythm that worked; a paragraph never did. Vary
the treatment from line to line (typed, word by word, an inline UI chip).

## Worlds and the device

- `GradientWorld`: a base colour, a soft top sweep, and blobs (radial gradients clear by 70% of their ellipse)
  drifting on slow orbits. A different `seed` per text screen changes the layout and keeps the style. Use the
  product's own gradients (Kallo used its onboarding's apricot, sage, violet and sky). The starter's `WORLD` in
  `config.ts` is a deliberately plain grey-blue placeholder: replace it from the brand inventory, and if the
  product has no gradients, agree a small provisional palette with the owner before building on it.
- `PhotoWorld`: a photo, cover-fit, blurred 6 px, brightness 0.9, pushed in 0.4% per second. Kallo used six
  generated, lived-in rooms by time of day; empty rooms read as vacant.
- `Device`: a CSS body around the screen. No bezel image ships. Phones stay flat and front-on; never tilt or
  hold them. Three presets, chosen with `PRESET` in `src/film/config.ts`:

  | preset | screen | body | camera | for |
  |---|---|---|---|---|
  | `iphone` (`IPHONE`) | 1320x2868, radius 190 | 60 px bezel | island 380x112 | iOS Simulator captures (6.9", 3x) |
  | `android` (`ANDROID`) | 1080x2400 (20:9), radius 104 | 40 px bezel | punch hole, 52 px | Pixel 7/8 emulator captures |
  | `browser` (`BROWSER`) | 1600x1000 page, radius 22 | a 76 px bar with three dots and an address field | none | web-only and B2B products, no phone |

  Change `w`/`h` to your capture's size. The starter's Demo and Lift scenes run on all three; for the browser the
  sample is a separate web recording (`sample_web.mp4`) and the Demo camera's zooms are multiples of the
  whole-window fit (`REC.zoom(whole)` in `config.ts`), because a wide window is small in 9:16. Phone zooms stay
  absolute.
- `At`: places device-px content so device point (cx, cy) sits at a frame point, at scale k. Feed it the camera.

## Recipes (`engine/recipes/`)

Five techniques from the worked film, ported as components with props. Each has a demo scene on generated media
in `src/film/recipes/` (no product UI, no real people), played by the `Recipes-169`, `Recipes-45` and
`Recipes-916` compositions: scrub them in the studio, copy the one you need into a scene, delete the rest.
The timings are the film's unless marked.

### Container morph (`container-morph.tsx`)

One rounded box changes shape while its content crosses from one layout to another: a phone screen becomes a
browser window (the film's phone-to-web beat), a card becomes a full screen.

- `ContainerMorph { p, from, to, a, b, bg, fadeOut?, fadeIn?, shadow? }`. `from`/`to` are frame-px boxes with a
  radius; `a`/`b` are the two contents, each with its own size and fixed scale `k`, centred in the moving box.
  `p` is the eased progress. `morphBox(from, to, p)` gives the box alone.
- Film: `p = ramp(s, t, t + 0.5)` (0.5 s, ease in-out). The source content fades out over p 0.06 to 0.4, the
  target fades in over p 0.4 to 0.75, so there is a moment of plain fill and the two layouts never
  double-expose. Draw the phone body yourself behind the box and fade it over p 0 to 0.25, so the bezel is gone
  before the box visibly grows. The shadow grows with p. The pointer appears only once p reaches 1. Sound: a
  long cinematic swoosh at the morph's start, −10 dB, pan 0.15.
- Use it when the same product lives on two surfaces, or when a detail opens into its own screen. Keep each
  side at its own scale; scaling the content with the box makes text swell and reads as a cheap zoom.
- Demo: `MorphDemo` (the phone sample becomes the web sample, debug badges patched).

### Feed docking (`feed-dock.tsx`)

People gather as avatars in frame space, then each one flies into their own post in a feed on the device, and
the post opens as they land (the film's circle scene).

- `FeedStack { rows, s, top, x, w, render }` draws the feed on the screen: rows `{ id, h, arrive? }` stacked
  from `top`. A row with `arrive` opens from arrive − 0.06 to arrive + 0.3 (expo), pushing the rows below it
  down; its content slides from 35% above its slot, fades in at 1.4x its opening and scales from 0.97.
  `rowOpen(row, s)` and `rowTop(rows, id, s, top)` give the same numbers for your own targets.
- `DockingAvatars { s, people, ring, target, gather?, stagger?, spin?, fly?, arc? }` draws the avatars:
  `people` are `{ id, initials, color, arrive }`; `target(id)` returns the docked avatar's frame-px centre and
  diameter (map the post's avatar point through the camera). `Avatar` is the placeholder: a coloured circle
  with initials. In a real film use real photos only with the people's consent.
- Film: avatars appear 0.07 s apart (each over 0.35 s, expo, from 60% scale); the ring turns at 0.4 rad/s and
  gathers over 0.55 to 1.1 s (radius 300 → 170 px in portrait, 260 → 160 in 16:9; diameter 168 → 92, 150 → 84;
  it rises to 14% of the height, 16% in 16:9, and flattens to 0.3 as tall). The phone rises in over 0.7 to 1.2 s
  (expo, from 85% scale and half a frame lower), framed at k 0.6 so about two thirds of it shows. Arrivals at
  1.15, 1.3, 1.55, 1.8, 2.05 and 2.3 s; each flight takes the last 0.35 s before its arrival (ease in-out) along
  an arc 50 px high, shrinking to the post's avatar size and losing its white ring and shadow. The avatar is
  removed 0.04 s after landing. Sound: one pop per avatar appearing (panned left to right), one pop per
  arrival, on the arrival time.
- Read the target at the landing frame (`rowTop` at arrive + 0.04). The film's code read it 0.4 s after
  arrival; with newer posts opening above, that point has already moved down by most of a row. The recipe
  fixes it.
- Use it for anything social or collaborative: friends, teammates, contributors joining. Newest posts at the
  top, so each arrival is seen.
- Demo: `DockDemo` (six placeholder people, a drawn feed).

### Scanner composite (`scanner.tsx`)

A camera screen whose "live" picture is your own still photo, under the app's real scanner chrome. A simulator
has no camera, so the film builds the view (the film's barcode and label scans).

- `Viewfinder { s, w, h, cam, chrome?, chromeB?, mix?, flash?, drift?, children }`. `children` is the picture at
  its own pixels; `cam = { x, y, z }` is the picture point shown at the screen's centre and its scale. The chrome
  is laid over with `mix-blend-mode: screen`: capture the app's scanner screen with nothing in front of the
  camera (the simulator shows black) and its black becomes transparent while the white guide, labels and
  buttons stay. `chromeB` and `mix` crossfade to a second chrome (the app switching modes). `flashAt(s, t)` and
  `pulseAt(s, t)` give the shutter flash and the "found" pulse.
- Film (v9): the barcode move ran 0.25 to 1.3 s (ease in-out) from z 0.52 to 0.6 on a 3024x6032 photo, a gentle
  push from the desk onto the code; the found pulse came at 1.3 s (in 0.08 s, held 0.08 s, out 0.1 s: a 10 px
  green ring, radius 60, around the guide), then the viewfinder dimmed 45% over 1.55 to 1.75 s while the real
  result sheet slid up over it (1.55 to 1.85 s, expo). The label move ran 0.25 to 1.6 s from z 0.95 to the
  zoom that fits the label; the handheld drift (two sines per axis, about ±8 px) faded to 0 over 1.2 to 1.75 s,
  the phone steadying, and the shutter flashed at 1.9 s (up in 0.05 s, held 0.05 s, gone 0.35 s after). The
  earlier v8 cut pushed harder, z 0.4 to 0.55 over 1.0 s, a 1.4x push. To land the code in the guide rather
  than the screen's centre, aim the camera at `code.y + (screenCentreY − guideCentreY) / z`. Sound: a short
  swipe as the phone comes to the object (−17 dB), a melodic tone on "found" (−12 dB), a shutter-like click on
  the photo. The demo uses the v8 shape (1.4x over 1.0 s, pulse 0.1/0.1/0.1, drift off over the last 0.1 s).
- Fill the screen at the widest zoom: the picture must cover the screen at the smallest z (the demo uses
  z 0.92, which just covers 2868 px of screen with a 4000 px tall picture). No black void around the photo.
- Use your own photos or openly licensed ones, credited as their licence asks.
- Demo: `ScanDemo` (a drawn desk and box, a valid EAN-13 of a made-up code, a drawn chrome).

### Tile burst and return (`tile-burst.tsx`)

A screen's own tiles burst out into a wall in frame space, each bar drawing itself, then fly back into their
places on the device as it arrives behind them (the film's micronutrient wall).

- `TileBurst { s, back, W, H, n, tw, th, cols, render, home, homeK, g?, gap?, stagger?, enter?, spin? }`.
  `render(i, bar)` draws tile i at tw x th with its bar at `bar` (0..1). Draw the device's copy with the same
  component so the hand-off cannot be seen. `home(i)` is the tile's top-left on the device in frame px, or null
  for a tile below the fold on the device: it rises 40% of the height out of frame instead. `homeK` is the
  camera's scale. `back` is the return's progress.
- Film: 17 tiles of 610x226, 3 columns in portrait and 5 in 16:9, at 0.54 and 0.52 scale, gaps 18 and 22 px.
  Each leaves the centre 0.045 s after the last, takes 0.55 s (expo) to reach its slot, spinning in from up to
  ±12°; its bar draws over 0.25 to 0.95 s after it leaves. The wall breathes ±3 px while it holds. It was
  complete 1.75 s after the burst, held about 0.85 s, then the phone rose in (0.55 s, from 220 px lower) and
  the tiles returned over 0.7 s (ease in-out), staggered 0.025 s each, fading in their last 15% as the phone's
  own tiles took over. Sound: a long swoosh on the burst, nine pops 0.09 s apart (one per two tiles), a long
  whoosh on the return.
- Use it to say "there is more than you think" with the product's own components: stats, integrations, settings.
  Real tiles only: lift them from the recording (`CutOut`) or from screenshots of the build.
- Demo: `TilesDemo` (twelve drawn stat tiles; ten return to a drawn stats screen, two rise away).

### Scene clock (`scene-clock.tsx`)

A hand-drawn analog clock in a top corner that carries a "day in the life" across scenes without words (the
film's breakfast-to-night run, which the owner asked for instead of a printed time).

- `SceneClock { s, from, to, P, at?, sweep?, enter?, hide?, ink?, face?, corner?, W? }`. Each scene passes its
  own range, `from` → `to` in minutes of the day (`hm('7:50')` = 470); give the next scene `from` = this
  scene's `to`, or the hands jump. Times past midnight go above 1440 and the hands keep turning forward.
- Film timing per scene: the clock fades in over 0.2 s (`enter`), the hands sweep over 0.05 to 0.6 s
  (`sweep`), then hold. `at` delays both to a later scene second (in four of the film's scenes the clock
  arrived after the scene's first beat, as late as 2.85 s in). `hide` (0..1) fades it under your control; the
  film faded it over 0.3 s in its last night scene, and with the phone as the phone left the frame.
- Placement: 36 px from the top-left of the layout area in portrait (52 x 44 px in 16:9), a 140 px disc (148 in
  16:9) with a 124 px clock (132). The layout area is the safe band in 9:16, so the clock clears the platforms'
  top bar. `corner: 'right'` mirrors it (pass `W`); keep it out of the right-hand button column in 9:16.
- The face "boils" (re-drawn with a 3.5% wobble) 12 times a second, from scene seconds, so it looks the same at
  any fps. `ink` defaults to the theme's ink; on a dark scene pass a light ink and a dark `face`.
- Demo: `ClockDemo` (three beats, 7:50 → 8:12 → 12:40 → 19:05, then hidden).

## Safe bands (`safe-band.tsx`)

TikTok, Reels and Shorts cover the top and bottom of a 9:16 frame with their own UI. At 1080x1920 the engine
lays every scene out in the band y 140 to 1620 (140 px off the top, 300 off the bottom; it scales with width)
and passes `c.H` = 1480. Backgrounds (`GradientWorld`, `PhotoWorld`, `EndCard`'s fill, anything inside
`<Bleed>`) extend past the band to the frame edges. A frame counts as 9:16 when H/W > 1.6; 16:9 and 4:5 have no
band. 9:16 stacks what 16:9 places side by side (Kallo's two cards: one above the other, scale 0.62).
`<Reel band={false}>` turns the band off for compositions no platform draws over (the store preview).

## Render pipeline (`render/`)

1. `node render/stills.mjs <dir> <seconds...>` (env `COMP`, `SCALE`) bundles once and renders PNG stills.
   `SCALE=0.5` renders half-size stills, enough to check layout. Render the beats, downscale (`sips -Z 800`),
   look, fix, repeat. A contact sheet of 8 to 12 stills per format is the review unit.
2. `bash render/master.sh <Comp> <name> [mix.wav]`:
   - Remotion renders PNG frames into ProRes 4444 (`--image-format png`), muted: the master.
   - x264 `-preset slow -crf 14 -tune grain -pix_fmt yuv420p`, AAC 256k from the mix: the upload file.
   - x264 crf 22 `-tune grain`: a light copy for chat apps and review links (some cap uploads near 30 MB;
     Kallo's 16:9 crf 14 master was 31 MB).
   - The picture sets the length. A mix shorter than the picture is padded with silence (`apad`, then `-t`
     the picture's length); a longer one is cut at the last frame with a warning (the cue sheet is out of
     date). Both MP4s are then checked against the master's frame count: video stream, audio stream and
     container must each be within one frame, or the script exits 1. (It used `-shortest` before, which cut a
     3 s render to 1 s under a 1 s mix.)

Why: the soft gradients banded into visible steps when frames went through JPEG and a default x264 encode.
PNG into ProRes keeps the master clean; `-tune grain` keeps the faint noise that dithers a gradient, so it stays
smooth at the same crf.

3. `bash render/store.sh [Store-886x1920] <name> [mix.wav]`: the App Store preview (below). Same ProRes master,
   then H.264 High, yuv420p, constant 11.5 Mbps (ffprobe reads about 10.7; Apple asks for 10 to 12), the
   composition's fps, stereo AAC 256 kb/s at 48 kHz (a silent stereo track when there is no mix). It then probes
   the file and exits 1 unless: H.264 High, yuv420p, the composition's exact size, at most 30 fps, 10 to 12 Mbps,
   AAC stereo 48 kHz at about 256 kb/s, under 500 MB, and 15 to 30 s long (skipped with `FRAMES=`, for a test
   range). Tested on a 3 s range (passed, 10.7 Mbps, 248 kb/s with a mix) and on the 7.4 s example (failed the
   length check, as it should).

Composition ids allow letters, digits and `-` only (`Film-45`, not `Film_45`).

### The store preview composition (`Store-886x1920`)

Opt-in: delete it if the film has no store cut. `src/film/Store.tsx` registers an App Store app preview at
886x1920 (iPhone with Dynamic Island or Face ID, portrait) and 30 fps (Apple's maximum). Apple takes only
screen captures of the app itself, so the frame is the app's screen: the recording fills it edge to edge
(scaled to cover; a 1320x2868 capture loses 2 px top and bottom), with no device body, no pointer, no camera
zoom into the UI and no safe band (`<Reel band={false}>`). Motion comes from the app and from the cuts.

The example reuses the Demo scene's segment list, bridge and patch, so the same cuts land on the same source
frames as in the 60 fps film. A real preview needs its own scenes array of full-screen cuts, 15 to 30 s,
recorded on the device class it is for; another class (iPad 1200x1600, older iPhones 1080x1920) is another
composition with that size. Store rules and the checklist: `branches.md`, Store preview.

## Pitfalls

- **Variable frame rate.** `simctl io recordVideo` and most screen recorders write a frame only when pixels
  change, so video time is not wall time and a still screen leaves gaps of seconds. A screen that never changes
  during a take never reaches the file: a 2.6 s recording of an idle simulator produced one frame. Remotion's
  `OffthreadVideo` mis-seeks on these sparse files. Convert every clip with
  `ffmpeg -vf fps=60 -fps_mode cfr` (`capture/vfr_to_cfr.sh`) before it goes into `public/rec/`. For a state that
  was static during the take, use a screenshot as a still.
- **A seek near a state change can land on either side.** `Clips` seeks in seconds (`segWindow`: the source
  second of each segment's first frame, passed as a fractional `trimBefore`), so the same scene second shows the
  same source frame at 30 and 60 fps. The decoder still shows whole source frames. Tested on a CFR 60 file whose
  card pops in at exactly 7.6 s: holds at source frames 455/456/457 showed before/after/after, and playback from
  7.5 s showed the card from its 6th frame on, so seeking is frame-exact. But a `src` within half a frame of a
  change can land on either side. Keep holds at least 2
  frames (0.035 s) clear of any state change, and pick the frame from a still, not from the log.
- **`/tmp` purges.** macOS deleted untouched files in a `/tmp` scratchpad under disk pressure (the disk was 93%
  full): sources, recordings, the SFX library, login state. Keep the film project in a real folder under your
  home directory from day one. If it happens, Remotion bundle folders
  (`$TMPDIR/remotion-webpack-bundle-*`) hold a full copy of `public/`, and their `.map` files' `sourcesContent`
  hold the TypeScript sources.
- **Low disk breaks stills.** With 3.5 GB free on a 460 GB disk, every still that showed a 1320x2868 video
  frame failed with `Failed to fetch ... disk space is low`; a 660x1434 copy rendered. Free space, or use a
  half-size copy for previews and the full one for the master.
- **Gradients band** through JPEG frames or default x264 tuning. Use the master pipeline above.
- **`NODE_OPTIONS` preloads** injected by some terminals break `npx remotion`; run it with `env -u NODE_OPTIONS`.
- **Non-ASCII typing.** Simulator automation sends US-keyboard events. Type through the language's own input
  method (Vietnamese: the Telex keyboard plus `capture/telex.py`), see the note in `telex.py`.
- **Taps that miss.** An overlay can swallow taps on part of a button (Kallo: the lower half of Save meal under
  the composer). If a tap does nothing, tap the control's top edge and check the frame.

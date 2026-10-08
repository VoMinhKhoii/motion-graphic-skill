# Capture: record the real product

The single most important product-truth rule: the UI in the film is the real build, recorded. A UI re-implemented in the film engine "looks broken" to the person who built the product, even when it is pixel-close. Record it.

## Pick the route first

Check what the session can drive before writing take sheets, and say it to the owner:

| Product | Route | Needs | Starter device preset |
|---|---|---|---|
| iOS app | iOS Simulator, `ios_sim_record.py` | macOS, Xcode, idb | `iphone` |
| Android app | emulator or device over adb, `android_record.py` | Android SDK platform-tools, an emulator image or a USB-debugging device | `android` |
| Web app, SaaS dashboard, B2B tool | headless Chromium, `web_screencast.cjs` | Node, Playwright | `browser` |
| Desktop app, or none of the above works here | user-recorded footage | the owner records to a spec | match the footage |

Set `PRESET` in the starter's `src/film/config.ts` to match. A web-only product gets the `browser` frame, never a phone around a page it does not have.

## Plan the takes

For each scene in the storyboard, write a take sheet:
- **Start state:** screen, account, data, time of day, locale.
- **Actions with timing:** tap, type, wait for result, scroll, tap Save.
- **End state, and what gets cut:** waits, spinners beyond two status words, stalls.
- **What must be real:** the numbers, the names, the text typed.

Record long, cut in the edit. A take can be 2 minutes for 4 seconds of film.

## Demo data

- Use a dev or staging environment, never production. Seed a believable account: a real-looking name, avatar, friends and history. Clear the day you will demo so gauges start empty.
- **Every number on screen comes from a real run.** If an AI pipeline is involved, run the real pipeline; results vary run to run, so record the run you show and quote its numbers.
- After the take, delete test data through the app's own UI (that exercises the real delete path), then verify in the database.
- Re-record pattern: if a take needs an empty day that already has meals, move those rows aside temporarily, record, then move them back.

## Record the original state, restore at delivery

Capture changes things that belong to the owner. In the worked example these stayed changed until sign-off: the film account's language and country (vi and Vietnam; they were en and US), the simulator's keyboards (Vietnamese Telex only; it had English and Vietnamese) with autocorrect, auto-capitalisation, spelling and smart punctuation off, one saved test meal, and a dev backend and debug build still running. Before the first change, write each original value down in `film/capture-state.md`. At delivery, put each one back and check it.

Gate, before the first change:
- [ ] Account: language, country or region, any in-app locale, and every field the takes will edit (name, goals, units).
- [ ] iOS Simulator: the keyboard list (Settings > General > Keyboard > Keyboards) and the four toggles (Auto-Capitalization, Auto-Correction, Check Spelling, Smart Punctuation), as they are now. The status bar override is cleared with `xcrun simctl status_bar booted clear`.
- [ ] Android: `android_record.py prep` saves the spell checker, show touches, pointer location, the demo-mode permission and the active keyboard to `<REC_DIR>/.prep.json` before it changes them. Gboard's own Auto-correction and suggestion strip cannot be read over adb: note them by hand.
- [ ] Test data: every record the takes will create, and every record they will change, move aside or delete.
- [ ] Anything left running (a dev backend, a debug build, a simulator).

Gate, at delivery:
- [ ] iOS: `xcrun simctl status_bar booted clear`; keyboards and toggles back to the recorded values.
- [ ] Android: `android_record.py unprep` restores the saved values (a setting that was unset is deleted again), switches back to the saved keyboard and leaves demo mode. Gboard by hand.
- [ ] Account fields back to the recorded values; test records deleted through the app, moved rows moved back (unless the owner wants them kept).
- [ ] Processes stopped, unless the owner wants them running.
- [ ] Tell the owner what was restored, and anything that could not be.

## iOS Simulator

Tooling: `xcrun simctl` plus `idb`; the helper is `scripts/capture/ios_sim_record.py`.
```bash
export SIM_UDID=<your booted simulator>
python3 ios_sim_record.py start take_en           # waits for "Recording started"
python3 ios_sim_record.py tap 146 886 log_tab     # idb points, logged with time
python3 ios_sim_record.py type "a chicken caesar wrap: …"
python3 ios_sim_record.py tap 396 883 send
python3 ios_sim_record.py stop                    # prints the event log
```

**Status bar:**
```bash
xcrun simctl status_bar booted override --time 12:30 --dataNetwork wifi --wifiBars 3 \
  --cellularMode active --cellularBars 4 --batteryState discharging --batteryLevel 100
```
`--batteryState charged` draws a green bolt; use `discharging` at 100.

**Keyboard:** turn these off in Settings → General → Keyboard: Auto-Capitalization, Auto-Correction, Check Spelling and Smart Punctuation. Otherwise "parmesan" becomes "Parmesan" mid-take. Writing the preferences with `defaults` did not take effect; use the Settings UI (it can be driven through accessibility).

**Typing:**
- Letter by letter, always. Word-by-word typing looks janky.
- `idb ui text` types one character at a time and only handles ASCII.
- For other scripts, add the language's keyboard layout and send its keystrokes. Vietnamese uses Telex: `dd`→đ, `aa`→â, `ow`→ơ, `uw`→ư, tone keys `s f r x j` straight after the vowel. `scripts/capture/telex.py` converts text to keystrokes. Make that layout the only keyboard for the take; idb can't press the switch shortcut.
- A hardware-keyboard simulator shows no on-screen keyboard, which is what you want in a product film.

**Locale:** many apps store the language in-app. Switch it through the app's own settings, not by writing preferences, because apps often write their stored locale back on launch. Also set the account's server-side language if the backend localises content.

**Time-dependent UI:** greetings like "Good evening" follow the device clock. If you must shoot a lunch scene at night, patch the greeting's hour in a local film-only build, never committed, or shoot at the right hour.

**Launching from Settings** leaves a "◀ Settings" back link in the status bar. Terminate the app, press Home, and launch it again.

**Tap targets:**
- Read element frames from the accessibility tree (`idb ui describe-all`) and tap inside them.
- Watch for overlays: one app's composer overlay swallowed taps on the lower half of a Save button that sat just above it. Tap the top edge (frame y + 5), and report it as a product bug.

**The recording is variable frame rate:**
- `simctl io recordVideo` writes frames only when the screen changes. Idle time is compressed, the first frame is the first change, and a static screen never appears.
- So:
  1. take a full-resolution screenshot of any static opening screen (Home) and use it as a still;
  2. convert every recording to constant 60 fps before editing (`scripts/capture/vfr_to_cfr.sh`), because Remotion's OffthreadVideo mis-seeks on sparse VFR files;
  3. find moments by looking at frames of the CFR file, not by wall-clock action logs, because idle compression shifts them.
- `scripts/research/activity.py` prints per-second screen activity by region (top, middle, bottom). Typing, row landings and taps show up as bands.

**Debug builds stall.** Simulator builds are debug builds. Expect 0.3–0.7 s freezes on saves and refetches, then several UI changes popping in one frame. Find them with `scripts/capture/frame_pts.py` (real frame timestamps and gaps), cut the stall in the edit, and bridge the pop with a short crossfade (see `engine.md`).

**Leaked UI:**
- A wrong time label, a debug banner or a stale value can be covered with a patch: a crop of the same UI from a clean frame, laid over the recording for a source-time range.
- Measure the crop from the real frames.

## Android emulator or device

Tooling: `adb` (Android SDK platform-tools); the helper is `scripts/capture/android_record.py`. It mirrors the iOS helper: one command per call, an event log with times. It has not run against a real emulator or device yet; its start checks and prep/unprep restore are tested against a stub `adb` (`scripts/capture/tests/check_android_record.py`). Run a 10 s test take first.
```bash
export ANDROID_SERIAL=emulator-5554                 # adb devices; needed when more than one is attached
python3 android_record.py prep                      # saves the current settings, then demo mode, spell checker and touch dots off
python3 android_record.py start take_en             # screenrecord at 20 Mbit/s; exits 1 (no state) if it did not begin
python3 android_record.py tap 540 2210 log_tab      # pixels, not points: adb works in screen pixels
python3 android_record.py type "a chicken caesar wrap"
python3 android_record.py key ENTER send
python3 android_record.py stop                      # pulls the file, prints the log
bash vfr_to_cfr.sh clips/take_en.mp4 film/engine/public/rec/take_en.mp4
```

- **Emulator:** a Pixel image from Android Studio's Device Manager records 1080x2400 (20:9), which is the starter's `android` preset. Use a Google APIs image, not Google Play, if you need `adb root`.
- **Status bar:** `prep` turns on System UI demo mode (`settings put global sysui_demo_allowed 1`, then `am broadcast -a com.android.systemui.demo -e command enter|clock|battery|network|notifications`): 9:41, full battery and signal, no notification icons. `unprep` exits it and restores what `prep` saved.
- **Keyboard:** autocorrect and the suggestion strip belong to the keyboard app. In Gboard, turn off Text correction > Auto-correction and Show suggestion strip by hand. `prep` turns off the system spell checker.
- **Typing:** `adb shell input text` is ASCII only and sends a whole string at once, so the helper sends one character per call (about 4 to 8 per second, because each call starts a process on the device). For accents, Vietnamese or emoji, install ADBKeyboard and make it the active keyboard; the helper then sends each character through it. That keyboard has no visible keys. If the film must show a keyboard with non-ASCII text, paste the text and cut the paste in the edit.
- **screenrecord limits:** 3 minutes per file (it stops by itself; `stop` warns), no audio, variable frame rate like simctl. Always convert with `vfr_to_cfr.sh`. Some emulators record 0.3 to 1 s of black first: wait a second after `start`.
- **Lag:** each `input` call takes 0.15 to 0.5 s to land. Time pointer taps to the frame where the app reacts (`frame_pts.py`, `research/activity.py`), never to the log time.
- **Coordinates:** adb pixels are recording pixels, so `fromPoints(DEVICE, x, y, 1)` (scale 1) maps them into the film. `adb shell uiautomator dump` gives element bounds in the same pixels.
- **Real device:** the same commands work over USB. Demo mode works on Pixels; some vendor skins ignore it, so clean the status bar in the edit with a patch.

## Web app

The Chrome DevTools Protocol screencast delivers frames at CSS pixels and ignores a context's device scale factor: a 1440 px viewport gives 1440 px frames, which is about 480p after zooming into the input. Fix:
- Launch Chromium with `--force-device-scale-factor=Z` and keep the viewport at the real window size (1440 × 900) with device scale factor Z (Z = 2 or 3). The frames come out at 2880 × 1800 for Z = 2, and the page still sees a 1440 px window, so its media queries, `innerWidth` and responsive layout are the product's own. The script checks `innerWidth` and stops if it differs.
- Do not fake it with a larger viewport plus `html { zoom: Z }`: the page then sees a 2880 px window and can switch to its wide-screen layout (tested: a `min-width: 1920px` rule fired).
- Launch Chromium with `--enable-gpu-rasterization --ignore-gpu-blocklist --enable-gpu`, plus `--use-angle=metal` on macOS only (the script picks by OS; `GPU=0` drops them all). That gave about 57 fps at 2× and 34 fps at 3× on an M-series Mac. A machine with no GPU (a Linux server, CI) manages far fewer frames: use ZOOM=1 there, or record on a laptop.
- Playwright must be resolvable from the script, not from the product repo: Node looks for `playwright` from the script's own folder upwards. Install it in the film workspace (`cd film/engine && npm i -D playwright && npx playwright install chromium`) and run with `PLAYWRIGHT=$PWD/node_modules/playwright`, or point `PLAYWRIGHT` at any existing install. The script says so and exits if it cannot load it.
- Keep each frame's real timestamp and lay down a constant-rate sequence: output frame k (time k/60) is the last frame captured at or before it. Do not use an ffmpeg concat list with per-frame durations: it quantises the times to 1/25 s and silently drops frames (tested: 152 distinct frames kept in 3 s at 60 fps with the sequence).
- Script: `scripts/capture/web_screencast.cjs`.
- Map browser coordinates to video coordinates: video px = CSS px × Z, plus any fake browser chrome you draw.

Type letter by letter with a per-key delay (about 45 ms). Record a separate typing-only take at higher zoom if the typing shot is a close-up.

## Web-only and desktop products

- **Web-only, B2B, dashboards:** record with `web_screencast.cjs` at the window size you will show (the starter's `browser` preset is a 1600x1000 page under a 76 px bar; change `w`/`h` in `BROWSER` to your capture). Keep the film's frame a browser window, or the bare page; no phone.
- **Seed the dashboard** like any demo account: real-looking rows, charts with history, no "test" or lorem text, no empty states unless the beat is about them.
- **Wide windows in tall formats:** a 16:10 window is small in 9:16. Plan close-ups (the starter's Demo scene zooms relative to the whole-window fit for the `browser` preset) or lift single components out with `CutOut`.
- **Desktop apps (Electron, native):** there is no scripted route here. Use macOS's own screen recording (Cmd+Shift+5, "Record Selected Portion" around the window) or OBS at 60 fps, and treat the result as user-recorded footage below.

## User-recorded footage

When the session cannot drive the product (no simulator, no emulator, a desktop app, hardware, an account the session must not touch), ask the owner to record. Send them this spec, word for word if useful:

- **Resolution:** native, no scaling: the simulator or device at full size, or the browser window at 2x (a Retina screen records at 2x already). Same window size for every take.
- **Frame rate:** 60 fps. On macOS, QuickTime and Cmd+Shift+5 record at the screen's rate; check with `ffprobe` and convert with `vfr_to_cfr.sh` anyway.
- **Clean screen:** a clean status bar (simulator status-bar override, Android demo mode, or a full battery and Wi-Fi with Do Not Disturb on), no notifications, no touch indicators, no cursor if the film draws its own pointer (hide it, or keep it still and out of the way), no browser extensions or bookmarks bar, a neutral desktop behind the window.
- **Data:** the seeded demo account; the real numbers you will quote.
- **A tap log:** for each take, the wall-clock time of each tap or key press (say "tap" aloud and record the mic, or note the time from a stopwatch on screen), plus what was tapped. The log tells you where to look; the frame where the app reacts is still found with `frame_pts.py`.
- **Long takes:** record each beat with a second of stillness before and after. Several short takes beat one perfect take.
- **No editing:** raw files only. Trimming, speed changes and compression happen in the film.

## Mobile on a real device

Device recordings have notification banners and touch indicators. If you must use one (for a camera feature, for example), clean the status bar by inpainting and then compositing simulator glyphs, and keep the device frame consistent with simulator shots.

## Camera features (scan, photo)

The simulator has no camera. Composite: a real photo of the product or label (shoot your own, or use openly licensed photos and credit them) inside the app's own scanner chrome, then cut to the real result sheet. Fill the viewfinder; no black void around the photo. Capture the chrome as the app's scanner screen with nothing in front of the camera (the simulator shows black) and screen-blend it over the photo: the starter's `Viewfinder` recipe does this (`engine.md`, Recipes).

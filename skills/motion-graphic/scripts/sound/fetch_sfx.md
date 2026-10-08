# Fetching the SFX

The catalogue (`sfx_catalog.md`) lists 15 Mixkit and 14 Pixabay sounds. Download them into a local folder that
is ignored by git (for example `lib/sfx/`), under the catalogue's file names. Never commit them.

## Mixkit: plain HTTP

Mixkit serves each sound at a stable asset URL. `curl` works, no login, no browser:

```bash
mkdir -p lib/sfx && cd lib/sfx
while read -r name id; do
  [ -f "$name" ] || curl -sfL -A "Mozilla/5.0" -o "$name" "https://assets.mixkit.co/active_storage/sfx/$id/$id.wav"
done <<'EOF'
click_mouse_1_mouse_click_close.wav 1113
click_mouse_2_clear_mouse_clicks.wav 2997
click_ui_3_modern_click_box_check.wav 1120
glitch_or_stutter_2_digital_glitch_break.wav 2951
heart_like_2_click_melodic_tone.wav 1129
impact_3_futuristic_bass_hit.wav 2303
keyboard_1_smartphone_typing.wav 1393
keyboard_2_laptop_keyboard.wav 2536
notify_2_success_software_tone.wav 2865
pop_3_dry_pop_up.wav 2356
riser_3_cinematic_trailer_riser.wav 790
whoosh_long_1_air_woosh.wav 1489
whoosh_long_2_cinematic_swoosh.wav 1481
whoosh_short_1_fast_whoosh.wav 1490
whoosh_short_2_fast_sweep.wav 174
EOF
```

To find new Mixkit sounds, browse `https://mixkit.co/free-sound-effects/<category>/` (click, whoosh, swoosh, pop,
notification, bass, glitch, type, keyboard, cinematic). Each card's preview player carries the asset URL.

## Pixabay: a real browser

Pixabay sits behind Cloudflare. `curl` gets HTTP 403 on the sound pages. What works:

1. Launch a real Chromium through Playwright, with the GPU on and the automation flag hidden:
   `args: ['--use-angle=metal', '--enable-gpu', '--disable-blink-features=AutomationControlled']`, a normal desktop
   Chrome user agent, a 1440x900 viewport, and an init script that sets `navigator.webdriver` to `undefined`.
   (`--use-angle=metal` is macOS; drop it elsewhere.)
2. Open `https://pixabay.com/sound-effects/<slug>/`. While the page title says "Just a moment", Cloudflare is
   checking; wait in 3 s steps, up to about 36 s.
3. Read the page HTML and collect every link matching
   `https://cdn.pixabay.com/download/audio/...mp3?filename=...`.
4. **Keep only the link whose `filename` contains the sound's id** (the number at the end of the slug, for
   example `467466` in `clean-minimal-pop-467466`). A sound page also lists related sounds, often before the main
   one, so the first link on the page is frequently the wrong sound.
5. Download that link with the page's own request context (`page.request.get(url)`), so the Cloudflare
   clearance cookies go with it. The CDN itself also answers plain `curl` once you have the right URL.
6. Wait about 4 s between pages. Skip files that already exist, so the run can be repeated after a failure.

After downloading, check each file: it decodes (`ffprobe -v error <file>`), and its duration is close to the
catalogue's. A wrong-sound download usually shows up as a different length.

If the automated browser is still blocked, open the pages in your own browser and press Download; the saved
file name ends in the same id, which is your check.

## Music

Music follows the same two routes (Mixkit `assets.mixkit.co/music/<id>/<id>.mp3`, Pixabay through a browser).
Read the music licence separately from the SFX one: Mixkit's Stock Music Free License excludes TV and radio
broadcast, games, and remixing into a music-only track, which the SFX licence allows. Platforms with Content ID
may flag some tracks; Pixabay's search data carries a `hasYoutubeContentId` flag per item, so prefer items where it is false. Paid libraries (Epidemic Sound and
similar) need an active plan at download time; do not start a trial on someone else's behalf.

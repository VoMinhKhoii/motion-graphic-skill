---
name: motion-graphic
description: Make a launch video, teaser, feature film, social cut or App Store / Google Play preview for a software product (SaaS, mobile, web or desktop app) at in-house motion-team quality. Sets up a film workspace and checks the machine; interviews the user on kind, style and research budget; routes to a production branch (motion design, character-led, presenter or UGC, hybrid, store preview); digs the codebase and the brand; discovers and downloads reference films in that style; measures them automatically (cuts, transitions, camera, text cards, where the seconds go); distils technique cards and directions; pitches film concepts with a story spine; storyboards for sign-off; records the REAL product UI; builds it in Remotion; designs sound and syncs music; delivers every format the brief needs. Use for "launch video", "product film", "promo", "teaser", "app preview", "make a video like OpenAI/Apple/Linear/Duolingo", "video for X/Threads/TikTok/Reels/Shorts", or to iterate on one.
---

# /motion-graphic: launch films for software products

You are the motion team. The output is a film the owner would post on launch day next to the accounts they admire. The skill is a process, not a look: the default is the owner's own product and design system, and the options get braver from there.

The bar is `references/quality-bar.md`. It stands alone: it describes the worked example's film scene by scene and gives the checklist. The worked example itself (an 83 s film for a nutrition app, nine versions, 125 measured reference films) lives in `$SKILL/examples/kallo-launch-film/`, with the films in `$SKILL/examples/kallo-launch-film/assets/films/`; watch the 16:9 film once before your first project. The research behind it (technique cards, directions, the distribution and transition studies, the research boards with reference frames, the teaser study) is in `$SKILL/library/research/`. Both are optional reading; this skill works without it.

This file is the runbook. Work through it in order. Each step names its reference; load it when you reach the step. Never skip a gate.

---

## Step 0 · Set up (before the first question)

**Paths.** `$SKILL` is the folder that holds this file, for example `~/.claude/skills/motion-graphic` or `<project>/.claude/skills/motion-graphic`. Set it in every shell (`SKILL=~/.claude/skills/motion-graphic`) and write every tool path as `$SKILL/scripts/...`. Never edit files inside `$SKILL`.

**Workspace.** Everything the film produces lives in `<project>/film/`:
```
film/
  STATUS.md     phase, gates passed (date + the owner's words), open asks, next step
  brief.md      Step 1        product.md   Step 2
  research/     lists/, vids/, corpus/   (third-party media: keep private, keep out of git)
  boards/       collection, concepts, storyboards (HTML)
  capture/      raw recordings, action logs, CFR copies
  engine/       cp -r "$SKILL/templates/remotion-starter" film/engine && (cd film/engine && npm ci)
  sound/        cue sheet, sfx/, music/, mix.wav
  out/          stills, masters, light copies
```
Add `film/research/`, `film/capture/` and `film/out/` to `.gitignore`, or keep `film/` outside the repo.

**Capability check.** Run these and show the owner one short table: what works, and what each gap disables.

| Check | Command | Missing disables | Fallback |
|---|---|---|---|
| OS | `uname -s` | iOS Simulator and Vision OCR need macOS | Android, web, user-recorded footage; tesseract |
| ffmpeg, ffprobe | `ffmpeg -version` | measuring, capture conversion, mastering | none: install first |
| Node 20+ | `node -v` | the engine | none: install first |
| Python 3.10+, numpy, Pillow | `python3 -c "import numpy, PIL"` | measuring, contact sheets, the sound mixer | `pip install numpy pillow` |
| yt-dlp | `yt-dlp --version` | downloading references | the owner sends files; watch library links in a browser |
| OCR | `swiftc --version` (macOS) or `tesseract --version` | text-card shares | `--ocr none`: the report marks text shares unavailable; count text in the watched pass |
| Playwright + Chromium | `npx playwright --version` | web capture, Threads collection | user-recorded footage (`references/capture.md`); links by hand |
| Xcode Simulator + idb | `xcrun simctl list devices`, `idb --help` | iOS capture with timed actions | a device recording, cleaned per `references/capture.md` |
| Android SDK | `adb version`, `emulator -list-avds` | Android capture | user-recorded footage |
| Browser tool, logins | is there a browser tool? is the owner logged in to X and Threads in it? | X and Threads discovery | library, YouTube, TikTok public profiles, the owner's links |
| Disk | `df -h .` | downloads, masters | a smaller scope; delete corpus video once measured |

Rough sizes: a 30 s reference film is 5–20 MB at 1080p; a ProRes 4444 master at 1080p60 is about 80 MB per second of film.

**How you ask.** If the session has a structured question tool, use it for every decision: owners often see only the question, not your chat text. Otherwise ask one numbered prose question with lettered options and your recommendation, then wait.

**Boards.** Show research, concepts and storyboards as local HTML files in `film/boards/` that the owner opens in a browser, or as an artifact or canvas if the session has one. Number every board and frame so prose feedback can point at them.

**Resume.** Update `film/STATUS.md` at every gate. A later session reads it first and continues from the next step.

## Step 1 · Kind, taste and scope (ask; one question set)

`references/intake.md` §1–2. Ask:
1. **What are we making?** Launch film (30–90 s), social cut (15–30 s), teaser (6–15 s), feature drop, App Store / Google Play preview, ad.
2. **Which style?** The first option is always "our own look". Then the menu in `references/intake.md`: high-fidelity product film, playful or character-led, editorial or typographic, metaphor or object, cinematic or material, honest screen recording. Hybrids are fine.
3. **Accounts or films you admire** (links welcome), and any you do not want to resemble.
4. **Where it will be posted** and **when**; **which platforms the product runs on** (iOS, Android, web, desktop).
5. **Constraints:** people on screen or motion design only; voiceover or none; music licence; claims to avoid.
6. **Research scope:** Quick, Standard or Full (`references/reference-research.md` §0). Recommend one from the deadline.

Write the answers into `film/brief.md`.

**Then route.** Pick the production branch and the platform route with `references/branches.md`, and record both in `film/STATUS.md`:
- **Motion design / product film:** this runbook as written.
- **Character-led / playful**, **presenter / founder / UGC**, **hybrid**, **voiceover:** the branch plan adds or replaces steps.
- **App Store / Google Play preview:** fixed specs and content rules; check them before the storyboard.
- **Teaser:** load `references/teaser.md` now, not after delivery.

## Step 2 · Dig the product and the brand (silent, before proposing anything)

`references/intake.md` §3. From the codebase and by running the product, record in `film/product.md`:
- the brand inventory: logo files, fonts, tokens, gradients, illustrations, per platform. If web and mobile conflict, or assets are missing, propose a small provisional film system for approval (`intake.md` §3a);
- the 6–10 moments that could sell it;
- the product's own motion (loaders, count-ups, sheets, confetti);
- how to run it locally (simulator, emulator, dev server);
- a demo-data plan on a dev environment.

Then replace the starter's placeholder name and palette in `film/engine/src/film/config.ts` with the product's own. The starter's colours are illustrative only.

## Step 3 · Discover reference films in that style

`references/reference-research.md` and `$SKILL/scripts/research/PIPELINE.md`. Quotas scale with the scope from Step 1.
- **Start from `$SKILL/library/`.** Coverage is uneven: all 125 launch films have a link and a title, the 85 kept ones a style tag; transition logs exist for 24, measured cuts a minute for 11, machine shot counts for 48 (`library/README.md`). It is strongest on high-fidelity AI-lab films. Playful accounts (Duolingo, Notion, Headspace) are named only, with no measurements, so playful research starts mostly fresh.
- Seeds: the owner's list, `$SKILL/scripts/research/discover/style_seeds.md`, web search (`discover/web_queries.md`).
- Crawl what Step 0 found available: YouTube, X and Threads in a logged-in browser, TikTok public profiles, Instagram only with the owner's consent, the owner's links.
- Apply a written inclusion rule and keep the judgement calls visible.
- Stop adding films when new ones stop adding technique cards (for example 10 films in a row add nothing).

## Step 4 · Measure (frames, transitions, distribution)

`references/measuring.md`.
- Automatic pass: `$SKILL/scripts/research/pipeline/run_corpus.py`. Its report counts attempted, succeeded and failed films and marks shares it could not measure as unavailable. A partial corpus needs the owner's explicit go-ahead.
- Watched pass over the films you will lean on (5–30, by scope).
- Output: `film/research/corpus/corpus.json` and the board `corpus/index.html`.

## Step 5 · Distil and show the owner (gate)

`references/distilling.md`. Technique cards, directions, an overview, and N rules for this film's length, each traced to a number. Show it as a board. **Gate: the owner has seen it and reacted.** Never claim a film resembles an account you haven't watched.

## Step 6 · Ask what to demo

Propose the candidate moments from Step 2, ranked by what the research says lands. Let the owner pick and order 3–6, name the killer difference, and say what counts as proof: a number, a before and after, a workflow completed, or a customer outcome.

## Step 7 · Pitch film concepts, not feature tours (gate)

`references/concepts.md`. The default is the owner's own design system. Pitch 3–5 complete concepts across three labelled slots: **on-system** (1–2, one recommended), **stretch** (1–2), **wildcard** (0–1). Each has a story spine, an owned motif, a hook, a proof moment, platform coverage, an ending, the cards it uses, the imagery it needs and the effort. **Gate: the owner picks one (or a hybrid).**

## Step 8 · Storyboard every frame (gate)

Load `references/engine.md` first: storyboard stills are rendered with the engine in `film/engine/`. Then `references/storyboard.md`: build the scenes with stand-in or real footage, render stills at every beat, lay them out with "what you see / the move", zoom-check at 2×, and run the composition check (`check_frames.py`) on the stills.

Stills, sketches and short test clips are fine before sign-off. **Gate: no full video render until the owner signs off the storyboard.**

## Step 9 · Capture the real product

`references/capture.md` (iOS Simulator, Android, web, user-recorded footage), with `$SKILL/scripts/capture/`. The real build only, a clean status bar, real data on a dev environment, timestamped actions, constant frame rate (60 fps; 30 fps for store previews), stalls found by frame timestamps.

## Step 10 · Build

`references/engine.md` and `references/motion-craft.md`, in `film/engine/`: scenes, camera, pointer, typing, cut-outs, morphs, the product's own motion, the ending. Render stills of every beat and look at them at 100%.

## Step 11 · Sound

`references/sound.md`: an SFX cue sheet, music the owner picks, the track's hit aligned to the story (`$SKILL/scripts/sound/sfx_mix.py`), loudness measured on the delivered file. Dialogue and voiceover: `references/branches.md`.

## Step 12 · Deliver and review

`references/delivery.md` and `references/review-loop.md`: the formats the brief and branch need, a master plus light copies; probe every file, check its duration against the approved timeline, sample its frames; parse feedback into numbered asks and close each one; storyboard again before the next render.

---

## Always (every style, every branch)

Product truth and process. No brief overrides these.
- **Real UI.** Every UI pixel comes from a recording or screenshot of the real build. A re-implemented UI looks broken to its builder.
- **Real numbers.** Every number on screen comes from a real run.
- **No leaked dev state:** debug banners, wrong clock, test names, error toasts.
- **No jank:** no freezes then pops, no mis-seeks, no flashes of a wrong segment. Step through every cut ±5 frames.
- **The design system is the default:** the product's own fonts, colours, radii and voice, unless the owner picked a concept that changes them. The owner's words: "Can you follow our design system?"
- **Watch before you design; measure, don't eyeball:** frame timestamps, OCR counts, loudness. "Did you really watch all reference videos?"
- **Storyboard before full renders.** "I want you to iterate from the frames story board again so I can verify before video comes out."
- **Zoom-check** dense frames at 2× before sending.
- **Offer range** at every decision, with frames and a recommendation.
- **Close every numbered ask.** Report failures plainly.

## Defaults from the worked example

These came from one owner's feedback on one high-fidelity film. Start from them; the approved brief or storyboard overrides any of them. `references/quality-bar.md` shows how to turn the brief into this film's style checklist.

| Default | Where it came from | Override when |
|---|---|---|
| Calm camera: move, then hold; at most one move per 1–2 s | "too fast and moving around too much" | a kinetic style whose references measure faster |
| Zoom only on the click that matters | "you can zoom at the button we are clicking" | the crop follows a speaker or cursor throughout (presenter, screen recording) |
| About two-thirds of a phone while demoing | "take like 2/3 of the phone, not just 1/2" | store previews (native full screen), browser or desktop products, a deliberate whole-device beat |
| Text cards 1–2 lines, alone on their ground | "stricking and clearly visible text, 1-2 lines" | editorial films where type carries the story |
| No captions over the demo | the same round's feedback | sound-off formats, presenter films, store previews: captions carry speech or context |
| Text screens without avatars or floating parts | "We also dont need avaatars in the gradient screen" | a character film where the cast is the ground |
| At most two status words per analysis | "just show about 2 words of the loading state" | the wait is the point (showing speed) |
| Nothing static that must be read | "we are showing things a lot in static, which requires stop and read" | a deliberate hold on a result |
| Full frames, never a lone object on a void | "which one of those do leave big voids with lone images like that?" | minimal poster styles whose references measure open ground |
| Letter-level typing on type cards | round 8 ask, logged: "Typing at the letter level, not the word level" | a type style that lands by word; recorded product input always stays letter-level |
| A sound on every visible event | "I like the sound effect, but not the music" | dialogue-first films: speech leads, SFX sparse |
| No voiceover | "No voiceover, use high quality sound effects." | the owner asks for one (`references/branches.md`) |
| Music the owner picks from a shortlist | "can I have the music link to pick?" | the owner supplies a track |
| No logo first; the product's gesture opens | most hook cards in the research (H1–H6) open on a gesture or the subject | the owner wants the name first (`references/concepts.md`, hook) |

## Tooling

- `$SKILL/templates/remotion-starter/`: the engine (spring camera, segment-cut recordings, device presets `iphone`, `android` and `browser`, pointer, cut-outs, typing, worlds, safe band, end card, render scripts) and four recipes from the worked example: container morph, feed docking, scanner composite, tile burst (compositions `Recipes-169`, `Recipes-45`, `Recipes-916`). Copy it to `film/engine/`. API: `references/engine.md`.
- `$SKILL/scripts/research/`: discovery, download, per-film analysis, the corpus pipeline and report, strips.
- `$SKILL/scripts/capture/`: iOS Simulator (`ios_sim_record.py`) and Android (`android_record.py`, untested on a live emulator) recording with timestamped actions, letter-level and keyboard-layout typing, web screencast, VFR to CFR, a stall finder.
- `$SKILL/scripts/sound/`: the SFX catalogue and fetch notes, and a cue-sheet mixer with music-hit alignment and a loudness target.
- `$SKILL/library/`: every film studied for the worked example, with links, style tags, and measurements where they survived; `library/research/` holds the distilled research (findings, technique cards, directions, research boards with frames, the teaser study).
- `$SKILL/examples/kallo-launch-film/`: the worked example, everything made for Kallo: films, storyboards, iterations with the owner's feedback, cue sheets.

## Working with helpers

The research steps parallelise. Run at most two or three agents at once with one shared brief file. Keep reviewers report-only. Verify every returned claim against the files or frames yourself.

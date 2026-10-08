# Intake: the brief, the taste interview, the codebase dig

The goal of intake is a one-page brief the owner has confirmed, plus a list of the 3–5 product moments the film must sell. Everything downstream (which accounts to research, which directions to propose) depends on the taste answer, so get it explicitly.

## 1. The taste interview

Ask as one structured question set (multiple choice plus "other"). Do not guess the style from the product category.

**Style menu.** The first option is always the default: **"Our own look"**, meaning the product's current design system and brand, art-directed. Then offer these, with one or two named examples each, and let the owner pick one or a hybrid. Whatever they pick, the film stays in their design system unless they choose a stretch or wildcard concept later (`concepts.md`).

| Style | What it feels like | Where to look (examples, verify they are still current) |
|---|---|---|
| Our own look (default) | The product's fonts, colours, gradients and motion, at their best | The product itself, its landing page, its App Store screenshots |
| High-fidelity product film | Real UI at hero scale, calm camera, typed lines, one accent colour, silence before the name | OpenAI, Anthropic/Claude, xAI, Manus, Linear, Raycast, Arc/The Browser Company |
| Playful / character-led | Mascots or brand primitives acting out a rule, bouncy timing, bright colour | Duolingo, Notion, Figma, Headspace, Arc's early films |
| Editorial / typographic | Big type carries the story; UI appears as evidence | Stripe Sessions, Vercel, Apple keynote openers |
| Metaphor / object | Everyday objects stand in for the product; no UI until the end | Samsung "What's coming?", teenage engineering, Nothing |
| Cinematic / material | Macro footage, rim light, music-led cuts | Claude model teasers, OpenAI DevDay stings, Nothing hardware |
| Screen-recording honest | A real demo, tight crops, cursor tracking (Screen Studio look) | Indie launches, Raycast extensions, Cursor |

Then ask:
1. **Accounts or films they admire** (2–5). Links if they have them. These seed the research corpus.
2. **Accounts they do not want to resemble.** Saves a round.
3. **Pace:** calm and premium, fast and punchy, or "fast but readable".
4. **People:** motion design only, or are hands, faces and live action allowed? In the worked example "motion design only" removed 40 of 125 reference films. Someone speaking to camera routes to the presenter branch (`branches.md`).
5. **Voiceover:** none is common for social, but narration is a valid choice; it adds a script, recording and captions (`branches.md`). Captions whenever speech matters and viewing may be sound-off.
6. **Music:** do they have a licence (Epidemic Sound, Artlist)? Otherwise royalty-free (Pixabay, Mixkit, CC0) chosen from a shortlist you prepare.
7. **Research scope:** Quick, Standard or Full (`reference-research.md` §0). A same-week teaser is Quick.

The answers pick a production branch: motion design, character-led, presenter or UGC, hybrid, or store preview. `branches.md` has each branch's plan.

## 2. The job of the film

- **Kind:** launch film (30–90 s), social cut (15–30 s), teaser (6–15 s), feature drop, App Store / Google Play preview (fixed specs and content rules: `branches.md`), ad.
- **Platforms and aspect ratios:**
  - X and Threads: 4:5 or 16:9.
  - TikTok, Reels, Shorts: 9:16, with safe zones.
  - YouTube and the website: 16:9.
  - Store previews: the store's own sizes per device class (`branches.md`).
  - Plan every aspect from day one; laying out for all three later is cheaper than reframing.
- **Must-show features** and **killer differences.** Ask what a competitor cannot show.
- **Claims to avoid:** pricing, dates, unreleased features, health or finance claims.
- **Deadline and posting slot.** Teasers go out 1–3 days before launch.

## 3. The codebase and product dig

Before proposing anything, learn the product from its source and from running it.

- **Design system:** fonts and their files, colour tokens, radii, the icon set, dark mode, and the voice (sentence case? emoji?). Use the product's own fonts in the film.
- **Core flows:** find the 3–5 moments that sell it.
  - Look at the routes and screens, the onboarding, the empty states, the "aha" interaction.
  - In the worked example: typed meal → itemised result; barcode and label scan; a social Circle feed; relog; sharing a meal; micronutrients.
- **Real data:** what will be on screen? Plan a demo account and seed data on a dev environment, never production. Every number shown must come from a real run.
- **Run it:**
  - Can you launch the app in a simulator or emulator and the web app locally?
  - Which states are slow or flaky (network, AI calls)?
  - Note the hooks you will need: status bar override, locale switch, time of day, autocorrect.
- **Where the product's own motion lives:** loading states, count-ups, sheets, confetti. These become the film's transitions.
- **Assets you may use:** the logo and wordmark files, product photography, mascot art.

### 3a. Brand inventory

List the authoritative assets, per platform, in `film/product.md`:

| Asset | Where it lives (path or owner) | Web | iOS | Android | Conflicts or gaps |
|---|---|---|---|---|---|
| Logo, wordmark (vector) | | | | | |
| Fonts (files and licence) | | | | | |
| Colour tokens, dark mode | | | | | |
| Gradients, backgrounds | | | | | |
| Illustrations, mascot | | | | | |
| Icon set | | | | | |

"Authoritative" means the file the product ships, not a screenshot. If two platforms disagree (a different font on web and mobile, two greens), or assets are missing, do not pick silently. Propose a **provisional film system** and get it approved before the concepts:
- at most 2 fonts: the product's UI font plus, if needed, one display face the brand already uses;
- a palette taken from the logo and the product's main screens (sample the pixels), with one accent;
- one ground: a gradient or a flat colour built from that palette;
- show it as one board: type specimen, swatches, the ground, one frame with real UI on it.

The starter's palette and name in `film/engine/src/film/config.ts` are placeholders. Replace them with the approved system before the first storyboard still; never let them become the film's look by default.

## 4. The brief (write it, get it confirmed)

```
Product:        one line
Film:           kind, length, platforms + aspect ratios
Taste:          chosen style + admired accounts + anti-references
Must show:      3–5 moments, in priority order
Proof:          a number, a before/after, a workflow completed or a customer outcome; real UI; demo data plan
Constraints:    people on screen?, voiceover?, music licence, claims to avoid
Branch:         motion design / character / presenter / hybrid / store preview; platform route
Research:       Quick / Standard / Full, and what discovery access exists (Step 0)
Deliverables:   masters, light copies, aspect variants, captions/credits
Sign-off:       who, and at which gates (collection, storyboard, final)
Deadline:       date + posting slot
```

## 5. Expectations to set

- The first deliverable is research and a collection of techniques, not a video. Say so.
- Stills come early; every full video render waits for storyboard sign-off.
- Expect three or more rounds. The worked example took nine film versions and three teaser versions over a week. Each round's feedback is in `examples/kallo-launch-film/03-iterations.md`.
- Agree the production budget next to the research scope and write both in `film/brief.md`: how many storyboard and render rounds are planned before launch (for example two storyboard passes and two renders for a teaser, three and four for a launch film), and the date each gate must close. When a round would break the deadline, say so and offer to cut scope rather than quality.

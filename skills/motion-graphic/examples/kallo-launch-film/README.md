# Worked example: the Kallo launch film

> This listing is the lean build of the skill. The media of the worked example (the film, the 63-board Kallo storyboard archive and the teaser study page) are in the full repository: https://github.com/VoMinhKhoii/motion-graphic-skill/ (install from there with `npx skills add VoMinhKhoii/motion-graphic-skill` or the plugin marketplace to get them).


One full run of the launch-video process, from the brief to the delivered films, for a real product. It is told as it happened, wrong turns included, because the wrong turns are where most of the method came from.

This is evidence of the method, not a style to copy. Kallo's owner asked for one particular taste. Your product and your taste will lead to different references, different cards and a different film. What should carry over is the order of the work and the checks.

## What Kallo is

Kallo is a text-first nutrition tracker for iOS and the web. You type what you ate in plain language ("two slices of sourdough toast with half an avocado, a fried egg in a teaspoon of olive oil, and a flat white with oat milk"), and it breaks the sentence into ingredients, matches each against food-composition databases, estimates the portions, and returns calories, macros and micronutrients, row by row. The more detail you give, the closer the number. It also reads barcodes and nutrition labels, lets you relog a past meal, split a shared meal between friends, and follow friends' meals in a feed called Circle. The app ships in English and Vietnamese and is meant for a global audience.

## The brief

From the owner, on 30 September 2026:

| | |
|---|---|
| Length | 15–25 s at first. Released later: "30s or even more is good if you make it super cleans, eye catching and visually appealing". The final film is 83.1 s. |
| Platforms | X and Threads. A 9:16 cut for TikTok, Reels and Shorts was added at the end. |
| Voice | No voiceover. "High quality sound effects." |
| Content | The killer and main features, the difference from other trackers, and "the fact that we have both IOS + web fully functional". |
| People | None. Motion design only: no live action, no hands, no people in the imagery. |
| UI | Added after the first full cut: every UI pixel must be the real app, recorded, not rebuilt. |
| Audience | Global. The owner had to repeat this; default examples must not lean on one country's food. |
| Bar | "the launch video on X that receive complements from even senior motion designers". |

## The taste

**High-fidelity product film, like the frontier AI labs.** The owner named four accounts: OpenAI, Claude (Anthropic), xAI and Manus, and asked for "clean and high fidelity on both typography and visual". That choice decided everything downstream: which films were studied, which techniques were measured, and what "good" meant in review. A user who wants a playful, character-led film would start from different accounts and end with a different film through the same steps.

## Timeline at a glance

| Date | Step | Result |
|---|---|---|
| 30 Sep | Brief. First storyboards, drawn without watching the references. | Rejected. |
| 30 Sep | 125 reference films downloaded and analysed by script. Storyboards redrawn. | Rejected again: "you never watch those videos … never distill any design direction". |
| 30 Sep | Films with people filtered out (85 kept). 92 measured technique cards, 10 directions. | Accepted as the reference base. |
| 30 Sep | Five film concepts, K1–K5. | The owner picks K3 "One day": the colour of the light tells the time of day. |
| 30 Sep–1 Oct | Overnight build, v1 to v4, three rounds with two report-only AI advisors. | Advisors: ship. Owner: "not that peak"; the UI was rebuilt and looked broken. |
| 1 Oct | Distribution study (how the films spend their seconds). v6 from real recordings. | "Its now super good." |
| 1 Oct | v7: pointer tracking, component morphs, more text, music bed. | Long list of notes; music rejected. |
| 2 Oct | v8 applies every note. | "We have lost some of that elegant look". New rule: storyboard before every render. |
| 2 Oct | v9 storyboard, three passes, then the render. | Signed off. |
| 5–6 Oct | v9b–v9d: letter-level typing, a sharp 60 fps web capture, the owner's music, the credit line removed. A 9:16 cut. | Final film. |
| 6–7 Oct | Teaser study (25 teasers, a reveal ladder), the owner's own flow, English and Vietnamese cuts. | Final teasers. |

The final film, scene by scene (83.1 s):

| Start | Scene |
|---|---|
| 0.0 s | Opening: "Introducing Kallo", the line "The text-first nutrition tracker, built for precision.", a careless meal typed and analysed (259 kcal), "Kallo pays attention to details that matter.", the same meal typed in detail (504 kcal), the two cards side by side, "+245 kcal" |
| 21.35 s | "From barcode scanning…", then a barcode scan |
| 25.8 s | "…to nutrition label reading.", then a label read from a photo of a real tin |
| 32.05 s | The phone becomes a browser: a lunch typed, sent and saved on the web |
| 45.05 s | "At Kallo, we believe every journey works out better when we all feel supported. Especially dieting." |
| 48.1 s | Circle: friends' posts drop in, a like, group tabs |
| 54.6 s | "We make it easy for you to relog a meal.", then a relog |
| 61.0 s | "Want to share a meal?", then a pizza split between friends and shared |
| 75.3 s | "Not just calories and macros.", the micronutrient tiles burst into a wall and fly home |
| 79.1 s | Home, the wordmark, "Try it now" and the URL |

## Deliverables

| File | Format | Length |
|---|---|---|
| `assets/films/kallo_v9d_16x9_light.mp4` | 1920x1080, 60 fps | 83.1 s |

This is the "light" copy (x264 CRF 22). The same film was also delivered at 4:5 (1080x1350) and 9:16 (1080x1920), and the teaser as two 9:16 cuts (English 12.4 s, Vietnamese 10.6 s); those are left out to keep the skill small, and the storyboard archive shows their frames. The masters were x264 CRF 14 from a ProRes 4444 render and are not included. Storyboard frames and the six generated room backgrounds are listed in [assets/README.md](assets/README.md).

## The files

1. [01-research/corpus.md](01-research/corpus.md): what was collected and how: 125 films, the motion-design-only rule, the three measurement passes.
2. [library/research/findings.md](../../library/research/findings.md): the eight things nearly all of them do, where the seconds go, the transition mix, twelve exemplar moves, nine rules.
3. [library/research/technique-cards.md](../../library/research/technique-cards.md): all 92 technique cards, grouped by role, each with a measured recipe and its source.
4. [library/research/directions.md](../../library/research/directions.md): the ten directions built from the cards.
5. [02-concepts/film-directions.md](02-concepts/film-directions.md): the five film concepts and why K3 won.
6. [02-concepts/advisor-review.md](02-concepts/advisor-review.md): the three advisor rounds on v1–v4, and what they missed.
7. [03-iterations.md](03-iterations.md): **start here if you read one file.** Every round from v1 to v9, the 9:16 cut and the teaser, with the owner's feedback quoted, and the lessons.
8. [04-teaser.md](04-teaser.md): the teaser study, the reveal ladder, the owner's flow, the timings and the music alignment.
9. [05-sound.md](05-sound.md): the effects vocabulary and placement rules, the music decisions, the mix.
10. [06-production-notes.md](06-production-notes.md): capturing a real app for film: simulator and browser lessons, stalls, variable frame rate, and recovering from a purged temp folder.
11. [artifacts/](artifacts/README.md): the working pages themselves, offline: the 82-board storyboard canvas (references, concepts, every storyboard pass, the teaser), the teaser study and the launch intros. Open `artifacts/storyboard-canvas/index.html` to see what the owner saw at each decision.
12. [library/](../../library/README.md): every reference film studied, as links and measurements.

## A note on quotes and sources

The owner's feedback is quoted as written, typos included, trimmed to the lines about the video. Reference films are named and, where a public link is known, linked; no frames, audio or footage from them are included. Numbers about the references come from the study's own measurements.

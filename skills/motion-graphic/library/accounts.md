# Accounts by style

Every account studied for the worked example, what it is good for, and the numbers we measured on it. Styles follow the menu in `references/intake.md`. Film-level rows are in `launch-films.csv`, `google-films.csv` and `teasers.csv`.

How the numbers were made:
- **Length:** median duration of the films downloaded from the account (all, and the ones kept under the "motion design only" rule). Source: the post listings, `launch-films.csv`.
- **Cuts a minute:** the measured pass, every hard change in the picture at 4 fps, median per account. Source: `research/findings.md`.
- **Designed transitions a minute, demo share, text share:** the watched pass, 6 films per lab account and 8 Google films logged second by second. Demo share is the share of runtime with the product on screen. Text share is standalone text cards. Recomputed from the logs for this library.
- **Views:** median views of the kept films on 30 September 2026.

## The four lab accounts (high-fidelity product films)

| Account | Films (kept) | Length, all / kept | Cuts a minute | Designed transitions a minute | Demo share | Text share | Kept views, median |
|---|---|---|---|---|---|---|---|
| [Claude](https://x.com/claudeai) | 31 (23) | 52.2 s / 52.2 s | 16.5 | 13.5 | 71% | 14% | 12.9M |
| [OpenAI](https://x.com/OpenAI) | 32 (21) | 44.1 s / 30.0 s | 5.7 | 16.0 | 71% | 14% | 5.1M |
| [Manus](https://x.com/ManusAI) | 31 (24) | 31.4 s / 28.5 s | 13.6 | 19.7 | 65% | 6% | 99K |
| [xAI](https://x.com/SpaceXAI) (posted as SpaceXAI) | 31 (17) | 25.6 s / 19.2 s | 1.9 | 16.4 | 59% | 14% | 8.8M |

What each is good for:
- **Claude.** Real UI recomposed at poster scale on warm paper or patterned pastel grounds, a big cursor, serif lines between shots (direction D2). Also the archival cut-out numerals for model launches (D3), macro horizon match-cuts (D4, *Opus 5.5*), drawn ideas that become the UI (D8) and 8-bit mascots (D7). The fastest cutter of the four.
- **OpenAI.** The typed-headline system on white: one bold line typed at 20–34 characters a second, one rebuilt component at hero scale, a dot that carries the cuts (D1). Also frosted phone slabs in gradient worlds (D5), sunrise and cosmos light stories (D9) and glyph-face character casts (D7).
- **Manus.** Many short feature films from one template: dot-grid grey canvas, prompt card, rebuilt result, one continuous camera (D1). Also the poster loops for small updates (D10) and a device-shape morph (*Manus Desktop*). The best source when the film must be cheap and repeatable.
- **xAI.** Dark instrument films: idle dots that turn into live bars, grey words that snap to white, one accent colour, the product's own sound (D6). Also the light caret system of *Grok 4.5* (D1) and fluid-gradient partner loop cards (D10). Few cuts; motion lives inside the frame.

Styles inside these accounts (from direction membership, `launch-films.csv` column `style_tags`):

| Style | Films | Accounts |
|---|---|---|
| High-fidelity product film | 54 | all four |
| Editorial / typographic | 32 | all four (D1 typed films, D10 loop posters) |
| Screen-recording honest | 13 | all four (captured terminals and web apps) |
| Playful / character-led | 12 | Claude, OpenAI, Manus |
| Cinematic / material | 8 | all four |
| Metaphor / object | 3 | Claude (cut-out numerals) |

## Google (motion vocabulary only)

| Account | Films | Watched | Length, watched films | Cuts a minute | Designed transitions a minute | Demo share | Text share |
|---|---|---|---|---|---|---|---|
| [Google](https://x.com/Google) | 38 measured | 8 | median 55.2 s (8.0–98.7 s) | 3.7 | 11.8 | 58% | 5% |

Good for: title splits that open onto the first UI card, blur pull-backs, one hue per chapter in carousels. The owner's limit: "Google is more on a slow side. I want fast. Just a reference for possible kinds of motion." Take its moves, not its pace.

## Teaser accounts

From the 25-teaser study (`teasers.csv`). Lengths are of the teasers we downloaded.

| Account | Teasers | Length range | Good for | Ladder rung |
|---|---|---|---|---|
| [Samsung](https://www.youtube.com/@samsung) | 10 | 8.0–17.0 s | Metaphor teasers: one everyday object, one cut, one 3–4 word line at 62–79% of the runtime | 2 |
| [Nothing](https://www.youtube.com/@NothingTechnology) | 3 | 8.0–38.7 s | Mystery (abstract dots) and partial crops | 1, 3 |
| [CMF by Nothing](https://www.youtube.com/@cmfbynothing) | 1 | 6.0 s | Partial crops, no cuts | 3 |
| [Notion](https://x.com/NotionHQ) | 1 | 10.0 s | A 2.6 s real-UI glimpse, then the wordmark; the copy lives in the post text | 4 |
| [Raycast](https://www.youtube.com/@raycastapp) | 2 | 38.6–298.8 s | Glimpse and name; plays like a trailer | 4 |
| [Made by Google](https://www.youtube.com/@madebygoogle) | 3 | 15.0–56.8 s | Glimpse and name for hardware | 4 |
| [Framer](https://www.youtube.com/@framer) | 2 | 10.2–30.8 s | Partial (a hardware collaboration) and a feature teaser | 3 |
| [Figma](https://www.youtube.com/@figma) | 1 | 39.7 s | A full feature demo before launch | 5 |
| [Apple](https://www.youtube.com/@Apple) | 1 | 29.8 s | A full demo | 5 |
| [teenage engineering](https://www.youtube.com/@teenageengineering) | 1 | 18.5 s | Object-led metaphor | 2 |

## Other channels scanned, not studied

Listed in `channels/` but no film from them was measured: [OpenAI on YouTube](https://www.youtube.com/@OpenAI), [Anthropic on YouTube](https://www.youtube.com/@anthropic-ai), [Google Gemini](https://www.youtube.com/@GoogleGemini), [Linear](https://www.youtube.com/@linear), [The Browser Company](https://www.youtube.com/@TheBrowserCompany), [Humane](https://www.youtube.com/@Humane), [rabbit](https://www.youtube.com/@rabbitinc). `channels/README.md` ranks them by style.

## Style to accounts

Where to start Step 3 of `SKILL.md` for each style. "Studied" means we measured films from the account. "Named only" means `references/intake.md` suggests it but this library holds no data for it. The playful row is thin: its studied films are AI-lab character shorts, and the dedicated playful brands are named only, so a playful film's research starts mostly fresh.

| Style | Studied | Scanned only | Named only |
|---|---|---|---|
| High-fidelity product film | Claude, OpenAI, Manus, xAI | Linear, The Browser Company, Anthropic and OpenAI on YouTube | Raycast feature films, Arc |
| Playful / character-led | Claude (8-bit mascots), OpenAI (glyph casts, plush characters), Manus (clay mascots) | Figma, Framer | Duolingo, Notion, Headspace |
| Editorial / typographic | OpenAI (typed headlines), Manus, xAI loop cards | Linear, Framer | Stripe Sessions, Vercel |
| Metaphor / object | Claude (cut-out numerals), Samsung teasers, teenage engineering | Nothing, CMF | |
| Cinematic / material | Claude (*Opus 5.5*), OpenAI (*dots*, *Daybreak*), xAI (*Rename sting*), Nothing teasers | Apple, Made by Google | |
| Screen-recording honest | Claude (captured terminals), xAI (*Polymarket*, *Kalshi*, *Grok 4 free*), Manus (*Slack connector*), Google (*Gemma 4*, as a counter-example) | Framer, Figma | Cursor, indie launches |
| Motion vocabulary (any style) | Google | Google Gemini | |

Accounts and links change. Re-verify a link before you rely on it.

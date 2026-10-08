# YouTube channel scans

Twenty YouTube channels were listed on 7 October 2026 for the teaser study, with `yt-dlp --flat-playlist -j` on each channel's `/videos` and `/shorts` tabs (newest 200 of each). Nothing was downloaded at this step. Each CSV here is a compact candidate list for one channel.

## Columns

| Column | Meaning |
|---|---|
| `url` | The video or Short. |
| `tab` | `videos` or `shorts`. |
| `title` | The title as YouTube listed it. |
| `duration_s` | Length in seconds. The flat listing gives no length for most Shorts, so it is often blank there. |
| `views` | View count on 7 October 2026. |
| `date` | Blank. The flat listing does not return upload dates. Read them per video with `yt-dlp -j <url>` when you need them. |
| `flags` | `teaser` when the title says coming / coming soon / teaser / trailer / sneak peek / soon / get ready; `launch` when it says introducing / launch / announce / meet / is here / now available / out now / new / unveil / reveal. A keyword match, not a judgement. |
| `candidate` | `y` when a flag is set and the video is 120 s or shorter (or its length is unknown). Start here. |

Rows are sorted with candidates first, then by views. To keep the files small, only candidates and videos of 90 s or less are kept. Run `scripts/research/scan_channel.sh <handle>` for a channel's full list.

## The channels

| Handle | Listed | Kept here | Candidates | Note |
|---|---|---|---|---|
| samsung | 400 | 132 | 60 | Source of the "What's coming?" teaser series (10 of the 25 teasers are Samsung's). |
| madebygoogle | 400 | 162 | 52 | Pixel launch and teaser films. |
| Apple | 195 | 56 | 21 | Product films; few are teasers. |
| cmfbynothing | 73 | 45 | 21 | Short "Out now" and "coming soon" product films. |
| figma | 400 | 34 | 20 | "Introducing" feature films and Figma Update teasers. |
| teenageengineering | 137 | 65 | 19 | "introducing" films for hardware; object-led. |
| NothingTechnology | 385 | 58 | 18 | Teasers and OS launch films. |
| OpenAI | 279 | 88 | 17 | YouTube copies of launch films, plus talks. |
| GoogleGemini | 31 | 17 | 6 | Feature films. |
| anthropic-ai | 173 | 42 | 13 | YouTube copies of Claude launch films, plus talks. |
| linear | 80 | 31 | 13 | "Introducing" feature films, 30–70 s. |
| framer | 242 | 45 | 12 | Feature launches and tutorials. |
| TheBrowserCompany | 113 | 28 | 9 | Arc and Dia "Introducing" films. |
| Humane | 34 | 4 | 3 | OS update films. |
| rabbitinc | 12 | 9 | 1 | Few launch films. |
| raycast | 35 | none | none | Wrong channel: this handle is a VFX tutorial channel. The Raycast app is `@raycastapp`; its two teasers are in `../teasers.csv`. Not shipped. |
| NotionHQ | 0 | none | none | The scan returned nothing. Notion's teaser came from X instead. |
| arcinternet | 0 | none | none | Empty scan. Use TheBrowserCompany. |
| nothing | 0 | none | none | Empty scan. Use NothingTechnology. |
| perplexity_ai | 0 | none | none | Empty scan. Re-check the handle. |

## Which channel for which style

This ranking is our judgement from the titles and from the films we downloaded and studied. It is not measured. Use it to decide where to start, then watch.

| Style (see `references/intake.md`) | Start with | Then |
|---|---|---|
| High-fidelity product film | linear, TheBrowserCompany, anthropic-ai, OpenAI | figma, framer |
| Editorial / typographic | linear, framer | OpenAI |
| Metaphor / object | samsung ("What's coming?"), teenageengineering | cmfbynothing, NothingTechnology |
| Cinematic / material | NothingTechnology, Apple | madebygoogle |
| Playful / character-led | figma, framer (Shorts) | none of the scanned channels is mainly playful; look elsewhere |
| Screen-recording honest | framer, figma (tutorials and feature Shorts) | linear |
| Teasers of any style | samsung, NothingTechnology, cmfbynothing, madebygoogle | figma, framer |

Links rot and counts change. Re-run the scan before you rely on a number.

# Web search templates: find the accounts, then the films

Web search finds *who* makes films in a style. The platform tools (`youtube_search.sh`, `scan_channel.sh`, `x_search.md`, `tiktok.sh`) then list *their* films. Run 3–6 of these per style with WebSearch, note every account or studio that comes up twice, and check the films before you add an account to `style_seeds.md` for this project.

Replace `<category>` with the product's category (note-taking app, AI agent, fintech, developer tool) and `<year>` with this year and last year.

## Any style

- `best product launch videos <year>`
- `best SaaS launch video <year> motion design`
- `"launch film" <category> <year>`
- `site:x.com "introducing" <category> video`
- `<competitor> launch video` (the owner's competitors and the companies they admire)
- `motion design studio SaaS launch video case study`
- `"product video" agency portfolio <category>`

## Per style

| Style | Queries |
|---|---|
| High-fidelity product film | `"launch video" "product film" UI animation <year>` · `best app launch film real UI <year>` · `"made with" Remotion OR "After Effects" product launch video UI` · `<lab or tool> introducing video <year>` |
| Playful / character-led | `brand mascot animation launch video app` · `playful 2D animated product launch video <year>` · `character animation app explainer brand refresh` · `"brand refresh" video animation app <year>` |
| Editorial / typographic | `kinetic typography product launch video` · `typographic brand film tech company` · `keynote opener kinetic type <year>` · `"manifesto" video tech brand typography` |
| Metaphor / object | `teaser video objects no product shown` · `"coming soon" teaser video tech brand <year>` · `product teaser stop motion OR CGI objects metaphor` · `hardware teaser film abstract` |
| Cinematic / material | `CGI product film macro lighting tech <year>` · `cinematic brand film AI model launch` · `octane OR redshift product launch film studio` · `material study film product reveal` |
| Screen-recording honest | `"Screen Studio" launch video examples` · `indie hacker launch video screen recording` · `best Product Hunt launch videos <year>` · `cursor zoom screen recording product demo launch` |

## Galleries worth checking

Verify each still exists and is current before relying on it.

- **Product Hunt:** top launches of the day and month. Most top launches carry a video; filter by your category.
- **Behance and Dribbble:** search "product launch video", "SaaS motion", "app promo". Good for finding studios; client films are linked from the case studies.
- **Vimeo Staff Picks and Vimeo search:** "product film", "launch film". Studios post their reels here first.
- **Studio portfolios:** motion studios that specialise in software films list their clients. Each client is a seed account.
- **Godly, Land-book, SaaS Landing Page and similar site galleries:** sites with hero videos. The hero video is often a cut of the launch film.
- **The brands' own newsrooms and changelogs:** launch posts embed the film and give the date.
- **Remotion showcase:** films made in code, closest to what this skill builds.

## Turning results into a seed list

1. For each account found, open its X media tab or YouTube channel and look at 3 films (`analyze_video.py` sheets are enough).
2. Keep it if at least 2 of the 3 match the chosen style. Write down one line on why.
3. Stop at 3–5 main accounts plus 1 vocabulary account (see `references/reference-research.md`).

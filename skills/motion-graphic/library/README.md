# Reference library

Every reference film studied for the worked example (`examples/kallo-launch-film/`), as links, metadata and our own measurements. Start Step 3 of `SKILL.md` here, so you spend the crawl on what this does not cover.

## Coverage, honestly

Counted from the CSVs:

| Field | Launch films (125) | Google (38) | Teasers (25) |
|---|---|---|---|
| Link | 125 | 29 | 25 |
| Title | 125 | 8 | 25 |
| Style tags, directions | 85 (the kept films) | none | reveal-ladder rung for 19 |
| Technique-card codes | 67 | none | none |
| Watched-pass transition log, demo and text share | 24 | 8 | none |
| Measured cuts a minute | 11 | none | 25 |
| Machine-pass shot count | 48 | none | cuts for 25 |

It is strongest on high-fidelity AI-lab launch films (OpenAI, Claude, xAI, Manus). The 12 playful films are AI-lab character shorts. Duolingo, Notion and Headspace are named only: no films listed, no measurements. **If the owner picks a playful or character-led style, the research starts mostly fresh;** use this library for vocabulary, not as the corpus.

## What is here

| File | Rows | What it holds |
|---|---|---|
| `launch-films.csv` / `.json` | 125 | Launch films from OpenAI, Claude, xAI and Manus on X: link, title, date, length, views, style tags, kept or excluded under "motion design only" and why, direction, technique-card codes, and the watched-pass transition log where one exists. |
| `google-films.csv` / `.json` | 38 | Google films from X, used as motion vocabulary only. 8 were watched second by second. |
| `teasers.csv` / `.json` | 25 | Pre-launch teasers from YouTube and X: length, cuts, views, reveal-ladder rung. |
| `channels/` | 15 CSVs | Candidate lists from 20 YouTube channel scans, with likely launch and teaser films flagged. See `channels/README.md`. |
| `accounts.md` | | Style to accounts, with each account's measured medians. |
| `baselines.md` | | Corpus numbers to compare against: lengths, where the seconds go, the 298-transition mix, teaser timing. |
| `posting.md` | | When and how to post the film: measured time bands, warm-up cadence, formats that spread. |
| `research/` | | The distilled research: findings (where the seconds go, the 298-transition mix, 12 moves), 92 technique cards, 10 directions, the research boards with a real frame per card, the teaser study. See `research/README.md`. |

## How it was gathered

All of it between 30 September and 7 October 2026.
- **30 Sep.** 125 films listed from the four X accounts' media tabs in a signed-in browser and downloaded with `yt-dlp`. A machine pass (cut detection, contact sheets, loudness) ran on all of them. Eight study passes then went through the 85 kept films and recorded 267 techniques, each proven by a frame, merged into 92 cards and 10 directions.
- **1 Oct.** After the first cut, 24 lab films and 8 Google films were logged second by second (segments and 298 transitions), and 123 films were measured at 4 fps.
- **5–6 Oct.** Social-launch research on X, Threads and TikTok (`posting.md`).
- **7 Oct.** 20 YouTube channels scanned and 25 teasers downloaded and measured.

The analysis files from those passes were later deleted. This library was rebuilt on 7 October from the research write-ups now in `research/` and the teaser study in `examples/kallo-launch-film/04-teaser.md`, the original listing and download records, the study scripts that defined directions and cards, and the per-film watched-pass logs. Fields that could not be recovered are left blank, never guessed.

## Field notes

- **URLs.** The download folders were named `<account>_<media id>`, and the media id is not the post id. The post ids here come from the original listing (`launch-films.csv` keeps the media id in its own column). For Google, only some post ids could be recovered; `google-films.csv` says how each URL was matched, and leaves it blank when it could not be.
- **Dates** of X posts are decoded from the post id (X ids carry their creation time). Google rows give the media upload date instead. Teaser dates are YouTube upload dates.
- **Style tags** come from which of the 10 directions a film belongs to (D1–D10; listed in `references/distilling.md` and written up in `research/directions.md`), plus `screen-recording` where the study notes say the film is real screen capture. Excluded films have no style tags.
- **Technique cards** are the codes in `research/technique-cards.md` whose source or "also seen in" frames come from that film.
- **Notes** are one line from our own study notes, in our words.
- **Blank fields:** transition logs exist only for the 24 watched lab films; per-film measured cuts a minute survived for 11 lab films; the machine-pass shot count for 48. Excluded films have no direction, cards or note. Channel scans have no dates.
- **Titles** that would name a person are replaced with a description.

## How to use it

1. **Pick the style** with the owner (Step 1). Open `accounts.md` and take the accounts listed for that style as seeds for Step 3. Check the coverage table above first: for some styles there is little here. Add the wider seed list in `$SKILL/scripts/research/discover/style_seeds.md` for accounts this library has no data on, and rescan a channel with `$SKILL/scripts/research/scan_channel.sh`.
2. **Filter the CSVs** by `style_tags` or `directions`. For each match, open the link, watch it, and decide whether it fits your brief. Sort `channels/*.csv` by `candidate` to find more.
3. **Reuse the measurements as baselines.** `baselines.md` gives the medians of a high-fidelity product film. Compare your storyboard and your cuts against them, and measure your own style's films (Step 4) when the style differs.
4. **Use `posting.md`** when you plan the release, and re-run its method for your own audience.

## Links rot

Every link was checked as well-formed when this was written, but posts get deleted and channels renamed. Re-verify each link before you cite it, and re-read view counts, which change daily.

## Licence

This folder contains links and our own measurements and notes only. No video files, frames or thumbnails from any third-party film are included. The films belong to their owners. Open them at the links. The measurements and notes are ours and ship under this repo's licence.

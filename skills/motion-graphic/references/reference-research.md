# Reference research: build a corpus you have actually watched

You are building evidence, not a mood board. The output is a folder of real films on disk (`film/research/vids/`), a metadata file per film, and an inclusion decision for each.

## 0. Pick a scope at intake

Agree the scope in Step 1, before any download. Every quota in this file scales with it.

| Scope | New films | Watched closely | Time | Disk (30 s films) | Fits |
|---|---|---|---|---|---|
| Quick | library + 10–20 | 5–8 | 1–2 h | 0.05–0.4 GB | a teaser, a feature drop, a style the library already covers |
| Standard | 30–60 | 10–15 | half a day | 0.15–1.2 GB | most launch films |
| Full | 60–150 | 15–30 | 1–2 days | 0.3–3 GB | a flagship launch; the worked example (125 films) |

How the numbers come out: a 30 s reference film is 5–20 MB at 1080p, and the measuring pipeline runs about 1 s of compute per second of film on an Apple M2 (`$SKILL/scripts/research/PIPELINE.md`). Most of the time goes to finding films and the watched pass, not to compute. Delete the video files once a film is measured and its strips are cut, if disk is short.

**Stopping rule.** Stop adding films when new films stop adding new technique cards: for example, 10 films in a row that add nothing. Note in the overview where you stopped and why.

**Checkpoint.** Write the phase state to `film/STATUS.md` after each pass (listed, downloaded, measured, watched), with counts, so a later session resumes instead of starting over.

## 1. Pick the accounts from the taste answer

- Start with the films in `$SKILL/library/` that match the style. Coverage is uneven: all 125 launch films have a link and a title and the 85 kept ones a style tag; transition logs survive for 24, measured cuts a minute for 11, machine shot counts for 48 (`$SKILL/library/README.md`). Playful accounts (Duolingo, Notion, Headspace) are named only. For a playful or character-led film, expect to start mostly fresh.
- Add the accounts the owner named, then 2–4 peers in the same style; see the menu in `intake.md` and `$SKILL/scripts/research/discover/style_seeds.md`.
- Add one "vocabulary" source whose pace you will not copy but whose moves you can borrow. In the worked example Google was added for its title splits and blur pull-backs. The owner was explicit: "Google is more on a slow side. I want fast. Just a reference for possible kinds of motion."
- For a teaser, research teasers specifically: hardware and app companies' "coming soon" posts, self-leaks and countdown clips. See `teaser.md`.

## 2. Collect

Quotas scale with the scope: Quick takes 3–6 films from each of 2–4 accounts, Standard 10–15 from each of 3–5, Full 20–35 from each of 4–8. The worked example (Full) downloaded 125 films from four accounts, about 31 each, and kept 85.

**YouTube:** list a channel's videos and shorts without downloading:
```bash
"$SKILL/scripts/research/scan_channel.sh" OpenAI          # → lists/yt_OpenAI.jsonl (title, duration, url, views)
```
Filter by title keywords and duration (teasers: `teaser|coming|soon|sneak|introducing`, ≤40 s), then download the picks:
```bash
"$SKILL/scripts/research/download.sh" urls.txt vids/      # yt-dlp, ≤1080p, mp4, plus .info.json
```

**X (Twitter):**
- yt-dlp downloads the video of a public post URL without login.
- Listing an account's media needs a logged-in browser. Read the page text or DOM from a signed-in tab, collect post URLs, then hand them to yt-dlp. Don't extract or replay auth tokens; read what the page shows.
- A backgrounded browser window may report itself hidden and stop loading infinite feeds. Keep the window visible while collecting.
- **No login, or no browser tool?** Skip X and Threads listing. Use the library, YouTube, TikTok public profiles and links the owner pastes; yt-dlp still downloads a single public X post. A Quick scope can start from ten links.

**TikTok:** `yt-dlp --flat-playlist -j https://www.tiktok.com/@handle` lists a profile with views and dates, logged out.

**Store with each film:**
- the `.info.json` (title, upload date, view count, description);
- a stable id, `<account>__<post-id>.mp4`;
- the post text. The post copy is part of the launch: Notion Mail's teaser put the whole pitch in the post and none in the video.

## 3. Decide inclusion explicitly

Write the rule down, apply it per film, and show the owner the judgement calls. Example rule from the worked run:

> Motion design only. A film is out if people are a subject anywhere in it (live action, or people filmed, drawn or generated as its imagery). A film stays when people appear only incidentally inside the product's own screens (an avatar, a thumbnail); techniques are taken only from shots with no person in them.

The result is a count per account (kept / total) plus a list of judgement calls the owner can flip, for example "kept: macro and space footage but no people; out: opens on real footage of a bird".

## 4. Watch, for real

- Make a timestamped contact sheet for every film (`$SKILL/scripts/research/analyze_video.py <films...> --out <dir>`; `run_corpus.py` does this for you) and look at it.
- For the films you will lean on (5–30, by scope), do a watched pass: log second by second what is on screen (demo, text card, logo, transition), the camera state, and the sound.
- Never describe a film you have not looked at, and never label a direction "closest to @X" unseen.

## 5. Legal and hygiene

- Keep the corpus private and local. It exists to be studied, not republished.
- **Private review vs public.** Research boards with third-party frames (cards, strips, the corpus report) are for the owner's private review: local files, or a private artifact shared only with the team. Anything published publicly (a case study, a blog post, a public repo) refers to films by link, account, title and timestamp, describes them in words, and uses your own frames, unless the owner decides otherwise for credited research commentary.
- Never ship third-party audio, and never use third-party frames as imagery in the film.
- Scratch directories under `/tmp` can be purged by the OS after a few days. Keep the corpus and every derived dataset in a durable project folder; the worked example lost its raw corpus that way and had to rebuild its findings from the published boards.

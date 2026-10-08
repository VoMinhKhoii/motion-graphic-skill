# Finding launch films on Threads

Many brands cross-post their launch films to Threads, sometimes in a different cut from X. Use it when an account is more active there, or to get a second aspect ratio of a film.

## What yt-dlp can do

Nothing, at the time of writing. `yt-dlp --list-extractors | grep -i threads` returns no match with yt-dlp 2026.08.19 (it lists Instagram and TikTok, not Threads). Check again with your version; if an extractor appears, `../download.sh` works on Threads post URLs and you can skip the `curl` step below.

## The route: read the video element, then curl

1. Open a search or profile page in a browser. A **profile** (`https://www.threads.com/@<handle>`) is readable logged out, but shows only the first few posts before a login prompt. **Search** (`https://www.threads.com/search?q=<query>&serp_type=default`) needs the user's own logged-in browser.
2. Run `threads_collect.js` in the page (same ways as `x_collect.js`, see `x_search.md`). It scrolls in steps and returns, per post with a video: the permalink, the handle, the visible post text, and the `<video>` element's own `src`.
3. Download each `src` right away; it is a signed CDN URL that expires within hours:

```bash
# result.json is the collector's output saved from the browser tool
python3 - <<'EOF' > dl.sh
import json
for p in json.load(open('result.json'))['posts']:
    if p['video_src'].startswith('http'):
        print(f"curl -sL -o 'vids/{p['handle']}__{p['code']}.mp4' '{p['video_src']}'")
EOF
mkdir -p vids && sh dl.sh
```

4. Save the post text yourself (the collector returns it): there is no `.info.json` for these. Write one per film with at least `{"title", "uploader_id", "webpage_url", "description"}` so `run_corpus.py` can read the account and title.

**Read the page DOM only.** The video `src` is a public media URL the page already shows to the viewer. Never read, copy or replay cookies, session tokens or request headers, and never call Threads' internal GraphQL endpoints with them.

Tested on 2026-10-07 on a public brand profile, logged out, through Playwright MCP: the collector returned 4 posts, all with an `https://…fbcdn.net/…mp4` source; `curl` fetched a 1280x720, 69 s MP4 (HTTP 200) without cookies. Search was not tested logged in.

## Search queries

Threads search is keyword search with no operators (no `filter:video`, no `min_faves`). Search for the words, then let the collector keep only the posts with a video.

| Goal | Query |
|---|---|
| Launches | `introducing`, `"now available"`, `launch video` |
| Teasers | `coming soon`, `teaser` |
| A style | the style words from `x_search.md`, one or two at a time |
| An account | open its profile instead; search mixes in replies and mentions |

Use the "Recent" tab (`&filter=recent`) for new posts. Threads ranks the default tab by engagement, which is what you want for finding well-known films.

## Limits

- `blob:` sources: some players stream through Media Source Extensions and expose only a `blob:` URL. Those cannot be fetched; open the post's own page and run the collector there, or skip it.
- The post text the collector reads is the visible card text, including the handle and the "1d" age.
- Dates are relative ("1d", "3w"). If you need the exact date, open the post and read the `<time datetime>` attribute.

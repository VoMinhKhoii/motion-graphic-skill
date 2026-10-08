# Finding launch films on X

X is where most software launch films are posted first, often only there. Listing them needs a logged-in browser; downloading a public post's video does not.

## The route

1. The user opens X in their own browser, logged in as themselves. You never log in for them and never ask for a password.
2. You open a search or profile URL from the list below in that browser.
3. You run `x_collect.js` in the page. It scrolls in steps and returns the URLs of posts that carry a video, with the post text, date and like count it can read from the page.
4. You save the URLs to `urls.txt` and run `../download.sh urls.txt vids/`. yt-dlp downloads public X post videos without login.

**Read the page DOM only.** Never read, copy, export or replay cookies, auth tokens, `ct0`/`auth_token` values or request headers, and never call X's internal APIs with them. If a download fails for a post that needs login (age-gated, protected account), skip it or ask the user to save the video themselves.

## Search URLs

Paste the query after `https://x.com/search?f=top&q=` (URL-encode it; spaces become `%20`). Use `f=top` for the most-liked first and `f=live` for newest first.

| Goal | Query |
|---|---|
| One account's films | `from:<handle> filter:native_video` |
| One account, launches only | `from:<handle> filter:native_video (introducing OR launch OR "now available" OR meet)` |
| Big launches, any account | `"introducing" filter:native_video min_faves:2000` |
| Recent launches | `(launch OR introducing OR "now available") filter:native_video min_faves:1000 since:2025-01-01` |
| Teasers | `("coming soon" OR "something new" OR tomorrow) filter:native_video min_faves:500` |
| A product category | `(introducing OR launch) (app OR AI OR API) filter:native_video min_faves:1000 since:2025-06-01` |
| Exclude replies and reposts | add `-filter:replies -filter:nativeretweets` |
| A date window | `since:2026-01-01 until:2026-04-01` |

A profile's media tab also works: `https://x.com/<handle>/media`. It shows images too; the collector keeps only posts with a video.

## Queries per style

The style names match the menu in `references/intake.md`. Combine a style's words with `filter:native_video min_faves:500` (raise the bar to 2000+ for big brands).

| Style | Query words |
|---|---|
| High-fidelity product film | `introducing`, `"now available"`, `"rolling out"`, `"available today"`, plus the product noun (`app`, `agent`, `model`) |
| Playful / character-led | `meet`, `"say hello"`, `mascot`, `"new look"`, `"brand refresh"` |
| Editorial / typographic | `"a new way to"`, `manifesto`, `"we believe"`, `"designed for"` |
| Metaphor / object | `teaser`, `"something is coming"`, `"what's coming"`, `"coming soon"` |
| Cinematic / material | `"a film"`, `"short film"`, `"launch film"`, `rendered` |
| Screen-recording honest | `demo`, `"how it works"`, `"built this"`, `"shipped"`, `"just launched"` |

Motion designers often repost their client work with credit. Search `"motion design" (launch OR "product video") filter:native_video min_faves:300` and follow the studios you find back to their clients.

## Running x_collect.js

The script is one async function. It reads `window.__xCollectOpts = {steps, waitMs, idleStops}` if set (defaults 40 scroll steps, 1.4 s wait, stop after 4 steps that add nothing). Results accumulate on `window.__xCollected`, so running it twice on the same tab continues where it stopped.

- **Playwright MCP:** `browser_navigate` to the search URL, then `browser_evaluate` with the file's whole text as `function`. The Playwright browser is a separate profile; the user has to log in to X in that window themselves.
- **Chrome DevTools MCP:** `new_page` or `navigate_page` in the user's Chrome, then `evaluate_script` with the file's text as `function`. This uses the user's existing session.
- **A built-in browser or computer-use tool:** navigate, then run the file in its JavaScript evaluator; if it has none, the user can paste it into the DevTools console as `await (<file text>)()` and copy the result.
- **No automation at all:** the user opens the search, scrolls, and copies the post links by hand. Ten links are enough for a Quick scope; Standard and Full scopes need more (`references/reference-research.md` §0).

Keep the tab visible while it runs. X stops loading the feed in a hidden or backgrounded window, and the run ends early with fewer posts.

Then:

```bash
# from the JSON result, one URL per line
python3 -c 'import json,sys; [print(u) for u in json.load(sys.stdin)["urls"]]' < x_result.json > urls.txt
../download.sh urls.txt vids/
```

## Limits

- X shows roughly the last 800 to 3,200 posts of a profile; older films need search with `since:`/`until:` windows.
- `min_faves` and `filter:native_video` are unofficial operators. They have worked for years but can change.
- The like and repost counts are whatever the page shows ("2.1K"), not exact numbers.

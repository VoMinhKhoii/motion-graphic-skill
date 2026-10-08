# Instagram

Instagram is the least reliable source to automate. Use it for accounts that post only there (some hardware and consumer brands); find the same film on YouTube, X or Threads first when you can.

## What works

- **A single public post or reel URL with yt-dlp.** `yt-dlp https://www.instagram.com/reel/<code>/` often works logged out, and `../download.sh` accepts these URLs. Instagram rate-limits logged-out requests quickly; after a few downloads it answers with a login redirect.
- **With the user's browser cookies, if they choose to.** `yt-dlp --cookies-from-browser chrome <url>` (or `safari`, `firefox`) lets yt-dlp read the user's own session from their browser profile. This is the user's decision, made per session: say what it does and ask. Never copy cookies out of a browser by other means, and never store them in the project.
- **Listing a profile in the browser.** Open `https://www.instagram.com/<handle>/reels/` in the user's logged-in browser and collect the reel links from the DOM: every `a[href*="/reel/"]`. The `threads_collect.js` pattern works with that selector change; or scroll and copy the links by hand.
- **Cross-posts.** Threads profiles mirror many Instagram reels, and the Threads route (`threads_search.md`) gives a direct MP4.

## What to avoid

- `instagram:user` is marked "CURRENTLY BROKEN" in yt-dlp 2026.08.19 (`yt-dlp --list-extractors | grep -i instagram`); do not build on profile extraction.
- Do not use a dedicated scraping account, third-party "Instagram downloader" sites, or private API wrappers. They break, get accounts banned, and some harvest credentials.
- Do not batch hundreds of requests. Pick the 5–15 films you need.
- Hashtag pages (`instagram:tag`) and Explore are not useful for finding launch films: they are dominated by creators, not brands.

## Storing

Name files `<handle>__<code>.mp4` so `run_corpus.py --account-from-filename` reads the account. Save the caption: with yt-dlp it is in the `.info.json`; from the browser, write a small `.info.json` yourself (`{"title", "uploader_id", "webpage_url", "description"}`).

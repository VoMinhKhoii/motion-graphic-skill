async () => {
  // x_collect.js: harvest the URLs of posts that carry a video from an X search or profile page that is
  // already open and loaded in the user's own browser. It reads the page DOM only. It never reads, copies or
  // replays cookies, tokens or request headers.
  //
  // Run it:
  //   Playwright MCP        browser_evaluate with this whole file as the `function` argument
  //   Chrome DevTools MCP   evaluate_script with this whole file as the `function` argument
  //   DevTools console      paste:  await (<this file>)()
  // It scrolls in steps, collects as it goes (X removes posts that scroll out of view), and returns
  // { count, urls, posts }. Paste `urls` into a urls.txt for ../download.sh, which hands them to yt-dlp.
  //
  // Tunables: change these three lines, or set window.__xCollectOpts = {steps, waitMs, idleStops} first.
  const opts = Object.assign({ steps: 40, waitMs: 1400, idleStops: 4 }, window.__xCollectOpts || {});
  const seen = (window.__xCollected = window.__xCollected || new Map()); // survives re-runs on the same tab
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  const harvest = () => {
    let added = 0;
    for (const art of document.querySelectorAll('article[data-testid="tweet"], article')) {
      const hasVideo = !!art.querySelector('[data-testid="videoPlayer"], [data-testid="videoComponent"], video');
      if (!hasVideo) continue;
      // The post's own permalink is the status link that wraps its <time>; quoted posts have their own.
      const timeEl = art.querySelector('a[href*="/status/"] time');
      const link = timeEl ? timeEl.closest('a') : art.querySelector('a[href*="/status/"]');
      if (!link) continue;
      const m = link.getAttribute('href').match(/^\/([^/]+)\/status\/(\d+)/);
      if (!m) continue;
      const url = `https://x.com/${m[1]}/status/${m[2]}`;
      if (seen.has(url)) continue;
      const textEl = art.querySelector('[data-testid="tweetText"]');
      const stat = (id) => {
        const el = art.querySelector(`[data-testid="${id}"]`);
        return el ? (el.getAttribute('aria-label') || el.textContent || '').trim() : '';
      };
      seen.set(url, {
        url,
        handle: m[1],
        id: m[2],
        time: timeEl ? timeEl.getAttribute('datetime') : null,
        text: textEl ? textEl.innerText.slice(0, 280) : '',
        likes: stat('like'),
        reposts: stat('retweet'),
      });
      added++;
    }
    return added;
  };

  let idle = 0;
  for (let i = 0; i < opts.steps && idle < opts.idleStops; i++) {
    const added = harvest();
    idle = added ? 0 : idle + 1;
    window.scrollBy(0, Math.round(window.innerHeight * 0.85));
    await sleep(opts.waitMs);
  }
  harvest();
  const posts = [...seen.values()];
  return { count: posts.length, urls: posts.map((p) => p.url), posts };
}

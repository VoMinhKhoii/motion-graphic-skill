async () => {
  // threads_collect.js: harvest Threads posts that carry a video from a search or profile page that is
  // already open in the user's own browser. It reads the page DOM only. It never reads, copies or replays
  // cookies, tokens or request headers.
  //
  // Run it the same way as x_collect.js (Playwright MCP browser_evaluate, Chrome DevTools MCP evaluate_script,
  // or the console: await (<this file>)()). It scrolls in steps and returns
  // { count, posts: [{url, handle, text, video_src, poster}], srcs }.
  //
  // yt-dlp has no Threads extractor (checked with yt-dlp 2026.08.19), so the download route is the video
  // element's own src: `curl -L -o <handle>__<code>.mp4 "<video_src>"`. The src is a signed CDN URL that
  // expires within hours, so download soon after collecting. A src that starts with "blob:" cannot be
  // fetched with curl; open that post on its own page and run this again, or skip it.
  const opts = Object.assign({ steps: 40, waitMs: 1500, idleStops: 4 }, window.__thCollectOpts || {});
  const seen = (window.__thCollected = window.__thCollected || new Map());
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // A post's container is the nearest ancestor that holds exactly one permalink of the form /@handle/post/<code>.
  const containerOf = (video) => {
    let el = video;
    for (let up = 0; up < 25 && el; up++, el = el.parentElement) {
      const links = new Set(
        [...el.querySelectorAll('a[href*="/post/"]')]
          .map((a) => (a.getAttribute('href').match(/^\/@[^/]+\/post\/[^/?#]+/) || [])[0])
          .filter(Boolean),
      );
      if (links.size === 1) return { el, path: [...links][0] };
      if (links.size > 1) return null;
    }
    return null;
  };

  const harvest = () => {
    let added = 0;
    for (const v of document.querySelectorAll('video')) {
      const c = containerOf(v);
      if (!c) continue;
      const url = `https://www.threads.com${c.path}`;
      const src = v.currentSrc || v.src || (v.querySelector('source') || {}).src || '';
      const prev = seen.get(url);
      if (prev && prev.video_src) continue;
      const m = c.path.match(/^\/@([^/]+)\/post\/(.+)$/);
      seen.set(url, {
        url,
        handle: m[1],
        code: m[2],
        text: (c.el.innerText || '').replace(/\s+/g, ' ').slice(0, 280),
        video_src: src,
        poster: v.poster || '',
      });
      if (!prev) added++;
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
  return { count: posts.length, posts, srcs: posts.filter((p) => p.video_src.startsWith('http')).length };
}

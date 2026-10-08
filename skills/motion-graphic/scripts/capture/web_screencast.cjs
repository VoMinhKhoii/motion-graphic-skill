// web_screencast.cjs: record a web app at real speed and high resolution, driven by a list of steps.
//
// Usage:
//   node web_screencast.cjs <steps.json> <out.mp4>
//   ZOOM=2 W=1440 H=900 node web_screencast.cjs steps.json clips/web_lunch.mp4
//
// steps.json:
//   { "url": "http://localhost:3000/app",
//     "storageState": "state.json",              (optional: a Playwright login state, never committed)
//     "css": "nextjs-portal{display:none}",       (optional: hide dev overlays and debug badges)
//     "steps": [
//       { "do": "wait", "ms": 800 },
//       { "do": "click", "selector": "textarea" },               (any Playwright selector)
//       { "do": "type", "text": "plan a weekend in Lisbon", "delay": 45 },
//       { "do": "press", "key": "Enter" },
//       { "do": "waitFor", "selector": "text=Save", "timeout": 120000 },
//       { "do": "mark", "label": "result" } ] }
//
// Env: ZOOM (default 2), W x H (CSS viewport, default 1440x900), FPS (output, default 60), KEEP=1 keeps the frames,
//      PLAYWRIGHT (module path, default "playwright"), GPU=0 drops the GPU flags.
//
// Playwright: Node resolves require('playwright') from THIS file's folder upwards, not from where you run it,
// so installing Playwright in the product's own repo does not make it visible here. Either
//   - install it next to the film: `cd film/engine && npm i -D playwright && npx playwright install chromium`, and
//     run with PLAYWRIGHT=$PWD/node_modules/playwright (an absolute path), or
//   - point PLAYWRIGHT at any existing install: PLAYWRIGHT=/path/to/project/node_modules/playwright.
//
// How it gets sharp, smooth frames:
// - The Chrome DevTools screencast ignores a context's deviceScaleFactor and delivers CSS-pixel frames. Chrome's
//   --force-device-scale-factor=ZOOM flag does raise it: the page keeps a W x H CSS viewport (innerWidth, media
//   queries and the product's responsive layout are exactly those of a W x H window) and the frames come out at
//   W*ZOOM x H*ZOOM. ZOOM 2 gives a 2880x1800 capture of the real 1440x900 layout. (Do not fake it with a larger
//   viewport and `html{zoom}`: the page then sees a 2880 px window and may switch to its wide-screen layout.)
// - Chromium launches with GPU flags: --enable-gpu-rasterization --ignore-gpu-blocklist everywhere, plus
//   --use-angle=metal on macOS only (Linux uses its own GL or Vulkan backend; Windows uses D3D11 by default).
//   With software rendering the screencast managed ~14 fps at 2x; with the GPU ~57 fps (Apple M2). ZOOM 3
//   drops to ~9 fps. On a machine with no GPU (CI, most Linux servers) use ZOOM=1 and expect fewer frames.
// - Frames arrive when the page repaints, each with its own timestamp. Output frame k (time k/FPS) is the last
//   captured frame at or before that time, piped to ffmpeg in order and encoded at exactly
//   FPS. So the clip runs at true speed with no interpolation, every captured frame keeps its own time, and still
//   moments are held frames. (An ffmpeg concat list would quantise the frame times to 1/25 s first.)
// Step times are logged to <out>.events as "<seconds since first frame> <label>" for cutting the edit.
// Use the browser's own clock in the page (page.clock) if the UI shows the time; it is not set here.
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
let chromium;
try {
  ({ chromium } = require(process.env.PLAYWRIGHT || 'playwright'));
} catch (e) {
  console.error(`Cannot load Playwright from "${process.env.PLAYWRIGHT || 'playwright'}". Install it next to the film ` +
    '(cd film/engine && npm i -D playwright && npx playwright install chromium) and run with ' +
    'PLAYWRIGHT=$PWD/node_modules/playwright, or point PLAYWRIGHT at an existing install.');
  process.exit(1);
}
// GPU rasterisation everywhere; Metal through ANGLE exists only on macOS
const GPU_ARGS = process.env.GPU === '0' ? [] : ['--enable-gpu-rasterization', '--ignore-gpu-blocklist', '--enable-gpu',
  ...(process.platform === 'darwin' ? ['--use-angle=metal'] : [])];

const [specPath, outPath] = process.argv.slice(2);
if (!specPath || !outPath) { console.error('usage: node web_screencast.cjs <steps.json> <out.mp4>'); process.exit(1); }
const spec = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const Z = +(process.env.ZOOM || 2), W = +(process.env.W || 1440), H = +(process.env.H || 900), FPS = +(process.env.FPS || 60);
const dir = outPath.replace(/\.mp4$/, '') + '_frames';

(async () => {
  fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  const browser = await chromium.launch({ args: [...GPU_ARGS, `--force-device-scale-factor=${Z}`] });
  const ctx = await browser.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: Z, ...(spec.storageState ? { storageState: spec.storageState } : {}) });
  const page = await ctx.newPage();
  await page.goto(spec.url, { waitUntil: 'networkidle' });
  if (spec.css) await page.addStyleTag({ content: spec.css });
  const vw = await page.evaluate(() => [innerWidth, devicePixelRatio]);
  if (vw[0] !== W) throw new Error(`page sees a ${vw[0]} px wide window, expected ${W}`);
  await page.waitForTimeout(1000);
  const cdp = await ctx.newCDPSession(page);
  const stamps = [];
  const events = [];
  cdp.on('Page.screencastFrame', async (f) => {
    fs.writeFileSync(path.join(dir, `f${String(stamps.length).padStart(5, '0')}.jpg`), Buffer.from(f.data, 'base64'));
    stamps.push(f.metadata.timestamp);
    await cdp.send('Page.screencastFrameAck', { sessionId: f.sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 95, maxWidth: W * Z, maxHeight: H * Z, everyNthFrame: 1 });
  await page.waitForTimeout(500);
  // frame timestamps are wall-clock seconds, so step times are logged on the same clock, from the first frame
  const t0 = stamps.length ? stamps[0] : Date.now() / 1000;
  const log = (label) => events.push(`${(Date.now() / 1000 - t0).toFixed(3)} ${label}`);
  for (const s of spec.steps) {
    log(`${s.do} ${s.label || s.selector || s.text || s.key || s.ms || ''}`.trim());
    if (s.do === 'wait') await page.waitForTimeout(s.ms);
    else if (s.do === 'click') await page.locator(s.selector).first().click();
    else if (s.do === 'type') { if (s.selector) await page.locator(s.selector).first().click(); await page.keyboard.type(s.text, { delay: s.delay ?? 45 }); }
    else if (s.do === 'press') await page.keyboard.press(s.key);
    else if (s.do === 'waitFor') await page.locator(s.selector).first().waitFor({ timeout: s.timeout ?? 30000 });
    else if (s.do === 'mark') { /* logged above */ }
    else throw new Error(`unknown step ${s.do}`);
  }
  await page.waitForTimeout(600);
  const tStop = Date.now() / 1000; // a still page sends no frames, so the last frame is held until here
  await cdp.send('Page.stopScreencast');
  await browser.close();
  if (stamps.length < 1) throw new Error('no frames captured');
  // constant-rate stream: output frame k shows the last captured frame at or before k/FPS. The JPEGs are piped
  // to ffmpeg in that order (image2pipe at FPS), so a long still hold costs no files or links, only pipe bytes.
  const span = tStop - stamps[0];
  const n = Math.max(1, Math.round(span * FPS));
  const ff = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-c:v', 'mjpeg', '-framerate', String(FPS),
    '-i', '-', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-c:v', 'libx264', '-crf', '14', '-g', '30', '-pix_fmt', 'yuv420p',
    '-r', String(FPS), '-movflags', '+faststart', outPath], { stdio: ['pipe', 'inherit', 'inherit'] });
  ff.stdin.on('error', () => {}); // if ffmpeg dies, `done` rejects with its exit code
  const done = new Promise((res, rej) => ff.on('close', (c) => (c === 0 ? res() : rej(new Error(`ffmpeg exited ${c}`)))));
  const write = (buf) => new Promise((res) => (ff.stdin.write(buf) ? res() : ff.stdin.once('drain', res)));
  let j = 0, jBuf = -1, buf = null;
  const used = new Set();
  for (let k = 0; k < n; k++) {
    const t = stamps[0] + k / FPS;
    while (j + 1 < stamps.length && stamps[j + 1] <= t + 1e-6) j++;
    if (j !== jBuf) { buf = fs.readFileSync(path.join(dir, `f${String(j).padStart(5, '0')}.jpg`)); jBuf = j; }
    used.add(j);
    await write(buf);
  }
  ff.stdin.end();
  await done;
  console.log(`frames ${stamps.length} captured over ${span.toFixed(2)} s, ${used.size} used in ${n} output frames at ${FPS} fps` +
    ' (a still page sends none; typing and animation should reach 30-60 fps)');
  fs.writeFileSync(outPath.replace(/\.mp4$/, '.events'), events.join('\n') + '\n');
  if (!process.env.KEEP) fs.rmSync(dir, { recursive: true, force: true });
  console.log('wrote', outPath);
})().catch((e) => { console.error('ERR', e.message.slice(0, 400)); process.exit(1); });

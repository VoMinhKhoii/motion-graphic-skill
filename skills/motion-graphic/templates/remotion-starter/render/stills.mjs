// stills.mjs: bundle once, then render PNG stills of one composition at the given film times (seconds).
//
// Usage (from the template root):
//   node render/stills.mjs <outDir> <seconds...>
//   COMP=Film-916 PREFIX=v2 node render/stills.mjs out/stills 0.5 3.0 6.2
//
// Env: COMP (default Film-45), PREFIX (default "f"), SCALE (default 1; 0.5 renders half-size stills, a quarter of
// the pixels: enough to check layout, and kinder to a full disk). Files are named <PREFIX>_<COMP>_<centiseconds>.png,
// e.g. f_Film-45_0300.png for 3.0 s. Look at every still before you call a change done; downscale first
// (`sips -Z 800 in.png --out small.png`) so a contact sheet stays cheap to read.
// If `npx`/`node` fails with a preload error, run with `env -u NODE_OPTIONS`.
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition } from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const [outDir, ...times] = process.argv.slice(2);
if (!outDir || times.length === 0) {
  console.error('usage: node render/stills.mjs <outDir> <seconds...>');
  process.exit(1);
}
const id = process.env.COMP ?? 'Film-45';
const prefix = process.env.PREFIX ?? 'f';
const scale = Number(process.env.SCALE ?? 1);
fs.mkdirSync(outDir, { recursive: true });
// Each bundle is a ~320 MB folder in the OS temp dir; delete it when done, or a day of stills fills the disk.
const serveUrl = await bundle({ entryPoint: path.resolve('src/index.ts') });
try {
  const composition = await selectComposition({ serveUrl, id });
  for (const t of times) {
    const frame = Math.min(composition.durationInFrames - 1, Math.round(Number(t) * composition.fps));
    const out = path.resolve(outDir, `${prefix}_${id}_${String(Math.round(Number(t) * 100)).padStart(4, '0')}.png`);
    await renderStill({ composition, serveUrl, output: out, frame, scale });
    console.log('rendered', id, t, 's ->', out);
  }
} finally {
  fs.rmSync(serveUrl, { recursive: true, force: true });
}

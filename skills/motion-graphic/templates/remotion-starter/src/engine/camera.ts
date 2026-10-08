import type { Ctx } from './reel';

/**
 * A camera key: from time `t` (scene seconds) the camera wants to centre point (x, y) at scale `k`.
 * (x, y) are in device pixels (see device.tsx); `k` is frame pixels per device pixel.
 * `snap: true` jumps there at once (a cut) instead of travelling.
 */
export type CamKey = { t: number; x: number; y: number; k: number; snap?: boolean };

/** The spring's simulation step (Hz). Not the film's frame rate: the track is sampled by seconds, so it renders
 * the same at 30 and 60 fps. */
const STEP_HZ = 60;

const cache = new Map<string, { x: number; y: number; k: number }[]>();

/**
 * The tracking camera: a critically damped spring chasing a step target, the way screen-recording tools follow
 * a cursor. It leaves each key at speed, eases into the next and settles with no overshoot: "move, then hold".
 * Scale is sprung in log space so zooms feel even. `omega` is the stiffness in rad/s. Measured at 60 fps,
 * time to cover 95% / 99% of a move:
 *   7.5  0.65 / 0.95 s  a calm follow          9   0.55 / 0.80 s  brisk (the default)
 *   8    0.62 / 0.90 s                         12  0.42 / 0.62 s  snappy punch-ins
 * The track is integrated once per key set in 1/60 s steps and cached, so any frame can be rendered in any order,
 * at any composition frame rate.
 */
export function camAt(keys: CamKey[], s: number, omega = 9) {
  const id = JSON.stringify(keys) + omega;
  let track = cache.get(id);
  if (!track) {
    track = [];
    const end = Math.max(...keys.map((k) => k.t)) + 6;
    let x = keys[0].x, y = keys[0].y, lk = Math.log(keys[0].k);
    let vx = 0, vy = 0, vk = 0;
    const dt = 1 / STEP_HZ;
    let ki = 0;
    for (let i = 0; i <= Math.ceil(end * STEP_HZ); i++) {
      const t = i / STEP_HZ;
      while (ki + 1 < keys.length && keys[ki + 1].t <= t + 1e-9) {
        ki++;
        if (keys[ki].snap) {
          x = keys[ki].x; y = keys[ki].y; lk = Math.log(keys[ki].k);
          vx = vy = vk = 0;
        }
      }
      const g = keys[ki];
      const ax = -2 * omega * vx - omega * omega * (x - g.x);
      const ay = -2 * omega * vy - omega * omega * (y - g.y);
      const ak = -2 * omega * vk - omega * omega * (lk - Math.log(g.k));
      vx += ax * dt; vy += ay * dt; vk += ak * dt;
      x += vx * dt; y += vy * dt; lk += vk * dt;
      track.push({ x, y, k: Math.exp(lk) });
    }
    cache.set(id, track);
  }
  const i = Math.max(0, Math.min(track.length - 1, Math.round(s * STEP_HZ)));
  return track[i];
}

/**
 * The camera for a scene, plus `map`, which turns a device-pixel point into a frame-pixel point. Use `map` for
 * anything drawn in frame space on top of the device (the pointer, callouts), so it keeps its size whatever the
 * camera does. Keys are written for portrait; landscape frames multiply every k by `landscapeK` (default 0.84),
 * because a 1080 px tall frame needs a slightly wider shot than a 1350 or 1920 px tall one to show the same UI.
 */
export function useCam(c: Ctx, keys: CamKey[], { omega = 9, landscapeK = 0.84 } = {}) {
  const kk = c.P ? keys : keys.map((k) => ({ ...k, k: k.k * landscapeK }));
  const cam = camAt(kk, c.s, omega);
  const map = (x: number, y: number) => ({ x: c.W / 2 + (x - cam.x) * cam.k, y: c.H / 2 + (y - cam.y) * cam.k });
  return { cam, map };
}

/**
 * The key scale that fits a box `h` device px tall into `frac` of the layout height. It divides out the
 * landscape factor, so after useCam applies it the box really fills `frac` of the height in every format.
 */
export const fitK = (c: Ctx, h: number, frac = 0.9, landscapeK = 0.84) => (c.H * frac) / h / (c.P ? 1 : landscapeK);

/** fitK for a whole box: the key scale that fits w x h device px into `frac` of the layout, by whichever side binds. */
export const fitBox = (c: Ctx, w: number, h: number, frac = 0.9, landscapeK = 0.84) =>
  Math.min(fitK(c, h, frac, landscapeK), (c.W * frac) / w / (c.P ? 1 : landscapeK));

/**
 * Clamp a key's y so the device's top and bottom edges never come more than `m` frame px inside the frame: no
 * empty void above or below the phone on a close shot. If the whole device fits, it is centred.
 */
export const holdEdges = (c: Ctx, key: CamKey, deviceH: number, m = 0, landscapeK = 0.84): CamKey => {
  const k = c.P ? key.k : key.k * landscapeK;
  const half = (c.H / 2 - m) / k;
  if (2 * half >= deviceH) return { ...key, y: deviceH / 2 };
  return { ...key, y: Math.min(deviceH - half, Math.max(half, key.y)) };
};

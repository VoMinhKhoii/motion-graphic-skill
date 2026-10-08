import React from 'react';
import { expo, io, lerp, ramp, rand } from '../time';

/**
 * Tile burst and return: a screen's own tiles (stat cards, chips, settings rows) burst out of the centre into a
 * wall in frame space, each one's bar or value drawing itself, then every tile flies back to its place on the
 * device as the device arrives behind them. The tiles become the screen. Ported from the launch film's
 * micronutrient wall (17 tiles: wall complete 1.75 s after the burst starts, held, then a 0.7 s return).
 *
 * All tiles are tw x th tile px. `render(i, bar)` draws tile i at that size; `bar` (0..1) is its draw-on
 * progress. Draw the device's copy of each tile with the same component, so the hand-off is invisible.
 * `home(i)` is where tile i's top-left sits on the device, in frame px (screen point through the camera), or
 * null for a tile that is off screen on the device: it rises out of frame instead. `homeK` is the camera's
 * scale (frame px per tile px on the device).
 * `s` is seconds since the burst starts; `back` (0..1) is the return's progress (the film: ramp over 0.7 s, io).
 */
export const TileBurst: React.FC<{
  s: number;
  back: number;
  W: number;
  H: number;
  n: number;
  tw: number;
  th: number;
  cols: number;
  render: (i: number, bar: number) => React.ReactNode;
  home: (i: number) => { x: number; y: number } | null;
  homeK: number;
  g?: number;
  gap?: number;
  stagger?: number;
  enter?: number;
  spin?: number;
}> = ({ s, back, W, H, n, tw: TW, th: TH, cols, render, home, homeK, g = 0.53, gap = 20, stagger = 0.045, enter = 0.55, spin = 24 }) => {
  if (back >= 0.999) return null;
  const tw = TW * g, th = TH * g;
  const rows = Math.ceil(n / cols);
  const gw = cols * tw + (cols - 1) * gap, gh = rows * th + (rows - 1) * gap;
  const x0 = W / 2 - gw / 2, y0 = H / 2 - gh / 2;
  return (
    <>
      {Array.from({ length: n }, (_, i) => {
        const col = i % cols, row = Math.floor(i / cols);
        const inRow = row === rows - 1 ? n - row * cols : cols; // the last row is centred
        const rx = x0 + ((cols - inRow) * (tw + gap)) / 2 + col * (tw + gap);
        const ry = y0 + row * (th + gap);
        const t0 = 0.08 + i * stagger;
        const a = ramp(s, t0, t0 + enter, expo);
        const rot = (rand(i * 7.7) - 0.5) * spin * (1 - a); // each tile spins in from its own small angle
        const drift = Math.sin(s * 0.9 + i) * 3; // the wall breathes while it holds
        const wallX = lerp(W / 2 - tw / 2, rx, a), wallY = lerp(H / 2 - th / 2, ry, a) + drift;
        // the return, staggered 0.025 s per tile inside `back`
        const bi = ramp(back, Math.min(0.5, i * 0.025), Math.min(1, 0.5 + i * 0.025), io);
        let x = wallX, y = wallY, sc = g * (0.35 + 0.65 * a), op = Math.min(1, a * 1.5);
        const to = home(i);
        if (to) {
          x = lerp(wallX, to.x, bi); y = lerp(wallY, to.y, bi); sc = lerp(sc, homeK, bi);
          op *= 1 - ramp(bi, 0.85, 1); // the device's own tile takes over in the last 15%
        } else {
          y = wallY - bi * H * 0.4; op *= 1 - bi;
        }
        const bar = ramp(s, t0 + 0.25, t0 + 0.95, expo); // draws itself after the tile has landed in the wall
        return (
          <div
            key={i}
            style={{
              position: 'absolute', left: x, top: y, width: TW, height: TH, transform: `scale(${sc}) rotate(${rot}deg)`, transformOrigin: '0 0', opacity: op,
              filter: `drop-shadow(0 ${14 * (1 - bi)}px ${22 * (1 - bi)}px rgba(20,20,30,0.18))`,
            }}
          >
            {render(i, bar)}
          </div>
        );
      })}
    </>
  );
};

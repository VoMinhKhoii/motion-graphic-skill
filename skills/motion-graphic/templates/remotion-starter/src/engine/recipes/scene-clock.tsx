import React from 'react';
import { useTheme } from '../theme';
import { lerp, ramp, rand } from '../time';

/**
 * Scene clock: a hand-drawn analog clock in a corner that carries a "day in the life" across scenes. Each scene
 * that shows it passes its own time range (`from` → `to`, minutes of the day); the hands sweep forward between
 * them, so the clock reads as one clock running through the film, never as a time stamp.
 *
 * Timing per scene (the worked example's values):
 *   0.00-0.20  the clock fades in (`enter`)
 *   0.05-0.60  the hands sweep from `from` to `to` (`sweep`), then hold
 * `at` shifts both to a later scene second (the clock arrives after the scene's first beat). `hide` (0..1) fades it
 * out under your own control: tie it to whatever leaves the frame (the last scene, a full-screen beat).
 * Give the next scene `from` = this scene's `to`, or the hands jump.
 *
 * The face is an ink circle that "boils" (re-drawn with a small wobble) 12 times a second, like hand-drawn
 * animation, from scene seconds, so it looks the same at any frame rate. Place it inside the layout area the
 * scene receives (`W` x `H` from Reel): in 9:16 that is the safe band, so the top-left corner is clear of the
 * platforms' top bar. `P` (portrait) picks the smaller size and margins.
 */
export const SceneClock: React.FC<{
  s: number;
  from: number;
  to: number;
  P: boolean;
  at?: number;
  sweep?: [number, number];
  enter?: number;
  hide?: number;
  ink?: string;
  face?: string;
  corner?: 'left' | 'right';
  W?: number;
}> = ({ s, from, to, P, at = 0, sweep = [0.05, 0.6], enter = 0.2, hide = 0, ink, face = 'rgba(250,250,250,0.82)', corner = 'left', W = 0 }) => {
  const th = useTheme();
  const t = s - at;
  const vis = ramp(t, 0, enter) * (1 - hide);
  if (vis <= 0.001) return null;
  const m = lerp(from, to, ramp(t, sweep[0], sweep[1]));
  const box = P ? 140 : 148, size = P ? 124 : 132;
  const mx = P ? 36 : 52, my = P ? 36 : 44;
  return (
    <div
      style={{
        position: 'absolute', left: corner === 'left' ? mx : W - mx - box, top: my, width: box, height: box, borderRadius: '50%',
        background: face, backdropFilter: 'blur(14px)', boxShadow: '0 10px 30px -8px rgba(30,20,10,0.35), 0 0 0 1px rgba(255,255,255,0.35)',
        display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: vis,
      }}
    >
      <HandClock minutes={m} boil={Math.floor(s * 12)} size={size} ink={ink ?? th.ink} />
    </div>
  );
};

/** "7:50" → 470 minutes. Times past midnight can go above 1440; the hands keep turning forward. */
export const hm = (t: string) => {
  const [h, m] = t.split(':').map(Number);
  return h * 60 + m;
};

/** A closed smooth path through `pts` (Catmull-Rom to cubic Bézier). */
const smooth = (pts: [number, number][]) => {
  const n = pts.length;
  let d = `M ${pts[0][0].toFixed(2)} ${pts[0][1].toFixed(2)}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n], p1 = pts[i], p2 = pts[(i + 1) % n], p3 = pts[(i + 2) % n];
    const c1 = [p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6];
    const c2 = [p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6];
    d += ` C ${c1[0].toFixed(2)} ${c1[1].toFixed(2)}, ${c2[0].toFixed(2)} ${c2[1].toFixed(2)}, ${p2[0].toFixed(2)} ${p2[1].toFixed(2)}`;
  }
  return `${d} Z`;
};

/** A slightly wobbly line from a to b, as a pen would draw it. */
const stroke = (a: [number, number], b: [number, number], seed: number, wob: number) => {
  const mx = (a[0] + b[0]) / 2 + (rand(seed) - 0.5) * wob;
  const my = (a[1] + b[1]) / 2 + (rand(seed + 1) - 0.5) * wob;
  return `M ${a[0].toFixed(2)} ${a[1].toFixed(2)} Q ${mx.toFixed(2)} ${my.toFixed(2)} ${b[0].toFixed(2)} ${b[1].toFixed(2)}`;
};

/**
 * The clock drawing: a wobbly ink circle (18 points, each nudged per boil step), four tick dashes and two
 * tapered hands. `minutes` is the time of day; `boil` is the boil step (any integer; change it 12 times a second).
 */
export const HandClock: React.FC<{ minutes: number; boil: number; size: number; ink: string }> = ({ minutes, boil, size, ink }) => {
  const c = size / 2, r = size * 0.42;
  const pts: [number, number][] = Array.from({ length: 18 }, (_, i) => {
    const a = (i / 18) * Math.PI * 2;
    const rr = r * (1 + (rand(boil * 31 + i) - 0.5) * 0.035);
    return [c + Math.cos(a) * rr, c + Math.sin(a) * rr];
  });
  const ticks = [0, 1, 2, 3].map((q) => {
    const a = (q / 4) * Math.PI * 2 - Math.PI / 2;
    return stroke([c + Math.cos(a) * r * 0.78, c + Math.sin(a) * r * 0.78], [c + Math.cos(a) * r * 0.9, c + Math.sin(a) * r * 0.9], boil * 7 + q, 1.2);
  });
  const hand = (turn: number, len: number, seed: number) => {
    const a = turn * Math.PI * 2 - Math.PI / 2;
    return stroke([c - Math.cos(a) * r * 0.08, c - Math.sin(a) * r * 0.08], [c + Math.cos(a) * len, c + Math.sin(a) * len], boil * 13 + seed, 1.6);
  };
  const sw = size * 0.028;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ overflow: 'visible' }}>
      <g fill="none" stroke={ink} strokeLinecap="round" strokeLinejoin="round">
        <path d={smooth(pts)} strokeWidth={sw} />
        {ticks.map((d, i) => <path key={i} d={d} strokeWidth={sw * 0.9} />)}
        <path d={hand(((minutes / 60) % 12) / 12, r * 0.5, 1)} strokeWidth={sw * 1.25} />
        <path d={hand((minutes % 60) / 60, r * 0.74, 2)} strokeWidth={sw * 0.95} />
      </g>
      <circle cx={c} cy={c} r={sw * 0.9} fill={ink} />
    </svg>
  );
};

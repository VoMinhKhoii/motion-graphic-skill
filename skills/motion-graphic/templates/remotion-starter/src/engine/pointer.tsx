import React from 'react';
import { useTheme } from './theme';
import { io, lerp } from './time';

/**
 * Pointer events in device px: arrive at a point, tap it, or drag between two points.
 * Time a `tap` to the frame where the recording reacts (the button darkens, the field focuses), not to when you
 * think a finger would press. Read that frame off the recording; see capture/frame_pts.py and the rec.py log.
 */
export type PtrEvent =
  | { kind: 'at'; t: number; x: number; y: number }
  | { kind: 'tap'; t: number; x: number; y: number }
  | { kind: 'drag'; t: number; t1: number; x: number; y: number; x1: number; y1: number };

/** Where the pointer is at time s. A move takes at most `travel` seconds before its event and arcs slightly. */
export function pointerAt(evs: PtrEvent[], s: number, travel = 0.36) {
  let px = evs[0].x, py = evs[0].y, prevEnd = -1e9;
  for (const e of evs) {
    const start = Math.max(prevEnd, e.t - travel);
    if (s < e.t) {
      if (s <= start) return { x: px, y: py };
      const u = io((s - start) / Math.max(1e-6, e.t - start));
      const dx = e.x - px, dy = e.y - py;
      const arc = Math.sin(Math.PI * u) * 0.1;
      return { x: px + dx * u - dy * arc, y: py + dy * u + dx * arc };
    }
    if (e.kind === 'drag') {
      if (s <= e.t1) {
        const u = io((s - e.t) / (e.t1 - e.t));
        return { x: lerp(e.x, e.x1, u), y: lerp(e.y, e.y1, u) };
      }
      px = e.x1; py = e.y1; prevEnd = e.t1;
    } else {
      px = e.x; py = e.y; prevEnd = e.t;
    }
  }
  return { x: px, y: py };
}

/**
 * The press (0..1) and the ripple age (seconds, -1 = none) at time s. A tap presses in over the 0.08 s before
 * its time and releases over 0.12 s after; the ripple runs 0.5 s from the tap.
 */
export function clickAt(evs: PtrEvent[], s: number) {
  let press = 0, ripple = -1;
  for (const e of evs) {
    const d = s - e.t;
    if (e.kind === 'tap') {
      if (d > -0.08 && d < 0.12) press = Math.max(press, d < 0 ? (d + 0.08) / 0.08 : 1 - d / 0.12);
      if (d >= 0 && d < 0.5) ripple = d;
    }
    if (e.kind === 'drag') {
      if (s >= e.t - 0.06 && s <= e.t1 + 0.06) press = 1;
      if (d >= 0 && d < 0.5) ripple = d;
    }
  }
  return { press, ripple };
}

/**
 * The pointer: a pointing hand, fingertip on the point. It glides between events, dips on the press and leaves
 * a ring. It is drawn in frame space through `map` (from useCam), so its size never changes with the camera.
 * It fades in 0.45 s before the first event and out 0.45 s after the last. `size` is frame px (64-74 reads well).
 * `ring` defaults to the theme's `accentSolid`.
 */
export const Pointer: React.FC<{ evs: PtrEvent[]; s: number; map: (x: number, y: number) => { x: number; y: number }; size: number; travel?: number; ring?: string }> = ({ evs, s, map, size, travel = 0.36, ring }) => {
  const th = useTheme();
  const p = pointerAt(evs, s, travel);
  const c = clickAt(evs, s);
  const f = map(p.x, p.y);
  const first = evs[0].t, last = Math.max(...evs.map((e) => (e.kind === 'drag' ? e.t1 : e.t)));
  const vis = Math.min(1, Math.max(0, (s - (first - 0.45)) / 0.2)) * Math.min(1, Math.max(0, (last + 0.45 - s) / 0.2));
  if (vis <= 0.001) return null;
  const u = size / 32; // drawn on a 32-unit grid, fingertip at (12, 1.5)
  return (
    <div style={{ position: 'absolute', left: f.x, top: f.y, width: 0, height: 0, opacity: vis, pointerEvents: 'none' }}>
      {c.ripple >= 0 && (
        <div
          style={{
            position: 'absolute', left: -size * 0.45, top: -size * 0.45, width: size * 0.9, height: size * 0.9, borderRadius: '50%',
            border: `${size * 0.06}px solid ${ring ?? th.accentSolid}`, opacity: 0.85 * (1 - c.ripple / 0.5), transform: `scale(${0.35 + c.ripple * 2.4})`,
          }}
        />
      )}
      <svg
        width={size} height={size} viewBox="0 0 32 32"
        style={{ position: 'absolute', left: -12 * u, top: -1.5 * u, transform: `scale(${1 - 0.1 * c.press}) translateY(${c.press * 1.2 * u}px)`, transformOrigin: `${12 * u}px ${1.5 * u}px`, filter: 'drop-shadow(0 3px 6px rgba(0,0,0,0.32))' }}
      >
        <path
          d="M12 1.5C13.4 1.5 14.5 2.6 14.5 4L14.5 12.5C14.9 11.9 15.6 11.5 16.4 11.5C17.6 11.5 18.5 12.3 18.6 13.4C19 12.9 19.6 12.6 20.3 12.6C21.5 12.6 22.4 13.5 22.5 14.6C22.9 14.2 23.5 14 24.1 14C25.3 14 26.2 14.9 26.2 16.1L26.2 21.5C26.2 26 23.3 29.5 18.8 29.5L15.5 29.5C12.6 29.5 10.6 28.2 9.1 26L5.2 20.3C4.5 19.3 4.7 18 5.6 17.3C6.6 16.6 7.9 16.8 8.6 17.7L9.5 18.9L9.5 4C9.5 2.6 10.6 1.5 12 1.5Z"
          fill="#FFFFFF" stroke="#141413" strokeWidth={1.35} strokeLinejoin="round"
        />
        <path d="M14.5 12.5L14.5 17.2M18.6 13.4L18.6 17.6M22.5 14.6L22.5 18" stroke="#141413" strokeWidth={1.1} strokeLinecap="round" fill="none" />
      </svg>
    </div>
  );
};

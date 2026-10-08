import React from 'react';
import { expo, io, lerp, ramp } from '../time';
import { useTheme } from '../theme';

/**
 * Feed docking: people gather as avatars around the frame, then each one flies into its own post in a feed
 * on the device, and the post opens at the moment the avatar lands. Two parts that share arrival times:
 *   FeedStack       the feed on the screen: rows that open one by one, pushing the rows below them down
 *   DockingAvatars  the avatars in frame space: appear, orbit, gather to the top, fly along an arc, vanish on landing
 * Times are scene seconds. The launch film's numbers are the defaults.
 */

/** A feed row: its height in screen px, and when it arrives (undefined = there from the start). */
export type FeedRow = { id: string; h: number; arrive?: number };

/** How open a row is at s: 0..1, opening from arrive - 0.06 to arrive + 0.3 with an expo ease (0.36 s). */
export const rowOpen = (row: FeedRow, s: number) => (row.arrive === undefined ? 1 : ramp(s, row.arrive - 0.06, row.arrive + 0.3, expo));

/** The top of row `id` at time s, in screen px. Rows above it that are still opening move it. */
export const rowTop = (rows: FeedRow[], id: string, s: number, top: number) => {
  let y = top;
  for (const r of rows) {
    if (r.id === id) return y;
    y += r.h * rowOpen(r, s);
  }
  return y;
};

/**
 * The rows, stacked from `top` (screen px), each clipped to its open height. A row's content slides down from
 * 35% above its slot, fades in faster than it opens (opacity = 1.4 x open) and scales from 0.97.
 * `render(row)` draws one row's content at full size (left 0, width w).
 */
export const FeedStack: React.FC<{ rows: FeedRow[]; s: number; top: number; x: number; w: number; render: (row: FeedRow) => React.ReactNode }> = ({ rows, s, top, x, w, render }) => {
  let y = top;
  return (
    <>
      {rows.map((row) => {
        const g = rowOpen(row, s);
        const sy = y;
        y += row.h * g;
        if (g <= 0.001) return null;
        return (
          <div key={row.id} style={{ position: 'absolute', left: x, top: sy, width: w, height: row.h * g, overflow: 'hidden' }}>
            <div style={{ position: 'absolute', left: 0, top: -(1 - g) * row.h * 0.35, width: w, height: row.h, opacity: Math.min(1, g * 1.4), transform: `scale(${0.97 + 0.03 * g})`, transformOrigin: '50% 0' }}>
              {render(row)}
            </div>
          </div>
        );
      })}
    </>
  );
};

/** A placeholder avatar: a coloured circle with initials. Use real (licensed, consenting) photos in a real film. */
export const Avatar: React.FC<{ d: number; color: string; initials: string }> = ({ d, color, initials }) => {
  const th = useTheme();
  return (
    <div style={{ width: d, height: d, borderRadius: '50%', background: color, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: th.font, fontWeight: 600, fontSize: d * 0.38, color: '#FFFFFF', letterSpacing: -d * 0.01 }}>
      {initials}
    </div>
  );
};

export type Person = { id: string; initials: string; color: string; arrive: number };

/**
 * The avatars, in frame px. Each appears (staggered by `stagger`), rides a ring that turns at `spin` rad/s,
 * and the ring gathers (`gather`: it shrinks from R0 to R1, flattens to an ellipse 0.3 as tall, and rises from
 * cy0 to cy1). Over the last `fly` seconds before its arrival an avatar flies to `target(id)` along an arc
 * `arc` px high, shrinking to the slot's diameter and losing its white ring and shadow; it is removed 0.04 s
 * after landing, when the row's own avatar has taken over.
 * `target(id)` returns the docked avatar's centre and diameter in frame px: map the slot's screen point through
 * the camera, at the row's position on the landing frame (rowTop at arrive + 0.04). Not later: a row that
 * opens above it afterwards pushes it down, and a target read then sends the avatar to the wrong post.
 */
export const DockingAvatars: React.FC<{
  s: number;
  people: Person[];
  ring: { cx: number; cy0: number; cy1: number; R0: number; R1: number; d0: number; d1: number };
  target: (id: string) => { x: number; y: number; d: number };
  gather?: [number, number];
  stagger?: number;
  spin?: number;
  fly?: number;
  arc?: number;
}> = ({ s, people, ring, target, gather: gw = [0.55, 1.1], stagger = 0.07, spin = 0.4, fly: flyDur = 0.35, arc = 50 }) => {
  const gather = ramp(s, gw[0], gw[1], io);
  const R = lerp(ring.R0, ring.R1, gather);
  return (
    <>
      {people.map((p, i) => {
        if (s > p.arrive + 0.04) return null;
        const appear = ramp(s, 0.05 + i * stagger, 0.4 + i * stagger, expo);
        const a0 = (i / people.length) * Math.PI * 2 - Math.PI / 2 + s * spin;
        const home = { x: ring.cx + Math.cos(a0) * R, y: lerp(ring.cy0, ring.cy1, gather) + Math.sin(a0) * R * lerp(1, 0.3, gather) };
        const fly = ramp(s, p.arrive - flyDur, p.arrive, io);
        const tgt = target(p.id);
        const d = lerp(lerp(ring.d0, ring.d1, gather), tgt.d, fly);
        const x = lerp(home.x, tgt.x, fly), y = lerp(home.y, tgt.y, fly) - Math.sin(Math.PI * fly) * arc;
        return (
          <div
            key={p.id}
            style={{
              position: 'absolute', left: x - d / 2, top: y - d / 2, width: d, height: d, borderRadius: '50%', overflow: 'hidden', opacity: appear,
              transform: `scale(${0.6 + 0.4 * appear})`, boxShadow: `0 ${16 * (1 - fly)}px ${36 * (1 - fly)}px rgba(20,20,30,0.3), 0 0 0 ${6 * (1 - fly)}px #FFFFFF`,
            }}
          >
            <Avatar d={d} color={p.color} initials={p.initials} />
          </div>
        );
      })}
    </>
  );
};

import React from 'react';
import { lerp, ramp } from '../time';

/** A box in frame px, with its corner radius. */
export type Box = { x: number; y: number; w: number; h: number; r: number };

/** One side of a morph: content laid out at its own w x h, drawn at scale k, centred in the moving box. */
export type MorphSide = { w: number; h: number; k: number; node: React.ReactNode };

/** The box at progress p: every edge and the radius interpolated together. */
export const morphBox = (from: Box, to: Box, p: number): Box => ({
  x: lerp(from.x, to.x, p), y: lerp(from.y, to.y, p), w: lerp(from.w, to.w, p), h: lerp(from.h, to.h, p), r: lerp(from.r, to.r, p),
});

/**
 * Container morph: one rounded box changes shape (a phone screen into a browser window, a card into a full
 * screen) while its content crosses from `a` to `b` inside it. Each side keeps its own fixed scale and stays
 * centred in the box, so nothing stretches; the box's edges do the moving.
 *
 * `p` is the morph's progress, 0..1, already eased (the film: ramp(s, t, t + 0.5) with ease in-out, 0.5 s).
 * The content cross leaves a gap where only the box's `bg` shows, so the two layouts never double-expose:
 * `a` fades out over p 0.06..0.4 and `b` fades in over p 0.4..0.75 (the film's numbers).
 * The shadow grows with p (the window lifts as it opens). Draw the source device's body yourself behind it and
 * fade it out over p 0..0.25, so the bezel is gone before the box has visibly grown.
 */
export const ContainerMorph: React.FC<{
  p: number;
  from: Box;
  to: Box;
  a: MorphSide;
  b: MorphSide;
  bg: string;
  fadeOut?: [number, number];
  fadeIn?: [number, number];
  shadow?: number;
}> = ({ p, from, to, a, b, bg, fadeOut = [0.06, 0.4], fadeIn = [0.4, 0.75], shadow = 0.5 }) => {
  const r = morphBox(from, to, p);
  const aIn = 1 - ramp(p, fadeOut[0], fadeOut[1]);
  const bIn = ramp(p, fadeIn[0], fadeIn[1]);
  const side = (sd: MorphSide, opacity: number) =>
    opacity > 0.001 && (
      <div
        style={{
          position: 'absolute', left: (r.w - sd.w * sd.k) / 2, top: (r.h - sd.h * sd.k) / 2, width: sd.w, height: sd.h,
          transform: `scale(${sd.k})`, transformOrigin: '0 0', opacity,
        }}
      >
        {sd.node}
      </div>
    );
  return (
    <div
      style={{
        position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, borderRadius: r.r, overflow: 'hidden', background: bg,
        boxShadow: `0 50px 90px -40px rgba(20,20,30,${shadow * p})`,
      }}
    >
      {side(a, aIn)}
      {side(b, bIn)}
    </div>
  );
};

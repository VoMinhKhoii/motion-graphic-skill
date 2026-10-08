import React from 'react';
import { Img, staticFile } from 'remotion';
import { useBand } from './safe-band';
import { rand } from './time';

/** A full-bleed layer: covers the layout area plus the safe-band margins, so backgrounds reach the frame edges. */
const Full: React.FC<{ W: number; children: (H: number) => React.ReactNode; H: number; style?: React.CSSProperties }> = ({ W, H, children, style }) => {
  const { t, b } = useBand();
  return <div style={{ position: 'absolute', left: 0, top: -t, width: W, height: H + t + b, overflow: 'hidden', ...style }}>{children(H + t + b)}</div>;
};

/** One soft colour blob: an RGB triple "r,g,b" and its peak alpha. */
export type Blob = { rgb: string; a: number };

/**
 * A moving gradient world for text and title shots: a base colour, a soft linear sweep from the top (or the
 * bottom), and blobs that each drift on a slow orbit. Each blob is a radial gradient that fades to clear by 70%
 * of its ellipse, so nothing has an edge. Pass a different `seed` per shot: the layout changes, the style stays.
 * Use the product's own palette (its onboarding or marketing gradients), not a generic one.
 */
export const GradientWorld: React.FC<{ s: number; W: number; H: number; seed: number; base: string; sweep: [string, string]; blobs: Blob[]; strength?: number }> = ({ s, W, H, seed, base, sweep, blobs, strength = 1 }) => (
  <Full W={W} H={H} style={{ background: base }}>
    {(HH) => {
      const flip = rand(seed * 3.1) > 0.5;
      return (
        <>
          <div style={{ position: 'absolute', inset: 0, opacity: strength, background: `linear-gradient(${flip ? 180 : 0}deg, ${sweep[0]} 0%, ${sweep[1]} 26%, transparent 42%)` }} />
          {blobs.map((b, i) => {
            const r1 = rand(seed * 17 + i * 3.3), r2 = rand(seed * 29 + i * 7.1), r3 = rand(seed * 41 + i * 1.9);
            const hx = (0.12 + 0.76 * r1) * W, hy = (0.1 + 0.8 * r2) * HH;
            const sp = 0.35 + 0.35 * r3, ph = r1 * 6.28;
            const x = hx + Math.sin(s * sp + ph) * W * 0.06;
            const y = hy + Math.cos(s * sp * 0.8 + ph * 1.3) * HH * 0.05;
            const rx = (0.3 + 0.22 * r3) * Math.max(W, HH) * (1 + 0.06 * Math.sin(s * 0.9 + ph));
            const ry = rx * (0.62 + 0.25 * r2);
            const a = b.a * strength;
            return (
              <div
                key={i}
                style={{ position: 'absolute', left: x - rx, top: y - ry, width: rx * 2, height: ry * 2, background: `radial-gradient(closest-side, rgba(${b.rgb},${a}) 0%, rgba(${b.rgb},${a * 0.45}) 38%, rgba(${b.rgb},0) 70%)` }}
              />
            );
          })}
        </>
      );
    }}
  </Full>
);

/**
 * A photo as a world: cover-fit, blurred 6 px so the device in front stays the subject, dimmed, and pushed in
 * very slowly (0.4% per second) so it never sits dead still. `src` is a path under public/.
 * Use your own or generated images; never a stock photo you cannot redistribute.
 */
export const PhotoWorld: React.FC<{ s: number; W: number; H: number; src: string; blur?: number; dim?: number; fade?: number }> = ({ s, W, H, src, blur = 6, dim = 0.9, fade = 1 }) => (
  <Full W={W} H={H} style={{ background: '#1B1917', opacity: fade }}>
    {() => <Img src={staticFile(src)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.08 + s * 0.004})`, filter: `blur(${blur}px) saturate(0.95) brightness(${dim})` }} />}
  </Full>
);

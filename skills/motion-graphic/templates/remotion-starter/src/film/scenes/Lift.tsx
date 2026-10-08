import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Clips, type Seg } from '../../engine/clips';
import { CutOut } from '../../engine/cutout';
import { Pointer, type PtrEvent } from '../../engine/pointer';
import type { Ctx } from '../../engine/reel';
import { expo, ramp } from '../../engine/time';
import { Words } from '../../engine/type';
import { GradientWorld } from '../../engine/worlds';
import { REC, UI, WORLD } from '../config';

/**
 * Pattern: one component lifted out of the recording at hero scale, a one-line headline over it, and a tap.
 * The card is the recording's own pixels (held at src 11.0, when it is complete), cut 3 px inside its border
 * and given one clean border and a rounded corner. It rises in at 0.15 s; the tap at 1.6 s presses it.
 */
export const LIFT_DUR = 3.0;

const HOLD: Seg[] = [{ t0: 0, t1: 99, clip: REC.clip, src: 11.0, rate: 0 }];

export const Lift: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H } = c;
  const r = UI.card;
  const k = Math.min((W * 0.8) / r.w, (H * 0.5) / r.h);
  const rise = ramp(s, 0.15, 0.75, expo);
  const press = 1 - 0.025 * (ramp(s, 1.52, 1.6) - ramp(s, 1.62, 1.85));
  const cw = r.w * k, ch = r.h * k;
  const left = (W - cw) / 2, top = H * 0.6 - ch / 2 + (1 - rise) * H * 0.12;
  // recording px on the card → frame px, for the pointer
  const map = (x: number, y: number) => ({ x: left + (x - r.x) * k, y: top + (y - r.y) * k });
  const evs: PtrEvent[] = [
    { kind: 'at', t: 1.0, x: UI.accentBar.x + r.w * 0.42, y: UI.accentBar.y + r.h * 0.36 },
    { kind: 'tap', t: 1.6, ...UI.accentBar },
  ];
  return (
    <AbsoluteFill>
      <GradientWorld s={s + 4} W={W} H={H} seed={3} {...WORLD} />
      <div style={{ position: 'absolute', left: 0, right: 0, top: H * 0.2, transform: 'translateY(-50%)', display: 'flex', justifyContent: 'center' }}>
        <Words s={s} t0={0.1} lines={['Every answer, *one card.']} size={c.P ? 72 : 76} />
      </div>
      <div style={{ position: 'absolute', left, top, opacity: rise, transform: `scale(${press})` }}>
        <CutOut rect={r} screenW={REC.w} screenH={REC.h} k={k} radius={UI.cardRadius} edge={UI.cardEdge} edgeColor={UI.cardEdgeColor}>
          <Clips s={s} segs={HOLD} w={REC.w} h={REC.h} bg={REC.bg} />
        </CutOut>
      </div>
      <Pointer evs={evs} s={s} map={map} size={c.P ? 74 : 64} />
    </AbsoluteFill>
  );
};

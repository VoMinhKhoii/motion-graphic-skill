import React from 'react';
import { AbsoluteFill } from 'remotion';
import { type CamKey, useCam } from '../../engine/camera';
import { At, Device, IPHONE, onScreen } from '../../engine/device';
import type { Ctx } from '../../engine/reel';
import { TileBurst } from '../../engine/recipes/tile-burst';
import { io, ramp } from '../../engine/time';
import { GradientWorld } from '../../engine/worlds';
import { WORLD } from '../config';

/**
 * Recipe demo: tile burst and return. Twelve stat tiles burst out of the centre into a wall (one every
 * 0.045 s), each bar draws itself, the wall holds, then the phone rises in behind and ten tiles fly home into
 * its grid while the two that sit below the fold on the phone rise out of frame. Tiles are drawn here.
 */
export const TILES_DUR = 3.4;
const BURST = 0.2; // the first tile leaves the centre
const N = 12, ON_PHONE = 10;
const TW = 588, TH = 218; // tile px (= screen px on the phone)
const GRID = { x: 60, y: 420, gap: 24 }; // the phone's 2-column grid, screen px
const HUES = ['#7C8DB5', '#7CB59A', '#B58C7C', '#A27CB5', '#B5A97C', '#5F8FA8'];

const Tile: React.FC<{ i: number; bar: number }> = ({ i, bar }) => {
  const frac = 0.35 + 0.6 * ((i * 37) % 11) / 10; // each tile's own value
  return (
    <div style={{ position: 'relative', width: TW, height: TH, borderRadius: 28, background: '#FFFFFF' }}>
      <div style={{ position: 'absolute', left: 36, top: 36, width: 180 + (i % 3) * 30, height: 28, borderRadius: 8, background: '#9AA1AC' }} />
      <div style={{ position: 'absolute', left: 36, top: 82, width: 130, height: 48, borderRadius: 10, background: '#2A2D33' }} />
      <div style={{ position: 'absolute', left: 36, top: 160, width: TW - 72, height: 18, borderRadius: 9, background: '#ECEEF1' }} />
      <div style={{ position: 'absolute', left: 36, top: 160, width: (TW - 72) * frac * bar, height: 18, borderRadius: 9, background: HUES[i % HUES.length] }} />
    </div>
  );
};

const tilePos = (i: number) => ({ x: GRID.x + (i % 2) * (TW + GRID.gap), y: GRID.y + Math.floor(i / 2) * (TH + GRID.gap) });

const Stats: React.FC = () => (
  <div style={{ position: 'relative', width: IPHONE.w, height: IPHONE.h, background: '#F4F5F7' }}>
    <div style={{ position: 'absolute', left: 72, top: 200, width: 380, height: 80, borderRadius: 12, background: '#2A2D33' }} />
    <div style={{ position: 'absolute', left: 72, top: 310, width: 260, height: 36, borderRadius: 10, background: '#C9CDD4' }} />
    {Array.from({ length: ON_PHONE }, (_, i) => (
      <div key={i} style={{ position: 'absolute', left: tilePos(i).x, top: tilePos(i).y }}>
        <Tile i={i} bar={1} />
      </div>
    ))}
  </div>
);

export const TilesDemo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H, P } = c;
  const kN = 0.5;
  const keys: CamKey[] = [{ t: 0, x: (IPHONE.w + 2 * IPHONE.bezel) / 2, y: 1550, k: kN, snap: true }];
  const { cam, map } = useCam(c, keys);
  // the wall is complete (every bar drawn) by about 1.75; it holds, then unites into the phone
  const phoneIn = ramp(s, 2.1, 2.65, io);
  const back = ramp(s, 2.2, 2.9, io);
  const home = (i: number) => {
    if (i >= ON_PHONE) return null;
    const q = onScreen(IPHONE, tilePos(i).x, tilePos(i).y);
    return map(q.x, q.y);
  };
  return (
    <AbsoluteFill>
      <GradientWorld s={s + 6} W={W} H={H} seed={11} {...WORLD} />
      {phoneIn > 0.001 && (
        <At cx={cam.x} cy={cam.y} k={cam.k} fx={W / 2} fy={H / 2 + (1 - phoneIn) * 220} opacity={phoneIn}>
          <Device spec={IPHONE}>
            <Stats />
          </Device>
        </At>
      )}
      <TileBurst
        s={s - BURST} back={back} W={W} H={H} n={N} tw={TW} th={TH} cols={P ? 3 : 4} g={P ? 0.5 : 0.48} gap={P ? 18 : 22}
        render={(i, bar) => <Tile i={i} bar={bar} />} home={home} homeK={cam.k}
      />
    </AbsoluteFill>
  );
};

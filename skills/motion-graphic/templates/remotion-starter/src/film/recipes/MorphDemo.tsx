import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Clips, type Patch, type Seg } from '../../engine/clips';
import { At, BROWSER, Device, IPHONE, deviceSize } from '../../engine/device';
import type { Ctx } from '../../engine/reel';
import { ContainerMorph } from '../../engine/recipes/container-morph';
import { io, ramp } from '../../engine/time';
import { GradientWorld } from '../../engine/worlds';
import { PHONE_REC, WEB_REC, WORLD } from '../config';

/**
 * Recipe demo: container morph. The phone app (held on its finished frame) becomes the same product's web app:
 * the phone body fades over the first quarter, the screen's box grows into the browser window in 0.5 s, and the
 * two layouts cross inside it with a gap between them. Both sides are the sample clips (generated media).
 */
export const MORPH_DUR = 2.6;
const T = 0.8; // the morph starts

const PHONE_HOLD: Seg[] = [{ t0: 0, t1: 99, clip: 'sample', src: 11.0, rate: 0 }];
const WEB_HOLD: Seg[] = [{ t0: 0, t1: 99, clip: 'sample_web', src: 11.0, rate: 0 }];
// cover the sample's leaked debug badge in both apps, 6 px over its edge (see Demo.tsx)
const cover = (rec: typeof PHONE_REC | typeof WEB_REC): Patch[] => {
  const b = rec.ui.debugBadge;
  return [{ clip: rec.clip, from: 0, x: b.x - 6, y: b.y - 6, w: b.w + 12, h: b.h + 12, fill: rec.bg }];
};

export const MorphDemo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H } = c;
  const p = ramp(s, T, T + 0.5, io);
  // the phone, whole, centred
  const ph = IPHONE, pd = deviceSize(ph);
  const k0 = Math.min((H * 0.86) / pd.h, (W * 0.9) / pd.w);
  const px = W / 2 - (pd.w * k0) / 2, py = H / 2 - (pd.h * k0) / 2;
  const from = { x: px + ph.bezel * k0, y: py + ph.bezel * k0, w: ph.w * k0, h: ph.h * k0, r: ph.radius * k0 };
  // the browser window, fitted to 90% of the width or 80% of the height
  const bd = deviceSize(BROWSER);
  const kb = Math.min((W * 0.9) / bd.w, (H * 0.8) / bd.h);
  const to = { x: W / 2 - (bd.w * kb) / 2, y: H / 2 - (bd.h * kb) / 2, w: bd.w * kb, h: bd.h * kb, r: BROWSER.radius * kb };
  return (
    <AbsoluteFill>
      <GradientWorld s={s} W={W} H={H} seed={5} {...WORLD} />
      {p < 0.25 && (
        <At cx={0} cy={0} k={k0} fx={px} fy={py} opacity={1 - ramp(p, 0, 0.25)}>
          <Device spec={ph}>
            <div />
          </Device>
        </At>
      )}
      <ContainerMorph
        p={p}
        from={from}
        to={to}
        bg={BROWSER.screenBg}
        a={{ w: ph.w, h: ph.h, k: k0, node: <Clips s={s} segs={PHONE_HOLD} w={ph.w} h={ph.h} bg={PHONE_REC.bg} patches={cover(PHONE_REC)} /> }}
        b={{
          w: bd.w, h: bd.h, k: kb,
          node: (
            <Device spec={BROWSER}>
              <Clips s={s} segs={WEB_HOLD} w={BROWSER.w} h={BROWSER.h} bg={WEB_REC.bg} patches={cover(WEB_REC)} />
            </Device>
          ),
        }}
      />
    </AbsoluteFill>
  );
};

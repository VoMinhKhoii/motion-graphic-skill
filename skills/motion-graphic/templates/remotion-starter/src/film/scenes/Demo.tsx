import React from 'react';
import { AbsoluteFill } from 'remotion';
import { type CamKey, fitBox, holdEdges, useCam } from '../../engine/camera';
import { Bridge, Clips, type Patch, type Seg } from '../../engine/clips';
import { At, Device, OnScreen, deviceSize, onRec } from '../../engine/device';
import { Pointer, type PtrEvent } from '../../engine/pointer';
import type { Ctx } from '../../engine/reel';
import { PhotoWorld } from '../../engine/worlds';
import { DEVICE, REC, UI } from '../config';

/**
 * Pattern: the device with a real recording, a camera that moves then holds, and pointer taps timed to the
 * frames where the app reacts. The source timeline is in scripts/make_sample_clip.sh; both sample clips (phone
 * and web) share it, so this edit works for every device preset in config.ts.
 *
 * The edit (scene second → source second):
 *   0.00-0.90  hold Home (src 1.0, rate 0) while the camera settles and the pointer arrives
 *   0.90-1.20  real speed through the tap: the input focuses at src 2.0 = scene 0.90, the tap's frame
 *   1.20-2.65  typing at 2x (src 2.5 → 5.4): one letter every 0.06 s on screen, still letter by letter
 *   2.65-3.25  real speed into Send: src 6.0, the button's flash, lands on scene 3.00, the second tap
 *   3.25-3.60  0.35 s of the "thinking" dots: enough to read as work, the other 1.0 s of stall is cut
 *   3.60-5.80  the result pops in at src 7.62; a 0.3 s bridge dissolves the pre-pop frame over the pop,
 *              then the rows land at real speed (src 7.9, 8.4, 8.9 = scene 3.88, 4.38, 4.88)
 *   5.80-7.40  real speed: the "saved" toast at src 10.5 = scene 6.50
 */
export const DEMO_DUR = 7.4;

const CLIP = REC.clip;
export const SEGS: Seg[] = [
  { t0: 0, t1: 0.9, clip: CLIP, src: 1.0, rate: 0 },
  { t0: 0.9, t1: 1.2, clip: CLIP, src: 2.0, rate: 1 },
  { t0: 1.2, t1: 2.65, clip: CLIP, src: 2.5, rate: (5.4 - 2.5) / 1.45 },
  { t0: 2.65, t1: 3.25, clip: CLIP, src: 5.65, rate: 1 },
  { t0: 3.25, t1: 3.6, clip: CLIP, src: 6.25, rate: 1 },
  { t0: 3.6, t1: 5.8, clip: CLIP, src: 7.62, rate: 1 },
  { t0: 5.8, t1: DEMO_DUR + 1, clip: CLIP, src: 9.8, rate: 1 },
];
export const BRIDGE = { t: 3.6, dur: 0.3, clip: CLIP, src: 6.55 };
/**
 * The leaked debug badge, covered with the app's own background for the whole clip. The cover is 6 px larger
 * than the badge on every side: H.264's 4:2:0 chroma bleeds a saturated colour 1-2 px past its edge (more in a
 * scaled-down file), and an exact-size patch leaves a faint coloured outline.
 */
const PAD = 6;
const B = UI.debugBadge;
export const PATCHES: Patch[] = [{ clip: CLIP, from: 0, x: B.x - PAD, y: B.y - PAD, w: B.w + 2 * PAD, h: B.h + 2 * PAD, fill: REC.bg }];

export const Demo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H } = c;
  const D = deviceSize(DEVICE);
  const pt = (x: number, y: number) => onRec(DEVICE, REC, x, y);
  const input = pt(UI.input.x + UI.input.w / 2, UI.input.y + UI.input.h / 2);
  const send = pt(UI.send.x, UI.send.y);
  const card = pt(UI.card.x + UI.card.w / 2, UI.card.y + UI.card.h / 2);
  const whole = fitBox(c, D.w, D.h, 0.92);
  const z = REC.zoom(whole);
  const keys: CamKey[] = [
    { t: 0, x: D.w / 2, y: D.h / 2, k: whole, snap: true },
    { t: 0.45, x: input.x, y: input.y, k: z.input }, // down to the input as the pointer arrives; held while typing
    { t: 2.6, x: send.x - D.w * 0.14, y: send.y, k: z.send }, // punch in on Send before it is pressed
    { t: 3.3, x: card.x, y: card.y, k: z.card }, // up to where the result lands; held while the rows land
    { t: 5.6, x: D.w / 2, y: D.h / 2, k: whole }, // out to the whole device for the toast
  ].map((k) => holdEdges(c, k, D.h, 40));
  const { cam, map } = useCam(c, keys);
  const evs: PtrEvent[] = [
    { kind: 'at', t: 0.3, x: D.w * 0.75, y: input.y - D.h * 0.17 },
    { kind: 'tap', t: 0.9, x: input.x - 200, y: input.y },
    { kind: 'at', t: 1.5, x: D.w * 0.72, y: input.y + D.h * 0.066 }, // out of the way of the letters
    { kind: 'tap', t: 3.0, ...send },
    { kind: 'at', t: 3.7, x: D.w * 0.8, y: card.y + D.h * 0.18 },
  ];
  const sw = REC.w, sh = REC.h;
  return (
    <AbsoluteFill>
      <PhotoWorld s={s} W={W} H={H} src="img/sample_room.jpg" />
      <At cx={cam.x} cy={cam.y} k={cam.k} fx={W / 2} fy={H / 2}>
        <Device spec={DEVICE}>
          <OnScreen spec={DEVICE} rec={REC}>
            <Clips s={s} segs={SEGS} w={sw} h={sh} patches={PATCHES} bg={REC.bg} />
            <Bridge s={s} {...BRIDGE} w={sw} h={sh} patches={PATCHES} />
          </OnScreen>
        </Device>
      </At>
      <Pointer evs={evs} s={s} map={map} size={c.P ? 74 : 64} />
    </AbsoluteFill>
  );
};

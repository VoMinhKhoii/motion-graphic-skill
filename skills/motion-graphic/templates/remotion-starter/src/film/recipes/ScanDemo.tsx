import React from 'react';
import { AbsoluteFill } from 'remotion';
import { fitBox } from '../../engine/camera';
import { At, Device, IPHONE, deviceSize } from '../../engine/device';
import type { Ctx } from '../../engine/reel';
import { Viewfinder, flashAt, pulseAt } from '../../engine/recipes/scanner';
import { expo, io, lerp, ramp } from '../../engine/time';
import { GradientWorld } from '../../engine/worlds';
import { WORLD } from '../config';

/**
 * Recipe demo: scanner composite. The "camera" is a drawn desk with a product box and a printed barcode (a
 * valid EAN-13 of a made-up code); the scanner chrome is drawn white-on-black and screen-blended over it, the
 * way a capture of the app's empty scanner screen would be. The picture moves from wide onto the code in 1 s
 * (a 1.4x push) with a handheld drift, the guide pulses "found" at 1.45 s, and the shot flashes at 1.95 s, held still.
 */
export const SCAN_DUR = 2.6;
const SHOT = 1.95;

// the guide in screen px, and the barcode's centre in picture px
const GUIDE = { x: 240, y: 1060, w: 840, h: 460 };
const CODE = { x: 1250, y: 1950 };
const PIC = { w: 2400, h: 4000 }; // tall enough to cover the screen at the widest zoom

// EAN-13: left digits in L or G code by the first digit's parity pattern, right digits in R code
const L = ['0001101', '0011001', '0010011', '0111101', '0100011', '0110001', '0101111', '0111011', '0110111', '0001011'];
const G = ['0100111', '0110011', '0011011', '0100001', '0011101', '0111001', '0000101', '0010001', '0001001', '0010111'];
const R = ['1110010', '1100110', '1101100', '1000010', '1011100', '1001110', '1010000', '1000100', '1001000', '1110100'];
const PAR = ['LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG', 'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL'];
const ean13 = (code: string) => {
  const d = code.split('').map(Number);
  let m = '101';
  for (let i = 1; i <= 6; i++) m += PAR[d[0]][i - 1] === 'L' ? L[d[i]] : G[d[i]];
  m += '01010';
  for (let i = 7; i <= 12; i++) m += R[d[i]];
  return m + '101';
};

const Barcode: React.FC<{ code: string; w: number; h: number }> = ({ code, w, h }) => {
  const m = ean13(code), mw = w / (m.length + 14);
  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
      <rect width={w} height={h} fill="#FBFAF7" />
      {m.split('').map((b, i) => (b === '1' ? <rect key={i} x={(i + 7) * mw} y={h * 0.1} width={mw + 0.2} height={h * 0.75} fill="#151412" /> : null))}
    </svg>
  );
};

/** The "camera picture": a desk, a mug, a notebook and a product box with a barcode panel. All drawn. */
const Desk: React.FC = () => (
  <div style={{ position: 'relative', width: PIC.w, height: PIC.h, background: 'linear-gradient(160deg, #B9B2A6, #8F877B)' }}>
    <div style={{ position: 'absolute', left: 120, top: 260, width: 700, height: 900, borderRadius: 30, background: '#6E7B8C', transform: 'rotate(-8deg)' }} />
    <div style={{ position: 'absolute', left: 1700, top: 2500, width: 520, height: 520, borderRadius: '50%', background: '#E9E4DA', boxShadow: 'inset 0 0 0 60px #D6CFC2' }} />
    <div style={{ position: 'absolute', left: 800, top: 1000, width: 900, height: 1300, borderRadius: 40, background: '#C9D3E0', boxShadow: '0 60px 80px -30px rgba(0,0,0,0.45)' }}>
      <div style={{ position: 'absolute', left: 80, top: 100, width: 520, height: 90, borderRadius: 14, background: '#3F4A5A' }} />
      <div style={{ position: 'absolute', left: 80, top: 230, width: 360, height: 50, borderRadius: 12, background: '#8996A8' }} />
      <div style={{ position: 'absolute', left: 150, top: 800, width: 600, height: 300 }}>
        <Barcode code="5901234123457" w={600} h={300} />
      </div>
    </div>
  </div>
);

/** The scanner's chrome, white on black: corner brackets around the guide, a hint, a shutter. */
const Chrome: React.FC<{ found: number }> = ({ found }) => {
  const g = GUIDE, k = 90, sw = 12;
  const corners = [
    `M${g.x},${g.y + k} V${g.y} H${g.x + k}`, `M${g.x + g.w - k},${g.y} H${g.x + g.w} V${g.y + k}`,
    `M${g.x},${g.y + g.h - k} V${g.y + g.h} H${g.x + k}`, `M${g.x + g.w - k},${g.y + g.h} H${g.x + g.w} V${g.y + g.h - k}`,
  ];
  return (
    <svg width={IPHONE.w} height={IPHONE.h} viewBox={`0 0 ${IPHONE.w} ${IPHONE.h}`} style={{ position: 'absolute', inset: 0 }}>
      <rect width={IPHONE.w} height={IPHONE.h} fill="#000" />
      {corners.map((d, i) => <path key={i} d={d} fill="none" stroke="#FFF" strokeWidth={sw} strokeLinecap="round" />)}
      {found > 0 && <rect x={g.x} y={g.y} width={g.w} height={g.h} rx={56} fill="none" stroke="#7CD39A" strokeWidth={10} opacity={found} />}
      <rect x={410} y={880} width={500} height={56} rx={28} fill="#FFF" opacity={0.85} />
      <circle cx={IPHONE.w / 2} cy={2560} r={92} fill="none" stroke="#FFF" strokeWidth={10} />
      <circle cx={IPHONE.w / 2} cy={2560} r={72} fill="#FFF" />
    </svg>
  );
};

export const ScanDemo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H } = c;
  const D = deviceSize(IPHONE);
  const k = fitBox(c, D.w, D.h, 0.94) * (c.P ? 1 : 0.84);
  const rise = ramp(s, 0, 0.4, expo);
  const move = ramp(s, 0.35, 1.35, io);
  const z = lerp(0.92, 1.3, move); // 0.92 just covers the 2868 px screen; 1.3 puts the 780 px code in the 840 px guide
  // the code lands in the guide's centre, not the screen's: offset the camera point by the gap, in picture px
  const gy = GUIDE.y + GUIDE.h / 2;
  const cam = { x: lerp(1300, CODE.x, move), y: lerp(2400, CODE.y + (IPHONE.h / 2 - gy) / z, move), z };
  const steady = 1 - ramp(s, SHOT - 0.1, SHOT);
  return (
    <AbsoluteFill>
      <GradientWorld s={s + 3} W={W} H={H} seed={9} {...WORLD} />
      <At cx={D.w / 2} cy={D.h / 2} k={k} fx={W / 2} fy={H / 2 + (1 - rise) * 300}>
        <Device spec={IPHONE}>
          <Viewfinder s={s} w={IPHONE.w} h={IPHONE.h} cam={cam} chrome={<Chrome found={pulseAt(s, 1.45)} />} flash={flashAt(s, SHOT)} drift={steady}>
            <Desk />
          </Viewfinder>
        </Device>
      </At>
    </AbsoluteFill>
  );
};

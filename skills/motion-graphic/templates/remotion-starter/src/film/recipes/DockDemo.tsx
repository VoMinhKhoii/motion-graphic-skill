import React from 'react';
import { AbsoluteFill } from 'remotion';
import { type CamKey, useCam } from '../../engine/camera';
import { At, Device, IPHONE, onScreen } from '../../engine/device';
import type { Ctx } from '../../engine/reel';
import { Avatar, DockingAvatars, type FeedRow, FeedStack, type Person, rowTop } from '../../engine/recipes/feed-dock';
import { expo, lerp, ramp } from '../../engine/time';
import { GradientWorld } from '../../engine/worlds';
import { WORLD } from '../config';

/**
 * Recipe demo: feed docking. Six placeholder people (coloured circles with initials, no real faces) appear in a
 * ring, the ring gathers to the top as the phone rises in, and each person flies into their own post; the post
 * opens as they land, 0.25 s apart, pushing the older posts down. The feed is drawn here, in screen px.
 */
export const DOCK_DUR = 3.2;

const PEOPLE: Person[] = [
  { id: 'you', initials: 'Y', color: '#5F6B7A', arrive: 1.15 },
  { id: 'a', initials: 'AL', color: '#7C8DB5', arrive: 1.3 },
  { id: 'b', initials: 'BK', color: '#B58C7C', arrive: 1.55 },
  { id: 'c', initials: 'CM', color: '#7CB59A', arrive: 1.8 },
  { id: 'd', initials: 'DN', color: '#A27CB5', arrive: 2.05 },
  { id: 'e', initials: 'EO', color: '#B5A97C', arrive: 2.3 },
];
const WHO = Object.fromEntries(PEOPLE.map((p) => [p.id, p]));
// newest first: each friend's post opens at the top as they arrive; "you" already has posts in the feed
const ROWS: (FeedRow & { who: string; photo: boolean })[] = [
  { id: 'e', who: 'e', h: 300, arrive: 2.3, photo: false },
  { id: 'd', who: 'd', h: 520, arrive: 2.05, photo: true },
  { id: 'c', who: 'c', h: 300, arrive: 1.8, photo: false },
  { id: 'b', who: 'b', h: 520, arrive: 1.55, photo: true },
  { id: 'you1', who: 'you', h: 520, photo: true },
  { id: 'you2', who: 'you', h: 300, photo: false },
  { id: 'a', who: 'a', h: 300, arrive: 1.3, photo: false },
  { id: 'you3', who: 'you', h: 520, photo: true },
];
const SLOT_OF: Record<string, string> = { you: 'you1', a: 'a', b: 'b', c: 'c', d: 'd', e: 'e' };
const TOP = 430; // the feed starts under the header (screen px)
const AV = { x: 60, y: 48, d: 96 }; // the avatar inside a post
const TABS: [number, number][] = [[72, 140], [232, 260], [512, 220], [752, 200]]; // group tabs under the title: [x, width]

const Post: React.FC<{ row: (typeof ROWS)[number] }> = ({ row }) => {
  const p = WHO[row.who];
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: 1248, height: row.h - 24, borderRadius: 36, background: '#FFFFFF' }}>
      <div style={{ position: 'absolute', left: AV.x, top: AV.y }}>
        <Avatar d={AV.d} color={p.color} initials={p.initials} />
      </div>
      <div style={{ position: 'absolute', left: 184, top: 62, width: 260, height: 30, borderRadius: 8, background: '#2A2D33' }} />
      <div style={{ position: 'absolute', left: 184, top: 108, width: 140, height: 22, borderRadius: 8, background: '#D5D8DE' }} />
      {row.photo ? (
        <div style={{ position: 'absolute', left: 60, top: 176, width: 1128, height: row.h - 24 - 216, borderRadius: 24, background: `linear-gradient(135deg, ${p.color}55, ${p.color}AA)` }} />
      ) : (
        <>
          <div style={{ position: 'absolute', left: 60, top: 180, width: 900, height: 28, borderRadius: 8, background: '#C9CDD4' }} />
          <div style={{ position: 'absolute', left: 60, top: 226, width: 620, height: 28, borderRadius: 8, background: '#C9CDD4' }} />
        </>
      )}
    </div>
  );
};

const Feed: React.FC<{ s: number }> = ({ s }) => (
  <div style={{ position: 'relative', width: IPHONE.w, height: IPHONE.h, background: '#F4F5F7', overflow: 'hidden' }}>
    <div style={{ position: 'absolute', left: 72, top: 200, width: 420, height: 80, borderRadius: 12, background: '#2A2D33' }} />
    {TABS.map(([x, w], i) => (
      <div key={i} style={{ position: 'absolute', left: x, top: 320, width: w, height: 64, borderRadius: 32, background: i ? '#E1E4E9' : '#2A2D33' }} />
    ))}
    <FeedStack rows={ROWS} s={s} top={TOP} x={36} w={1248} render={(row) => <Post row={row as (typeof ROWS)[number]} />} />
  </div>
);

export const DockDemo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H, P } = c;
  const kF = 0.6; // about two thirds of the phone in view
  const topY = (H / 2 - 30) / (P ? kF : kF * 0.84); // the camera point that puts the phone's top 30 px below the frame top
  const keys: CamKey[] = [{ t: 0, x: (IPHONE.w + 2 * IPHONE.bezel) / 2, y: topY, k: kF, snap: true }];
  const { cam, map } = useCam(c, keys);
  const phoneIn = ramp(s, 0.7, 1.2, expo);
  const target = (id: string) => {
    const row = ROWS.find((r) => r.id === SLOT_OF[id])!;
    const y = rowTop(ROWS, row.id, WHO[id].arrive + 0.04, TOP); // where the row is at the landing frame
    const q = onScreen(IPHONE, 36 + AV.x + AV.d / 2, y + AV.y + AV.d / 2);
    return { ...map(q.x, q.y), d: AV.d * cam.k };
  };
  return (
    <AbsoluteFill>
      <GradientWorld s={s + 2} W={W} H={H} seed={7} {...WORLD} />
      <At cx={cam.x} cy={cam.y} k={cam.k * lerp(0.85, 1, phoneIn)} fx={W / 2} fy={H / 2 + (1 - phoneIn) * H * 0.55} opacity={phoneIn}>
        <Device spec={IPHONE}>
          <Feed s={s} />
        </Device>
      </At>
      <DockingAvatars
        s={s}
        people={PEOPLE}
        target={target}
        ring={{ cx: W / 2, cy0: H * 0.5, cy1: H * (P ? 0.14 : 0.16), R0: P ? 300 : 260, R1: P ? 170 : 160, d0: P ? 168 : 150, d1: P ? 92 : 84 }}
      />
    </AbsoluteFill>
  );
};

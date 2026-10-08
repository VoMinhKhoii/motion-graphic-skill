import React from 'react';
import { AbsoluteFill } from 'remotion';
import type { Ctx } from '../../engine/reel';
import { SceneClock, hm } from '../../engine/recipes/scene-clock';
import { ramp } from '../../engine/time';
import { Words } from '../../engine/type';
import { GradientWorld } from '../../engine/worlds';
import { WORLD } from '../config';

/**
 * Recipe demo: scene clock. Three short beats stand in for three scenes of a day; each passes its own time range
 * and the next one starts where the last ended (7:50 → 8:12 → 12:40 → 19:05). In a film each range goes in its
 * own scene with `at` 0; here one scene fakes three by shifting `at`, so the clock re-enters on each cut as it
 * would at a scene start. It fades out with `hide` at the end.
 */
export const CLOCK_DUR = 3.8;
const BEATS = [
  { at: 0, from: hm('7:50'), to: hm('8:12'), line: 'Breakfast', seed: 2 },
  { at: 1.2, from: hm('8:12'), to: hm('12:40'), line: 'Lunch', seed: 5 },
  { at: 2.4, from: hm('12:40'), to: hm('19:05'), line: 'Dinner', seed: 9 },
];

export const ClockDemo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H, P } = c;
  const i = s >= BEATS[2].at ? 2 : s >= BEATS[1].at ? 1 : 0;
  const b = BEATS[i];
  const next = BEATS[i + 1]?.at;
  return (
    <AbsoluteFill>
      <GradientWorld s={s} W={W} H={H} seed={b.seed} {...WORLD} />
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <Words key={i} s={s} t0={b.at + 0.15} lines={[b.line]} size={P ? 88 : 96} exit={next !== undefined ? next - 0.35 : undefined} />
      </AbsoluteFill>
      <SceneClock s={s} at={b.at} from={b.from} to={b.to} P={P} W={W} hide={ramp(s, 3.4, 3.7)} />
    </AbsoluteFill>
  );
};

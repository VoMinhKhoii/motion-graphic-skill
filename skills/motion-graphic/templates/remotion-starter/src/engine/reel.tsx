import React from 'react';
import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig } from 'remotion';
import { BandProvider, bandFor } from './safe-band';
import { frameAt, ramp } from './time';

/**
 * What every scene receives. `s` is seconds since the scene started, the same at any frame rate; `frame` is the
 * composition frame since the scene's first frame (it depends on the fps: do not time anything with it). W x H is
 * the layout area: the safe band in 9:16, the whole frame otherwise. `P` is portrait (4:5 and 9:16), `tall` is
 * 9:16 only.
 */
export type Ctx = { s: number; frame: number; W: number; H: number; P: boolean; tall: boolean };

/**
 * One scene of the film. `dur` is its length in seconds. `fadeIn` (optional) starts it that many seconds early,
 * over the end of the previous scene, and dissolves it in: a crossfade that shortens the film by `fadeIn`.
 */
export type Scene = { id: string; dur: number; fadeIn?: number; C: React.FC<{ c: Ctx }> };

/** Scene start times (seconds) and the film's total length. */
export const timeline = (scenes: Scene[]) => {
  const starts: number[] = [];
  let t = 0;
  for (const sc of scenes) {
    t -= sc.fadeIn ?? 0;
    starts.push(t);
    t += sc.dur;
  }
  return { starts, duration: t };
};

/** Frames for a <Composition durationInFrames> at the composition's `fps`. */
export const durationInFrames = (scenes: Scene[], fps: number) => Math.round(timeline(scenes).duration * fps);

/**
 * Plays the scenes in order, one <Sequence> each, laid out in the safe band, the background `bg` full-bleed.
 * `band={false}` turns the 9:16 safe band off: for a store preview, where no platform draws over the frame.
 * Scene boundaries and every scene's clock come from the composition's fps.
 */
export const Reel: React.FC<{ scenes: Scene[]; bg: string; band?: boolean }> = ({ scenes, bg, band: withBand = true }) => {
  const { width: W, height: H, fps } = useVideoConfig();
  const band = withBand ? bandFor(W, H) : { t: 0, b: 0 };
  const { starts } = timeline(scenes);
  return (
    <BandProvider value={band}>
      <AbsoluteFill style={{ background: bg, overflow: 'hidden' }}>
        {scenes.map((sc, i) => {
          const f0 = frameAt(starts[i], fps);
          const f1 = frameAt(starts[i] + sc.dur, fps);
          return (
            <Sequence key={sc.id} name={sc.id} from={f0} durationInFrames={Math.max(1, f1 - f0)}>
              <div style={{ position: 'absolute', left: 0, top: band.t, width: W, height: H - band.t - band.b }}>
                <Host C={sc.C} W={W} H={H - band.t - band.b} P={H > W} tall={H / W > 1.6} fadeIn={sc.fadeIn ?? 0} t0={f0 / fps - starts[i]} />
              </div>
            </Sequence>
          );
        })}
      </AbsoluteFill>
    </BandProvider>
  );
};

/** `t0`: the scene second of the Sequence's first frame (0 when the scene starts exactly on a frame). */
const Host: React.FC<{ C: Scene['C']; W: number; H: number; P: boolean; tall: boolean; fadeIn: number; t0: number }> = ({ C, W, H, P, tall, fadeIn, t0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = t0 + frame / fps;
  const a = fadeIn > 0 ? ramp(s, 0, fadeIn) : 1;
  return (
    <AbsoluteFill style={{ opacity: a }}>
      <C c={{ s, frame, W, H, P, tall }} />
    </AbsoluteFill>
  );
};

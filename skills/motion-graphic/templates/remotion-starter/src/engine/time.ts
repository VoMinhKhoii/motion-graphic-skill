import { Easing, interpolate } from 'remotion';

/**
 * The frame rate the social compositions are registered at (Root.tsx). Nothing else reads it: the engine takes
 * the rate from the composition (`useVideoConfig().fps`), so one film renders the same at 60 fps and at 30 fps
 * (a store preview). Scene code works in seconds (`s`), never in frames.
 */
export const FILM_FPS = 60;

/** Seconds to a frame index at `fps`: the first frame at or after second `t`. Use it at <Sequence> boundaries. */
export const frameAt = (t: number, fps: number) => Math.ceil(t * fps - 1e-6);

/** Ease in-out (cubic): the default for moves that start and stop on screen. */
export const io = Easing.inOut(Easing.cubic);
/** Ease out (cubic): things that arrive. */
export const out = Easing.out(Easing.cubic);
/** Expo-out: fast attack, long settle. The "move, then hold" curve for type and UI entrances. */
export const expo = Easing.bezier(0.16, 1, 0.3, 1);
export const expoInOut = Easing.bezier(0.87, 0, 0.13, 1);

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

/** 0 before `a`, 1 after `b`, eased in between. The workhorse: `ramp(s, 1.2, 1.6)` is a 0.4 s fade from 1.2 s. */
export const ramp = (s: number, a: number, b: number, e: (t: number) => number = io) =>
  interpolate(s, [a, b], [0, 1], { ...clamp, easing: e });

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
/** Interpolate a scale in log space, so a zoom from 0.5 to 2 feels even all the way. */
export const logLerp = (a: number, b: number, t: number) => a * Math.pow(b / a, t);

/** Deterministic pseudo-random in [0, 1). Never use Math.random in a frame: every frame must render the same twice. */
export const rand = (n: number) => {
  const x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};

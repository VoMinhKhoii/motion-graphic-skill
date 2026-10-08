import React from 'react';
import { Img, OffthreadVideo, Sequence, staticFile, useVideoConfig } from 'remotion';
import { frameAt, io, ramp } from './time';

/**
 * One cut of a screen recording: scene seconds [t0, t1) play `clip` from source second `src` at `rate`.
 *   rate 1    real speed (results landing, animations: keep these real)
 *   rate 2-4  typing and scrolling, still letter by letter (see references/engine.md for the limits)
 *   rate 0    hold the frame at `src` (a still that the camera can move over)
 * A segment list is an edit decision list: the recording timeline is cut, not sped up as a whole.
 * `clip` names public/<dir>/<clip>.mp4. Recordings must be constant frame rate; see capture/vfr_to_cfr.sh. The
 * composition's fps can differ from the recording's (a 30 fps store cut of a 60 fps take): seeks are in seconds.
 */
export type Seg = { t0: number; t1: number; clip: string; src: number; rate: number };

/**
 * A cover laid over a recording while `clip` is between source seconds `from` and `to`: hides leaked UI (a
 * debug badge, a wrong clock, a notification) with an image of the right pixels, or with a flat `fill`.
 * Coordinates are recording pixels.
 */
export type Patch = { clip: string; from: number; to?: number; x: number; y: number; w: number; h: number; img?: string; fill?: string; radius?: number };

/** The segment playing at scene second `s` and the source second it shows, or null between segments. */
export const srcAt = (segs: Seg[], s: number) => {
  const g = segs.find((p) => s >= p.t0 && s < p.t1);
  return g ? { g, t: g.src + (s - g.t0) * g.rate } : null;
};

/**
 * Where segment `p` plays at composition rate `fps`: its first and last-plus-one frame (scene frames, with the
 * `offset` added), and the source second its first frame shows. The first frame is the first one at or after
 * t0, and the source time is read at that frame, so every frame shows exactly `srcAt(segs, s)` at any fps.
 */
export const segWindow = (p: Seg, fps: number, offset = 0) => {
  const f0 = frameAt(p.t0 + offset, fps);
  const f1 = frameAt(p.t1 + offset, fps);
  return { f0, n: Math.max(1, f1 - f0), src0: p.src + (f0 / fps - offset - p.t0) * p.rate };
};

/**
 * The recordings at their native size (w x h), one segment at a time, with patches on top. Every segment is
 * its own <Sequence> with an <OffthreadVideo>; only the live one is displayed.
 * `offset`: when you pass a shifted clock (s = sceneSeconds - 3) for a nested sub-timeline, pass offset 3, so the
 * Sequences (which always run on the scene's own clock) line up with it.
 */
export const Clips: React.FC<{ s: number; segs: Seg[]; w: number; h: number; patches?: Patch[]; bg?: string; offset?: number; dir?: string }> = ({ s, segs, w, h, patches = [], bg = '#FFFFFF', offset = 0, dir = 'rec' }) => {
  const { fps } = useVideoConfig();
  const now = srcAt(segs, s);
  const live = patches.filter((p) => now && p.clip === now.g.clip && now.t >= p.from && (p.to === undefined || now.t < p.to));
  return (
    <div style={{ position: 'relative', width: w, height: h, background: bg, overflow: 'hidden' }}>
      {segs.map((p, i) => {
        const { f0, n, src0 } = segWindow(p, fps, offset);
        return (
          <Sequence key={i} from={f0} durationInFrames={n} layout="none">
            <OffthreadVideo
              src={staticFile(`${dir}/${p.clip}.mp4`)}
              trimBefore={src0 * fps} // composition frames, so a fraction is fine: the seek is src0 seconds at any fps
              playbackRate={p.rate || 0.0001}
              muted
              style={{ position: 'absolute', inset: 0, width: w, height: h, display: now?.g === p ? 'block' : 'none' }}
            />
          </Sequence>
        );
      })}
      {live.map((p, i) =>
        p.img ? (
          <Img key={i} src={staticFile(p.img)} style={{ position: 'absolute', left: p.x, top: p.y, width: p.w, height: p.h, borderRadius: p.radius }} />
        ) : (
          <div key={i} style={{ position: 'absolute', left: p.x, top: p.y, width: p.w, height: p.h, background: p.fill, borderRadius: p.radius }} />
        ),
      )}
    </div>
  );
};

/**
 * A crossfade bridge over a cut-out app stall. When the app freezes (a debug build, a slow save) and then pops
 * its new state in one frame, cut the stall out of the segments and lay this over the first frames after the
 * cut: the last pre-stall frame (`clip` at `src`), dissolving away over `dur` seconds from scene second `t`.
 * The pop becomes a 0.3 s dissolve and whatever animates after it stays real.
 */
export const Bridge: React.FC<{ s: number; t: number; dur: number; clip: string; src: number; w: number; h: number; patches?: Patch[]; dir?: string }> = ({ s, t, dur, clip, src, w, h, patches, dir }) => {
  if (s < t || s >= t + dur) return null;
  return (
    <div style={{ position: 'absolute', inset: 0, opacity: 1 - ramp(s, t, t + dur, io) }}>
      <Clips s={s} segs={[{ t0: 0, t1: 1e4, clip, src, rate: 0 }]} w={w} h={h} patches={patches} dir={dir} />
    </div>
  );
};

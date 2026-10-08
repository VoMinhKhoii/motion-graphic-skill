import React from 'react';
import { AbsoluteFill } from 'remotion';
import { EndCard } from '../../engine/end-card';
import type { Ctx } from '../../engine/reel';
import { BRAND } from '../config';

/**
 * Pattern: the fade to the end card. The scene has `fadeIn: 0.4` in the reel, so it dissolves in over the
 * last 0.4 s of the previous scene; the wordmark lands at 0.5 s and the line 0.25 s after it.
 * To use an SVG wordmark: mark={{ img: 'img/wordmark.svg', w: 300 }}.
 */
export const END_DUR = 2.4;

export const End: React.FC<{ c: Ctx }> = ({ c }) => (
  <AbsoluteFill>
    <EndCard s={c.s} W={c.W} H={c.H} t0={0.4} mark={{ text: BRAND.name }} line={BRAND.line} bg="#0E0D0C" ink="#F8F7F4" />
  </AbsoluteFill>
);

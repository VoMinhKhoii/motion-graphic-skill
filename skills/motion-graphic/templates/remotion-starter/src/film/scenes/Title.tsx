import React from 'react';
import { AbsoluteFill } from 'remotion';
import type { Ctx } from '../../engine/reel';
import { useTheme } from '../../engine/theme';
import { expo, ramp } from '../../engine/time';
import { Typed } from '../../engine/type';
import { GradientWorld } from '../../engine/worlds';
import { BRAND, WORLD } from '../config';

/**
 * Pattern: a type-on title on a gradient. "Introducing" types at 26 letters/s with a caret, then the name opens
 * beside it (its box widens while the word rises out of a blur), then the whole line lifts away at 1.95 s.
 */
export const TITLE_DUR = 2.5;

export const Title: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H } = c;
  const th = useTheme();
  const size = c.P ? 96 : 104;
  const name = ramp(s, 0.58, 0.95, expo);
  const gone = ramp(s, 1.95, 2.3);
  const nameW = size * 0.62 * BRAND.name.length;
  return (
    <AbsoluteFill>
      <GradientWorld s={s} W={W} H={H} seed={1} {...WORLD} />
      <AbsoluteFill style={{ alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: size * 0.26 * name, opacity: 1 - gone, transform: `translateY(${-gone * 40}px) scale(${1 + gone * 0.04})`, filter: `blur(${gone * 10}px)` }}>
          <Typed s={s} t0={0.1} text="Introducing" size={size} cps={26} caretUntil={0.6} />
          <div style={{ width: nameW * name, height: size * 1.3, overflow: 'hidden', display: 'flex', alignItems: 'center' }}>
            <span
              style={{
                flexShrink: 0, fontFamily: th.font, fontSize: size, fontWeight: 700, letterSpacing: -size * 0.04, lineHeight: 1.2,
                backgroundImage: th.accent, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent',
                opacity: name, transform: `translateY(${(1 - name) * size * 0.4}px)`, filter: `blur(${(1 - name) * 8}px)`,
              }}
            >
              {BRAND.name}
            </span>
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

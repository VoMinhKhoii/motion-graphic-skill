import React from 'react';
import { useTheme } from './theme';
import { expo, ramp } from './time';

type Word = { w: string; accent?: boolean };
const parse = (line: string): Word[] => line.split(' ').map((w) => (w.startsWith('*') ? { w: w.slice(1), accent: true } : { w }));

/**
 * Headline type, word by word: each word rises 0.42 em out of a 9 px blur over 0.42 s (expo-out).
 * Write `*word` to mark an accent word (filled with theme.accent). `t0` starts the first word, `gap` staggers
 * the rest (0.07 s), `exit` (optional) lifts the block up and out over 0.35 s.
 * One or two lines, three to six words: the line is the subject of its shot.
 */
export const Words: React.FC<{
  s: number; t0: number; lines: string[]; size: number; gap?: number; exit?: number; weight?: number;
  color?: string; align?: 'center' | 'left'; lineHeight?: number; tracking?: number;
}> = ({ s, t0, lines, size, gap = 0.07, exit, weight = 600, color, align = 'center', lineHeight = 1.1, tracking = -0.035 }) => {
  const th = useTheme();
  let k = 0;
  const gone = exit === undefined ? 0 : ramp(s, exit, exit + 0.35);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: align === 'center' ? 'center' : 'flex-start', opacity: 1 - gone, transform: `translateY(${-gone * size * 0.5}px)`, filter: `blur(${gone * 10}px)` }}>
      {lines.map((line, li) => (
        <div key={li} style={{ display: 'flex', flexWrap: 'nowrap', gap: size * 0.25, fontFamily: th.font, fontSize: size, fontWeight: weight, color: color ?? th.ink, letterSpacing: size * tracking, lineHeight }}>
          {parse(line).map((wd, wi) => {
            const d = t0 + gap * k++;
            const a = ramp(s, d, d + 0.42, expo);
            return (
              <span
                key={wi}
                style={{
                  display: 'inline-block', opacity: a, transform: `translateY(${(1 - a) * size * 0.42}px)`, filter: `blur(${(1 - a) * 9}px)`,
                  ...(wd.accent ? { backgroundImage: th.accent, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', paddingBottom: size * 0.08 } : {}),
                }}
              >
                {wd.w}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

/**
 * Text typed in place, letter by letter, with a caret. `cps` letters per second from `t0` (16 reads as a fast
 * typist; 26 for a two-word title). The caret is solid while typing, then blinks at 2.2 Hz until `caretUntil`.
 */
export const Typed: React.FC<{ s: number; t0: number; text: string; size: number; cps?: number; caretUntil?: number; color?: string; weight?: number }> = ({ s, t0, text, size, cps = 16, caretUntil = 1e9, color, weight = 600 }) => {
  const th = useTheme();
  const n = Math.max(0, Math.min(text.length, Math.floor((s - t0) * cps)));
  const caretOn = s < caretUntil && (s < t0 + text.length / cps + 0.1 || Math.floor(s * 2.2) % 2 === 0);
  return (
    <span style={{ fontFamily: th.font, fontSize: size, fontWeight: weight, color: color ?? th.ink, letterSpacing: -size * 0.035, whiteSpace: 'pre' }}>
      {text.slice(0, n)}
      <span style={{ display: 'inline-block', width: size * 0.06, height: size * 0.95, marginLeft: size * 0.05, transform: `translateY(${size * 0.14}px)`, background: caretOn ? th.accentSolid : 'transparent', borderRadius: 2 }} />
    </span>
  );
};

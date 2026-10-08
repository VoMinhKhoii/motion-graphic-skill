import React from 'react';
import { Img, staticFile } from 'remotion';
import { useBand } from './safe-band';
import { useTheme } from './theme';
import { expo, ramp } from './time';

/**
 * The end card: the wordmark, then one line under it (availability, a URL, "Coming soon"). Nothing else.
 * `mark` is either an image path under public/ (an SVG wordmark) or plain text set in the theme font.
 * The wordmark lands at t0 + 0.1 (0.4 s, expo-out), the line 0.25 s later. `bg` covers the whole frame.
 */
export const EndCard: React.FC<{ s: number; W: number; H: number; t0?: number; mark: { img: string; w: number } | { text: string }; line: string; bg: string; ink: string; size?: number }> = ({ s, W, H, t0 = 0, mark, line, bg, ink, size = 1 }) => {
  const th = useTheme();
  const { t, b } = useBand();
  const a = ramp(s, t0 + 0.1, t0 + 0.5, expo);
  const l = ramp(s, t0 + 0.35, t0 + 0.75, expo);
  const markSize = Math.min(W, H) * 0.13 * size;
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: W, height: H }}>
      <div style={{ position: 'absolute', left: 0, right: 0, top: -t, bottom: -b, background: bg }} />
      <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: markSize * 0.3 }}>
        <div style={{ opacity: a, transform: `translateY(${(1 - a) * 16}px)`, filter: `blur(${(1 - a) * 6}px)` }}>
          {'img' in mark ? (
            <Img src={staticFile(mark.img)} style={{ width: mark.w * size }} />
          ) : (
            <div style={{ fontFamily: th.font, fontSize: markSize, fontWeight: 700, letterSpacing: -markSize * 0.04, color: ink }}>{mark.text}</div>
          )}
        </div>
        <div style={{ fontFamily: th.font, fontSize: markSize * 0.42, fontWeight: 400, letterSpacing: -markSize * 0.004, color: ink, opacity: l * 0.86, transform: `translateY(${(1 - l) * 12}px)` }}>{line}</div>
      </div>
    </div>
  );
};

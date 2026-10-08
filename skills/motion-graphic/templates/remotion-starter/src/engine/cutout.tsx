import React from 'react';

/**
 * Lifts one component out of a recording and shows it on its own, at any scale: a card, an input box, a chart.
 * The UI is real pixels, so it reads as the product, not a mock.
 *
 * The trick that makes it clean: cut `edge` px INSIDE the component's own border, then draw one fresh border of
 * the same width and colour in its place, with your own radius. Cutting on or outside the border shows page
 * background in the corners, a doubled edge, or the app's square fills poking past a rounded corner.
 *
 * `rect` is the component's outer box in recording px (measure it on a still). `children` is the recording at its
 * native size (usually <Clips .../>, at screenW x screenH). `k` scales the result: frame px per recording px.
 * The rect can change over time (a box that grows a line as text wraps): pass the current rect each frame.
 */
export const CutOut: React.FC<{
  rect: { x: number; y: number; w: number; h: number };
  screenW: number;
  screenH: number;
  k: number;
  radius: number;
  edge?: number;
  edgeColor?: string;
  bg?: string;
  shadow?: number;
  children: React.ReactNode;
}> = ({ rect, screenW, screenH, k, radius, edge = 0, edgeColor = 'transparent', bg = '#FFFFFF', shadow = 1, children }) => (
  <div
    style={{
      position: 'relative', boxSizing: 'border-box', width: rect.w * k, height: rect.h * k, borderRadius: radius * k,
      border: edge ? `${edge * k}px solid ${edgeColor}` : undefined, overflow: 'hidden', background: bg,
      boxShadow: shadow ? `0 ${40 * shadow}px ${80 * shadow}px -30px rgba(30,20,10,${0.35 * shadow})` : undefined,
    }}
  >
    <div style={{ position: 'absolute', left: -(rect.x + edge) * k, top: -(rect.y + edge) * k, width: screenW, height: screenH, transform: `scale(${k})`, transformOrigin: '0 0' }}>{children}</div>
  </div>
);

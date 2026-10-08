import React from 'react';

/**
 * Safe bands for 9:16 (TikTok, Reels, Shorts). The platforms draw their own top bar and a caption plus buttons
 * at the bottom. At 1080x1920 the band is y 140..1620: 140 px off the top, 300 px off the bottom. Scene layout
 * happens inside the band; backgrounds (and anything else wrapped in <Bleed>) still reach the frame's edges.
 *
 * 16:9 and 4:5 have no band: the whole frame is safe.
 */
export type Band = { t: number; b: number };

/** The band for a frame size. Any frame taller than 1.6:1 counts as 9:16; the band scales with width. */
export const bandFor = (W: number, H: number): Band => {
  if (H / W <= 1.6) return { t: 0, b: 0 };
  const u = W / 1080;
  return { t: Math.round(140 * u), b: Math.round(300 * u) };
};

const BandContext = React.createContext<Band>({ t: 0, b: 0 });
export const BandProvider = BandContext.Provider;
export const useBand = () => React.useContext(BandContext);

/**
 * Lets its children escape the safe band: a full-bleed box from the frame's top edge to its bottom edge, drawn
 * from inside a scene that is laid out in the band. Children get the full frame height as `H`.
 */
export const Bleed: React.FC<{ W: number; H: number; children: (H: number) => React.ReactNode }> = ({ W, H, children }) => {
  const { t, b } = useBand();
  return <div style={{ position: 'absolute', left: 0, top: -t, width: W, height: H + t + b }}>{children(H + t + b)}</div>;
};

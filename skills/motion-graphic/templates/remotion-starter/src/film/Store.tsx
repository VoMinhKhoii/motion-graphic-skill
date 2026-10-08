import React from 'react';
import { AbsoluteFill } from 'remotion';
import { Bridge, Clips } from '../engine/clips';
import { type Ctx, type Scene, Reel, durationInFrames } from '../engine/reel';
import { ThemeProvider } from '../engine/theme';
import { REC, THEME } from './config';
import { BRIDGE, DEMO_DUR, PATCHES, SEGS } from './scenes/Demo';

/**
 * Store preview (App Store app preview). Apple takes only screen captures of the app itself: no device frame,
 * no hands, no camera zoom into the UI. So the frame IS the app's screen: the recording fills it edge to edge
 * (scaled to cover; a 1320x2868 capture loses 2 px top and bottom at 886x1920), with no safe band, because no
 * platform draws over a store preview. Motion comes from the app and from the cuts of the segment list.
 *
 * Runs at 30 fps (Apple's maximum). It reuses the Demo scene's edit (segments, bridge, debug-badge patch), so the
 * same cuts land on the same source frames as in the 60 fps film. A real preview is 15-30 s: give it its own
 * scenes array of full-screen cuts, recorded on the device class it is for. Phone recordings only (PRESET iphone
 * or android). Render with render/store.sh.
 */
export const STORE_FPS = 30;

const StoreDemo: React.FC<{ c: Ctx }> = ({ c }) => {
  const { s, W, H } = c;
  const k = Math.max(W / REC.w, H / REC.h);
  return (
    <AbsoluteFill style={{ background: REC.bg }}>
      <div style={{ position: 'absolute', left: (W - REC.w * k) / 2, top: (H - REC.h * k) / 2, width: REC.w, height: REC.h, transform: `scale(${k})`, transformOrigin: '0 0' }}>
        <Clips s={s} segs={SEGS} w={REC.w} h={REC.h} patches={PATCHES} bg={REC.bg} />
        <Bridge s={s} {...BRIDGE} w={REC.w} h={REC.h} patches={PATCHES} />
      </div>
    </AbsoluteFill>
  );
};

export const STORE_SCENES: Scene[] = [{ id: 'store-demo', dur: DEMO_DUR, C: StoreDemo }];
export const STORE_FRAMES = durationInFrames(STORE_SCENES, STORE_FPS);

export const Store: React.FC = () => (
  <ThemeProvider value={THEME}>
    <Reel scenes={STORE_SCENES} bg={REC.bg} band={false} />
  </ThemeProvider>
);

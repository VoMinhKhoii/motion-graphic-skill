import React from 'react';
import { ramp } from '../time';

/**
 * Scanner composite: a camera screen (barcode, document, QR scanner) whose live picture is your own still
 * photo, under the app's real scanner chrome. A simulator cannot film a real object, so the film builds the
 * view: the picture is panned and zoomed like a phone being brought to the object, a small handheld drift rides
 * on top, and the chrome is laid over it with `mix-blend-mode: screen`.
 *
 * Why screen: capture the app's scanner screen with nothing in front of the camera (the simulator shows black),
 * and that capture is the chrome. Screen-blending makes its black parts transparent and keeps its white guide,
 * labels and buttons on top, without cutting anything out by hand. Coloured chrome brightens the picture a
 * little where it overlaps; that is how a real viewfinder looks too.
 *
 * `w` x `h` is the screen (recording px). `cam` is the picture point shown at the screen's centre (picture px)
 * and its scale `z`. `drift` scales the wobble (0 = held still, e.g. at the instant a photo is taken).
 * `chromeB` + `mix` crossfade to a second chrome (the app switching modes). `flash` (0..1) is a white flash.
 */
export const Viewfinder: React.FC<{
  s: number;
  w: number;
  h: number;
  cam: { x: number; y: number; z: number };
  chrome?: React.ReactNode;
  chromeB?: React.ReactNode;
  mix?: number;
  flash?: number;
  drift?: number;
  children: React.ReactNode;
}> = ({ s, w, h, cam, chrome, chromeB, mix = 0, flash = 0, drift = 1, children }) => {
  // the film's handheld wobble: two sines per axis, about +-8 px at drift 1
  const sx = (Math.sin(s * 2.1) * 6 + Math.sin(s * 5.3) * 2.5) * drift;
  const sy = (Math.cos(s * 1.7) * 5 + Math.sin(s * 4.1) * 2) * drift;
  const layer = (node: React.ReactNode, opacity: number) =>
    node && opacity > 0.001 ? <div style={{ position: 'absolute', inset: 0, mixBlendMode: 'screen', opacity }}>{node}</div> : null;
  return (
    <div style={{ position: 'relative', width: w, height: h, overflow: 'hidden', background: '#000', isolation: 'isolate' }}>
      <div style={{ position: 'absolute', left: w / 2, top: h / 2, transform: `translate(${-cam.x * cam.z + sx}px, ${-cam.y * cam.z + sy}px) scale(${cam.z})`, transformOrigin: '0 0' }}>{children}</div>
      {layer(chrome, 1 - mix)}
      {layer(chromeB, mix)}
      {flash > 0 && <div style={{ position: 'absolute', inset: 0, background: '#FFFFFF', opacity: flash }} />}
    </div>
  );
};

/** The shutter flash at `t`: up in 0.05 s, held 0.05 s, gone by t + 0.35 (the film's numbers). */
export const flashAt = (s: number, t: number) => ramp(s, t, t + 0.05) * (1 - ramp(s, t + 0.1, t + 0.35));

/** A "found it" pulse at `t`: in over 0.1 s, held 0.1 s, out over 0.1 s (the film's barcode-detected ring). */
export const pulseAt = (s: number, t: number) => ramp(s, t, t + 0.1) * (1 - ramp(s, t + 0.2, t + 0.3));

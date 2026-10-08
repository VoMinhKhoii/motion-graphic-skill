import React from 'react';

/**
 * A device, drawn in CSS: no bezel image is shipped. The screen is the recording's native size (e.g. 1320x2868
 * for a 6.9" iPhone simulator capture); the body adds `bezel` px all round, plus a top `bar` for a browser
 * window. All camera and pointer coordinates are "device px": the body's own pixels, origin at its top-left.
 */
export type DeviceSpec = {
  /** Screen size in recording pixels. */
  w: number;
  h: number;
  /** Screen corner radius, recording pixels. */
  radius: number;
  /** Body thickness around the screen. 0 draws a bare rounded screen. */
  bezel: number;
  /** Body colour (a browser's bar colour). */
  body: string;
  /** A camera-cutout pill at the top centre (iPhone): [width, height, top offset], or null for none. */
  island: [number, number, number] | null;
  /** A round punch-hole camera at the top centre (most Android phones): [diameter, top offset], or null. */
  punch?: [number, number] | null;
  /** A browser window's top bar height (dots and address field). 0 or absent for a phone. */
  bar?: number;
  /** The address shown in the browser bar. */
  url?: string;
  /** Fill shown behind the screen content (the app's own background). */
  screenBg: string;
};

/** An iPhone-like phone for 1320x2868 recordings (6.9" simulator at 3x). */
export const IPHONE: DeviceSpec = { w: 1320, h: 2868, radius: 190, bezel: 60, body: '#1C1C1E', island: [380, 112, 40], screenBg: '#F3F1EC' };

/**
 * A Pixel-like Android phone: 1080x2400 (20:9, what a Pixel 7/8 emulator records), smaller corners, a thinner
 * body, no island, a punch-hole camera.
 */
export const ANDROID: DeviceSpec = { w: 1080, h: 2400, radius: 104, bezel: 40, body: '#202124', island: null, punch: [52, 34], screenBg: '#F3F1EC' };

/**
 * A desktop browser window for a web-only or B2B product: a 1600x1000 page under a 76 px bar, no phone.
 * Record the page at this size (scripts/capture/web_screencast.cjs), or change w/h to your capture.
 */
export const BROWSER: DeviceSpec = { w: 1600, h: 1000, radius: 22, bezel: 0, body: '#E9E7E2', island: null, bar: 76, url: 'app.example.com', screenBg: '#F3F1EC' };

export const DEVICES = { iphone: IPHONE, android: ANDROID, browser: BROWSER };
export type DevicePreset = keyof typeof DEVICES;

const barOf = (d: DeviceSpec) => d.bar ?? 0;

/** The body's outer size in device px. */
export const deviceSize = (d: DeviceSpec) => ({ w: d.w + 2 * d.bezel, h: d.h + 2 * d.bezel + barOf(d) });

/** A point on the screen (recording px) to device px. */
export const onScreen = (d: DeviceSpec, x: number, y: number) => ({ x: x + d.bezel, y: y + d.bezel + barOf(d) });

/**
 * A point in input-tool coordinates to device px. iOS automation tools (idb, XCUITest) work in points; a 3x
 * screen has 3 recording px per point. `scale` is that ratio. Android's adb works in pixels: scale 1.
 */
export const fromPoints = (d: DeviceSpec, x: number, y: number, scale = 3) => onScreen(d, x * scale, y * scale);

/** A recording's size. When it differs from the screen (a sample clip on another device), it is fitted. */
export type RecSize = { w: number; h: number };

/** How a recording sits on the screen: scaled to the screen's width, centred top to bottom. k = 1 when they match. */
export const recFit = (d: DeviceSpec, rec: RecSize) => {
  const k = d.w / rec.w;
  return { k, x: 0, y: (d.h - rec.h * k) / 2 };
};

/** A point in recording px to device px, through recFit. */
export const onRec = (d: DeviceSpec, rec: RecSize, x: number, y: number) => {
  const f = recFit(d, rec);
  return onScreen(d, f.x + x * f.k, f.y + y * f.k);
};

/** Lays a recording (children laid out at rec.w x rec.h, e.g. <Clips>) onto the screen through recFit. */
export const OnScreen: React.FC<{ spec: DeviceSpec; rec: RecSize; children: React.ReactNode }> = ({ spec, rec, children }) => {
  const f = recFit(spec, rec);
  return <div style={{ position: 'absolute', left: f.x, top: f.y, width: rec.w, height: rec.h, transform: `scale(${f.k})`, transformOrigin: '0 0' }}>{children}</div>;
};

/** The browser window's top bar: three dots and an address field, on the body colour. */
const BrowserBar: React.FC<{ d: DeviceSpec }> = ({ d }) => {
  const b = barOf(d), dot = b * 0.18;
  return (
    <div style={{ position: 'absolute', left: 0, top: 0, width: d.w, height: b, display: 'flex', alignItems: 'center', borderBottom: '1px solid rgba(0,0,0,0.08)' }}>
      {[0, 1, 2].map((i) => (
        <span key={i} style={{ position: 'absolute', left: b * 0.42 + i * dot * 1.9, top: (b - dot) / 2, width: dot, height: dot, borderRadius: dot / 2, background: 'rgba(0,0,0,0.16)' }} />
      ))}
      <span
        style={{
          margin: '0 auto', width: d.w * 0.34, height: b * 0.5, borderRadius: b * 0.25, background: 'rgba(255,255,255,0.85)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontFamily: 'system-ui, -apple-system, Arial, sans-serif', fontSize: b * 0.24, color: 'rgba(0,0,0,0.5)',
        }}
      >
        {d.url}
      </span>
    </div>
  );
};

/**
 * The device: the screen (any children, laid out at w x h) inside a CSS body. `frame` (0..1) fades the body
 * away, leaving a bare rounded screen, for a beat that wants only the UI.
 */
export const Device: React.FC<{ spec: DeviceSpec; children: React.ReactNode; frame?: number }> = ({ spec: d, children, frame = 1 }) => {
  const { w, h } = deviceSize(d);
  const b = barOf(d);
  const on = frame > 0.001;
  return (
    <div style={{ position: 'relative', width: w, height: h }}>
      {on && (
        <div
          style={{
            position: 'absolute', inset: 0, borderRadius: d.radius + d.bezel, background: d.body, opacity: frame, overflow: 'hidden',
            boxShadow: b
              ? '0 0 0 1px rgba(0,0,0,0.12), 0 40px 90px -30px rgba(0,0,0,0.35)'
              : `0 0 0 ${Math.max(2, d.bezel * 0.06)}px rgba(255,255,255,0.18) inset, 0 60px 120px -40px rgba(0,0,0,0.45)`,
          }}
        >
          {b > 0 && <BrowserBar d={d} />}
        </div>
      )}
      <div
        style={{
          position: 'absolute', left: d.bezel, top: d.bezel + b, width: d.w, height: d.h, overflow: 'hidden', background: d.screenBg,
          // under a browser bar only the bottom corners are round
          borderRadius: b ? `0 0 ${d.radius}px ${d.radius}px` : d.radius,
        }}
      >
        {children}
        {d.island && on && (
          <div style={{ position: 'absolute', left: (d.w - d.island[0]) / 2, top: d.island[2], width: d.island[0], height: d.island[1], borderRadius: d.island[1] / 2, background: '#000', opacity: frame }} />
        )}
        {d.punch && on && (
          <div style={{ position: 'absolute', left: (d.w - d.punch[0]) / 2, top: d.punch[1], width: d.punch[0], height: d.punch[0], borderRadius: '50%', background: '#000', opacity: frame }} />
        )}
      </div>
    </div>
  );
};

/**
 * Places device-px content so that device point (cx, cy) sits at frame point (fx, fy), at scale k. Feed it the
 * camera: <At cx={cam.x} cy={cam.y} k={cam.k} fx={W / 2} fy={H / 2}>.
 */
export const At: React.FC<{ cx: number; cy: number; k: number; fx: number; fy: number; children: React.ReactNode; opacity?: number }> = ({ cx, cy, k, fx, fy, children, opacity = 1 }) => (
  <div style={{ position: 'absolute', left: fx - cx * k, top: fy - cy * k, transform: `scale(${k})`, transformOrigin: '0 0', opacity }}>{children}</div>
);

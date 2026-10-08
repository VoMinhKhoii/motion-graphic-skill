import { DEVICES, type DevicePreset, type DeviceSpec } from '../engine/device';
import type { Theme } from '../engine/theme';
import { DEFAULT_THEME } from '../engine/theme';
import type { Blob } from '../engine/worlds';

/**
 * Everything product-specific in the example film lives here. Replace it with your product's name, palette and
 * your recording's measured geometry. All rects are recording pixels, measured on stills of the recording.
 */
export const BRAND = { name: 'Acme', line: 'Available today' };

/** PLACEHOLDER accent, caret and tap ring (ink-grey): set `accent` and `accentSolid` from the brand inventory. */
export const THEME: Theme = { ...DEFAULT_THEME };

/**
 * The gradient world's palette. PLACEHOLDER: a deliberately plain grey-blue set so nobody ships it by accident.
 * Replace with the product's own gradients/colours from the brand inventory (its onboarding, marketing site or
 * design tokens). If the product has none, agree a small provisional palette with the owner first.
 */
export const WORLD = {
  base: '#F4F5F7',
  sweep: ['rgba(190,200,215,0.45)', 'rgba(190,200,215,0.12)'] as [string, string],
  blobs: [
    { rgb: '150,165,190', a: 0.3 },
    { rgb: '175,185,200', a: 0.28 },
    { rgb: '130,145,170', a: 0.24 },
    { rgb: '200,205,215', a: 0.32 },
  ] satisfies Blob[],
};

/**
 * Which device frames the recording: 'iphone', 'android' (Pixel-like, 20:9, punch-hole camera) or 'browser'
 * (a desktop window, no phone; for web-only and B2B products). The Demo and Lift scenes follow it.
 */
export const PRESET = 'iphone' as DevicePreset;

/**
 * The recordings and their measured geometry, in recording px. These are the sample clips from
 * scripts/make_sample_clip.sh: a phone app (used on both phones; on Android it is fitted to the 1080 px wide
 * screen) and a web app for the browser. `zoom(whole)` gives the camera scales the Demo scene uses for each beat;
`whole` is the scale that shows the whole device in the current format.
 * The phone clip's background is drawn as #F3F1EC but decodes as #F0EFEC after the H.264 round trip: measure
 * fill colours on a rendered still, never from the design tokens.
 */
export const PHONE_REC = {
  clip: 'sample', w: 1320, h: 2868, bg: '#F0EFEC',
  zoom: (_whole: number) => ({ input: 0.78, send: 1.05, card: 0.74 }), // absolute: the phone is portrait in every format
  ui: {
    input: { x: 60, y: 2560, w: 1200, h: 170 },
    send: { x: 1170, y: 2645 },
    card: { x: 60, y: 1340, w: 1200, h: 720 },
    cardEdge: 3,
    cardEdgeColor: '#DFDFD6', // measured on the decoded video
    cardRadius: 44, // the radius the lifted card is given (the sample draws square corners)
    accentBar: { x: 260, y: 1988 },
    debugBadge: { x: 1090, y: 58, w: 170, h: 54 },
  },
};
export const WEB_REC = {
  clip: 'sample_web', w: 1600, h: 1000, bg: '#F0EFEC',
  zoom: (whole: number) => ({ input: whole * 1.6, send: whole * 2.2, card: whole * 1.35 }), // relative: a wide window is small in 9:16
  ui: {
    input: { x: 360, y: 860, w: 1180, h: 80 },
    send: { x: 1485, y: 900 },
    card: { x: 360, y: 440, w: 1180, h: 340 },
    cardEdge: 3,
    cardEdgeColor: '#DFDFD6',
    cardRadius: 18,
    accentBar: { x: 520, y: 740 },
    debugBadge: { x: 1440, y: 20, w: 140, h: 40 },
  },
};

export const REC = PRESET === 'browser' ? WEB_REC : PHONE_REC;
export const UI = REC.ui;
export const DEVICE: DeviceSpec = { ...DEVICES[PRESET], screenBg: REC.bg };

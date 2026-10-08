import React from 'react';

/**
 * The film's look, read by the engine's type, pointer and end-card components. Set it once per film with
 * <ThemeProvider value={...}>; every field has a neutral default so a component also works on its own.
 */
export type Theme = {
  /** CSS font-family. Load real font files with @remotion/fonts before the first render (see README). */
  font: string;
  /** Main text colour. */
  ink: string;
  /** Accent: a CSS colour or gradient, used as a text fill for accent words. */
  accent: string;
  /** A solid accent colour for the caret (type.tsx) and the pointer's tap ring (pointer.tsx). */
  accentSolid: string;
};

/**
 * PLACEHOLDERS. The accent, caret and tap ring are deliberately ink-grey so nobody ships them by accident: the
 * brand inventory supplies the real values (the product's own accent gradient and its solid accent), or the
 * provisional palette agreed with the owner when the product has none. Set them in src/film/config.ts (THEME).
 */
export const DEFAULT_THEME: Theme = {
  font: "'Inter', 'SF Pro Display', system-ui, -apple-system, 'Helvetica Neue', Arial, sans-serif",
  ink: '#141413',
  accent: 'linear-gradient(92deg, #4A515C 0%, #7C8490 100%)',
  accentSolid: '#5F6670',
};

const ThemeContext = React.createContext<Theme>(DEFAULT_THEME);
export const ThemeProvider = ThemeContext.Provider;
export const useTheme = () => React.useContext(ThemeContext);

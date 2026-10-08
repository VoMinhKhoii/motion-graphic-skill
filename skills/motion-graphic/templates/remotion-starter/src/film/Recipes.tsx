import React from 'react';
import { type Scene, Reel, durationInFrames } from '../engine/reel';
import { FILM_FPS } from '../engine/time';
import { ThemeProvider } from '../engine/theme';
import { THEME, WORLD } from './config';
import { CLOCK_DUR, ClockDemo } from './recipes/ClockDemo';
import { DOCK_DUR, DockDemo } from './recipes/DockDemo';
import { MORPH_DUR, MorphDemo } from './recipes/MorphDemo';
import { SCAN_DUR, ScanDemo } from './recipes/ScanDemo';
import { TILES_DUR, TilesDemo } from './recipes/TilesDemo';

/**
 * The five production recipes (src/engine/recipes/), one demo scene each, on generated media only. Not part of
 * the film: scrub them in the studio (Recipes-45 etc.), copy the one you need into a scene, delete the rest.
 */
export const RECIPE_SCENES: Scene[] = [
  { id: 'morph', dur: MORPH_DUR, C: MorphDemo },
  { id: 'dock', dur: DOCK_DUR, C: DockDemo },
  { id: 'scan', dur: SCAN_DUR, C: ScanDemo },
  { id: 'tiles', dur: TILES_DUR, C: TilesDemo },
  { id: 'clock', dur: CLOCK_DUR, C: ClockDemo },
];

export const RECIPES_FRAMES = durationInFrames(RECIPE_SCENES, FILM_FPS);

export const Recipes: React.FC = () => (
  <ThemeProvider value={THEME}>
    <Reel scenes={RECIPE_SCENES} bg={WORLD.base} />
  </ThemeProvider>
);

import React from 'react';
import { type Scene, Reel, durationInFrames, timeline } from '../engine/reel';
import { ThemeProvider } from '../engine/theme';
import { FILM_FPS } from '../engine/time';
import { THEME, WORLD } from './config';
import { DEMO_DUR, Demo } from './scenes/Demo';
import { END_DUR, End } from './scenes/End';
import { LIFT_DUR, Lift } from './scenes/Lift';
import { TITLE_DUR, Title } from './scenes/Title';

/**
 * The example film: four scenes, one per pattern. Reorder, retime or add scenes here; each scene owns its own
 * clock (`c.s` starts at 0), so changing one scene's length never shifts the timing inside another.
 * `fadeIn` overlaps a scene with the end of the previous one and dissolves it in.
 */
export const SCENES: Scene[] = [
  { id: 'title', dur: TITLE_DUR, C: Title },
  { id: 'demo', dur: DEMO_DUR, C: Demo },
  { id: 'lift', dur: LIFT_DUR, fadeIn: 0.3, C: Lift },
  { id: 'end', dur: END_DUR, fadeIn: 0.4, C: End },
];

export const FILM_FRAMES = durationInFrames(SCENES, FILM_FPS);
/** Scene start times in seconds, for the sound cue sheet (scripts/sound/sfx_mix.py). */
export const SCENE_STARTS = Object.fromEntries(SCENES.map((sc, i) => [sc.id, timeline(SCENES).starts[i]]));

export const Film: React.FC = () => (
  <ThemeProvider value={THEME}>
    <Reel scenes={SCENES} bg={WORLD.base} />
  </ThemeProvider>
);

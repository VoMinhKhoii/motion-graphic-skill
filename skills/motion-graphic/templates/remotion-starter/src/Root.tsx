import React from 'react';
import { Composition } from 'remotion';
import { FILM_FPS } from './engine/time';
import { FILM_FRAMES, Film } from './film/Film';
import { RECIPES_FRAMES, Recipes } from './film/Recipes';
import { STORE_FPS, STORE_FRAMES, Store } from './film/Store';

/**
 * One film component, three formats. Composition ids allow letters, numbers and "-" only (no "_").
 *   Film-169  1920x1080  YouTube, X, the website
 *   Film-45   1080x1350  X and Threads feeds, Instagram feed
 *   Film-916  1080x1920  TikTok, Reels, Shorts (laid out in the safe band y 140..1620)
 * Recipes-*: the five recipe demos (src/film/Recipes.tsx), in the same three formats. Not part of the film.
 * Store-886x1920: an App Store app preview (iPhone 6.9"/6.5" portrait) at 30 fps: the recording full-screen, no
 *   device, no safe band (src/film/Store.tsx, render/store.sh). Opt-in: delete it if the film has no store cut.
 * Every composition can run at its own fps: the engine reads it from the composition.
 */
export const Root: React.FC = () => (
  <>
    <Composition id="Film-169" component={Film} durationInFrames={FILM_FRAMES} fps={FILM_FPS} width={1920} height={1080} />
    <Composition id="Film-45" component={Film} durationInFrames={FILM_FRAMES} fps={FILM_FPS} width={1080} height={1350} />
    <Composition id="Film-916" component={Film} durationInFrames={FILM_FRAMES} fps={FILM_FPS} width={1080} height={1920} />
    <Composition id="Recipes-169" component={Recipes} durationInFrames={RECIPES_FRAMES} fps={FILM_FPS} width={1920} height={1080} />
    <Composition id="Recipes-45" component={Recipes} durationInFrames={RECIPES_FRAMES} fps={FILM_FPS} width={1080} height={1350} />
    <Composition id="Recipes-916" component={Recipes} durationInFrames={RECIPES_FRAMES} fps={FILM_FPS} width={1080} height={1920} />
    <Composition id="Store-886x1920" component={Store} durationInFrames={STORE_FRAMES} fps={STORE_FPS} width={886} height={1920} />
  </>
);

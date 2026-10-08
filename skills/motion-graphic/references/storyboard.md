# Storyboard: every frame, signed off before any full render

A render takes 20–60 minutes and an owner's attention. A storyboard takes 5 minutes to look at and catches 80% of the problems. In the worked example one unreviewed render "lost some of that elegant look from the last version"; from then on every version went through a frames storyboard first, and no render was rejected for taste again.

## What a storyboard is

Real frames rendered from the actual edit, not sketches. Load `engine.md` first. Build the scene in the engine (`film/engine/`), render stills at the beats (`film/engine/render/stills.mjs`), and lay them out as a board in `film/boards/` (or an artifact or canvas if the session has one):
- **A plan board:**
  - the owner's notes from the last round, each with "what changed";
  - the scene list with start times and durations;
  - the sound plan;
  - the open questions.
- **Beat boards:** 6–8 frames per row, in order, each with its time, scene, "what you see" and "the move", one line each. Outline the frames that changed in this round.

Once the film exists, the storyboard is cheap: rendering 60–80 stills takes minutes.

**What may render before sign-off:** stills, contact sheets and short test clips of one move (a few seconds, to judge a transition's timing). **What waits:** the full film render in any format.

## Before footage exists

For the very first concept round, use stand-in footage: an existing recording, or the product's screenshots composited in the engine. Label stand-ins on the board ("stand-in meal until the real one is recorded"). Do not hand-draw UI; owners judge the real product.

## What to check on every board before sending

- **Zoom check.** Open dense frames at 2× and look for overlaps, clipped edges, doubled borders, leaked UI states and wrong radii. Contact sheets hide these.
- **Composition check.** Run it on every board's stills before the owner sees them:
  ```bash
  "$SKILL/scripts/research/pipeline/check_frames.py" film/engine/out/stills --baseline film/research/corpus/corpus.json --roles film/boards/roles.csv
  ```
  Pass the roles. The storyboard knows each beat's role, so write `roles.csv` beside the board, one row per still: `03_card.png,card`, `05_demo.png,demo`, `09_end.png,logo` (roles: card, demo, text_over, logo, other). Without it the role is guessed from OCR, and the guess cannot tell a card set in small type from a sparse UI page. It flags three things (`measuring.md`, Composition): a lone object on a void (nothing runs off the frame, a card, pill, device or cut-out floats, and content covers less than the corpus demo p25); a demo subject (a device, window or cut-out, never a line of type) seen from too far away; and a text card with small type, more than 3 lines or too many words. Type alone on its ground passes, and so does a sparse full-screen UI. Letterbox or pillarbox bars are cut off before measuring. Every FLAG needs a fix or a reason written on the board next to the frame. Without a corpus it uses defaults rounded from the worked example's lab corpus and says so. It does not judge whether a whole device beside a headline is big enough, or a pill whose shadow grazes the edge: judge those by eye.
- **Text.** 1–2 lines, short, and readable at phone size on the platform's feed.
- **Safe zones** for 9:16 (see `delivery.md`).
- **Every number is real.**
- **The brief's style checklist** (`quality-bar.md`): for the worked example, for instance, at most two loading words per analysis in every run shown.
- **Store previews:** every frame is the app's own screen at the store's size (`branches.md`).

## Presenting choices

When something needs a decision (an ending, a meal, a direction), put every option on the board with real frames, and ask in one question: the structured question tool if the session has one, otherwise one numbered prose question with lettered options. Two lessons:
- Owners may not see your chat prose, only the canvas and the question. Put the details, including exact text, in the place they look.
- Explain jargon with frames. "Hard cut on the total" needed two side-by-side frame pairs before the owner could judge it.

## Owner edits

Owners edit canvases directly (wording, layout). Before publishing a new version, re-read the live canvas and merge onto it; never overwrite their edits with your stale copy. With local HTML boards, the owner answers in prose by board and frame number ("B3 F5: shorter line"); number them so every note maps to one frame, and log the notes in `film/STATUS.md`.

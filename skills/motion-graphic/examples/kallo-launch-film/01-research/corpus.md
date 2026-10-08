# The reference corpus

What was collected for the Kallo film, how it was filtered, and how it was measured. Nothing here is a copy of a reference film. The films are named, linked where a public link is known, and described in numbers.

## Why the corpus exists

The first storyboards were drawn from memory of what "a frontier-lab launch film" looks like. None of the reference films had been opened. The owner rejected them:

> Did you actually watch the video produced by the X threads I show you? None of these are those direction? You think big tech and frontier labs would launch stuff like this?

The first reference that was actually downloaded (OpenAI's "Ultrafast") turned out to be a 3D toy-rocket split-screen metaphor with no UI in it at all. The premise of every direction on the board was wrong. Everything below was done after that.

## The accounts

The owner named four accounts as the taste reference ("clean and high fidelity on both typography and visual"):

| Account | Public page | Films downloaded | Kept as motion design |
|---|---|---|---|
| OpenAI | https://x.com/OpenAI | 32 | 21 |
| Claude (Anthropic) | https://x.com/claudeai | 31 | 23 |
| xAI (posted as SpaceXAI) | https://x.com/SpaceXAI | 31 | 17 |
| Manus | https://x.com/ManusAI | 31 | 24 |
| **Total** | | **125** | **85** |

Two Claude posts the owner pointed at directly during the reviews:
- https://x.com/claudeai/status/2102435511222890900 , used to show what "full-screen images" means (full-bleed imagery, never a lone object on an empty ground).
- https://x.com/claudeai/status/2100258492590207079 , used as the model for a camera that rides with the cursor and lands tight on the control before a click.

Google was added on 1 October, after the first full cut, as a source of motion vocabulary only: 8 films watched second by second, 38 in the measured pass. The owner set its limit:

> Google is more on a slow side. I want fast. Just a reference for possible kinds of motion.

## How the films were collected

- **Download.** Public X post videos download without a login using `yt-dlp`.
- **Listing an account's videos.** This is the hard part. Logged-out X shows nothing, and a backgrounded browser tab does not lazy-load more posts when scrolled. The listing was read from inside a signed-in browser tab. Do not script around an account's login or read its tokens to do this; ask the user to open the media tab, or to approve the method first.
- **YouTube channels** (used later for the teaser study) can be listed without a login: `yt-dlp --flat-playlist -j` on the channel's `/videos` and `/shorts` pages gives title, duration, URL and views per video.

## The inclusion rule: motion design only

The owner's brief excluded people and live action. The same rule was applied to the references, after the owner said "pls just take thosse motion vids only":

- A film is **out** if people are a subject anywhere in it: live action, or people filmed, drawn or generated as its imagery.
- A film **stays in** when people appear only incidentally inside the product's own screens (an avatar, a file thumbnail). Its techniques are then taken only from shots with no person in them.

Result: 85 of 125 kept, 40 left out.

Judgement calls that were shown to the owner as overridable:
- Claude "Opus 5.5" is kept. It uses filmed macro and space footage, but has no people.
- Claude "Fable 5.1" is out. It opens and closes on real footage of a bird.
- Four Manus films are out because people are part of their imagery: "Manus 1.6", the dragon-rider film, "Manus 2.0" and "Meeting Minutes".

## How the films were measured

There were three passes, each answering a different question.

### 1. The machine pass (every film)

A script broke each film into:
- the hook (the first 3 s as a strip of frames);
- a timestamped contact sheet;
- shots, by cut detection;
- the ending;
- a motion-energy curve (frame differences over time);
- the audio: a spectrogram and loudness over time.

This pass alone was not enough. Per-account notes were written from it, but they were never turned into decisions, and the next concept frames still put small food cut-outs in the middle of empty cream frames. No reference film does that. The owner:

> I just feel like you never watch those videos. Never distill any design direction.

### 2. The study passes (85 films): techniques with a proving frame

Eight study passes, each covering a set of one account's films, went through the 85 kept films and recorded every technique they could prove with a frame. Each technique was measured, not described:
- **sizes** as a share of the frame (cap height as % of frame height, component width as % of frame width);
- **timings** from 8–12 fps frame bursts around the moment;
- **colours** sampled from pixels;
- **loudness** from the audio track, for the sound cards.

The passes recorded 267 techniques. Merging duplicates gave 92 cards ([technique-cards.md](../../../library/research/technique-cards.md)), which were then clustered into 10 directions ([directions.md](../../../library/research/directions.md)). The model for this format was a treatment the owner had made earlier for a TikTok creator study: one card per technique with a real frame, a code, a name, when to use it, a measured recipe, a "for you" line and the source.

### 3. The distribution study (after the first cut): how the seconds are spent

The owner's review of the first full cut (v4) said the design and the motion were "not that peak". The cards described single moments well, but nothing said how a film spends its time: how much of it is product, how long a text card holds, how often something changes. So the films were watched again, for distribution rather than frames.

- **The watched pass.** 24 lab films (6 per account) plus 8 Google films were logged second by second: every segment (demo, standalone text, text over the demo, logo, other) and every transition with its type and length. That gave 298 logged transitions in the 24 lab films.
- **The measured pass.** 123 films (the 85 lab films plus 38 Google films) at 4 fps. Frame differences gave the cut count, and the motion between cuts was classified (still, in-frame motion, pan, zoom in, zoom out).
- **Twelve exemplar moves** were then pulled frame by frame: 13 frames at 10 fps (1.2 s) around each logged moment, to see exactly what moves and what holds still.

The two passes count cuts differently. The watched pass logs designed transitions; the measured pass counts every hard change in the picture, including flash cuts. Both are reported in [findings.md](../../../library/research/findings.md).

The films in the watched pass, with their lengths:

| Account | Films (length) |
|---|---|
| Claude | Computer use (45.0 s), Managed Agents (59.0 s), Artifacts (59.8 s), Plugins (63.2 s), Dispatch (73.2 s), Microsoft 365 (87.2 s) |
| Manus | Slides (16.3 s), Similarweb (29.9 s), Skills (32.5 s), Telegram (36.8 s), Manus Desktop (55.9 s), Browser (59.5 s) |
| OpenAI | Computer History (28.2 s), Memory (33.0 s), Codex app (42.9 s), Codex on mobile (64.0 s), Law (77.3 s), Financial Services (81.0 s) |
| xAI | Grok app (9.6 s), Which voice is real? (21.0 s), Grok on iPhone (24.2 s), Voice cloning (31.7 s), Grok in the terminal (43.4 s), Voice agents (45.9 s) |
| Google (motion only) | Android Drop (8.0 s), Chat / Spark (11.7 s), Skills (47.2 s), Gemini Spark (49.3 s), Spark clock (61.1 s), Google Fi (73.3 s), Gemma 4 (98.1 s), Pics (98.7 s) |

## What to copy from this for your own film

- Pick the reference accounts from the user's stated taste, then download a lot of them. 20–30 films per account was enough to see patterns; 125 in total was enough to measure medians.
- Filter by the brief's own rule (here: no people) before studying, so the techniques you collect are ones you are allowed to use.
- Measure moments (cards) and distributions (time budgets) separately. You need both.
- Do not design anything until the cards and directions exist and the user has seen them.

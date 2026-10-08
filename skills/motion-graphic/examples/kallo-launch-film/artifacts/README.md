# The working pages, archived

During the project, every decision was put in front of the owner as a page, not as chat text: a storyboard canvas with 82 boards, a teaser study and a launch-intro study. These are offline copies of the Kallo pages; the research pages of the same canvas (the reference collection and the motion study, 19 boards) and the teaser study are not about Kallo, so they live with the research in `../../../library/research/`. Both are offline copies, taken on 7 October 2026, so the whole trail survives without the original hosting. Open the files in a browser; no build step.

| Open | What it is |
|---|---|
| `storyboard-canvas/index.html` | The Kallo pages of the canvas (63 boards), page by page. Each page opens as one scroll of its boards; each board also opens alone at full size (1440 px wide). |
| `launch-intros.html` | Launch-screen intro directions for the app itself: the wordmark animates while the app loads underneath. Interactive. |

## The canvas pages, in the order they were made

| Page | Boards | What it shows |
|---|---|---|
| `round2.html` | 34 | Round 2 storyboards, four directions (A–D), each with a direction card, its references and 6–7 frames. Superseded: drawn before the references were properly distilled. Kept as the "before". |
| `films.html` | 6 | Five film concepts (K1–K5), each beat by beat with the decisions to make, plus the comparison and recommendation. |
| `k3.html` | 3 | K3 "One day", the chosen concept: the film, every beat, and the review trail. |
| `v7.html` | 5 | The v7 plan and storyboard. |
| `v9.html` | 8 | The v9 storyboard for sign-off: every frame before the render, changes outlined, the notes each pass answered. |
| `teaser.html` | 7 | Teaser directions A, B, C, then the owner's own flow in English and Vietnamese. |

The boards are the published state of the last day. Some show intermediate decisions that changed later; `../03-iterations.md` tells which.

## What is in the frames

- **Kallo's own frames** (storyboards, film stills, the rooms): made for this project, shared for reference only, like the rest of `../assets/` (see the repository licence).
- **Frames from reference films** (the "looks like" frames on the concept boards and the round-2 reference boards here; the reference collection, motion study and teaser study in `../../../library/research/`): stills from other companies' public films, each credited to its film and timestamp, kept as research commentary by the owner's decision. They belong to their owners. Do not reuse them as imagery, and do not copy them into your own public pages: the skill's own boards keep third-party frames private (`../../../references/distilling.md` §4).

## How the copy was made

The canvas was read file by file from its hosting, every image it referenced was downloaded, and each board's HTML was rewritten to point at the local copy (`img/`) instead of the hosting's asset store. The editor's runtime was stripped; the boards are plain HTML and CSS. One board (`boards/K3Film.html`) embeds four short MP4 clips of the film.

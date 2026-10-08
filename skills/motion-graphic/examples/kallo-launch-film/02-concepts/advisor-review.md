# Advisor review of K3 (v1 to v4)

The owner went to sleep on 30 September with one instruction: have a complete K3 film by morning, then iterate with two advisors, checking whether it is high class, catches viewers from different backgrounds, and would read as coming from a big-tech motion team.

The advisors were two independent reviewers, both **report-only** (they could read the renders and the code, but not edit):
- Codex (gpt-6.1-sol), run from the command line;
- a second Claude agent (Fable).

Each round, both got the same brief, the rendered film and a contact sheet, and returned a list of problems. The agent fixed what both agreed on, and rendered again.

## The three rounds

| Round | What the reviewers said | What changed |
|---|---|---|
| **1 · v1 (31 s)** | Both: the first 1.5 s is an empty gradient. The claim is on screen about 1 s at 20–30 px. Eight identical pushes. The split is rushed. "Typed carelessly" reads as a judgement of the viewer. The night comparison (1,579 kcal) cannot be reconciled on screen. Fable: the white clay device and a smudge of a sun read as a template. | A cold open inside the composer. The claim at 28/40/160 px, held 2.5 s. No strikethrough on the careless meal. A dark titanium phone edge. Silent pushes plus slow drifts. The real share flow. Gradient banding fixed by rendering PNG frames to ProRes, then x264 with `-tune grain`. |
| **2 · v3 (34 s)** | Both: the product's magic (text becomes items) happens off screen. The 7-day chart with one bar reads as an empty account. The share needs holds. The 4:5 web crop is wrong. Fable: the ingredient pills start late. The pizza shows 2,457 kcal while the ring says 681 left. The nutrition label mixes US and EU formats. | Frame 1 holds the food words. The parse plays on screen. The claim's number sits level with the card's total. An honest over-target ring. The night scene uses the log's own ring and vitamins. A UK/EU label, re-read by the real OCR. Speed-ramped holds. |
| **3 · v4 (34.75 s)** | Codex: "Ship: yes. The 4:5 Light can go out on X and Threads as is." Non-blocking: the web beat is small at feed size; the phone under the claim in 4:5 is small; the Nutrition "avg" rows sit just above the vitamins. | A v5 polish list. It was never built (see below). |

Both reviewers preferred the "Light" look (gradients) to "Places" (generated rooms), so both versions were delivered.

## Every number on screen was real

A rule from the start: no invented numbers. Each one came from the app's pipeline on the development server, and the review checked that they add up across the film. The v4 day:

- **Breakfast, typed in detail:** 506 kcal, P 16, C 53, F 26 g (sourdough 70 g 174 kcal, avocado topping 86 g 151, fried egg 55 g 110, flat white 200 g 71). The careless version, "avo toast, egg, coffee": 337 kcal.
- **A granola bar,** label read by the app's OCR from a camera frame: 180 kcal, P 4, C 26, F 7 g, fibre 3 g, 40 g serving, high confidence.
- **Lunch:** 565 kcal, P 39, C 38, F 29 g.
- **A pizza** of 2,457 kcal (960 g, P 106, C 288, F 98 g), split by portions: 5 of 20 parts is 614 kcal, 9 is 1,106, 6 is 737, using the app's own split logic.
- **The day:** 506 + 180 + 565 + 614 = 1,865 of a 1,932 target.

## What the review found in the app

Checking the numbers this closely surfaced real product issues, which were reported to the owner rather than hidden in the edit:
- The label OCR dropped US calories: a "Calories 180" row has no unit, and the unit parser only accepted kcal, cal or kJ.
- Salt was not converted to sodium (sodium mg = salt g × 400).
- The same breakfast sentence returned 436 and 506 kcal on two runs. The film used 506.
- "kcal left" meant the daily budget on the ring and the share you keep on the share button, three seconds apart.
- The iPhone and web composers had different placeholder text.

## What the review missed

The advisors said ship. The owner did not. Their verdict on v4, the next morning:

> okay, I think the idea is there, its quite good. But the design and motion is not that peak tho. transition also a bit janky.

and the first specific point:

> the UI on mobile is broke. looks like you didnt use the actual build but render it again base on the code?

Neither reviewer had flagged that the UI was a re-implementation. Both checked the film against its own brief and against the numbers. Neither compared it with the real app, and neither compared its time budget with the references. The owner did both.

Lessons for the method:
- **An advisor review is a floor, not a verdict.** It catches legibility, consistency and arithmetic. It does not replace the person whose taste set the brief.
- **Give advisors the references, not only the brief.** A reviewer that has seen the reference films and the real product can catch "this is a rebuild" and "this camera moves too much".
- **The v5 polish list was dropped.** The owner's notes changed the approach (real recordings, less camera, more UI motion), so the rebuild was called v6. There is no delivered v5.

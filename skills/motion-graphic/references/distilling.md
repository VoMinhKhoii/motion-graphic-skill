# Distilling: technique cards, directions, rules

Research is not done until it is a collection the owner can browse and choose from. In the worked example the owner rejected a pile of per-account notes ("I just feel like you never watch those videos. Never distill any design direction.") and pointed to an earlier canvas where every technique was a card with a real frame. Build that.

## 1. Technique cards

One card per technique, merged across films. Fields:

| Field | Example (card H1 from the worked run) |
|---|---|
| Code | H1. The letter is the role (below), the number its order |
| Name | Frame 1 is typing |
| When to use | Naming the product with its own gesture |
| Measured recipe | One centred line, cap height 5–8% of the frame, types at 20–34 characters/s straight into its final layout (no reflow). Fresh letters land in an accent and settle to ink |
| For this product | The meal types itself on frame 1 at ~20 characters/s, food words landing tan, then settling to ink |
| Proof | A real frame from the first source film, with account, title and timestamp (private boards; see §4) |
| Also seen in | Other films and timestamps |

Roles, as letter codes:
- **H**: hooks (the first 3 s);
- **C**: composition (how a frame is built);
- **T**: type;
- **I**: imagery and grounds;
- **P**: product (how UI is shown);
- **X**: transitions;
- **R**: rhythm;
- **S**: sound;
- **E**: endings.

The worked run recorded 267 techniques from 8 study passes and merged them into 92 cards across five collections:
1. hooks and composition;
2. type and imagery;
3. product;
4. transitions and rhythm;
5. sound and endings.

Rules for cards:
- Every recipe is a measurement: a percentage of the frame, seconds, counts, hex colours sampled from pixels. "Large type" is not a recipe; "cap height 7.1% of frame height" is.
- Composition (C) cards, and any card whose recipe places things in the frame, cite the composition numbers from the corpus report for that role: content coverage, largest empty region, edge bleed, subject size, text cell. Write it in this form: "content 85–100% (demo median 92%), runs off 3 edges, UI type in the middle row", with your corpus's numbers. "Full-bleed" alone is not a recipe.
- Every card has a real frame. A card you cannot prove with a frame gets deleted.
- Write the "for this product" line. It forces you to imagine the technique in the owner's product before the owner has to.

## 2. Directions

A direction is a coherent grammar that several films share. Cluster the cards and films into directions: 2–4 for a Quick scope, 4–6 for Standard, 6–10 for Full (the worked example had 10). For each, write:
- **One-line definition**, for example "The sentence is the interface: the film is typed; one rebuilt component at a time steps out of it at hero scale; a dot carries every cut."
- **The rules:** 4–6 bullets with numbers (grounds, sizes, type speeds, cut rate, sound).
- **For this product:** one paragraph describing the film in this direction.
- **Why it fits / watch out:** be honest about the risk, for example "the most-used grammar in AI launches; without an owned motif it reads as a template".
- **Cards to build it from**, by code.
- **Films** in this direction, with view counts if you have them. Views are a weak signal but owners like them.

The ten directions found in the high-fidelity lab corpus are written up in `library/research/directions.md`, the 92 cards in `library/research/technique-cards.md`, and the boards with a real frame per card in `library/research/boards/refs.html`. They were:
- sentence as interface;
- poster-scale UI on paper;
- specimen assembly;
- macro material;
- device slab in a colour world;
- the dark instrument;
- a cast plays the product;
- a drawn idea hands over to the UI;
- light tells the time;
- living posters.

## 3. The overview page

Put a one-page overview in front:
- the corpus counts;
- the inclusion rule and the judgement calls;
- "N things nearly all of them do", each tied to card codes;
- the directions list.

The owner should be able to read it in two minutes and then dive into cards.

## 4. Where to show it

A visual board with the frames, never a markdown wall: local HTML files in `film/boards/`, or a private artifact or canvas if the session has one. The worked run used a multi-page design canvas: an overview, ten direction boards, five collection boards, a motion study (timelines, transitions, rules) and then the film concepts. Show frames at a size where the technique is visible, and zoom-check dense boards at 2× before sharing.

**Private review, not publication.** These boards hold third-party frames, so they are for the owner and the team only. Keep them local or in a private, unlisted artifact. If anything from the research is published publicly (a case study, a blog post, a public repo), replace the reference frames with links, timestamps and words, or with your own frames, unless the owner decides to publish credited stills as research commentary. The worked example's archive does that, by the owner's decision, and says so in its README.

## 5. From directions to concepts

Wire 3–5 concept films from the collection. Each concept is a complete film:
- the story in two sentences;
- what it proves;
- how it shows every platform (iOS and web, say);
- the motif it owns;
- what imagery it needs;
- the effort;
- every beat naming the cards it uses.

Show them side by side with a decision table. In the worked run the owner picked "K3 · One day": the colour of the light tells the time of day, and each meal of a day demos a feature. That one concept then carried all nine versions.

## Pitfalls seen

- **Lone objects on empty grounds.** Measured, about 8% of the lab corpus's frames (419 of 5,295 samples) do hold one object on an empty ground, but on purpose and at hero scale: one control alone on a brand colour, about half the frame wide, for a beat (card H3). What the owner rejected in the worked example was the other kind: small cards, numbers and devices parked in the middle of a cream void, frame after frame. Check your own corpus: the report's Composition section gives the coverage, subject-size and edge-bleed numbers, and `check_frames.py` flags lone small objects against them (`storyboard.md`). It does not yet catch small devices placed beside a headline (the headline and the devices read as one subject), so check those frames by eye: show about two-thirds of the phone, not half.
- **Copying one film.** The owner asked for no direct copy of a single film's signature shot (a horizon match-cut). Take the grammar, invent the motif.
- **Generic AI-film look.** Cream, one accent and a serif reads as one particular lab. Make the product's own type and colours carry the film.

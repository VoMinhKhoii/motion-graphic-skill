# Five film concepts

On 30 September, after the owner had seen the technique cards and the ten directions, they asked for "4-5 new directions" built from them, "base on the way you wire diff design + story telling, there should be some decision can make and the product should turns out smoothly."

Five concepts came back, each a complete 20 s film. Every beat named the cards it used and showed the reference frame it borrowed from. The shared constraints: every number on screen comes from a real run of the app's pipeline, no people, sound effects only, the brand's typeface and the app's own gradients.

## The five

| | K1 · One sentence | K2 · The ring | K3 · One day | K4 · The race | K5 · Guess the plate |
|---|---|---|---|---|---|
| **The story** | The meal types itself, Kallo reads it, the sentence breaks into its ingredients, one detail changes the number, and the camera pulls back to reveal it was the app all along, on iPhone and then on the web. | Food from every kitchen packs into the shape of Kallo's ring gauge, shot after shot, faster and faster. It stops dead on one meal, and that ring of food becomes the app's ring, filling with the real numbers. | One continuous shot across a day of eating. The light moves from dawn to night, each meal is typed as it happens, alternating iPhone and web, and the day's ring fills. | Two cards, one lunch. Left: a generic food database (search, pick "1 serving", adjust grams, repeat). Right: Kallo, one sentence. The right timer stops first, and its answer is closer to what was eaten. | A question the viewer answers before Kallo does. Two plates, the same words, one detail different. The slots stay empty; a beat of silence; then the real numbers land. Round two is left open for the replies. |
| **What it proves** | Typed meal, ingredients, the detail, real numbers | Real food becomes numbers; any kitchen | Logging all day; iPhone and the web as one diary | Speed, and the detail against "1 serving" | The detail changes the number |
| **iOS and web** | Yes: an outline morph | Yes: the ring on both | Yes: the core of the story | Yes, at the end | Yes, at the end |
| **Owned motif** | The shelf and the tan dot | Kallo's ring gauge made of food | Light across a day | The split race | Empty slots, then the reveal |
| **Generated images** | A few cut-outs | About 40 cut-outs | Optional skies | None | Plated photos |
| **Effort** | Medium | High | Medium, and needs new captures | Medium | Low |
| **Closest directions** (our reading) | D1, D5 | D3, D4 | D9, D5 | D7 (the race), C4 | D6 (the empty slots) |

The colour came from the app itself, not from the references:
- **Brand sweep:** apricot #FFD2B0 to lilac #DCC4FF, diagonal. It is the "+" button in the tab bar.
- **Start aurora** (onboarding): an apricot to lilac wash, an ember #E05A2B glow low-left and a violet #8A4FE0 glow high-right.
- **Step blobs** (onboarding): terracotta #E2966E, sage #8FAE74, violet #9E76C0, sky #92B6CF.
- **Macro colours** (the rings): protein #D46A86, carbs #E09C84, fat #E8C55C.

Taking the gradients from the app's own onboarding is what kept the film from reading as a copy of any one reference. The cream-and-one-accent look, for example, reads as Anthropic's.

## Who makes what

The concepts split the work by what each tool can do truthfully:
- **An image model** (Codex) makes everything that is a picture: food cut-outs, plated dishes, rooms, paper grounds. Every brief says no people, no hands, no text, and states the app's palette.
- **The UI** was planned to be rebuilt in code from the app's source, with real data. This was the first big mistake: the rebuilt screens looked broken next to the real app, and from v6 on every UI pixel is a recording of the real build. See [../03-iterations.md](../03-iterations.md).
- **Type and numbers** are set in the edit, and every number comes from a real pipeline run.
- **Transitions** are code, built from the cards.

## The pick, and why K3 won

The agent's recommendation was K1 for launch day (the product truth in 20 s), K2 as a teaser the day before, and K5 as a follow-up post. K3 was described as "the calmest, and needs fresh captures".

The owner chose K3:

> wwait, the K3 idea wwhere color indicating time of the day looks goood. lets have a story board for that. but I want all frame + the full story too. that way I can imagine wwhats happeing

Why it turned out to be the right call, seen from the end of the project:

- **It holds many features without a list.** The owner soon asked to show more than the core input: label and barcode scan, Circle (the social feed), relog, sharing a meal, micronutrients, and the web. In K1 these would be a feature list. In K3 each one is simply the next meal of the day: breakfast typed at 8:12, a label scanned at 10:30, lunch on the web at 12:40, Circle at 3:15, a relog at 4:30, a shared pizza at 7:05, nutrients at 10:40.
- **It says "every meal, all day" without a sentence.** The time of day is carried by the light, so the film never needs a caption to explain that this is daily use.
- **It is a world, not a void.** A sky or a room behind every beat answered the earlier rejection of lone objects on empty cream.
- **It survives a change of look.** The colour of light first lived in gradients ("Light"), then in six generated rooms ("Places"), which the owner preferred. Time was later also shown by a hand-drawn clock in the top-left corner. The concept did not depend on any one rendering of it.

The cost was the one the summary named: it needed new captures of the app at every time of day, and the light story can slow the pace. Both came true. The captures took most of the production time (see [../06-production-notes.md](../06-production-notes.md)), and pace was a recurring note in the reviews.

## Decisions left open on the board, and how they ended

| Decision | Options on the board | What happened |
|---|---|---|
| Format | 16:9 master for X plus a 4:5 cut for Threads, or one 1:1 | 4:5 and 16:9 from v4 on; a 9:16 cut for TikTok, Reels and Shorts was added after v9. |
| Sound | Licensed sound effects mixed to −14 LUFS, or a music bed under the effects | Effects first. A music bed was added in v7, rejected, and replaced by a track the owner picked. See [../05-sound.md](../05-sound.md). |
| Last line | "Log it the way you ate it." or "Say what you ate." | Neither. The end card became two plain lines, "Try it now" and the URL, after the owner pointed to xAI's "Available now" card. |
| Length | 20 s | 34.75 s at v4, 72 s at v7, 83.1 s final. The owner: "30s or even more is good if you make it super cleans, eye catching and visually appealing tho", and later "Don't worry about duration". |

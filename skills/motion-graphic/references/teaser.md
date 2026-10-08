# Teasers: how much to give away in 6–15 seconds

A teaser runs 1–3 days before launch. Its job is curiosity that converts on launch day. Research teasers separately from launch films; they follow different rules. Load this file at Step 1 when the owner picks a teaser, so research, concepts and the storyboard follow it from the start.

## Research

Scan the YouTube channels of companies known for teasers and filter for short clips with teaser words in the title:
```bash
"$SKILL/scripts/research/scan_channel.sh" <channel>     # for each channel
# filter titles: teaser|coming|soon|sneak|leak|preview|glimpse|countdown|"what's coming", duration ≤ 40 s
```
The worked run downloaded 25 teasers (Samsung, Google Pixel, Nothing, CMF, Framer, Figma, teenage engineering, Raycast, Notion, Apple) and broke ten down frame by frame. They are listed, with lengths, cuts and ladder rungs, in `$SKILL/library/teasers.csv`.

## Findings from that study

- The short, effective ones run 6–14 s; 38 s is a trailer, not a teaser.
- 8 of 10 are one continuous action with 0–1 cuts: a hand cuts, a cursor clicks, dots morph.
- The only line of text arrives 62–79% into the clip, 3–4 words.
- The name or logo comes last, often only in the final second.
- The most-viewed in the set (Notion Mail, 10 s) showed a 2.6 s glimpse of the real UI, then the name. The pitch lived in the post text, not the video.
- Pure mystery works only for brands people already follow.

## The reveal ladder

| Level | On screen | Example | Fits when |
|---|---|---|---|
| 1 Mystery | Abstract shapes, a number | Nothing "Updating…" | Followers are already waiting |
| 2 Metaphor | An everyday object stands in for the product | Samsung "What's coming?" (pizza, chocolate, dalgona cut into a phone shape) | The product's shape or idea is the news |
| 3 Partial | Tight crops of the real product | Nothing "Control freak", Framer × Work Louder | The product looks good up close |
| 4 Glimpse + name | One real action in the real UI, then the name | Notion Mail, Raycast, Pixel 10a | A new product from a small account |
| 5 Demo | Full walkthrough | Launch films | Launch day, not before |

A new SaaS from a small account sits at level 4, held to one action. The launch film does the full demo; don't spoil it.

## Structure that worked

The worked teaser, as the owner designed it:
1. Home.
2. Tap into the main screen.
3. Type one real input letter by letter.
4. Send.
5. The result lands.
6. Zoom out.
7. Save.
8. The day's gauge and numbers go up.
9. Fade to black on the wordmark and "Coming soon". No date.

That runs 10.6–12.4 s with the waits cut. Cut it in each audience's language with a meal or input native to that audience; the Vietnamese cut was typed through the Vietnamese keyboard in the Vietnamese app.

Sound: SFX-only reads raw and honest. Or use a trailer track whose drop lands on the key action and whose hit lands on the name (see `sound.md`).

## Options to show the owner

- **A · The leak:** the phone's own screen recording, as if posted too early; a hard cut on the result.
- **B · One sentence:** only the input on the brand ground, opening into the result.
- **C · The number:** type only; each input phrase gives way to its number.

Render every option's frames on the storyboard before asking. Owners often design their own flow from the options, as happened here.

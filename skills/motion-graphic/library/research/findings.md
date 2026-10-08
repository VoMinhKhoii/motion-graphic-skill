# Findings

What the reference films have in common, measured. Sources: the study passes over 85 motion-design films, the watched pass over 24 lab films (plus 8 Google films), and the measured pass over 123 films at 4 fps. Method in [corpus.md](../../examples/kallo-launch-film/01-research/corpus.md). Card codes (H1, X3, ...) point to [technique-cards.md](technique-cards.md).

## Eight things nearly all of them do

1. **Frames are full.** Hero scale means the subject fills the frame and runs off its edges. Empty space exists only around one line of type. No film parks a small object in the middle of an empty ground. Cards C1, I1, I2, P3.
2. **One thing at a time.** One line, one component, one state change per beat. Never a whole screen shown small. Cards H3, P3, C5.
3. **The product's own gesture is the grammar.** Typing, a caret, a toggle, a cursor, a chip: the film moves the way the product moves. Cards H1, P1, P2, T4.
4. **A motif carries every cut.** A dot, a hairline or a shared contour hands one shot to the next. Hard cuts are kept for chapters. Cards X1, X3, X11, C2.
5. **Move, then hold.** Fast ease-out moves of 0.3–0.6 s, then 2–4 s holds. Few cuts: 0–6 a minute in the product films. Cards R3, R2.
6. **Numbers resolve; they don't pop.** Count-ups, sweeps and blur-to-sharp. The number is the payoff, so it arrives as an event. Cards P8, P9, P10, T9.
7. **Silence is a tool.** Near-silence until the first result, a drop-out for the magic moment, silence for the name. Cards S1, S3, S5.
8. **The end is a dot becoming the mark.** Dot, mark, wordmark typed on, held 2.5–3 s in silence. The availability line sits just before it. Cards E1, E2.

## Where the seconds go

From the watched pass (24 lab films, second by second) and the measured pass (123 films at 4 fps).

| Measure | Value | Basis |
|---|---|---|
| Share of runtime that is the product on screen | **67%** | median, 24 lab films |
| Share that is standalone text | **11%** | median, 24 lab films |
| Share that is text laid over the demo | **0%** | median, 24 lab films |
| Share that is the logo | 7% | median, 24 lab films |
| A standalone text card | **2.6 s**, 6 words on 2 lines | median of 77 cards; half hold 2.0–3.4 s |
| Headline-size type | about 3 words, 2.1 s on screen | measured, 123 films |
| A demo beat (time before a cut, a camera move or the app's next state) | **2.9 s** | median |
| Logged transitions of every kind | 16.4 a minute | watched pass |

Demo share by account (median): Claude 71%, OpenAI 71%, Manus 65%, xAI 59%, Google 58%.

Cuts a minute, by account (measured pass, every hard change including flash cuts):

| Account | Cuts a minute |
|---|---|
| Claude | 16.5 |
| Manus | 13.6 |
| OpenAI | 5.7 |
| Google | 3.7 |
| xAI | 1.9 |

How the camera spends its time (measured, 85 lab films): still 54%, in-frame motion 23%, pan 6%, zoom in 4%, zoom out 4%.

The shape of a typical film: most of it is the product, cut into short beats. Text gets a few seconds in total. The logo gets the last two or three.

## How one shot becomes the next

298 transitions logged in the 24 lab films. A fifth are plain hard cuts. The rest are designed moves, most of them half a second or less. Morphs, type-ons and mask reveals take longest, at a median 0.7 s.

| Transition | Share of 298 | Count | Median length |
|---|---|---|---|
| Hard cut | 21% | 64 | instant |
| Camera move | 14% | 41 | 0.5 s |
| The app's own UI state change | 11% | 32 | 0.3 s |
| Push / slide | 11% | 32 | 0.4 s |
| Crossfade | 9% | 27 | 0.4 s |
| Scale-out | 9% | 26 | 0.4 s |
| Morph (shape A becomes B) | 8% | 23 | 0.7 s |
| Type-on / type-off | 6% | 19 | 0.7 s |
| Scale-into | 6% | 18 | 0.4 s |
| Match cut | 3% | 8 | 0.1 s |
| Mask reveal | 2% | 6 | 0.7 s |
| Wipe | 1% | 2 | 0.3 s |

### Twelve exemplar moves

Each was studied as 13 frames at 10 fps (1.2 s) around the logged moment. For each: the move, and what holds still while the rest changes. That second part turned out to matter most (rule 8 below).

1. **The bubble stays; the phone grows behind it.** Claude, *Dispatch*, 8.9 s, scale-out, 0.5 s. The prompt sits alone as a hero-size bubble. The thread's background and time stamp fade in behind it, then the camera pulls back (9.0–9.4 s) until it is an ordinary message in a whole phone. *Fixed:* the bubble. It only shrinks, staying near frame centre, while the screen and then the phone arrive around it.
2. **The headline becomes the screen's title.** Claude, *Dispatch*, 2.1 s, morph, 0.3 s. The phone screen fades and grows in around the claim (half-transparent at 2.1 s, solid by 2.2 s) and the pill badge above it drops out. The claim is now the app screen's own title. *Fixed:* the headline, pixel for pixel. Only the frame around it changes.
3. **The button squashes into the tab underline.** xAI, *Voice agents*, 7.4 s, morph, 0.5 s. The "Create Agent" pill fills orange, squashes into a thin bar and becomes the active-tab underline as five icons pop in above it. It is one link of a chain: pill, iris circle (6.0 s), underline, card edge (9.6 s). *Fixed:* the horizontal centre line. Pill, bar and underline all sit on it.
4. **The lone mic is the phone's mic.** Manus, *Telegram*, 21.7 s, scale-out, 0.4 s. A big mic button pulses alone on the background. In one beat the camera pulls back and it is the mic in the corner of a whole phone running the app. *Fixed:* nothing holds its place on screen. The eye follows the mic as it shrinks into the phone's lower corner. This is the one exemplar without a fixed element.
5. **One button lifted out of the phone.** Claude, *Artifacts*, 44.4 s, scale-out, 0.4 s. The Share button lifts off the phone and scales about 3x toward the centre while the phone and the room dim to black. Its press and state change then play at that size (Share, Copy link, Copied, to 46.5 s). *Fixed:* the button. Once the phone has gone it is the only thing on screen.
6. **The notification opens into the page.** Claude, *Artifacts*, 38.8 s, scale-into, 0.5 s. The tapped lock-screen notification expands into a terracotta card that fills the phone's screen, lightens to pink, then white, and the page fades in. The OS app-open zoom is used as the transition. *Fixed:* the phone and the blurred room behind it. Only the screen changes.
7. **The phone card widens into a desktop card.** Manus, *Manus Desktop*, 1.3 s, morph, 0.5 s. A phone-shaped card widens into a desktop-shaped one. The five stacked words fly into one line ("Mobile" becomes "Computer", "Now" is inserted) and the dock spreads from 4 to 7 icons. *Fixed:* the card's centre, its cloud wallpaper and the dock along its bottom edge.
8. **The coin docks into the toolbar.** Manus, *Browser*, 7.0 s, morph, 1.5 s. A browser window slides in from the right beneath the coin. The coin shrinks onto the toolbar's extension slot (7.4 s), its glow fades, and from then on it is the toolbar icon. *Fixed:* the coin. It drifts a little right and shrinks while the window arrives to meet it.
9. **Four app icons collapse to one.** Claude, *Microsoft 365*, 4.0 s, morph, 0.4 s. PowerPoint, Excel and Word fade out right to left while Outlook slides to the centre. The caption swaps, line by line, to the Outlook chapter's line. *Fixed:* the grey ground and the surviving icon, which carries the eye into the chapter.
10. **The lone icon match-cuts to its window.** Claude, *Microsoft 365*, 7.75 s, match cut. A hard cut from the centred Outlook icon to the Outlook window at the same centre on the same grey. A salmon glow then blooms around the window over about a second. *Fixed:* the centre point and the grey ground carry across the cut.
11. **The headline becomes a dot, the dot the next background.** OpenAI, *Law*, 7.3 s, scale-into, 0.3 s. The "Powered by" line has just shrunk into a dot (6.2 s). The dot flicks through colours, then grows, accelerating, into a circle that covers the frame and is the black ground of the next title. *Fixed:* the frame centre. Headline, dot and circle share one point.
12. **The title splits and the first card rises.** Google, *Android Drop*, 1.6 s, mask reveal, 0.2 s. "Android" exits up and "Drop" exits down with motion blur while the first UI card rises out of the gap between them. *Fixed:* the pastel gradient behind. The card is born where the words were.

## Nine rules

Written for a 30 s phone-app film cut at the fast end (like Claude and Manus, not like Google). Each rule rests on a number above. The final Kallo film ran 83.1 s, because the owner asked for more features and said length did not matter if it stayed clean, but the per-beat rules held at that length.

| # | Rule | In a 30 s film | Traced to |
|---|---|---|---|
| 1 | Two-thirds of it is the app. | About 20 of the 30 s show the product itself; roughly 3 s of text cards and 2 s of logo at the end. | Demo 67% of runtime, standalone text 11%, logo 7% (medians, 24 lab films). |
| 2 | One text card, maybe two. | A card carries about 6 words on 2 lines and holds 2.6 s. Anything set at headline size is about 3 words and stays about 2.1 s. | Text cards: median 2.6 s (half between 2.0 and 3.4 s). Headline-size type: 3 words, 2.1 s (measured, 123 films). |
| 3 | No captions over the demo. | While the app is on screen, its own words do the talking: the typed meal, the item names, the numbers. Claims go on their own card. | Text over the demo: a median 0% of runtime. |
| 4 | Something changes every three seconds. | 20 s of product at that pace is about 7 demo beats, each ended by a cut, a camera move or the app's next state. | A demo beat lasts a median 2.9 s. |
| 5 | Fast is about eight cuts. | Even the fastest accounts cut about once every 3.6–4.4 s, so a fast 30 s film has 7–8 cuts. The rest of the pace comes from designed moves inside the shots. | Cuts a minute: Claude 16.5, Manus 13.6 (measured). Logged transitions of every kind: 16.4 a minute. |
| 6 | Let the app animate itself. | Prefer the product's own state change and short pushes. Keep camera moves to half a second. Spend a morph only on one or two hero moments. | The app's own UI state change 11% at 0.3 s, push/slide 11% at 0.4 s, camera move 14% at 0.5 s, morph 8% at 0.7 s. |
| 7 | Hold the camera still about half the time. | The motion lives inside the frame: typing, items landing, a ring filling. Pans and zooms are brief accents. | Measured, 85 lab films: still 54%, in-frame motion 23%, pan 6%, zoom in 4%, zoom out 4%. |
| 8 | Keep one thing fixed through every designed transition. | The meal sentence, the total, a button or the frame centre stays put while the rest changes around it, so the eye never has to search. | Eleven of the twelve exemplars hold one element in place; 79% of transitions are something other than a hard cut. |
| 9 | Borrow Google's moves, not its pace. | Its title splits, blur pull-backs and hue-per-chapter carousels are worth taking. Its cutting rate is about a fifth of the fast end's. | Google 3.7 cuts a minute against Claude 16.5. |

## What these numbers changed in the Kallo film

- **Rules 2 and 3** ended the habit of captioning the demo. By v9 every claim sits alone on its own gradient card, 1–2 lines, and the demo carries no text.
- **Rules 6 and 7** put the owner's v4 complaint ("cursor tracking overused, morphing underused") into numbers: the camera should be still about half the time, and the motion should come from the app.
- **Rule 8** became the test for every morph after v6: the composer box, the result card and the gauge each hold their place while the frame changes around them.
- **Rule 4** set the pace of the edit. When a beat ran well past 3 s with nothing changing (the micronutrient wall, the relog demo), the owner flagged it as static.

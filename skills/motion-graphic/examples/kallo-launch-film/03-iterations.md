# Iterations: v1 to v9, the 9:16 cut and the teaser

A chronological log of every round between the brief (30 September 2026) and the final teaser (7 October 2026). For each round: what was shown, what the owner said (quoted as written, typos included, trimmed to the lines about the video), and what changed.

This is the most useful file in the example. The research and the concept took one day. The rest of the week was spent here, and most of what the skill now says comes from a note in this log.

Times are UTC. Version lengths are measured from the delivered files.

## Day 1 · 30 September: the brief and two rejected storyboards

### The brief

> Make me an arrow 15-25s launch video.
> Target platform: X, Threads.
> Preference: https://x.com/OpenAI , https://x.com/claudeai , https://x.com/SpaceXAI , https://x.com/ManusAI, you know my direction I want on clean and high fidelity on both typography and visual
> No preference on features, but I expect to see killers and mains features/difference + the fact that we have both IOS + web fully functional
> No voiceover, use high quality sound effects.
>
> Imagine this will be the launch video on X that receive complements from even senior motion designers and make the whole day's attention to our product launch.

### Round 0a · four storyboard directions, made without watching anything (07:54)

**Shown:** four directions on a storyboard canvas: phone mockups, UI screenshots and captions, each labelled "closest to @claudeai" or "closest to @OpenAI". None of the reference films had been opened.

**Owner (08:13):**
> Did you actually watch the video produced by the X threads I show you? None of these are those direction? You think big tech and frontier labs would launch stuff like this?

**Changed:** 125 films were downloaded and analysed by script (cut detection, contact sheets, motion curves, spectrograms). See [01-research/corpus.md](01-research/corpus.md). The first one opened, OpenAI's "Ultrafast", had no UI in it at all.

### Round 0b · storyboards after the machine pass (14:56–15:29)

**Shown:** new storyboards, informed by per-account notes written from the machine analysis.

**Owner:**
> Is it me or the storyboards looks too simple? And why is there still a lot of weird Lora Italic? Can you follow our design system?

> bruh you got like 120+ high fedelity videos, its so rich already to distill their design.

> Plus theres a direction that completely wrong product. we're not analyzing through images?

> those clay dish look bad. just not use it

> I'd rather use sth hyper realistic, even if its imagen from codex

> SUppose you are Anthropic design team and are releasing a dieting tool, would you use this video?

> yeah thats right. and the product needs to be global also. how many time I need to told you the product no longer for Vietnamese only?

**Changed:**
- The film follows the product's own design system: its typeface (Be Vietnam Pro), its colours, no decorative serif italics.
- A direction built on photo recognition was dropped. Kallo reads text, not images.
- No stylised 3D props. Imagery, when used, is photoreal.
- The meals become international everyday food. Vietnamese dishes appear only in the Vietnamese-language cut (this came back in the teaser).

### Round 0c · lone objects on voids (15:51–16:17)

**Shown:** concept frames with single food cut-outs in the middle of an empty cream frame.

**Owner:**
> https://x.com/claudeai/status/2102435511222890900
> What I mean is full screen images like this, not those individual sitting super deadass on a white background? Did you really watch all reference videos? which one of those do leave big voids with lone images like that?

> theres plenty similar to these also. dont copy directly. I just feel like you never watch those videos. Never distill any design direction. Can you reference my [TikTok treatment] artifact for tiktok and do the same thing? extract references from all the videos, split into diff design and directions

> pls just take thosse motion vids only

**Changed:** the research was redone as a distillation: films with people filtered out (85 of 125 kept), 267 techniques proven by a frame, merged into 92 measured technique cards and 10 directions. See [library/research/technique-cards.md](../../library/research/technique-cards.md) and [library/research/directions.md](../../library/research/directions.md). The first of the "eight things they all do" is the direct answer to this round: frames are full, and no film parks a small object on an empty ground.

### Round 0d · five film concepts (17:06–18:04)

**Owner (17:06):**
> Yeah so base on these, can you give me like 4-5 new directions? base on the way you wire diff design + story telling, there should be some decision can make and the product should turns out smoothly.

**Shown:** five 20 s concepts, K1 to K5. See [02-concepts/film-directions.md](02-concepts/film-directions.md).

**Owner:**
> wwait, the K3 idea wwhere color indicating time of the day looks goood. lets have a story board for that. but I want all frame + the full story too. that way I can imagine wwhats happeing

> wwould love if the meals you are demoing are in more details. thats the point where doing text

> hey u think u can geneerate a less detailed, careless version of those meals? to show the diff?

> remember other stuff/features we have to show to tho

> 30s or even more is good if you make it super cleans, eye catching and visually appealing tho

**Changed:** K3 "One day" was chosen. The demo meals became long, specific sentences, each with a careless twin, so the film can show that detail changes the number. The feature list grew: label and barcode scan, Circle, relog, sharing a meal, micronutrients, and the web. Length was released from 20 s.

## Night 1 · v1 to v4 with two advisors

The owner went to sleep with a goal: a complete film by morning, iterated with two report-only advisors. Three review rounds produced v1 (31 s), v3 (34 s) and v4 (34.75 s). The UI was rebuilt in code from the app's source, set in a gradient world ("Light") and, in a second version, in six generated rooms ("Places"). The advisors' last verdict was "Ship: yes." Details in [02-concepts/advisor-review.md](02-concepts/advisor-review.md).

## Day 2 · 1 October

### v4 · 34.75 s · the owner's verdict (03:22)

> okay, I think the idea is there, its quite good. But the design and motion is not that peak tho. transition also a bit janky. I think the version of not gradient background is better overall in terms of first look and the day in time is more intuitive.
> Something first: the UI on mobile is broke. looks like you didnt use the actual build but render it again base on the code?
> I think the transition, is somewhere between overused and underused. What I mean overused, is cursor tracking. It makes our eyes need to follow diff position and changes so drastically. What is underused, is kind of motion, right now. We got no creative morphing, scrolling, transitioning.
> Theres sometime too much text. I see it needs to always be, stricking and clearly visible text, 1-2 lines. everything we want them to watch needs to be the central of attention.
> Theres are some place in the video which are not realing intuitive. For ex, in circle, instead of showing things static (oh yes, the problem it we are showing things a lot in static, which requires stop and read to understand) , we can show posts appears incrementally,
> For the time, Im thinking instead of showing that dry time, we can have a hand drawn clock, running somewhere on top left

The same review asked for the references to be studied again, this time for how the films spend their time (demo against text, how often transitions happen, how much is morphing), not only for single frames. Google was added as a motion source, with a limit:

> Google is more on a slow side. I want fast. Just a reference for possible kinds of motion.

**Changed, in v6:**
- **The real build.** Every UI pixel became a recording of the real app: the development build running in the iOS simulator, driven by scripted taps, and the web app recorded in a headless browser. Nothing is rebuilt from source any more.
- **Places over Light.** The six generated rooms (dawn kitchen, morning desk, noon desk, afternoon pantry, evening table, night room) became the default world.
- **Less camera, more product motion.** The camera stays still while the app animates. New moves: the composer close-up pulls back after Send; the phone becomes the browser and back through a container transform; at the end the Home ring zooms in and becomes the end card.
- **Text: 1–2 lines, alone.** No paragraphs, no stacked labels.
- **Incremental reveals** instead of static screens.
- **A hand-drawn analog clock** in the top-left corner instead of a typed time.
- **The distribution study.** 24 lab films and 8 Google films were logged second by second and 123 films measured at 4 fps. It produced the time budgets and the nine rules in [library/research/findings.md](../../library/research/findings.md): demo 67% of the runtime, a text card 2.6 s, a demo beat 2.9 s, the camera still 54% of the time.

v4 was the version two advisors had approved. The owner's notes undid most of it in one message. There was no v5: the advisors' polish list for v5 was dropped and the rebuild was called v6.

### v6 · 33.4 s · real recordings in rooms (06:54)

**Owner:**
> Coooooollllll. Its now super good. Now add creative cursor tracking and movement to it. Focused to the main content, click acitivy, add cursor, more morphing. More text in between.
> At first, I want the "Introducing Kallo - The text-first nutrition tracker, built for precision."
> At Kallo, we believe every journey works out better when we all feel supportive, especially dieting
> And the circle, be creative here, wwym we show reload. Manipulate a bit. Show each post incrementially appears in. Add more Circle with names and person too.
> Its a high end visual motion demo video, we not showing this to an elderly to teach them to use the app.

This reads like a reversal of "cursor tracking is overused", and it is not. The v4 complaint was about a camera that jumped between distant positions so the eye had to chase. What the owner wanted now was screen-recording-style tracking: zoom on the main content, a visible pointer, visible clicks, and a camera that follows the pointer smoothly. Tracking itself was fine; drastic chasing was not.

**Changed, in v7:**
- A spring camera that follows a touch pointer, with a press and ripple on every tap.
- Component-level morphs, not only whole-device ones: the composer lifts out of the phone, the careless card becomes the detailed card and docks back into the phone; friends' faces become posts; nutrient tiles burst into a wall and fly home.
- The text lines the owner wrote, on screens lit with the onboarding's own gradients and moving blobs, a different layout each time.
- Circle posts drop in one at a time (composited from the real feed's pixels, no pull-to-refresh), with five friends and photos.
- The rooms regenerated to look lived-in.
- A 125 BPM electronic music bed and licensed effects on every event.
- Built long on purpose (72 s) so it could be trimmed.

## Day 3 · 2 October: the biggest note, a lost look, and the storyboard rule

### v7 · 72.25 s (03:31)

**Owner** (trimmed):
> First of all, what I must say is, super great progress!!!!!!
> * Overall, some place can be a bit faster, like text display,... try a lil faster pace overall. I like the sound effect, but not the music, can I have the music link to pick?
> * I'm thinking theres too much time for text, I mean not the amount, but per time it appears. Cause u know the background is just color make the text appearance a bit boring when appear independently. How do other often show text beside plain background? Is there some sort of images directions?
> * Make the cursor the finger pointer, sometime, you can zoom at the button we are clicking, and show the clicking.
> * Kallo workmark got clipped here.
> * The first four slides are all text, in which, how about this: First introducing, then we display the first careless meal, the "A nutrition tracker that pays attentions to details, then we show the new one, then show both side by side, then tell the difference?
> * Top right of the input box got a lil error, I know its from the app but can you help fix before putting on video? Also on that frame, I would love if you can take out the input box only, no outside padding, and put it at middle, when send, we can show loading at also at midddle, then morph to the result card (for the loading state, instead of high speed the actual loading state, just show about 2 words of the loading state)
> * Same order for barcode and label scan, from barcode scan, we should demo, then to label scan, then demo
> * For filler frame like that at 17s, would be better if we not crop the top (we let the top and bottom iphone touch the screen's edge a lot), meaning zoom more, position better so less white void at bottom. We just need to see from the top of iphone, to below the meal cards a bit.
> * The nutrition label reading is quite plain. better if we can show the camera, move camera to the label, then click take picture. go through the process
> * I dont know whats this web frame are. For the web, after we morph from mobile in, we should then focus on input, cursor tracking as we type, click send, the zoom out a lil, show analyzing. Manipulate the loading state here somehow to see that we not speed up the vid, but the analysis actually really fast.
> * In the Circle part, "At Kallo we belive" got wrong typography. Good effect, but it takes too much time here, a bit slower than expected.
> * Pls add my avatar to the circle demo. You got my avatar.
> * Pls also create more circle, so we got diff names, diff groups,...
> * For share meal demo, lets add more friends to it, so it looks more collaborative.
> * For the micronutrient, pls use the bedroom background from start. also, after showing all micronutrient, it stays dead for quite long before united in the phone.

And at 04:19:
> hey for the nutrition label + qr code, can you use actual product from internet instead of AI gen?

**Changed, in v8 (61.4 s):**
- A pointing-hand finger instead of a disc. The camera rides with it on long moves, punches in tight on the control before a click, then shows the press. The model was a Claude demo the owner linked, where the camera rides the cursor and lands tight on each control.
- Text lines hold about half as long, and their treatment varies from line to line: typed, inline UI chips, text above the live demo, text beside a floating component, giant type, text over the room photo.
- The opening restructured as the owner described: introduce, careless meal, the line about details, the detailed meal, both side by side, the difference.
- **The input box alone.** The composer is cut out of the recording with no padding, centred; on Send, a centred loading state of two status words morphs into the result card.
- **Real products.** The barcode and label scans use real product photos (from Open Food Facts, licensed CC BY-SA, credited on the end card), not generated packaging.
- The label scan plays as a camera: move to the label, tap the shutter, read.
- Circle: the owner's avatar, three groups, more friends.
- The music was removed; a shortlist of tracks was sent for the owner to pick.

### v8 · 61.4 s (05:11–05:33)

**Owner:**
> We have lost some of that elegant look from the last version. I want you to iterate from the frames story board again so I can verify before video comes out.

Then the owner wrote the new opening themselves:
> First, for the first part, on gradient background, lets Introducing Kallo at middle, then transit to "The text-first nutrition tracker, built for precision." Then show the first typed message, when click send, morph to Iphone view and analyzing state (with morning background behind.) then to gradient "Kallo pay attentions to details that matter." then back to the background with preivous iphone result, morph to previous input, morph to more detailed input. then to result card, move to right, surface old one on left, then just "+222 ..." at top

> In the circle phone demo, take like 2/3 of the phone, not just 1/2

> Same for the relog. Show "We make it..." on gradient alone, then demo. The demo should be, first full iphone view, then more focused a bit to the lower part. then start demo.

> The demo on share meal is too fast and moving around too much. For share meal, we no longer need to demo the analyze. so no need to zoom at first, zoom later when save and start clicking share meal. We also dont need avaatars in the gradient screen

**What went wrong in v8:** every note from v7 was applied, and the sum was busier than v7. The share demo had 14 camera moves in 9 seconds. The text treatments were varied for variety's sake. Floating avatars and components sat next to text lines. Each change was defensible alone; together they lost the calm that made v6 work.

**Changed, in the v9 storyboard:**
- **Storyboard before every render.** From here on, every version was first shown as a page of frames rendered from the actual edit, at the real timings, and the video was rendered only after the owner signed the frames off.
- **Zoom only on key clicks.** The camera holds still on the area being demoed and zooms only for the click the scene is about (Save, Share), never once per tap. Taps play at the recording's real speed, about 1 s per friend added.
- **2/3-phone framing.** Demos show about two-thirds of the phone (a scale of about 0.6–0.68 of the phone's height), "not just 1/2", and no deep punch-ins. The relog starts on the whole phone, eases to its lower two-thirds, then the demo starts.
- **Text alone on the gradient.** No avatars, no floating components next to a line.
- **Reveals breathe.** After a full reveal (the micronutrient wall), hold about 1 s before the next move.
- **Skip what has been shown.** The share starts from a result already read; the analysis is not demoed twice.

### v9 storyboard · passes 1 to 3 (06:39–08:02)

**Owner, pass 1:**
> from 16.3 to 18.1, can we still keep that background?
> * Overlap on barcode.
> * Barcode sheet being cut on top.
> * For the nutrition label reading here, the original UI make we can capture the background so we dont have that black void surrounding.
> * at 30.4s, I need it to be even more focused on the input.
> * Other words got dropped?
> * I like the confetti of the Share button when clicked, but dont like the frame where the button stands alone.
> * After choosing all people, zoom more the the battery before click split even and edit portion. You can do cursor tracking when edit portion then back the share button.
> * In not just calories and macros. no need highlight macros.
> * Make the try it now like this (I mean typography level). Remove we make logging a meal better.

The end-card reference was xAI's plain "Available now" card: two lines, one size, one weight, no tagline, no pill.

**Owner, pass 2:**
> can you show the ressults beffore the Kallo pays attentions...? I think thats more natural?

> this one kinda invincible with the background.
> Also can you use the new cocoa images inside Downloads? So you dont have to generate a background which looks fake tho

**Changed:**
- **Effects stay on the real UI.** The Share confetti stays in place on the real screen; the lifted, isolated button is gone.
- **Zoom on what the action is about:** the split bar before "Split evenly", then the camera rides the finger tight through the portion drag.
- **Typed input framed very close** (about 2.7x) with the camera tracking the caret.
- **Camera feeds fill the viewfinder.** The scanned photo is extended so there is no black void around it. The AI-generated table under the cocoa tin looked fake and was replaced by the owner's own photo of the tin on a desk.
- **Backgrounds stay** behind the side-by-side comparison; a soft light goes behind headline text where needed. The "+245 kcal" line, invisible against the room, got a veil.
- **Order: result, then line, then back.** The careless message's result lands in the phone first and holds a beat, then the line "Kallo pays attention to details that matter.", then back to that result before it lifts into the input.
- **Two status words at most**, in every analysis shown. The app cycles through several status words while it works ("Connecting…", "Crunching…", "Weighing…", "Plating…"). Each recording's status line was read by OCR and cut past the extras: the careless run keeps "Connecting…, Crunching…", the detailed run "Connecting…, Weighing…", the web "Analyzing…, Weighing…". The web run had shown five.
- **The cut-out edge.** The composer had been cut at the wrong corner radius (58 against the app's 65) with a second border drawn over the app's own, which doubled the edge. It is now cut just inside the app's border, with one border at the app's radius.
- **The end card**: "Try it now" and the URL, plain.

The careless meal was re-recorded for v9 on an empty morning: 259 kcal against the detailed 504 kcal, so the difference line changed from "+222" to "+245".

**Owner:** "pls proceed to the video". v9 was rendered: 80.1 s.

## 5–6 October: sharper capture, music, the last frame

There were no review rounds on 3–4 October.

### v9 · 80.1 s (5 October, 15:14–17:14)

**Owner:**
> I believe we can zoom more to the input here and center it vertically to the screen. same here we can zoom more in? so its more focused. after this, zoom in and out and time somehow after we click save, we are able to see the numbers in the Gauge goes up.
> The demo in the relog is a bit static and boring, can you just add a lil moving, transition?
> When choose person to share meal, can we pick people a lil faster?
> The micronutrients at the expanded view stay static for a bit too long. pls reduce that.

The same round asked for typing letter by letter instead of word by word, and pointed out that the web capture looked soft, about 480p next to the sharp phone footage. The owner also supplied the music they had picked (Pixabay, "Your Pulse"), see [05-sound.md](05-sound.md).

**Changed, in v9b (82.35 s):**
- **Letter-level typing.** Every typed meal was re-recorded one letter at a time. iOS sometimes flashes a selection or an autocorrect bubble mid-word; those frames were found and cut.
- **The 480p web blur.** The browser screencast (Chrome DevTools Protocol) caps frames at CSS pixels and ignores the device pixel ratio, so a 1440x900 window arrives as 1440x900 frames even on a retina setting. Once the camera zoomed into the input, that was about 480p on screen. The fix: a 2880x1800 viewport at device pixel ratio 1, with `html { zoom: 2 }` injected after load. The page lays out as 1440x900 but paints at twice the size. See [06-production-notes.md](06-production-notes.md).
- The web input framed tighter and centred; after Save the camera pulls out so the gauge numbers can be seen going up.
- The relog demo got movement; friend picks got faster; the micronutrient wall holds less.

**Owner (16:35):**
> Hey, is it because the the lighter version or I I will see in the web the more is still kind of buggy if you extract it like frame by frame and you may notice like component missing and stuff. Like like the error state was disappeared uh, the everything disappeared and it's just not smooth on the web demo. Everything else I would say perfect.

> never mind i have time. this is the launch video. i want the best quality

**Changed, in v9c (83.1 s, 6 October):** the 2x screencast in software rendering only delivered about 16–19 fps, so frames were missing and components seemed to blink. With GPU flags on the browser, the same capture runs at about 57 fps. The web typing was re-taken at 3x and the analysis at 2x, with no frame interpolation.

On the same night, macOS purged the temporary folder the whole project lived in. Sources, recordings and the sound library were rebuilt from Remotion's own bundle cache and the repo (see [06-production-notes.md](06-production-notes.md)).

### v9c to v9d · the source credit (6 October, 00:44)

**Owner:**
> oh can u remove that source reference at the last frame? not so necessary right the images are publicly available…?

**Changed, in v9d:** the line "Product photos: Open Food Facts contributors, CC BY-SA" was removed from the end card. Nothing else changed.

A note for anyone repeating this: "publicly available" is not the same as "free of conditions". CC BY-SA asks for attribution. If you remove the credit from the frame, put it in the post text or the video description, or use photos you own. For product shots, the cleanest option is to photograph the product yourself, which is what was done for the cocoa tin.

### The 9:16 cut (6 October, 04:29)

**Owner:**
> hey can you also make a verson with frames compatible to tiktok, youtube short and reels?

**Changed:** a 1080x1920 version of v9d. Reframing alone was not enough, because TikTok, Reels and Shorts cover the top and bottom of the frame with their own interface (the top bar; the caption, the buttons and the progress bar). Every scene is laid out inside a safe band, 140 px from the top and 300 px from the bottom (y 140 to 1620, so 1080x1480), while backgrounds and the phone bleed past it to the frame edges. The side-by-side comparison of the careless and detailed cards becomes a stack, careless above and detailed below.

## 6–7 October: the teaser

### The request (6 October, 16:52)

> Hey, uh, the team kind of demand a teaser video before this official product launch. So can you do some research? to see uh, direction from others who have done some short sort of leaks leaks on my pre-launch of the product to see how much we should do and put it in the uh, the short video maybe just like five to ten seconds or so but yeah you see how they can do it and also for this please include to the detail news on an English and one in Vietnamese

**Shown:** a teaser study of 25 real teasers, a five-level reveal ladder, and three directions (A the leak, B one sentence, C the number). See [04-teaser.md](04-teaser.md).

### The owner's flow (17:32)

> Okay, the mail looks good. I already made some uh, edits. In the canvas, video I think we can we can do it this way so first so show the home screen then click on to the uh, click on to the login page then start typing click send then after the new cards are out we zoom out click save then after the macros went up the total macro of the day went up in the guage uh, then we show the fade into the black screen with Kallo but don't show the the launch date please just say coming soon

("the mail" is the Notion Mail reference; "the login page" is the app's Log tab.)

**Changed:** none of the three directions was used as proposed. The owner kept the level-4 idea (one real action, then the name) and wrote their own sequence. It was recorded fresh in both languages, each with the app in that language.

The Vietnamese take needed a different keyboard. The recording tool cannot type Vietnamese diacritics directly, so the simulator was set to the Vietnamese Telex keyboard and the meal was sent as Telex keystrokes (for example `a` + `a` gives "â", `o` + `w` gives "ơ", and an `s` typed right after a vowel adds the acute tone, and `f` the grave, so "lườn" is typed `l u w o w f n`).

### Teaser v2 to v3 (7 October, 02:32–03:26)

**Owner:**
> changes: make the VN version this meal: phở lườn gà không da, ít bánh, nước trong. and the end screen is coming soon. right now lets say no music, just sound effects.

and then supplied a track:
> heres the audio

(Pixabay, "Trailer Suspense", #415585.)

**Changed:**
- The Vietnamese meal became "phở lườn gà không da, ít bánh, nước trong" (chicken breast pho, no skin, fewer noodles, clear broth): 393 kcal.
- Both cuts end on the wordmark and "Coming soon" ("Sắp ra mắt"). No date.
- Faster: English 12.4 s, Vietnamese 10.6 s.
- **The gauge jank.** On Save, the debug build stalled for about 0.7 s, then the card fold, the new numbers and the "Meal saved" toast all appeared in one frame. The stall was cut, and the jump was bridged by dissolving the last pre-save frame away over 0.3 s. The ring fill that follows is the app's real 60 fps animation.
- **Two status words at most**, the same rule as the film.
- **The music**, aligned so its drop lands on the Save tap and its hit on the wordmark. See [04-teaser.md](04-teaser.md) and [05-sound.md](05-sound.md).

## Lessons

Each lesson is tied to the round that taught it.

1. **Watch the references before drawing anything.** Round 0a. Labelling a direction "closest to @X" without having seen X's films produced a board the owner rejected in one line.
2. **Downloading is not studying.** Round 0b and 0c. Machine analysis and per-account notes did not change the design. Measured technique cards and directions, shown to the owner before any concept, did.
3. **Full frames, never lone objects on voids.** Round 0c. "Hero scale" means the subject fills the frame and runs off its edges.
4. **Ask who the audience is, and check every example against it.** Round 0b. "The product needs to be global" had been said before; the default meals should have been international from the start.
5. **Use the real build. Never re-implement the UI.** v4. A rebuild from source looks broken next to the real app, and the people who know the app see it at once.
6. **Advisors catch arithmetic, not taste.** v4. Two reviewers said ship; the owner rejected it. Give reviewers the references and the real product, and treat their pass as a floor.
7. **Measure distributions, not just moments.** v4. Cards say how one move is built; the time budget (demo 67%, a text card 2.6 s, a beat 2.9 s, the camera still about half the time) says how a film feels.
8. **The camera serves the pointer, it does not chase it.** v4 to v6. Screen-recording-style tracking is welcome; jumping between distant positions is not.
9. **Morph components, not only devices.** v6. The memorable moves were the composer lifting out, the card docking back, tiles bursting and flying home.
10. **1–2 striking lines, alone, each with one job.** v4, v7, v8. No paragraphs, no captions over the demo, no props next to the line.
11. **Nothing static that needs reading.** v4, v9b. Reveal incrementally, and hold a full reveal about 1 s, not longer.
12. **Applying every note can still make it worse.** v8. Review the sum, not the list. Storyboard before every render, at the real timings, and get sign-off before spending render time.
13. **Zoom only on the key click.** v8. One zoom per scene, on the action the scene is about. Play taps at real speed.
14. **Frame the phone at about two-thirds.** v8. Half a phone is too tight to read the context; the whole phone is too small to read the text.
15. **Edit the app's quirks out, not its truth.** v7 to v9. Cut status words down to two, fix a cut-out edge, patch a clock. Never change a number.
16. **Show the result before the line that comments on it.** v9 pass 2. The line lands harder when the viewer has just seen what it refers to.
17. **Type letter by letter, and cut the keyboard's flashes.** v9. Word-by-word typing reads as fake.
18. **Capture the web at twice the size, with a GPU.** v9b, v9c. A soft or stuttering web beat is the first thing a viewer notices next to sharp phone footage.
19. **Mind licences when removing credits.** v9d. Public images can carry attribution terms; own the photo or keep the credit somewhere.
20. **Lay out tall cuts inside the platforms' safe band.** 9:16. Let the backgrounds bleed; keep text and the action inside y 140–1620.
21. **Research the teaser genre separately.** Teaser. A teaser is not a short launch film: it shows less, names the product last, and depends on how well known the brand already is.
22. **Let the owner write the flow when they can see it.** Teaser. The owner's own sequence beat all three proposed directions; the job became executing it precisely.

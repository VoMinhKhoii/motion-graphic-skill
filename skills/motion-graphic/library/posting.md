# Posting the film: what we measured

Generalisable findings from the social-launch research done for the worked example on 5–6 October 2026. The product's audience was Vietnamese and English-speaking, so the clocks below are Vietnam time (UTC+7) with US Eastern alongside. Re-run the measurement for your own audience; the method transfers, the hours may not.

Private material from that research (the founder's own accounts, group members, drafts) is left out.

## Method

- **Score each post against its own account.** Engagement = likes + replies or comments + reposts or shares, plus one. Divide by the median of that account's other posts. 1.2x means 20% above that account's usual. This controls for account size.
- **Drop young posts.** Posts younger than 48 hours (7 days on TikTok) are still growing and drag a band down.
- **Use 3-hour bands** and 95% confidence intervals from 600 bootstrap resamples. Call a gap real only when the best band's interval sits entirely above the worst band's.
- **Read public data only**, as text from the page. Do not use an account's tokens or cookies to call private APIs.

## What was measured

| Platform | Sample | Quality |
|---|---|---|
| TikTok | 4,037 videos from 132 Vietnamese creators (diet, gym, calorie, student-IT, developer and AI-tool topics), the latest 60 per creator, posted 7–92 days earlier | strongest |
| X | full 90-day timelines of 6 English AI and dev-tool builder accounts, 386 posts, replies left out | moderate |
| Threads | search samples: 290 Vietnamese and 234 English posts, scored against the sample median (account size not controlled) | directional only |
| LinkedIn, Facebook groups | not measured; automated reading was blocked or failed | none |

## Best times

| Platform | Finding |
|---|---|
| TikTok | Only one band beats the noise: 06:00–09:00 local, 1.21x engagement (95% CI 1.03–1.58, 220 videos) and 1.09x views. Every other band sits within about 10% of usual. The evening band (18:00–21:00, 1,364 videos) is exactly 1.00x, so posting a big video in the evening carries no penalty. |
| X | No band is reliably better: every interval includes 1.0. Views ran 1.17x in the 21:00–24:00 Vietnam band, which is 10:00–13:00 US Eastern. Post when US readers are awake and you can stay up to reply. |
| Threads (Vietnamese) | Marketing blogs say 11:00–14:00 and 18:00–20:00. A 370-post check by Vietnam time gave median likes / replies: 21–24h 104 / 20, 18–21h 89 / 11, 06–11h 73 / 20, 11–14h 28 / 8, 14–18h 18 / 6, after midnight 67. The evening claim held; lunchtime did not. Window used: 19:30–22:30. |

**Weekday.** No platform showed a weekday effect that cleared the noise. TikTok was flat: every weekday 0.97–1.03x over 3,963 videos. On X, two samples disagreed on the best day and their intervals overlapped. Pick the day you can stay online for the first hour after each post.

## How fast posts grow

A snapshot across posts of different ages, as a share of the account's usual engagement. It shows why young posts are dropped before scoring.

| Age of post | X | TikTok |
|---|---|---|
| 0–24 h | 0.23–0.72x (rising through the day) | 0.35x |
| 24–48 h | 1.18x | 0.93x |
| 48–96 h | | 0.68x |
| 96–168 h | | 0.73x |

Do not judge a post before 48 hours.

## Warm-up before launch

For a quiet account that needs to restart before launch day (L0). Mechanics marked "claimed" come from creator advice and platform statements, not from our data.

| Mechanic | Status | What to do |
|---|---|---|
| Replies drive reach | observed, and stated by Meta | Every top post in the Threads sample had a high reply count. Spend 15–20 minutes a day on real replies in your topic's threads. |
| End on a question people want to answer | observed | Reply-heavy posts close on a genuine question or a request for a verdict. "I'm a [role], [ask for one word]" had the highest reply-to-like ratio in the sample. |
| Video or images beat plain text | observed | Every app post with reach had a short screen video or images. |
| Reply within the first hour | claimed | Post only when you can stay online 30–60 minutes. |
| 3–5 posts a week | claimed | The plan used 6 posts over 14 days, 2 days apart, plus daily replies. |
| A long gap means a cold start | claimed | Start two weeks out; do not post in bursts. |
| Engagement bait ("let's connect") | avoid | It gets replies from people outside your audience, and platforms say they down-rank it. |

A two-week shape that follows from this:
- **L−14:** tidy the profile; start daily replies.
- **L−13:** a comeback post that brings something concrete.
- **L−10:** "what I built" with 3–4 screenshots; pin it.
- **L−8:** a one-word question about the problem your product solves.
- **L−6:** a lesson from building it.
- **L−4:** a 10–15 s feature clip.
- **L−2:** a 5–6 s teaser cut from the launch film. No date.
- **L−1:** the teaser on the short-video platform, in its best band.
- **L0:** the launch post with the film; reply to everyone for an hour.
- **L+1 onward:** the second language, then one community post every 2–3 days.

## What spreads at launch

Observed in the samples (X For You and search, Threads search, TikTok):
- **Humble beats polished.** The biggest indie-app launch in the Vietnamese Threads sample (52.5K likes, 9.1K shares) was one self-deprecating line, "free", and a short screen video. No feature list. Polished ads got little.
- **The X launch template:** "I made X", one sentence on the concept, the constraint that makes it different, "launching today", then a video. Builder posts that reached For You were small things shipped with a short video and one concrete, measurable claim.
- **A crowded category needs a sharp first line.** A generic calorie-tracker launch from an account with an audience got 31 likes. Say what is different in the first line.
- **Arguments are reach.** When a category is argued in public (here, whether AI can estimate calories from a photo), a reply with real proof in a big thread is seen by more people than a post from a small account.
- **TikTok brand formats.** One calorie-app brand account ([@calai.app](https://www.tiktok.com/@calai.app)) had a median of 13.1K views over its last 30 videos; its hits (230K–440K) were a green-screen rebuttal of doubters, a how-to tip and a reply to a comment. Its founder's personal skits were single takes with no cuts. The brand also ran a large paid creator programme, so copy the formats, not the reach.
- **Shares count on Vietnamese TikTok.** On Vietnamese posts in a For You sample, shares often matched or beat likes.

## Community groups

- Read each group's rules first. Several large groups ban links or promotion outright; one diet group was run by a competing app.
- Ask an admin before posting a launch. Give value first (a breakdown, a menu, a lesson) and put the link in a comment only where allowed.
- Builder groups often require a tag and remove pure launch posts. Post the build story instead.
- Reading Facebook groups from a signed-in browser was blocked by the agent's safety classifier as personal-data handling, even when scoped narrowly. Do this research by hand.

## Accounts studied

Only brand accounts are named here. The X and TikTok samples also covered individual creators and builders; they are counted above but not listed.

| Account | Platform | Why |
|---|---|---|
| [@calai.app](https://www.tiktok.com/@calai.app) | TikTok | Category leader's organic formats |
| [@NotionHQ](https://x.com/NotionHQ) | X | Most-viewed teaser in the teaser study |

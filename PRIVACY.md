# Privacy

The motion-graphic skill is a set of instructions, local scripts and a project template. It has no server, no account, no analytics and no telemetry. Its authors receive nothing from you.

## What stays on your machine

When you use the skill, your agent works in your project, on your machine:
- It reads your codebase and runs your app to learn its design system and flows.
- It records your own app (simulator, emulator or browser) with a dev account and data you choose. Recordings can show names, avatars or other data from that account. Use demo data.
- It saves reference films you approve, their measurements, storyboards, renders and sound in your project's `film/` folder. The skill tells the agent to keep downloaded films private and out of git.

Nothing in this list is sent to the skill's authors or to any service of theirs. You can delete the `film/` folder at any time.

## What goes to other services

Some steps contact third-party services on your behalf, with your agent's usual approval:
- **Reference research:** search queries and video URLs go to YouTube, X, TikTok and Threads (through `yt-dlp` or a browser session you are logged in to). Their own privacy policies apply. The skill never reads or exports your cookies or tokens and never posts.
- **Packages:** `npm` and Playwright download packages from their registries.
- **Sound:** you fetch music and sound effects yourself from their sites.

Your agent itself (for example Claude) processes what it reads under its own terms.

## Contact

Questions or problems: open an issue at https://github.com/VoMinhKhoii/motion-graphic-skill/issues

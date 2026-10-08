# Delivery: aspect ratios, safe zones, masters, sharing

## Aspect ratios from one edit

Deliver the formats the brief and the branch need. For social, build one film component that reads the frame size and lays out for portrait or landscape, and render:

| Ratio | Size | Where |
|---|---|---|
| 16:9 | 1920×1080 | YouTube, website, X |
| 4:5 | 1080×1350 | X and Threads feeds, Instagram feed |
| 9:16 | 1080×1920 | TikTok, Instagram Reels, YouTube Shorts, Stories |

60 fps for UI films: scrolling and typing look smoother. Live-action presenter films deliver at the frame rate they were shot at.

**Store previews are a separate deliverable,** not a social cut resized. Apple takes 15–30 s at most 30 fps, at fixed sizes per device class; Google Play takes a YouTube link and autoplays only the first 30 s, muted. The specs, content rules and the validation checklist are in `branches.md`.

## 9:16 safe zones

TikTok, Reels and Shorts cover the top with tabs and the bottom with the caption and username, and run a column of buttons down the right edge. The worked example's baseline: lay every scene out in a safe band of about 1080×1480, 140 px from the top and 300 px from the bottom. Let backgrounds and the device bleed to the frame edges. The engine's `SafeBand` does this with a React context:
- scenes see a virtual height of 1480;
- background layers extend by the bleed.

**The right-hand column is a horizontal exclusion too.** The like, comment and share buttons sit over the right edge of the lower half. As a starting assumption, keep key content out of the right 15% of the width below the middle, then check it: put a screenshot of a posted video from each target app over your frames at the same scale and look. Platforms move these controls, so re-check per project.

If the proof moment (the hero click, the number, the result) falls under that column, fix the frame, in this order:
1. move the camera so the subject sits left of centre for that beat;
2. move or re-time the subject (a different take, a different scroll position);
3. lay that beat out differently in 9:16 (stack instead of side by side).
Shrinking the whole UI until nothing overlaps makes it unreadable; do not do that either. Accept an obscured frame only for incidental UI, never for the proof moment, and tell the owner which frames you accepted.

Use the taller frame where it helps. A side-by-side comparison of two cards became a vertical stack about 50% larger in 9:16.

## Masters and copies

`film/engine/render/master.sh <CompositionId> <name> [mix.wav]` (`engine.md`):
1. Remotion renders PNG frames into a ProRes 4444 master, muted.
2. x264 at crf 14, `-preset slow -tune grain`, plus the AAC mix, for posting. Grain tuning stops gradients banding.
3. A crf 22 light copy for sending around (about 40% of the size).

Check every deliverable before calling it done:
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration -of csv=p=0 film.mp4
ffmpeg -hide_banner -i film.mp4 -vn -af ebur128=peak=true -f null - 2>&1 | tail -12
```
- The video stream's duration equals the approved timeline (the composition's length), and the audio is not shorter: a mix shorter than the picture must never cut the film's last seconds.
- Integrated loudness and true peak meet the target in `sound.md`.
- Sample 4–6 frames from the final file (not the stills) and look at them.

Partial re-renders save hours: render only the changed frame range (`--frames=a-b`), then stream-copy the untouched head and concatenate.

## Sharing with a team

- **A streaming page:** an fMP4 HLS stream (`init.mp4`, numbered `.mp4` segments, the playlist) played with hls.js. It loads instantly and scrubs well. Add a chapter list that seeks the video, and the caption credits with a copy button.
- **Drive or a shared folder:** most connectors can't upload large binaries inline. Gather the files in one local folder with clear names, make the destination folders, and drag them in, or use an authorised sync tool (rclone) when the owner has approved it.
- Name files `<product>_<cut>_<ratio>[_light].mp4`, for example `kallo_teaser_vi_9x16_light.mp4`.

## Posting checklist

- Caption credits for any openly licensed photos (CC BY-SA requires them). Or replace those photos with your own to drop the credit.
- Music licence: keep the licence page and track id with the project. Social platforms' music detection can flag royalty-free tracks; keep an SFX-only version ready.
- Check post copy against the owner's messaging rules: no unannounced pricing, dates or plans.

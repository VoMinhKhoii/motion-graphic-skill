#!/usr/bin/env bash
# vfr_to_cfr.sh: convert a screen recording to constant 60 fps before it goes anywhere near Remotion.
#
# Usage:
#   vfr_to_cfr.sh <in.mp4> <out.mp4> [fps]
#   vfr_to_cfr.sh clips/take3.mp4 ../templates/remotion-starter/public/rec/take3.mp4
#
# Why: `xcrun simctl io recordVideo` (and most screen recorders) write variable frame rate. They emit a frame
# only when the screen changes, so a still screen can leave gaps of seconds between frames, and video time is not
# wall time. Remotion's OffthreadVideo seeks by timestamp and mis-seeks on these sparse files (wrong or stale
# frames, holds landing on the wrong state). `fps=60` duplicates the last frame through each gap, `-fps_mode cfr`
# writes one frame every 1/60 s, so source second N is frame N*60 exactly. The timeline is unchanged: a gap
# stays the same length, it just holds a picture. crf 14 keeps UI text sharp; -g 30 keeps seeks fast.
#
# A screen that never changes during the take (a static Home) never reaches the file at all; take a screenshot
# for that state instead (xcrun simctl io <udid> screenshot still.png).
set -euo pipefail
in="${1:?usage: vfr_to_cfr.sh <in> <out> [fps]}"; out="${2:?usage: vfr_to_cfr.sh <in> <out> [fps]}"; fps="${3:-60}"
mkdir -p "$(dirname "$out")"
ffmpeg -hide_banner -loglevel error -y -i "$in" -vf "fps=$fps" -fps_mode cfr -an \
  -c:v libx264 -preset medium -crf 14 -g 30 -pix_fmt yuv420p -movflags +faststart "$out"
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,avg_frame_rate,nb_frames,duration -of csv=p=0 "$out"

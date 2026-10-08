#!/usr/bin/env bash
# master.sh: render a composition to a ProRes master, then the delivery files.
#
# Usage (from the template root):
#   bash render/master.sh <CompositionId> <outname> [mix.wav]
#   bash render/master.sh Film-45 acme_4x5 public/audio/mix.wav
#
# Writes:
#   out/master/<outname>.mov        ProRes 4444 from PNG frames, no audio (the archival master)
#   out/film/<outname>.mp4          H.264 crf 14, -tune grain, yuv420p, AAC 256k: the upload file
#   out/film/<outname>_light.mp4    H.264 crf 22, -tune grain: a light copy for chat apps and review links
# With no mix.wav the MP4s are silent. FRAMES=0-239 renders only that frame range, a quick picture check (the mix is not offset to match).
#
# The picture sets the length, never the audio. A mix shorter than the picture is padded with silence; a mix
# longer than the picture is cut at the last frame, with a warning (the cue sheet is out of date: re-run
# sfx_mix.py with the film's current length). After encoding, both MP4s are checked against the master: if
# either differs by more than one frame, the script exits non-zero.
#
# Why this chain: soft gradients (the GradientWorld, blurred photos, shadows) band into visible steps when frames
# go through JPEG and then a default x264 encode. PNG frames into ProRes 4444 keep the master clean. x264's
# default tuning smooths the faint noise that dithers a gradient, and the steps come back; `-tune grain` keeps
# that noise, so the gradient stays smooth at the same crf. crf 14 is near-transparent for social uploads, which
# re-encode anyway; crf 22 came out at 40% of the size in testing and is fine for review.
set -euo pipefail
cd "$(dirname "$0")/.."
COMP="${1:?composition id}"; NAME="${2:?output name}"; MIX="${3:-}"
mkdir -p out/master out/film
# NODE_OPTIONS preloads injected by some shells break the Remotion CLI; drop them for this call.
env -u NODE_OPTIONS npx remotion render src/index.ts "$COMP" "out/master/$NAME.mov" \
  --codec prores --prores-profile 4444 --image-format png --muted ${FRAMES:+--frames=$FRAMES} > "out/master/$NAME.log" 2>&1 \
  || { tail -20 "out/master/$NAME.log"; exit 1; }

# The rendered picture's length: frame count over frame rate, read from the master itself.
probe() { ffprobe -v error -select_streams "$2" -show_entries "$3" -of default=nw=1:nk=1 "$1" | head -1; }
FPS_R=$(probe "out/master/$NAME.mov" v:0 stream=r_frame_rate)
NFR=$(ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of default=nw=1:nk=1 "out/master/$NAME.mov")
VDUR=$(python3 -c "n,d='$FPS_R'.split('/'); print(f'{$NFR*int(d)/int(n):.6f}')")
FRAME=$(python3 -c "n,d='$FPS_R'.split('/'); print(f'{int(d)/int(n):.6f}')")
echo "master: $NFR frames at $FPS_R = ${VDUR}s"

X264=(-c:v libx264 -preset slow -tune grain -pix_fmt yuv420p -movflags +faststart)
if [ -n "$MIX" ]; then
  ADUR=$(probe "$MIX" a:0 stream=duration)
  if python3 -c "import sys; sys.exit(0 if $ADUR > $VDUR + $FRAME else 1)"; then
    echo "WARNING: the mix ($ADUR s) is longer than the picture ($VDUR s); cutting it at the last frame. Is the cue sheet out of date?" >&2
  elif python3 -c "import sys; sys.exit(0 if $ADUR < $VDUR - $FRAME else 1)"; then
    echo "note: the mix ($ADUR s) is shorter than the picture ($VDUR s); padding it with silence."
  fi
  # apad makes the audio endless; -t stops both streams at the picture's length.
  ffmpeg -loglevel error -y -i "out/master/$NAME.mov" -i "$MIX" -map 0:v -map 1:a "${X264[@]}" -crf 14 \
    -af apad -c:a aac -b:a 256k -t "$VDUR" "out/film/$NAME.mp4"
  ffmpeg -loglevel error -y -i "out/film/$NAME.mp4" "${X264[@]}" -crf 22 -c:a copy "out/film/${NAME}_light.mp4"
else
  ffmpeg -loglevel error -y -i "out/master/$NAME.mov" "${X264[@]}" -crf 14 -an "out/film/$NAME.mp4"
  ffmpeg -loglevel error -y -i "out/film/$NAME.mp4" "${X264[@]}" -crf 22 -an "out/film/${NAME}_light.mp4"
fi

# Every delivered file must be as long as the picture, to within one frame: video stream, audio stream, container.
fail=0
for f in "out/film/$NAME.mp4" "out/film/${NAME}_light.mp4"; do
  for what in "v:0 stream=duration" "a:0 stream=duration" "v:0 format=duration"; do
    set -- $what
    d=$(probe "$f" "$1" "$2")
    [ -z "$d" ] && continue # a silent file has no audio stream
    if ! python3 -c "import sys; sys.exit(0 if abs($d - $VDUR) <= $FRAME + 1e-6 else 1)"; then
      echo "ERROR: $f $1 $2 is ${d}s, the picture is ${VDUR}s (more than one frame apart)" >&2; fail=1
    fi
  done
done
ls -la "out/master/$NAME.mov" "out/film/$NAME.mp4" "out/film/${NAME}_light.mp4"
[ "$fail" = 0 ] && echo "durations OK: every file is ${VDUR}s within one frame" || exit 1

#!/usr/bin/env bash
# make_sample_clip.sh: build a placeholder "app" screen recording so the example film renders with no real capture.
#
# Usage: bash scripts/make_sample_clip.sh            (run from the template root)
#        SCALE=0.5 bash scripts/make_sample_clip.sh  (a 660x1434 file; the film still lays it out at 1320x2868)
#
# Use SCALE=0.5 when stills fail with "Failed to fetch ... disk space is low": Chrome refuses large video
# frames when the disk is nearly full (seen at 3.5 GB free on a 460 GB disk), and a smaller file gets through.
#
# Writes:
#   public/rec/sample.mp4        1320x2868, 60 fps constant frame rate, 12 s, H.264 (a phone app)
#   public/rec/sample_web.mp4    1600x1000, the same app as a web page on the same timeline (device preset 'browser')
#   public/img/sample_room.jpg   1920x1920 soft colour field, a stand-in photo for PhotoWorld
#
# The "app" is drawn with ffmpeg drawbox only, so it works on ffmpeg builds without drawtext/freetype.
# Text is shown as letter blocks. The source timeline (seconds) that src/film/scenes/Demo.tsx cuts from:
#   0.0  Home: title, three feed cards, an empty input box, a red DEBUG badge top right (leaked UI to patch)
#   2.0  the input is tapped: its border turns accent
#   2.5  typing starts, one letter block every 0.12 s (letter-level, like a real take)
#   5.4  typing ends; the Send button turns dark
#   6.0  Send is tapped: the button flashes accent
#   6.15 "thinking" dots blink: an app stall, 1.45 s of nothing new
#   7.6  the result card pops in, in one frame (the cut-and-bridge case)
#   7.9  8.4  8.9   its three rows land
#   9.4  the total bar lands
#  10.5  a "saved" toast slides up
#   A thin grey bar along the bottom edge grows with source time, so a still shows which source second it is.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p public/rec public/img

W=1320; H=2868; DUR=12; FPS=60; SCALE="${SCALE:-1}"
BG=0xF3F1EC; CARD=0xFFFFFF; INK=0x1C1B19; GREY=0xD9D5CC; SOFT=0xEAE6DE; ACC=0x5B5BD6; EDGE=0xE3DFD6

f=""
add() { f="${f:+$f,}$1"; }
box() { add "drawbox=x=$1:y=$2:w=$3:h=$4:color=$5:t=fill${6:+:enable='$6'}"; }
frame() { add "drawbox=x=$1:y=$2:w=$3:h=$4:color=$5:t=$6${7:+:enable='$7'}"; }

# leaked debug badge (the Patch example covers it)
box 1090 58 170 54 0xE5484D
# home indicator
box 520 2800 280 14 $INK
# header: title and sub-line
box 80 210 520 92 $INK
box 80 330 380 40 $GREY
# three feed cards with a thumbnail and two lines each
for i in 0 1 2; do
  y=$((440 + i * 290))
  box 60 $y 1200 250 $CARD
  box 100 $((y + 45)) 160 160 "$([ $i = 0 ] && echo 0xF2B8A0 || ([ $i = 1 ] && echo 0xA8C9A0 || echo 0xB8B4E8))"
  box 300 $((y + 60)) 560 46 $INK
  box 300 $((y + 130)) 760 34 $GREY
done
# input box: border grey, accent once focused at 2.0
box 60 2560 1200 170 $CARD
frame 60 2560 1200 170 $GREY 4 'lt(t,2.0)'
frame 60 2560 1200 170 $ACC 6 'gte(t,2.0)'
# typed letters: "plan a weekend in lisbon", one block per letter from 2.5 s
TEXT="plan a weekend in lisbon"
x=110; tc=2.5
for ((i = 0; i < ${#TEXT}; i++)); do
  ch="${TEXT:i:1}"
  if [ "$ch" = " " ]; then x=$((x + 22)); else
    box $x 2616 30 58 $INK "gte(t,$tc)"; x=$((x + 36))
  fi
  tc=$(python3 -c "print(round($tc + 0.12, 2))")
done
# Send button: grey, dark when there is text, an accent flash on the tap
box 1110 2585 120 120 $SOFT 'lt(t,5.4)'
box 1110 2585 120 120 $INK 'gte(t,5.4)'
box 1110 2585 120 120 $ACC 'between(t,6.0,6.18)'
# the stall: three dots blinking in turn
for k in 0 1 2; do
  box $((110 + k * 60)) 1400 36 36 $GREY "between(t,6.15,7.6)*lt(mod(t*3-$k*0.33,1),0.5)"
done
# the result card pops in at 7.6 (one frame), rows land, then the total
box 60 1340 1200 720 $EDGE 'gte(t,7.6)'
box 63 1343 1194 714 $CARD 'gte(t,7.6)'
box 110 1390 420 64 $INK 'gte(t,7.6)'
for r in 0 1 2; do
  y=$((1500 + r * 130)); tr=$(python3 -c "print(round(7.9 + $r * 0.5, 2))")
  c="$([ $r = 0 ] && echo 0xF2B8A0 || ([ $r = 1 ] && echo 0xA8C9A0 || echo 0xB8B4E8))"
  box 110 $((y + 18)) 44 44 "$c" "gte(t,$tr)"
  box 180 $((y + 20)) $((520 - r * 90)) 40 $INK "gte(t,$tr)"
  box 1010 $((y + 20)) 200 40 $GREY "gte(t,$tr)"
done
box 110 1930 1100 4 $SOFT 'gte(t,9.4)'
box 110 1960 300 56 $ACC 'gte(t,9.4)'
box 910 1960 300 56 $INK 'gte(t,9.4)'
# the saved toast slides up from 10.5
add "drawbox=x=410:y='2380+max(0,(10.8-t))*400':w=500:h=110:color=$INK:t=fill:enable='gte(t,10.5)'"
add "drawbox=x=450:y='2420+max(0,(10.8-t))*400':w=30:h=30:color=0x46C080:t=fill:enable='gte(t,10.5)'"
# source-time bar along the bottom edge
add "drawbox=x=0:y=2852:w='max(2,$W*t/$DUR)':h=16:color=$GREY:t=fill"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=$BG:s=${W}x${H}:r=$FPS:d=$DUR" \
  -vf "$f,scale=trunc($W*$SCALE/2)*2:trunc($H*$SCALE/2)*2,format=yuv420p" -r $FPS -fps_mode cfr \
  -c:v libx264 -preset veryfast -crf 18 -g 30 -movflags +faststart public/rec/sample.mp4

# the same app as a web page, 1600x1000, on the same source timeline (for the 'browser' device preset)
W=1600; H=1000; f=""
box 0 0 300 $H $SOFT                                   # sidebar with five nav items
for i in 0 1 2 3 4; do box 40 $((120 + i * 70)) $((160 - i * 12)) 26 $GREY; done
box 1440 20 140 40 0xE5484D                             # leaked debug badge
box 360 60 420 56 $INK; box 360 140 300 28 $GREY        # header
for i in 0 1 2; do                                      # three feed cards side by side
  x=$((360 + i * 405)); box $x 210 370 200 $CARD
  box $((x + 30)) 240 110 110 "$([ $i = 0 ] && echo 0xF2B8A0 || ([ $i = 1 ] && echo 0xA8C9A0 || echo 0xB8B4E8))"
  box $((x + 165)) 250 170 30 $INK; box $((x + 165)) 300 140 22 $GREY
done
box 360 860 1180 80 $CARD
frame 360 860 1180 80 $GREY 3 'lt(t,2.0)'
frame 360 860 1180 80 $ACC 4 'gte(t,2.0)'
x=390; tc=2.5
for ((i = 0; i < ${#TEXT}; i++)); do
  ch="${TEXT:i:1}"
  if [ "$ch" = " " ]; then x=$((x + 12)); else box $x 880 16 40 $INK "gte(t,$tc)"; x=$((x + 21)); fi
  tc=$(python3 -c "print(round($tc + 0.12, 2))")
done
box 1450 870 70 60 $SOFT 'lt(t,5.4)'
box 1450 870 70 60 $INK 'gte(t,5.4)'
box 1450 870 70 60 $ACC 'between(t,6.0,6.18)'
for k in 0 1 2; do box $((400 + k * 40)) 600 24 24 $GREY "between(t,6.15,7.6)*lt(mod(t*3-$k*0.33,1),0.5)"; done
box 360 440 1180 340 $EDGE 'gte(t,7.6)'
box 363 443 1174 334 $CARD 'gte(t,7.6)'
box 410 470 360 40 $INK 'gte(t,7.6)'
for r in 0 1 2; do
  y=$((530 + r * 56)); tr=$(python3 -c "print(round(7.9 + $r * 0.5, 2))")
  c="$([ $r = 0 ] && echo 0xF2B8A0 || ([ $r = 1 ] && echo 0xA8C9A0 || echo 0xB8B4E8))"
  box 410 $y 30 30 "$c" "gte(t,$tr)"
  box 460 $((y + 2)) $((420 - r * 70)) 26 $INK "gte(t,$tr)"
  box 1330 $((y + 2)) 160 26 $GREY "gte(t,$tr)"
done
box 410 706 1080 3 $SOFT 'gte(t,9.4)'
box 410 720 220 40 $ACC 'gte(t,9.4)'
box 1270 720 220 40 $INK 'gte(t,9.4)'
# the saved toast drops in at the top right from 10.5
add "drawbox=x=1180:y='80-max(0,(10.8-t))*300':w=360:h=70:color=$INK:t=fill:enable='gte(t,10.5)'"
add "drawbox=x=1205:y='103-max(0,(10.8-t))*300':w=24:h=24:color=0x46C080:t=fill:enable='gte(t,10.5)'"
add "drawbox=x=0:y=992:w='max(2,$W*t/$DUR)':h=8:color=$GREY:t=fill"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=$BG:s=${W}x${H}:r=$FPS:d=$DUR" \
  -vf "$f,scale=trunc($W*$SCALE/2)*2:trunc($H*$SCALE/2)*2,format=yuv420p" -r $FPS -fps_mode cfr \
  -c:v libx264 -preset veryfast -crf 18 -g 30 -movflags +faststart public/rec/sample_web.mp4

# a stand-in "photo": a soft colour field with grain, 1920x1920
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "gradients=s=1920x1920:c0=0x3B2F2A:c1=0x8C6A55:c2=0xD9B48F:c3=0x51606B:n=4:speed=0:seed=7" \
  -vf "noise=alls=6:allf=t,gblur=sigma=12" -frames:v 1 -q:v 3 public/img/sample_room.jpg

for v in public/rec/sample.mp4 public/rec/sample_web.mp4; do
  ffprobe -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,nb_frames -of csv=p=0 "$v"
done
ls -la public/rec/sample.mp4 public/rec/sample_web.mp4 public/img/sample_room.jpg

#!/usr/bin/env bash
# store.sh: render an App Store app preview and check it against Apple's spec.
#
# Usage (from the template root):
#   bash render/store.sh [CompositionId] <outname> [mix.wav]
#   bash render/store.sh Store-886x1920 acme_preview public/audio/store_mix.wav
#   FRAMES=0-89 bash render/store.sh Store-886x1920 test     # a 3 s test range; the 15-30 s check is skipped
#
# Writes:
#   out/master/<outname>.mov   ProRes 4444 from PNG frames, no audio (the archival master)
#   out/store/<outname>.mp4    H.264 High, yuv420p, constant 11.5 Mbps (Apple asks for 10-12;
#                              ffprobe reads about 10.7), the composition's fps
#                              (at most 30), stereo AAC 256 kb/s at 48 kHz
# With no mix.wav the file gets a silent stereo track: uploads without an audio track have been refused.
#
# Then it probes the file and exits non-zero if any of these fail: H.264 High, yuv420p, the composition's exact
# size, at most 30 fps, video 10-12 Mbps, AAC stereo 48 kHz at about 256 kb/s, under 500 MB, 15-30 s long (skipped
# with FRAMES). Look the spec up again before each project (references/branches.md, Store preview); stores change it.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ $# -ge 2 ] && [[ "$1" == Store-* ]]; then COMP="$1"; shift; else COMP="Store-886x1920"; fi
NAME="${1:?output name}"; MIX="${2:-}"
mkdir -p out/master out/store
env -u NODE_OPTIONS npx remotion render src/index.ts "$COMP" "out/master/$NAME.mov" \
  --codec prores --prores-profile 4444 --image-format png --muted ${FRAMES:+--frames=$FRAMES} > "out/master/$NAME.log" 2>&1 \
  || { tail -20 "out/master/$NAME.log"; exit 1; }

probe() { ffprobe -v error -select_streams "$2" -show_entries "$3" -of default=nw=1:nk=1 "$1" | head -1; }
M="out/master/$NAME.mov"
FPS_R=$(probe "$M" v:0 stream=r_frame_rate)
NFR=$(ffprobe -v error -count_packets -select_streams v:0 -show_entries stream=nb_read_packets -of default=nw=1:nk=1 "$M")
VDUR=$(python3 -c "n,d='$FPS_R'.split('/'); print(f'{$NFR*int(d)/int(n):.6f}')")
echo "master: $NFR frames at $FPS_R = ${VDUR}s"

OUT="out/store/$NAME.mp4"
V=(-c:v libx264 -preset slow -profile:v high -pix_fmt yuv420p -b:v 11.5M -minrate 11.5M -maxrate 11.5M -bufsize 23M
   -x264-params nal-hrd=cbr -movflags +faststart)
A=(-c:a aac -b:a 256k -ar 48000 -ac 2)
if [ -n "$MIX" ]; then
  ffmpeg -loglevel error -y -i "$M" -i "$MIX" -map 0:v -map 1:a "${V[@]}" -af apad "${A[@]}" -t "$VDUR" "$OUT"
else
  ffmpeg -loglevel error -y -i "$M" -f lavfi -i anullsrc=r=48000:cl=stereo -map 0:v -map 1:a "${V[@]}" "${A[@]}" -t "$VDUR" "$OUT"
fi

# The spec check, on the delivered file.
W=$(probe "$M" v:0 stream=width); H=$(probe "$M" v:0 stream=height)
python3 - "$OUT" "$W" "$H" "${FRAMES:-}" "$MIX" <<'PY'
import json, os, subprocess, sys
f, W, H, frames, silent = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4], not sys.argv[5]
p = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', f],
                              capture_output=True, text=True, check=True).stdout)
v = next(s for s in p['streams'] if s['codec_type'] == 'video')
a = next((s for s in p['streams'] if s['codec_type'] == 'audio'), None)
n, d = map(int, v['r_frame_rate'].split('/'))
dur = float(p['format']['duration'])
vb = int(v.get('bit_rate', 0)) / 1e6
checks = [
    ('video codec h264 High', v['codec_name'] == 'h264' and v.get('profile') == 'High', f"{v['codec_name']} {v.get('profile')}"),
    ('pixel format yuv420p', v.get('pix_fmt') == 'yuv420p', v.get('pix_fmt')),
    (f'size {W}x{H}', (v['width'], v['height']) == (W, H), f"{v['width']}x{v['height']}"),
    ('frame rate <= 30', n / d <= 30 + 1e-6, f'{n / d:.3f}'),
    ('video 10-12 Mbps', 10 <= vb <= 12, f'{vb:.2f} Mbps'),
    ('audio AAC stereo 48 kHz', a is not None and a['codec_name'] == 'aac' and a['channels'] == 2 and a['sample_rate'] == '48000',
     'none' if a is None else f"{a['codec_name']} {a['channels']}ch {a['sample_rate']} Hz"),
    # AAC spends almost nothing on silence, so the silent track (no mix) reads a few kb/s: only a mix is checked.
    ('audio about 256 kb/s', a is not None and (silent or 200 <= int(a.get('bit_rate', 0)) / 1e3 <= 270),
     'none' if a is None else f"{int(a.get('bit_rate', 0)) / 1e3:.0f} kb/s" + (' (silent track, not checked)' if silent else '')),
    ('under 500 MB', os.path.getsize(f) < 500e6, f'{os.path.getsize(f) / 1e6:.1f} MB'),
]
if frames:
    print(f'note: FRAMES={frames}, so the 15-30 s length check is skipped ({dur:.2f} s)')
else:
    checks.append(('length 15-30 s', 15 <= dur <= 30, f'{dur:.2f} s'))
bad = 0
for name, ok, got in checks:
    print(('ok    ' if ok else 'FAIL  ') + f'{name}: {got}')
    bad += not ok
sys.exit(1 if bad else 0)
PY
ls -la "$OUT"

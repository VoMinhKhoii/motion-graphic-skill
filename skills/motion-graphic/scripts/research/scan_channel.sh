#!/usr/bin/env bash
# scan_channel.sh: list a YouTube channel's videos and shorts as JSON lines, without downloading anything.
#
# Usage:
#   scan_channel.sh <handle> [outdir] [max]
#   scan_channel.sh OpenAI refs/lists 200
#
#   handle  the channel handle without "@" (youtube.com/@<handle>)
#   outdir  where to write <outdir>/yt_<handle>.jsonl (default: lists)
#   max     items per tab (default: 200)
#
# Each line: {"ch", "tab" (videos|shorts), "title", "dur" (s), "url", "views"}. Sort by views or date, pick the
# launch films, then feed their URLs to download.sh. Needs yt-dlp and python3.
set -euo pipefail
h="${1:?usage: scan_channel.sh <handle> [outdir] [max]}"
out="${2:-lists}"; max="${3:-200}"
mkdir -p "$out"
for tab in videos shorts; do
  yt-dlp --flat-playlist --playlist-end "$max" -j "https://www.youtube.com/@$h/$tab" 2>/dev/null \
  | python3 -c "
import sys, json
for l in sys.stdin:
    d = json.loads(l)
    print(json.dumps({'ch': '$h', 'tab': '$tab', 'title': d.get('title'), 'dur': d.get('duration'), 'url': d.get('url'), 'views': d.get('view_count')}))" || true
done > "$out/yt_$h.jsonl"
echo "$h: $(wc -l < "$out/yt_$h.jsonl" | tr -d ' ') items -> $out/yt_$h.jsonl"

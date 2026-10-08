#!/usr/bin/env bash
# tiktok.sh: list a TikTok profile's videos as JSON lines, without downloading. Works logged out.
#
# Usage:
#   tiktok.sh <handle> [outdir] [max]
#   tiktok.sh notionhq lists 200
#
#   handle  without "@" (tiktok.com/@<handle>)
#   outdir  writes <outdir>/tt_<handle>.jsonl (default: lists)
#   max     items to list (default 200)
#
# Each line: {"ch", "title" (the caption), "dur" (s), "views", "date" (YYYYMMDD or null), "url"}; the same
# shape scan_channel.sh writes, so youtube_channel_filter.py filters it too:
#   youtube_channel_filter.py lists/tt_notionhq.jsonl --title 'introducing|launch|new' --max-dur 60 --urls urls.txt
#   ../download.sh urls.txt vids/
#
# Profiles are the reliable route. Hashtag (tiktok:tag), sound and search extraction are marked broken or
# blocked in current yt-dlp; find accounts on the web (web_queries.md) and list their profiles instead.
# If TikTok answers with an empty list, retry later, or ask the user to paste the profile's video links. Needs yt-dlp and python3.
set -euo pipefail
h="${1:?usage: tiktok.sh <handle> [outdir] [max]}"; h="${h#@}"
out="${2:-lists}"; max="${3:-200}"
mkdir -p "$out"
yt-dlp --flat-playlist --playlist-end "$max" -j "https://www.tiktok.com/@$h" 2>/dev/null | H="$h" python3 -c '
import json, os, sys, datetime
for line in sys.stdin:
    d = json.loads(line)
    ts = d.get("timestamp")
    date = datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y%m%d") if ts else d.get("upload_date")
    print(json.dumps({"ch": os.environ["H"], "title": (d.get("title") or d.get("description") or "")[:200], "dur": d.get("duration"),
                      "views": d.get("view_count"), "date": date, "url": d.get("url") or d.get("webpage_url")}, ensure_ascii=False))' \
  > "$out/tt_$h.jsonl" || true
echo "$h: $(wc -l < "$out/tt_$h.jsonl" | tr -d ' ') items -> $out/tt_$h.jsonl"

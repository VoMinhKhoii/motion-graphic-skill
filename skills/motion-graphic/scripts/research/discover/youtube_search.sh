#!/usr/bin/env bash
# youtube_search.sh: search YouTube for candidate films and write one JSON line per hit. Downloads nothing.
#
# Usage:
#   youtube_search.sh "<query>" [N] [--min-dur S] [--max-dur S] [--min-views V] [--full] [--out file.jsonl]
#   youtube_search.sh "app launch video motion design" 40 --max-dur 120 --min-views 10000
#   youtube_search.sh "introducing" 30 --full --out lists/yt_introducing.jsonl
#
#   N            number of search results to ask for (default 20); filters run after, so you may get fewer
#   --min-dur    drop hits shorter than S seconds        --max-dur    drop hits longer than S seconds
#   --min-views  drop hits with fewer than V views
#   --full       resolve every hit (about 1-2 s each) to get the upload date; flat search leaves date empty
#   --out        write here instead of stdout
#
# Each line: {"title", "channel", "handle", "duration", "views", "date" (YYYYMMDD or null), "url", "query"}.
# Then: pick the films you want, put their URLs in a file, and run ../download.sh urls.txt vids/.
# Search ranking favours tutorials and agencies; channel scans (../scan_channel.sh + youtube_channel_filter.py)
# find a brand's own launch films more reliably. Needs yt-dlp and python3.
set -euo pipefail
q="${1:?usage: youtube_search.sh \"query\" [N] [--min-dur S] [--max-dur S] [--min-views V] [--full] [--out f]}"
shift
n=20
if [ $# -gt 0 ] && [[ "$1" =~ ^[0-9]+$ ]]; then n="$1"; shift; fi
mind=0; maxd=0; minv=0; full=0; out=""
while [ $# -gt 0 ]; do
  case "$1" in
    --min-dur) mind="$2"; shift 2 ;;
    --max-dur) maxd="$2"; shift 2 ;;
    --min-views) minv="$2"; shift 2 ;;
    --full) full=1; shift ;;
    --out) out="$2"; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
flat=(--flat-playlist); [ "$full" = 1 ] && flat=(--skip-download --no-warnings)
run() {
  yt-dlp "ytsearch$n:$q" "${flat[@]}" -j 2>/dev/null | Q="$q" MIND="$mind" MAXD="$maxd" MINV="$minv" python3 -c '
import json, os, sys
mind, maxd, minv = float(os.environ["MIND"]), float(os.environ["MAXD"]), float(os.environ["MINV"])
for line in sys.stdin:
    d = json.loads(line)
    dur, views = d.get("duration") or 0, d.get("view_count") or 0
    if dur < mind or (maxd and dur > maxd) or views < minv:
        continue
    print(json.dumps({"title": d.get("title"), "channel": d.get("channel"), "handle": d.get("uploader_id"),
                      "duration": dur, "views": views, "date": d.get("upload_date"),
                      "url": d.get("webpage_url") or d.get("url"), "query": os.environ["Q"]}, ensure_ascii=False))'
}
if [ -n "$out" ]; then
  mkdir -p "$(dirname "$out")"; run > "$out"; echo "$(wc -l < "$out" | tr -d ' ') hits -> $out" >&2
else
  run
fi

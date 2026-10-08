#!/usr/bin/env bash
# download.sh: download reference films (X, YouTube, TikTok, Instagram, anything yt-dlp supports) for study.
#
# Usage:
#   download.sh <urls.txt> [outdir]
#   download.sh refs/urls.txt refs/vids
#
#   urls.txt  one URL per line; blank lines and lines starting with # are skipped
#   outdir    default: vids
#
# Writes <outdir>/<uploader>__<id>.mp4 plus <same>.info.json (title, description, views, date), capped at
# 1080p, merged to MP4. Files already present are skipped, so the script can be re-run after a failure.
# X/Twitter: public posts usually work without login; if one fails, add --cookies-from-browser <browser> to ARGS.
# These are third-party films: study them locally, describe them in words and numbers, never redistribute them.
set -uo pipefail
list="${1:?usage: download.sh <urls.txt> [outdir]}"; out="${2:-vids}"
mkdir -p "$out"
ARGS=(-f "bv*[height<=1080]+ba/b[height<=1080]/b" --merge-output-format mp4 --write-info-json --no-playlist
      --restrict-filenames -o "$out/%(uploader_id,uploader)s__%(id)s.%(ext)s" --download-archive "$out/.archive")
ok=0; fail=0
while IFS= read -r url; do
  url="${url%%#*}"; url="$(echo "$url" | xargs)"; [ -z "$url" ] && continue
  if yt-dlp "${ARGS[@]}" "$url" >/dev/null 2>"$out/.last_err"; then ok=$((ok + 1)); else
    fail=$((fail + 1)); echo "FAIL $url: $(tail -1 "$out/.last_err")"
  fi
done < "$list"
echo "done: $ok ok, $fail failed -> $out"

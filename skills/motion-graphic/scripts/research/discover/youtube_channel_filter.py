#!/usr/bin/env python3
"""youtube_channel_filter.py: keep the launch films from a channel scan, drop the rest.

Usage:
  youtube_channel_filter.py <scan.jsonl> [<scan.jsonl> ...] [--title REGEX] [--exclude REGEX]
                            [--min-dur S] [--max-dur S] [--min-views V] [--tab videos|shorts]
                            [--sort views|dur] [--top K] [--urls urls.txt]

  youtube_channel_filter.py lists/yt_OpenAI.jsonl --title 'introducing|launch|meet|now available' --max-dur 120
  youtube_channel_filter.py lists/yt_*.jsonl --title 'teaser|coming|soon|sneak' --max-dur 40 --urls teasers.txt

Input: the JSON lines from ../scan_channel.sh ({"ch","tab","title","dur","url","views"}) or from
youtube_search.sh ({"title","channel","duration","views","url",...}); both shapes are read.
--title and --exclude are case-insensitive regexes on the title. Default exclude drops obvious non-films
(livestream, podcast, interview, webinar, full keynote, tutorial, "how to").
Prints a table (views, seconds, channel, title, url) and, with --urls, writes the kept URLs one per line for
../download.sh. Pure python3, no dependencies.
"""
import argparse, json, re, sys

DEFAULT_EXCLUDE = r'live ?stream|podcast|interview|webinar|keynote|full event|tutorial|how to|q&a|ama\b'


def rows(paths):
    for p in paths:
        for line in open(p, encoding='utf-8'):
            if not line.strip():
                continue
            d = json.loads(line)
            yield {'ch': d.get('ch') or d.get('handle') or d.get('channel') or '', 'tab': d.get('tab', ''),
                   'title': d.get('title') or '', 'dur': d.get('dur', d.get('duration')) or 0,
                   'views': d.get('views') or 0, 'url': d.get('url') or ''}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('scans', nargs='+')
    ap.add_argument('--title', default='', help='keep titles matching this regex')
    ap.add_argument('--exclude', default=DEFAULT_EXCLUDE, help="drop titles matching this regex ('' to keep all)")
    ap.add_argument('--min-dur', type=float, default=0); ap.add_argument('--max-dur', type=float, default=0)
    ap.add_argument('--min-views', type=float, default=0); ap.add_argument('--tab', default='')
    ap.add_argument('--sort', choices=['views', 'dur'], default='views'); ap.add_argument('--top', type=int, default=0)
    ap.add_argument('--urls', help='write kept URLs here')
    a = ap.parse_args()
    keep_re = re.compile(a.title, re.I) if a.title else None
    drop_re = re.compile(a.exclude, re.I) if a.exclude else None
    kept = []
    for r in rows(a.scans):
        if keep_re and not keep_re.search(r['title']):
            continue
        if drop_re and drop_re.search(r['title']):
            continue
        if r['dur'] < a.min_dur or (a.max_dur and r['dur'] > a.max_dur) or r['views'] < a.min_views:
            continue
        if a.tab and r['tab'] != a.tab:
            continue
        kept.append(r)
    kept.sort(key=lambda r: -r[a.sort])
    if a.top:
        kept = kept[:a.top]
    for r in kept:
        print(f"{r['views']:>11,}  {r['dur']:>5.0f}s  {r['ch'][:18]:<18}  {r['title'][:70]:<70}  {r['url']}")
    print(f'{len(kept)} kept', file=sys.stderr)
    if a.urls:
        with open(a.urls, 'w') as f:
            f.write(''.join(r['url'] + '\n' for r in kept))
        print(f'urls -> {a.urls}', file=sys.stderr)


if __name__ == '__main__':
    main()

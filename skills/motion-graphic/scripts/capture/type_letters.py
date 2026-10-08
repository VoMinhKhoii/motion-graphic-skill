#!/usr/bin/env python3
"""type_letters.py: type into the focused field of the iOS Simulator one character at a time, like a person.

Usage:
  type_letters.py "<sentence>" [--min 0.01] [--max 0.04] [--pause 0.12]

Env: SIM_UDID (default: the first booted simulator).

Sends one `idb ui text` call per character with a random 10-40 ms gap, plus --pause after , . : ; +.
Letter by letter matters: a field that receives a whole word at once (idb text "word") jumps a word per frame
on screen, and no amount of slowing down in the edit makes that look typed. A letter-level take can later be
sped up 2-4x in the edit and still read as typing. For non-ASCII text see telex.py.
"""
import argparse, json, os, random, subprocess, sys, time


def udid():
    u = os.environ.get('SIM_UDID')
    if u:
        return u
    d = json.loads(subprocess.check_output(['xcrun', 'simctl', 'list', 'devices', 'booted', '-j']))
    for devs in d['devices'].values():
        for x in devs:
            if x.get('state') == 'Booted':
                return x['udid']
    sys.exit('no booted simulator; boot one or set SIM_UDID')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('text'); ap.add_argument('--min', type=float, default=0.01); ap.add_argument('--max', type=float, default=0.04)
    ap.add_argument('--pause', type=float, default=0.12)
    a = ap.parse_args()
    u = udid()
    for ch in a.text:
        subprocess.run(['idb', 'ui', 'text', '--udid', u, ch], check=True)
        time.sleep(random.uniform(a.min, a.max) + (a.pause if ch in ',.:;+' else 0))


if __name__ == '__main__':
    sys.exit(main())

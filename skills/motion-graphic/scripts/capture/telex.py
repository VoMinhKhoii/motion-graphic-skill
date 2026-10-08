#!/usr/bin/env python3
"""telex.py: Vietnamese text to the Telex keystrokes that type it.

Usage:
  telex.py "<Vietnamese text>"         prints the keystrokes, e.g. "phở bò" -> "phowr bof"
  from telex import keys                keys(text) -> one keystroke string per character

Each character becomes its base letter, its shape key (aa/ee/oo for the circumflex, aw for the breve, ow/uw for
the horn, dd for đ), then its tone key (s acute, f grave, r hook, x tilde, j dot), right after its own vowel.

Why this exists, and the general lesson for any non-ASCII text: automation tools that "type text" into a
simulator (idb ui text, simctl) send key events for a US keyboard. They cannot send precomposed characters like
"ở" or "é" or CJK. Type the way a person on that language's keyboard would: switch the Simulator to the
language's input method (Settings > General > Keyboard > Keyboards; for Vietnamese keep only "Vietnamese - Telex"
for the take) and send that input method's keystrokes, so the app sees real composed input. For languages with an
IME candidate step (Japanese, Chinese), script the candidate pick too, or paste with `xcrun simctl pbcopy` and a
long-press Paste (paste shows no typing, so use it only where typing is not on screen). Turn autocorrect,
auto-capitalisation and smart punctuation off for the take, and check every take for a flashed suggestion bubble.
"""
import sys, unicodedata

TONES = {'́': 's', '̀': 'f', '̉': 'r', '̃': 'x', '̣': 'j'}
SHAPE = {'̂': lambda b: b + b, '̆': lambda b: b + 'w', '̛': lambda b: b + 'w'}  # circumflex, breve, horn


def keys(text):
    out = []
    for ch in text:
        if ch in 'đĐ':
            out.append('dd' if ch == 'đ' else 'DD')
            continue
        d = unicodedata.normalize('NFD', ch)
        base, marks = d[0], d[1:]
        k = base
        for m in marks:
            if m in SHAPE:
                k = SHAPE[m](base)
        for m in marks:
            if m in TONES:
                k += TONES[m]
        out.append(k)
    return out


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    print(''.join(keys(sys.argv[1])))

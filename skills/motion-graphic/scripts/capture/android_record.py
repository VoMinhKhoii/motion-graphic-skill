#!/usr/bin/env python3
"""android_record.py: record an Android emulator or device over adb and log every action with its time, so the
edit can be cut from the log instead of by scrubbing. The Android twin of ios_sim_record.py.

Usage (each command is a separate call; state lives in <REC_DIR>/.rec.json between calls):
  android_record.py prep                  save the current settings, then: clean status bar (demo mode), spell
                                          checker off, touch dots and pointer location off
  android_record.py start NAME            start recording to <REC_DIR>/NAME.mp4 (returns once recording has begun;
                                          exits 1, writing no state, if it did not)
  android_record.py tap X Y LABEL         tap at (X, Y) in screen pixels (adb works in pixels, not points)
  android_record.py swipe X1 Y1 X2 Y2 [S] swipe in pixels over S seconds (default 0.4)
  android_record.py type "TEXT"           type one character at a time (see "Text" below), logged start and end
  android_record.py key KEYCODE [LABEL]   press a key: ENTER, BACK, HOME, DEL, or a number
  android_record.py mark LABEL            log a moment ("result landed", "take 2")
  android_record.py stop                  stop the recording, pull the file, print the log
  android_record.py unprep                restore the settings `prep` saved (and the keyboard), leave demo mode

Env:
  ANDROID_SERIAL  the device or emulator to drive (adb devices). adb itself reads it. Needed when two are attached.
  REC_DIR         where clips and logs go (default: ./clips)
  BITRATE         screenrecord bit rate in Mbit/s (default 20; the default 4 smears UI text)
  START_TIMEOUT   seconds `start` waits for the recording to begin (default 8)
  ADB_TIMEOUT     seconds any other adb call may take before the script gives up (default 20)

Starting is checked, not assumed. `start` waits for screenrecord's setup line (--verbose), or, failing that,
for the process to be alive with the file on the device after 2 s. If screenrecord exits early (no device, an
unauthorised device, an encoder that refuses the size) or nothing happens within START_TIMEOUT, it kills the
local adb process, prints what screenrecord said, writes no state and exits 1, so a take never runs blind.

The log, <REC_DIR>/NAME.events, has lines "<seconds since recording started> <label>". Times are when the
command was sent; each `adb shell input` call starts a process on the device, so the screen reacts 0.15-0.5 s
later (more on a cold emulator). Find the exact frame of each reaction with frame_pts.py or
research/activity.py, and time the film's pointer taps to that frame.

screenrecord limits:
  - 3 minutes per file (--time-limit caps at 180 s). The recording stops by itself; plan takes under 3 minutes
    or record several and cut between them. `stop` warns if a take hit the limit.
  - Variable frame rate: like simctl, it writes a frame only when the screen changes. Always run
    vfr_to_cfr.sh on the pulled file before Remotion sees it.
  - No audio. Some devices refuse sizes above the panel's own; the emulator records at its full resolution.
  - The first 0.3-1 s can be black on some emulators: start, wait a second, then act (the log shows when).

Text: `adb shell input text` types ASCII only, sends the whole string at once, and needs spaces as %s and
shell characters escaped. This script sends one character per call for a letter-by-letter take (about 4-8
characters per second, limited by adb; speed it up in the edit if needed, see references/engine.md). For
anything outside ASCII (accents, Vietnamese, emoji) `input text` fails: install ADBKeyboard
(github.com/senzhk/ADBKeyBoard), make it the active keyboard (`adb shell ime set com.android.adbkeyboard/.AdbIME`),
and this script sends each character through it. ADBKeyboard has no on-screen keys, so the keyboard is not
visible in the take; if the film must show a keyboard, type ASCII with the normal one, or paste the text
(put it on the clipboard on the device, long-press the field, Paste) and cut the paste in the edit.

Clean takes: `prep` turns on demo mode (clock 9:41, full battery and signal, no notification icons), turns the
spell checker off and hides touch dots. Before it changes anything it saves the current values (spell checker,
show touches, pointer location, demo-mode permission, the active keyboard) to <REC_DIR>/.prep.json; running
`prep` again keeps the first snapshot. `unprep` puts those exact values back (a setting that was unset is
deleted again), switches back to the saved keyboard if you changed it (ADBKeyboard), leaves demo mode and
deletes the snapshot. Run it at delivery, on the same device (it warns if the serial differs). Autocorrect and the suggestion strip belong to the keyboard app, not to
adb: in Gboard turn off Settings > Text correction > Auto-correction and Show suggestion strip by hand, once.

Needs the Android SDK platform-tools (adb) and an emulator (Android Studio > Device Manager, a Pixel image) or a
device with USB debugging on. Not yet run against a real emulator or device; the start checks and the prep/unprep
restore are tested against a stub adb (tests/check_android_record.py). Run `prep`, a 10 s take and `stop` once
before relying on it.
"""
import json, os, queue, random, shlex, signal, subprocess, sys, threading, time

REC_DIR = os.path.abspath(os.environ.get('REC_DIR', 'clips'))
STATE = os.path.join(REC_DIR, '.rec.json')
PREP = os.path.join(REC_DIR, '.prep.json')
LIMIT = 180  # screenrecord's own maximum, seconds
ADBKBD = 'com.android.adbkeyboard/.AdbIME'
START_TIMEOUT = float(os.environ.get('START_TIMEOUT', '8'))
ADB_TIMEOUT = float(os.environ.get('ADB_TIMEOUT', '20'))
# The settings `prep` changes, as (namespace, key, value during the take).
PREP_SETTINGS = [('secure', 'spell_checker_enabled', '0'), ('system', 'show_touches', '0'),
                 ('system', 'pointer_location', '0'), ('global', 'sysui_demo_allowed', '1')]


def adb(*args, check=True, capture=False, timeout=None):
    try:
        r = subprocess.run(['adb', *args], check=check, capture_output=capture, text=True, timeout=timeout or ADB_TIMEOUT)
    except FileNotFoundError:
        sys.exit('adb not found: install the Android SDK platform-tools and put adb on PATH')
    except subprocess.TimeoutExpired:
        sys.exit(f"adb {' '.join(args)[:80]} did not answer in {timeout or ADB_TIMEOUT:.0f} s: is the device connected and "
                 'authorised (adb devices)?')
    except subprocess.CalledProcessError as e:
        sys.exit(f"adb {' '.join(args)[:80]} failed (exit {e.returncode}): {(e.stderr or e.stdout or '').strip()[-300:]}")
    return r.stdout if capture else None


def sh(cmd, check=True):
    return adb('shell', cmd, check=check, capture=True)


def log(label):
    st = json.load(open(STATE))
    with open(st['events'], 'a') as f:
        f.write(f"{time.time() - st['t0']:.3f} {label}\n")


def demo(on):
    if on:
        sh('settings put global sysui_demo_allowed 1')
        cmds = ['enter', 'clock -e hhmm 0941', 'battery -e level 100 -e plugged false', 'network -e wifi show -e level 4',
                'network -e mobile show -e datatype none -e level 4', 'notifications -e visible false']
        for c in cmds:
            sh(f'am broadcast -a com.android.systemui.demo -e command {c}')
    else:
        sh('am broadcast -a com.android.systemui.demo -e command exit')


def ascii_arg(ch):
    """One character as an `input text` argument: %s for a space, everything shell-special quoted."""
    return '%s' if ch == ' ' else shlex.quote(ch)


def type_chars(text):
    imes = sh('ime list -s')
    adbkbd = ADBKBD in imes and ADBKBD in sh('settings get secure default_input_method')
    for ch in text:
        if ch.isascii() and ch.isprintable():
            sh(f'input text {ascii_arg(ch)}')
        elif adbkbd:
            sh(f"am broadcast -a ADB_INPUT_TEXT --es msg {shlex.quote(ch)}")
        else:
            sys.exit(f"'{ch}' is not ASCII and `input text` cannot type it. Install ADBKeyboard and make it the "
                     f'active keyboard (adb shell ime set {ADBKBD}), or paste the text (see --help).')
        # a person's rhythm on top of adb's own ~0.15 s per call: a beat after punctuation
        time.sleep(random.uniform(0.0, 0.03) + (0.12 if ch in ',.:;+' else 0))


def serial():
    return (adb('get-serialno', capture=True, check=False) or '').strip()


def prep():
    """Snapshot what prep changes, then change it. A second prep keeps the first snapshot: the values from before
    any prep are the ones to restore."""
    if os.path.exists(PREP):
        print(f'keeping the snapshot from the first prep ({PREP}); run unprep to restore it')
    else:
        snap = {'serial': serial(), 'settings': {f'{ns} {key}': sh(f'settings get {ns} {key}').strip() for ns, key, _ in PREP_SETTINGS},
                'keyboard': sh('settings get secure default_input_method').strip()}
        json.dump(snap, open(PREP, 'w'), indent=1)
        print('saved the current settings to', PREP)
    for ns, key, val in PREP_SETTINGS:
        sh(f'settings put {ns} {key} {val}')
    demo(True)
    print('demo mode on (9:41, full battery and signal, no notifications); spell checker, touch dots and pointer\n'
          'location off. By hand, once: Gboard > Text correction > Auto-correction off, Show suggestion strip off\n'
          '(write down what they were; unprep cannot restore the keyboard app\'s own settings).')


def unprep():
    """Put back exactly what prep found: a value, or "null" (the setting did not exist), which is deleted again."""
    demo(False)
    if not os.path.exists(PREP):
        print('no prep snapshot (.prep.json): left demo mode only. Check spell checker, show touches, pointer location '
              'and the keyboard by hand.', file=sys.stderr)
        return
    snap = json.load(open(PREP))
    if snap.get('serial') and snap['serial'] != serial():
        print(f"WARNING: the snapshot is from device {snap['serial']}, this is {serial()}: restoring anyway.", file=sys.stderr)
    for k, v in snap['settings'].items():
        ns, key = k.split()
        sh(f'settings delete {ns} {key}' if v in ('null', '') else f'settings put {ns} {key} {shlex.quote(v)}')
    kb = snap.get('keyboard', 'null')
    if kb not in ('null', '') and sh('settings get secure default_input_method').strip() != kb:
        sh(f'ime set {shlex.quote(kb)}')
    os.remove(PREP)
    print('restored:', ', '.join(f'{k}={v}' for k, v in snap['settings'].items()), f'keyboard={kb}; demo mode off')


def on_device(remote):
    """True if the file exists on the device. A short timeout of its own: a hung adb answers "not yet"."""
    try:
        r = subprocess.run(['adb', 'shell', f'test -e {remote} && echo yes'], capture_output=True, text=True, timeout=3)
    except subprocess.TimeoutExpired:
        return False
    return r.stdout.strip() == 'yes'


def start(name):
    """Start screenrecord and return only once it is recording. State is written after that, never before."""
    remote = f'/sdcard/{name}.mp4'
    rate = int(float(os.environ.get('BITRATE', '20')) * 1e6)
    sh(f'rm -f {remote}', check=False)  # an old file of the same name would pass the "file exists" check
    p = subprocess.Popen(['adb', 'shell', 'screenrecord', '--verbose', '--bit-rate', str(rate), '--time-limit', str(LIMIT), remote],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
    lines, q = [], queue.Queue()
    threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
    t_start, how, reason = time.time(), '', ''
    while not how and not reason:
        try:
            line = q.get(timeout=0.2); lines.append(line.rstrip())
            # --verbose prints the display and encoder setup before the first frame
            if 'Content area' in line or 'Configuring recorder' in line:
                how = 'screenrecord reported its setup'
        except queue.Empty:
            pass
        if p.poll() is not None:
            how, reason = '', f'screenrecord exited at once (code {p.returncode})'
        elif not how and time.time() - t_start >= 2 and on_device(remote):
            how = 'the file is on the device and screenrecord is running'
        elif not how and time.time() - t_start >= START_TIMEOUT:
            reason = f'no sign of a recording after {START_TIMEOUT:.0f} s'
    if how:  # confirm: still running a second later, and the file is there
        time.sleep(1.0)
        alive, there = p.poll() is None, on_device(remote)
        if not (alive and there):
            gone = [f'screenrecord had exited (code {p.returncode})'] if not alive else []
            reason = f"{how}, but 1 s later " + ' and '.join(gone + ([] if there else ['the file was not on the device']))
    if reason:
        if p.poll() is None:
            os.killpg(p.pid, signal.SIGKILL)
        try:  # and the device side, in case it did start
            subprocess.run(['adb', 'shell', 'pkill -INT screenrecord'], capture_output=True, timeout=5)
        except subprocess.TimeoutExpired:
            pass
        said = '\n  '.join(l for l in lines[-8:] if l) or '(nothing)'
        print(f'NOT RECORDING: {reason}. screenrecord said:\n  {said}\nNo state written. Check `adb devices` (one device, '
              '"device" not "unauthorized"), ANDROID_SERIAL, and try a lower BITRATE.', file=sys.stderr)
        return 1
    t0 = time.time()
    events = os.path.join(REC_DIR, name + '.events')
    json.dump({'pid': p.pid, 't0': t0, 'events': events, 'out': os.path.join(REC_DIR, name + '.mp4'), 'remote': remote}, open(STATE, 'w'))
    open(events, 'w').write('0.000 recording started\n')
    print('recording', remote, f'({how}; stops by itself after {LIMIT} s)')
    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ('-h', '--help'):
        print(__doc__); return 1
    cmd = sys.argv[1]
    os.makedirs(REC_DIR, exist_ok=True)
    if cmd == 'prep':
        prep()
    elif cmd == 'unprep':
        unprep()
    elif cmd == 'start':
        return start(sys.argv[2])
    elif cmd == 'tap':
        x, y, label = sys.argv[2], sys.argv[3], sys.argv[4]
        log(f'tap {label} {x} {y}')
        sh(f'input tap {x} {y}')
    elif cmd == 'swipe':
        x1, y1, x2, y2 = sys.argv[2:6]
        dur = float(sys.argv[6]) if len(sys.argv) > 6 else 0.4
        log(f'swipe {x1} {y1} {x2} {y2} {dur}')
        sh(f'input swipe {x1} {y1} {x2} {y2} {int(dur * 1000)}')
    elif cmd == 'type':
        log('type start'); type_chars(sys.argv[2]); log('type end')
    elif cmd == 'key':
        code = sys.argv[2]
        log(f"key {sys.argv[3] if len(sys.argv) > 3 else code}")
        sh(f"input keyevent {code if code.isdigit() else 'KEYCODE_' + code.upper()}")
    elif cmd == 'mark':
        log(sys.argv[2])
    elif cmd == 'stop':
        st = json.load(open(STATE))
        log('stop')
        took = time.time() - st['t0']
        # SIGINT on the device lets screenrecord finish the file; killing the local adb process does not stop it
        sh('pkill -INT screenrecord', check=False)
        for _ in range(60):
            try:
                os.kill(st['pid'], 0); time.sleep(0.5)
            except ProcessLookupError:
                break
        time.sleep(1.0)  # the file is finalised after the process prints its last line
        adb('pull', st['remote'], st['out'])
        sh(f"rm {st['remote']}", check=False)
        print(open(st['events']).read())
        if took >= LIMIT - 1:
            print(f'WARNING: the take ran {took:.0f} s; screenrecord stopped at {LIMIT} s, so events after that have no picture.')
        print('wrote', st['out'], os.path.getsize(st['out']) if os.path.exists(st['out']) else 'MISSING')
        print('next: vfr_to_cfr.sh', st['out'], '<public/rec/NAME.mp4>   (screenrecord writes variable frame rate)')
    else:
        print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())

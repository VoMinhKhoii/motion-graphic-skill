#!/usr/bin/env python3
"""ios_sim_record.py: record the iOS Simulator and log every action with its time, so the edit can be cut
from the log instead of by scrubbing.

Usage (each command is a separate call; state lives in <REC_DIR>/.rec.json between calls):
  ios_sim_record.py start NAME           start recording to <REC_DIR>/NAME.mp4 (returns once recording has begun)
  ios_sim_record.py tap X Y LABEL        tap at (X, Y) in points (idb coordinates), logged as "tap LABEL X Y"
  ios_sim_record.py swipe X1 Y1 X2 Y2 [S]  swipe in points over S seconds (default 0.4)
  ios_sim_record.py type "TEXT"          type one character at a time, like a person (logged start and end)
  ios_sim_record.py telex "TEXT"         Vietnamese through the Simulator's Vietnamese Telex keyboard (see telex.py)
  ios_sim_record.py mark LABEL           log a moment ("result landed", "take 2")
  ios_sim_record.py stop                 stop the recording, print the log

Env:
  SIM_UDID   the simulator to drive (xcrun simctl list devices booted). Default: the first booted simulator.
  REC_DIR    where clips and logs go (default: ./clips)

The log, <REC_DIR>/NAME.events, has lines "<seconds since recording started> <label>". Times are when the
command was sent; the screen reacts 0.1-0.4 s later. Find the exact frame of each reaction with frame_pts.py or
research/activity.py, and time the film's pointer taps to that frame.

After stop, run vfr_to_cfr.sh on the clip: simctl writes variable frame rate and drops frames while the screen
is still, and Remotion mis-seeks on such files.

Needs Xcode (xcrun simctl) and idb (pip install fb-idb, brew install idb-companion).
"""
import json, os, queue, random, signal, subprocess, sys, threading, time

REC_DIR = os.path.abspath(os.environ.get('REC_DIR', 'clips'))
STATE = os.path.join(REC_DIR, '.rec.json')


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


def log(label):
    st = json.load(open(STATE))
    with open(st['events'], 'a') as f:
        f.write(f"{time.time() - st['t0']:.3f} {label}\n")


def idb(*args):
    subprocess.run(['idb', 'ui', *args, '--udid', udid()], check=True)


def type_chars(chars):
    for ch in chars:
        idb('text', ch)
        # a person's rhythm: 10-40 ms between keys, a beat after punctuation
        time.sleep(random.uniform(0.01, 0.04) + (0.12 if ch in ',.:;+' else 0))


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 1
    cmd = sys.argv[1]
    os.makedirs(REC_DIR, exist_ok=True)
    if cmd == 'start':
        name = sys.argv[2]
        if os.path.exists(STATE):
            prev = json.load(open(STATE))
            try:
                os.kill(prev['pid'], 0)
                sys.exit(f"a take is still recording ({prev['out']}); run `stop` first")
            except (ProcessLookupError, PermissionError, KeyError):
                pass  # the previous take has ended; its state is stale
        out = os.path.join(REC_DIR, name + '.mp4')
        p = subprocess.Popen(['xcrun', 'simctl', 'io', udid(), 'recordVideo', '--codec=h264', '--force', out],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, start_new_session=True)
        # simctl prints "Recording started" once frames flow; anything else (an exit, an error, silence) is a failure
        lines, q, started, reason = [], queue.Queue(), False, ''
        threading.Thread(target=lambda: [q.put(l) for l in p.stdout], daemon=True).start()
        t_start = time.time()
        while not started and not reason:
            try:
                line = q.get(timeout=0.2); lines.append(line.rstrip())
                started = 'Recording started' in line
                if started:
                    t_seen = time.time()  # the footage's time zero; the check below must not shift it
            except queue.Empty:
                pass
            if not started and p.poll() is not None:
                reason = f'simctl exited (code {p.returncode})'
            elif not started and time.time() - t_start > 10:
                reason = 'no "Recording started" after 10 s'
        if started:
            time.sleep(0.5)
            if p.poll() is not None:
                reason = f'simctl exited right after starting (code {p.returncode})'
        if reason:
            if p.poll() is None:
                os.killpg(p.pid, signal.SIGKILL)
            said = '\n  '.join(l for l in lines[-8:] if l) or '(nothing)'
            print(f'NOT RECORDING: {reason}. simctl said:\n  {said}\nNo state written. Check the booted simulator '
                  '(`xcrun simctl list devices booted`) and SIM_UDID.', file=sys.stderr)
            sys.exit(1)
        t0 = t_seen
        events = os.path.join(REC_DIR, name + '.events')
        json.dump({'pid': p.pid, 't0': t0, 'events': events, 'out': out}, open(STATE, 'w'))
        open(events, 'w').write('0.000 recording started\n')
        print('recording', out)
    elif cmd == 'tap':
        x, y, label = sys.argv[2], sys.argv[3], sys.argv[4]
        log(f'tap {label} {x} {y}')
        idb('tap', x, y)
    elif cmd == 'swipe':
        x1, y1, x2, y2 = sys.argv[2:6]
        dur = sys.argv[6] if len(sys.argv) > 6 else '0.4'
        log(f'swipe {x1} {y1} {x2} {y2} {dur}')
        idb('swipe', x1, y1, x2, y2, '--duration', dur)
    elif cmd == 'type':
        log('type start'); type_chars(sys.argv[2]); log('type end')
    elif cmd == 'telex':
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from telex import keys
        log('type start')
        for k in keys(sys.argv[2]):
            type_chars(k)
        log('type end')
    elif cmd == 'mark':
        log(sys.argv[2])
    elif cmd == 'stop':
        st = json.load(open(STATE))
        log('stop')
        os.killpg(st['pid'], signal.SIGINT)  # SIGINT lets simctl finish the file; SIGKILL leaves it unplayable
        for _ in range(60):
            try:
                os.kill(st['pid'], 0); time.sleep(0.5)
            except ProcessLookupError:
                break
        print(open(st['events']).read())
        print('wrote', st['out'], os.path.getsize(st['out']) if os.path.exists(st['out']) else 'MISSING')
    else:
        print(__doc__); return 1


if __name__ == '__main__':
    sys.exit(main())

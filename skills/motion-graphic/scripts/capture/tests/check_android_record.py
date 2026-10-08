#!/usr/bin/env python3
"""check_android_record.py: test android_record.py against a stub `adb` (no emulator or device needed).

Usage:
  check_android_record.py

The stub keeps the device's settings in a JSON file and acts out one mode per run of android_record.py:
  fail   every adb call exits 1 ("no devices")                    start must exit 1 and write no state
  hang   screenrecord prints nothing and never writes a file      start must give up after START_TIMEOUT, exit 1,
                                                                  write no state and kill the local adb process
  early  screenrecord prints its setup line, then exits 1         start must notice and exit 1, no state
  ok     screenrecord prints its setup line and records           start exits 0 and writes state; stop pulls the file
Then prep/unprep: the stub starts with the spell checker already off, touch dots on, pointer location and the
demo-mode permission unset, and a custom keyboard. prep must snapshot those, a second prep must keep the first
snapshot, and unprep must restore them exactly (unset settings deleted again, the keyboard switched back after
ADBKeyboard was made active) rather than to fixed values.
Prints one line per check; exits 1 if any fails.
"""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(HERE, 'android_record.py')

STUB = r'''#!/usr/bin/env python3
import json, os, signal, sys, time
mode, db, pidf = os.environ['STUB_MODE'], os.environ['STUB_DB'], os.environ['STUB_PID']
a = sys.argv[1:]
if mode == 'fail':
    print('error: no devices/emulators found', file=sys.stderr); sys.exit(1)
store = json.load(open(db)) if os.path.exists(db) else {}
save = lambda: json.dump(store, open(db, 'w'))
if a[0] == 'get-serialno':
    print('emulator-5554'); sys.exit(0)
if a[0] == 'pull':
    open(a[2], 'wb').write(b'fake mp4'); sys.exit(0)
cmd = ' '.join(a[1:]); w = cmd.split()
if w[0] == 'screenrecord':
    open(pidf, 'w').write(str(os.getpid()))
    if mode == 'hang':
        time.sleep(600)
    print('Display is 1080x2400 @60.00fps', flush=True)
    print('Configuring recorder for 1080x2400 video/avc at 20.00Mbps', flush=True)
    if mode == 'early':
        time.sleep(0.2); print('ERROR: unable to configure video encoder', flush=True); sys.exit(1)
    print('Content area is 1080x2400 at offset x=0 y=0', flush=True)
    store['file'] = 1; save()
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    time.sleep(600)
elif cmd.startswith('test -e'):
    print('yes' if mode == 'ok' and store.get('file') else '')
elif w[:2] == ['settings', 'get']:
    print(store.get(f'{w[2]} {w[3]}', 'null'))
elif w[:2] == ['settings', 'put']:
    store[f'{w[2]} {w[3]}'] = w[4]; save()
elif w[:2] == ['settings', 'delete']:
    store.pop(f'{w[2]} {w[3]}', None); save()
elif w[:2] == ['ime', 'set']:
    store['secure default_input_method'] = w[2]; save()
elif 'com.android.systemui.demo' in cmd:
    if w[-1] in ('enter', 'exit'):
        store['demo'] = w[-1]; save()
elif cmd.startswith('pkill'):
    try:
        os.kill(int(open(pidf).read()), signal.SIGTERM)
    except Exception:
        pass
'''

bad = 0


def check(name, ok, got=''):
    global bad
    print(('ok    ' if ok else 'FAIL  ') + name + (f'  ({got})' if got and not ok else ''))
    bad += not ok


def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    # a zombie still answers kill 0; ps shows its state
    st = subprocess.run(['ps', '-o', 'stat=', '-p', str(pid)], capture_output=True, text=True).stdout.strip()
    return bool(st) and not st.startswith('Z')


def main():
    work = tempfile.mkdtemp(prefix='androidrec_')
    bin_dir = os.path.join(work, 'bin'); os.makedirs(bin_dir)
    open(os.path.join(bin_dir, 'adb'), 'w').write(STUB); os.chmod(os.path.join(bin_dir, 'adb'), 0o755)
    db, pidf, rec = os.path.join(work, 'device.json'), os.path.join(work, 'sr.pid'), os.path.join(work, 'clips')
    state = os.path.join(rec, '.rec.json')

    def run(mode, *args, timeout=60):
        env = {**os.environ, 'PATH': bin_dir + os.pathsep + os.environ['PATH'], 'STUB_MODE': mode, 'STUB_DB': db,
               'STUB_PID': pidf, 'REC_DIR': rec, 'START_TIMEOUT': '2', 'ADB_TIMEOUT': '5'}
        t = time.time()
        r = subprocess.run([sys.executable, REC, *args], capture_output=True, text=True, env=env, timeout=timeout)
        return r.returncode, r.stdout + r.stderr, time.time() - t

    for mode in ('fail', 'hang', 'early'):
        for f in (db, pidf, state):
            if os.path.exists(f):
                os.remove(f)
        rc, out, took = run(mode, 'start', 'take1')
        check(f'{mode}: start exits non-zero', rc != 0, (rc, out[-300:]))
        check(f'{mode}: no state written', not os.path.exists(state))
        check(f'{mode}: says NOT RECORDING', 'NOT RECORDING' in out, out[-300:])
        if mode == 'hang':
            check('hang: gives up within START_TIMEOUT + a few seconds', took < 8, f'{took:.1f}s')
            time.sleep(0.3)
            check('hang: the local adb screenrecord process was killed', os.path.exists(pidf) and not alive(int(open(pidf).read())))

    for f in (db, pidf, state):
        if os.path.exists(f):
            os.remove(f)
    rc, out, _ = run('ok', 'start', 'take1')
    check('ok: start exits 0 and writes state', rc == 0 and os.path.exists(state), out[-300:])
    rc, out, _ = run('ok', 'tap', '100', '200', 'send')
    rc, out, _ = run('ok', 'stop')
    check('ok: stop pulls the file and logs the tap', rc == 0 and os.path.exists(os.path.join(rec, 'take1.mp4')) and 'tap send' in out, out[-300:])

    # prep / unprep restore the original values, not fixed ones
    json.dump({'secure spell_checker_enabled': '0', 'system show_touches': '1', 'secure default_input_method': 'com.example/.Ime'},
              open(db, 'w'))
    before = json.load(open(db))
    rc, out, _ = run('ok', 'prep')
    dev = json.load(open(db))
    check('prep: exits 0 and changes the settings', rc == 0 and dev['system show_touches'] == '0' and dev['system pointer_location'] == '0'
          and dev['global sysui_demo_allowed'] == '1' and dev.get('demo') == 'enter', (rc, dev))
    snap = json.load(open(os.path.join(rec, '.prep.json')))
    check('prep: snapshot holds the originals', snap['settings'] == {'secure spell_checker_enabled': '0', 'system show_touches': '1',
          'system pointer_location': 'null', 'global sysui_demo_allowed': 'null'} and snap['keyboard'] == 'com.example/.Ime', snap)
    run('ok', 'prep')  # a second prep must not snapshot the prepped values
    check('second prep keeps the first snapshot', json.load(open(os.path.join(rec, '.prep.json'))) == snap)
    dev = json.load(open(db)); dev['secure default_input_method'] = 'com.android.adbkeyboard/.AdbIME'; json.dump(dev, open(db, 'w'))
    rc, out, _ = run('ok', 'unprep')
    dev = json.load(open(db))
    restored = {k: v for k, v in dev.items() if k not in ('demo', 'file')}
    check('unprep: every setting back to its original (unset ones deleted, keyboard restored)', rc == 0 and restored == before,
          (restored, before))
    check('unprep: demo mode left, snapshot removed', dev.get('demo') == 'exit' and not os.path.exists(os.path.join(rec, '.prep.json')))

    shutil.rmtree(work, ignore_errors=True)
    print('all checks passed' if not bad else f'{bad} checks FAILED')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()

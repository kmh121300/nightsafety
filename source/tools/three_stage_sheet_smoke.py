"""Exercise hidden/summary/detail route sheet gestures on an installed emulator APK."""
import argparse
import hashlib
import json
import os
import time
from integration_smoke import Smoke, PACKAGE, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', default='emulator-5556')
    args = parser.parse_args()
    assert args.serial.startswith('emulator-')
    s = Smoke(os.path.join(os.environ['LOCALAPPDATA'], 'Android/Sdk/platform-tools/adb.exe'), args.serial)
    s.output_dir.mkdir(parents=True)
    outcome, failure = 'FAIL', ''
    apk_hash = hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest()
    installed = s.shell('pm', 'path', PACKAGE).strip().removeprefix('package:')
    assert s.shell('sha256sum', installed).split()[0] == apk_hash
    try:
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.wait(lambda: s.find(id='route_spinner') is not None, 'Initial summary missing')
        time.sleep(2)
        s.dump()
        summary = s.bounds(s.find(id='controls_scroll'))
        x = (summary[0] + summary[2]) // 2
        s.shell('input', 'swipe', x, summary[1] + 25, x, summary[3] - 80, 500)
        s.wait(lambda: s.find(id='sheet_restore_area') is not None, 'Summary did not hide', timeout=15)
        assert s.find(id='route_spinner') is None, 'Hidden sheet still exposes summary'
        s.screenshot('hidden.png')
        edge = s.bounds(s.find(id='sheet_restore_area'))
        for control in ('location', 'preview', 'reset_map'):
            assert s.bounds(s.find(id=control))[3] <= edge[1], 'Map buttons overlap restore bar'
        s.shell('input', 'swipe', x, (edge[1] + edge[3]) // 2, x, summary[1] - 150, 350)
        s.wait(lambda: s.find(id='route_spinner') is not None and
               abs(s.bounds(s.find(id='controls_scroll'))[1] - summary[1]) <= 4,
               'Bottom edge did not restore summary')
        s.screenshot('summary.png')
        s.shell('input', 'swipe', x, summary[1] + 25, x, 200, 500)
        s.wait(lambda: s.find(id='controls_scroll') is not None and
               s.bounds(s.find(id='controls_scroll'))[1] < summary[1] - 80, 'Summary did not expand')
        s.screenshot('detail.png')
        detail = s.bounds(s.find(id='controls_scroll'))
        s.shell('input', 'swipe', x, detail[1] + 25, x, summary[3] - 80, 250)
        s.wait(lambda: abs(s.bounds(s.find(id='controls_scroll'))[1] - summary[1]) <= 4,
               'Downward fling skipped summary', timeout=15)
        assert s.find(id='sheet_restore_area') is None
        s.shell('input', 'swipe', x, summary[1] + 25, x, summary[3] - 80, 500)
        s.wait(lambda: s.find(id='sheet_restore_area') is not None, 'Second hide failed')
        s.click(id='reset_map')
        s.dump()
        assert s.find(id='sheet_restore_area') is None, 'Restore area blocks fullscreen map'
        s.shell('input', 'keyevent', '4')
        s.wait(lambda: s.find(id='sheet_restore_area') is not None, 'Fullscreen exit lost hidden state')
        s.click(id='sheet_restore_area')
        s.wait(lambda: s.find(id='route_spinner') is not None, 'Accessible restore click failed')
        outcome = 'PASS'
    except Exception as error:
        failure = str(error)
        s.screenshot('failure.png')
    finally:
        (s.output_dir / 'three-stage-result.json').write_text(json.dumps(dict(
            date=time.strftime('%Y-%m-%d'), apk_sha256=apk_hash, outcome=outcome, failure=failure,
            size=s.shell('wm', 'size').strip(), density=s.shell('wm', 'density').strip()
        ), indent=2), encoding='utf-8')
        print(outcome, failure, 'Evidence:', s.output_dir, flush=True)
    assert outcome == 'PASS', failure


if __name__ == '__main__':
    main()

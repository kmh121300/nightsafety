"""Verify top card minimize/restore independently of the route sheet and fullscreen."""
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
        s.wait(lambda: s.find(id='route_spinner') is not None, 'Initial route not ready')
        s.wait(lambda: s.find(id='minimize_top_card') is not None, 'Minimize button missing', timeout=8)
        origin = s.find(id='origin_input').get('text')
        destination = s.find(id='destination_input').get('text')
        summary = s.find(id='route_summary').get('text')
        sheet = s.bounds(s.find(id='controls_scroll'))
        s.click(id='minimize_top_card')
        s.wait(lambda: s.find(id='expand_top_card') is not None, 'Expand icon missing')
        assert all(s.find(id=x) is None for x in ['origin_input', 'destination_input', 'favorite_list'])
        assert s.bounds(s.find(id='controls_scroll')) == sheet, 'Minimize moved lower sheet'
        s.screenshot('minimized.png')
        s.click(id='reset_map')
        s.dump()
        assert s.find(id='expand_top_card') is None, 'Expand icon blocks fullscreen'
        s.shell('input', 'keyevent', '4')
        s.wait(lambda: s.find(id='expand_top_card') is not None, 'Fullscreen exit lost minimized state')
        s.click(id='expand_top_card')
        s.wait(lambda: s.find(id='origin_input') is not None, 'Top card did not expand')
        assert s.find(id='origin_input').get('text') == origin
        assert s.find(id='destination_input').get('text') == destination
        assert s.find(id='route_summary').get('text') == summary
        s.wait(lambda: s.find(id='map_attribution') is not None and
               s.bounds(s.find(id='map_attribution'))[1] >= s.bounds(s.find(id='top_container'))[3],
               'Expanded card covers map attribution')
        s.screenshot('expanded.png')
        outcome = 'PASS'
    except Exception as error:
        failure = str(error)
        s.screenshot('failure.png')
    finally:
        (s.output_dir / 'top-card-result.json').write_text(json.dumps(dict(
            date=time.strftime('%Y-%m-%d'), apk_sha256=apk_hash, outcome=outcome, failure=failure,
            size=s.shell('wm', 'size').strip(), density=s.shell('wm', 'density').strip()
        ), indent=2), encoding='utf-8')
        print(outcome, failure, 'Evidence:', s.output_dir, flush=True)
    assert outcome == 'PASS', failure


if __name__ == '__main__':
    main()

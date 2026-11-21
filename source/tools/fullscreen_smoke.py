"""Check map fullscreen entry, exit, state and adaptive layouts on an emulator."""
import argparse
import hashlib
import json
import os
import re
import time

from integration_smoke import PACKAGE, ROOT, Smoke


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='emulator-5556')
    parser.add_argument('--profile', choices=('standard', 'small', 'pane'), default='standard')
    args = parser.parse_args()
    assert args.serial.startswith('emulator-'), 'Use an emulator for temporary screen overrides'
    s = Smoke(os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe'), args.serial)
    apk_hash = hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest()
    installed = s.shell('pm', 'path', PACKAGE).strip().removeprefix('package:')
    assert s.shell('sha256sum', installed).split()[0] == apk_hash, 'Installed APK differs from local APK'
    original = {key: s.shell('wm', key).strip() for key in ('size', 'density')}
    outcome, failure, cleanup_errors = 'FAIL', '', []
    try:
        if args.profile != 'standard':
            size, density = {'small': ('720x1280', '360'), 'pane': ('1200x1920', '320')}[args.profile]
            s.shell('wm', 'size', size)
            s.shell('wm', 'density', density)
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.expect('지도 준비 완료', id='map_status')
        s.search()
        summary = s.visible('route_summary').get('text')
        before = s.bounds(s.find(id='map_container'))
        assert s.find(id='reset_map').get('text') == '전체화면', 'Fullscreen button label missing'
        for mode in ('tmap', 'local'):
            if mode == 'local':
                s.tap_node(s.find(id='preview'))
                s.expect('로컬 좌표 미리보기', id='map_status')
            s.click(id='reset_map')
            s.wait(lambda: s.find(id='reset_map', text='화면 복귀') is not None, 'Fullscreen exit unavailable')
            assert all(s.find(id=id) is None for id in ('search_routes', 'controls_scroll', 'map_status', 'favorite_list'))
            full = s.bounds(s.find(id='map_container'))
            assert full[3] - full[1] > before[3] - before[1], 'Map did not expand vertically'
            assert full[2] - full[0] >= before[2] - before[0], 'Map narrowed'
            root = s.bounds(s.nodes[0])
            density = int(re.findall(r'\d+', s.shell('wm', 'density'))[-1]) / 160
            assert full[0] <= root[0] + 1 and full[2] >= root[2] - 1, 'Map does not fill available width'
            assert full[1] - root[1] <= 64 * density and root[3] - full[3] <= 64 * density, 'Non-map panels still occupy fullscreen'
            s.screenshot(args.profile + '-' + mode + '-fullscreen.png')
            if mode == 'tmap':
                s.tap_node(s.find(id='reset_map'))
            else:
                s.shell('input', 'keyevent', '4')
            s.wait(lambda: s.find(id='reset_map', text='화면 복귀') is None and s.find(id='reset_map', text='전체화면') is not None,
                   'Original map controls not restored')
            assert s.bounds(s.find(id='map_container')) == before, 'Map layout not restored'
            assert s.find(id='route_summary').get('text') == summary, 'Search result changed'
            s.passed(args.profile + ': ' + mode + ' fullscreen expands, hides panels, exits and preserves route')
        s.tap_node(s.find(id='preview'))
        s.expect('지도 준비 완료', id='map_status')
        s.screenshot(args.profile + '-restored.png')
        outcome = 'PASS'
    except Exception as error:
        failure = str(error) or type(error).__name__
        s.screenshot('failure.png')
        print('FAIL: ' + failure, flush=True)
    finally:
        for key, value in original.items():
            try:
                override = re.search(r'Override ' + key + r':\s*(\S+)', value, re.I)
                s.shell('wm', key, override[1] if override else 'reset')
                assert s.shell('wm', key).strip() == value
            except Exception as error:
                cleanup_errors.append(str(error) or key + ' restore failed')
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.output_dir.mkdir(exist_ok=True)
        result = dict(date=time.strftime('%Y-%m-%d'), profile=args.profile, outcome=outcome,
                      failure=failure, cleanup_errors=cleanup_errors, steps=s.steps,
                      apk_sha256=apk_hash)
        (s.output_dir / 'fullscreen-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Evidence: ' + str(s.output_dir), flush=True)
    assert outcome == 'PASS' and not cleanup_errors, failure or 'Screen cleanup failed'


if __name__ == '__main__':
    main()

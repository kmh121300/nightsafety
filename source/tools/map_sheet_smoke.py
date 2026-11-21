"""Visual regression checks for floating controls and the collapsed route sheet."""
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
    assert args.serial.startswith('emulator-'), 'Temporary screen changes require an emulator'
    s = Smoke(os.path.join(os.environ['LOCALAPPDATA'], 'Android', 'Sdk', 'platform-tools', 'adb.exe'), args.serial)
    original = {k: s.shell('wm', k).strip() for k in ('size', 'density')}
    apk_hash = hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest()
    installed = s.shell('pm', 'path', PACKAGE).strip().removeprefix('package:')
    assert s.shell('sha256sum', installed).split()[0] == apk_hash
    failure, cleanup = '', []
    measurements = {}
    try:
        if args.profile != 'standard':
            size, dpi = {'small': ('720x1280', '360'), 'pane': ('1200x1920', '320')}[args.profile]
            s.shell('wm', 'size', size)
            s.shell('wm', 'density', dpi)
        s.shell('cmd', 'statusbar', 'collapse')
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.wait(lambda: s.find(id='map_status') is not None, 'App screen not visible')
        s.expect('지도 준비 완료', id='map_status')
        time.sleep(1)
        dpi = int(re.findall(r'\d+', s.shell('wm', 'density'))[-1]) / 160
        s.dump()
        controls = {id: s.bounds(s.find(id=id)) for id in ('location', 'reset_map', 'preview')}
        obstacles = [s.bounds(s.find(id=id)) for id in ('favorite_list', 'search_card')]
        for box in controls.values():
            assert box[3] - box[1] >= 48 * dpi - 1, 'Map touch target smaller than 48dp'
            assert all(box[2] <= other[0] or box[0] >= other[2] or box[3] <= other[1] or box[1] >= other[3]
                       for other in obstacles), 'Map buttons overlap search/header'
        sheet = s.bounds(s.find(id='controls_scroll'))
        if args.profile != 'pane':
            assert all(box[3] <= sheet[1] - 4 * dpi for box in controls.values()), 'Map buttons overlap collapsed sheet'
            summary = s.find(id='route_summary')
            assert summary is not None, 'Collapsed summary missing'
            box = s.bounds(summary)
            assert box[3] < sheet[3] - 24 * dpi, 'Summary collides with navigation bar'
            assert box[3] - box[1] >= 30 * dpi, 'Two-line summary clipped'
            measurements['summary'] = box
        measurements.update(buttons=controls, sheet=sheet)
        s.screenshot(args.profile + '-collapsed.png')
        if args.profile != 'pane':
            s.dump()
            sheet = s.bounds(s.find(id='controls_scroll'))
            x1, y1, x2, y2 = sheet
            s.shell('input', 'swipe', (x1 + x2) // 2, y1 + int(10 * dpi), (x1 + x2) // 2, int(90 * dpi), 600)
            s.wait(lambda: s.bounds(s.find(id='controls_scroll'))[1] < y1 - 40 * dpi, 'Sheet did not expand')
            assert s.bounds(s.find(id='controls_scroll'))[1] >= 24 * dpi, 'Expanded drag handle overlaps status bar'
            s.screenshot(args.profile + '-expanded.png')
            s.dump()
            x1, y1, x2, y2 = s.bounds(s.find(id='controls_scroll'))
            s.shell('input', 'swipe', (x1 + x2) // 2, y1 + int(10 * dpi), (x1 + x2) // 2, y2 - int(20 * dpi), 600)
            time.sleep(1)
        s.click(id='reset_map')
        s.wait(lambda: s.find(id='reset_map', text='화면 복귀') is not None, 'Fullscreen unavailable')
        assert s.find(id='controls_scroll') is None and s.find(id='favorite_list') is None
        s.screenshot(args.profile + '-fullscreen.png')
        s.shell('input', 'keyevent', '4')
        s.expect('전체화면', id='reset_map')
        s.passed(args.profile + ': no overlap, visible summary, sheet and fullscreen/back')
    except Exception as error:
        failure = str(error) or type(error).__name__
        s.screenshot('failure.png')
        print('FAIL: ' + failure, flush=True)
    finally:
        s.shell('cmd', 'statusbar', 'collapse')
        for key, value in original.items():
            try:
                override = re.search(r'Override ' + key + r':\s*(\S+)', value, re.I)
                s.shell('wm', key, override[1] if override else 'reset')
                assert s.shell('wm', key).strip() == value
            except Exception as error:
                cleanup.append(str(error) or key)
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.output_dir.mkdir(exist_ok=True)
        (s.output_dir / 'map-sheet-result.json').write_text(json.dumps(dict(
            date=time.strftime('%Y-%m-%d'), profile=args.profile, apk_sha256=apk_hash,
            failure=failure, outcome='FAIL' if failure else 'PASS', cleanup_errors=cleanup,
            measurements=measurements, steps=s.steps), ensure_ascii=False, indent=2), encoding='utf-8')
        print('Evidence: ' + str(s.output_dir), flush=True)
    assert not failure and not cleanup, failure or 'Screen cleanup failed'


if __name__ == '__main__':
    main()

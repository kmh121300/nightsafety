"""Exercise development-emulator error/recovery paths; restore changed OS settings."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import time
from integration_smoke import Smoke, PACKAGE, ROOT


def mock_is_default(text):
    return ('No operations.' in text and 'Default mode: deny' in text) or text.strip().split(';')[0] == 'MOCK_LOCATION: default'


def failure_message(error):
    return str(error).splitlines()[0] if str(error).splitlines() else type(error).__name__


def capture_field_error(s, control, name):
    # Android EditText's error popup is absent from UIAutomator XML; inspect the capture.
    s.click(id=control)
    s.shell('input', 'keyevent', '4')
    s.screenshot(name)
    s.dump()
    assert s.find(id=control) is not None, 'Rejected-input dialog disappeared'


def permission_state(smoke):
    text = smoke.shell('dumpsys', 'package', PACKAGE)
    result = {}
    for name in ('ACCESS_COARSE_LOCATION', 'ACCESS_FINE_LOCATION'):
        match = re.search(r'android.permission.' + name + r': granted=(true|false), flags=\[([^\]]*)\]', text)
        assert match, 'Location permission state unavailable'
        result[name] = {'granted': match[1] == 'true',
                        'flags': [flag.strip() for flag in match[2].split('|') if flag.strip()]}
    return result


def run(s, added_providers):
    s.shell('am', 'force-stop', PACKAGE)
    s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
    s.expect('지도 준비 완료', id='map_status')
    origin = s.visible('origin_input').get('text')
    destination = s.visible('destination_input').get('text')

    s.click(id='destination_input')
    s.click(id='place_lookup')
    capture_field_error(s, 'place_query', 'blank-search.png')
    s.enter('zz_no_such_place_20261105', id='place_query')
    s.click(id='place_lookup')
    time.sleep(3)
    capture_field_error(s, 'place_query', 'no-result-search.png')
    s.enter('0', id='place_latitude')
    s.click(id='android:id/button1')
    capture_field_error(s, 'place_latitude', 'invalid-input.png')
    assert s.find(id='place_latitude') is not None, 'Invalid coordinate dialog closed'
    s.click(text='닫기')
    s.expect('검색 결과 없음', id='map_status')
    assert s.visible('destination_input').get('text') == destination
    s.passed('Blank/no-result place search and out-of-area coordinates keep the original endpoint')

    s.click(id='swap_endpoints')
    assert s.visible('origin_input').get('text') == destination
    assert s.visible('destination_input').get('text') == origin
    s.expect('현재 선은 이전 결과', id='map_status')
    s.click(id='save_favorite')
    s.expect('최신 경로를 검색한 뒤 저장하세요', id='map_status')
    s.click(id='swap_endpoints')
    assert s.visible('origin_input').get('text') == origin
    assert s.visible('destination_input').get('text') == destination
    s.passed('Two endpoint swaps restore labels and stale input cannot be saved as latest')

    s.search()
    scores = {control: s.visible(control).get('text') for control in ('score_value', 'average_value', 'weak_value')}
    s.command('reverse', '--remove', 'tcp:8765')
    s.click(id='search_routes')
    s.expect('경로 검색 실패:', id='map_status')
    s.expect('이전 결과 유지', id='map_status')
    for control, value in scores.items():
        s.expect(value, id=control)
    s.click(id='save_favorite')
    s.expect('최신 경로를 검색한 뒤 저장하세요', id='map_status')
    s.command('reverse', 'tcp:8765', 'tcp:8765')
    s.search()
    s.passed('Disconnected search reports failure and keeps old scores; stale save blocked; reconnect succeeds')

    # Explicit force-stop discards unsaved in-memory inputs; explicit Room saves were tested separately.
    s.click(id='swap_endpoints')
    s.shell('am', 'force-stop', PACKAGE)
    s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
    s.expect('지도 준비 완료', id='map_status')
    assert s.visible('origin_input').get('text') == origin
    assert s.visible('destination_input').get('text') == destination
    s.passed('Force-stop/relaunch uses default unsaved inputs; no latest server result is claimed at startup')

    for name in ('ACCESS_FINE_LOCATION', 'ACCESS_COARSE_LOCATION'):
        s.shell('pm', 'revoke', PACKAGE, 'android.permission.' + name)
        s.shell('pm', 'clear-permission-flags', PACKAGE, 'android.permission.' + name, 'user-set', 'user-fixed')
    s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
    s.expect('지도 준비 완료', id='map_status')
    s.click(id='location')
    s.wait(lambda: any(n.get('resource-id', '').endswith('/permission_deny_button') for n in s.nodes), 'OS permission prompt missing')
    s.screenshot('permission-request.png')
    s.tap_node(next(n for n in s.nodes if n.get('resource-id', '').endswith('/permission_deny_button')))
    s.dump()
    assert not any(state['granted'] for state in permission_state(s).values())
    assert s.visible('origin_input').get('text') == origin
    s.search()
    s.passed('OS location denial keeps manual endpoints and server route search usable')

    s.shell('appops', 'set', 'com.android.shell', 'android:mock_location', 'allow')
    for provider in ('network', 'gps'):
        s.shell('cmd', 'location', 'providers', 'add-test-provider', provider)
        added_providers.append(provider)
        s.shell('cmd', 'location', 'providers', 'set-test-provider-enabled', provider, 'true')
    s.shell('cmd', 'location', 'set-location-enabled', 'true')
    s.shell('pm', 'grant', PACKAGE, 'android.permission.ACCESS_COARSE_LOCATION')
    assert not permission_state(s)['ACCESS_FINE_LOCATION']['granted']
    s.click(id='location')
    s.expect('위치 확인 시간 초과', id='map_status')
    assert s.visible('origin_input').get('text') == origin
    s.screenshot('location-timeout.png')
    s.passed('Coarse-only permission with no mock fix times out and preserves manual origin')

    s.shell('pm', 'grant', PACKAGE, 'android.permission.ACCESS_FINE_LOCATION')
    s.click(id='location')
    s.shell('cmd', 'location', 'providers', 'set-test-provider-location', 'network', '--location', '37.346,126.736', '--accuracy', '5')
    s.expect('현재 위치', id='origin_input')
    s.expect('현재 선은 이전 결과', id='map_status')
    s.screenshot('mock-location.png')
    s.search()
    s.passed('Injected in-area precise location updates origin and allows route search')

    check_location_disabled(s)


def check_location_disabled(s):
    origin = s.visible('origin_input').get('text')
    s.shell('cmd', 'location', 'set-location-enabled', 'false')
    time.sleep(2)
    s.dump()
    if s.find(text='No location access') is not None:
        s.click(text='Close')
    assert s.shell('cmd', 'location', 'is-location-enabled').strip() == 'false'
    s.click(id='location')
    s.wait(lambda: any(text in (s.find(id='map_status').get('text', '') if s.find(id='map_status') is not None else '')
                       for text in ('받지 못했습니다', '시간 초과')), 'No GPS-off failure feedback')
    assert s.visible('origin_input').get('text') == origin
    s.screenshot('location-disabled.png')
    s.search()
    s.passed('Location disabled gives failure feedback without clearing origin or blocking manual search')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    parser.add_argument('--only-location-off', action='store_true', help='Retry the OS-dialog-blocked final check without repeating completed cases')
    args = parser.parse_args()
    assert args.serial.startswith('emulator-'), 'This test changes settings only on an emulator'
    s = Smoke(str(Path.home() / 'AppData/Local/Android/Sdk/platform-tools/adb.exe'), args.serial)
    original_permissions = permission_state(s)
    original_location = s.shell('cmd', 'location', 'is-location-enabled').strip()
    original_mock = s.shell('appops', 'get', 'com.android.shell', 'android:mock_location')
    assert mock_is_default(original_mock), 'Unexpected shell mock operation; preserve it manually'
    s.output_dir.mkdir(parents=True)
    outcome = 'PASS'
    failure = ''
    cleanup_errors = []
    added_providers = []
    try:
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        if args.only_location_off:
            s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
            s.expect('지도 준비 완료', id='map_status')
            s.shell('pm', 'grant', PACKAGE, 'android.permission.ACCESS_COARSE_LOCATION')
            s.shell('pm', 'grant', PACKAGE, 'android.permission.ACCESS_FINE_LOCATION')
            check_location_disabled(s)
        else:
            run(s, added_providers)
    except Exception as error:
        outcome = 'FAIL'
        failure = failure_message(error)
        print('FAIL: ' + failure, flush=True)
        try:
            s.screenshot('failure.png')
        except Exception:
            pass
    finally:
        actions = [('cmd', 'location', 'providers', 'remove-test-provider', p) for p in added_providers]
        actions += [('cmd', 'location', 'set-location-enabled', original_location),
                    ('appops', 'set', 'com.android.shell', 'android:mock_location', 'default')]
        for name, state in original_permissions.items():
            permission = 'android.permission.' + name
            actions += [('pm', 'grant' if state['granted'] else 'revoke', PACKAGE, permission),
                        ('pm', 'clear-permission-flags', PACKAGE, permission, 'user-set', 'user-fixed')]
            flags = [flag.lower().replace('_', '-') for flag in state['flags'] if flag in ('USER_SET', 'USER_FIXED')]
            if flags:
                actions.append(('pm', 'set-permission-flags', PACKAGE, permission, *flags))
        for action in actions:
            try:
                s.shell(*action)
            except Exception:
                cleanup_errors.append(' '.join(action[:3]))
        try:
            s.command('reverse', 'tcp:8765', 'tcp:8765')
            assert permission_state(s) == original_permissions, 'Permission state differs after cleanup'
            assert s.shell('cmd', 'location', 'is-location-enabled').strip() == original_location
            assert mock_is_default(s.shell('appops', 'get', 'com.android.shell', 'android:mock_location'))
            s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        except Exception as error:
            cleanup_errors.append(failure_message(error))
        report = {'date': time.strftime('%Y-%m-%d'), 'environment': args.serial + ' API35',
                  'apk_sha256': hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest(),
                  'outcome': outcome, 'steps': s.steps, 'failure': failure,
                  'original_permissions': original_permissions, 'original_location_enabled': original_location,
                  'cleanup_errors': cleanup_errors}
        (s.output_dir / 'error-recovery-result.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Evidence saved: ' + str(s.output_dir), flush=True)
    assert outcome == 'PASS' and not cleanup_errors, 'Error/recovery verification did not pass; see dated evidence'


if __name__ == '__main__':
    main()

"""Check compact portrait UI and isolated empty/error states; restore emulator display settings."""
import argparse
from copy import deepcopy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import time
import urllib.request
from integration_smoke import Smoke, PACKAGE, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    args = parser.parse_args()
    assert args.serial.startswith('emulator-'), 'Display settings may only be changed on a test emulator'
    s = Smoke(str(Path.home() / 'AppData/Local/Android/Sdk/platform-tools/adb.exe'), args.serial)
    s.output_dir.mkdir(parents=True)
    size, density = s.shell('wm', 'size'), s.shell('wm', 'density')
    request = {'region_id': 'siheung', 'origin': {'latitude': 37.3418341, 'longitude': 126.7315593, 'source': 'osm'},
               'destination': {'latitude': 37.35171, 'longitude': 126.7427421, 'source': 'osm'}}
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765/v1/routes/compare',
            data=json.dumps(request).encode(), headers={'Content-Type': 'application/json'}), timeout=30) as response:
        empty = deepcopy(json.load(response))
    empty['status'] = 'no_route'
    empty['data']['routes'] = []
    empty['data']['candidate_search_complete'] = True
    mode = ['empty']

    class FixtureHandler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length', '0')))
            payload = json.dumps(empty if mode[0] == 'empty' else {'error': {'message': '화면 검사 연결 오류'}}).encode()
            self.send_response(200 if mode[0] == 'empty' else 503)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    observations = []
    outcome, failure, cleanup_errors = 'PASS', '', []

    def buttons(profile, scale, state):
        s.dump()
        frame = s.find(id='map_container')
        assert frame is not None, 'Map frame missing'
        bounds = s.bounds(frame)
        record = {'profile': profile, 'state': state, 'map': bounds, 'buttons': {}}
        observations.append(record)
        for control in ('location', 'reset_map', 'preview'):
            node = s.find(id=control)
            assert node is not None, control + ' is outside the visible map'
            b = s.bounds(node)
            record['buttons'][control] = b
            assert b[2] - b[0] >= 48 * scale - 2 and b[3] - b[1] >= 48 * scale - 2, control + ' clipped below 48dp'
            assert bounds[0] <= b[0] < b[2] <= bounds[2] and bounds[1] <= b[1] < b[3] <= bounds[3], control + ' exceeds map bounds'

    try:
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        for profile, dimensions, dpi in (('small', '720x1280', 360), ('standard', '1080x2220', 440)):
            s.shell('wm', 'size', dimensions)
            s.shell('wm', 'density', str(dpi))
            s.shell('am', 'force-stop', PACKAGE)
            s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
            s.wait(lambda: s.find(id='map_status') is not None, 'App UI not ready')
            s.expect('지도 준비 완료', id='map_status')
            s.screenshot(profile + '-initial.png')
            buttons(profile, dpi / 160, 'initial')
            s.search()
            s.expect('CCTV 16 · 비상벨 16 · 보안등 12', id='route_facility_counts')
            for control in ('score_value', 'average_value', 'weak_value'):
                assert 0 <= float(s.visible(control).get('text', '')) <= 100
            s.screenshot(profile + '-metrics.png')
            buttons(profile, dpi / 160, 'normal search')
            s.click(id='data_info')
            s.expect('자료 정보')
            s.expect('보안등 기준일:')
            s.screenshot(profile + '-data-dialog.png')
            scroll = s.find(cls='android.widget.ScrollView')
            if scroll is not None and scroll.get('scrollable') == 'true':
                x1, y1, x2, y2 = s.bounds(scroll)
                s.shell('input', 'swipe', (x1 + x2) // 2, y2 - 20, (x1 + x2) // 2, y1 + 20, 600)
                s.expect('자료 정보')
                s.screenshot(profile + '-data-dialog-bottom.png')
            s.click(text='닫기')
            s.passed(profile + ': map touch targets, metric/count scrolling and data dialog reachable')
            if profile == 'small':
                s.click(id='destination_input')
                s.enter('anchor', id='place_query')
                s.click(id='place_lookup')
                s.click(text='정왕역 주변 보행 지점 (출구 연결 미검증)')
                buttons(profile, dpi / 160, 'long destination/stale result')
                s.screenshot('small-long-destination.png')
                s.command('reverse', 'tcp:8765', 'tcp:' + str(server.server_port))
                s.click(id='search_routes')
                s.expect('연결된 후보가 없습니다', id='map_status')
                s.expect('현재 입력에 연결된 경로가 없습니다', id='route_summary')
                assert s.visible('save_favorite').get('enabled') == 'false'
                assert s.visible('route_spinner').get('enabled') == 'false'
                s.screenshot('small-empty.png')
                buttons(profile, dpi / 160, 'empty result')
                mode[0] = 'error'
                s.click(id='search_routes')
                s.expect('화면 검사 연결 오류', id='map_status')
                s.expect('이전 결과 유지', id='map_status')
                s.screenshot('small-error.png')
                buttons(profile, dpi / 160, 'error')
                s.command('reverse', 'tcp:8765', 'tcp:8765')
                s.search()
                s.passed('small: long destination, empty/disabled controls, error text and live recovery')
    except Exception as error:
        outcome = 'FAIL'
        failure = str(error).splitlines()[0] if str(error).splitlines() else type(error).__name__
        print('FAIL: ' + failure, flush=True)
        try:
            s.screenshot('failure.png')
        except Exception:
            pass
    finally:
        for command, old in (('size', size), ('density', density)):
            try:
                override = re.search(r'Override ' + command + r':\s*(\S+)', old, re.I)
                s.shell('wm', command, override[1] if override else 'reset')
                assert s.shell('wm', command).strip() == old.strip(), command + ' not restored'
            except Exception as error:
                cleanup_errors.append(str(error) or type(error).__name__)
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        server.shutdown()
        server.server_close()
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        result = {'date': time.strftime('%Y-%m-%d'), 'serial': args.serial, 'outcome': outcome, 'failure': failure,
                  'apk_sha256': hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest(),
                  'steps': s.steps, 'original_size': size.strip(), 'original_density': density.strip(),
                  'observations': observations, 'cleanup_errors': cleanup_errors, 'adb_reverse_restored': True,
                  'empty_error_source': 'Isolated fixture on the selected emulator; no DB data changed'}
        (s.output_dir / 'screen-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Evidence saved: ' + str(s.output_dir), flush=True)
    assert outcome == 'PASS' and not cleanup_errors, 'Screen checks did not pass; see dated evidence'


if __name__ == '__main__':
    main()

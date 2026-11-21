"""Check route count UI and API36 input stability, including an isolated missing-source fixture."""
import argparse
from copy import deepcopy
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
import time
import urllib.request
from integration_smoke import Smoke, PACKAGE, ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', required=True)
    args = parser.parse_args()
    assert args.serial.startswith('emulator-'), 'Use an emulator for isolated response fixtures'
    s = Smoke(str(Path.home() / 'AppData/Local/Android/Sdk/platform-tools/adb.exe'), args.serial)
    request = {'region_id': 'siheung', 'origin': {'latitude': 37.3418341, 'longitude': 126.7315593, 'source': 'osm'},
               'destination': {'latitude': 37.35171, 'longitude': 126.7427421, 'source': 'osm'}}
    with urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:8765/v1/routes/compare',
            data=json.dumps(request).encode(), headers={'Content-Type': 'application/json'}), timeout=30) as response:
        live = json.load(response)
    counts = live['data']['routes'][0]['facility_counts']
    partial = deepcopy(live)
    partial['status'] = 'partial_success'
    partial['data']['missing_types'] = ['security_lamp']
    partial['data']['score_basis_types'] = ['cctv', 'emergency_bell']
    for route in partial['data']['routes']:
        route['facility_counts']['security_lamp'] = None
        route['score_status'] = 'partial'
        for key in ('safety_score', 'average_safety', 'weak_safety'):
            route[key] = None
    payload = json.dumps(partial).encode()

    class FixtureHandler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            self.rfile.read(int(self.headers.get('Content-Length', '0')))
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    server = ThreadingHTTPServer(('127.0.0.1', 0), FixtureHandler)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    s.output_dir.mkdir(parents=True)
    outcome, failure = 'PASS', ''
    pids = []

    def remember_pid(stage):
        pid = s.shell('pidof', PACKAGE).strip()
        assert pid and (not pids or pid == pids[0]['pid']), 'App process changed during input regression'
        pids.append({'stage': stage, 'pid': pid})

    try:
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.expect('지도 준비 완료', id='map_status')
        remember_pid('map_ready')
        s.search()
        expected = f'CCTV {counts["cctv"]} · 비상벨 {counts["emergency_bell"]} · 보안등 {counts["security_lamp"]}'
        s.expect(expected, id='route_facility_counts')
        s.screenshot('route-counts.png')
        s.click(id='cctv_filter')
        s.expect(expected, id='route_facility_counts')
        s.click(id='cctv_filter')
        s.expect(expected, id='route_facility_counts')
        s.passed('Three route counts match live API and remain unchanged by map filtering')
        for index in range(2):
            s.click(id='destination_input')
            s.visible('place_query')
            remember_pid('input_open_' + str(index + 1))
            s.click(text='닫기')
        s.passed('Repeated endpoint input dialogs open without app disappearance')

        s.command('reverse', 'tcp:8765', 'tcp:' + str(server.server_port))
        s.search()
        s.expect('보안등 —', id='route_facility_counts')
        s.expect('보안등 자료 미확보 · 부분 시설지표', id='warning')
        s.expect('—', id='average_value')
        s.expect('—', id='weak_value')
        s.screenshot('missing-lighting.png')
        s.passed('Injected missing-lighting response shows an unknown count and explicit partial-data reason')
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        s.search()
        s.expect(expected, id='route_facility_counts')
        s.expect('공공시설 기반 안전지표', id='score_heading')
        s.passed('Restoring the live server restores official metrics and lighting count')

        for control in ('origin_input', 'destination_input'):
            s.click(id=control)
            s.enter('anchor', id='place_query')
            s.click(id='place_lookup')
            s.click(text='대학 옆문 보행 지점 (현장 미검증)')
        s.search()
        s.expect('0m · 약 0.0분', id='route_summary')
        for control in ('score_value', 'average_value', 'weak_value'):
            s.expect('—', id=control)
        remember_pid('zero_route_complete')
        s.screenshot('api36-zero-route.png')
        s.passed('Normal route to same-anchor zero route clears scores while keeping the same app process')
    except Exception as error:
        outcome = 'FAIL'
        failure = str(error).splitlines()[0] if str(error).splitlines() else type(error).__name__
        print('FAIL: ' + failure, flush=True)
        try:
            s.screenshot('failure.png')
        except Exception:
            pass
    finally:
        s.command('reverse', 'tcp:8765', 'tcp:8765')
        server.shutdown()
        server.server_close()
        result = {'date': time.strftime('%Y-%m-%d'), 'serial': args.serial,
                  'apk_sha256': hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest(),
                  'outcome': outcome, 'failure': failure, 'steps': s.steps, 'pids': pids,
                  'expected_live_counts': counts, 'fixture': 'Missing lighting response injected only on the selected emulator',
                  'adb_reverse_restored': True}
        (s.output_dir / 'spec-ui-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print('Evidence saved: ' + str(s.output_dir), flush=True)
    assert outcome == 'PASS', 'Spec UI check did not pass; see dated evidence'


if __name__ == '__main__':
    main()

"""Exercise map coordinate picking, automatic anchor adjustment and route search."""
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
    outcome, failure, observations = 'FAIL', '', []
    sha = hashlib.sha256((ROOT / 'app/build/outputs/apk/debug/app-debug.apk').read_bytes()).hexdigest()
    installed = s.shell('pm', 'path', PACKAGE).strip().removeprefix('package:')
    assert s.shell('sha256sum', installed).split()[0] == sha
    try:
        s.command('reverse', 'tcp:8765', 'tcp:8767')
        s.shell('am', 'force-stop', PACKAGE)
        s.shell('am', 'start', '-n', PACKAGE + '/.MainActivity')
        s.expect('지도 준비 완료', id='map_status')
        s.click(id='minimize_top_card')
        box = s.bounds(s.find(id='controls_scroll'))
        x = (box[0] + box[2]) // 2
        s.shell('input', 'swipe', x, box[1] + 25, x, box[3] - 80, 500)
        s.wait(lambda: s.find(id='sheet_restore_area') is not None, 'Lower sheet did not hide')
        for mode, role in [('tmap', '출발지'), ('local', '도착지')]:
            if mode == 'local':
                s.click(id='preview')
                s.click(id='minimize_top_card')
                # Search restores the summary; hide it again to expose more map.
                s.dump()
                lower = s.find(id='controls_scroll')
                if lower is not None:
                    b = s.bounds(lower)
                    s.shell('input', 'swipe', x, b[1] + 25, x, b[3] - 80, 500)
                    s.wait(lambda: s.find(id='sheet_restore_area') is not None, 'Local sheet did not hide')
            s.dump()
            frame = s.bounds(s.find(id='map_container'))
            px = int(frame[0] + (frame[2] - frame[0]) * (0.3 if mode == 'tmap' else 0.65))
            py = int(frame[1] + (frame[3] - frame[1]) * 0.48)
            s.shell('input', 'swipe', px, py, px, py, 1100)
            s.expect('지도에서 선택한 위치')
            s.screenshot(mode + '-menu.png')
            s.dump()
            choice = s.find(text=role + '로 설정')
            assert choice is not None, 'Map endpoint menu disappeared before selection'
            s.tap_node(choice)
            print(mode + ': endpoint selected', flush=True)
            s.wait(lambda: s.find(text=role + ' 보행 지점 확인') is not None or
                   s.find(id='expand_top_card') is not None, 'Automatic route search did not finish')
            assert s.find(text=role + ' 보행 지점 확인') is None, 'Unwanted snap confirmation dialog'
            s.click(id='expand_top_card')
            s.expect('서버 검색 완료', id='map_status')
            label = s.find(id='origin_input' if mode == 'tmap' else 'destination_input').get('text')
            assert role in label and '보정' in label
            s.screenshot(mode + '-route.png')
            observations.append({'mode': mode, 'role': role, 'label': label, 'confirmation': False})
            s.passed(mode + ': long press, automatic snap and search without confirmation')
        s.wait(lambda: s.find(id='origin_input') is not None, 'Inputs not restored')
        assert '지도 출발지' in s.find(id='origin_input').get('text')
        assert '지도 도착지' in s.find(id='destination_input').get('text')
        s.screenshot('selected-inputs.png')
        outcome = 'PASS'
    except Exception as error:
        failure = str(error)
        s.screenshot('failure.png')
    finally:
        (s.output_dir / 'map-long-press-result.json').write_text(json.dumps(dict(
            date=time.strftime('%Y-%m-%d'), apk_sha256=sha, outcome=outcome,
            failure=failure, observations=observations), ensure_ascii=False, indent=2), encoding='utf-8')
        print(outcome, failure, 'Evidence:', s.output_dir, flush=True)
    assert outcome == 'PASS', failure


if __name__ == '__main__':
    main()

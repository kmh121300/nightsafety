"""Verify fixed MVP app text under system font changes; restore the setting afterward."""
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
from integration_smoke import Smoke


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serial', default='emulator-5554')
    args = parser.parse_args()
    date = datetime.now().strftime('%Y-%m-%d')
    smoke = Smoke(str(Path.home() / 'AppData/Local/Android/Sdk/platform-tools/adb.exe'), args.serial)
    smoke.output_dir = Path(__file__).resolve().parents[1] / 'verification' / ('font-lock-' + datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    smoke.output_dir.mkdir()
    print('Evidence: ' + str(smoke.output_dir), flush=True)
    original = smoke.shell('settings', 'get', 'system', 'font_scale').strip()
    checks = []

    def text_heights():
        smoke.wait(lambda: smoke.find(text='밤길 지킴이') is not None, 'App title absent')
        title = smoke.bounds(smoke.find(text='밤길 지킴이'))
        subtitle = smoke.bounds(smoke.find(text='보행 경로 비교'))
        return {'title': title[3] - title[1], 'subtitle': subtitle[3] - subtitle[1]}

    try:
        smoke.shell('settings', 'put', 'system', 'font_scale', '1.0')
        smoke.shell('am', 'force-stop', 'kr.ac.tukorea.nightsafety')
        smoke.shell('am', 'start', '-n', 'kr.ac.tukorea.nightsafety/.MainActivity')
        smoke.expect('시설 기록 1381개', id='route_summary')
        baseline = text_heights()
        for scale in ('1.3', '2.0', '0.85'):
            smoke.shell('settings', 'put', 'system', 'font_scale', scale)
            actual = text_heights()
            assert actual == baseline, f'App text changed at system scale {scale}: {baseline} -> {actual}'
            checks.append({'system_scale': scale, 'pixel_heights': actual})
            print('PASS: fixed app text at system scale ' + scale, flush=True)
        smoke.click(id='data_info')
        smoke.expect('자료 정보')
        message = smoke.bounds(smoke.find(id='android:id/message'))
        smoke.shell('settings', 'put', 'system', 'font_scale', '2.0')
        smoke.expect('자료 정보')
        assert smoke.bounds(smoke.find(id='android:id/message')) == message, 'Open dialog resized or recreated'
        smoke.screenshot('fixed-dialog-system-scale-2.png')
        smoke.click(text='닫기')
        smoke.visible('origin_input')
        assert smoke.find(id='origin_input').get('content-desc', '').startswith('출발지 ')
        assert smoke.find(id='destination_input').get('content-desc', '').startswith('도착지 ')
        smoke.screenshot('fixed-app-system-scale-2.png')
        print('PASS: open dialog retained and endpoint descriptions preserved', flush=True)
        smoke.shell('am', 'force-stop', 'kr.ac.tukorea.nightsafety')
        smoke.shell('am', 'start', '-n', 'kr.ac.tukorea.nightsafety/.MainActivity')
        assert text_heights() == baseline, 'App text changed on cold start with large system font'
        smoke.screenshot('fixed-cold-start-system-scale-2.png')
        print('PASS: fixed app text on cold start at system scale 2.0', flush=True)
    except Exception as error:
        try:
            smoke.screenshot('failure.png')
        finally:
            (smoke.output_dir / 'failure.txt').write_text('작성일: ' + date + ' · 최종 수정일: ' + date + '\n\n' + str(error), encoding='utf-8')
        raise
    finally:
        if original == 'null':
            smoke.shell('settings', 'delete', 'system', 'font_scale')
        else:
            smoke.shell('settings', 'put', 'system', 'font_scale', original)
        assert smoke.shell('settings', 'get', 'system', 'font_scale').strip() == original, 'System font scale not restored'

    apk = Path(__file__).resolve().parents[1] / 'app/build/outputs/apk/debug/app-debug.apk'
    result = {'작성일': date, '최종 수정일': date, 'verified_at': datetime.now().isoformat(),
              'apk_sha256': hashlib.sha256(apk.read_bytes()).hexdigest(), 'baseline': baseline,
              'checks': checks, 'dialog_retained': True, 'cold_start_fixed': True,
              'descriptions_preserved': True, 'system_font_restored': True}
    (smoke.output_dir / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print('PASS: font checks complete; original system font scale restored', flush=True)


if __name__ == '__main__':
    main()

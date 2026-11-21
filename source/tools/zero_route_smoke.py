"""Replace three numeric route metrics with same-anchor zero-distance values."""
from pathlib import Path
import argparse
from integration_smoke import Smoke


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial', default='emulator-5554')
    args = parser.parse_args()
    adb = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
    smoke = Smoke(adb, args.serial)
    smoke.command("reverse", "tcp:8765", "tcp:8765")
    smoke.shell("am", "force-stop", "kr.ac.tukorea.nightsafety")
    smoke.shell("am", "start", "-n", "kr.ac.tukorea.nightsafety/.MainActivity")
    smoke.expect("지도 준비 완료", id="map_status")
    smoke.search()
    for control in ('score_value', 'average_value', 'weak_value'):
        assert 0 <= float(smoke.visible(control).get('text', '')) <= 100, 'Normal route score absent'
    print("PASS: normal route has three numeric scores before zero-route regression", flush=True)
    for control in ("origin_input", "destination_input"):
        smoke.click(id=control)
        smoke.enter("anchor", id="place_query")
        smoke.click(id="place_lookup")
        smoke.click(text="대학 옆문 보행 지점 (현장 미검증)")
    smoke.search()
    smoke.expect("동일 보행 지점 · 이동거리 0", id="warning")
    smoke.expect("0m · 약 0.0분", id="route_summary")
    smoke.expect("이동 없는 경로 · 시설지표 미산출", id="warning")
    for control in ('score_value', 'average_value', 'weak_value'):
        smoke.expect('—', id=control)
    smoke.screenshot("integration-zero-route.png")
    print("PASS: same anchor returns zero distance/time without a drawable route or app crash", flush=True)
    print("Evidence saved: " + str(smoke.output_dir), flush=True)


if __name__ == "__main__":
    main()

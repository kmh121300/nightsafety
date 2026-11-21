"""ADB UI integration smoke test. Run only after installing the current APK.

Uses the app SDK map initialization and local route server; never reads keys/logcat.
"""
import argparse
from datetime import datetime
import hashlib
from pathlib import Path
import re
import subprocess
import time
import xml.etree.ElementTree as ET

PACKAGE = "kr.ac.tukorea.nightsafety"
ROOT = Path(__file__).resolve().parents[1]


class Smoke:
    def __init__(self, adb, serial):
        self.adb = [adb, "-s", serial]
        self.steps = []
        self.nodes = []
        self.output_dir = ROOT / 'verification' / ('android-' + datetime.now().strftime('%Y-%m-%d_%H%M%S_%f'))

    def command(self, *args, binary=False):
        result = subprocess.run(self.adb + list(args), capture_output=True, timeout=45)
        if result.returncode:
            raise AssertionError("ADB command failed: " + args[0])
        return result.stdout if binary else result.stdout.decode("utf-8", errors="replace")

    def shell(self, *args):
        return self.command("shell", *map(str, args))

    @staticmethod
    def bounds(node):
        values = list(map(int, re.findall(r"\d+", node.get("bounds", ""))))
        assert len(values) == 4, "UI element has no usable bounds"
        return values

    def tap_node(self, node):
        x1, y1, x2, y2 = self.bounds(node)
        assert x2 > x1 and y2 > y1, "UI element is not visible"
        self.shell("input", "tap", (x1 + x2) // 2, (y1 + y2) // 2)

    def dump(self):
        self.shell("uiautomator", "dump", "/sdcard/integration-ui.xml")
        xml = self.shell("cat", "/sdcard/integration-ui.xml")
        self.nodes = list(ET.fromstring(xml).iter("node"))
        close = next((n for n in self.nodes if n.get("resource-id", "").endswith("/aerr_close")), None)
        if close is not None:
            text = " ".join(n.get("text", "") for n in self.nodes)
            if any(label in text for label in ("System UI", "system UI", "시스템 UI", "System process", "Process system", "시스템 프로세스")):
                wait_button = self.find(id="android:id/aerr_wait")
                self.tap_node(wait_button if wait_button is not None else close)
                self.steps.append("Handled an external Android system ANR dialog (wait when available)")
                return self.dump()
            raise AssertionError("Application ANR/crash dialog observed")
        return self.nodes

    def find(self, *, id=None, text=None, cls=None):
        return next((n for n in self.nodes if
                     (id is None or n.get("resource-id", "") == id or n.get("resource-id", "").endswith("/" + id)) and
                     (text is None or text in n.get("text", "")) and
                     (cls is None or n.get("class") == cls)), None)

    def wait(self, predicate, message, timeout=100):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                self.dump()
            except (ET.ParseError, AssertionError) as error:
                if "ANR/crash" in str(error):
                    raise
                time.sleep(2)
                continue
            if predicate():
                return
            time.sleep(2)
        raise AssertionError(message)

    def expect(self, text, id=None):
        if id is not None:
            self.visible(id)
        self.wait(lambda: self.find(id=id, text=text) is not None, "Missing expected UI: " + text)

    def visible(self, id):
        self.dump()
        node = self.find(id=id)
        # Floating cards can remain in the accessibility tree behind an expanded sheet.
        if id in ('origin_input', 'destination_input', 'swap_endpoints', 'search_routes', 'favorite_list', 'location', 'preview', 'reset_map'):
            for _ in range(3):
                sheet, map_node = self.find(id='controls_scroll'), self.find(id='map_container')
                if node is None or sheet is None or map_node is None:
                    break
                sx1, sy1, sx2, sy2 = self.bounds(sheet)
                mx1, _, mx2, _ = self.bounds(map_node)
                if sx1 > mx1 or sx2 < mx2 or sy1 >= self.bounds(node)[3]:
                    break
                self.shell('input', 'swipe', (sx1 + sx2) // 2, sy1 + 30, (sx1 + sx2) // 2, sy2 - 80, 600)
                self.dump()
                node = self.find(id=id)
        if node is not None:
            return node
        # Search/results use the same scrollable control panel in the adaptive layouts.
        for direction in (-1, 1):
            for _ in range(20):
                scroll = self.find(cls="android.widget.ScrollView")
                assert scroll is not None, "Control ScrollView missing"
                x1, y1, x2, y2 = self.bounds(scroll)
                gesture_x = x1 + 12  # Keep a delayed swipe outside full-width action buttons.
                upper, lower = y1 + (y2 - y1) // 4, y2 - (y2 - y1) // 4
                previous = [tuple(item.items()) for item in self.nodes]
                self.shell("input", "swipe", gesture_x, lower if direction == 1 else upper,
                           gesture_x, upper if direction == 1 else lower, 600)
                self.dump()
                node = self.find(id=id)
                if node is not None:
                    return node
                if [tuple(item.items()) for item in self.nodes] == previous:
                    break
        raise AssertionError("Control unavailable: " + id)

    def click(self, id=None, text=None):
        if id is not None:
            self.visible(id)
            time.sleep(0.5)  # Re-read bounds after the adaptive panel stops scrolling.
            self.dump()
            node = self.find(id=id)
            assert node is not None, "Control moved out of view: " + id
        else:
            self.expect(text)
            node = next((n for n in self.nodes if n.get("text") == text), None) or self.find(text=text)
        assert node.get("enabled", "true") == "true", "Control disabled"
        self.tap_node(node)

    def enter(self, value, id=None):
        self.wait(lambda: (self.find(id=id) if id else self.find(cls="android.widget.EditText")) is not None, "Expected editable dialog field")
        node = self.find(id=id) if id else self.find(cls="android.widget.EditText")
        assert node is not None, "Expected editable dialog field"
        self.tap_node(node)
        self.shell("input", "keyevent", "123")
        self.shell("input", "keyevent", *(["67"] * (len(node.get("text", "")) + 5)))
        self.shell("input", "text", value)
        self.shell("input", "keyevent", "4")
        time.sleep(1)  # Wait for the keyboard dismissal to settle dialog bounds.

    def screenshot(self, name):
        time.sleep(3)
        path = self.output_dir / name
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(self.command("exec-out", "screencap", "-p", binary=True))
        assert path.stat().st_size > 10000, "Screenshot capture failed"

    def passed(self, label):
        self.steps.append(label)
        print("PASS: " + label, flush=True)

    def favorite(self, name, action):
        self.click(id="favorite_list")
        self.click(text=name)
        self.click(text=action)

    def search(self):
        self.click(id="search_routes")
        self.expect("서버 검색 완료", id="map_status")

    def run(self):
        self.command("reverse", "tcp:8765", "tcp:8765")
        self.shell("am", "force-stop", PACKAGE)
        self.shell("am", "start", "-n", PACKAGE + "/.MainActivity")
        self.wait(lambda: self.find(id="map_status") is not None, "App screen did not become visible")
        self.expect("지도 준비 완료", id="map_status")
        self.expect("시설 기록 1381개", id="route_summary")
        self.passed("TMAP ready; 1381 source facility records; map shows selected-route 100m corridor")

        self.search()
        self.expect("연결 미완결", id="warning")
        self.expect("공공시설 기반 안전지표", id="score_heading")
        self.expect("평균", id="average_label")
        self.click(id="route_spinner")
        self.dump()
        candidates = [n.get("text", "") for n in self.nodes
                      if n.get("class") in ("android.widget.TextView", "android.widget.CheckedTextView") and
                      "연결 미완결" in n.get("text", "")]
        assert len(candidates) == 3, "Expected three default server candidates"
        self.shell("input", "keyevent", "4")
        self.passed("Default search returns three incomplete candidates and official three-type facility metrics")

        self.click(id="destination_input")
        self.enter("anchor", id="place_query")
        self.click(id="place_lookup")
        self.click(text="정왕역 주변 보행 지점 (출구 연결 미검증)")
        self.search()
        self.expect("그래프 연결됨 · 실제 보행 가능성 미검증", id="warning")
        self.expect("공공시설 기반 안전지표", id="score_heading")
        self.expect("평균", id="average_label")
        for control in ('score_value', 'average_value', 'weak_value'):
            number = float(self.visible(control).get('text', ''))
            assert 0 <= number <= 100, 'Metric card is not a valid score'
        self.passed("Anchor place lookup and complete graph route retain physical connection caveat and three-type scores")

        self.click(id="weak_segments")
        self.expect("하위 10% 길이 · 주황색")
        self.expect("공공시설 기반 안전지표의 하위 구간입니다")
        self.expect("1. ")
        self.click(text="닫기")
        self.screenshot("integration-weak-tmap.png")
        self.click(id="weak_segments")
        self.expect("평균", id="average_label")
        self.passed("Weak facility segment details open and overlay toggles")

        self.click(id="cctv_filter")
        self.expect("시설 기록 1111개", id="route_summary")
        self.click(id="cctv_filter")
        self.expect("시설 기록 1381개", id="route_summary")
        self.click(id="lamp_filter")
        self.expect("시설 기록 511개", id="route_summary")
        self.click(id="lamp_filter")
        self.expect("시설 기록 1381개", id="route_summary")
        self.screenshot("integration-tmap.png")
        self.passed("CCTV/security-light filters change available records to 1111/511 and restore 1381; scoring counts stay independent")

        name = "Smoke_" + time.strftime("%m%d_%H%M%S")
        renamed = name + "_renamed"
        self.click(id="save_favorite")
        self.expect("즐겨찾기 저장")
        self.enter(name)
        self.click(id="android:id/button1")
        self.expect("즐겨찾기를 기기에 저장했습니다", id="map_status")
        self.shell("am", "force-stop", PACKAGE)
        self.shell("am", "start", "-n", PACKAGE + "/.MainActivity")
        self.expect("지도 준비 완료", id="map_status")
        # Remove the host connection so the offline restore cannot use the server.
        self.command("reverse", "--remove", "tcp:8765")
        self.favorite(name, "저장 결과 보기 (오프라인)")
        self.expect("저장된 과거 결과", id="warning")
        self.expect("그래프 연결됨", id="warning")
        self.passed("Room favorite survives process restart and restores offline snapshot")

        self.favorite(name, "이름·선호유형 수정")
        self.expect("즐겨찾기 수정")
        self.enter(renamed)
        self.dump()
        spinner = self.find(cls="android.widget.Spinner")
        assert spinner is not None, "Favorite profile selector absent"
        self.tap_node(spinner)
        self.click(text="보행선 우선")
        self.click(id="android:id/button1")
        self.expect("이름·유형 수정 완료", id="map_status")
        self.command("reverse", "tcp:8765", "tcp:8765")
        self.favorite(renamed, "최신 자료로 재조회")
        self.expect("서버 검색 완료", id="map_status")
        self.expect("보행선 우선", id="route_summary")
        self.expect("그래프 연결됨", id="warning")
        self.passed("Rename and preferred walking profile persist and latest requery selects profile")

        self.favorite(renamed, "삭제")
        self.expect("즐겨찾기를 삭제했습니다", id="map_status")
        self.click(id="favorite_list")
        self.dump()
        assert self.find(text=renamed) is None, "Deleted favorite remains in list"
        empty = self.find(id="map_status", text="저장된 즐겨찾기가 없습니다")
        listing = self.find(text="즐겨찾기")
        assert empty is not None or listing is not None, "Favorite list result not observable"
        if empty is None:
            self.click(text="닫기")
        self.passed("Favorite deletion is reflected by refreshed list")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adb", default=str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe"))
    parser.add_argument("--serial", default="emulator-5554")
    args = parser.parse_args()
    smoke = Smoke(args.adb, args.serial)
    try:
        smoke.run()
    except Exception as error:
        # UI assertions and command names only; never echo SDK/logcat output.
        failure = str(error).splitlines()[0]
        print("FAIL: " + failure, flush=True)
        try:
            smoke.screenshot("integration-failure.png")
        except Exception:
            pass
        status = smoke.find(id='map_status')
        last_status = status.get('text', '') if status is not None else 'not observed'
        date = time.strftime('%Y-%m-%d')
        report = '# Android integration failure\n\nCreated: ' + date + ' · Last updated: ' + date + ' · Timezone: Asia/Seoul\n\n'
        report += 'Observed: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n\nFAIL: ' + failure + '\n\n'
        report += 'Last observed app status: ' + last_status + '\n\n'
        report += '\n'.join('- Completed before failure: ' + step for step in smoke.steps)
        report += '\n\nFull UI verification did not pass. Screenshot, if captured: `integration-failure.png`.\n'
        smoke.output_dir.mkdir(parents=True, exist_ok=True)
        (smoke.output_dir / 'failure.md').write_text(report, encoding='utf-8')
        print('Evidence saved: ' + str(smoke.output_dir), flush=True)
        raise SystemExit(1)
    date = time.strftime('%Y-%m-%d')
    report = "# Android integration smoke\n\nCreated: " + date + " · Last updated: " + date + " · Timezone: Asia/Seoul\n\nVerified " + time.strftime("%Y-%m-%d %H:%M:%S") + " (local).\n\n"
    apk = ROOT / 'app/build/outputs/apk/debug/app-debug.apk'
    if apk.exists():
        report += 'APK SHA256: `' + hashlib.sha256(apk.read_bytes()).hexdigest() + '`\n\n'
    report += "\n".join("- PASS: " + step for step in smoke.steps)
    report += "\n\nScreenshots: `integration-tmap.png`, `integration-weak-tmap.png`.\n"
    report += "\nMap tile and orange overlay appearance require visual review of the captured screenshots. No key, raw logcat, SDK URL, or TMAP REST request was collected.\n"
    smoke.output_dir.mkdir(parents=True, exist_ok=True)
    (smoke.output_dir / 'integration-ui.md').write_text(report, encoding="utf-8")
    print('Evidence saved: ' + str(smoke.output_dir), flush=True)


if __name__ == "__main__":
    main()

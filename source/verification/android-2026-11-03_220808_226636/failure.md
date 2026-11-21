# Android integration failure

Created: 2026-11-03 · Last updated: 2026-11-03 · Timezone: Asia/Seoul

Observed: 2026-11-03 22:12:07

FAIL: Application ANR/crash dialog observed

Last observed app status: not observed

- Completed before failure: Dismissed an external Android system ANR dialog
- Completed before failure: Dismissed an external Android system ANR dialog
- Completed before failure: TMAP map ready and 1381 facility records including 870 security-light records
- Completed before failure: Default search returns three incomplete candidates and qualified historical metrics
- Completed before failure: Anchor place lookup and complete graph route retain physical/stale-data caveats
- Completed before failure: Weak historical segment details open and overlay toggles

Full UI verification did not pass. Screenshot, if captured: `integration-failure.png`.

## 2026-11-03 진단

작성일: 2026-11-03 · 최종 수정일: 2026-11-03 · 시간 기준: Asia/Seoul

Windows / Pixel_3a Android15 API35, 임시 사용자 이미지·headless SwiftShader·3072MB, emulator-5556에서 검사했다. 실제 DB 서버는 configured=true/verified=true, safenight/startup_snapshot이며 시설 API1,378행을 확인했다. 설치 APK와 로컬 APK의 SHA256은 모두 `57d3fc82978f492e38de66a8938e469a68d81ef4b630f2a5e7ea3f9f7ffedb17`이다.

실행: `.\.venv\Scripts\python.exe -X utf8 tools/integration_smoke.py --serial emulator-5556`, 종료코드1. 앱 자체 ANR 화면을 시각 확인했다. Android 진단 서비스의 해당 앱 ANR 메인 스레드만 추려 확인했으며 원본 로그·SDK 키·URL은 보존하지 않았다. `/data/anr` 직접 읽기와 adbd root는 이 시스템 이미지에서 허용되지 않았다.

- Input dispatching timed out: MotionEvent 대기5003ms.
- 메인 스레드: `TMapMarkerItem.createMarker` → `TMapView.addTMapMarkerItem` → `TmapPilotMap.update:88` → `MainActivity.refresh:172` → `MainActivity.showWeakSegments:195`.
- 취약 구간 토글에도 기존 update가 전체 시설 마커를 삭제·재생성한다. 해당 작업 중 메인 스레드 입력 지연이 발생했다. 필터 검사 진입 때 ANR 창을 감지했으며 실제 멈춘 스택은 취약 구간 토글이다.
- 앞선 외부 System UI ANR2회와 이 앱 자체 ANR은 구분한다. 과거 지도 준비 대기 실패의 원인이 같다고 확정하지 않는다.

`integration-weak-tmap.png`에서 실제 TMAP 타일·로고·시설·경로·주황 취약 구간과 과거 지표/공식점수 미산출/현장 미검증 안내를 시각 확인했다. 전체 필터·Room 후속 검증은 이 실행에서 미완료다.

# Android integration smoke

Created: 2026-11-03 · Last updated: 2026-11-03 · Timezone: Asia/Seoul

Verified 2026-11-03 22:32:35 (local).

APK SHA256: `07115bef4ea8a710aaed9aba6d8e45c7602c3ee047eb5b2ffbf4411b563367fe`

- PASS: TMAP map ready and 1381 facility records including 870 security-light records
- PASS: Default search returns three incomplete candidates and qualified historical metrics
- PASS: Anchor place lookup and complete graph route retain physical/stale-data caveats
- PASS: Weak historical segment details open and overlay toggles
- PASS: CCTV/security-light filters change 1381 to 1111/511 and restore 1381
- PASS: Room favorite survives process restart and restores offline snapshot
- PASS: Rename and preferred walking profile persist and latest requery selects profile
- PASS: Favorite deletion is reflected by refreshed list

Screenshots: `integration-tmap.png`, `integration-weak-tmap.png`.

Map tile and orange overlay appearance require visual review of the captured screenshots. No key, raw logcat, SDK URL, or TMAP REST request was collected.

## 2026-11-03 환경·시각 검토·검증 범위

작성일: 2026-11-03 · 최종 수정일: 2026-11-03 · 시간 기준: Asia/Seoul

실행 시각22:26:20~22:32:35 KST, 명령 `.\.venv\Scripts\python.exe -X utf8 tools/integration_smoke.py --serial emulator-5556`, 종료코드0, 위8개 단계 모두 통과했다. Windows / Python3.10.11 / Pixel_3a Android15 API35 / emulator-5556 / 임시 사용자 이미지·headless SwiftShader·3072MB·no-snapshot 환경이다. 기존 AVD 사용자 자료는 삭제하지 않았다.

서버는 실제 DB에서 시작 시 snapshot을 복원했다. `/health`의 configured=true/verified=true·safenight/startup_snapshot, 시설 API1,378행, graph_version=`osm-bb4586cbb583`·facility_version=`pilot-96aa968e4ab1`을 확인했다. 앱은 고정 asset의 시설1,381기록(서버1,378+OSM 경찰3객체)을 표시한다. 서버/API와 앱 마커의 자동 viewport 동기화를 구현/검증했다는 뜻은 아니다.

수정 APK와 설치 APK 바이트 SHA256 일치 확인. main/debug 소스22개 집계 SHA256은 `660ef8d5975dc58f63da6c6463fb8a9cd92e1b6377714a094e185e96ea884d03`이다. 정렬 상대경로(`/`)·NUL·파일 바이트·NUL 순서, 비밀 설정/생성 BuildConfig 제외. Git 커밋은 미기록(작업 폴더는 Git 저장소 아님).

두 캡처를 직접 시각 검토했다. 실제 TMAP 타일·로고·경로·시설·주황 취약 구간과 과거 지표/공식점수 미산출/실제 보행 미검증 안내를 확인했다. 지도 영역(40,350)-(1040,1040)의 RGB(205,85,15) ON1,969/OFF0픽셀 대조도 통과했다. Android 단위17개·실패0·오류0, lint 오류0/경고44, 새 APK 빌드는 별도 Gradle 실행 종료코드0이었다.

앞선 [앱 ANR](../android-2026-11-03_220808_226636/failure.md)과 [수정본 첫 전체 실행의 ADB 실패](../android-2026-11-03_221824_537215/failure.md)는 당시 결과로 보존한다. 이번 실행은 앱 ANR/외부 System UI ANR 닫기 없이8개 단계를 완료했다. 단일 시험 환경의 기본 통합 시연 검증이며 모든 명세 TC·실기기 GPS/위치 권한·야간 보행/점등·공식 안전점수·성능 목표·운영 배포의 인수는 아니다. 최초 대량 시설 표시/필터 복원은 동기 SDK 작업이므로 실기기 성능은 별도로 확인해야 한다.

관련: [개발 로그](../../../log/log-2026-11-03-r4-ui.md), [로드맵](../../../ROADMAP.md).

# Android integration smoke

Created: 2026-11-05 · Last updated: 2026-11-05 · Timezone: Asia/Seoul

Verified 2026-11-05 22:09:06 (local).

APK SHA256: `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9`

- PASS: TMAP map ready and 1381 facility records including 870 security-light records
- PASS: Default search returns three incomplete candidates and official three-type facility metrics
- PASS: Anchor place lookup and complete graph route retain physical connection caveat and three-type scores
- PASS: Weak facility segment details open and overlay toggles
- PASS: CCTV/security-light filters change 1381 to 1111/511 and restore 1381
- PASS: Room favorite survives process restart and restores offline snapshot
- PASS: Rename and preferred walking profile persist and latest requery selects profile
- PASS: Favorite deletion is reflected by refreshed list

Screenshots: `integration-tmap.png`, `integration-weak-tmap.png`.

Map tile and orange overlay appearance require visual review of the captured screenshots. No key, raw logcat, SDK URL, or TMAP REST request was collected.

## 2026-11-05 환경·캡처 확인

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 검사 완료: 22:09 KST.

- Windows 호스트, Pixel_3a 임시 read-only AVD, API35, emulator-5556. 기존 환경 재사용, 앱 데이터 초기화/재설치 없음.
- 실행 전 로컬/설치 APK SHA256 일치. 서버 health ready, DB configured/verified true, mode startup_snapshot. 요청마다 실시간 DB 조회를 확인한 것은 아니다.
- source 가상환경에서 `tools/integration_smoke.py --serial emulator-5556` 실행, 종료 코드0·8개 PASS. 이번 실행 중 실패·ANR 처리 기록 없음.
- 캡처2장 직접 확인: TMAP 지도 타일·경로선·주황색 하위 구간·시설 점·점수 카드 표시. 전체9.1/평균13.0/취약0.0. 결과 패널은 스크롤 위치에 따라 일부 내용이 화면 밖에 있으며 작은 화면 전체 UI 인수는 별도다.
- 시험용 즐겨찾기 삭제 완료, ADB reverse 복원, 서버/에뮬레이터 유지.
- 앱/서버/DB/검사 도구 코드 변경·새 빌드 없음. 실제 GPS·권한 예외·제조사 UI/성능·현장·최종 사용자 UI 인수는 미검증. API36.1 화면 소실 원인은 미확정이다.

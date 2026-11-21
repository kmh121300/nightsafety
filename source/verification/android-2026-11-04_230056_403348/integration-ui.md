# Android integration smoke

Created: 2026-11-04 · Last updated: 2026-11-04 · Timezone: Asia/Seoul

Verified 2026-11-04 23:09:47 (local).

APK SHA256: `973ebc2d10dff824cbc98bbc6cdf074d7a84d400c47b7a569ad7d1adb6d703fc`

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

## 2026-11-04 시각 검토·환경

작성일: 2026-11-04 · 최종 수정일: 2026-11-04 · 시간 기준: Asia/Seoul

실제 DB startup_snapshot(configured/verified=true), 새3유형 점수 bundle, Pixel_3a Android15 API35/emulator-5556·임시 이미지·headless SwiftShader·3072MB. 전체 스크립트 종료코드0, 위8개 통과. APK 설치 바이트와 로컬 해시 일치 확인.

두 캡처를 직접 검토했다. 공공시설 기반 안전지표9.1/100·평균13.0·취약0.0, 구간 등급 색/범례·주황 취약 구간·시설1,381기록·출처/기준일·TMAP 타일/로고를 확인했다. 시설 작동 미확인/점수 제외 문구는 없다. 주황 RGB(205,85,15)의 지도 영역(40,350)-(1040,1040) ON1,969/OFF0픽셀 대조도 통과했다. 실기기·현장·명세 전체 인수와 구분한다.

DB/API·단위/빌드·별도 시설 상세/0거리 근거는 [통합 검증 기록](../mvp-scoring-2026-11-04/verification.md)을 따른다.

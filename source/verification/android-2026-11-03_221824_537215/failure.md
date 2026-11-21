# Android integration failure

Created: 2026-11-03 · Last updated: 2026-11-03 · Timezone: Asia/Seoul

Observed: 2026-11-03 22:24:44

FAIL: ADB command failed: shell

Last observed app status: 즐겨찾기를 삭제했습니다

- Completed before failure: TMAP map ready and 1381 facility records including 870 security-light records
- Completed before failure: Default search returns three incomplete candidates and qualified historical metrics
- Completed before failure: Anchor place lookup and complete graph route retain physical/stale-data caveats
- Completed before failure: Weak historical segment details open and overlay toggles
- Completed before failure: CCTV/security-light filters change 1381 to 1111/511 and restore 1381
- Completed before failure: Room favorite survives process restart and restores offline snapshot
- Completed before failure: Rename and preferred walking profile persist and latest requery selects profile

Full UI verification did not pass. Screenshot, if captured: `integration-failure.png`.

## 2026-11-03 환경 및 후속 관찰

작성일: 2026-11-03 · 최종 수정일: 2026-11-03 · 시간 기준: Asia/Seoul

Pixel_3a Android15/API35, emulator-5556, 실제 DB configured=true/verified=true·safenight/startup_snapshot·시설1,378행. 수정 APK SHA256 `07115bef4ea8a710aaed9aba6d8e45c7602c3ee047eb5b2ffbf4411b563367fe`, 설치 APK와 로컬 파일 일치 확인.

수정본의 전체 검사에서 취약 구간·CCTV/보안등 필터·Room 재시작/오프라인 복원·수정/최신 재조회까지7개 단계가 통과했다. 마지막 삭제 후 목록 검사에서 ADB shell 명령이 실패했고 실패 캡처도 저장되지 않았다. 직후 `adb devices -l`은 device, 에뮬레이터 프로세스 존재, UI dump/read 종료코드0을 확인했다. 화면 문구는 '즐겨찾기를 삭제했습니다'였다. ADB 실패의 정확한 원인은 미확정이며 앱 전체 통과로 바꾸지 않는다.

후속 검사에서 '목록 전체가 비었다'를 즉시 assertion한 시도는 실패했다. 기존 항목 존재/비동기 목록 갱신을 구분하지 않은 단정이므로 삭제 실패의 증거나 인수 통과로 해석하지 않는다. 이후 원래 전체 스크립트를 재실행한다.

두 캡처를 시각 검토했다. TMAP 타일/로고·경로·시설·과거 지표/공식점수 미산출/현장 미검증 안내 표시를 확인했다. 지도 영역(40,350)-(1040,1040)의 RGB(205,85,15)는 취약 구간 ON1,969픽셀/OFF0픽셀이다. 새 결과는 별도 폴더에 기록하며 이 실패를 덮어쓰지 않는다.

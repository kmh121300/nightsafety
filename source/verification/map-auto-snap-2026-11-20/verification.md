# 지도 선택 시 확인 창 없이 자동 보정·검색

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 시간 기준: Asia/Seoul

사용자 요청으로 `출발지/도착지 보행 지점 확인` 창을 제거했다. 지도 길게 누르기 메뉴에서 방향을 고르면 기존 snap API 성공 후 좌표를 바로 반영하고 기존 search를 호출한다. 입력 이름의 보정 거리, 오류/지역 검증, 최신 revision만 처리하는 post(ticket), 실제 보행 지점 기준 경로 계산은 유지한다. 보정 실패 시 기존 입력을 유지하는 오류 안내는 남긴다. 서버/DB/그래프/점수/SDK 설정 변경 없음.

## 2026-11-20 검증

- 환경: Windows/JDK21.0.11/Gradle9.7.1, API35 Pixel_3a emulator-5556 host GPU, 일반1080×2220/440dpi.
- 대상 APK SHA-256: `0d965d977dfcf5d4ec8207d58c5a2450a976b763139a1ea14937fdaa589af814`. 설치 해시 대조 통과.
- 변경 전 [회귀 실패](../android-2026-11-20_114952_651045/map-long-press-result.json): `Unwanted snap confirmation dialog`.
- 최종 assembleDebug/testDebugUnitTest/lintDebug 종료코드0, BUILD SUCCESSFUL(54초). Android41개 성공/실패0/오류0, lint 오류0·경고50. [실행 기록](../../../log/map-auto-snap-2026-11-20-gradle.txt).
- [DB health](db-health.json): verified=true/startup_snapshot. 기존8767 DB 서버와 기기8765 reverse를 사용했다. 서버 코드는 이번 UI 변경에서 바꾸지 않았다.
- [최종 UI 회귀 PASS](../android-2026-11-20_115543_207274/map-long-press-result.json): TMAP 출발지/로컬 도착지 선택 후 별도 보정 확인 창이 없음, 서버 검색 완료와 보정 거리 이름/입력 반영 확인.
- [TMAP 결과](../android-2026-11-20_115543_207274/tmap-route.png), [로컬 결과](../android-2026-11-20_115543_207274/local-route.png), [선택 입력](../android-2026-11-20_115543_207274/selected-inputs.png) 캡처 검토.
- [중간 미완료 검사](../android-2026-11-20_115151_723957/map-long-press-result.json)는 `Missing expected UI: 출발지로 설정`으로 실패했다. 당시 캡처에는 메뉴와 경로 갱신이 관찰됐지만 선택/읽기 시점의 원인은 미확정이다. 검사 절차에서 메뉴를 다시 덤프해 현재 항목을 한 번 누르고, 숨겨진 하단 패널의 출현 대신 상단 검색 완료/입력값을 확인하도록 조정한 후 PASS. 이 사이 앱 코드는 변경하지 않았다.

작은 화면/실기기/TalkBack·서버 전체 테스트·현장 보행은 이번 UI 단계 삭제에서 반복하지 않았다. 기존 수동 확인/취소 검증은 각각 당시 APK의 과거 결과로 보존한다. 파일럿 밖 미지원, 원래 점→보행 지점 사이 실제 통행 미확인 한계는 동일하다.

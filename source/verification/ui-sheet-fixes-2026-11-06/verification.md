# 지도 UI 겹침/요약/가독성 수정 검증

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

검사 완료: 2026-11-06 23:46 KST. 사용자 승인한3개 UI 문제를 수정했다. 기존 캡처/실패/이전 APK 묶음은 보존한다. [수정 전 검토](../ui-review-2026-11-06/verification.md), [구현/중간 실패 로그](../../../log/log-2026-11-06-ui-sheet-fixes.md).

대상 debug APK SHA256 `259dec689c428456ac244bff7333400533d94eaf80e6e86a6152881e19310fd3`. API35 emulator-5556, Pixel_3a, Intel Arc/host GPU, 기존 별도 read-only 시험 VM. 실제 기기는 사용하지 않았다. 최종 APK 설치/빌드/보관 해시 일치 확인.

## 수정 결과

- h720dp에 남은 이전 map_panel을 제거하고 공통48dp 가로 지도 버튼 행을 접힌 시트 위에 배치했다. 전체화면/고정 pane에서는 탐색/출처 위 여백을 적용한다.
- route_summary의 실제 하단+8dp+탐색 inset으로 접힌 높이를 계산한다. 펼친 시트는 maxHeight로 상태바 아래까지 제한해 손잡이와 시스템 제스처가 겹치지 않게 했다. [Material1.10 구현](https://raw.githubusercontent.com/material-components/material-components-android/1.10.0/lib/java/com/google/android/material/bottomsheet/BottomSheetBehavior.java)의 측정/offset/maxHeight 동작을 확인했다.
- 툴바를 흰 ui_card 배경/10dp padding으로 표시하고 phone 상단 inset을 카드 바깥 margin으로 적용했다. pane은 루트 안전 padding을 유지한다. phone 하단 탐색 영역은 흰 scrim으로 뒤 문구를 가리고, 전체화면에서는 scrim을 숨겨 지도 출처를 보존한다.
- ViewBinding/같은 SDK 지도 view·카메라·경로/필터·서버/DB·Room·점수·세로/글꼴 고정 정책은 유지했다. 변경된 높이/여백만 갱신해 layout 요청을 반복하지 않는다.

| 검사 | 최종 결과 | 근거 |
| --- | --- | --- |
| testDebugUnitTest / lintDebug / assembleDebug | BUILD SUCCESSFUL, 단위27 실패0/오류0, lint 오류0/경고38 | [빌드](build-result.json) |
| 도구 회귀 | 13개 통과 | [작업 로그](../../../log/log-2026-11-06-ui-sheet-fixes.md) |
| small720×1280/density360 | 버튼48dp/헤더·시트 겹침 없음, 요약 표시, 시트 펼침/안전 손잡이·접힘·전체화면/뒤로 통과 | [결과](../android-2026-11-06_234052_220447/map-sheet-result.json) |
| standard1080×2220/density440 | 같은 phone 회귀 통과 | [결과](../android-2026-11-06_234151_952068/map-sheet-result.json) |
| pane1200×1920/density320 | 고정 좌우 배치의 버튼/헤더 겹침·전체화면/뒤로 통과. BottomSheet는 없는 variant | [결과](../android-2026-11-06_234249_602158/map-sheet-result.json) |
| 소스/코드 검토 | 직접 findViewById 없음, 공통 map_panel만 존재, 독립 검토 중요 지적 없음 | [작업 로그](../../../log/log-2026-11-06-ui-sheet-fixes.md) |

표준 [기본 화면](../android-2026-11-06_234151_952068/standard-collapsed.png), 작은 화면 [펼침](../android-2026-11-06_234052_220447/small-expanded.png), 대화면 [고정 패널](../android-2026-11-06_234249_602158/pane-collapsed.png), 표준 [전체화면](../android-2026-11-06_234151_952068/standard-fullscreen.png)을 직접 열어 확인했다. 제목 뒤 지도 글자가 가려지고 버튼 겹침·요약 잘림이 해소됐다. 전체화면의 SDK/OSM 출처 표시도 확인했다. 세 검사 모두 cleanup_errors0이며 원래 화면 크기/밀도를 복원했다.

## 중간 결과 보존

수정 전 버튼 겹침, 삭제된 qualified 리소스 flat이 incremental 빌드에 남아 생긴 첫 바인딩 시작 crash, 작은 화면 상태바를 건드린 drag, topMargin 방식의 접힌 위치 회귀, 최종 APK의 이전 좌표 기반 자동 swipe 실패를 각각 날짜 보고서/캡처/해시로 보존했다. clean 후 오래된 flat이 사라졌고, 상단 제한은 margin 대신 maxHeight로 바꿨다. 최종 동일 APK의 직접 제스처/최신 bounds 기반600ms 자동 검사를 통과했다. 상세 근거는 로그를 따른다. 이전 실패를 성공으로 덮지 않았다.

[최종 설치 묶음](../../delivery/2026-11-06-ui-sheet-fixes/README.md), [실기기 절차](../../DEVICE-TEST.md).

이번 검사는 UI 회귀다. 실제 서버 경로 검색·Room 전체 흐름·위치 권한/GPS·실기기/OEM·다른 OS/임의 창 크기·성능·명세 전체 인수는 반복하지 않았다. 초기 — 점수/시설 수는 검색 전 상태이므로 계산 오류로 판정하지 않는다. 과거 전체 기능 성공은 당시 APK 근거로 보존한다. 사용자의 최종 UI 인수는 별도다.

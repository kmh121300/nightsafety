# 지도 전체화면 검증

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

검사일: 2026-11-06. 사용자 요청으로 기존 `전체 보기`(고정 중심/zoom 초기화) 버튼을 `전체화면`으로 바꾸고 실제 지도 확장 기능을 구현했다. 상단·검색·결과 패널을 숨기고 지도를 앱 가용 영역에 채운다. 지도 조작 버튼·TMAP/OSM 출처·시스템 상태/탐색 막대는 유지한다. `화면 복귀` 또는 시스템 뒤로로 원래 배치로 돌아온다.

ViewBinding과 같은 SDK/Canvas 지도 view를 유지하며 camera reset/recreation을 호출하지 않는다. 검색 결과/선택 경로·필터를 전환 과정에서 변경하지 않는다. fullscreen 여부는 Bundle에 저장한다. Android33+는 [OnBackInvokedDispatcher](https://developer.android.com/reference/android/window/OnBackInvokedDispatcher), 이전 OS는 기존 onBackPressed fallback을 사용한다. 구형 fallback에만 새 제스처 lint 예외/사유를 명시했다.

대상: debug APK SHA256 `eb23f011afd8758722af2eaee31164216dbaa997b89b450771963d88034cc38d`, API35 emulator-5556, 기존 DB snapshot 로컬 서버. 최종 APK 설치/빌드/보관 해시 일치 확인. 서버·DB·Room·점수 정책 변경 없음.

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| 빌드/단위/lint | BUILD SUCCESSFUL, 단위27개 실패0/오류0, lint 오류0/경고41 | [최종 빌드](build-final-result.json) |
| 도구 회귀 | 13개 통과, 새 smoke 문법/직접 findViewById 없음 확인 | [로그](../../../log/log-2026-11-06-map-fullscreen.md) |
| 최종 small | 720×1280 density360, TMAP/로컬 각 진입·패널 숨김·지도 확장·버튼/뒤로 복귀·검색 결과 보존 통과 | [결과](../android-2026-11-06_113543_758678/fullscreen-result.json) |
| 최종 pane | 1200×1920 density320, 동일2개 흐름과 원래 좌우 배치 복원 통과 | [결과](../android-2026-11-06_113724_614363/fullscreen-result.json) |
| 일반 화면 | 동일 DEX/직전 문구 APK6d2f에서 TMAP/로컬2개 흐름 통과 | [당시 결과](../android-2026-11-06_112520_309070/fullscreen-result.json) |
| 코드 검토 | 독립 read-only 검토 중요 지적 없음 | [로그](../../../log/log-2026-11-06-map-fullscreen.md) |

단위27개는 Kotlin 변경 후 실행해 통과했고 마지막 문자열만 변경한 빌드에서는 UP-TO-DATE다. 최종 APK와 직전 문구 APK의 모든 DEX가 동일함을 직접 비교했다. 일반 화면의 전체 흐름을 최종 해시로 반복한 것은 아니며, 최종 해시에서는 small/pane4개 흐름을 검증했다. 기존 전체 UI8개·오류/권한 검사는 각각 당시 APK 근거다.

최종 [작은 화면](../android-2026-11-06_113543_758678/small-tmap-fullscreen.png)과 [대화면](../android-2026-11-06_113724_614363/pane-tmap-fullscreen.png) 캡처를 직접 확인했다. 한 줄 `화면 복귀`가 잘리지 않고 지도·경로·시설·출처가 표시된다. 각 검사 cleanup_errors0, 화면 설정 원래1080×2220/density440 복원. 검색 결과와 복귀 전후 지도 영역이 유지됨을 확인했다.

중간 실패도 보존한다. [기존 APK의 명칭 실패](../android-2026-11-06_111825_079283/fullscreen-result.json), [최종 문구 빠른 tap 진입 미확인](../android-2026-11-06_113236_719693/final-caption-result.json). 후자는 정상 화면 캡처를 남겼고 앱 수정 없이 기존 안정화/좌표 재확인 click helper로 재검사해 통과했다. 중간 두 줄 문구의 작은 버튼 잘림 가능성은 한 줄 `화면 복귀`로 보완했다. 자세한 초기 lint 실패/해시 정정 이력은 로그를 따른다.

[최종 설치 묶음](../../delivery/2026-11-06-fullscreen/README.md), [기기 연결 안내](../../DEVICE-TEST.md).

실기기 GPS·제조사별 UI/성능·사용자 최종 UI·API26~32 구형 뒤로가기 실행·프로세스 재생성 시 전체 상태 복원은 이번에 검증하지 않았다. 기존 API36.1 과거 소실 원인·전체 명세·현장·운영 인수 범위는 미완료 유지한다.

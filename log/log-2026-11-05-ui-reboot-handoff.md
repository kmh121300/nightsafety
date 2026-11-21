# UI 작업 재부팅 전 인계

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 기록 시각: 13:37 KST · 시간 기준: Asia/Seoul

사용자가 컴퓨터 재부팅을 위해 현재 상태 기록과 중단을 요청했다. 추가 수정·빌드를 시작하지 않고 여기서 일시 중단한다. 재부팅 후 이 문서와 [로드맵](../ROADMAP.md)을 먼저 읽고 이어간다. 사용자는 UI 정리를 위임했고 최종 디자인 검사는 모든 작업 뒤 직접 하기로 했다. 중간 디자인 승인을 재요청하지 않는다.

## 현재까지 완료한 작업

- Kotlin/XML UI에 네이비/청록, 검색·지도·경로 비교/시설 영역, 전체·평균·취약 숫자 카드, 가로/600dp 두 열 배치, 자료 정보/읽기 쉬운 시설 상세를 적용했다. 원본 자료·DB·서버·점수 정책·의존성은 변경하지 않았다.
- 경찰시설의 OSM 후보/공식 여부·출입구 미확인 자격을 목록·필터·상세에 보존했다. 사용자가 제외한 시설 작동 여부 안내와 구분한다.
- 실제 ANR의 원인은 필터 복원 시 TMAP 마커 수백 개를 main 스레드에서 동기 추가한 것이었다. `FacilityOverlay.kt`의 `FacilityOverlayQueue`가 실제 반영 상태를 기준으로 프레임당8개 처리하고 새 요청/지도 종료 시 대기를 취소한다. `TmapPilotMap.close()`와 MainActivity의 지도 종료3개 경로를 연결했다. 추가 코드 검토에서 Important/Critical 없음.
- 자동 검사 도구는 스크롤 뒤 좌표 재조회·가장자리 제스처를 사용한다. `zero_route_smoke.py`에는 세 숫자 카드의 `—` 확인과 캡처 경로 출력을 추가했다. 이 수정된 0거리 검사는 아직 실행하지 않았다.

## 검증된 APK와 근거

- APK: `source/app/build/outputs/apk/debug/app-debug.apk`.
- SHA256: `1b4d9a5e19eaa43174bbb8ebc864b44f60c671952ff81d8a9713946ee6a3e6ad`.
- Android25개 실패0, 도구7개 통과. `gradlew.bat testDebugUnitTest lintDebug assembleDebug` 성공, lint 오류0/경고24. 검사 환경 Windows/JDK21/AGP9.4.0/Gradle9.7.1, API35 Pixel_3a/SwiftShader 임시 에뮬레이터.
- 13:21 KST 이 APK의 실제 DB 기반 **기본 UI8개 전체 통과**. 필터1,381→1,111/511→1,381, 검색/구간/Room 저장·재시작·오프라인 복원·이름/유형 수정·최신 재조회·삭제 확인. [전체 결과](../source/verification/android-2026-11-05_130904_166965/integration-ui.md). 설치 APK 해시도 로컬 파일과 일치했다.
- 기존 서버가 DB startup snapshot/bundle `local-mvp-3types-v1`을 정상 로드했다. DB import/전체 API 대조는 이번 UI 작업에서 반복하지 않았다.
- [추가 캡처/검증 기록](../source/verification/ui-polish-2026-11-05/verification.md): 세로 점수, 자료 정보, 보안등 상세, 경찰시설 후보 상세, 가로/태블릿 크기/글꼴1.3 캡처가 있다. 배치 캡처 성공과 상태 보존 성공은 구분해야 한다.

## 미완료 문제와 소스/APK 차이

1. **회전 후 검색 결과 점수가 초기 자료로 돌아가는 문제 미해결.** 단일 회전 재현에서 PID `13979`는 그대로였고 도착지 이름도 보존됐지만 점수는 `9.1 → —`로 바뀌었다. `rotation-state-debug.png`와 가로/태블릿 캡처를 보존했다. 초기 추가 검사에서는 입력도 초기값인 장면이 있었다. 단순 배치 통과로 인정하지 않는다.
2. 우선 확인할 코드: MainActivity의 `loadData()`에서 `lastNonConfigurationInstance`를 비동기 asset 로드 완료 후 읽는 경로, `onRetainNonConfigurationInstance`, `onSaveInstanceState`, RouteWorkflow의 `attach/saveState`. `saveState`는80,000자 이상 snapshot을 Binder에 넣지 않는다. **retained data를 onCreate에서 즉시 잡아 비동기 완료까지 보존하는 방식은 아직 검증하지 않은 수정 가설**이다. 큰 snapshot을 Bundle에 무조건 넣거나 DB/저장 정책을 바꾸지 않는다.
3. **확대 글꼴 상단 잘림:** 1.3배에서 부제목이 잘리고 저장 목록 버튼이 두 줄로 나뉘었다. `view_toolbar.xml`의 헤더 높이를 wrap_content/minHeight48dp, 저장 버튼 폭/높이를 wrap_content/minWidth80dp/minHeight48dp로 수정했다. **이 마지막 XML 변경은 아직 빌드/설치/검증하지 않았다. 현재 APK에는 포함되지 않는다.**
4. 따라서 UI 전체 작업은 완료/사용자 인수 상태가 아니다. 최종 디자인 검사는 사용자 대기, 실기기 GPS/권한·현장·명세 전체 TC·운영 배포도 미완료다.

## 재시작 후 순서

1. 회전 점수 유실을 재현하고 최소 수정한다. 수정 전후에 같은 도착지·선택 경로·세 점수·연결/저장 상태가 유지되는지 확인한다. 빠른 연속 화면 변경도 점검한다.
2. 마지막 헤더 XML을 포함해 Android 단위/lint/APK를 빌드하고 새 해시를 기록한다. 기존25개/7개 및 이전 APK 전체 UI 성공은 과거 근거로 보존한다.
3. `source`에서 `.venv\Scripts\python.exe -X utf8 server/app.py`로 기존 DB snapshot 서버를 실행한다. SDK `platform-tools\adb.exe`, API35 `Pixel_3a`, 포트5556, `-gpu swiftshader -no-window -no-snapshot`을 사용한 임시 데이터 경로는 `%TEMP%\safenight-mvp-20261104`였다. 기본 AVD 데이터를 초기화하지 않는다. emulator는 관리 가능한 exec 세션에서 실행하면 안정적이었다. 부팅 완료1/패키지 서비스 준비를 확인하고 APK 설치 후 검사를 시작한다. 서버/SDK는 환경 권한에 따라 escalation이 필요했다.
4. `.venv\Scripts\python.exe -X utf8 tools/integration_smoke.py --serial emulator-5556`와 `tools/zero_route_smoke.py --serial emulator-5556`를 순서대로 실행한다. ADB 자동화를 동시에 돌리지 않는다. 가로/태블릿/확대 글꼴 캡처는 **같은 검색 결과 보존까지 assertion**을 추가해 재검사한다.
5. 임시 추가 검사 스크립트는 `%TEMP%\safenight_ui_review_20261105.py`, 재현 스크립트는 `%TEMP%\safenight_rotation_debug_20261105.py`다. 앞 스크립트는 배치/상세만 assert하므로 상태 유실을 잡지 못했다. 예전 `%TEMP%\safenight_ui_resources_20261105.py`는 최신 테마/ID를 덮어쓰므로 다시 실행하지 않는다.
6. [UI 로그](log-2026-11-05-ui-polish.md), [계획](../source/docs/superpowers/plans/2026-11-05-ui-polish.md), 검증 보고서·README·로드맵의 날짜/링크/검사 결과를 함께 마무리한다. 서버와 이번 임시 에뮬레이터만 종료하고 자료·과거 실패 캡처를 보존한다.

비밀번호/DB 연결 문자열/SDK 키는 이 문서에 포함하지 않았다.

## 재부팅 후 후속 결정 — 2026-11-05

사용자가 일반 회전을 막는 MVP 방식을 선택했다. 회전 점수 복원은 우선 작업에서 제외하고 MainActivity 세로 고정/API36 대화면 호환 설정을 적용했다. 헤더 후속 XML도 새 APK에 반영·검증했다. 이 인계의13:37 시점 순서를 그대로 실행하지 말고 [후속 세로 고정 기록](log-2026-11-05-portrait-lock.md)과 현재 로드맵을 우선한다. 창 크기/글꼴 변경 시 상태 복원과 추가0거리·최종 사용자 UI·실기기 인수는 남아 있다.

같은 날 추가로 사용자가 앱 글꼴 배율 고정을 선택했다. 배율1.0 및 fontScale 변경 직접 처리를 적용하고 시스템0.85/1.3/2.0·열린 창·큰 글꼴 새 시작을 확인했다. 최신 시작점은 [글꼴 고정 기록](log-2026-11-05-font-lock.md)이다. 일반 창 크기/프로세스 재생성 복원은 계속 미완료다.

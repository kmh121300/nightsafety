# 오류·복구 및 위치 권한 모의 검증

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 검증일: 2026-11-05 · 시간 기준: Asia/Seoul

22:43 KST 결과 정리. Windows/JDK21, API35 Pixel_3a 임시 read-only emulator-5556, DB startup_snapshot 로컬 서버. 수정 APK SHA256 `f1d1a7c84d926be070ceb1b0447de95c8dfbf261d23ed1b479ed58324aa673ef`, 설치 해시 일치.

## 결과

동일 수정 APK에서 아래8개 항목 통과. 앞7개는 [전체 시도 JSON](../android-2026-11-05_223346_459677/error-recovery-result.json), 마지막1개는 [한정 재검사 JSON](../android-2026-11-05_224138_022854/error-recovery-result.json)이다. 전체 시도는 마지막 OS 안내창 때문에 FAIL로 보존하며8개가 한 실행에서 모두 통과했다고 표기하지 않는다.

- PASS: Blank/no-result place search and out-of-area coordinates keep the original endpoint
- PASS: Two endpoint swaps restore labels and stale input cannot be saved as latest
- PASS: Disconnected search reports failure and keeps old scores; stale save blocked; reconnect succeeds
- PASS: Force-stop/relaunch uses default unsaved inputs; no latest server result is claimed at startup
- PASS: OS location denial keeps manual endpoints and server route search usable
- PASS: Coarse-only permission with no mock fix times out and preserves manual origin
- PASS: Injected in-area precise location updates origin and allows route search
- PASS: Location disabled gives failure feedback without clearing origin or blocking manual search

[빌드 기록](../android-2026-11-05_223346_459677/build-result.json): Android 단위25개 실패0/오류0, lint 오류0/경고27, APK 빌드 성공. 도구11개는 안내창 처리 추가 후 다시 실행해 통과했다. 추가 lint 경고1개는 비트맵 생성의 UseKtx 권장이다.

## 수정과 근거

- 첫 위치 수신 시 SDK setIconVisibility가 미생성 tracking marker를 참조해 실제 crash. [수정 전 stack](../android-2026-11-05_222019_313588/location-crash-sanitized.txt) 보존. 일회성 위치를 기존 TMapMarkerItem으로 표시·변경 시 재중심하도록 수정했다. 지속 추적을 켜지 않는다.
- 검색0건 후 '찾는 중' 상태 잔류는 [수정 전 assert 실패](../android-2026-11-05_223025_607460/no-results-status-red.json) 후 완료 문구로 수정했다. [새 캡처](../android-2026-11-05_223346_459677/no-result-search.png)에서 상단/입력창의 검색 결과 없음 안내를 확인했다.
- [최초 도구 실패](../android-2026-11-05_221538_586047/failure.md)는 Android EditText 오류 popup의 XML 누락, appops 기본값 표기·빈 오류 처리 문제다. 도구를 수정하고 당시 캡처를 보존했다.
- 새 APK 마지막 시도는 Android의 No location access 안내창이 버튼을 가려 실패했다. [실패 캡처](../android-2026-11-05_223346_459677/failure.png)를 보존하고 Close 처리 후 마지막 항목만 재검사했다. 위치 OFF 유지 assert와 기존 입력 유지·재검색 통과를 확인했다.

## 캡처·설정 복원

빈/무결과 검색·범위 밖 좌표의 오류 안내를 직접 캡처 확인했다. [모의 위치](../android-2026-11-05_223346_459677/mock-location.png)에서 흰 테두리의 파란 위치 점·현재 위치 출발지·재중심을 확인했다. [위치 OFF](../android-2026-11-05_224138_022854/location-disabled.png)에서 수신 실패 안내·기존 출발지 유지를 확인했다.

두 권한 denied와 원래 USER_SET 등 flags, 시스템 위치 ON, shell mock effective default, ADB reverse를 복원했다. 마지막 두 실행 모두 cleanup_errors는 비어 있다. 모의 provider는 제거했고 서버/에뮬레이터는 유지한다.

## 범위와 한계

실기기 연결 전2번의 지정 검사 범위 완료이며 전체 명세 TC 인수는 아니다. 대략 권한만 허용한 무수신/시간 초과는 확인했지만 OS가 흐리게 만든 실제 대략 좌표의 정확도는 검증하지 않았다. 주입한 위치는 실제 GPS가 아니다. 앱 강제 종료 후 미저장 입력은 기본값으로 돌아간다. 명시 저장의 재시작/오프라인 복원은 이전1번 근거다.

1번 전체 UI8개/0거리/글꼴 검사는 당시 APK로 보존하며 이 수정 APK에 전체8개를 다시 실행했다고 주장하지 않는다. 이번에는 영향 있는 오류·검색·위치 표시를 재검사했다. 실제 GPS·제조사별 동작·API36.1 별도 화면 소실 원인·일반 창 크기/미저장 상태 복원·현장·사용자 최종 UI 인수는 남는다. API36.1 현상이 이번 SDK crash와 동일하다고 단정하지 않는다.

[작업 로그](../../../log/log-2026-11-05-error-recovery.md), [로드맵](../../../ROADMAP.md).

마감 재확인: [최종 상태](final-state.json)에서 앱 지도 준비·서버 ready/DB verified·설치 APK 해시·권한/위치/mock 기본값/reverse 복원을 확인했다. 신규 문서 링크와 날짜/UTF-8 검사 통과. 기존 ROADMAP 발표 문서 링크2개 누락은 이번 범위 밖으로 보존했다.

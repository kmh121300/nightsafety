# 연결 환경 기동 및 최신 APK 0거리 검사

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자가 서버·에뮬레이터를 연결하고 남아 있는0거리 검사를 진행하도록 요청했다. 작업 시작20:32 KST에는8765 listener와 ADB 연결이 없었다. 기존 source 환경에서 서버를 실행하고 Medium_Phone_API_36.1을 emulator-5558/-no-window/-no-snapshot/-gpu swiftshader/-memory3072/-read-only로 기동했다. 기존 AVD를 초기화하지 않는다.

**최종 결과21:12 KST:** 같은 APK를 API35 환경에서 정상 숫자 점수→0거리0m/0분·세 점수 `—` 초기화까지 검사해 통과했다. 지도에서 이전 경로선 제거를 직접 확인했다. 아래의 진행/실패 절은 중간 기록이며 최종 통과와 구분해 보존한다. 서버와5556은 연결된 상태로 유지한다.

## 연결과 대상

- 서버:127.0.0.1:8765, health ready. 기존 DB startup_snapshot의 configured/verified true 확인. bundle `local-mvp-3types-v1`, graph `osm-bb4586cbb583`, facility `pilot-15b18eb4d217`, scoring `mvp-3types-20-5-k2050100-q05-equal-v1`, routing `dijkstra-3types-risk-v1`. 새 import/DB 변경 없음.
- 에뮬레이터: API36(system image36.1), adb 부팅 완료1·package 서비스 준비 확인. 기본 경로의 AVD config 조회는 실패했으나 CLI가 해당 AVD를 찾아 기동했고 실제 API를 ADB로 확인했다.
- 새 빌드 없이 최신 고정 글꼴 APK를 설치했다. SHA256 `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9`이며 설치 파일도 sha256sum으로 일치 확인했다. adb reverse tcp:8765 연결 확인.

## 준비 실패와 검사 도구 보완

설치 명령이 아직 실행 중인데 패키지 조회/앱 실행 검사를 먼저 시작해 패키지 미발견으로 실패했다. 설치 성공을 확인한 뒤 종속 단계들을 다시 순서대로 실행했다. 이 준비 실패를 앱 동작 검사 성공으로 취급하지 않는다.

첫 정식 시작에서 검사 도구는 Application ANR이라고 보고했지만 [실제 캡처](../source/verification/zero-route-2026-11-05-startup/startup-failure.png)는 **Process system isn't responding** 창이었다. 앱 대상 ANR 진단 출력은 없었고 Android 시스템 창으로 분류했다. helper가 이 영문 어순을 인식하지 못한 회귀를 먼저 실패로 확인했다. 해당 문구를 whitelist에 추가하고 대기 버튼이 있으면 Close 대신 Wait를 선택하도록 수정했다. 우리 앱의 ANR은 계속 실패하도록 보호하는 검사도 추가했다. 도구9개 모두 통과. 앱/서버 코드는 변경하지 않아 APK를 다시 빌드하지 않았다.

## 0거리 검사 진행

기존 `tools/zero_route_smoke.py`에 정상 경로 검색과 전체/평균/취약의 숫자 점수 확인을 먼저 추가했다. 따라서 이어지는0거리 검사에서 이전 숫자가 `—`로 실제 초기화되는지도 확인할 수 있다. 정상 경로의 세 숫자 점수 단계는 통과했으며 동일 보행 지점 선택/0거리 최종 검사를 진행 중이다.

초기 환경 기동과 시스템 창 처리로 처음 예상한10분을 넘겼다. 최종 결과 전에는0거리 검사 완료로 표시하지 않는다. 실기기/전체 명세/최신 Room 전체 UI·최종 사용자 UI 인수와는 별도다.

관련: [로드맵](../ROADMAP.md), [이전 연결 상태](log-2026-11-05-connection-check.md), [APK 글꼴 검증](../source/verification/font-lock-2026-11-05_162308/verification.md).

## API36.1 입력 실패와 대체 환경

정상 경로의 세 숫자 지표는 확인했으나 place_query 대기100초 후 입력창 미발견으로 중단됐다. [캡처/후속 조사](../source/verification/zero-route-2026-11-05-input/failure.md)에서 앱 PID가 없고 NexusLauncher가 앞에 있었으며, 앱 Java crash/종료 이력으로 원인을 특정하지 못했다. 이 실행을0거리 UI 성공으로 기록하지 않는다. 이번에 띄운5558만 종료하고, 기존 API35 Pixel_3a/%TEMP% safenight-mvp-20261104 데이터 기반의5556을 read-only로 기동해 재검사를 진행한다.

대체 환경 부팅 중 [실제 DB snapshot 기반 API 검사](../source/verification/zero-route-api-2026-11-05/verification.md)는 통과했다. 같은 anchor 요청에 후보1개/already_at_destination/0m/0초/세 점수null/geometry·구간·간선 없음 확인. 앱 UI 결과와 구분한다.

## API35 최종 통과

API35 첫 시작에서도 [Pixel Launcher 응답 지연 창](../source/verification/zero-route-2026-11-05-api35-startup/failure.md)이 검사를 막았다. 해당 시스템 창의 이름을 확인한 후 Wait만 선택했고 앱 ANR을 무시하도록 범위를 넓히지 않았다. 이번 read-only 에뮬레이터에만 stayon을 켰다. 재검사의 `tools/zero_route_smoke.py --serial emulator-5556`은 종료0으로 통과했다.

21:12 KST [최신 APK UI 결과](../source/verification/android-2026-11-05_210638_044884/verification.md)에서 정상 경로의 세 숫자 지표를 먼저 확인한 뒤 같은 대학 옆문 anchor 양쪽 입력, 0m/0분, 이동 없는 경로/지표 미산출, 세 점수 `—`를 확인했다. 거리/세 점수를 한 화면에 추가 캡처했고 지도에 이전 경로선이 남지 않은 것을 직접 확인했다. 결과 JSON의 APK 해시는 위 설치 해시와 동일하다.

마지막 health ready/DB startup snapshot verified true·ADB device/reverse를 재확인했다. 서버70631 세션과 이번 API35 에뮬레이터29808 세션은 연결 상태로 유지하며, 먼저 시도한 API36.1/5558은 종료했다. 프로세스 ID/세션 값은 이번 실행 참고값이며 재부팅 뒤 재사용하지 않는다. API36.1 앱 화면 소실 원인은 미확정으로 남기고, 실기기/최신 Room 전체·최종 사용자 UI 인수 완료로 확대하지 않는다.

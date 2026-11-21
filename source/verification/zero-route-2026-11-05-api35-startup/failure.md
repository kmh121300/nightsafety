# API35 초기 Pixel Launcher 창

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

대체 API35 환경에서 첫 앱 시작 검사도 helper의 Application ANR/crash 문구로 중단됐다. [실제 캡처](startup-failure.png)는 앱이 아닌 Pixel Launcher isn't responding 창이며 뒤의 앱은 지도 준비 완료 상태였다. 이 첫 실행은0거리 UI 통과가 아니다.

Pixel Launcher 문구를 직접 확인한 뒤 해당 Android 창의 aerr_wait만 선택했다. 다른 앱 오류를 무차별로 무시하도록 helper 범위를 넓히지 않았다. 이번 read-only 임시 에뮬레이터에는 stayon을 켜서 검사 중 화면 꺼짐을 막았다. 이후 동일 APK로 UI 검사를 처음부터 다시 수행했다.

재검사에서는 정상 숫자 점수→같은 anchor의0m/0분/세 점수 `—` 초기화가 [통과](../android-2026-11-05_210638_044884/verification.md)했다. [전체 로그](../../../log/log-2026-11-05-zero-route.md).

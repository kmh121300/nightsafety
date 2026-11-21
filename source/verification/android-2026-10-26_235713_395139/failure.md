# 호스트 GPU 환경의 Android UI 검사 실패

작성일: 2026-10-27 · 최종 수정일: 2026-10-27 · 실행 시작: 2026-10-26 23:57 KST · 결과 확인: 2026-10-27

현재 소스의 새 APK(단위14개 통과, lint 오류0/경고49)를 Pixel_3a/API35의 WHPX·Intel 호스트 GPU 환경에 설치했다. DB 서버 health는 safenight/startup_snapshot ready였다.

실제 UI 도구 결과: `FAIL: Missing expected UI: TMAP 지도 · 파일럿 실데이터`. 검색·즐겨찾기 단계에 진입하지 못했다.

- [실패 화면](integration-failure.png): 검은 화면.
- [Android 홈 화면 비교](android-home-black.png): 앱을 벗어나 홈 키를 누른 후에도 검은 화면.
- 전원 진단: Awake, IsPowered=true, StayOn=true, sys.boot_completed=1. 앱 프로세스 존재.

따라서 이번 상태 대기 실패를 TMAP/앱 기능 결함으로 단정하지 않는다. 이 호스트 GPU 실행은 Android 홈 화면 렌더링부터 정상임을 확인하지 못한 환경이다. 하드웨어 가속 또는 GPU의 정확한 내부 실패 원인까지 확정한 것은 아니다. 과거 소프트웨어 렌더링 검사도 전부 같은 원인이라고 주장하지 않는다.

화면 유지 설정을 원래 값으로 복원하고 이 에뮬레이터를 종료했다. 기존 AVD 사용자 자료는 삭제하지 않았다. 이후 검사는 별도의 TEMP 사용자 데이터 이미지와 소프트웨어 렌더링으로 시작한다. 전체 후속 결과: [R4 검증 기록](../android-r4-2026-10-26.md).

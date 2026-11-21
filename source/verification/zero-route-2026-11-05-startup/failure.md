# 0거리 검사 전 시스템 창 오분류

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

20:40 KST 초기 앱 시작 검사에서 helper가 Application ANR/crash dialog observed로 중단됐다. [캡처](startup-failure.png)의 실제 창은 앱 이름이 아닌 `Process system isn't responding`이다. 뒤의 앱은 지도 준비 완료 상태였다. 이 시점의 검사는 통과하지 않았다.

도구는 System process 어순은 알았지만 Process system을 인식하지 못했다. 이 오분류를 단위 검사 실패로 확인한 뒤, 해당 영문 문구와 Wait 우선 처리를 반영했다. 앱 자체의 ANR을 자동 무시하지 않는 보호 검사도 추가했다. 전체 도구9개 통과 후 UI 검사를 다시 시작했다.

별도의 사전 준비 단계에서 APK 설치 완료 전 실행/패키지 조회가 실패한 일도 있었으며 설치 성공 확인 후 해결했다. 앱/서버 소스나 DB는 변경하지 않았다. [작업 로그](../../../log/log-2026-11-05-zero-route.md).

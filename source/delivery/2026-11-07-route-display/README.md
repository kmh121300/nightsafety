# 경로 표시 개선 설치 묶음

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

[설치 APK](night-safety-route-display-debug.apk) · [SHA256](SHA256SUMS.txt) · [대상 정보](manifest.json).

SHA256: `05fb61fac4d40eeb0a6bc25f20a88cb2a558dc8af994b7896a08b892cb35549f`.

Android8.0(API26) 이상용 debug APK. 선택 경로에 흰 테두리와 파란 선, 나머지 후보에 옅은 회색, 출발/도착 핀을 적용했다. 지도와 시설 목록은 선택 경로100m 주변으로 제한하고 보유 기록 수와 표시 수를 구분한다. 점수/원본 좌표/서버/DB/Room 정책은 유지한다.

2026-11-07 빌드·단위31·도구14·서버 연동 UI8개·화면3프로필 통과. lint 오류0/경고39. [검증과 캡처](../../verification/route-display-2026-11-07/verification.md), [실기기 연결 절차](../../DEVICE-TEST.md).

install -r로 기존 즐겨찾기를 유지한다. 검색에는 PC 서버, 지도에는 인터넷이 필요하다. 실제 도로 정합성·실기기/GPS·사용자 최종 UI·전체 명세/운영 인수는 미완료다. 이전 APK/실패 기록은 보존한다.

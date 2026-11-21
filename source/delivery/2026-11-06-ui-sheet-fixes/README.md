# 지도 UI 수정 설치 묶음

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

[설치 APK](night-safety-ui-sheet-debug.apk) · [SHA256](SHA256SUMS.txt) · [대상 정보](manifest.json).

SHA256: `259dec689c428456ac244bff7333400533d94eaf80e6e86a6152881e19310fd3`.

Android8.0(API26) 이상용 debug APK. 상단 버튼 겹침·접힌 요약 잘림·제목 가독성을 수정했다. 공통48dp 지도 버튼 행, 실제 요약 높이 기반 시트, 상태바 아래 손잡이와 탐색 영역 보호를 적용했다. ViewBinding과 기존 서버/DB/Room/점수 정책은 유지한다.

2026-11-06 단위27·도구13, 빌드 성공/lint 오류0·경고38. 최종 APK API35 small/standard/pane3개 프로필 회귀 통과. [정확한 검증 범위/캡처](../../verification/ui-sheet-fixes-2026-11-06/verification.md), [설치·서버 연결·실기기 표](../../DEVICE-TEST.md).

install -r로 기존 즐겨찾기를 유지한다. 검색에는 PC 서버, 지도에는 인터넷이 필요하다. 실기기/사용자 최종 UI·전체 명세/운영 인수는 미완료다. 이전 설치 묶음은 당시 근거로 보존한다.

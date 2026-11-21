# 지도 전체화면 설치 묶음

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

[설치 APK](night-safety-fullscreen-debug.apk) · [SHA256](SHA256SUMS.txt) · [대상 정보](manifest.json).

SHA256: `eb23f011afd8758722af2eaee31164216dbaa997b89b450771963d88034cc38d`.

Android8.0(API26) 이상용 개발 debug APK. 전체화면을 누르면 지도만 앱 영역에 크게 표시하며, 화면 복귀/뒤로로 돌아온다. 기존 ViewBinding과 검색 결과를 유지한다. 최종 APK의 API35 small/pane TMAP/로컬4개 흐름 통과, 빌드 성공/lint 오류0·경고41. 단위27개는 동일 Kotlin 코드의 직전 실행 통과, 마지막 문구 빌드는 UP-TO-DATE다. 도구13개 통과.

[검증 범위/근거](../../verification/fullscreen-2026-11-06/verification.md), [USB 설치·서버 연결·실기기 검사표](../../DEVICE-TEST.md). 기존 즐겨찾기를 유지하는 install -r 업데이트를 사용한다. 검색에는 PC 서버, 지도에는 인터넷이 필요하다.

실기기·사용자 최종 UI·전체 명세/현장/운영 인수는 미완료다. 이전 설치 묶음과 검증은 당시 근거로 보존한다.

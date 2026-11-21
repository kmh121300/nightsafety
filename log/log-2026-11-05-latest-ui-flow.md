# 최신 APK 전체 기능 흐름 검사

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자가 승인한 실기기 연결 전 검사 중1번만 실행했다. 21:58~22:09 KST, Windows와 기존 API35 Pixel_3a 임시 read-only 에뮬레이터5556, DB 시작 snapshot 서버를 사용했다. 서버 health ready, DB configured/verified true. 설치/로컬 APK SHA256은 `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9`로 일치했다.

source 가상환경에서 `python -X utf8 tools/integration_smoke.py --serial emulator-5556` 실행, 종료 코드0·8개 PASS:

1. TMAP 준비·시설1381개(보안등870개 포함).
2. 기본 검색 후보3개·연결 미완결 안내·공식3유형 지표.
3. OSM anchor 검색·그래프 연결·실제 보행 미검증 안내·세 점수0~100.
4. 취약 구간 상세와 강조 전환.
5. CCTV/보안등 필터1381→1111/511→1381.
6. Room 저장 후 프로세스 재시작·서버 연결 해제 상태의 snapshot 복원·과거 결과 안내.
7. 이름·선호유형 수정·연결 복원 후 최신 재조회·보행선 우선 적용.
8. 이번 시험용 즐겨찾기 삭제·목록 갱신.

[실행 보고서](../source/verification/android-2026-11-05_215835_067057/integration-ui.md)와 캡처2장을 보존했다. 캡처에서 지도 타일·경로선·주황색 강조·점수 카드를 직접 확인했다. 이번 실행 중 실패·외부 시스템 ANR 처리 기록 없음. 앞선0거리/API36.1 실패 기록은 수정하지 않았다.

앱/서버/DB/검사 도구 코드 변경·새 빌드·DB 가져오기는 하지 않았다. ADB reverse 복원, 서버/5556 유지. 다음은 [2번 오류·복구/권한 모의](log-2026-11-05-pre-device-checks.md)다. 일반 창 크기/프로세스 종료 시 미저장 입력 복원·API36.1 화면 소실 원인·실기기 GPS/제조사 UI/성능·현장·명세 전체/사용자 최종 UI 인수는 이번 통과 범위가 아니다. [로드맵](../ROADMAP.md).

문서 마감 확인: 변경5개 파일의 UTF-8·2026-11-05 날짜·신규 내부 링크·8개 PASS/실제 APK 해시 일치를 확인했다. 기존 ROADMAP 발표 문서 링크2개는 대상 파일이 없어 미해결로 남겼으며 이번 검사 범위의 새 링크에는 누락이 없다. 최종 서버 ready/DB verified·ADB device/reverse 연결 확인 완료.

# MVP 3유형 점수 적용 계획

작성일: 2026-11-04 · 최종 수정일: 2026-11-04 · 시간 기준: Asia/Seoul

사용자가 정책을 실제 적용하도록 지시했다. [정책](../../../../md/night-safety-mvp-scoring-policy-ko.md)을 기존 Python/PostGIS/Kotlin/XML 구조에 직접 적용한다. 추가 승인 없이 구현·검증·기록까지 진행한다. Git 저장소가 아닌 현재 작업 폴더를 사용한다.

- [x] 서버/DB: 보안등 eligibility, 자료 기간 상한 제거, 3유형 정식 점수/등급·완결 경로 추천, 누락/0거리·구버전 구분. Engine/source metadata를 DB snapshot에 함께 보존. test_backend/test_database의 회귀 실패→수정→통과.
- [x] Android/도구: 공식 필드를 파싱·표시하고 보안등 점수 제외·작동 미확인 문구 제거. 구 snapshot 부분지표는 그대로 구분. parser 단위 검사, DB/API·전체 UI 도구의 기대값 갱신. 빌드/단위/lint 검증.
- [x] 실제 검증/기록: 새 append-only DB bundle import·전체 복원/API 대조, 설치 APK 해시와 전체 UI 확인, 읽기 전용 코드 검토. 실패는 별도 날짜 기록으로 보존. 로드맵/로그/실행 안내 갱신.

핵심 검사: 180/365일 초과 자료, 조명 미확보와 정상0건, 시설 중복, 같은 geometry 재평가, 0거리·미완결, 구 snapshot·버전 불일치. 경로 topology·자료 원본을 변경하지 않는다. 실기기/현장/배포 검증을 이 작업의 성공으로 간주하지 않는다.

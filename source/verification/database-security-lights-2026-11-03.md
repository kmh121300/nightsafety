# 보안등 DB 반영·복원/API 재검증

작성일: 2026-11-03 · 최종 수정일: 2026-11-03 · 시간 기준: Asia/Seoul

검사 시각: 2026-11-03 15:29~15:31 KST. 사용자가 DB를 재활성화했다고 알린 뒤 기존 승인 범위의 보안등 import를 재개했다. 이전 `tenant/user not found` 실패는 [기존 검사 기록](security-lights-2026-11-03/verification.md)에 보존한다.

## 환경과 대상

- Windows / 프로젝트 `.venv` Python3.10.11 / 기존 Supabase PostgreSQL·PostGIS3.3 / `safenight` 스키마.
- 대상 코드: 현재 `server/engine.py`, `server/database.py`, `server/postgis.py`, `tools/db_smoke.py`. Git 커밋은 미기록(작업 폴더는 Git 저장소 아님).
- 입력: 기존 CCTV270·비상벨238행과 [보안등 파일럿 asset](../app/src/main/assets/pilot-security-lights.geojson)870행. 원본 CSV SHA256 `7c441fea2d6e651320aca98c178127e1078c8cd5d0b384797f2631a2273941ed`.
- 새 코드·APK 변경 없음. 기존 APK SHA256 `57d3fc82978f492e38de66a8938e469a68d81ef4b630f2a5e7ea3f9f7ffedb17`은 이번 DB/API 검사의 실행 대상이 아니며 앱 전체 통과로 해석하지 않는다.
- sandbox 연결은 제한으로 실패했고 권한 확장 환경에서는 읽기 연결이 성공했다. 연결 문자열·비밀번호·키는 기록하지 않았다.

## 실행과 결과

실행 위치는 `source`이며 Python 명령은 `.\.venv\Scripts\python.exe -X utf8`를 사용했다.

| 명령 | 결과 |
| --- | --- |
| `server/postgis.py` | 읽기 접속 성공. 기존5개 테이블, 시설508·노드27,607·간선8,208·구간22,256 확인 |
| `server/postgis.py --apply` | 한 트랜잭션의 append-only 새 버전 가져오기 및 commit 성공. 시설1,378·노드27,607·간선8,208·구간22,256 |
| `tools/db_smoke.py --verify-import` | 종료코드0, PASS. 같은 버전 재가져오기 행수 불변, 잘못된 도형의 시험 import 전체 rollback 확인 |

DB 복원 결과와 로컬 원본의 모든 노드/태그·방향별 간선·시설/속성·점수 표본/구간/비용을 대조해 일치했다. SRID4326/도형 유효성, 테이블5개의 RLS, DB 기반 HTTP health/config/facilities/places, 후보3개 경로 비교·evaluate·0거리 응답, 하위10% 길이와 공식 점수 null이 통과했다. 시설 API의 보안등870건도 검사했다. 검증용 HTTP 서버는 도구 종료 시 닫힌다.

후속 읽기 전용 검사에서 전체 bundle2개의 manifest와 실제 각 테이블 행수가 모두 일치했다. 이전 시설508·노드27,607·간선8,208·구간22,256 버전이 보존됐고 최신 버전은 시설1,378건임을 확인했다. 검사 결과 PASS.

## 상태 영향과 남은 범위

R3 및 R5의 **보안등 실제 DB 저장·서버 시작 시 복원/API 연결 검증은 완료**다. 운영 서버는 새로 배포하지 않았으며 실행 중 서버가 있다면 재시작해야 최신 bundle을 읽는다. 기존 점수 기준과 공식 점수 null, 보안등 표시 전용 정책은 유지한다.

이번에는 Android 에뮬레이터/실기기 UI를 재실행하거나 APK를 다시 빌드하지 않았다. 최신 전체 UI의 이전 실패, 실기기 GPS·권한, 야간 점등/접근성·이용조건·공식 점수 인수·운영 배포는 남아 있다. [15:11 로컬 파일 기반 보안등 UI 통과](android-2026-11-03_150042_324475/security-lights-ui.md)와 이번 DB/API 통과는 서로 다른 환경의 근거다.

관련: [로드맵](../../ROADMAP.md), [개발 로그](../../log/log-2026-11-03-security-lights.md).

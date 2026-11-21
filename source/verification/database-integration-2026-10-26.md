# 실제 PostgreSQL/PostGIS 통합 검증 — 2026-10-26

작성일: 2026-10-26 · 최종 수정일: 2026-10-26 · 실제 검증일: 2026-10-26 · 시간 기준: Asia/Seoul

DB/API와 Android 전체 UI 결과는 별개입니다. 이후 상태 변경과 전체 작업 순서는 [전체 로드맵](../../ROADMAP.md)을 확인합니다. 문서 안내 추가만으로 검증 날짜나 결과를 갱신하지 않습니다.

사용자가 준비한 개발 DB의 `safenight` 스키마에서 실행했다. PostGIS 3.3.7은 `extensions`에 설치되어 있다. 연결 문자열·계정·비밀번호는 이 기록에 포함하지 않는다.

## 구현과 저장 결과

- `ns_bundle`: 버전·출처 상태·예상 행수 기록.
- `ns_node`: OSM 노드 27,607개. 장소 검색에 필요한 비탐색 노드와 태그도 보존.
- `ns_facility`: CCTV·비상벨 508개. 경찰시설 3개는 기존 Android 번들 표시만 유지.
- `ns_edge`: 방향별 간선 8,208개와 거리·시간·위험 비용·인접 시설 ID.
- `ns_segment`: 계산 구간 22,256개와 길이 가중 점수 표본.
- 공간 인덱스·외래 키와 테이블 5개 RLS 활성화. 공개 클라이언트 정책·권한 추가 없음.

서버는 `.env.local` 또는 환경변수의 DATABASE_URL이 있으면 시작 시 DB의 최신 bundle을 읽기 전용 repeatable-read 트랜잭션으로 복원한다. 탐색은 복원한 메모리 그래프의 기존 Dijkstra로 수행한다. DB 오류·불완전 bundle이면 시작을 중단한다. 설정이 없으면 기존 로컬 파일 모드다. DB 연결 검증 여부와 startup_snapshot 모드를 `/health`, `/v1/config`에 표시한다. DB 갱신 반영에는 서버 재시작이 필요하다.

호스팅 DB의 기본 실수 출력이 일부 비용을 15자리로 줄이는 것을 전체 대조 검사에서 발견했다. 로딩 트랜잭션에 extra_float_digits=3을 적용한 후 전체 간선·구간 비용이 원본과 정확히 일치했다.

## 실제 실행한 검증

프로젝트 전용 `.venv`에 psycopg 3.3.6을 설치했다.

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s server -p 'test*.py' -v
.\.venv\Scripts\python.exe -X utf8 server/postgis.py --apply
.\.venv\Scripts\python.exe -X utf8 server/postgis.py
.\.venv\Scripts\python.exe -X utf8 tools/db_smoke.py --verify-import
```

- 서버 테스트 16개 통과: 기존 11개 + DB 환경설정·복원·미완결 bundle·실패 시 로컬 대체 방지·오류의 비밀정보 숨김 5개.
- 동일 자료 반복 import 후 모든 행수 유지.
- 잘못된 geometry를 포함한 시험 bundle import 실패 후 해당 bundle 0행, 기존 bundle 행수 유지. 전체 트랜잭션 rollback 확인.
- 전체 노드/태그·방향별 그래프·시설·모든 간선과 점수 표본이 로컬 원본과 정확히 일치.
- 저장 geometry 전부 유효, SRID4326 확인. RLS 테이블 5개 확인.
- DB 복원 엔진으로 실제 HTTP `/health`, `/v1/config`, `/v1/facilities`, `/v1/places`, `/v1/routes/compare`, `/v1/routes/evaluate` 통과.
- 대학–정왕역 주변 보행 anchor의 경로 후보 3개가 원본의 형상·간선·거리·시간·부분 지표·시설 개수·생성 정책과 일치.
- 하위10% 길이, 공식 안전점수 null 유지, 동일 anchor의 0거리 응답 확인.
- DB 기반 로컬 서버를 `127.0.0.1:8765`에 시작함. 확인 시점의 실행 상태이며 이후 종료 여부는 이 기록이 보장하지 않는다.
- 별도 코드 검토에서 진행을 막는 구현 문제 없음. 오래된 README의 DB 미연결 문구를 갱신함.

## Android 화면 확인

기존 Debug APK를 Pixel_3a 에뮬레이터에 재설치하고 adb reverse로 DB 기반 서버에 연결했다. 첫 전체 UI 검사는 지도 준비 상태를 기다리는 중 에뮬레이터 System UI의 응답 없음 창으로 실패했다. 첫 실패 캡처에서 TMAP 인증 성공·지도 타일·시설 표시는 확인했다. 시스템 창 정리 및 화면 깨우기/잠금 해제 후 두 번 재시도했으나 모두 `TMAP 지도 · 파일럿 실데이터` 상태를 기다리다 시간 초과했다. 중간 검은 화면과 마지막 도착지 설정 대화상자도 관찰했다. 첫 System UI 오류 외의 재시도 실패 원인은 확정하지 않았다.

전체 검색·즐겨찾기 UI 통과로 기록하지 않는다. Android 소스는 변경하지 않았고 새 APK 빌드도 실행하지 않았다. 기존 2026-10-16 UI 성공 기록과 이번 DB/API 성공을 새 UI 전체 성공으로 합치지 않는다. 테스트용 에뮬레이터는 종료하며 DB 기반 로컬 서버는 유지한다.

## 남은 범위

현재 연결은 개발용 가져오기 권한을 가진 계정이다. 운영용 읽기 전용 계정 분리·성능/백업·HTTPS 운영 배포, 실기기 GPS, 현장 보행은 미검증이다. pgRouting 실행이나 요청마다 DB에서 계산하는 경로 서버를 구현한 것은 아니다. 가로등 누락·과거 시설 자료·실제 출구 연결 미검증은 그대로이며 공식 안전점수는 null이다.

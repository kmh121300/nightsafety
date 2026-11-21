# DB snapshot 기반 0거리 API 확인

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

기존 PostGIS startup snapshot 서버의 보행 anchor 조회 후 대학 옆문 보행 지점 하나를 출발·도착 양쪽에 넣어 `/v1/routes/compare`를 호출했다. 새 DB import/데이터 수정은 하지 않았다.

[검사 결과](result.json): 후보1개, 상태 already_at_destination, 거리0m·시간0s, 전체/평균/취약 점수 모두 null, geometry null, segments/edge_references 비어 있음. assert 모두 통과했다. bundle/graph/scoring/routing 버전은 결과에 함께 기록했다.

이 결과는 API 범위이며 Android 앱의 표시 검증을 대신하지 않는다. [작업 로그](../../../log/log-2026-11-05-zero-route.md).

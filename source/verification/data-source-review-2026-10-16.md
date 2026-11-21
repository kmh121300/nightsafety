# 외부 시설 자료 재확인 — 2026-10-16

작성일: 2026-10-16 · 최종 수정일: 2026-10-26 (문서 안내 추가) · 실제 원천 확인일: 2026-10-16

원천 응답은 당시 확인 결과입니다. 이번에는 외부 API를 다시 호출하지 않았습니다. 현재 확보/대기 상태와 병행 작업은 [전체 로드맵](../../ROADMAP.md)을 확인합니다.

기존 Smartstlamp HTTP502 기록은 2026-10-05 결과다. 2026-10-16에는 HTTP200과 정상 JSON 응답을 확인했다. 현재 상태를 계속502라고 보고하지 않는다.

- 원천: https://openapi.gg.go.kr/Smartstlamp
- 무필터 pSize100: head 총71건, row5건. 샘플은 만안구이며 기준일20260206.
- 좌표 필드: REFINE_WGS84_LAT, REFINE_WGS84_LOGT.
- SIGUN_NM=시흥시: INFO-200(해당 데이터 없음).
- SIGNGU_NM=시흥시: 무필터와 같은 만안구5건. 필터 적용이 검증된 것이 아님.
- 샘플의 SIGUN_NM은 null, SIGNGU_NM은 만안구. 전수 조회·필터·시흥 커버리지를 별도 검증해야 함.

**시흥시 가로등 좌표·전체 커버리지를 확보한 결과는 아니다.** 만안구 샘플을 시흥 앱이나 공식 점수에 넣지 않았다. 표준 보안등과 스마트 가로등도 임의로 동일 유형으로 취급하지 않는다.

공식 후보 자료: [공공데이터포털](https://www.data.go.kr/data/75232/linkedData.do), [경기데이터드림](https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId=VEY71398U2941WM4E7PV21507518&infSeq=1).

호출 증거는 lamp-source-check-2026-10-16.json에 보존했다. 이 별도 원천에 TMAP 앱키를 사용하지 않았다.

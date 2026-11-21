# 핵심38개 기능 명세와 현재 MVP 대조

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

[기능 명세1.2](../../../md/night-safety-functional-specification-ko.md)의 F-01~09 총38개를 코드와 기존 근거에 대조했다. 아래 상태는 구현 범위/근거의 판독이며 모든 TC를 새로 실행한 인수표가 아니다. 미구현·명세 차이를 미검증으로 숨기지 않는다. P0 표기는 명세 우선순위이며 모든 항목을 이번 변경으로 완료했다는 뜻이 아니다.

J=[22:09 전체 UI](../android-2026-11-05_215835_067057/integration-ui.md), K=[오류/권한](../error-recovery-2026-11-05/verification.md), I=[서버/DB/MVP 정책](../mvp-scoring-2026-11-04/verification.md), [0거리](../android-2026-11-05_210638_044884/verification.md). 이번 보완/새 APK 실행 결과는 [종합 검증](verification.md)에 별도로 기록한다.

| 기능 | 우선순위 | 현재 판정 | 코드·근거 | 충족 범위와 남은 차이 |
| --- | --- | --- | --- | --- |
| F-01-01 지도 초기 표시 | P0 | 부분 구현/검증 | MainActivity.displayMap·mapFailure, TmapPilotMap; J/K | 지도·로컬 대체/재시도 존재. 서비스 경계선 표시·인증 실패 개별 TC 미검증 |
| F-01-02 현재 위치 표시·지도 재중심 | P0 | 부분 구현/검증 | MainActivity.requestLocation; K | 일회성 마커/재중심·모의 수신/거부/시간 초과/OFF 검증. 정확도 원·수신 시각 상시 표시는 미구현, 실제 GPS 미검증 |
| F-01-03 지도 이동·확대·축소·범위 갱신 | P0 | 명세와 차이 | TmapPilotMap; /v1/facilities | 지도 제스처 지원. 앱은 고정 파일럿 시설 패키지를 사용하며 viewport별 재조회·페이지·별도 확대/축소 버튼 미구현 |
| F-02-01 출발지 설정 | P0 | 부분 구현 | RouteWorkflow.editPlace/useCurrentLocation; J/K | 직접 좌표·OSM 검색·현재 위치 존재. 지도 pin 출발지 지정 미구현 |
| F-02-02 목적지 검색·설정 | P0 | 부분 구현/검증 | RouteWorkflow·RouteApi.places; J/K | OSM 목록 선택/0건·범위 검사. 시흥 전체 POI/동명 장소 주소 구분 미지원 |
| F-02-03 출발·목적지 교환 | P1 | 구현/범위 검증 | RouteWorkflow.changed; K | 두 번 교환·이전 결과 안내/저장 차단 통과. 지연 응답과 동시 교환 TC 미실행 |
| F-02-04 경로 검색 요청·입력 검증 | P0 | 부분 구현/검증 | RouteWorkflow.search/post, RouteApi; K | 입력/범위·연결 실패·이전 결과 유지 검증. 실제 지연 응답 무시 개별 TC 미실행 |
| F-03-01 OSM 보행 그래프 구축·공개 | P0 | 구현/부분 검증 | server.engine + OSM 준비 자료; I | 원본 방향 간선/DB snapshot 사용. 전체 gate/foot=no/육교 층별 현장·전수 TC 미완료 |
| F-03-02 출발·도착 보행 anchor 연결 검증 | P0 | 구현/부분 검증 | engine anchors/compare; I/J | 정왕역 실제 출구는 미완결 유지. 그래프 anchor와 실제 출입구 통행 증거 구분, 현장 미검증 |
| F-03-03 빠른 경로 계산 | P0 | 구현/부분 검증 | engine Dijkstra; test_backend; I | 최소 비용/고정 속도 ETA 구현. 명세 전체 toy·고정 대기 TC 개별 대조 미완료 |
| F-03-04 안전 우선 경로 계산 | P0 | 구현/부분 검증 | engine compare; test_mvp_scoring; I | 3유형 비용 후보 중 최종 점수 재선택. 후보 풀 내 최선이며 전역 최적 보장 아님 |
| F-03-05 후보 병합·중복 제거·시간상한 적용 | P0 | 구현/부분 검증 | engine candidate merge/time cap; I | 중복·최대3·시간상한 있음. 모든 경계/최선 보존 TC 전수 인수 아님 |
| F-03-06 균형·보행선·추가 후보 생성 | P1 | 구현/부분 검증 | engine profiles; I/J | 균형·보행선 정책과 선호 재조회 확인. K=30 밖 사례 개별 TC 미대조 |
| F-04-01 경로 segment 분할·표본 구성 | P0 | 구현/부분 검증 | engine samples/segments; I | 20m 이하 구간·5m 이하 표본. 명세45m 분할 예 개별 실행 근거 미연결 |
| F-04-02 segment 안전도 계산·시설 영향 분석 | P0 | 구현/부분 검증 | engine point_score; test_backend/test_mvp_scoring; I | 거리 kernel·유형 max·원천 0/누락 처리. 현장 유효성/전 TC 아님 |
| F-04-03 평균 안전도 계산 | P0 | 구현/부분 검증 | engine metrics; test_backend; I | 길이 가중 평균·DB 전 표본 대조 근거. 명세 개별 예 전수 인수 아님 |
| F-04-04 취약구간 안전도 계산 | P0 | 구현/부분 검증 | engine metrics; test_backend; I | 하위10% 길이 가중 경계·weak 길이 검사. 분할 독립성 전체 TC 미완료 |
| F-04-05 경로 전체 안전점수 계산 | P0 | 구현/부분 검증 | engine metrics, ServerBundleParser; I/0거리 | 3유형 공식/부분 구분·거리0 null. 모델 가중치 보정은 별도 |
| F-04-06 경로 주변 시설 고유 개수 집계 | P0 | 서버 구현/앱 보완 | engine facility_counts, ServerBundleParser; 이번 회귀 | 서버 고유 개수/nullable 값을 앱으로 전달하도록 보완. 구간별 중복 전수 TC는 기존 근거와 별도 |
| F-05-01 후보 경로 선 표시·선택 | P0 | 구현/부분 검증 | TmapPilotMap/PilotPreviewView; J/0거리 | 후보/선택/등급 표시·0거리 선 제거. 미완결 gap 실선 금지 검증 일부 |
| F-05-02 경로 비교 정보 표시 | P0 | 필수 누락 보완 | MainActivity.refresh, 공통 result XML; 이번 회귀/UI | 거리/ETA/보행비율/3점수 + 누락된3시설 수 추가. 빠른 대비 차이·다른 버전 비교 전체 계약 미완료 |
| F-05-03 구간 등급·취약구간 지도 표시 | P0 | 구현/부분 검증 | segmentColor·TmapPilotMap; I/J | 색/범례/주황 취약 구간 있음. 모든 임계값·접근성 TC 전수 인수 아님 |
| F-05-04 취약구간 상세·판단 이유 조회 | P0 | 부분 구현 | MainActivity.showWeakSegments; J | 하위 구간 길이·점수·시설 기반 설명 표시. segment별 유형 기여/시설 ID/이유코드와 마커 연결 상세 미구현 |
| F-06-01 시설 종류별 마커 표시·범위 조회 | P0 | 명세와 차이 | PilotData assets·FacilityOverlayQueue; J | 파일럿1381개 표시. API bbox 존재하나 앱은 서버 시설 페이지/viewport 자동 갱신 미연결 |
| F-06-02 시설 종류 ON/OFF 필터 | P0 | 구현/범위 검증 | MainActivity.visibleKinds, FacilityOverlayQueue; J/이번 UI | 마커 필터·경로 수치 불변 확인. 모든 유형 연속 조작 TC는 일부만 검증 |
| F-06-03 시설 상세정보 조회 | P0 | 구현/부분 검증 | PilotData.facilityDetail·showFacility; I | 출처/기준일·주소 누락·경찰 후보 구분. 원천 필드 조합 전체 TC 미완료 |
| F-07-01 경로 즐겨찾기 저장 | P1 | 구현/범위 검증 | FavoriteStore.save·FavoriteValidation·RouteWorkflow; J | 저장/재시작 검증. 저장소 강제 실패 TC 미실행 |
| F-07-02 즐겨찾기 목록·상세·재조회 | P1 | 구현/범위 검증 | RouteWorkflow.openFavorite; J | Room 목록·오프라인 snapshot·과거 안내. 모든 버전 차이 TC 미실행 |
| F-07-03 즐겨찾기 이름·유형 수정 | P1 | 구현/부분 검증 | FavoriteStore.rename·FavoriteDao; J | 이름/유형 변경·과거 선 안내 확인. createdAt 보존/modifiedAt 갱신은 코드 근거, DB 개별 TC 미실행 |
| F-07-04 즐겨찾기 삭제 | P1 | 구현/부분 검증 | FavoriteStore.delete·FavoriteDao; J | 시험용 ID 삭제/목록 갱신. 다른 항목 보존 다중 기록 TC 미실행 |
| F-07-05 저장 경로 버전 확인·안전도 재평가 | P1 | 명세와 차이 | RouteWorkflow.openFavorite(requery=true); J | 항상 endpoint 재탐색 방식. 동일 geometry 재평가/metadata 버전 분기 UI 미구현; evaluate API는 존재 |
| F-08-01 공공데이터 수집·동기화 | P0 | MVP 대체/부분 구현 | 수동 CSV import·postgis·security_lights; I | 검증 CSV 수동 반영. 다페이지 외부 API 정기 동기화/실패 재시도 미구현 |
| F-08-02 시설 정제·중복·범위 검사 | P0 | 구현/부분 검증 | security_lights·postgis; I | ID/공유 좌표 보존·범위 격리·실패 rollback 근거. 신규 원천 전수 TC 미완료 |
| F-08-03 시설·segment 지표 사전계산·원자적 공개 | P0 | 명세와 차이 | postgis transaction·database.load; I | DB bundle 원자 import·시작 snapshot. 실행 중 새 bundle hot-swap 미구현, 재시작 반영 |
| F-08-04 데이터 기준일·미확보·갱신 상태 공개 | P0 | 구현/부분 검증 | engine source_states/config·MainActivity.showDataInfo; I/이번 UI | 기간 제한 없음·출처/기준일·0/누락 처리. 앱 원천 전 상태 갱신/운영 동기화 TC 미완료 |
| F-09-01 오류·재시도·요청 취소·부분성공 | P0 | 부분 구현/검증 | RouteApi/RouteWorkflow·ServerBundleParser; K | revision 취소·연결/위치 timeout·부분/이전 안내. 429 Retry-After·명시 cancel 버튼·오류 유형별 전체 UI 미구현 |
| F-09-02 점수·라우팅 설정 버전 관리 | P0 | 구현/부분 검증 | engine version config·database manifest; I | 설정/graph/facility 버전과 검증 있음. 일반 사용자 설정 UI 없음, Infinity 등 전체 설정 TC 미연결 |
| F-09-03 비회원 개인정보·키·저장정책 | P0 | 구현/부분 검증 | FavoriteValidation·RouteApi·server.app; I/K | 회원 없음·명시 저장·키 분리·raw SDK 로그 금지. APK 전수 보안/운영 DB 계정·전체 개인정보 인수 미완료 |

## 이번 작업에서 보완한 범위

정상 파일럿 검색/비교에 이미 반환되던 경로 주변 CCTV·비상벨·보안등3개 숫자를 앱에서 버리던 누락을 보완했다. 0·null·이전 snapshot을 구분하고 값 범위/정수/필수 유형 미확보 시 잘못된 숫자를 거절한다. 지도에 표시 중인 전체 시설 수와 별개이며 필터로 재계산하지 않는다. 원천 누락 이유도 부분 지표 안내에 표시한다. 서버 계산·DB·Room schema는 바꾸지 않았다.

## MVP 범위와 미구현의 처리

고정 파일럿 패키지/직접 좌표·OSM 입력/명시 재조회/서버 재시작 snapshot은 현재 기본 통합 시연 범위다. 지도 pin·자동 bbox/페이지·세부 구간 이유/시설 연결·동일 geometry 재평가·429 정책·실행 중 bundle 교체는 **명세와 차이 또는 미구현으로 남으며**, 이번 대조가 이를 인수 완료로 면제하지 않는다. 서비스 범위 확대/운영 정기 수집과 P2는 자동 구현하지 않았다. 향후 명세 전체 인수 전 이 항목들을 구현하거나 변경된 요구 범위를 별도로 합의해야 한다.

실제 GPS/정확도·제조사별 동작·현장 출입구/통행·이용조건·성능/HTTPS 배포는 기기/현장/운영 검증이다. 세로 고정·글꼴1.0 고정은 사용자가 선택한 MVP 정책으로 유지하며, 일반 창 크기/프로세스 복원 문제는 해결로 표시하지 않는다.

다음 화면·설치 준비 단계에서는 이 표의 미지원 범위를 실기기 검사표에 이어 기록한다. '기기 연결 전 지정 검사 완료'와 '38개 기능/교차TC 전체 인수 완료'를 구분한다. [로드맵](../../../ROADMAP.md).

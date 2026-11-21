# 밤길 지킴이 — 시흥 라우팅 준비도 점검

2026-10-05. 원본 OSM bbox `126.719,37.334,126.751,37.359` 스냅샷만 사용했다. `raw.osm` SHA256: `bb4586cbb583446979b8461f85c9ac8e8599cfe10de49029749629902576692d`. 원본 파일·V2 코드·OSM 지도 변경은 0건이다. 이 점검은 지도 및 그래프 검증이며 실제 야간 보행 현장 검증은 아니다.

**판정: 알고리즘·데모 개발은 진행 가능. 현재 데이터로 대학→정왕역 실제 출구까지 야간 길안내를 완료했다고 표시할 수 없다.** 현장 검증된 한 개의 corridor를 먼저 확보하는 것이 최소 범위다. 도로 선형에 foot 허용 태그가 있는 것과 연속 보도가 실제로 존재하는 것은 다르다.

## 실제로 실행한 검증

캠퍼스 polygon way234844934 경계를 통과하는 기존 highway 7개를 자동 추출했다. 공식 정문/서문/북문과 각각 일치한다고 판정하지 않았다. 바깥 node `4130186271,3040043928,4657546842,4657546844,4665172637,9799703999,9799704016` 및 내부 node `9799703963`에서, 역 주변 기존 highway node `4665188383,4665188380,4673861122`와 실제 출구1 `3403277121`, 출구2 `3403277120`까지 총40쌍을 각 정책별 정·역방향으로 탐색했다. 근접 snap이나 신규 간선 없이 원본 연속 node 쌍만 이용했다.

| 그래프 정책 | 방향 간선 수 | 도달한 쌍/40, 정방향 | 역방향 | 해석 |
|---|---:|---:|---:|---|
| inferred | 9,904 | 24 | 24 | 역 주변 3개 node는 전부 도달, 실제 출구2개는 전부 실패 |
| 주요도로 primary/secondary 제외 | 9,424 | 24 | 24 | 주변 node 연결은 유지되지만 보도 증빙은 별도 |
| 보행선 또는 foot 명시 허용만 | 1,708 | 0 | 0 | 해당 origin-target 쌍은 단절 |
| 계단·bridge 태그 간선 제외 | 9,786 | 24 | 24 | 그래프상 우회 가능. 계단 없는 접근성 검증은 아님 |
| foot/access 허용이 명시된 간선만 | 154 | 0 | 0 | 명시 접근권 데이터만으로는 서비스 범위가 성립하지 않음 |

이 스냅샷에서 위 그래프의 비대칭 간선은 모두0개라 정·역방향 결과가 같다. 따라서 **실제 보행 일방통행 데이터 처리의 검증 사례가 확보된 것은 아니다.** 모든 도달쌍에서 A*와 Dijkstra 정책비용이 일치했고, 반환 간선이 원본 way의 연속 node인지 검사했다. 전체 시흥 도달률·서버 부하·최신 지도 동기화는 이40쌍 시험으로 입증하지 않았다.

외부 옆문 node9799703999→역 주변 node4665188383 기준: V2 보행선 우선은1,932.56m, 전용 보행선76.40%, 나머지456.08m는 도로 선형이다. 교량·계단 제외 시1,579.26m 경로로 바뀌며 도로 선형 사용으로 우회한다. 출구1까지12.56m 미검증 간격은 그대로이고, 출구2도 graph에 없다.

## 6개 교정 후보의 결론

| 후보 | 지도에서 확인한 사실 | 필요한 다음 증거 / 처리 |
|---|---|---|
| station-exit-gap | 출구1 node는 highway에 소속되지 않음. crossing way472303067의 node4665188383과12.56m | 역 출구→광장/보도로 실제 통행 가능한 연속 선형, 장애물·단차·층을 현장이나 시설 도면으로 확인. 임의12.56m connector 금지 |
| side-door-explicit-access-gap | 옆문 service endpoint와 foot=yes road node4130186271은 다른 ID,11.30m | 옆문 운영시간·출입 자격 및 두 지점 사이 실제 보도 확인. 태그 없는 service를 이름만 보고 footway로 재분류 금지 |
| explicit-component-nearest-gap | 두 explicit 성분 최근접 node 사이101.06m | 직선은 도로·대지의 통행 증거가 아님. 실제 보도/횡단 선형과 연결 node 확인. 단순 최근접 병합 금지 |
| road-run-0 | 기존 service/residential ways1067311768,471567474,76.53m | 옆문 외부 접근로와 교차로 보도의 연속성 확인 |
| road-run-1 | 마유로 tertiary foot=yes way493192211,162.66m | 보도 위치·진행방향별 횡단 연결 확인. road centerline offset 생성으로 대체하지 않음 |
| road-run-3 | residential/service ways473224934,473225094,473225014,216.90m | 주거도로·주차장 진입부 실제 보행 통로와 보도 단절 확인 |

**지도와 검색 문서만으로 승인 가능한 topology repair는0건이다.** 새 태그·선형을 관측한 것으로 꾸미지 않았다. 원본 geometry는 기존 `correction-candidates.geojson`, 추가 조사용 노드·태그는 `routing-evidence.json`에 있다.

## 횡단·출입·육교 신뢰도

보행선 우선 후보에서 crossing node11개를 확인했다. 신호 태그3개, marked7개, 유형 미기재2개이며 일부 node는 신호와 marked를 동시에 가질 수 있으므로 수치를 합쳐 횡단보도 개수로 읽으면 안 된다. 한 횡단 way의 양쪽 도로 node도 각각 집계될 수 있다. 미기재 node8189625930·3040044456부터 조사한다. node13702941711은 도로 way493192211, crossing footway1495768594, sidewalk1495768614를 공유하므로 지도상 횡단 연결 근거가 있다. 이는 현재 신호 작동·실제 안전·양쪽 보도 연속성을 증명하지 않는다.

후보에 steps way는0개, bridge footway471592949는1개다. 해당 육교의 계단·경사로·승강기·야간 폐쇄를 입증하는 태그/공식 운영자료는 확보하지 못했다. 후보 way에 opening_hours/conditional 태그가 없는 사실은24시간 개방의 증거가 아니다. bbox에 barrier=gate node도 없어 OSM만으로 캠퍼스 gate 운영을 판단할 수 없다.

대학 학보의2024 캠퍼스 소개는 남문(정문)·서문·북문(후문) 명칭을 제공한다. 해당 페이지 직접 fetch는403이고 검색 인덱스만 확인했으므로 지도와 대응 좌표 및 현재 운영시간은 미확인이다. 공식 대학·코레일 검색에서도 옆문/출구 connector를 승인할 도면과 야간 운영시간을 확보하지 못했다. 문서 부재를 폐쇄/개방의 증거로 사용하지 않았다.

## K개 후보 +10분 필터: 실제 반례 확인

원본 방향 간선에 Yen loopless 거리순 K=30을 실행했다.30개는1,572.40~1,591.62m에 몰리고, 전용 보행선 비율은0.17~13.12%다. V2의1,932.56m/76.40% 후보는30개에도 포함되지 않았다. **거리순 K=3만 생성한 뒤 시설 점수로 재정렬하면 보행선 후보가 누락된다.** 이 문제는 K만 조금 늘리면 해결된다고 보장할 수 없다.

공유 원본 간선길이/두 경로 중 짧은 길이<80%라는 실험 필터를 pairwise 적용한 greedy 선택은 rank1·2·4·14의4개를 남겼다. 단순 way ID가 다른30개를30개의 유의미한 대안이라고 세면 안 된다. 80%는 실험 기준이며 안전 기준이 아니다. 거리순 rank4도 보행선 비율0.17%라 기하학적 다양성 자체가 보도 확보를 뜻하지 않는다.

속도1.2m/s를 **실험상 가정**하면 +10분은+720m이고, shortest1,572.40m 기준 상한2,292.40m다. 보행선 우선 후보는 shortest보다360.16m/+5.00분으로 한도 안이다. 후보 생성에서 거리 최적·보행선 우선·검증된 접근권/횡단 우선 등의 정책을 각각 실행하고 합쳐 중복/공유율을 제거한 뒤 실제 예상시간으로 필터하는 것이 최소 수정안이다. 현재 ETA는 횡단 신호 대기·경사·사용자 속도를 반영하지 못한다. K개를 채우기 위한 가짜 route는 반환하지 않고 부족한 개수를 그대로 반환한다.

## 비용함수와 A* 주의점

현재 `sum(distance×multiplier)`는 multiplier≥1이므로 각 edge cost≥실제거리이며, Haversine heuristic은 삼각부등식으로 하한이 된다. 원본 스냅샷의 도달쌍에서 Dijkstra와 일치했다. 태그·시설 confidence를 반영한 `distance+nonnegative penalty`도 같은 하한을 유지할 수 있다. 시간 비용이라면 heuristic도 distance/max_speed 등 시간 단위로 맞춰야 한다.

‘안전한 edge에 할인’으로 multiplier<1을 주면서 Haversine을 그대로 쓰면 admissibility가 깨질 수 있다. 음수 안전보너스를 더하면 Dijkstra/A* 전제까지 깨진다. risk multiplier2/4는 경험적으로 보정된 위험 확률이 아니므로 UI에는 안전점수로 표시하지 않는다.

경로 전체의 평균/비율/최솟값/CCTV 중복 제거/최악구간 등 **비선형 최종 score**를 그대로 edge 합산 최적이라고 주장할 수 없다. 동일 node에서도 누적 노출·최악구간·수집된 시설 집합이 다른 경로가 존재한다. 먼저 제한시간 내 다양한 후보를 생성하고 별도 score로 순위를 매기는 MVP가 가능하되 전역 최적 안전경로 보장은 하지 않는다. 엄밀한 최적화가 요구되면 목적함수를 additive로 재설계하거나 상태 확장·다중 label 및 시간제약 최적화가 필요하다.

파서의 다음 점검항목: 현재 `foot/access` conditional은 보수적으로 제외하지만 `oneway:foot:conditional`, node/way opening_hours, 보행 restriction relation은 완전 평가하지 않는다. 현재 후보에 해당 태그가 없는 것만 확인했다. bbox 밖 우회는 이번 시험에 포함되지 않았다. 이 부분은 배포 전 별도 정책·회귀 케이스가 필요하다.

## 최소 진행 범위와 출시 gate

1. 지금: 원본 스냅샷/graph 버전 고정, graph-only 경로 데모, 정책 후보 합치기, 부족한 후보/route_incomplete 상태 및 endpoint gap UI. 실제 출구까지 완료 경로는 null을 유지한다.
2. 현장: 주·야간 동일 corridor 왕복 확인, 옆문 운영·출입권,456m 도로 선형 구간, 유형 미기재 횡단2개, 육교 진입부, 출구1 connector를 사진/GPS/시간/조사자/근거와 함께 기록한다. 실제 선형만 검수 후 별도 버전으로 입력한다.
3. 한 corridor 공개 시험: 검증된 start/end 연결, 모든 횡단과 접근권, 폐쇄시 우회/안내불가 처리, ETA 오차 및 안전점수 오인 여부를 통과시킨다. 이후 bbox 및 OD를 확대한다.
4. 미검증 지역 fallback: ‘해당 구간 보행 연결 미확인’과 마지막 검증 node를 표시하고 경로를 중단한다. 지도/시설 정보만 보여주거나 외부 길찾기 handoff를 제공하되 외부 경로를 본 앱의 안전 검증 결과로 표시하지 않는다.

실행검증: 원본 graph·정역방향 도달·A*/Dijkstra 일치·원본 간선 provenance·K=30·시간/다양성 계산. 문서만 확인: OSM 태그 의미, NetworkX 알고리즘 전제, 대학 문 명칭. 미확보: 현재 출입시간/시설 도면. 필요 credentials: 이 로컬 재현에는 없음; 운영 지도갱신·외부 routing/API 인증은 별도 점검 범위. 반드시 현장: 실제 보도 연속성, gate 접근권, 육교, 출구 connector, 야간 운영 상태.

## 재현 및 1차 문서

`python project_readiness/routing/audit_routing.py` → `routing-evidence.json`, `expanded-routes.geojson`; 출력은 `verification.txt`에 보관. 읽기 전용 입력은 `osm_poc_v2/raw.osm`이다. 후보30개 생성은 알고리즘 PoC이며 NetworkX 패키지는 사용하지 않았다.

- A* 문서: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.shortest_paths.astar.astar_path.html
- Yen/simple paths 문서: https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.simple_paths.shortest_simple_paths.html
- OSM crossing: https://wiki.openstreetmap.org/wiki/Key:crossing
- OSM pedestrian direction: https://wiki.openstreetmap.org/wiki/Key:oneway:foot
- OSM conditional restrictions: https://wiki.openstreetmap.org/wiki/Conditional_restrictions
- 대학 학보2024 캠퍼스 소개(검색 인덱스 확인/직접 fetch403): https://news.tukorea.ac.kr/news/articleView.html?idxno=444

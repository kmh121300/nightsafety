# 밤길 지킴이 — 플랫폼 준비도

검토일: 2026-10-05. 공식 공개 문서 기준. 사용자 TMAP appKey/Supabase 프로젝트 접속정보가 없어 **실제 인증 API 호출·Android 빌드·Supabase DB 실행은 확인하지 못했다**. 현재 환경에는 psql/postgres/docker 실행기가 없다. 기존 OSM Python PoC는 DB 연동의 증거가 아니다.

## 판정

| 항목 | 판정 | 개발에 적용할 결정 |
|---|---|---|
| Kotlin Android + TMAP 지도 + 자체 OSM 경로/시설 overlay | 조건부 GO | 공식 Android 문서에 선·마커 API가 있다. 선택 SDK 버전으로 앱키 인증과 실제 기기 표출을 1회 통합 검증해야 한다. |
| TMAP 보행 최단 경로 | 조건부 GO | searchOption=10을 비교 기준으로 사용한다. 서비스키 호출은 미검증. |
| TMAP 보행 최속/안전 최적화 | 기능명 수정 필요 | 추천/대로우선은 최속 보장이나 CCTV·조명 가중 최적화가 아니다. 안전추천은 자체 그래프에서 계산한다. |
| Supabase PostGIS + pgRouting | 조건부 GO | 공식 지원. 실제 프로젝트 확장 버전·함수 signature·용량·시간은 verification.sql과 파일럿 import로 확인한다. |
| 비회원 즐겨찾기 | GO(설계) | Room에 사용자 선택 장소를 기기별 저장. 클라우드 동기화 요구가 생기면 Auth/RLS 추가. |
| TMAP 응답 영구 저장 | 현재 설계에 사용하지 않음 | 공식 약관의 24시간 제한 때문에 POI/경로 응답을 영구 자체 DB로 축적하는 계획은 변경해야 한다. |

## TMAP에서 확정된 내용

보행자 endpoint는 `POST https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1`, 인증은 appKey header다. 옵션은 **0 추천, 4 추천+대로우선, 10 최단, 30 최단거리+계단제외**다. 보행 경유지는 최대 5곳. '빠른 길'이라는 UI는 추천 경로와 추정시간으로 바꾸거나, 자체 이동시간 비용 모델을 정의해야 한다. 대로우선이라는 이유만으로 안전점수가 높다고 처리하지 않는다. [보행자 API](https://tmap-skopenapi.readme.io/reference/보행자-경로안내)

TMAP REST는 X=경도, Y=위도. 요청/응답 모두 `WGS84GEO`를 명시한다. **WGS84GEO와 Google Mercator(EPSG:3857)는 서로 다르다.** DB·GeoJSON은 EPSG:4326의 `[longitude, latitude]`로 통일하고 Android SDK adapter에서 변환한다. 공식 Android 목차에서 구 Raster `setCenterPoint(longitude,latitude)`와 Vector `setCenterPoint(latitude,longitude)`가 다르므로 공통 순서라고 가정하지 않는다. 선/마커 생성으로 OSM 경로와 공공시설을 표현할 기술적 수단이 있다. [지도/Android API 가이드](https://tmapapi.tmapmobility.com/main.html)

| TMAP 그룹 | Free 일 한도 | Premium 건당(VAT 포함 표기) |
|---|---:|---:|
| 경로안내(보행자 포함) | 1,000 | 11원 |
| 지도보기 | 100,000 | 0.11원 |
| POI 검색 | 20,000 | 1.1원 |
| 지오코딩 | 20,000 | 0.55원 |

공식 요금표에서 Free 한도 초과 시 자동 차단. Lite 월 2,200,000원(VAT 포함)이므로 팀 프로젝트는 먼저 Free 일 한도를 계측한다. 옵션 3개를 별도 요청하면 한 사용자의 검색이 3호출이 될 수 있다. 그룹 한도이며 보행자를 독립 1,000건 추가로 계산하지 않는다. [공식 요금표](https://openapi.sk.com/products/calc?menuSeq=5&svcSeq=4)

TMAP 공식 약관은 얻어진 데이터를 저장한 후 24시간 이상 사용할 수 없다고 명시한다. POI 검색·지오코딩은 장소 선택 도구로 사용하고, 응답 snapshot/경로는 만료를 적용한다. 영구 즐겨찾기는 사용자 직접 지정 좌표·별칭 또는 별도 이용허락을 가진 공공/OSM 데이터로 설계한다. TMAP에서 반환한 좌표·이름·ID까지 어떤 범위로 장기 보존 가능한지, OSM 기반 경로를 TMAP 지도에 겹치는 배포 조건은 공개 간단 약관만으로 확정하지 못했다. **기술적 overlay 지원을 계약상 포괄 허용으로 해석하지 않는다.** 출시 전 개발문의에 구체 사용방식을 확인해야 한다. 로고/출처 표시도 선택 SDK 정책을 확인하고 보존한다. [공식 약관](https://tmapapi.tmapmobility.com/terms.html)

## Supabase에서 확정된 내용

| Free 자원 | 공개 한도/조건 |
|---|---|
| DB | 500MB/프로젝트, Shared CPU·500MB RAM |
| 파일 Storage | 1GB |
| 전송 | egress 5GB + cached egress 5GB (서로 별도 계량) |
| Data API | 요청 수 unlimited; 처리량/CPU/전송이 무제한이라는 뜻은 아님 |
| Edge Functions | 월 500,000 invocations |
| 프로젝트 | 활성 2개, 1주 비활동 후 pause |
| Pro | 월 $25부터, 유료 플랜 compute credit $10/월; 추가 프로젝트 compute 비용 고려 |

[가격](https://supabase.com/pricing), [함수 가격](https://supabase.com/docs/guides/functions/pricing). OSM raw 7.9MB만 보고 500MB 안에 들어간다고 확정할 수 없다. import 후 geometry·인덱스·시설·로그를 포함해 실제 크기를 측정한다. 시흥 일부 파일럿은 시작 가능한 규모로 판단하되 실제 성능·동시요청은 미검증이다.

Supabase 공식 문서는 PostGIS와 pgRouting을 지원하고 pgRouting 확장 활성화를 안내한다. upstream 최신은 4.0.2(2026-09-05)지만 **사용자 hosted 프로젝트 설치버전과 같다는 보장은 없다**. Postgres/PostGIS/pgRouting 버전과 overload는 동봉 SQL로 읽어야 한다. 구 블로그의 pgr_createTopology 의존은 피하고 OSM node ID로 topology를 만든 뒤 교차·보행 연결을 검증한다. upstream 4.0에서 여러 구 함수가 제거되었다. [Supabase pgRouting](https://supabase.com/docs/guides/database/extensions/pgrouting), [공식 releases](https://github.com/pgRouting/pgrouting/releases)

첫 DB 라우터는 `pgr_dijkstra(edges_sql,start_vid::bigint,end_vid::bigint,true)`와 `pgr_ksp(edges_sql,start_vid::bigint,end_vid::bigint,k::integer,true,false)` one-to-one 형태로 계획한다. 실제 schema/overload를 먼저 조회하고 호출한다. 비용 열은 id/source/target/cost/reverse_cost. 보행 가능한 arc의 비용은 **양수**로 유지하고 위험 페널티를 더한다. 음수 비용은 안전 보너스가 아니라 해당 방향 arc가 없는 의미로 쓰인다. `pgr_KSP` 후보가 모두 거의 같은 길일 수 있으므로 거리 상한·중복률 필터도 별도로 필요하다. 비용 최소와 실제 거리 최소는 다르며 UI에는 두 값을 구분한다. [Dijkstra family](https://docs.pgrouting.org/dev/en/dijkstra-family.html), [KSP category](https://docs.pgrouting.org/dev/en/KSP-category.html)

기존 자체 Python A* PoC와 pgRouting A*는 별개다. 경위도 degree 좌표와 m/초/위험 비용을 그대로 섞으면 admissible heuristic이 깨질 수 있다. DB 첫 구현은 Dijkstra로 비교 기준을 만들고, A*는 투영 m좌표·비용 하한에 맞춘 factor와 heuristic 검증 후 채택한다. Python 지오데식 A*도 heuristic이 실제 cost의 하한인지 비교해야 한다. 단순 거리와 독립적인 위험점수를 비용으로 더했다면 거리 기반 하한을 유지할 수 있지만 안전 보너스로 비용을 빼면 하한이 바뀐다. [A* family](https://docs.pgrouting.org/3.7/en/aStar-family.html)

## Kotlin·비회원·서비스 연결 결정

Supabase Kotlin client `supabase-kt`는 커뮤니티 유지관리 라이브러리이며 Data API/RPC 호출 가능. DB raw 접속정보를 앱에 넣지 않는다. 비회원 시설 조회는 허용한 공개 조회/RPC만 개방하고 즐겨찾기는 Room 권장. 앱 삭제/기기 변경 후 복원까지 필요하면 로그인 또는 anonymous Auth로 확장한다. anonymous Auth는 단순 anon key와 다르며 `authenticated` 역할의 사용자/JWT를 생성하고, 세션을 잃으면 같은 계정을 복원하지 못할 수 있다. [Kotlin 소개](https://supabase.com/docs/reference/kotlin/introduction), [RPC](https://supabase.com/docs/reference/kotlin/rpc), [Room](https://developer.android.com/training/data-storage/room), [anonymous Auth](https://supabase.com/docs/guides/auth/auth-anonymous)

Android에는 Supabase publishable key만 허용하고 secret/service_role/DB password는 서버에서만 사용한다. RLS와 grants는 시설 공개 읽기·사용자별 쓰기를 구분한다. TMAP REST 호출은 서버 endpoint로 모아 키와 일 호출예산을 보호한다. SDK 지도키는 클라이언트 인증 수단이므로 서버 secret처럼 숨길 수 있다고 가정하지 말고 제품이 제공하는 앱 제한/등록을 적용한다. 라우팅 endpoint는 시흥 bbox·최대 거리·K 상한·query timeout·rate limit를 둔다. 그래프 테이블 전체를 클라이언트에 공개하지 않는다. [API keys](https://supabase.com/docs/guides/getting-started/api-keys)

다음 실제 검증 3개가 끝나면 통합개발 GO로 올릴 수 있다: (1) 팀 TMAP 키로 보행 option=10 호출/지도 overlay 1회, (2) 팀 Supabase에서 verification.sql 결과와 toy Dijkstra/KSP 확인, (3) 파일럿 graph·시설 import 후 두 경로 비용/좌표/크기/응답시간 확인. 현재 작성된 SQL은 미실행이며 확장 활성화나 데이터 변경을 수행하지 않는다.

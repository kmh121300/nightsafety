# 겹친 안전시설 마커 UI 개선 및 종류별 개수 요약 적용 로그

작성일: 2026-11-08 · 최종 수정일: 2026-11-08 · 시간 기준: Asia/Seoul

## 1. 작업 배경 및 요구사항

- 사용자 요청에 따라 지도에서 마커가 겹쳤을 때(`FacilityCluster`) 표시되는 배지 아이콘과 클러스터 터치 시 열리는 팝업 UI를 더 직관적이고 깔끔한 카드형 디자인으로 개선함.
- 기존에는 겹친 마커를 누르면 개별 시설의 주소 목록(`CCTV · 경기도 시흥시 ...`)을 나열했으나, 주소 대신 시설 종류별 개수(`CCTV 2개`, `비상벨 1개`, `보안등 2개` 등)로 묶어서 요약 표시하도록 변경함.

## 2. 변경 내용

- **시설 종류별 그룹 요약 로직 추가 ([`FacilityCluster.kt`](../source/app/src/main/java/kr/ac/tukorea/nightsafety/FacilityCluster.kt))**
  - `FacilityKindGroup(kind, label, count, members)` 데이터 클래스 및 `summaryText`(`"$label ${count}개"`) 속성 추가.
  - `summarizeFacilityCluster(members)` 함수로 클러스터 내 시설을 `CCTV` → `비상벨` → `보안등` → `경찰` 순으로 그룹화하여 종류별 개수를 집계함.
  - `clusterSummaryTitle(members)` 함수로 클러스터 대표 제목을 `"CCTV 2개 · 비상벨 1개 (총 3개)"` 형태로 생성함.
- **겹친 마커 배지 아이콘 시각 개선 ([`FacilityMarkerIcons.kt`](../source/app/src/main/java/kr/ac/tukorea/nightsafety/FacilityMarkerIcons.kt))**
  - `facilityKindDrawableRes(kind)` 헬퍼 함수를 공개하여 다이얼로그 아이콘과 지도 마커가 동일한 벡터 리소스를 참조하도록 통일함.
  - `FacilityClusterIcons.forMembers(members)`에서 대표 시설 원형 마커 뒤에 겹침을 나타내는 보조 원형 링을 배치하고, 우측 상단에 흰색 테두리가 적용된 청록색 캡슐형 `+N` 배지(`#087F78`)를 렌더링하도록 개선함.
- **클러스터 요약 커스텀 다이얼로그 UI 추가**
  - [`ui_cluster_badge.xml`](../source/app/src/main/res/drawable/ui_cluster_badge.xml): 캡슐형 개수 배지 배경 추가.
  - [`dialog_facility_cluster.xml`](../source/app/src/main/res/layout/dialog_facility_cluster.xml): `이 위치의 안전시설` 헤더, `총 N개` 배지, 종류별 요약 부제(`CCTV 2개 · 비상벨 1개`), 그룹 카드 리스트 컨테이너, `닫기` 버튼을 포함한 둥근 카드형 다이얼로그 레이아웃 추가.
  - [`item_facility_cluster_row.xml`](../source/app/src/main/res/layout/item_facility_cluster_row.xml): 시설 종류 아이콘, `"CCTV 2개"` 요약 텍스트, `"눌러서 상세 정보 확인"` 안내 문구, 우측 개수 배지(`2개`)로 구성된 카드 행 레이아웃 추가.
  - [`MainActivity.kt`](../source/app/src/main/java/kr/ac/tukorea/nightsafety/MainActivity.kt): `showFacilityGroup`에서 `DialogFacilityClusterBinding` 및 `ItemFacilityClusterRowBinding`을 사용해 종류별 개수 카드를 표시하고, 각 카드를 누르면 `showFacilityKindGroup`을 통해 단일 시설 상세 또는 번호가 매겨진 다중 시설 상세(`[1] ... [2] ...`)를 표시하도록 연결함.
- **단위 테스트 추가 ([`FacilityClusterTest.kt`](../source/app/src/test/java/kr/ac/tukorea/nightsafety/FacilityClusterTest.kt))**
  - `summarizesOverlappingFacilitiesByKindCountInsteadOfAddresses` 테스트를 추가하여 겹친 시설들이 주소 대신 `"CCTV 2개"`, `"비상벨 2개"`, `"보안등 1개"` 형태로 정확히 집계되는지 검증함.

## 3. 검증 결과

- **검사 일시:** 2026-11-08 00:00~00:09 KST
- **대상 빌드:** `source/app/build/outputs/apk/debug/app-debug.apk`
- **단위 테스트 및 빌드:**
  - `.\gradlew.bat testDebugUnitTest assembleDebug` 실행 결과 `BUILD SUCCESSFUL` (단위 테스트 39개 전체 통과, 오류 0).
- **에뮬레이터 UI 검증 (`emulator-5556`):**
  - 새 디버그 APK 설치 및 `MainActivity` 실행 후 지도 위 겹친 시설 클러스터 마커(`+3`, `+7`)에 캡슐형 청록색 배지와 중첩 링이 정상 표시됨을 확인.
  - `+3` 클러스터 마커 터치 시 커스텀 다이얼로그(`이 위치의 안전시설`, `총 3개`, 부제 `CCTV 2개 · 비상벨 1개`, 카드 행 `CCTV 2개` 및 `비상벨 1개`)가 주소 나열 없이 깔끔하게 표시됨을 캡처로 확인.
  - 다이얼로그 내 `CCTV 2개` 카드 행 터치 시 `CCTV 2개` 상세 창(`[1]`, `[2]`)이 정상 열리는 것을 확인.
- **미검증 범위:**
  - 실제 물리 안드로이드 기기(실기기 GPS·해상도)에서의 최종 사용자 인수 및 현장 보행 검증은 별도 범위로 유지함.

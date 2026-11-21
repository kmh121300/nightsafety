# 네이버 지도 스타일 UI 전환 (풀스크린 맵 + 바텀시트) 검증 로그

작성일: 2026-11-06 · 시간 기준: Asia/Seoul

## 작업 개요
- **사용자 요청:** 기존 3단 분할(상단 검색-중앙 갇힌 지도-하단 스크롤) 레이아웃의 답답함과 비직관성을 개선하기 위해, 네이버 지도/카카오맵 스타일의 풀스크린 지도 및 하단 슬라이딩 바텀시트 구조로 전환.
- **적용 범위:**
  - XML 레이아웃 구조 전환 (`activity_main.xml`, `view_map_panel.xml`, `view_search_card.xml`, `view_result_panel.xml`, `view_toolbar.xml`).
  - Google Material 표준 `CoordinatorLayout` + `BottomSheetBehavior` 적용.
  - 상단 둥근 플로팅 검색 카드(`view_search_card.xml`, elevation 8dp).
  - 우측 컴팩트 플로팅 버튼 그룹(`location`, `preview`, `reset_map`).
  - 하단 슬라이딩 바텀시트(`controls_scroll`, 둥근 상단 모서리, 드래그 핸들 `—`, peekHeight 120dp).
  - 기존 백엔드, 데이터베이스(Room), TMAP SDK 연동 및 비즈니스 로직(RouteWorkflow 등) 100% 보존.

## 검증 내역
1. **빌드 검증:**
   - `./gradlew.bat assembleDebug` 빌드 성공 (오류 0).
   - `./gradlew.bat testDebugUnitTest` 단위 테스트 27개 전원 통과.

2. **에뮬레이터(`emulator-5556`, API 36.1) 실행 검증:**
   - 새 APK 설치 및 실행 확인.
   - **기본 화면:** 지도가 화면 전체(`[0,0][1080,2220]`)에 시원하게 깔리고 상단에 플로팅 검색 카드, 하단에 120dp 요약 바텀시트 정상 표시.
   - **경로 검색 동작:** [경로 검색] 클릭 시 정상적으로 서버 경로 탐색 수행 및 지도 선/마커 렌더링.
   - **바텀시트 제스처:**
     - 손가락으로 올리면(`STATE_EXPANDED`) 세부 점수(전체, 평균, 취약구간), 구간 범례, 주변 시설 카운트, 필터 체크박스, 하위 지표 구간 버튼 등이 부드럽게 펼쳐짐.
     - 손가락으로 내리면(`STATE_COLLAPSED`) 120dp 콤팩트 요약 카드로 접혀 지도가 화면 80% 이상 확보됨.
   - 캡처 결과물:
     - 기본 화면: `source/verification/naver_map_style.png`
     - 검색 후 접힌 상태: `source/verification/naver_map_collapsed.png`
     - 바텀시트 펼친 상태: `source/verification/naver_map_bottomsheet_expanded.png`

## 검증 범위 및 한계
- 본 작업은 모바일 UI 레이아웃의 모던화 및 에뮬레이터 검증이며, 실기기 GPS 수신 및 실도로 현장 보행 검증은 별도 과제입니다.

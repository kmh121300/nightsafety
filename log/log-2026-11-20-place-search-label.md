# 장소 검색 UI 문구 변경 — 2026-11-20

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 작업/검증 기준일: 2026-11-20 · 시간 기준: Asia/Seoul

## 변경 내용

사용자 요청에 따라 출발지/도착지 설정 다이얼로그에서 개발자/데이터 출처 용어인 `OSM` 표기를 사용자 친화적인 일반 표현으로 변경함.

- [`strings.xml`](../source/app/src/main/res/values/strings.xml#L42): `ui_place_query_hint` 값을 `"OSM 장소명 검색"` → `"장소 검색"`으로 변경
- [`RouteWorkflow.kt`](../source/app/src/main/java/kr/ac/tukorea/nightsafety/RouteWorkflow.kt#L98-L108):
  - 장소 조회 상태 메시지: `"OSM 장소를 찾는 중…"` → `"장소를 찾는 중…"`
  - 검색 결과 목록 다이얼로그 제목: `"OSM 장소 · 출입구 미검증"` → `"장소 · 출입구 미검증"` (출입구 미검증 안내는 유지)

## 검증 결과

- **검사 날짜 / 환경**: 2026-11-20 KST · Windows (`source/` 오프라인 Gradle 실행)
- **실행한 검사**:
  - `.\gradlew.bat testDebugUnitTest --offline` (통과, `BUILD SUCCESSFUL in 56s`)
  - `.\gradlew.bat installDebug --offline` (`Pixel_3a(AVD) - 15` / `emulator-5556` 새 `app-debug.apk` 빌드·설치 및 `MainActivity` 실행 확인)
- **미검증 범위**: 에뮬레이터/실기기 화면 자동 캡처 대조 및 전체 기능 회귀는 수행하지 않음.

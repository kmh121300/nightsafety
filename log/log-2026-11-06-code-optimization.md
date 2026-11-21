# 개발 로그: 2026-11-06 백엔드 및 안드로이드 앱 성능 최적화

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

## 1. 개요
* **목적**: 기능 계약·데이터 정합성·점수 계산 결과·DB 스냅샷 호환성을 100% 보존하면서, 서버 경로 응답 생성 및 초기화 시간 단축, 안드로이드 지도 렌더링 및 드래그 반응성 개선을 위해 7대 병목 지점을 최적화함.

## 2. 최적화 내역

### 2.1 백엔드 (`source/server/engine.py`, `source/server/database.py`)
1. **`point_score` 바운딩 박스 사전 필터링 및 불필요한 튜플 역전 제거**:
   * 25개 인접 격자 내 시설물에 대해 Haversine 삼각함수(`poc.hav`)를 호출하기 전에 위경도 차이(`abs(lat - f_lat) > 0.00091 or abs(lon - f_lon) > 0.00115`)로 100m 밖 시설물을 즉시 스킵하여, 서버 초기화 및 단위 테스트 실행 시간을 **32.35초 → 16.90초(약 48% 단축)**로 개선함.
2. **`public_route` 응답 생성 시 중복 공간 거리 재계산 제거**:
   * 세그먼트 생성 시 주변 시설물 목록(`_nearby_facilities`)을 사전 캐싱하고, DB 복원(`hydrate`) 시에도 첫 조회 시 캐싱 및 간선 내 시설물 부재 시 계산을 생략하여 매 응답마다 수백 회 반복되던 `point_score` 재호출을 제거함.
3. **`anchor` 및 `places` 전체 그래프 선형 탐색 최적화**:
   * `anchor()`에서 30m 반경 후보 노드를 위경도 박스로 1차 필터링하여 27,607개 전체 노드 삼각함수 계산을 수 개 노드로 축소함.
   * `places()`에서 `name` 태그 존재 여부를 선확인하고, 고정 보행 지점(`_explicit_nodes`)은 매칭 시에만 1회 계산 후 캐싱함.
4. **시설물 개수 집계 및 `deepcopy` 경량화**:
   * `facility_id -> facility_type` 해시맵(`self.facility_types`) 및 타입별 카운터(`self.type_record_counts`)를 캐싱하여 매 경로 생성 시 1,378개 전체 리스트 순회를 제거함.
   * `compare` 캐시 저장 및 `public_route` 변환 시 불필요한 전체 세그먼트/좌표 `copy.deepcopy()`를 얕은 복사 및 필수 메타데이터 복사로 대체함.

### 2.2 안드로이드 앱 (`PilotData.kt`, `TmapPilotMap.kt`, `PilotPreviewView.kt`, `MainActivity.kt`)
5. **`TmapPilotMap` 경로선(PolyLine) Dirty Check 적용**:
   * 시설물 필터 체크박스 토글 시 경로 데이터·선택 인덱스·취약구간 표시 여부가 바뀌지 않았으면 `removeAllTMapPolyLine()` 및 수백 개 세그먼트 폴리라인 재생성을 건너뛰도록 최적화함.
   * 마커 클릭 시 `facilitiesById` 해시맵으로 $O(1)$ 조회하도록 개선함.
6. **`PilotPreviewView.onDraw` 힙 객체 할당(DrawAllocation) 제거**:
   * 드래그·줌 프레임마다 수천 번 생성되던 `PointF`와 수십 번 생성되던 `Path` 객체를 제거하고, 단일 `linePath.reset()` 재사용 및 기본형(`Float`) 투영 함수(`projectX`, `projectY`), 삼각함수 상수 사전 계산으로 60fps 렌더링 시 GC 부하를 제거함 (Android Lint `DrawAllocation` 경고 해소).
7. **`PilotData` 필터 캐싱 및 `MainActivity` 재생성 시 재파싱 방지**:
   * `PilotData.visibleFacilities` 결과를 캐싱하고, 초기 파싱 시 라우트별 피처를 `groupBy`로 1회 분류함.
   * `MainActivity.loadData()`에서 `lastNonConfigurationInstance`에 파싱된 `PilotData`가 존재하면 백그라운드 Asset 4개 파일 I/O 및 JSON 재파싱을 즉시 건너뛰도록 개선함.

## 3. 검증 근거 (2026-11-06)
* **검사 환경**: Windows, Python venv, JDK 21 / AGP 9.4.0 / Gradle 9.7.1.
* **백엔드 단위 테스트**: `python -X utf8 -m unittest discover -s server -p "test*.py" -v` ➔ **24개 전체 통과 (16.898s)**.
* **도구 단위 테스트**: `python -X utf8 -m unittest discover -s tools -p "test*.py" -v` ➔ **13개 전체 통과 (0.042s)**.
* **Android 단위 테스트·Lint·빌드**: `gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug` ➔ **Android 단위 27개 전체 통과 (실패 0)**, **lint 오류 0 / 경고 41 (`DrawAllocation` 해소)**, **APK 빌드 성공**.
* **APK 해시 (SHA256)**: `2a759986fa3e1d4dc3aa8127412a1847d93d9802830c3f10e617defddcdfb4ed` (`source/app/build/outputs/apk/debug/app-debug.apk`).
* **미검증 범위**: 이번 작업은 알고리즘 결과와 UI/DB 계약을 유지한 내부 성능 최적화로, 새 APK의 에뮬레이터/실기기 UI 재실행, 실기기 GPS/권한, 현장 보행 검증, 사용자 최종 디자인 인수 및 운영 배포는 별도 미완료 상태로 유지함.

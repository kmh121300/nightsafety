# UI 정리 개발 검증

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자가 UI 정리와 개발 검증을 위임했으며 최종 디자인 검사는 나중에 직접 한다. 기존 Kotlin/XML·TMAP·Room 구조에 검색/지도/경로 비교/시설 영역과 가로/600dp 배치, 세 점수 카드, 읽기 쉬운 시설 상세와 자료 정보 창을 적용했다. 서버·DB·점수 정책·원본 자료는 변경하지 않았다.

## 대상과 환경

- 검사일: 2026-11-05. Windows, JDK21 / AGP9.4.0 / Gradle9.7.1, Android API35 Pixel_3a 임시 에뮬레이터, SwiftShader. 실제 태블릿 하드웨어 검증과 구분한다.
- APK: `app/build/outputs/apk/debug/app-debug.apk`.
- SHA256: `1b4d9a5e19eaa43174bbb8ebc864b44f60c671952ff81d8a9713946ee6a3e6ad` (ANR 수정본).
- 로컬 서버는 기존 PostGIS snapshot을 로드했다. health ready, DB startup_snapshot/configured/verified true, bundle `local-mvp-3types-v1`, graph `osm-bb4586cbb583`, scoring `mvp-3types-20-5-k2050100-q05-equal-v1`. 이번 작업에서 새 DB import나 전체 API 대조를 반복하지 않았다.

## 확인 결과

- `gradlew.bat testDebugUnitTest lintDebug assembleDebug`: 최종 빌드 성공, Android25개 실패0, lint 오류0/경고24.
- `python -X utf8 -m unittest discover -s tools -p 'test_*.py'`: 도구7개 통과. 출력의 fixed UI failure는 실패 기록 보존을 검사하는 의도된 fixture다.
- 시설 상세 회귀의 초기2개 실패를 수정했다. 코드 검토에서 경찰시설 후보 표시 누락1건을 발견, 새 회귀1개 실패 후 목록·필터·상세의 후보 자격을 보완했다. 작동 여부 안내를 되살리지 않았다.
- 초기 API27 전용 테마 속성 lint 실패를 values-v27로 분리해 수정했다. 점수 카드는 확대 글꼴에 따라 높이가 늘어난다.
- 임시 Android의 부팅/시스템 서비스 미준비로 최초 설치/UI 검사가 시작되지 못했다. 후속 중복 AVD 실행은 잠금 오류로 종료됐다. 기존 AVD 자료를 초기화하지 않고 이전 검증용 임시 이미지의 관리 가능한 실행 세션에서 최종 APK 설치 성공.
- 최초 UI APK는 지도 준비/시설1,381개, 기본 검색 후보3개/정식 지표, anchor 검색의 연결 안내/세 점수, 하위 지표 구간 창/overlay 토글까지 통과했으나 전체8개는 통과하지 못했다. [12:42 ADB 오류](../android-2026-11-05_123635_815055/failure.md), [12:49 저장 창/좌표 조작 실패](../android-2026-11-05_124311_435170/failure.md), [13:00 앱 ANR](../android-2026-11-05_125354_058424/failure.md)를 보존한다.
- ANR 원인은 MotionEvent 응답5019ms 초과, main 스레드의 `onCheckedChanged → refresh → syncFacilityOverlays → TMapView.addTMapMarkerItem → wgs84ToScreen`이었다. 변경 없는 마커는 이미 재사용했지만 필터 복원 시 대량 추가가 동기 실행됐다. 프레임당8개 갱신, 실제 반영 상태 기준 재계산, 새 필터/지도 종료 취소로 수정했다. 회귀3개 포함25개와 읽기 전용 추가 코드 검토 통과. 마커는 순차 반영되며 원본 개수/점수는 바뀌지 않는다.
- 자동 검사 도구도 스크롤 후 클릭 좌표 재조회와 버튼 밖 가장자리 제스처로 보완했다. 관련 회귀2개 실패→수정→통과. ANR 자체를 도구 실패로 취급하거나 성공으로 덮지 않았다. 수정 APK 실제 DB 기반 UI 재검증 중이다.

## 13:37 KST 재부팅 전 상태

위 APK의13:21 [기본 UI8개 전체](../android-2026-11-05_130904_166965/integration-ui.md)가 통과했고 설치 해시도 일치했다. 자료 정보의 실제3개 기준일, 보안등 주소/관리기관/공유 기록/출처와 경찰시설 OSM 후보 자격도 확인했다. 앞 절의 진행 중 문구는 이 결과 이전 기록이다.

세로·가로·태블릿 크기(1200×1920/density240)·글꼴1.3 캡처는 확보했으나, **같은 PID에서 단일 회전 후 도착지 이름이 유지된 채 점수가9.1→—로 유실**되는 문제를 재현했다. 첫 추가 캡처에는 입력 초기화 장면도 있었다. 화면 배치 캡처 성공을 상태 보존 통과로 취급하지 않는다.

확대 글꼴의 헤더 부제목 잘림·저장 목록 줄바꿈을 확인했다. `view_toolbar.xml` 높이/폭을 가변으로 바꿨으나 **미빌드이며 현재 APK에는 포함되지 않는다.** 회전 문제와 보완된0거리 검사는 미완료다. 사용자 재부팅 요청으로 중단하고 [인계 문서](../../../log/log-2026-11-05-ui-reboot-handoff.md)에 환경/재현/다음 시작점을 기록했다. 전체 UI 완료와 사용자 최종 디자인 검사는 미완료다.

캡처: [세로 점수](portrait-metrics.png), [자료 정보](data-info.png), [보안등 상세](lamp-detail.png), [경찰 후보 상세](police-candidate-detail.png), [가로—상태 문제 있음](landscape.png), [태블릿 크기](tablet-size.png), [확대 글꼴—헤더 문제 있음](tablet-large-font.png), [회전 재현](rotation-state-debug.png).

실기기 GPS/권한·현장 보행·명세 전체 개별 TC·운영 배포는 이번 검증에 포함하지 않는다.

관련: [UI 로그](../../../log/log-2026-11-05-ui-polish.md), [전체 로드맵](../../../ROADMAP.md), [전일 점수 검증](../mvp-scoring-2026-11-04/verification.md).

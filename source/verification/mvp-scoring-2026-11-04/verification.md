# MVP 3유형 점수·DB·앱 검증

작성일: 2026-11-04 · 최종 수정일: 2026-11-04 · 시간 기준: Asia/Seoul

환경: Windows/Python3.10.11/JDK21/Gradle9.7.1, 실제 PostGIS safenight/startup_snapshot. Pixel_3a Android15 API35/emulator-5556, 별도 TEMP 사용자 이미지·headless SwiftShader·3072MB. 기존 AVD 자료 보존. Git 커밋은 미기록(작업 폴더는 Git 저장소 아님). SDK/Gradle·실제 DB 검사는 권한 확장 환경에서 실행했다. 비밀 설정·연결 문자열·SDK/logcat 원문은 기록하지 않았다.

최종 APK SHA256: `973ebc2d10dff824cbc98bbc6cdf074d7a84d400c47b7a569ad7d1adb6d703fc`, 설치 APK 바이트와 일치 확인. main/debug22개 파일 집계 SHA256 `5846507098ceb49e4d297e7dda7c95e2f8e5058a6b6e892a6161b384595beaac`(정렬 상대경로 `/`·NUL·바이트·NUL, 비밀 설정/생성 BuildConfig 제외).

| 버전 | 값 |
| --- | --- |
| graph | osm-bb4586cbb583 |
| facility | pilot-15b18eb4d217 |
| scoring | mvp-3types-20-5-k2050100-q05-equal-v1 |
| routing | dijkstra-3types-risk-v1 |
| active_bundle | local-mvp-3types-v1 |

## 2026-11-04 실행 결과

source에서 Python 명령은 `.\.venv\Scripts\python.exe -X utf8`로 실행했다.

| 검사 | 결과 |
| --- | --- |
| 서버 | `-m unittest discover -s server -p 'test*.py' -v`: 최종24개 통과, 종료코드0(47.971s) |
| 도구 | `-m unittest discover -s tools -p 'test*.py' -v`: 5개 통과. 증거 보존 테스트 내부의 의도된 FAIL 문자열은 실제 suite 실패가 아님 |
| Android | `gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug --offline --console=plain`: 종료코드0, 최종20개·실패0·오류0, lint 오류0/경고45. 기존 inset deprecated 컴파일 경고 포함 |
| 변환 | `tools/prepare_security_lights.py`: 원본9,265행·파일럿870행·고유좌표533개 유지. 원본 CSV 보존, 새 asset/감사의 eligibility/notice 반영 |
| DB import | `server/postgis.py --apply`: 새 append-only bundle commit. 시설1,378·노드27,607·간선8,208·구간22,256 |
| DB 복원/API | `tools/db_smoke.py --verify-import`: 종료코드0. 모든 노드/태그·방향 간선·시설/속성·표본/구간/비용 동등성, 도형/SRID·RLS5개, HTTP health/config/facilities/places/compare/evaluate/0거리 통과 |
| DB 보호 | 재가져오기 행수 불변, invalid geometry import 전체 rollback 및 기존 bundle 불변 통과 |
| 실행 서버 | configured=true/verified=true, 새 startup_snapshot, 시설 API1,378행 |

## 실제 API 지표

23시 OSM 명시 anchor 대학 옆문–정왕역 주변 보행 지점 compare 응답 success. CCTV/비상벨/보안등 모두 ready, missing 없음, 각 route/score complete. 물리적 역 출구 자체의 연결 검증과 구분한다.

| 최종 역할 | 거리(m) | 전체 | 평균 | 하위10% |
| --- | ---: | ---: | ---: | ---: |
| fast | 1572.4006 | 9.1208 | 13.0298 | 0 |
| balanced | 1579.2583 | 9.5980 | 13.7115 | 0 |
| safe + pedestrian | 1933.4494 | 12.8359 | 18.3371 | 0 |

세 정식 지표가 null이 아니고 safe 점수가 fast 이상이다. 동일 가중치·unknown 실험계수0.5·40/70 등급 등 기존 초기 모델을 사용한 결과이며 현장 보정 검증과 다르다.

## 실패 재현·검토

새 서버 회귀4개·보안등 eligibility·앱 정식 필드/계산 기준2개는 기존 동작에서 실패 후 수정했다. 읽기 전용 코드 검토의 Important2건(앱 generated_profiles 대신 최종 roles 사용, 잘못된 조명 유형/도형을 정상0건으로 처리하던 경계)도 앱 회귀1개와 서버 두 입력 subtest가 실패한 뒤 수정해 최종 suite 통과. 정상 빈 원천은 ready/0건, 미확보 보안등 파일은 partial로 구분한다.

검토 전 APK `684ec5526ce85f0725f95b911bf66dcf5ebd2944047f8991c7834be2e1da43c8`의 첫 UI 실행은 지도 준비 후 최종 수정본 설치를 위해 중단했으며 전체 통과로 세지 않는다.

## UI 및 남은 범위

최종 APK의 [DB 기반 전체 UI8개](../android-2026-11-04_230056_403348/integration-ui.md)는 23:00:56~23:09:47 KST 종료코드0으로 통과했다. 지도/시설1,381개·기본 미완결 검색/정식 지표·명시 anchor 연결·취약 구간·필터·Room 저장/재시작/오프라인/수정/최종 역할 재조회/삭제를 확인했다. 두 캡처를 직접 시각 검토했으며 지도 영역(40,350)-(1040,1040)의 주황 RGB(205,85,15)는 ON1,969/OFF0픽셀이다. 정식 지표·구간 등급과 범례·기준일/출처·TMAP 로고가 표시되고 시설 작동 미확인/점수 제외 문구는 없다.

별도 보안등 상세 검사 종료코드0. 필터를 순차 적용해 보안등만870개로 만든 뒤 [상세 캡처](../android-2026-11-04_231018_217812/security-light-scoring-detail.png)의 기준일2026-02-24·조명 지표·출처/원문을 확인했다. visible UI 문자열에 작동·점등 미검증·점수 제외가 없는지 assertion하고 전체 필터1,381개로 복원했다. 단발 검사 스크립트는 TEMP의 safenight_detail_check_20261104.py다.

`tools/zero_route_smoke.py --serial emulator-5556` 종료코드0. 두 입력에 같은 명시 anchor를 선택해 거리/시간0·시설지표 미산출·경로선 없음과 앱 정상 표시를 [0거리 캡처](../android-2026-11-04_231401_674781/integration-zero-route.png)에서 시각 확인했다. API의 0거리 정식 지표 null과 일치한다.

위 캡처4개를 직접 검토했다. 과거 정책의 점수/저장 결과·검증 기록은 보존한다.

실기기 GPS/위치 권한·기기 성능·현장 보행·명세 전체 TC·운영 배포·시흥 전체 확대는 이 검사로 완료 처리하지 않는다.

관련: [개발 로그](../../../log/log-2026-11-04-mvp-scoring.md), [정책](../../../md/night-safety-mvp-scoring-policy-ko.md), [로드맵](../../../ROADMAP.md).

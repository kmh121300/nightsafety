# 지도 길게 누르기·보행 지점 보정 검증

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 시간 기준: Asia/Seoul

## 구현 범위와 의미

TMAP/로컬 지도 길게 누르기→출발지/도착지 메뉴→가까운 활성 graph node 보정→선택 좌표/보정 좌표/거리 확인→`이 지점으로 경로 검색`으로 기존 입력/검색/endpoint 핀 흐름에 연결했다. 취소하면 좌표를 반영하지 않는다. 보정 거리는 입력 이름에도 남는다. 로컬 미리보기는 GestureDetector와 현재 fit/zoom/pan의 좌표 역변환을 사용하고, 일반 시설 탭과 드래그/확대 동작을 유지한다.

`POST /v1/places/snap`은 파일럿 내부 좌표만 받고 활성 graph node 중 가장 가까운 점을 선택한다. 원래 좌표와 보정 좌표·gap_m·connector_status를 반환한다. 원래 점과 graph 간 실제 보행 연결은 승인하지 않는다. 기존 compare.anchor의30m 제한과 파일럿 범위는 변경하지 않았다. 명시적으로 보정한 node를 출발·도착으로 재선택해 경로를 구한다. 보정 간격은 경로 거리/ETA/안전점수에 합산하지 않으며 직선 connector를 만들지 않는다.

edge상의 최근접 점/임시 edge 분할, 장애물/출입구 검증, 다른 component까지 연결, 파일럿 밖 서비스 확대는 미지원이다. 가까운 node를 골라도 다른 입력과 graph가 단절돼 있으면 기존 경로 없음 처리를 따른다. 파일럿 안에서 별도 보정 거리 상한은 두지 않고 보정 거리를 확인 후 선택한다. DB·그래프·점수 정책·버전·SDK 키는 변경하지 않았다.

## 대상과 환경

- 대상: 이번 구현 직후 source 코드 및 `app/build/outputs/apk/debug/app-debug.apk`(44,726,330바이트).
- APK SHA-256: `8b5ae22b7efb87c3381da82885ca43d5e24875cb08513f948f5a53ef27602acc`.
- Windows / JDK21.0.11 / Gradle9.7.1 / compileSdk36. 서버 Python3.10.11 venv.
- API35 Pixel_3a AVD emulator-5556 host GPU, 일반1080×2220/440dpi 및 작은720×1280/360dpi.
- 새 서버는 DB snapshot을 읽어8767포트에서 실행. [health](db-health.json)에서 database.configured/verified=true, mode=startup_snapshot 확인. 기기8765→호스트8767 adb reverse. 이전 포트 서버와 구분한다. DB 쓰기/재가져오기는 하지 않았다.

## 2026-11-20 실제 검사 결과

1. 구현 전 새 회귀3개를 실행해 미지원 snap 메서드/HTTP404 실패를 확인했다. 구현 후 동일 회귀3개 통과. 실제 graph node만 선택, 원래30m 제한, 파일럿 밖/NaN/bool 입력, HTTP 성공/422, graph 불변 검사를 포함한다.
2. 서버 전체 단위27개 통과(55.993초), [실행 결과](../../../log/map-long-press-2026-11-20-server-tests.txt). 실제 DB 쓰기 테스트가 아니다.
3. 새 APK assembleDebug/testDebugUnitTest/lintDebug 종료코드0 / BUILD SUCCESSFUL(3분18초), Android41개 성공/실패0/오류0, lint 오류0·경고50. [실행 결과](../../../log/map-long-press-2026-11-20-gradle.txt). 추가2개는 보정 응답의 좌표/거리 파싱과 음수/비유한/지원 범위 밖/error 응답 거절 검사다.
4. DB API [보정 응답](far-snap.json): 원래 점에서 약70.79m 떨어진 node를 반환, connector_status=unverified_gap. 원래 점 그대로 compare 요청은422 유지. 파일럿 밖/bool 좌표422. [결과](api-result.json).
5. 동일 해시 설치 APK에서 [TMAP·로컬 지도 통합 PASS](../android-2026-11-20_113754_259440/map-long-press-result.json). TMAP 출발지 약25m 보정, 로컬 도착지 약50m 보정 후 서버 검색 완료. [TMAP 메뉴](../android-2026-11-20_113754_259440/tmap-menu.png), [보정 확인](../android-2026-11-20_113754_259440/tmap-snap.png), [로컬 메뉴](../android-2026-11-20_113754_259440/local-menu.png), [보정 확인](../android-2026-11-20_113754_259440/local-snap.png) 캡처 검토.
6. [입력/검색 결과](../android-2026-11-20_113754_259440/selected-inputs.png): 출발25m/도착50m 보정 이름, 출발·도착 핀, 빠른 경로742m/10.3분/5.3점 표시 확인. 보정된 양쪽 node 사이 결과이며 원래 클릭점까지의 경로가 아니다.
7. 같은 APK의 로컬 시설 마커 짧게 누르기: [시설 종류별 팝업](facility-tap.png) 정상 표시(CCTV3/비상벨1). 길게 누르기 뒤에도 일반 탭이 유지됨을 확인했다.
8. 작은 화면 [보정 확인 창](small-snap-confirm-ready.png) 검토. 지도 드래그 직후 메뉴가 뜨지 않음, 이어 길게 누르면 메뉴/약63m 보정 확인 창 표시, 취소 후 초기화 완료 출발·도착 이름 동일 유지 확인. [전후 값과 결과](cancel-check-ready.json). 완료 후 화면 설정 원복 및 앱 재실행.

## 중간 실패와 재검사 구분

- 첫 원거리 API 표본은 실제 gap5.416m라 `>30m` 검사에 실패했다. 다른 파일럿 표본을 비교해70.79m 사례로 원거리 동작을 검사했다. 최초 표본/검사 결과는 api-result.json에 기록했다.
- 첫 지도 자동 검사는 TMAP 선택/검색 후 최소화된 상단의 map_status를 읽으려다 실패했다. [당시 결과/캡처](../android-2026-11-20_113603_957553/map-long-press-result.json)를 보존한다. 상태 문구 확인 전에 상단을 펼치도록 검사 절차만 수정한 후 양쪽 지도 PASS. 앱 코드의 실패를 성공으로 덮은 것이 아니다.
- 첫 작은 화면 취소 검사에서 `Cancel changed endpoint` 불일치가 났고 당시 비교 전후 문자열은 미기록이다. [그때 시설 탭 기록](additional-ui.json)과 [당시 확인 창](small-snap-confirm.png)을 보존한다. 초기화 완료 입력까지 기다리고 비교 전후 문자열을 기록한 재검사에서는 일치했다. 초기 로딩과 비교 시점의 경합 가능성이 있으나 첫 전후 값이 없어 원인을 확정하지 않는다. 이 재검사 사이 앱 코드는 바꾸지 않았다.

## 미검증 범위

실기기/GPS/OEM·TalkBack 실제 실행·현장 접근성·대규모 지역/그래프 성능·전체 명세 인수는 미검증이다. 작은 화면은 확인 창/취소/드래그를 검사했으며 전체 검색 흐름은 일반 화면의 양쪽 지도에서 검사했다. 원래 점→node 보정은 실제 통행 가능성 증거가 아니다. 기존 시스템 상태바 겹침/대비 등은 이번 변경으로 해결하지 않았다.

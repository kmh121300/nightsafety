# 밤길 지킴이 — Android + 로컬 경로 서버

작성일: 2026-10-16 · 최종 수정일: 2026-11-21 · 시간 기준: Asia/Seoul

**2026-11-20 지도 길게 누르기:** TMAP/로컬 지도에서 길게 누르고 출발지 또는 도착지를 선택하면, 별도 확인 창 없이 가까운 등록 보행 지점으로 자동 보정하고 바로 경로를 검색합니다. 입력 이름에 보정 거리를 표시하고 경로 핀을 반영합니다. 거리/시간/점수는 보정된 보행 지점부터/까지이며 원래 누른 위치까지의 실제 통행 가능성을 보증하지 않습니다. 파일럿 밖은 지원하지 않습니다. 서버에 `POST /v1/places/snap`이 추가되어 서버 재시작이 필요합니다. 기존 경로 API의30m 제한·그래프·DB·점수 정책은 유지합니다. [작업 로그](../log/log-2026-11-20-map-long-press.md).

**2026-11-07 최신 시설 제목:** CSV 행 번호 대신 종류+주소를 표시한다. 도로명→지번→주소 정보 없음 순서, 원본508개 대조로 앱의 CCTV/비상벨 주소를 보완했다. 단위38·빌드·두 지도 목록/상세 확인, lint 오류0/경고41. [검증/대조 근거](verification/facility-addresses-2026-11-07/verification.md), [최신 APK](delivery/2026-11-07-facility-addresses/README.md). 실기기/최종 UI 인수는 별도다.

**2026-11-07 최신 시설 묶음:** 겹친 시설을 대표 마커+총개수로 표시하고 터치하면 목록→상세를 연다. TMAP/로컬 공통, 확대/필터에 따라 재계산한다. 단위36·빌드·두 지도 목록/상세·필터 복구/native 확대 확인, lint 오류0/경고41. [검증/미검증 범위](verification/facility-clusters-2026-11-07/verification.md), [최신 APK](delivery/2026-11-07-facility-clusters/README.md). 실기기/최종 UI 인수는 별도다.

**2026-11-07 비상벨 후속 수정:** 빨간 원형/흰 종·좌우 울림 표시로 변경했다. 공유 vector1개 변경, 새 APK 빌드·API35 TMAP/로컬 캡처 확인. [검증 범위](../log/log-2026-11-07-bell-icon.md), [최신 APK](delivery/2026-11-07-bell-icon/README.md). 아래 단위/lint/전체 UI 기록은 각각 당시 APK 근거다.

**2026-11-07 최신 시설 아이콘:** CCTV 카메라·비상 호출 버튼·보안등 가로등·경찰 방패를 흰28dp 배지로 바꿨다. TMAP/로컬 캡처와 두 지도 상세·CCTV 필터 복구, 단위31·빌드 통과, lint 오류0/경고40. [검증/미검증 범위](verification/facility-icons-2026-11-07/verification.md), [최신 APK](delivery/2026-11-07-facility-icons/README.md). 밀집 지점의 아이콘 겹침은 남으며 실기기/최종 UI 인수는 별도다.

**2026-11-07 최신 경로 표시 개선:** 선택 경로 파랑/흰 테두리·회색 후보·출발/도착 핀·지도/목록100m 주변 시설 표시를 적용했다. 점수와 경로 좌표는 유지한다. 단위31/도구14·서버 UI8·small/standard/pane3개·빌드 통과, lint 오류0/경고39. [검증/캡처](verification/route-display-2026-11-07/verification.md), [최신 APK](delivery/2026-11-07-route-display/README.md). 실제 도로 정합성/실기기·사용자 최종 UI 인수는 별도다.

**2026-11-06 최신 UI 수정:** 지도 버튼과 저장 목록/상태바 겹침·접힌 요약 잘림·투명 제목 가독성을 수정했다. 공통48dp 지도 버튼 행, 실제 요약 높이 기반 시트/안전 손잡이, 흰 툴바 카드·탐색 영역 보호를 적용했다. 단위27/도구13·API35 small/standard/pane3개 회귀·빌드 통과, lint 오류0/경고38. [수정 후 캡처/검증 범위](verification/ui-sheet-fixes-2026-11-06/verification.md), [최신 APK](delivery/2026-11-06-ui-sheet-fixes/README.md). 실기기/사용자 최종 UI·전체 기능 인수는 별도다.

**2026-11-06 전체화면 추가 당시:** 기존 전체 보기 초기화 버튼을 전체화면으로 바꿨다. 누르면 상단·검색·결과 패널을 숨기고 지도를 확장하며 화면 복귀/시스템 뒤로로 돌아온다. 지도 view와 결과를 유지한다. 최종 APK small/pane TMAP/로컬4개 흐름 통과. [검증 범위](verification/fullscreen-2026-11-06/verification.md), [최신 APK](delivery/2026-11-06-fullscreen/README.md). 이전 전체 UI/단위 기록은 각각 당시 APK·동일 코드 근거로 구분한다. 실기기/사용자 최종 UI 인수는 미완료다.

**2026-11-06 ViewBinding 전환 당시:** 앱 소유 화면·패널·경로 행·입력 대화상자 전체를 ViewBinding으로 전환했다. 단위27·도구13·전체 UI 기능8개·small/pane 검사를 새 APK에서 통과했다. lint 오류0/경고41. [최신 검증](verification/viewbinding-2026-11-06/verification.md), [최신 APK](delivery/2026-11-06-viewbinding/README.md), [실기기 절차](DEVICE-TEST.md). 아래 과거 검증은 각각 당시 APK 근거다. 실제 GPS·사용자 최종 UI·전체 명세 인수는 미완료다. 고정 글꼴/세로·점수·DB/Room 정책은 유지한다.

전체 진행 상태와 다음 작업은 [전체 로드맵](../ROADMAP.md), 문서 목록은 [문서 안내](../README.md)를 확인합니다. **2026-11-05 22:09 기준 고정 글꼴 APK의 전체 UI8개와 정상→0거리 검사가 API35에서 통과했고, 후속 위치 수정 APK의 오류/권한 지정8개도7+1회 분리 검증했습니다.** 검색/필터·Room 저장/재시작/오프라인/수정/재조회/삭제를 확인했으며, 실기기 GPS·위치 권한과 명세 전체 인수/현장/배포는 미완료입니다. [최신0거리 결과](verification/android-2026-11-05_210638_044884/verification.md), [최신 전체 UI8개](verification/android-2026-11-05_215835_067057/integration-ui.md).

Kotlin/XML 앱, TMAP 실제 지도, Python OSM 탐색 서버와 Room 즐겨찾기를 연결한 파일럿입니다. PostgreSQL/PostGIS의 safenight 스키마에 저장한 데이터를 서버 시작 시 읽어 사용합니다. 서비스 범위는 한국공학대학교–정왕역 주변이며 시흥 전체가 아닙니다.

2026-11-05 사용자 선택으로 MVP는 **세로 고정·앱 글꼴 배율1.0 고정**을 사용합니다. 시스템 큰 글꼴은 앱에 반영하지 않으며, 글꼴 설정만 변경할 때 열린 화면을 재생성하지 않습니다. 고정 글꼴 당시 APK 빌드·단위25개·lint 오류0/경고26, API36 배율 변경/큰 글꼴 새 시작/열린 창 유지 및 API35 정상 점수→0m/0분·세 점수 `—` 초기화·이전 경로선 제거가 확인됐습니다. 당시 검사 도구9개 통과. 서버와5556은 연결 상태로 유지합니다. 일반 창 크기/프로세스 복원·API36.1 입력 중 앱 화면 소실 원인·실기기/최종 사용자 UI 검사는 남습니다. [0거리 검증](verification/android-2026-11-05_210638_044884/verification.md), [글꼴 검증](verification/font-lock-2026-11-05_162308/verification.md), [연결·0거리 로그](../log/log-2026-11-05-zero-route.md). 이전 [세로 고정/태블릿 크기](verification/portrait-lock-2026-11-05_155732/verification.md)와 [전체 UI8개](verification/android-2026-11-05_130904_166965/integration-ui.md)는 각각 당시 APK의 근거로 보존합니다.

2026-11-04 [MVP 정책](../md/night-safety-mvp-scoring-policy-ko.md)을 서버·DB·앱에 실제 적용했습니다. 자료 기간 차단을 제거하고 보안등을 정식 점수에 포함했으며 시설 작동 미확인 안내를 제외했습니다. 서버24개·도구5개·Android20개, 새 APK 빌드/lint 오류0·경고45, 새 DB 전체 복원/API 대조·재가져오기/rollback과 최종 기본 UI8개가 통과했습니다. [최신 검증](verification/mvp-scoring-2026-11-04/verification.md), [새 APK 전체 UI](verification/android-2026-11-04_230056_403348/integration-ui.md).

2026-11-03 15시 보안등 추가본의 서버18개·도구5개·Android14개 검사와 DB 재활성화 후 보안등870행의 실제 import·복원/API 대조가 통과했습니다. 22시 전체 UI 재검사에서 시설 전체 재생성 ANR을 진단해 변경 시설만 SDK에 갱신하도록 수정했고, 회귀3개를 더한 Android17개·빌드/lint 및22:32 KST 최신 DB 기반 기본 UI8개가 통과했습니다. 중간 ANR·ADB 실패와 과거 지도 준비 실패는 당시 근거로 보존합니다. [보안등 검증](verification/security-lights-2026-11-03/verification.md), [DB 재검증](verification/database-security-lights-2026-11-03.md), [최신 전체 UI](verification/android-2026-11-03_222620_934204/integration-ui.md).

같은 날15:11 KST [보안등 범위 UI 검사](verification/android-2026-11-03_150042_324475/security-lights-ui.md)는 표시·필터·단독 목록/상세·로컬 서버 경로 검색이 통과했습니다. 실제 DB 기반 전체 UI 인수와는 별도입니다.

## 현재 기능

- TMAP 인증·실제 배경지도·시설/경로 표시. 키 없는 로컬 좌표 미리보기도 유지.
- 출발/도착 좌표 입력·로컬 OSM 장소 검색·교환·서버 경로 조회.
- 빠른/시설 비용/균형/보행선 정책 후보 생성·중복 제거·우회시간 상한.
- CCTV·비상벨·보안등 정식 전체/평균/취약 지표, 구간 등급 색/범례와 정확한 하위10% 길이 표시·상세.
- Room 즐겨찾기 저장·이름/유형 수정·삭제·재시작 후 오프라인 복원·최신 재검색.
- 시설 필터·상세, 위치 권한 거부·시간 초과, 이전 요청 취소·최신 결과 반영.
- 보안등870행의 조명 점수·마커·필터·출처/기준일/원문 상세. 시설 작동 미확인 안내 제외.

## 실행

Android Studio에서 이 source 폴더를 엽니다. Android SDK36과 JDK17 이상이 필요합니다. 검증 환경은 JDK21 / AGP9.4.0 / Gradle9.7.1입니다.

첫 번째 PowerShell 창에서 프로젝트 전용 Python 환경을 준비하고 서버를 실행합니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r server/requirements.txt
.\.venv\Scripts\python.exe -X utf8 server/app.py
```

localhost:8765에서만 대기합니다. source/.env.local의 DATABASE_URL이 비어 있지 않으면 safenight의 최신 버전 데이터를 읽어 메모리에 복원하고 Dijkstra로 탐색합니다. DB 읽기 실패 시 서버를 시작하지 않습니다. 환경변수와 설정 파일 모두에 DATABASE_URL 값이 없으면 기존 로컬 OSM/시설 파일로 실행합니다. DB 변경은 서버 재시작 후 반영되며 기존 연구 산출물은 덮어쓰지 않습니다. 설정 파일과 .venv는 Git 제외 대상입니다.

다른 창에서 빌드하고 대상 기기를 연결합니다.

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
$taskAdb = "$env:LOCALAPPDATA/Android/Sdk/platform-tools/adb.exe"
& $taskAdb devices
& $taskAdb -s emulator-5554 reverse tcp:8765 tcp:8765
& $taskAdb -s emulator-5554 install -r app/build/outputs/apk/debug/app-debug.apk
```

emulator-5554는 대상 기기 시리얼로 바꿉니다. USB 기기도 adb reverse로 연결할 수 있습니다. APK는 app/build/outputs/apk/debug/app-debug.apk입니다.

팀원은 전체 저장소 구조를 유지하고 source 폴더에서 아래 예시를 복사할 수 있습니다. 기존 설정이 있으면 덮어쓰지 않습니다. TMAP 키가 비어 있으면 로컬 지도 미리보기로 실행하며, DB 설정이 비어 있으면 동봉 자료로 서버를 실행합니다. 실제 키/DB 정보는 각자 로컬 파일에만 입력하고 커밋하지 않습니다.

```powershell
if (-not (Test-Path -LiteralPath local.properties)) { Copy-Item local.properties.example local.properties }
# DB 사용 시에만 선택적으로 준비합니다.
if (-not (Test-Path -LiteralPath .env.local)) { Copy-Item .env.example .env.local }
```

local.properties 설정 예시입니다. Android Studio에서 각자 Android SDK 경로를 지정합니다. 이 파일은 저장소에서 제외되며 실제 키를 채팅·로그에 기록하지 않습니다.

```properties
sdk.dir=C\:/Users/사용자/AppData/Local/Android/Sdk
TMAP_APP_KEY=팀에서_발급받은_앱키
API_BASE_URL=http://127.0.0.1:8765
```

개발용 HTTP는 debug의 localhost/127.0.0.1/10.0.2.2에만 허용합니다. 배포 서버는 HTTPS가 필요합니다.

## 사용 흐름

1. 기본 대학 옆문→정왕역 출구 입력으로 경로 검색. 실제 출구 연결은 미완결입니다.
2. 도착지의 OSM 검색어 anchor 또는 보행으로 그래프 지점을 명시적으로 선택할 수 있습니다. 역 주변 보행 지점은 실제 출구 자체와 다릅니다.
3. 후보 선택 후 하위 지표 구간을 누르면 시설지표의 하위10% 길이가 주황색으로 표시됩니다. 선택 경로의 구간 등급과 범례도 표시됩니다.
4. 최신 검색 후 즐겨찾기로 저장합니다. 오프라인 복원은 과거 결과로 표시하며 변경한 선호유형과 최신 자료는 재조회로 확인합니다.
5. 조작 버튼은 지도 아래 패널을 스크롤해서 이용합니다.

장소 검색은 파일럿 OSM 노드 이름 검색이며 TMAP REST POI·시흥 전체 검색이 아닙니다. Room에는 사용자/OSM endpoint와 자체 서버 snapshot만 저장합니다. TMAP 응답 장기 보관과 이동 이력 저장은 하지 않습니다.

## 데이터 해석

CCTV270행 + 비상벨238행 + 보안등870행 + OSM 경찰시설 점2개/건물1개 =1,381기록이며 고유 설치지점 수가 아닙니다. 보안등은 고유좌표533개이며 공유 좌표의 행은 중복 여부 미확인 상태로 보존합니다. 경찰시설3객체는 번들 overlay이고 서버 점수에서 제외됩니다. 서버 시설 API는1,378행이며 앱 시설 표시는 고정 asset 기반입니다.

CCTV 기준일2026-01-20, 비상벨2026-01-22, 보안등2026-02-24입니다. 자료 날짜에 따른 점수 사용기간 상한은 없습니다. 필수 유형은 cctv/emergency_bell/security_lamp이며 모두 준비되면 정식 safety_score/average_safety/weak_safety와 구간 등급을 계산합니다. 보행 anchor가 완결된 후보에서 safe/balanced 역할을 선택합니다. 자료 미확보는 정식 지표 null·공통 부분 지표로, 거리0은 모든 점수 null로 처리합니다. 구 snapshot의 부분/과거 상태는 유지합니다.

보안등 재생성: source에서 `.\.venv\Scripts\python.exe -X utf8 tools/prepare_security_lights.py`를 실행합니다. 원본 CSV는 보존하고 별도 `pilot-security-lights.geojson` 및 실행일/원본 해시별 감사 JSON을 생성합니다. 좌표 누락53행·범위 밖8,342행은 마커에 넣지 않습니다. [2026-11-03 검증](verification/security-lights-2026-11-03/verification.md).

complete는 선택한 그래프 지점까지 연결됐다는 뜻이며 실제 야간 통행·시설 작동 검증과 다릅니다. 정왕역 실제 출구와12.56m 연결은 아직 미검증입니다. 시간은 거리/1.2m/s이며 신호대기·경사는 반영하지 않습니다.

## 테스트·증거

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s server -p "test*.py" -v
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tools -p "test*.py" -v
.\gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
.\.venv\Scripts\python.exe -X utf8 tools/integration_smoke.py --serial emulator-5554
```

UI 검사는 대상에 최신 APK가 설치되고 로컬 서버가 실행된 환경이 필요합니다. tools/smoke_test.py도 같은 현재 통합 검사를 실행합니다.

새 UI 보고서/실패 기록/캡처는 `verification/android-YYYY-MM-DD_HHMMSS_마이크로초/`에 보존합니다. 과거 고정 경로의 성공 기록을 덮어쓰지 않습니다. 보고서의 날짜와 APK 해시를 함께 확인합니다. 시험 AVD에서 Android 홈 화면·부팅·화면 켜짐 상태부터 확인하고, 이전 AVD 사용자 자료를 지우는 대신 별도 임시 이미지로 구분할 수 있습니다.

- [TMAP 실인증 검증](verification/tmap-auth.md)
- [2026-10-16 당시 통합 UI 검사](verification/integration-ui.md)
- [외부 시설 자료 재확인](verification/data-source-review-2026-10-16.md)
- [2026-10-27 최신 자료원·사용자 도움 필요 항목](verification/data-source-review-2026-10-27.md)
- [서버 API·PostGIS 준비](server/README.md)
- [2026-10-26 실제 DB 통합 검증](verification/database-integration-2026-10-26.md)
- [2026-10-27 최신 앱 UI8개 통과](verification/android-2026-10-27_001901_382784/integration-ui.md)
- [2026-11-03 수정 APK·최신 DB 기반 기본 UI8개 통과](verification/android-2026-11-03_222620_934204/integration-ui.md)
- [새 빌드·실행 환경 분리와 검증 한계](verification/android-r4-2026-10-26.md)

초기 로컬 미리보기 결과인 verification/README.md는 첫 단계의 과거 검증 기록입니다.

## 외부 조건이 필요한 남은 작업

2026-11-03 15:31 KST 사용자 DB 재활성화 후 시설1,378개(CCTV270·비상벨238·보안등870), 노드27,607개·방향별 간선8,208개·구간22,256개 저장과 전체 DB/API 동등성 검증이 통과했습니다. 같은 버전 재가져오기 행수 불변·실패 rollback도 확인했습니다. 이전 접속 실패는 당시 기록으로 보존합니다. 탐색은 시작 시 DB snapshot을 읽은 메모리 Dijkstra이며 pgRouting 실행은 아닙니다. 실행 중 서버에는 재시작 후 새 bundle이 반영됩니다.

시흥 가로등 전체 좌표·이용조건, 최신 시설 자료, 교문·출구·보도·횡단·시설 접근성 현장 조사, 실제 기기 GPS 허용 흐름과 배포 서버 운영은 남아 있습니다.

2026-10-27 사용자는 기존 CCTV/비상벨 CSV가 최신 자료임을 확인했습니다. 재요청하지 않습니다. 2026-11-03 시흥 보안등 원본9,265행과 다운로드 출처를 확보하고 파일럿870행의 표시·DB 반영을 완료했습니다. 이용조건 상세·전수성·스마트가로등 요구 충족·실제 점등은 미확인입니다. CSV 기준일과 공식 점수 null 정책은 유지합니다.

OSM: © OpenStreetMap contributors / ODbL — https://www.openstreetmap.org/copyright
시설 원본 CSV의 다운로드 페이지·재사용 조건 확보는 배포 전에 필요합니다. TMAP 로고를 숨기지 않습니다.

## 문서 변경 이력

| 날짜 | 변경 |
| --- | --- |
| 2026-10-26 | 전체 로드맵 연결, 최신 UI 미완료 상태와 과거 검증 날짜를 명시함. DB 실행 안내 변경은 같은 날짜의 DB 로그 참조. |
| 2026-10-27 | 현재 소스의 빌드와 DB 기반 에뮬레이터 전체 흐름 통과를 반영. 날짜별 증거 보존/도구 회귀 실행 안내와 실기기 미검증을 추가함. |
| 2026-10-27 | R5 공개 원천/샘플 확인과 최신 시흥 자료 확보 대기를 구분하고 새 조사 기록을 연결함. |
| 2026-10-27 | 기존 CCTV/비상벨이 최신이라는 사용자 확인을 반영. 기존 CSV 유지·재요청 제외, 조명 자료 확보로 다음 작업을 정리함. |
| 2026-11-03 | 보안등870행 표시·필터·상세와 재생성/감사 안내 추가. 최신 단위/빌드 통과, 실제 DB 접속·전체 UI 실패와 과거 성공을 구분함. |
| 2026-11-03 | 시설 전체 재생성 ANR 수정 후 단위17개·빌드/lint·최신 DB 기반 기본 UI8개 통과. 이전 실패 보존, 실기기/현장/명세 전체 인수는 별도 유지. |
| 2026-11-04 | MVP 점수 정책·명세1.2 반영과 현재 코드의 기존180일/부분 지표 동작을 구분. 새 정책 구현·검증은 미완료. |
| 2026-11-04 | 새 정책을 서버/DB/앱에 실제 적용. 3유형 정식 지표·구간 등급·완결 경로 추천, 서버24/도구5/Android20·새 APK/lint·DB 대조·전체 UI8개·상세/0거리 검증 통과. |

2026-11-04 실제 적용 검증: 새 append-only3유형 bundle과 최종 APK를 사용했습니다. [적용 검증](verification/mvp-scoring-2026-11-04/verification.md). 이전 날짜의 표시 전용/점수 null 기록은 당시 결과입니다.

2026-11-05 22:09 KST 사전 검사1번 완료: 최신 APK 전체 UI8개·지도 캡처 확인 통과. 코드/APK 변경 없이 검사, 서버/5556 유지. [검사 로그](../log/log-2026-11-05-latest-ui-flow.md), [최신 전체 UI](verification/android-2026-11-05_215835_067057/integration-ui.md). 다음은 오류·복구/권한 모의 검사입니다.

2026-11-05 22:43 KST 사전 검사2번 완료: 첫 위치 수신 SDK crash를 일반 위치 마커/재중심으로 수정하고 검색0건의 로딩 상태 잔류를 수정했습니다. 새 APK 단위25개·도구11개·빌드 통과, lint 오류0/경고27, 설치 해시 일치·오류/권한 지정8개7+1회 검증·설정 복원 확인. 이전 UI8개는 당시 APK 근거로 보존하며 새 APK에 동일 전체8개를 재실행한 것은 아닙니다. [종합 검증](verification/error-recovery-2026-11-05/verification.md), [작업 로그](../log/log-2026-11-05-error-recovery.md). 다음은3번 API36.1 현상 분리·명세 필수 누락 대조입니다.

반복 검사(실기기 제외): `python -X utf8 tools/error_recovery_smoke.py --serial emulator-5556`. 마지막 OS 위치 OFF 항목만 재검사할 때 `--only-location-off`를 추가합니다. 권한/위치 설정을 일시 변경하고 finally에서 복원하므로 결과의 cleanup_errors도 함께 확인합니다.

2026-11-05 사전 검사3번: 경로별 CCTV·비상벨·보안등 고유 수를 비교 패널에 추가했고, null은 —·원천 미확보 이유로 표시합니다. 지도 필터와 무관합니다. 새 APK SHA256 `b50ae48ddaaa76ea933ad9f86821963f2f3d0aa3e9132f11b994012f2886084d`, Android27/도구12·빌드 통과, lint 오류0/경고31. API36.1에서 입력 반복·수치·부분/복구·0거리5개를2+3회 같은 PID로 확인했습니다. 과거 소실 원인은 미확정이며 전체 명세 인수 완료가 아닙니다. [최신 검증](verification/spec-audit-2026-11-05/verification.md), [38개 대조](verification/spec-audit-2026-11-05/functional-matrix.md). 다음은4번 화면/설치 준비입니다. 기존 전체 UI/오류 권한 검사는 각각 당시 APK 근거로 보존합니다.

최신 시설 수/부분 자료·입력 검사: `python -X utf8 tools/spec_audit_smoke.py --serial emulator-5558`. 선택한 에뮬레이터의 reverse만 임시 fixture 서버로 바꾸고 종료 시 복원하므로 실기기에는 사용하지 않습니다. API35/5556과 API36.1/5558 모두 최신 APK로 설치 해시 확인, 서버/에뮬레이터 유지 상태입니다.

2026-11-06 사전 검사4번 완료: 작은 높이 지도 버튼은 가로48dp 행, 가용 높이h720dp 이상은 기존 세로 배치를 사용합니다. 두 화면/본문·스크롤·긴 목적지·빈/오류/복구3개 묶음과7개 지도 상태가 통과했습니다. 빌드/lint 오류0·경고33·도구13개 통과. Android27개는11월5일 단위 근거로 보존합니다. [최신 화면 검증](verification/screen-install-2026-11-06/verification.md), [검증 APK·해시](delivery/2026-11-06/README.md), [USB 설치·실기기 표](DEVICE-TEST.md). 현재 서버와API35/5556 유지. 다음은 실제 휴대폰 검사/사용자 최종 UI 판단이며 명세 전체·현장·운영 완료가 아닙니다.

# 밤길 지킴이 전체 로드맵

작성일: 2026-10-26 · 최종 수정일: 2026-11-21 · 상태 기준일: 2026-11-20 · 시간 기준: Asia/Seoul

전체 개발 단계, 현재 구현·검증 상태와 다음 작업의 기준 문서입니다. [기능 명세](md/night-safety-functional-specification-ko.md)는 요구사항, [실행 안내](source/README.md)는 실행 방법, 날짜별 계획·로그·검증 문서는 근거를 담당합니다. 최초 문서 정리 때에는 기존 기록을 대조했으며 이후 새 실행 결과는 실제 검증 날짜와 근거를 붙여 갱신합니다.

## 현재 위치

- **2026-11-21 GitHub 팀 공유용 제외 규칙 보완:** root/source ignore 보완, 빈 설정 예시/실행 안내 추가. 실제 키 포함 ZIP1개·APK10개 제외 및 필수 소스 포함·임시 Git 추가 검사 통과, 검사한 알려진 비밀값/패턴 일치0건. 업로드/과거 원격 이력/재배포 조건은 미검증. 앱 구현·인수 상태와 기준일11-20 유지. [검증](source/verification/github-share-2026-11-21/verification.md), [로그](log/log-2026-11-21-github-share-preparation.md).

- **2026-11-20 지도 선택 자동 보정·검색 전환 완료:** 사용자 요청으로 보행 지점 확인 창 없이 방향 선택 직후 보정·검색. 보정 거리 표시와 입력 검증 유지. 새 APK 빌드/Android41·lint 오류0/경고50, API35 TMAP·로컬 자동 검색 및 DB snapshot 확인. 실기기/전체 인수는 미완료. [최신 검증](source/verification/map-auto-snap-2026-11-20/verification.md), [로그](log/log-2026-11-20-map-long-press.md).

- **2026-11-20 지도 길게 누르기 구현·지정 검증 완료:** TMAP/로컬 지도 출발·도착 메뉴, 가장 가까운 활성 보행 node 보정/거리 확인 후 검색·핀/입력 반영. 서버27/Android41·빌드/lint 오류0·경고50, DB API70.79m 보정 및 API35 양쪽 지도 검색·작은 화면 취소 확인. 기존30m compare 제한·파일럿 범위·DB/점수 유지. edge 임시 분할·현장 연결·실기기/전체 인수는 미완료. [검증/캡처](source/verification/map-long-press-2026-11-20/verification.md), [로그](log/log-2026-11-20-map-long-press.md).

- **2026-11-20 지도 길게 누르기 가능성 조사 당시:** SDK의 long-press 좌표 콜백과 서버30m 거절/파일럿 제한을 확인했다. 당시에는 미구현이었으며 후속 구현·검증은 위 최신 기록을 따른다. [당시 조사 로그](log/log-2026-11-20-map-long-press-feasibility.md).

- **2026-11-20 최소화 버튼 크기·위치 보완 완료:** 사용자 요청으로 저장 목록 왼쪽32dp 버튼/16dp 아이콘으로 변경, 터치48dp 유지. 새 APK 빌드·단위39·lint 오류0/경고50, API35 일반/작은 화면 배치·클릭 왕복 확인. [검증/캡처](source/verification/top-card-small-button-2026-11-20/verification.md), [로그](log/log-2026-11-20-top-card.md).

- **2026-11-20 상단 카드 최소화·지정 검증 완료:** `−` 최소화/오른쪽 위 사방 화살표 확대 및 지도 출처 위치 연동. 새 APK 빌드·단위39·lint 오류0/경고50, API35 일반/작은 화면 최소화·확대/입력·경로 요약 보존/전체화면 복귀·상하 독립성 통과. 실기기/전체 인수는 미완료. [검증/캡처](source/verification/top-card-2026-11-20/verification.md), [로그](log/log-2026-11-20-top-card.md).

- **2026-11-20 숨김 상태 복귀 손잡이 보완·지정 검증 완료:** 사용자 피드백으로 경로 내용은 숨기고 남색 바/밝은 손잡이는 남기도록 수정. 새 APK 빌드·단위39·lint 오류0/경고50, API35 일반 전체 제스처·작은 화면 손잡이/스와이프 복귀·지도 버튼 비겹침 확인. 실기기/전체 인수는 미완료. [최신 검증](source/verification/three-stage-handle-2026-11-20/verification.md), [로그](log/log-2026-11-20-three-stage-sheet.md).

- **2026-11-20 하단 패널 세 단계 구현·지정 검증 완료:** 완전 숨김→기존 요약→상세, 하단 스와이프/클릭 복귀 및 상세에서 내려 요약 정지 적용. 새 APK 빌드·단위39·lint 오류0/경고50, API35 일반/작은 화면 제스처·전체화면 복귀·DB 기반 검색 확인. 상단 UI 문제/실기기/전체 인수는 남는다. [검증](source/verification/three-stage-sheet-2026-11-20/verification.md), [로그](log/log-2026-11-20-three-stage-sheet.md).

- **2026-11-20 UI 담당자 수정본 병합:** 병합 전574파일 ZIP 백업/해시 대조 완료. UI17개 및 어두운 테마 호환 styles2개 반영. 새 APK 빌드·단위39개·lint 오류0/경고50 통과. DB 재활성화 후 스냅샷 로딩·API35 DB 기반 검색 확인, 상태바 대비·작은 화면 부제/출처 문제 발견. 실기기/전체 인수 미완료. [화면 검증](source/verification/ui-merge-2026-11-20/verification.md). [로그](log/log-2026-11-20-ui-merge.md).

- **2026-11-08 겹친 시설 마커 UI 개선 및 종류별 개수 요약 적용·검증 완료:** 사용자 요청으로 겹친 마커 터치 시 개별 주소 목록을 나열하는 대신 시설 종류별 개수(`CCTV 2개`, `비상벨 1개` 등)로 그룹화해 보여주는 카드형 커스텀 다이얼로그(`dialog_facility_cluster.xml`)와 캡슐형 `+N` 클러스터 배지 아이콘을 적용했다. 단위 테스트 39개·빌드 통과 및 에뮬레이터(`emulator-5556`) 클러스터 다이얼로그/상세 열기 캡처 검증 완료. [로그](log/log-2026-11-08-cluster-kind-ui.md). 실기기/전체 인수는 별도다.

- **2026-11-07 시설 종류/주소 표시 적용·지정 검증 완료:** 행 번호 대신 도로명→지번→주소 없음 제목을 공통 목록/상세에 적용했다. 원본508개 행/좌표/기준일 대조 후 앱 자료 주소2필드만 보완하고 exporter에 보존했다. 단위38·빌드·TMAP/로컬 목록/상세 확인, lint 오류0/경고41. [검증/대조/캡처](source/verification/facility-addresses-2026-11-07/verification.md), [최신 APK](source/delivery/2026-11-07-facility-addresses/README.md), [로그](log/log-2026-11-07-facility-address-titles.md). 원본 ID/좌표/점수/DB 유지, 실기기/전체 인수는 별도다.

- **2026-11-07 겹친 시설 묶음 구현/지정 검증 완료:** TMAP/로컬에서 대표 아이콘+총개수(+2/+3), 터치 목록→시설 상세를 적용했다. 화면 확대/필터/경로 변경에 맞춰 다시 묶으며 기존100m 표시·점수/원본/DB/Room을 유지한다. 단위36·빌드·두 지도 목록/상세·필터 복구·native 확대 확인, lint 오류0/경고41. [검증/캡처](source/verification/facility-clusters-2026-11-07/verification.md), [최신 APK](source/delivery/2026-11-07-facility-clusters/README.md), [로그](log/log-2026-11-07-facility-clusters.md). 실기기/최종 UI/전체 인수는 별도다.

- **2026-11-07 비상벨 종 아이콘 적용:** 사용자 피드백에 따라 빨간 원형/흰 종·좌우 울림 표시로 공통 vector를 수정했다. 새 APK 빌드11s·API35 TMAP/로컬 캡처·설치 해시 확인. 단위/lint/전체 UI는 리소스 변경에서 반복하지 않았다. [로그/검증](log/log-2026-11-07-bell-icon.md), [최신 APK](source/delivery/2026-11-07-bell-icon/README.md). 실기기/최종 UI 인수는 별도다.

- **2026-11-07 시설 아이콘 마커 구현/지정 검증 완료:** CCTV 카메라·비상 호출 버튼·보안등 가로등·경찰 방패28dp 공통 vector를 TMAP/로컬에 적용했다. 빌드/단위31·lint 오류0/경고40·두 지도 상세 열기/필터 회귀 통과. [검증/캡처](source/verification/facility-icons-2026-11-07/verification.md), [최신 APK](source/delivery/2026-11-07-facility-icons/README.md), [로그](log/log-2026-11-07-facility-icons.md). 밀집한 지점의 마커 겹침은 남고 실기기/사용자 최종 UI 인수는 별도다.

- **2026-11-07 경로 표시 개선/에뮬레이터 지정 검증 완료:** 선택 경로 파랑/흰 테두리·옅은 회색 후보·출발/도착 핀·지도/목록100m 주변 시설·native 카메라 여백 맞춤을 적용했다. 점수/원본 좌표/DB/Room은 유지한다. 최종 APK 단위31/도구14·서버 UI8·화면3프로필·빌드 통과, lint 오류0/경고39. [검증/캡처](source/verification/route-display-2026-11-07/verification.md), [최신 APK](source/delivery/2026-11-07-route-display/README.md), [로그](log/log-2026-11-07-route-display.md). 실제 도로 정합성/실기기·사용자 최종 UI/전체 인수는 미완료.

- **2026-11-06 캡처 UI3개 수정·에뮬레이터 검증 완료:** 공통48dp 지도 버튼 행으로 상단 겹침 해소, 실제 요약 높이 기반 peek/maxHeight·탐색 영역 보호로 잘림/손잡이 충돌 해소, 흰 툴바 카드로 가독성 보완. 최종 APK 단위27/도구13·빌드/lint 오류0·경고38·small/standard/pane3개 회귀 통과. [검증/수정 후 캡처](source/verification/ui-sheet-fixes-2026-11-06/verification.md), [최신 APK](source/delivery/2026-11-06-ui-sheet-fixes/README.md), [로그](log/log-2026-11-06-ui-sheet-fixes.md). 실기기·사용자 최종 UI/전체 기능 인수는 별도.

- **2026-11-06 22:53 KST 변경 UI 캡처 검토 완료, 수정 필요:** 현재 APK/API35/host GPU에서 지도·시트 드래그·전체화면/복귀를 관찰했다. 상단 버튼/저장 목록/상태바 겹침·접힌 요약 잘림·투명 제목 가독성 문제를 확인. h720dp 지도 variant에 이전 버튼 배치가 남아 있음. 코드 수정/전체 인수는 하지 않았다. [현재 캡처/발견 사항](source/verification/ui-review-2026-11-06/verification.md), [로그](log/log-2026-11-06-ui-capture-review.md).

- **2026-11-06 14:05 KST 네이버 지도 스타일 UI 전환(풀스크린 맵 + 슬라이딩 바텀시트) 완료:** 사용자 승인에 따라 기존 3단 분할 레이아웃을 네이버 지도/카카오맵 형태의 모던 UI로 전환함. `CoordinatorLayout` + Google Material 표준 `BottomSheetBehavior`를 적용하여 지도를 전체 화면에 100% 렌더링하고, 상단에는 둥근 플로팅 검색 카드를, 하단에는 120dp 콤팩트 요약에서 슬라이딩으로 상세 점수와 필터가 펼쳐지는 바텀시트를 배치함. 기존 백엔드, DB, Tmap 연동 및 단위 테스트 27개 100% 통과(오류 0), 에뮬레이터(emulator-5556) 설치 및 실행/제스처 검증 완료. [검증 로그](log/log-2026-11-06-naver-map-ui.md).

- **2026-11-06 12:55 KST 정왕역–한국공학대 1캠퍼스 정문 에뮬레이터 E2E 통합 검증 완료:** 사용자 요청으로 에뮬레이터(emulator-5556)에서 출발지를 정왕역, 도착지를 한국공학대학교 1캠퍼스 정문으로 설정하여 경로 검색 및 지도 전체화면/줌 동작을 검증함. OSM 장소 검색의 영문 별칭(`tukorea`, `gate` 등) 및 30m 이내 보행 앵커 필터링 보강으로 `한국공학대학교 1캠퍼스 정문 (보행 지점)`을 명시 지원함. 빠른 경로 1,942m/27.0분, 안전점수 12.4점(평균 17.6점, 취약 0.0점, CCTV 17/비상벨 17/보안등 51) 정상 산출 확인. 전체화면 확장 시 툴바·검색카드·결과패널 숨김 및 화면 복귀/지도 렌더링 확인. [검증 로그](log/log-2026-11-06-jeongwang-tukorea-e2e.md).

- **2026-11-06 지도 전체화면 구현/에뮬레이터 검증 완료:** 사용자 요청으로 기존 중심/zoom 초기화 버튼을 전체화면 확장으로 변경. 화면 복귀/뒤로로 복귀, 패널 숨김·검색 결과 보존. 최종 APK small/pane TMAP/로컬4개 통과, 일반 화면은 동일 DEX 직전 문구 APK 근거. 빌드/lint 오류0·경고41, 단위27/도구13 근거 확인. [검증](source/verification/fullscreen-2026-11-06/verification.md), [최신 APK](source/delivery/2026-11-06-fullscreen/README.md), [로그](log/log-2026-11-06-map-fullscreen.md). 실기기/최종 사용자 UI 인수는 미완료.

- **2026-11-06 사용자 요청 ViewBinding 전환 완료:** 메인·공통 패널·경로 행·입력 dialog3개 전환, 직접 findViewById 제거. 새 APK 단위27/도구13·전체 UI 기능8개·small/pane 통과, lint 오류0/경고41. [최신 검증](source/verification/viewbinding-2026-11-06/verification.md), [최신 APK](source/delivery/2026-11-06-viewbinding/README.md), [로그](log/log-2026-11-06-viewbinding.md). 실기기/최종 UI/전체 명세 인수와 구분한다.

- **실기기 연결 전 우선순위:** 사용자는 기기 없이 할 수 있는 MVP 준비를 먼저 마친 뒤 휴대폰을 연결하기로 했다. 1번 최신 APK 전체 검색/필터/Room 흐름은2026-11-05 22:09 KST API35에서8개 통과했다. 2번은 첫 위치 수신 crash·검색0건 상태 잔류를 수정하고 새 APK의 오류/권한 지정8개를7+1회 분리 검증해22:43 KST 완료했다. [종합 결과](source/verification/error-recovery-2026-11-05/verification.md), [로그](log/log-2026-11-05-error-recovery.md). 3번의 API36.1 조사·38개 기능 대조와 경로 시설 수 누락 보완을 수행했다. 새 APK 단위27/도구12·빌드 통과, lint 오류0/경고31. API36.1 지정5개2+3회는 같은 PID로 통과했으나 과거 소실 원인/명세 전체 인수는 미완료다. [검증](source/verification/spec-audit-2026-11-05/verification.md), [38개 대조표](source/verification/spec-audit-2026-11-05/functional-matrix.md). 2026-11-06 4번 작은/일반 화면·긴 목적지·빈/오류/복구 검사와 APK·해시·설치/실기기 검사표 준비를 마쳤다. 작은 화면 지도 버튼 잘림을 수정했고 빌드/lint 오류0·경고33·도구13·화면3묶음/지도7상태 통과. [검증](source/verification/screen-install-2026-11-06/verification.md), [설치 APK 묶음](source/delivery/2026-11-06/README.md), [휴대폰 연결/검사표](source/DEVICE-TEST.md). 다음은 실제 기기 연결·GPS/제조사 검증과 사용자 최종 UI 판단이다. [최신 전체 UI](source/verification/android-2026-11-05_215835_067057/integration-ui.md), [작업 로그](log/log-2026-11-05-latest-ui-flow.md). 실제 GPS·제조사별 UI/성능·현장은 기기 연결 이후/별도 검증이다. [기기 연결 전 검사 순서](log/log-2026-11-05-pre-device-checks.md).

- **2026-11-05 21:12 KST 연결·0거리 검사 완료:** DB snapshot 서버와 API35 에뮬레이터5556을 연결하고 최신 고정 글꼴 APK의 정상 숫자 점수→동일 anchor의0m/0분/세 점수 `—` 초기화를 확인했다. 이전 경로선 제거도 캡처 확인. 0거리 API의 지표null/geometry·구간·간선 없음 및 도구9개 통과. 서버와5556은 연결 상태로 유지한다. 초기 시스템/런처 창과 API36.1 입력 중 앱 화면 소실은 실패 근거로 보존하며 후자의 원인은 미확정이다. 실기기·최신 Room 전체 흐름·최종 사용자 UI/명세 인수는 남는다. [작업 로그](log/log-2026-11-05-zero-route.md), [0거리 UI](source/verification/android-2026-11-05_210638_044884/verification.md), [API](source/verification/zero-route-api-2026-11-05/verification.md).

- **2026-11-05 앱 글꼴 고정 적용:** 사용자 선택으로 앱 내부 글꼴 배율을1.0으로 고정했다. fontScale 변경만 Activity에서 처리해 열린 창을 유지한다. 빌드·단위25개·lint 오류0/경고26 통과. API36에서 시스템 배율0.85/1.3/2.0과 큰 글꼴 상태 새 시작에도 제목/부제 크기 동일, 자료 정보 창 유지/본문 확인·출발도착 설명 보존·시스템 설정 복원 통과. 시스템 큰 글꼴은 앱에 반영하지 않는 MVP 한계가 있다. 일반 창 크기/프로세스 재생성 복원·추가0거리·실기기/최종 사용자 UI 인수는 남는다. [글꼴 고정 로그](log/log-2026-11-05-font-lock.md), [최신 APK 검증](source/verification/font-lock-2026-11-05_162308/verification.md).

- **2026-11-05 세로 고정 적용:** 사용자가 MVP의 가로 회전을 막는 방식을 선택했다. MainActivity portrait와 API36 대화면 호환 설정을 적용하고 헤더 가변 크기 수정도 새 APK에 반영했다. 빌드·병합 Manifest 검사·lint 오류0/경고26 및 API36 휴대폰/태블릿 크기 모사의 방향 검사6개 통과. 회전 점수 복원은 고친 것이 아니라 MVP 우선 범위에서 제외한 상태다. 창 크기/글꼴 변경 시 상태 복원·0거리 추가 검사·최종 사용자 UI·실기기 인수는 남는다. [세로 고정 로그](log/log-2026-11-05-portrait-lock.md), [새 APK 검증](source/verification/portrait-lock-2026-11-05_155732/verification.md).

- **2026-11-05 재부팅 전 일시 중단:** UI 정리와 대량 마커 추가 ANR 수정 APK의 Android25개·도구7개·빌드/lint 오류0/경고24 및13:21 기본 UI8개가 통과했다. 추가 화면 검사에서 **회전 후 점수 유실**과 **확대 글꼴 헤더 잘림**을 발견했다. 헤더 XML만 추가 수정했으며 아직 빌드하지 않았다. UI 전체 완료/사용자 인수는 미완료다. 사용자 재부팅 요청으로 중단하며 **[재시작 인계 문서](log/log-2026-11-05-ui-reboot-handoff.md)를 먼저 읽고 회전 상태 보존부터 이어간다.** DB/점수 정책은 유지한다. [UI 로그](log/log-2026-11-05-ui-polish.md), [검증](source/verification/ui-polish-2026-11-05/verification.md).

- **완료된 검증:** 2026-11-04 새 정책의 서버24개·도구5개·Android20개, lint 오류0/경고45·새 APK 빌드, 새3유형 점수 DB import/복원/API 대조, 최종 DB 기반 기본 UI8개 통과. [적용 검증](source/verification/mvp-scoring-2026-11-04/verification.md), [전체 UI](source/verification/android-2026-11-04_230056_403348/integration-ui.md). 과거 근거는 해당 날짜의 기록으로 보존한다.
- **남은 실기기 작업:** R4 GPS·위치 권한 검사. 사용자는 집에 GPS 지원 Android 태블릿이 있다고 설명했으나 모델/OS·연결·실제 수신은 미확인이다. 호환되는 Android 실기기(휴대폰/태블릿)를 USB 디버깅으로 연결해 검사한다. 에뮬레이터 통과와 실기기 인수를 구분한다. [R4 검증 기록](source/verification/android-r4-2026-10-26.md).
- **태블릿 없이 진행한 R5:** **사용자는 기존 CCTV2130행(2026-01-20)·비상벨1851행(2026-01-22) CSV가 최신 자료라고 확인했다.** 재요청하지 않는다. 2026-11-03 보안등9,265행을 확보하고 파일럿870행/고유좌표533개의 서버/API·앱 마커/필터/상세를 구현했다. 좌표 누락53행·범위 밖8,342행을 감사 기록에 남기며 공유 좌표 행은 보존한다. 사용자 제공 출처 URL은 기록했고 이용조건·유형/현장 검증은 남는다. [보안등 검증](source/verification/security-lights-2026-11-03/verification.md). 공식 점수 정책은 유지한다.
- **2026-11-03 15시 검사:** 서버18개·도구5개·Android14개 통과, lint 오류0/경고44, 새 APK 빌드 통과. 보안등 없는 baseline과 전체 간선 비용·점수 표본·구간·토폴로지 동일 확인. 15:31 KST DB 재활성화 후 보안등870행 import·전체 DB/API 대조 통과. 최초 접속 실패와 지도 상태 문구 대기 [실패 기록](source/verification/android-2026-11-03_144825_157655/failure.md)은 보존한다. 최신 앱 검증은22:32 결과를 따른다.
- **2026-11-03 15:11 보안등 화면 검사:** 명시적 로컬 파일 서버에서 ON/OFF1,381→511→1,381, 보안등 단독870개 목록·상세·경로 검색 통과. 실제 DB 기반 전체 UI/실기기 인수와 구분한다. [완료 기록](source/verification/android-2026-11-03_150042_324475/security-lights-ui.md).
- **2026-11-03 15:31 DB 재검증:** 사용자 DB 재활성화 후 보안등870행을 포함한 새 bundle import·복원/API 전체 대조 통과. 시설1,378·노드27,607·간선8,208·구간22,256. 재가져오기 행수 불변과 실패 rollback 통과. 앞선 접속 실패는 당시 기록이며 현재 차단 조건에서 해소됐다. [DB 결과](source/verification/database-security-lights-2026-11-03.md).
- **아직 완료 아님:** 실기기 GPS/권한·성능, 명세 모든 개별 TC, 실제 야간 보행, 운영 배포와 시흥 전체 확대. 3유형 정식 점수와 완결 anchor 경로 safe/balanced 선택은 구현·기본 검증 완료다.
- **2026-11-03 22시 R4 재검사:** 취약 구간 토글의 전체 시설 재생성 ANR을 확인해 변경 시설만 갱신하도록 수정했다. 최종22:32 전체 UI8개 통과. 중간 수정본의 ADB 실패는 보존한다. [작업 로그](log/log-2026-11-03-r4-ui.md), [최종 결과](source/verification/android-2026-11-03_222620_934204/integration-ui.md). 다음은 실기기 GPS/권한이며 현재 기본 통합 검사에 사용자 추가 작업은 없다.
- **2026-11-03 R6 정책 논의:** 사용자 요청으로 UI 개선·실기기 검사에 앞서 점수 정책을 검토한다. MVP 정책안에서 '현재 시설 작동 여부 미확인' 문구를 제외하고 출처·기준일을 표시한다. 자료 허용기간 삭제·보안등 조명 지표 채택은 후속 설계 대상이며 아직 코드/명세에 적용하거나 점수를 활성화하지 않았다. [정책 기록](log/log-2026-11-03-r6-policy.md).
- **2026-11-04 정책 확정:** 자료 기간 상한 제거·CCTV/비상벨/보안등3유형·공공시설 기반 안전지표 명칭·출처/기준일·시설 작동 미확인 안내 제외를 명세1.2에 반영했다. 문서 단계 이후 같은 날 실제 구현/검증도 진행했다. [정책](md/night-safety-mvp-scoring-policy-ko.md), [정책 작업 로그](log/log-2026-11-04-r6-policy.md).
- **2026-11-04 실제 적용 완료:** 서버/DB/앱에 보안등 포함 정식 전체·평균·취약 지표, 구간 등급과 완결 경로 추천을 연결했다. 새 append-only bundle과 최종 APK의 전체 UI8개 통과. 이전 부분 snapshot·0거리·미완결 상태를 구분한다. [적용 로그](log/log-2026-11-04-mvp-scoring.md), [검증](source/verification/mvp-scoring-2026-11-04/verification.md).

담당자와 과제 마감일은 아직 이 문서에 확정된 정보가 없습니다. 단계별 날짜는 약속된 완료일이 아니라 실제 기록일입니다. 새 증거 없이 완료율이나 예상 일정을 만들어 표시하지 않습니다.

## 상태를 읽는 방법

| 상태 | 뜻 |
| --- | --- |
| 검증 통과 | 명시한 범위·날짜·환경의 검사에서 통과. 다른 범위의 인수를 자동으로 충족하지 않음. |
| 구현됨·재검증 필요 | 구현 및 과거 근거가 있으나 최신 환경의 검증은 미완료. |
| 부분 구현 | 현재 파일럿 범위만 지원하거나 명세의 일부 조건을 충족하지 못함. |
| 외부 조건 대기 | 자료·이용조건·현장 증거·기기가 필요한 작업. |
| 미착수 | 착수 또는 완료를 증명하는 기록이 없음. |
| 향후 범위 | 기본 통합 이후 판단할 확장. 현재 작업에 자동 포함하지 않음. |

## 전체 단계와 진행 순서

| 단계 | 목표와 현재 상태 | 선행 조건·병행 관계 | 통과 조건과 다음 행동 | 최근 근거 날짜 |
| --- | --- | --- | --- | --- |
| R1 자료·그래프 조사 | 초기 파일럿 조사 검증 기록 있음. 최신성·현장 접근성은 미확보. | 다른 모든 단계의 입력. 자료 보완은 R5에서 지속. | 원본·범위·출처·기준일·연결 한계를 보존. | [2026-10-05](md/project-readiness-ko.md) |
| R2 Android·로컬 서버 통합 | 구현됨. 지도 길게 누르기/보행 node 보정 후 검색·DB API 및 API35 지정 UI 검증 통과. | R1. DB 준비 전에는 로컬 메모리 자료 사용. | 검색→경로 비교→구간→필터→즐겨찾기 흐름. 최신 검증은 R4 근거 참조. | [2026-11-20](source/verification/map-long-press-2026-11-20/verification.md) |
| R3 실제 DB 저장·서버 복원 | **2026-11-04 새3유형 점수 bundle import/복원/API 검증 통과.** 시설1,378·노드27,607·간선8,208·구간22,256. | R1/R2. 기존 bundle 보존, 새 scoring/routing/facility 버전. | 전체 원본/표본/비용 대조·재가져오기 불변·rollback 통과. 런타임은 재시작 시 새 bundle 복원. | [2026-11-04](source/verification/mvp-scoring-2026-11-04/verification.md) |
| R4 최신 앱 전체 흐름·실기기 | **2026-11-20 지도 길게 누르기/보행 node 보정: 서버27·Android41·빌드·lint 오류0/경고50, DB/API35 양쪽 지도 지정 검색 통과. 시스템 상태바/전체 인수 미완료.** | 원본508개 행/좌표/기준일 대조해 앱 주소 보완. 묶음 확대/필터·서버 UI8/화면3프로필은 각 당시 APK 근거. | 실기기/GPS/OEM·현장·사용자 최종 UI·과거 API36.1 원인·명세/일반 창 복원은 미완료. | [최신 자동 보정 검증](source/verification/map-auto-snap-2026-11-20/verification.md), [이전 지도 선택 검증](source/verification/map-long-press-2026-11-20/verification.md), [버튼 배치](source/verification/top-card-small-button-2026-11-20/verification.md), [이전 상단 검증](source/verification/top-card-2026-11-20/verification.md), [손잡이 검증](source/verification/three-stage-handle-2026-11-20/verification.md), [이전 패널 검증](source/verification/three-stage-sheet-2026-11-20/verification.md), [병합 로그](log/log-2026-11-20-ui-merge.md), [이전 화면 검증](log/log-2026-11-08-cluster-kind-ui.md), [주소 검증](source/verification/facility-addresses-2026-11-07/verification.md), [기기 표](source/DEVICE-TEST.md) |
| R5 최신 자료·현장 조사 | **보안등870행의 표시·3유형 점수·실제 DB 반영/복원/API 연결 완료.** 이용조건·현장 보행 확인 대기. | 원본·유형·좌표 공유 기록 보존. | 자료 기간 상한 없음, 보안등을 조명으로 사용. Smartstlamp 확보는 MVP 필수 아님. | [정책](md/night-safety-mvp-scoring-policy-ko.md), [실제 검증](source/verification/mvp-scoring-2026-11-04/verification.md) |
| R6 명세 인수·공식 지표 시연 | **정책·3유형 정식 점수/구간 등급·완결 anchor 경로 추천 구현 및 DB/API·기본 UI 검증 통과. 전체 인수는 미완료.** | R4/R5의 자료·통합 근거. | 개별 기능/교차 TC·설정 조정·현장 corridor 대조. 0거리 null/누락 partial·미완결 추천 중단은 유지. | [2026-11-04](source/verification/mvp-scoring-2026-11-04/verification.md), [명세](md/night-safety-functional-specification-ko.md#section-11) |
| R7 운영 배포·성능 | 미착수/미검증. 현재 loopback 개발 서버. | R4의 안정된 통합. 데이터 공개는 R5/R6의 확보 범위를 따름. | 읽기 전용 운영 DB 계정, HTTPS 호스팅, 백업/복구, 응답시간·동시 요청·용량·cold start 측정. 개발용 계정을 운영 완료로 인정하지 않음. | [2026-10-26 잔여 범위](source/verification/database-integration-2026-10-26.md#남은-범위) |
| R8 시흥 전체·추가 지역 확대 | 향후 범위. 현재 서비스는 대학–정왕역 파일럿. | 앞선 단계의 검증된 자료·현장 범위·성능. | 실제 지역 커버리지·추가 OD·연결성과 용량 검증 후 확장. P2 기능은 별도 채택. | [명세 범위](md/night-safety-functional-specification-ko.md#section-1) |

초기 보고서의 8단계는 당시 착수 제안으로 보존합니다. 위 R1~R8은 후속 구현과 DB 검증을 반영해 재정리한 현재 단계이며 초기 표의 같은 번호와 일대일로 대응하지 않습니다. 자료를 먼저 확보해야 공식 지표를 활성화할 수 있지만, 자료 확보를 기다리는 동안 앱 통합 검증을 진행할 수 있습니다.

## 현재 작업과 보류 조건

| 순서 | 작업 | 완료로 판단할 증거 | 차단 조건 |
| --- | --- | --- | --- |
| 완료 2026-10-26 | 최신 Android 빌드와 단위/lint | 새 APK, 단위14개, lint 오류0/경고49, 설치 APK 해시 일치 | 과거 APK로 대체하지 않음 |
| 조사 2026-10-27 | 실패 환경과 앱 상태 구분 | Awake인데 홈도 검정인 호스트 GPU 실행, 앱 설치 전 System UI 응답 없음 캡처. 별도 임시 환경에서는 같은 APK로 지도 준비 통과. | 특정 드라이버 내부 원인/모든 과거 실패 원인은 미확정 |
| 완료 2026-10-27 | DB 기반 에뮬레이터 UI8개 재검증 | 검색→후보→구간→필터→저장→재시작/오프라인→수정/재조회/삭제와 캡처 | 명세 전체 TC·실기기 인수와 구분 |
| 기기 준비 후 | 실제 Android 기기 GPS·위치 권한 | 정상 수신·거부·대략 위치·GPS OFF/시간 초과·수동 입력 유지 | 연결된 물리 기기 없음. 사용자의 GPS 태블릿은 모델/OS·실제 수신 확인 필요 |
| 완료 2026-11-03 15:31 | DB 재활성화 후 보안등 신규 bundle 반영 | 1,378개 시설의 전체 DB/API 동등성·재가져오기/rollback 통과 | DB 차단 해소. 자료 기준일252일 경과·이용조건/현장은 별도 미확인 |
| 완료 2026-11-03 22:32 | 보안등 추가 수정 APK와 최신 DB의 전체 UI 재검사 | 지도/검색/구간/필터/Room 전체8개·종료코드0·캡처 시각 확인 | 이전 ANR/ADB 실패 보존. 실기기/명세 전체 인수와 구분 |
| 완료 2026-11-04 | 1번 MVP 점수 정책 확정·명세 반영 | 자료 기간 상한 제거·보안등 조명 채택·작동 미확인 문구 제외·출처/기준일·TC33~35를 문서에 반영 | 코드/DB/APK 적용과 동작 검증은 별도 미완료 |
| 완료 2026-11-04 | 2번 3유형 점수·새 bundle·API/앱 적용 | 서버24·도구5·Android20·새 APK/lint·DB/API·전체 기본 UI8개 통과 | 명세 전체 TC·실기기/현장·운영 배포는 별도 미완료 |
| 병행 | 현장 증거 확보 | 검증된 보행 연결·접근성 기록 | 팀의 주·야간 조사 필요 |

## 기능별 구현과 검증 현황

핵심 38개 기능을 빠뜨리지 않기 위한 추적표입니다. 명세의 모든 TC를 새로 실행한 인수표는 아닙니다. 구현 범위는 현재 실행 안내/기존 계획을 근거로 하며, 기능별 상세 TC와 대응이 불명확한 부분은 미검증으로 남깁니다. 최근 상태 갱신일은 2026-11-05이고 **검증 날짜는 아래 근거의 실제 날짜**입니다. 11월4일 정책 문서 반영은 새 점수 구현·동작 검증이 아닙니다.

근거: [A: 초기 앱·빌드 2026-10-16](source/verification/README.md), [B: 실제 TMAP 2026-10-16](source/verification/tmap-auth.md), [C: 통합 UI 2026-10-16](source/verification/integration-ui.md), [D: DB·서버/API 2026-10-26](source/verification/database-integration-2026-10-26.md), [E: 자료·경로 조사 2026-10-05](md/project-readiness-ko.md), [F: 원천 재확인 2026-10-16](source/verification/data-source-review-2026-10-16.md), [G: 새 APK·기본 UI8개 2026-10-27](source/verification/android-r4-2026-10-26.md), [H: 수정 APK·최신 DB 기본 UI8개 2026-11-03](source/verification/android-2026-11-03_222620_934204/integration-ui.md), [I: 3유형 점수·DB/API·최종 기본 UI 2026-11-04](source/verification/mvp-scoring-2026-11-04/verification.md), [J: 최신 APK UI8개 2026-11-05](source/verification/android-2026-11-05_215835_067057/integration-ui.md), [K: 위치 수정 APK 오류/권한 모의 2026-11-05](source/verification/error-recovery-2026-11-05/verification.md), [L: API36.1 조사·시설 수·38개 대조 2026-11-05](source/verification/spec-audit-2026-11-05/verification.md).

| 기능 ID | 현재 구현 범위 | 검증 상태·날짜·근거 | 남은 확인 |
| --- | --- | --- | --- |
| F-01-01 | TMAP·로컬 미리보기 | TMAP 준비/표시 2026-11-05 J 통과 | 인증 오류·실패 복구 개별 TC |
| F-01-02 | 일회성 현재 위치 마커·재중심·전경 권한/시간 초과 처리 | 2026-11-05 K: OS 거부·대략 권한 무수신 시간 초과·모의 정밀 위치·위치 OFF 통과, 첫 수신 crash 수정 | 실제 GPS·대략 좌표 정확도·OS26~29 분기/명세 전체 인수 |
| F-01-03 | 지도 조작, 서버 bbox 시설 조회 | 부분 근거 A/B/D, 지도 이동마다 자료 갱신하는 TC 미확인 | 연속 이동·최신 bbox와 응답 일치 |
| F-02-01 | 좌표·OSM 입력 | 기본 좌표/OSM 흐름 2026-11-05 J 통과 | 현재 위치·지도 pin 등 명세 입력방식 대조 |
| F-02-02 | 파일럿 OSM 이름 검색 | OSM anchor J, 검색0건 완료 상태 수정·UI 2026-11-05 K 통과 | TMAP POI/시흥 전체 검색 아님. 동명 장소 구분 대조 |
| F-02-03 | 출발·도착 교환 | 두 번 교환·이전 결과 안내·이전 결과 저장 차단 2026-11-05 K 통과 | 지연 응답·연속 교환 개별 TC |
| F-02-04 | 서버 검색·입력 검증·최신 요청 반영 | 2026-11-05 K 범위 밖 좌표·검색 실패/복구·이전 점수 유지·저장 차단 통과 | 지연 응답/취소/다양한 잘못된 입력 전체 TC |
| F-03-01 | OSM 파일럿 그래프·DB 복원 | 조사 2026-10-05 E, DB 전체 대조 2026-10-26 D | 시 전체·조건부 접근권·현장 확인 |
| F-03-02 | anchor·gap·미완결 처리 | 서버 2026-10-26 D | 실제 교문/역 출구 connector 증거 |
| F-03-03 | Dijkstra 빠른 후보·거리/1.2m/s 시간 | 서버 2026-10-26 D | 신호/경사 미반영, 명세 TC와 개별 대조 |
| F-03-04 | 3유형 시설 비용·최종 점수 기반 안전 우선 선택 | 2026-11-04 새 DB/API 및 UI 검증 통과 | 전역 최적 보장 아님. 명세의 개별 후보/시간상한 TC 대조 |
| F-03-05 | 중복·우회시간 상한·최대3개 반환 | 서버 2026-10-26 D | 고정4개 정책 풀과 전역 최적화를 구분 |
| F-03-06 | 균형·보행선 등 정책 후보 | 서버 D, 보행선 선호 재조회 UI 2026-11-04 I 통과 | 나머지 프로필별 개별 TC |
| F-04-01 | 20m 이하 구간·5m 이하 표본 | 계산/전체 복원 2026-10-26 D | 명세 TC의 정확한 분할 예와 별도 대조 |
| F-04-02 | CCTV/비상벨/보안등3유형 분석·기간 상한 없음 | 2026-11-04 서버/DB 대조 통과, 새 점수/구간 UI 확인 | 제공범위·갱신 실패 등 전체 개별 TC 대조 |
| F-04-03 | 길이 가중 정식 평균 지표 | 2026-11-04 서버24개·DB 전 표본/구간 대조 통과 | 명세 개별 분할/경계 TC 대조 |
| F-04-04 | 하위10% 길이 가중 정식 취약 지표 | 2026-11-04 경계 셀·weak 길이/API·UI 통과 | 명세 전체 경계·분할 독립성 TC 대조 |
| F-04-05 | 정식 전체 지표·거리0 null·누락시 부분 지표 | 2026-11-04 fixture/DB/파서, 2026-11-05 DB snapshot API·API35 최신 APK의 숫자→0거리 세 지표 `—` 초기화 통과 | 가중치 변경/모델 보정과 명세 전체 TC |
| F-04-06 | CCTV/비상벨/보안등 고유 개수·미확보 null | 서버/DB2026-11-04, 앱 파서/표시·0/null/불량 수치 회귀와16/16/12 필터 불변 UI2026-11-05 L 통과 | 반경/unique/eligible/raw 전체 계약 TC |
| F-05-01 | 경로 선·선택 표시 | 기본 흐름2026-11-04 I, 최신 APK의0거리 경로선 제거 캡처2026-11-05 통과 | 미완결 등 나머지 개별 UI TC |
| F-05-02 | 9개 기본 비교 지표·공식/부분/미확보 안내 | 누락된 시설3개 수치 표시·부분 조명 null/이유·복구 UI2026-11-05 L 통과 | 빠른 대비 차이·서로 다른 버전 비교 등 전체 TC |
| F-05-03 | 정식 구간 등급 색/범례와 하위10% 주황 표시 | 2026-11-04 UI/캡처·ON/OFF 화소 대조 통과 | 접근성·분할별 상세 등 전체 TC 대조 |
| F-05-04 | 하위10% 구간 상세·시설지표 설명 | 취약 상세·강조 전환 2026-11-05 J 통과 | 상세 필드별 개별 TC |
| F-06-01 | CCTV270·비상벨238·보안등870·경찰3 표시, 보안등 점수 연결 | 2026-11-04 서버/DB/API·새 APK UI 통과 | 전수/페이지·지도 범위 자동 갱신 미완료 |
| F-06-02 | 시설 필터 | CCTV/보안등1381→1111/511→1381 UI 2026-11-05 J 통과. 변경 시설만 SDK 갱신, 기존 회귀3개 | 점수/후보 불변 전체 TC |
| F-06-03 | 시설 상세·출처/기준일·작동 미확인 문구 제외 | 2026-11-04 앱 코드/파서 반영, 별도 보안등 상세 확인 | 필드별 원천/누락 표시 전체 TC |
| F-07-01 | Room 즐겨찾기 저장 | 최신 고정 글꼴 APK UI 2026-11-05 J 통과 | 저장 실패 TC |
| F-07-02 | 목록·오프라인 snapshot 복원 | 재시작/오프라인/과거 안내 UI 2026-11-05 J 통과 | 버전 차이별 전체 인수 |
| F-07-03 | 이름·선호유형 수정 | 이름·보행선 선호 수정 UI 2026-11-05 J 통과 | 생성일 보존 등 전체 TC |
| F-07-04 | 즐겨찾기 삭제 | 시험용 항목 삭제·목록 갱신 UI 2026-11-05 J 통과 | 다른 항목 보존 TC |
| F-07-05 | 새3유형 저장 snapshot·최종 역할 기준 선호 재조회 | 2026-11-04 파서 회귀, 최신 APK 선호 재조회 2026-11-05 J 통과 | 다양한 구/신 graph·facility 버전별 전체 인수 |
| F-08-01 | 수동 import·보안등 점수 대상 asset/감사·DB bundle | 2026-11-04 변환/격리·DB 재가져오기/rollback 통과 | 수집/동기화 실패·마지막 정상자료 전체 TC |
| F-08-02 | 원본 감사·원천 필드 보존 | 조사 2026-10-05 E, 전체 DB 대조 2026-10-26 D | 신규 원천의 ID충돌·범위 밖 격리 TC |
| F-08-03 | 사전계산·단일 트랜잭션 bundle·시작 시 복원 | DB 반복/rollback 2026-10-26 D | 실행 중 원자적 전환은 미구현, 재시작 방식과 명세 차이 정리 |
| F-08-04 | 출처·기준일·ready/unavailable·기간 상한 제거 | 2026-11-04 날짜 경과/정상0건/원천 미확보·잘못된 유형 회귀 통과 | 동기화 운영·새 자료 상태 전환 전체 TC |
| F-09-01 | revision 취소·서버/위치 실패·부분/이전 안내 | 오류/권한2026-11-05 K, 원천 부분/정상 복구2026-11-05 L 통과 | 429 Retry-After·명시 cancel·지연 응답 개별 UI TC/미구현은 L 대조표 |
| F-09-02 | 코드 내 점수/탐색 설정 버전 | DB 지원 버전/복원 2026-10-26 D | 설정 변경 도구·음수/Infinity 거절 등 전체 TC |
| F-09-03 | 키 분리·허용 snapshot 저장·서버 오류 비밀정보 숨김 | 부분 검사 A/C/D | 최신 APK·운영 DB 계정·전체 로그/개인정보 TC |

F-10-01~04는 명세의 별도 제안입니다. 현장 기록은 R5의 검증 근거로 수행하되 별도 앱 기능 채택을 뜻하지 않습니다. 보행속도 개인설정·오프라인 자체 탐색·외부 길찾기 전환은 자동으로 이번 범위에 넣지 않습니다.

## 완료 기준의 구분

| 수준 | 완료 조건 | 현재 상태 |
| --- | --- | --- |
| 파일럿 기본 통합 시연 | 제한 지역·자료 기준일·경로 연결 상태를 표시하고 검색/점수/표시/저장 흐름 검증 | **2026-11-04 새3유형 점수 APK의 DB 기반 기본 UI8개·상세/0거리 통과.** 명세 전체/실기기/현장 인수와 구분. |
| 명세 전체 시연 인수 | [11.2 시연 완료 조건](md/night-safety-functional-specification-ko.md#section-11)의 기능별/교차 TC, CCTV·비상벨·보안등 자료, 검증 corridor 등 충족 | 새3유형 점수 구현·기본 검증 완료, 현장·미대조 TC 때문에 전체 인수 미완료. 자료 경과일/Smartstlamp 확보는 차단 조건 아님. |
| 실제 사용·운영 배포 | 통과한 범위의 자료/통행 검증, 실기기, HTTPS·운영 권한·성능·복구 확인 | 미완료. 현재 loopback 개발 서버. |

## 적용한 범위와 설계 결정

| 결정 | 이유·적용 범위 | 제외하거나 남긴 조건 | 기록 날짜·근거 |
| --- | --- | --- | --- |
| 대학–정왕역부터 통합 | 자료와 그래프를 검토할 수 있는 파일럿 | 시흥 전체 서비스로 표현하지 않음 | 2026-10-05 [초기 점검](md/project-readiness-ko.md) |
| 원본 제안서의 지도/시설 표시에서 자체 후보·지표 명세로 구체화 | 기능 명세가 자체 탐색·구간 계산의 요구 기준을 제공 | 원본 제안서와 명세의 범위가 동일하다고 취급하지 않음. 외부 길찾기/공식 점수는 별도 상태. | 2026-10-05 [명세](md/night-safety-functional-specification-ko.md), 원본 제안서는 조사 자료 폴더에 보존 |
| TMAP 배경지도·로컬 OSM 검색 | 실제 지도와 보관 가능한 자체 endpoint 이용 | TMAP REST POI 또는 시 전체 장소 검색 아님 | 2026-10-16 [통합 계획](source/docs/superpowers/plans/2026-10-16-integration.md) |
| 과거 CCTV/비상벨 지표만 비교 | 180일 초과·가로등 미확보를 숨기지 않음 | 공식 점수·현재 안전/균형 추천 null | 2026-10-16 [통합 로그](log/log-2026-10-16-integration.md) |
| PostGIS 저장 + Python Dijkstra | 기존 검증된 탐색/API 유지 | pgRouting 실행 아님. 시작 시 DB snapshot을 읽으며 변경은 재시작 후 반영 | 2026-10-26 [DB 계획](source/docs/superpowers/plans/2026-10-26-postgis.md) |
| MVP 자료 기간 상한 제거·보안등 조명 채택 | 확보한 공공 CSV와 기존 계산식으로3유형 지표 구현 | 출처/기준일·작동 미확인 문구 제외, 입력/누락/버전/경로 계약 유지. 실제 DB/API·새 APK 기본 UI 검증 통과 | 2026-11-04 [적용 검증](source/verification/mvp-scoring-2026-11-04/verification.md) |

| 기존 MVP 대체 구현과 명세 차이 대조 | 제한 파일럿 패키지·직접 좌표/OSM·서버 시작 snapshot을 사용하는 현재 구조를 명시 | 지도 pin·viewport별 시설 조회·구간 유형 기여/시설 연결·동일 선 재평가·429 정책 등 미구현. 기본 시연 범위이며 전체 P0 인수 면제/완료 아님 | 2026-11-05 [38개 대조표](source/verification/spec-audit-2026-11-05/functional-matrix.md) |

## 문서 관리와 변경 이력

현재 상태는 이 문서에 모으고, 과거 계획·로그·검증 본문은 해당 날짜의 결과로 보존합니다. 초기 준비 보고서의 기준본은 `md/project-readiness-ko.md`입니다. 조사 패키지 안의 동일 보고서는 보관본으로 표시합니다. 과거 계획의 체크 완료는 그 작업 범위의 완료이며 전체 인수를 대신하지 않습니다.

변경마다 **관련 문서의 최종 수정일, 이 문서의 상태/변경 이력, 날짜별 개발 로그**를 같은 작업에서 갱신합니다. 검증일은 실제 실행한 날짜로 별도 기록합니다. 같은 날의 별도 변경은 행을 추가하고 필요하면 시각을 붙입니다. 상세 규칙은 [AGENTS.md](AGENTS.md)에 있습니다.

| 날짜 | 변경 | 상태에 미친 영향 | 근거 |
| --- | --- | --- | --- |
| 2026-10-05 | 초기 자료/경로 조사와 기능 명세 작성 | 초기8단계·P0/P1/P2·인수 기준 수립. 현재 로드맵을 만들며 기존 기록에서 옮긴 이력. | [초기 보고서](md/project-readiness-ko.md), [명세](md/night-safety-functional-specification-ko.md) |
| 2026-10-16 | Android·로컬 서버·Room 통합과 당시 UI 검증 | 파일럿 구현/과거 UI 근거 확보. 실제 DB 연결은 당시 미실행. | [통합 로그](log/log-2026-10-16-integration.md) |
| 2026-10-26 | 실제 DB 가져오기·복원·API 검증 | R3 검증 통과, R4 최신 앱 UI는 시간 초과로 미완료. | [DB 검증](source/verification/database-integration-2026-10-26.md) |
| 2026-10-26 | 전체 로드맵·38개 기능 현황·완료 수준·문서 역할 통합 | 새 구현/검증 결과 없음. 다음 작업과 병행 조건을 문서로 명시. | [문서 개선 로그](log/log-2026-10-26-documentation.md) |
| 2026-10-26 | 작성일/최종 수정일/실제 검증일 구분과 변경마다 날짜 기록 규칙 추가 | 이후 작업도 날짜·변경 근거를 남기도록 프로젝트 작업 규칙에 반영. | [AGENTS.md](AGENTS.md) |
| 2026-10-26 | R4 착수, 현재 Android 소스의 테스트·lint·새 APK 확인 | 단위14개 통과, lint 오류0/경고49. 최신 UI 검사는 아직 진행 중. | [R4 검증](source/verification/android-r4-2026-10-26.md) |
| 2026-10-26 | UI 도구의 과거 보고서/캡처 덮어쓰기 수정 | 실패를 재현한 회귀2개가 수정 후 통과. 이후 증거는 날짜/시각별 폴더 보존. 앱 기능 변경 없음. | [R4 로그](log/log-2026-10-26-r4-android.md) |
| 2026-10-27 | 호스트 GPU 환경의 홈/앱 검은 화면을 비교하고 임시 새 환경으로 분리 | 최신 UI 통과 아님. 화면 켜짐/부팅 상태와 무관한 해당 환경의 렌더링 이상 관찰. 기존 자료 보존. | [27일 R4 로그](log/log-2026-10-27-r4-android.md) |
| 2026-10-27 | 새 임시 환경에서 TMAP 준비/시설511개·기본 서버 검색 후보3개 검사 통과 | 전체 UI/실기기 검증 완료는 아직 아님. 실패 보고서 보존을 추가한 회귀는 총3개 통과. | [R4 검증](source/verification/android-r4-2026-10-26.md) |
| 2026-10-27 00:34 KST | 새 APK의 DB 기반 에뮬레이터 기본 UI8개 전체 통과 | 지도/검색/구간/필터/Room 저장·재시작·오프라인·수정·재조회·삭제 통과. 다음은 실기기 GPS/권한. | [완료 보고서](source/verification/android-2026-10-27_001901_382784/integration-ui.md) |
| 2026-10-27 | 설치 APK 해시 일치와 지도 캡처/overlay ON/OFF 확인 | 로컬 APK와 설치 APK 일치, 주황 화소 ON2039/OFF0. 앱 소스 수정 없이 시험 환경을 분리해 통과. | [R4 로그](log/log-2026-10-27-r4-android.md) |
| 2026-10-27 13:15 KST | R5 공식 CCTV/비상벨/조명 원천과 샘플 확인 | 공개 원천/일부 이용조건 확인. 최신 시흥 전수/기준일 미확보. 원본 파일 또는 정식 키 확보가 다음 단계이며 앱/DB 변경 없음. | [원천 조사](source/verification/data-source-review-2026-10-27.md), [로그](log/log-2026-10-27-data-sources.md) |
| 2026-10-27 | 실기기 준비 조건에 사용자 보유 GPS 태블릿 정보 반영 | 휴대폰만으로 한정하지 않음. 모델/OS·USB 연결·실제 수신은 미검증이며 R5는 기기 없이 병행. | [R5 로그](log/log-2026-10-27-data-sources.md) |
| 2026-10-27 | 사용자 지적에 따라 기존 csv 보유/기준일 재확인 및 요청 표현 정정 | CCTV2130행/2026-01-20, 비상벨1851행/2026-01-22 확인. 같은 파일의 재전송은 불필요하며 추가 확보는 조명/갱신본을 뜻함. 앱/DB 변경 없음. | [R5 로그](log/log-2026-10-27-data-sources.md) |
| 2026-10-27 | 사용자가 기존 두 CSV가 최신 자료임을 확인 | 현재 기준 자료로 확정하고 더 최신 파일 요청을 제외. 다음 자료 확보는 가로등/조명. 실제 기준일과 기존 점수 정책은 유지하며 원천 자동조회 성공으로 바꾸지 않음. | [R5 로그](log/log-2026-10-27-data-sources.md) |
| 2026-11-03 | 시흥 보안등 CSV9,265행의 인코딩·기준일·좌표·누락·중복·파일럿 범위 검사 | R5 보안등 원본 확보/파일 검사 완료. 유형·출처/이용조건·최신성·중복 검토 대기. 앱/DB 및 공식 점수 상태 유지. | [보안등 검사 로그](log/log-2026-11-03-security-lights.md) |
| 2026-11-03 | 사용자 제공 출처 기록, 보안등 파일럿870행의 별도 asset·감사·서버/API·앱 표시/필터/상세 구현 | 서버18·도구5·Android14개 통과, lint 오류0/경고44·APK 빌드 통과. 모든 간선의 기존 비용/점수 동일. DB 접속 실패·신규 import 미실행, 최신 전체 UI 실패 보존. | [개발 로그](log/log-2026-11-03-security-lights.md), [검증 보고서](source/verification/security-lights-2026-11-03/verification.md) |
| 2026-11-03 15:11 KST | 보안등의 에뮬레이터 표시·필터·목록·상세와 로컬 서버 검색 범위 검사 통과 | R5 보안등 로컬 연결 검증 완료. 전체 UI/실제 DB/실기기 인수는 미완료 유지. 과거 실패·성공 보존. | [보안등 UI 결과](source/verification/android-2026-11-03_150042_324475/security-lights-ui.md) |
| 2026-11-03 15:31 KST | 사용자 DB 재활성화 후 보안등870행의 새 bundle import·복원/API 전체 대조·재가져오기·rollback 통과 | R3 보안등 DB/API 검증 완료, R5 실제 DB 반영 완료. 기존 접속 실패 차단 해소. 최신 전체 UI·실기기/현장·공식 점수 인수는 미완료 유지. | [DB 결과](source/verification/database-security-lights-2026-11-03.md), [개발 로그](log/log-2026-11-03-security-lights.md) |
| 2026-11-03 22:12~22:26 KST | DB 기반 앱 ANR 진단 후 시설 overlay 차이만 갱신하도록 수정, 회귀3개 추가 | 전체 마커 재생성 동작의 회귀3개 실패 확인 후 Android17개·lint 오류0/경고44·APK 빌드 통과. 수정본 UI7개 단계 후 ADB 실패로 전체 재검사 중. DB/점수 정책 변경 없음. | [개발 로그](log/log-2026-11-03-r4-ui.md), [ANR 근거](source/verification/android-2026-11-03_220808_226636/failure.md), [수정본 실패](source/verification/android-2026-11-03_221824_537215/failure.md) |
| 2026-11-03 22:32 KST | 수정 APK의 최신 DB 기반 전체 기본 UI8개 재검사 통과 | R4 기본 통합 검증 완료. 지도/검색/구간/필터/Room 저장·재시작·오프라인·수정·재조회·삭제, 설치 APK 일치·캡처 확인. 실기기/명세 전체/현장/공식점수/운영 인수는 미완료 유지. | [완료 보고서](source/verification/android-2026-11-03_222620_934204/integration-ui.md), [개발 로그](log/log-2026-11-03-r4-ui.md) |
| 2026-11-03 23:06 KST | R6 정책 검토를 우선 논의하고 MVP 정책안의 시설 작동 여부 미확인 문구 제외 결정 기록 | 표시 정책만 결정. 코드/명세/DB·공식 점수와 현장 검증 상태는 변경 없음. | [정책 기록](log/log-2026-11-03-r6-policy.md) |
| 2026-11-04 | 사용자 지시에 따라1번 MVP 정책 확정·기능 명세1.2 반영 | 기간 상한 제거·CCTV/비상벨/보안등3유형·출처/기준일·작동 미확인 문구 제외·TC33~35 확정. R6 정책 정리 완료, 점수 코드/DB/APK·새 인수 검사는 미완료 유지. 과거 결과 보존. | [정책](md/night-safety-mvp-scoring-policy-ko.md), [기능 명세](md/night-safety-functional-specification-ko.md), [로그](log/log-2026-11-04-r6-policy.md) |
| 2026-11-04 | 정책 실제 적용 착수, 3유형 서버/DB 점수·추천·앱 파서/표시 구현 | 새 append-only DB import·복원/API 대조·rollback 통과. 코드 검토2건 회귀 후 수정, 최종 APK/전체 UI 확인 중. 과거 점수 null 근거는 보존. | [적용 로그](log/log-2026-11-04-mvp-scoring.md) |
| 2026-11-04 23:09 KST | 새 정책의 실제 서버/DB/앱 적용 및 최종 기본 UI8개 통과 | 자료 기간 차단 제거·보안등 포함 정식 지표/구간 등급·완결 경로 추천 활성화. 서버24/도구5/Android20·빌드/lint·DB 전체 대조/rollback·새 APK UI 통과. 전체 명세/실기기/현장 인수와 구분. | [검증](source/verification/mvp-scoring-2026-11-04/verification.md), [로그](log/log-2026-11-04-mvp-scoring.md) |
| 2026-11-05 | 사용자 위임에 따라 UI 정리 적용, 코드 검토의 경찰시설 후보 표시 보완 | Android22개·도구5개·APK/lint 오류0/경고24 통과. 실행 UI 검증 진행 중, 사용자 최종 디자인 검사 대기. DB/점수 정책 변경 없음. | [UI 계획](source/docs/superpowers/plans/2026-11-05-ui-polish.md), [UI 로그](log/log-2026-11-05-ui-polish.md) |
| 2026-11-05 13:09 KST | 필터 복원 시 TMAP 대량 마커 동기 추가 ANR을 진단하고 프레임당8개·취소/종료 처리로 수정 | 회귀3개 포함 Android25개·도구7개·빌드/lint 오류0/경고24 통과. 코드 검토에서 중요한 결함 없음, 새 APK 실행 재검증 중. 이전 실패/ANR 보존. | [UI 로그](log/log-2026-11-05-ui-polish.md), [ANR 근거](source/verification/android-2026-11-05_125354_058424/failure.md) |
| 2026-11-05 13:37 KST | 수정 APK의 기본 UI8개 통과 후 회전 점수 유실·확대 글꼴 헤더 잘림 확인, 사용자 재부팅 요청으로 일시 중단 | UI8개 성공/추가 화면 문제를 구분. 헤더 XML 후속 수정은 미빌드, 회전 문제 미해결, 전체 UI/사용자 인수 미완료. 다음 시작점·APK 해시·환경을 인계 문서에 보존. | [인계](log/log-2026-11-05-ui-reboot-handoff.md), [UI8개](source/verification/android-2026-11-05_130904_166965/integration-ui.md) |
| 2026-11-05 16:00 KST | 사용자 선택에 따라 MVP 세로 고정·API36 대화면 호환 속성 적용, 헤더 후속 수정 APK 반영 | 빌드/병합 Manifest/단위25개 기존 결과·lint 오류0/경고26·API36 방향6개 확인. 회전 복원은 후순위로 전환, 창 크기/글꼴 변경 상태 복원·추가0거리·실기기/사용자 인수는 미완료 유지. | [작업 로그](log/log-2026-11-05-portrait-lock.md), [검증](source/verification/portrait-lock-2026-11-05_155732/verification.md) |
| 2026-11-05 | 사용자 선택으로 MVP 앱 글꼴 배율1.0 고정, fontScale 변경 재생성 방지 | 수정 전 실제 글꼴 증가 회귀 실패 후 빌드/단위25개/lint 오류0·경고26 통과. API36 배율0.85/1.3/2.0·열린 창 유지·큰 글꼴 새 시작·설정 복원 확인. 일반 창 크기/프로세스 복원·추가0거리·실기기/최종 UI 인수는 미완료. | [작업 로그](log/log-2026-11-05-font-lock.md), [검증](source/verification/font-lock-2026-11-05_162308/verification.md) |
| 2026-11-05 16:36 KST | 사용자 요청으로0거리 검사 전 연결 상태만 확인 | 로컬8765 health/TCP 응답 없음·연결 ADB/에뮬레이터 프로세스 없음. DB 직접 상태 미확인. 환경 기동 필요, 코드/데이터·기존 검증·개발 진행 상태 변경 없음. | [연결 확인](log/log-2026-11-05-connection-check.md) |
| 2026-11-05 21:12 KST | 환경 연결 후 최신 APK의 정상 점수→0거리 회귀/API·지도 검사 완료, 외부 시스템 창 오분류 수정 | DB snapshot 서버/5556 연결 유지. 0m/0분·세 점수 `—`·기존 경로선 없음, 도구9개 통과. 앱/서버/DB/APK 변경 없음(검사 도구만 보완). API36.1 앱 화면 소실 원인 미확정·실기기/최신 Room 전체·최종 인수 미완료 유지. | [로그](log/log-2026-11-05-zero-route.md), [UI](source/verification/android-2026-11-05_210638_044884/verification.md), [API](source/verification/zero-route-api-2026-11-05/verification.md) |
| 2026-11-05 | 사용자 요청으로 기기 없이 가능한 MVP 검증을 먼저 마치는 순서 정리 | 최신 전체 흐름→오류/복구·권한 모의→미확정 종료 현상/필수 명세 대조→UI/설치 준비를 우선. 계획 기록이며 새 검사/구현 완료 아님. 실기기 GPS·제조사 동작/현장·배포는 분리. | [사전 검사 순서](log/log-2026-11-05-pre-device-checks.md) |
| 2026-11-05 15:40 KST | 기획 및 발표 평가를 위한 발표 자료 산출물 2종 작성 (슬라이드별 가이드 및 종합 설명서) | 기능·구현 상태 변동 없음. 팀명 '밤길 지킴이' 확정 반영, PPT 슬라이드별 대본 가이드 및 종합 설명서 작성. | [슬라이드 가이드](md/슬라이드별.md), [종합 설명서](md/해설.md), [작성 로그](log/log-2026-11-05-presentation-materials.md) |
| 2026-11-05 16:19 KST | 사용자 실제 실행 검증을 위한 `실행법.md` 가이드 문서 작성 | 기능·구현 상태 변동 없음. Android Studio 프로젝트 열기, 파이썬 서버 구동, adb 포워딩, 앱 실행 및 확인 절차 정리. | [실행법](실행법.md), [작성 로그](log/log-2026-11-05-run-guide.md) |
| 2026-11-05 22:09 KST | 실기기 연결 전1번 최신 APK 전체 기능 흐름8개 통과 | 설치 해시 일치·검색/구간/필터·Room 저장/재시작/오프라인/수정/재조회/삭제·캡처 확인. 코드/APK 변경 없음. 다음2번 오류/복구·권한 모의 미실행, API36.1/실기기/전체 인수는 미완료. | [로그](log/log-2026-11-05-latest-ui-flow.md), [검증](source/verification/android-2026-11-05_215835_067057/integration-ui.md) |
| 2026-11-05 | 사전 검사2번 오류·복구/위치 권한 모의 착수, 기존 Smoke 기반 검증 도구 추가 | 설치 APK/서버/기존 에뮬레이터 확인. 앱/서버/DB 변경 없음, 실제 검사 결과는 진행 중이며 통과로 표시하지 않음. | [로그](log/log-2026-11-05-error-recovery.md) |
| 2026-11-05 | 오류·복구 검사에서 첫 위치 수신 시 SDK 위치 아이콘 null crash와 검색0건 상태 잔류를 재현하고 수정 | 일반 마커로 일회성 위치 표시/재중심, 검색0건 완료 문구 추가. 수정 전 실패 보존, 새 APK 검증 진행 중. API36.1 별도 소실 원인이 같다고 단정하지 않음. | [로그](log/log-2026-11-05-error-recovery.md) |
| 2026-11-05 22:43 KST | 사전 검사2번 완료: 위치 첫 수신 crash/검색0건 상태 수정 후 지정8개7+1회 통과 | 새 APK 설치 해시 일치·Android25/도구11·빌드/lint 오류0·경고27. 권한/위치/모의 provider/reverse 원복 확인. 이전 APK UI8개/0거리 근거 보존. 다음3번·실기기·전체 인수 미완료. | [종합 검증](source/verification/error-recovery-2026-11-05/verification.md), [로그](log/log-2026-11-05-error-recovery.md) |
| 2026-11-05 | 사전 검사3번 착수: API36.1 read-only 재현 환경·38개 명세 대조, 경로 시설 수 UI 누락 확인 | 당시 APK 부재로 현재 APK 재현과 역사적 원인 판단을 구분. 필수 비교 수치 보완 설계, 새 검증은 진행 중. | [로그](log/log-2026-11-05-api36-spec-audit.md) |
| 2026-11-05 | 사전 검사3번 API36.1 재현 조사·38개 명세 대조, 경로 시설 수 UI 누락 보완 | 단위27/도구12·빌드/lint 오류0·경고31, 새 APK API36.1 지정5개2+3회 같은 PID 통과. 원천 누락/0 구분·필터 불변. 과거 APK 부재/소실 원인은 미확정, 전체 명세의 pin/bbox/상세 이유 등은 미완료 유지. | [검증](source/verification/spec-audit-2026-11-05/verification.md), [대조표](source/verification/spec-audit-2026-11-05/functional-matrix.md), [로그](log/log-2026-11-05-api36-spec-audit.md) |
| 2026-11-06 | 사전 검사4번 화면·설치 준비 착수, 서버/에뮬레이터 환경 재기동 | 기존 APK 해시 확인. 작은 화면/빈·오류/스크롤 검증과 APK·해시·USB 설치/실기기 검사표 준비 중, 통과 전. | [로그](log/log-2026-11-06-screen-install.md) |
| 2026-11-06 | 320×568dp에서 지도 로컬 보기 버튼 잘림 재현, 짧은 화면 지도 버튼을48dp 가로 행으로 수정 | 일반 높이720dp 이상은 기존 세로 배치 유지. Kotlin/서버/DB 변경 없음. 수정 전 실패 보존, 새 APK/UI 검증 진행 중. | [로그](log/log-2026-11-06-screen-install.md) |
| 2026-11-06 | 사전 검사4번 작은/일반 화면·설치 준비 완료 | 지도 버튼48dp 가로/세로 배치·긴 목적지·본문/스크롤·빈/오류/복구 통과. 도구13·빌드/lint 오류0·경고33, 검증 APK/해시·설치/실기기 표 준비. 실제 기기/사용자 UI/전체 명세 인수와 구분. | [검증](source/verification/screen-install-2026-11-06/verification.md), [로그](log/log-2026-11-06-screen-install.md), [설치 안내](source/DEVICE-TEST.md) |
| 2026-11-06 | 사용자 명시 요청으로 앱 ViewBinding 전체 전환 착수 | 메인/패널·대화면 qualifier·입력 dialog3개·경로 행을 전환 예정. 기존 설치 묶음/검증 보존, 새 APK 검증 전. | [계획](source/docs/superpowers/plans/2026-11-06-viewbinding.md), [로그](log/log-2026-11-06-viewbinding.md) |
| 2026-11-06 | ViewBinding 전체 전환·새 APK 재검증 완료, 설치 대상 갱신 | 메인/패널·행·dialog3개 전환, 단위27/도구13·UI 기능8·small/pane 통과. lint 오류0/경고41. 기존 근거 보존, 실기기/전체 인수 상태는 미완료 유지. | [검증](source/verification/viewbinding-2026-11-06/verification.md), [로그](log/log-2026-11-06-viewbinding.md), [APK](source/delivery/2026-11-06-viewbinding/README.md) |

| 2026-11-06 | 사용자 요청 지도 전체화면 착수 | 기존 reset 버튼은 중심/zoom 초기화임을 확인. 새 전체화면 UI·복귀 검증 전. | [로그](log/log-2026-11-06-map-fullscreen.md) |
| 2026-11-06 | 사용자 요청 지도 전체화면 구현/검증·설치 대상 갱신 | 전체 보기 초기화 대신 지도 확장·화면 복귀/뒤로 지원. 최종 small/pane4개 통과, 일반 화면은 동일 DEX 이전 문구 근거. 실패 보존·단위27/도구13·lint 오류0/경고41, 실기기 인수 미완료 유지. | [검증](source/verification/fullscreen-2026-11-06/verification.md), [로그](log/log-2026-11-06-map-fullscreen.md) |
| 2026-11-06 11:56 KST | 사용자 요청에 따라 서버·앱 7대 성능 최적화 적용 및 단위·빌드 검증 | 서버 `point_score` 박스 사전 필터·`public_route` 거리 재계산 제거·`anchor`/`places` 캐싱·시설 카운트/얕은 복사, 앱 `TmapPilotMap` 경로선 dirty check·`PilotPreviewView` DrawAllocation 제거·`PilotData` 캐싱/`MainActivity` retained 재파싱 생략. 서버24(32.35s→16.90s)·도구13·Android27·빌드/lint 오류0/경고41 통과. 새 APK UI 재실행·실기기·현장·최종 인수는 미완료 유지. | [최적화 로그](log/log-2026-11-06-code-optimization.md) |
| 2026-11-06 12:55 KST | 사용자 요청에 따라 정왕역–한국공학대 1캠퍼스 정문 에뮬레이터 통합 테스트 수행 | 에뮬레이터(emulator-5556)에서 정왕역–한국공학대 1캠퍼스 정문 경로 검색 정상 동작 확인(빠른 경로 1942m·27.0분, 안전점수 12.4점). 전체화면 전환 및 지도 줌/표시 정상 동작 확인. 실기기 GPS/현장 보행 검증은 미완료 유지. | [E2E 검증 로그](log/log-2026-11-06-jeongwang-tukorea-e2e.md) |
| 2026-11-06 14:05 KST | 사용자 승인에 따라 네이버 지도 스타일 UI 전환(풀스크린 맵 + 슬라이딩 바텀시트) 및 검증 완료 | 지도를 화면 전체 배경으로 확장하고 상단 플로팅 검색 카드, 하단 120dp Material BottomSheet 적용. 단위27개·빌드 오류0, 에뮬레이터(emulator-5556)에서 경로 검색 및 바텀시트 슬라이딩 제스처 검증 완료. | [UI 전환 로그](log/log-2026-11-06-naver-map-ui.md) |

| 2026-11-06 | 변경 UI 새 캡처 검토 착수 | 연결 기기 없음/기존 시험 VM 부팅 지연, 별도 임시 환경으로 재시도. 과거 캡처3개 PNG 서명 무효 확인, 새 시각 검토는 진행 중. 앱 코드 변경 없음. | [로그](log/log-2026-11-06-ui-capture-review.md) |
| 2026-11-06 22:53 KST | 현재 APK UI 새 캡처/시각 검토 완료 | host GPU 시험 VM에서 정상 캡처. 상단 겹침·접힌 시트 요약 잘림·제목 가독성 문제 확인, h720dp variant 이전 구조 잔존. 미수정/인수 미완료, 과거 손상 캡처/환경 실패 보존. 앱 코드 변경 없음. | [검토](source/verification/ui-review-2026-11-06/verification.md), [로그](log/log-2026-11-06-ui-capture-review.md) |

| 2026-11-06 | 사용자 승인으로 캡처 UI3개 결함 수정 착수 | h720dp 이전 구조·고정120dp peek·투명 툴바/inset 원인을 확인. 새 UI 회귀/구현/검증 진행 중. | [계획](source/docs/superpowers/plans/2026-11-06-map-sheet-fixes.md), [로그](log/log-2026-11-06-ui-sheet-fixes.md) |
| 2026-11-06 23:46 KST | 사용자 승인 UI3개 수정/검증·설치 대상 갱신 | 상단 겹침·요약 잘림·가독성 수정, 시스템 막대/시트 경계 보완. 최종3프로필·단위27/도구13·lint 오류0/경고38 통과. 중간 실패 보존, 실기기/전체 인수는 미완료 유지. | [검증](source/verification/ui-sheet-fixes-2026-11-06/verification.md), [로그](log/log-2026-11-06-ui-sheet-fixes.md) |

| 2026-11-07 | 사용자 승인 경로 표시 개선 착수 | 표시 전용100m 필터/캐시·endpoint helper와 지정4개 단위 통과. UI/SDK 전환·최종 검증은 진행 중. 좌표/점수/서버 변경 없음. | [계획](source/docs/superpowers/plans/2026-11-07-route-display.md), [로그](log/log-2026-11-07-route-display.md) |

| 2026-11-07 | 경로 표시 개선 구현/검증·설치 대상 갱신 | 단위31/도구14·서버 UI8·화면3프로필 통과, lint 오류0/경고39. 중간 실패와 과거 APK 보존. 실제 도로/실기기/전체 인수 미완료 유지. | [검증](source/verification/route-display-2026-11-07/verification.md), [로그](log/log-2026-11-07-route-display.md) |

| 2026-11-07 19:41 KST | 사용자 승인 시설 아이콘 마커 변경 착수 | TMAP/로컬 공통28dp 카메라·호출 버튼·가로등·방패 vector 적용, 표시/상세 회귀 검증 중. 점수/DB 변경 없음. | [로그](log/log-2026-11-07-facility-icons.md) |

| 2026-11-07 | 시설4종 아이콘 마커/지정 검증·설치 대상 갱신 | 단위31·빌드·두 지도 직접 상세 열기/CCTV 필터 복구 통과, lint 오류0/경고40. 밀집 마커 겹침·경찰 실제 표시/실기기/전체 인수 미검증 범위 명시. | [검증](source/verification/facility-icons-2026-11-07/verification.md), [로그](log/log-2026-11-07-facility-icons.md) |

| 2026-11-07 20:03 KST | 비상벨 배터리형 아이콘을 클래식 종/울림 표시로 교체 | 공유 vector1개, 새 APK 빌드·API35 두 지도 캡처/설치 해시 확인. 단위/lint/전체 UI 재검사는 반복하지 않았고 실기기/최종 인수는 미완료 유지. | [로그/검증](log/log-2026-11-07-bell-icon.md), [APK](source/delivery/2026-11-07-bell-icon/README.md) |

| 2026-11-07 | 사용자 요청 시설 마커 겹침 묶음 착수 | 대표 아이콘/+총개수·목록/상세, 화면 투영 기반 확대/필터 재계산과 기존 overlay 배치 유지 구현/검증 중. | [계획](source/docs/superpowers/plans/2026-11-07-facility-clusters.md), [로그](log/log-2026-11-07-facility-clusters.md) |

| 2026-11-07 | 겹친 시설 묶음/최신 메타데이터·목록/상세 구현 및 지정 검증 완료 | 단위36·두 지도 목록/상세·필터·native 확대·빌드 통과, lint 오류0/경고41. 중간 숫자 가림 보완/검토 지적 해결. 원본/점수/DB 불변, 실기기/전체 인수는 미완료. | [검증](source/verification/facility-clusters-2026-11-07/verification.md), [로그](log/log-2026-11-07-facility-clusters.md) |

| 2026-11-07 | 사용자 승인 시설 제목을 종류/주소로 개선 착수 | 원본 행/좌표/기준일 대조 후 표시용 주소 보완, 도로명/지번/주소 없음 fallback과 내부 ID 보존 회귀 검증 중. | [로그](log/log-2026-11-07-facility-address-titles.md) |

| 2026-11-07 | 시설 종류/주소 제목·표시용 주소 보완 및 지정 검증 완료 | 원본508개 전수 대조, 주소2필드만 앱 자산에 보완/exporter 보존. 단위38·빌드·두 지도 목록/상세 통과, lint 오류0/경고41. ID/좌표/점수/DB 유지, 실기기/전체 인수 미완료. | [검증](source/verification/facility-addresses-2026-11-07/verification.md), [로그](log/log-2026-11-07-facility-address-titles.md) |
| 2026-11-08 00:09 KST | 사용자 요청 겹친 시설 마커 UI 개선 및 주소 목록 대신 종류별 개수(`CCTV 2개`, `비상벨 1개` 등) 요약 다이얼로그 적용 | `FacilityCluster` 종류별 집계(`summarizeFacilityCluster`)·카드형 커스텀 다이얼로그(`dialog_facility_cluster.xml`)·캡슐형 `+N` 배지 적용. 단위39·빌드 통과 및 에뮬레이터(`emulator-5556`) 클러스터 다이얼로그/상세 열기 캡처 확인. 실기기/전체 인수는 미완료 유지. | [로그](log/log-2026-11-08-cluster-kind-ui.md) |


| 2026-11-20 | 사용자 요청 병합 전 백업 및 UI 담당자 수정본 반영 | UI17개+테마 호환2개 반영. 빌드/단위/lint 검증 착수, 실기기/전체 인수 미완료 유지. | [로그](log/log-2026-11-20-ui-merge.md) |
| 2026-11-20 | UI 병합 후 빌드·단위·lint 검증 완료 | 새 APK 빌드/단위39개 통과, lint 오류0·경고50. R4 최신 결과 반영, 화면/실기기/전체 인수 미완료 유지. | [로그](log/log-2026-11-20-ui-merge.md), [실행 결과](log/ui-merge-2026-11-20-gradle.txt) |
| 2026-11-20 | 병합 APK API35 에뮬레이터 화면 검사 | 설치 해시 일치, 로컬 원본 서버 검색/지정 동작·최종 TMAP 표시 확인. 상태바 대비/겹침·작은 화면 부제/출처 문제 발견, 코드 수정 없음. DB 서버 시작 실패/로컬 대체와 실기기·전체 인수 미완료 구분. | [검증/캡처](source/verification/ui-merge-2026-11-20/verification.md), [로그](log/log-2026-11-20-ui-merge.md) |

| 2026-11-20 | DB 재활성화 후 병합 APK 재검사 | PostGIS startup_snapshot verified=true 및 API35 검색/지표 확인. 기본 경로 연결 미완결·기존 UI 문제·실기기/전체 인수 미완료 유지. | [검증/캡처](source/verification/ui-merge-2026-11-20/verification.md) |

| 2026-11-20 | 사용자 승인 하단 패널 숨김/요약/상세 구현 및 검증 | 기존 APK 숨김 실패 보존, 새 APK 단위39/빌드/lint 오류0·경고50, API35 일반/작은 화면 제스처·전체화면/복귀·DB 검색 통과. 실기기/전체 인수 미완료. | [검증](source/verification/three-stage-sheet-2026-11-20/verification.md), [로그](log/log-2026-11-20-three-stage-sheet.md) |

| 2026-11-20 | 사용자 피드백 반영: 숨김 상태에 복귀 손잡이 표시 | 투명 복귀 영역을 남색 바/밝은 손잡이로 변경하고 지도 여백 조정. 새 APK 단위39/빌드/lint 오류0·경고50, API35 일반/작은 화면 복귀와 비겹침 통과. 실기기/전체 인수 미완료 유지. | [검증](source/verification/three-stage-handle-2026-11-20/verification.md), [로그](log/log-2026-11-20-three-stage-sheet.md) |

| 2026-11-20 10:42 KST | 사용자 승인 상단 카드 최소화 착수 | 기존 APK 최소화 버튼 부재를 회귀 검사로 확인하고 최소화/오른쪽 위 확대 기능 구현 착수. | [계획](source/docs/superpowers/plans/2026-11-20-top-card.md), [로그](log/log-2026-11-20-top-card.md) |
| 2026-11-20 | 상단 카드 최소화/확대·지도 출처 연동 구현 및 지정 검증 | 새 APK 단위39/빌드/lint 오류0·경고50, API35 일반/작은 화면 토글·입력/요약 보존·전체화면 복귀·상하 독립성 통과. 실기기/전체 인수 미완료. | [검증](source/verification/top-card-2026-11-20/verification.md), [로그](log/log-2026-11-20-top-card.md) |

| 2026-11-20 | 사용자 피드백: 최소화 버튼을 저장 목록 왼쪽에 작게 배치 | 보이는32dp/아이콘16dp·터치48dp, 상태 문구 줄 복구. 새 APK 빌드/단위39/lint 오류0·경고50, API35 일반/작은 화면 위치·최소화/확대 클릭 통과. 실기기/전체 인수 미완료 유지. | [검증](source/verification/top-card-small-button-2026-11-20/verification.md), [로그](log/log-2026-11-20-top-card.md) |
| 2026-11-20 | 사용자 요청: 출발·도착 입력창의 `OSM 장소명 검색` 문구를 `장소 검색`으로 변경 | `strings.xml` 힌트와 `RouteWorkflow.kt` 검색 상태·다이얼로그 제목에서 `OSM` 표기 제거(출입구 미검증 안내는 유지). 진행 상태 불변, `testDebugUnitTest` 및 `installDebug`(`emulator-5556` 설치·실행) 통과(화면 캡처·실기기 미수행). | [로그](log/log-2026-11-20-place-search-label.md) |

| 2026-11-20 | 지도 길게 누르기 및 가까운 보행 지점 보정 가능성 조사 | SDK javap 정적 확인/서버30m 제한 확인. 사용자 보정 방향 기록, 기능 구현·UI/DB 검증 상태는 변경 없음. | [조사 로그](log/log-2026-11-20-map-long-press-feasibility.md) |

| 2026-11-20 | 사용자 승인 지도 길게 누르기 구현 착수 | 별도 snap API 및 지도 메뉴/보정 확인 후 검색 계획. 기존 미지원 메서드/HTTP404 실패부터 확인. | [계획](source/docs/superpowers/plans/2026-11-20-map-long-press.md), [로그](log/log-2026-11-20-map-long-press.md) |
| 2026-11-20 | 지도 길게 누르기/보행 node 보정·검색 구현 및 지정 검증 | 서버27/Android41·빌드/lint 오류0·경고50, DB 원거리 보정/기존30m 거절, API35 TMAP·로컬 검색/작은 화면 취소 확인. node 재선택 방식/파일럿 범위/미검증 간격 구분, 실기기·전체 인수 미완료. | [검증](source/verification/map-long-press-2026-11-20/verification.md), [로그](log/log-2026-11-20-map-long-press.md) |

| 2026-11-20 | 사용자 요청 보정 확인 창 삭제·자동 검색 전환 | 새 APK 빌드/Android41·lint 오류0·경고50, API35 TMAP 출발지/로컬 도착지 선택 즉시 자동 보정·검색 확인. 보정 거리/검증 유지. 이전 확인 창 인수 기록 보존, 실기기/전체 인수 미완료. | [최신 검증](source/verification/map-auto-snap-2026-11-20/verification.md), [로그](log/log-2026-11-20-map-long-press.md) |

| 2026-11-21 | 팀 GitHub 공유 전 제외 규칙/키 포함 산출물 점검 | source 설정 파일은 제외되지만 root UI ZIP1개와 복사 APK10개에 TMAP 키가 포함된 채 업로드 후보임을 확인. 규칙 보완/업로드 미실행. 앱 코드·구현/인수 상태 및 상태 기준일11-20 유지. | [점검 로그](log/log-2026-11-21-github-ignore-review.md), [검사 결과](source/verification/gitignore-review-2026-11-21/audit.json) |

| 2026-11-21 | 사용자 승인 GitHub 팀 공유용 제외 규칙/설정 예시 정리 | root/source gitignore로 키 포함 ZIP/APK·민감 설정·생성물 제외, 필수 소스/빈 예시 포함 및 임시 실제 git add 검증 통과. 검사한 비밀값/패턴0건. 업로드는 미실행, 앱/인수 상태 변화 없음. | [검증](source/verification/github-share-2026-11-21/verification.md), [로그](log/log-2026-11-21-github-share-preparation.md) |

| 2026-11-21 | 팀 공유 문서의 기존 발표 문서 링크 복구 | README/ROADMAP 링크를 현재 실제 파일명으로 연결. 앱 진행 상태·과거 결과·날짜 변화 없음. | [공유 정리 로그](log/log-2026-11-21-github-share-preparation.md), [문서 안내](README.md) |

| 2026-11-21 | 사용자 지정 GitHub 저장소 nightsafety 확인/최초 업로드 절차 안내 | 웹 빈 저장소 표시·원격 참조 없음, 로컬 미초기화 확인. 실제 init/커밋/푸시 미실행. 앱/인수 상태 변화 없음. | [공유 로그](log/log-2026-11-21-github-share-preparation.md) |
| 2026-11-21 | `.gitattributes` 추가(GitHub 언어 통계에서 초기 PoC HTML 제외) | `night-safety-project-readiness/osm_poc_v2/route-v2.html`을 `linguist-generated=true`로 지정. 기능·진행 상태 불변, 로컬 커밋까지 완료(푸시 미실행). | [.gitattributes](.gitattributes) |

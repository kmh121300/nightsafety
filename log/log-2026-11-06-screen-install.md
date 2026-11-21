# 화면 점검과 실기기 설치 준비

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

사용자가 사전 검사4번 진행을 승인했다. 09:54 KST 시작 시 서버/ADB 기기 연결이 없어 기존 가상환경 서버와 API35 Pixel_3a 임시 read-only 데이터를 재사용해 다시 기동한다. 첫 emulator 명령의 지원하지 않는 -quiet 옵션은 제거 후 실행했다. 기존 데이터 초기화 없음.

최초 APK SHA256 b50ae48ddaaa76ea933ad9f86821963f2f3d0aa3e9132f11b994012f2886084d(11월5일 검증본) 확인. 작은 화면·일반 화면에서 버튼/본문/스크롤·빈/오류 상태를 검사하고, 검증된 APK 복사본/해시·설치 안내/실기기 검사표를 묶는다. 해상도/밀도 변경은 검사용 에뮬레이터에 한정하고 원래 override 값으로 복원한다. 사용자 최종 디자인 판단·실제 GPS/제조사/현장은 완료로 표시하지 않는다.

앱 변경이 필요하면 관찰된 잘림만 최소 수정하고 영향을 받는 UI 및 새 APK를 확인한다. 서버 계산/DB/점수 정책·세로/글꼴 고정·ViewBinding 전환은 이번 범위가 아니다. [로드맵](../ROADMAP.md), [검사 순서](log-2026-11-05-pre-device-checks.md).

## 작은 화면 관찰 (2026-11-06)

첫320×568dp preflight는 Pixel Launcher ANR로 중단됐다. 복원 후 XML에서 외부 런처 이름을 확인하고 Wait를 선택했다. 앱 ANR로 단정하지 않는다. [당시 결과](../source/verification/android-2026-11-06_100121_899156/small-preflight.json), [복원 후 창](../source/verification/android-2026-11-06_100121_899156/after-restore.png).

실제 화면 검사는 [small-initial.png](../source/verification/android-2026-11-06_100411_221578/small-initial.png)와 geometry assert에서 preview 버튼48dp 미만 잘림을 재현했다. [실패 결과](../source/verification/android-2026-11-06_100411_221578/screen-result.json). 지도는 남은 높이를 가중 배분받는데 세 버튼을 세로로168dp 쌓아 작은 지도 영역을 넘어선 것이 원인이다.

기존 map XML은 layout-h720dp에 그대로 보존하고 기본(짧은 화면)은 같은3개 버튼을48dp 가로 행으로 배치한다. 동작/ID/48dp 최소 터치/기존 일반 화면 디자인을 유지한다. Kotlin/서버/DB 변경 없음. 새 레이아웃/빈·오류 상태를 재검사하고 새 APK를 묶는다.

## 수정 APK와 도구 보완 (2026-11-06)

lintDebug/assembleDebug 성공(4분2초). Kotlin compile은 UP-TO-DATE이며 앱 코드/DB 변화 없음. lint 오류0/경고33. APK SHA256 b863ec3a3387d83c66ee59bfba7f85d58fea52ddb7d781e81734660385b1f0e6, 설치 후 일치 확인. Android27개는11월5일 당시 단위 근거로 보존하며 이번 XML 변경에서 재실행한 것으로 쓰지 않는다.

수정본 small-initial 캡처에서 실제 지도 타일과 가로3개 버튼을 직접 확인했다. 작은 결과 viewport는 기존10회 반 화면 스크롤 탐색의 범위를 넘을 수 있어12번째 위치의 항목을 못 찾는 회귀를 먼저 실패시켰다. 최대20회로 늘리고 같은 화면이 반복되면 해당 방향 끝으로 판단해 불필요한 스와이프를 중단하도록 도구만 수정했다. 회귀 포함 도구13개 통과. 런타임 화면 검사는 계속 진행 중이며 최종 결과와 분리한다.

수정 APK 첫 전체 화면 시도는 지도 버튼/정상 수치까지 진행한 뒤 기존 실행 프로세스에 로드된10회 탐색 도구가 data_info를 못 찾아 중단됐다. [결과](../source/verification/android-2026-11-06_101106_812471/screen-result.json) 보존. 앱 잘림 재발로 분류하지 않는다. 보완한20회/끝 감지 도구로 두 화면과 빈/오류 검사를 다시 실행한다. 자료 정보 창은 native 본문 스크롤도 확인한다.

설치 파일은 source/delivery/2026-11-06/night-safety-mvp-debug.apk에 복사하고 SHA256SUMS.txt와 실제 바이트 해시 일치를 확인했다. 화면 검사 완료 전에는 묶음 검증 완료로 표시하지 않는다. DEVICE-TEST.md에 대상 기기 선택·install -r·reverse·실기기 미검증 표를 추가하고 기존 실행법.md의 호출 연산자 누락/버튼 위치/위험 단정 표현을 바로잡았다.

## 지정 화면 검사·설치 준비 완료 (2026-11-06)

[마지막 실행](../source/verification/android-2026-11-06_101527_916705/screen-result.json) 종료0·3개 검사 묶음/7개 지도 상태 통과, 복원 오류0. 작은/일반 지도·자료 창, 긴 목적지·빈/오류 캡처를 직접 확인했다. [종합 검증](../source/verification/screen-install-2026-11-06/verification.md), [APK 묶음](../source/delivery/2026-11-06/README.md), [설치/실기기 표](../source/DEVICE-TEST.md). 도구13개를 다시 실행해 통과했다. 원본/설치본/복사본 해시 일치, size/density/reverse 복원. 서버와 API35/5556은 유지한다.

다음 단계는 실제 휴대폰 USB 연결/디버깅 허용 뒤 GPS·권한·제조사별 동작과 사용자의 최종 UI 판단이다. 정해 둔 사전 검사4번까지의 준비 완료이며 전체 명세 차이/API36.1 과거 원인/현장/운영 인수 완료가 아니다.

마감 재확인: 원본/설치본/설치 복사본/manifest/체크섬 일치·두 지도 레이아웃 APK 포함·화면3묶음/지도7상태 근거 일치·설정/reverse 원복·앱/서버 ready 확인. 변경8개 문서의 최종 수정일2026-11-06·UTF-8·신규 링크 확인. 기존 발표 문서 링크2개 누락은 미해결로 보존. 최종 상태는 source/verification/screen-install-2026-11-06/final-state.json 참조.

# 휴대폰 설치와 실기기 검사

작성일: 2026-11-06 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

기기 연결 전 화면 검사와 설치 파일 준비는 [로드맵](../ROADMAP.md)을 따른다. 이 문서는 연결 후 절차이며 실제 휴대폰 검사를 완료했다는 기록이 아니다. Android 8.0(API26) 이상이 필요하다. 현재 앱은 대학–정왕역 파일럿·세로 고정·앱 글꼴 배율1.0이며, 경로 계산에는 PC 서버 연결이 필요하다. 지도 타일에는 인터넷이 필요하다.

## 설치 파일

검사된 복사본은 [2026-11-07 시설 종류/주소 설치 묶음](delivery/2026-11-07-facility-addresses/README.md)에 APK·SHA256·대상 검사 근거와 함께 보관한다. 소스에서 다시 빌드한 파일은 해시가 달라질 수 있으므로 해당 복사본과 구분한다. 이번 묶음은 개발용 debug APK이며 운영 배포본이 아니다.

## 연결과 실행

사용자는 휴대폰에서 개발자 옵션/USB 디버깅을 켜고 PC에 USB로 연결한다. 휴대폰의 PC 디버깅 허용 창을 승인하면 이후 설치·연결 검사를 진행할 수 있다. 기기 초기화나 앱 삭제는 필요 없다.

PowerShell 첫 창에서 서버를 실행한다. 이미 서버가 실행 중이면 중복 실행하지 않는다.

```powershell
Set-Location 'C:\2026591004\source\1-2\moblie\source'
.\.venv\Scripts\python.exe -X utf8 server/app.py
```

서버 창은 유지하고 다른 PowerShell 창에서 대상 기기를 지정한다.

```powershell
Set-Location 'C:\2026591004\source\1-2\moblie\source'
$taskAdb = "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe"
& $taskAdb devices -l
# 위 목록에서 실제 휴대폰의 일련번호를 입력한다. emulator-*는 가상 기기다.
$deviceSerial = '실제_휴대폰_일련번호'
$installApk = '.\delivery\2026-11-07-facility-addresses\night-safety-facility-addresses-debug.apk'
Get-FileHash -LiteralPath $installApk -Algorithm SHA256
(Invoke-RestMethod 'http://127.0.0.1:8765/health').data.health
& $taskAdb -s $deviceSerial install -r $installApk
# install의 Success를 확인한 뒤 이어서 실행한다.
& $taskAdb -s $deviceSerial reverse tcp:8765 tcp:8765
& $taskAdb -s $deviceSerial shell am start -n 'kr.ac.tukorea.nightsafety/.MainActivity'
```

`device`가 아닌 `unauthorized`이면 휴대폰의 허용 창을 확인한다. 서버 health는 `ready`여야 한다. USB 재연결/재부팅 뒤에는 reverse를 다시 설정한다. `install -r`는 기존 즐겨찾기를 유지하는 업데이트 방식이다. 다른 서명 때문에 실패하면 앱을 지우지 말고 설치 오류만 확인한다.

## 실제 기기 검사표

검사일·휴대폰 모델·Android 버전·화면 설정·설치 APK SHA256·항목별 결과/캡처를 기록한다. 아래는 모두 기기 연결 후 확인할 항목이다.

| 항목 | 확인할 동작 | 현재 상태 |
| --- | --- | --- |
| 설치/연결 | APK 설치 해시, 지도 타일, 서버 검색 정상 | 실기기 미검증 |
| 실제 위치 수신 | 내 위치 선택 후 실제 위치 점과 수신 실패 안내를 확인. 파일럿 밖이면 기존 출발지 유지가 정상 | 실기기 미검증 |
| 권한 거부 | 위치 권한을 거부해도 직접 좌표/OSM 장소 선택과 검색 가능 | 실기기 미검증 |
| 대략 위치 | 대략 위치만 허용했을 때 실제 수신과 파일럿 범위 판정 확인. 정확도 원/수신 시각 상시 표시는 미지원 | 실기기 미검증 |
| GPS OFF/시간 초과 | 기존 입력 유지와 실패 안내, 다시 켠 뒤 수신 회복 | 실기기 미검증 |
| 화면/터치 | 제목·긴 목적지·지도 버튼·결과 스크롤·키보드/대화상자가 실제 화면에서 조작 가능 | 실기기 미검증 |
| 검색/시설 | 후보·점수·경로 주변3시설 수·취약 표시. 필터가 경로 수치를 바꾸지 않음 | 실기기 미검증 |
| 저장/재시작 | 시험용 즐겨찾기 저장·재실행·오프라인 복원·수정·재조회·본 시험 항목만 삭제 | 실기기 미검증 |
| 응답/안정성 | 연속 입력·필터·복귀 시 종료/ANR 여부와 체감 응답 기록 | 실기기 미검증 |
| 사용자 UI 판단 | 사용자가 최종 디자인과 사용 흐름 검사 | 사용자 검사 대기 |

위치·네트워크·권한 설정을 시험 중 바꿨다면 원래 값으로 돌린다. 에뮬레이터의 모의 수신은 실제 GPS 정확도 근거가 아니다. API26~29는 최근2분 이내 위치를 사용하는 분기여서 최신 Android와 안내가 다를 수 있다.

## 현재 한계

그래프 연결 완료는 실제 야간 보행 가능성을 뜻하지 않는다. 정왕역 실제 출구 연결·현장 왕복 통행·이용조건·운영 HTTPS/성능 검증은 별도다. 과거 API36.1 앱 소실 원인은 미확정이며 이후 지정 검사에서 재현되지 않은 상태다. 지도 pin·지도 이동에 따른 시설 재조회 등 명세 차이는 [38개 대조표](verification/spec-audit-2026-11-05/functional-matrix.md)에 남아 있다. 휴대폰 설치 준비와 명세 전체 인수를 구분한다.

2026-11-06 준비 근거: [작은/일반 화면·설치 검증](verification/screen-install-2026-11-06/verification.md). 위 실기기 표의 상태는 여전히 미검증입니다.

2026-11-06 ViewBinding 전환 후 최신 설치 대상 갱신: [새 APK 검증](verification/viewbinding-2026-11-06/verification.md). 단위27·전체 UI 기능8개·small/pane 통과, 실기기 표는 미검증 유지.

2026-11-06 전체화면 추가 후 최신 설치 대상 갱신: [검증](verification/fullscreen-2026-11-06/verification.md). 실제 기기에서 전체화면→화면 복귀/뒤로, 지도 조작·검색 결과 유지도 확인한다. 위 실기기 검사 상태는 미검증 유지.

2026-11-06 UI 겹침/요약/가독성 수정 APK로 설치 대상을 갱신했다. [현재 검증](verification/ui-sheet-fixes-2026-11-06/verification.md). 실제 기기에서는 카드/지도 버튼 겹침·접힌 요약·손잡이/시스템 막대·전체화면 복귀를 함께 확인한다. 위 실기기 표는 미검증 유지.

2026-11-07 경로 표시 개선 APK로 설치 대상을 갱신했다. [검증](verification/route-display-2026-11-07/verification.md). 실제 기기에서는 선택 경로/출발·도착 핀·시설100m 표시·전체화면 복귀를 확인한다. 실기기 검사 표는 미검증 유지.

2026-11-07 시설 아이콘 APK로 설치 대상을 갱신했다. [아이콘 검증](verification/facility-icons-2026-11-07/verification.md). 휴대폰에서4종 아이콘의 식별/밀집 겹침·확대·직접 상세 열기를 확인한다. 위 실기기 검사 상태는 미검증 유지.

2026-11-07 비상벨 종/울림 리소스 수정 APK로 설치 대상을 갱신했다. [검증](../log/log-2026-11-07-bell-icon.md). 실기기 검사 상태는 미검증 유지.

2026-11-07 겹친 시설 묶음 APK로 설치 대상을 갱신했다. [검증](verification/facility-clusters-2026-11-07/verification.md). 실기기에서 +숫자/목록 개수 일치·상세·확대/축소·필터/경로 변경 후 갱신을 확인한다. 실기기 검사 상태는 미검증 유지.

2026-11-07 시설 종류/주소 표시 APK로 설치 대상을 갱신했다. [검증](verification/facility-addresses-2026-11-07/verification.md). 실기기에서 긴 주소/목록/상세 제목 가독성도 확인한다. 실기기 검사 상태는 미검증 유지.

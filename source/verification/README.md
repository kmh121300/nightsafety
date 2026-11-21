# Android 파일럿 검증 — 2026-10-16

작성일: 2026-10-16 · 최종 수정일: 2026-10-26 (문서 안내 추가) · 실제 검증일: 2026-10-16

초기 로컬 미리보기 검증 기록입니다. 이후 같은 날 실제 TMAP·통합 UI 검사가 추가됐고 2026-10-26에는 DB/API 검사와 앱 UI 미완료가 기록됐습니다. 현재 상태는 [전체 로드맵](../../ROADMAP.md), 최신 결과는 [DB 통합 검증](database-integration-2026-10-26.md)을 확인합니다. 아래 당시 미검증 항목을 현재 상태로 해석하지 않습니다.

## 빌드 및 정적 검사

```powershell
.\gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug --offline --console=plain
```

결과: **BUILD SUCCESSFUL**, 단위 테스트 5개 통과, lint 0 errors / 30 warnings.
경고에는 최신 target/Gradle 권고, 하드코딩된 한국어 UI 문자열, 미사용/중복 리소스 등이 포함됩니다. 검증한 설정은 compileSdk/targetSdk 36, Gradle 9.7.1, AGP 9.4.0, JDK 21입니다.

단위 테스트는 실제 시설 행수·좌표 순서·기준일·경로 거리·null 점수, 잘못된 좌표 거절, 시설 필터, 경로 단절 거절을 확인했습니다. 최초 실행에서는 미구현 PilotData 참조로 컴파일 실패한 뒤 구현 후 통과했습니다.

## 실행 검사

```powershell
python -X utf8 tools/smoke_test.py
```

Pixel_3a AVD / Android API 35에서 실제 APK를 설치해 다음 흐름을 통과했습니다.

- 기본 1,572m 경로와 시설 기록 511개 표시.
- 시설 목록에서 CCTV 상세 및 access_verified=false 확인.
- CCTV 제외 후 241개 표시, 보행선 우선 1,933m 경로로 전환.
- Android의 Activity 재생성 후 선택 경로와 체크박스 상태 유지. 테스트에서 변경한 always_finish_activities 설정은 복원.
- 위치 권한 요청 후 거부해도 기존 지도·경로 선택 유지.
- 앱 크래시 로그 없음. 기본 화면으로 되돌려 pilot-local.png 캡처 및 시각 확인.

AVD의 저장된 상태에서 런처/System UI 응답 없음이 발생해 snapshot 없이 부팅했습니다. 실행 도중 Digital Wellbeing의 응답 없음 창도 처리했습니다. 테스트는 앱 자체의 응답 없음과 시스템 앱의 응답 없음을 구분하며, 앱 자체 오류는 실패로 처리합니다.

## 검증 한계

팀 TMAP 앱키가 없어 인증된 실제 배경지도와 SDK overlay의 런타임 동작은 검증하지 않았습니다. 이번 실행 검사는 배경지도 없는 로컬 좌표 미리보기입니다. TMAP 통합 코드는 실제 공식 SDK를 대상으로 컴파일했습니다.

실제 기기 GPS, 유효한 위치 수신, 서버/DB, 새로운 출발·도착 검색, 안전점수와 실제 야간 보행은 검증 범위 밖입니다. 기존 경로의 실제 출구 연결은 계속 미검증입니다.

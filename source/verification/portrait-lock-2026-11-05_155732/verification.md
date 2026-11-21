# 세로 고정 검증

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자가 MVP의 세로 고정을 선택해 MainActivity 방향과 API36 대화면 호환 속성을 적용했다. 재부팅 전에 수정한 헤더 가변 높이/폭도 포함한다. 회전 데이터 복원 자체를 수정한 것은 아니다.

## 빌드

- `gradlew.bat testDebugUnitTest lintDebug assembleDebug`: 성공. 단위25개 실패0/오류0(단위 task UP-TO-DATE), lint 오류0/경고26.
- 새 경고2개는 `LockedOrientationActivity`, 대화면 opt-out의 `DiscouragedApi`. 숨기지 않고 MVP 범위 제한으로 기록했다.
- 병합 Manifest의 portrait 및 API36 opt-out 속성 assert 통과.
- APK: `app/build/outputs/apk/debug/app-debug.apk`, SHA256 `eb926bc609f00f52fc02adb34764f03e52540edf68e9133655e0c39b56658559`.

## API36 에뮬레이터 검사

[원시 검사 결과](result.json)의6개 검사 모두 통과했다. 기본 휴대폰 크기1080×2400/density420에서 시작 및 회전 요청1/3 후 세로 유지, 글꼴1.3에서도 세로 유지. 1200×1920/density240 태블릿 크기 모사에서 회전 요청1/3 후 세로900×1200 호환 창을 유지했다. 가로 화면에는 양옆 여백이 생긴다. 임시 화면/글꼴/회전 설정을 원래 값으로 복원했고 기존 에뮬레이터를 종료하지 않았다.

캡처를 직접 확인해 큰 글꼴의 상단 제목·부제목이 잘리지 않고 저장 목록이 한 줄로 표시됨을 확인했다. 태블릿 크기는 세로 호환 창/두 열 배치와 스크롤을 확인했다. 이는 실제 태블릿 하드웨어 검증이 아니다.

- [휴대폰 세로 유지](phone-portrait-lock.png)
- [큰 글꼴 헤더](phone-large-font.png)
- [태블릿 크기 세로 호환 창](tablet-size-portrait-lock.png)

## 한계

DB/서버/점수 및 Kotlin 동작 코드는 변경하지 않았다. 이 APK에서 전체 검색·Room UI8개나0거리 검사를 새로 실행한 것은 아니다. 이전 APK의 [기본 UI8개 성공](../android-2026-11-05_130904_166965/integration-ui.md)은 당시 기록으로 보존한다. 설정/창 크기 변경 시 상태 유실, 실기기 GPS·현장, 제조사별 방향 정책, 최종 사용자 UI 검사는 미완료다.

API36 호환 설정은 임시 기능이므로 target API37로 올리기 전 재검토한다. [공식 설명](https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts), [작업 로그](../../../log/log-2026-11-05-portrait-lock.md), [로드맵](../../../ROADMAP.md).

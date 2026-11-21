# MVP 세로 고정

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자가 회전 점수 유실을 설명받은 뒤 가로로 돌리지 못하게 하는 방식을 선택했다. MVP의 일반 사용은 세로 고정으로 바꾸고 회전 상태 복원 수정은 후순위로 남긴다. 이전 ANR·회전 실패와 당시 APK 검증은 보존한다. ViewBinding 전환·DB/점수 정책·서버/원본 데이터는 변경하지 않는다.

## 적용

- MainActivity에 `android:screenOrientation="portrait"` 적용.
- 현재 targetSdk36의 대화면 기본 동작에 대응해 Activity에 `android.window.PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY=true` 적용. [Android 16 공식 안내](https://developer.android.com/about/versions/16/behavior-changes-16#adaptive-layouts)에 따른 임시 호환 설정이다. target API37로 올릴 때 대화면 지원을 재검토해야 한다. 화면 자체가 가로여도 앱은 세로 호환 창으로 표시될 수 있다.
- 재부팅 전 `view_toolbar.xml`의 가변 높이/저장 버튼 폭 수정도 새 APK에 반영했다. 큰 글꼴에서 제목·부제목·버튼의 고정 크기 잘림을 줄인다.
- 기존 가로/600dp 리소스는 OS가 별도 창 크기를 제공하는 경우를 위해 보존한다. 설정 변경/프로세스 재생성의 상태 유실 버그를 수정했다고 주장하지 않는다.

## 검증

2026-11-05 Windows/JDK21/AGP9.4.0/Gradle9.7.1. `gradlew.bat testDebugUnitTest lintDebug assembleDebug` 성공. 기존 단위25개 실패0/오류0이며 Kotlin/단위 task는 변경 입력 없음으로 UP-TO-DATE였다. lint 오류0/경고26으로, 세로 고정/호환 opt-out 관련 LockedOrientationActivity·DiscouragedApi 경고2개가 추가됐다. 사용자 선택을 반영한 제한이므로 숨기지 않았다.

병합 Manifest에서 portrait와 API36 호환 속성을 assert했다. 새 APK SHA256: `eb926bc609f00f52fc02adb34764f03e52540edf68e9133655e0c39b56658559`.

실행 중이던 API36 에뮬레이터5558을 재사용했다. 휴대폰 크기1080×2400/density420, user_rotation1/3 요청 후 앱은 세로1080×2400 유지. font_scale1.3 캡처에서 헤더 잘림과 저장 버튼 강제 줄바꿈이 해소된 것을 확인했다. 태블릿 크기1200×1920/density240 모사에서 user_rotation1/3 요청 후 앱은 세로900×1200 호환 창을 유지했으며 양옆 여백을 확인했다. 자동화6개 assertion 통과, 임시 글꼴/회전/화면 크기/밀도 설정 복원 명령 성공. 기존 에뮬레이터는 종료하지 않았다.

[실행 결과와 캡처](../source/verification/portrait-lock-2026-11-05_155732/verification.md). 이번 검사는 방향 제한·헤더 배치에 한정한다. 새 DB import·검색/Room 전체 UI8개·보완된0거리 검사를 반복하지 않았다. 실기기/제조사별 강제 방향 설정·창 크기/글꼴 변경 시 상태 복원·최종 사용자 디자인 검사는 남아 있다.

마지막 확인에서 본 작업의 링크·날짜·검사 결과6개와 APK 해시 일치를 확인했다. 전체 문서 검사에는 이 작업과 무관한 `presentation-slides-ko.md`, `presentation-overall-guide-ko.md` 미존재 링크가 ROADMAP/README에서 관찰됐다. 다른 문서 작업을 덮어쓰지 않도록 해당 링크는 수정하지 않았다.

# MVP 앱 글꼴 배율 고정

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자는 시스템 글꼴 확대가 앱에 반영되지 않는다는 설명 후 앱 글꼴을 고정하는 방식을 선택했다. MVP의 Android 화면/대화상자는 기본 배율1.0으로 표시한다. 사용자의 휴대폰 글꼴 설정 자체를 앱에서 바꾸는 기능은 추가하지 않았다.

## 변경 범위

- MainActivity.attachBaseContext에서 빈 Configuration의 fontScale만1.0으로 지정한 Context를 사용한다. density·locale·화면 크기를 복사해서 고정하지 않는다. 기존 sp 크기/리소스와 Activity를 사용하는 RouteWorkflow의 대화상자도 같은 기준을 따른다. 새 의존성·ViewBinding·설정 화면은 추가하지 않았다.
- Manifest의 MainActivity는 fontScale 변경만 직접 처리한다. 글꼴 설정만 바뀔 때 Activity가 재생성돼 열린 창/검색 상태를 잃는 경로를 피한다. 다른 창 크기/프로세스 재생성 복원 문제를 해결했다고 주장하지 않는다.
- 출발/도착의 화면 읽기 설명, 버튼 터치 크기와 스크롤은 유지했다. **시스템 큰 글꼴을 따라 확대하는 기능은 사용자 선택에 따라 앱에서 사용하지 않으므로 공개 배포 전 접근성 정책을 재검토해야 한다.** 지도 렌더러/키보드/OS 권한 창의 글꼴은 이 앱 UI 고정 범위와 구분한다.
- [Context 공식 문서](https://developer.android.com/reference/android/content/Context#createConfigurationContext(android.content.res.Configuration))의 부분 설정 override를 사용했다. 비선형 글꼴 배율을 수식으로 역산하거나 scaledDensity를 직접 조작하지 않았다. [Configuration 설명](https://developer.android.com/reference/android/content/res/Configuration#fontScale).

## 실패 확인 → 수정 → 통과

새 `tools/font_scale_smoke.py`는 제목·부제목의 실제 UI 높이를 비교한다. 최초 검사에서 스크롤 영역의 점수 필드를 찾지 못한 [도구 실패](../source/verification/font-lock-2026-11-05_161534/failure.txt)를 보존했다. 비교 대상을 스크롤과 무관한 제목/부제목으로 바꾼 뒤 기존 APK에서 system1.3일 때 제목80→94px, 부제목43→56px로 변하는 [의도한 회귀 실패](../source/verification/font-lock-2026-11-05_161846/failure.txt)를 확인했다. 이 실패 후에 구현했다.

2026-11-05 Windows/JDK21/Gradle9.7.1/AGP9.4.0, API36 에뮬레이터5558(1080×2400/density420). `gradlew.bat testDebugUnitTest lintDebug assembleDebug` 성공, 단위25개 실패0/오류0, lint 오류0/경고26. 병합 Manifest의 portrait 및 configChanges=fontScale도 assert했다. 새 APK SHA256 `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9`.

수정 APK에서 시스템 배율1.3/2.0/0.85의 제목80px·부제43px 유지, 열린 자료 정보 창의 글꼴 변경 중 유지/같은 bounds, 출발·도착 contentDescription 보존, 시스템 배율2.0 상태의 새 시작 모두 통과했다. 캡처를 직접 확인해 기본 제목/저장 버튼/자료 정보 본문에 잘림이 없음을 확인했다. 검사 후 시스템 font_scale를 원래 값으로 복원한 것도 읽어서 확인했다.

읽기 전용 코드 검토에서 중요한 결함은 없었고, 제안된 큰 글꼴 상태 새 시작 검사도 추가해 실행했다. [결과와 캡처](../source/verification/font-lock-2026-11-05_162308/verification.md).

## 남은 범위

최신 APK의 전체 검색/Room UI8개·추가0거리, 실제 태블릿/GPS·TalkBack 실사용·최종 사용자 UI 검사는 이번 글꼴 검사에서 수행하지 않았다. 서버/DB/점수/원본 자료도 변경하지 않아 import를 반복하지 않았다. 이전 APK의 성공/실패는 당시 기록으로 보존한다. 일반 창 크기/프로세스 재생성 상태 복원은 기존 제한으로 남긴다.

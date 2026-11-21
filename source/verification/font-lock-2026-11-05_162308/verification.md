# 고정 글꼴 배율 검증

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자 선택에 따라 MVP 앱의 Android 글꼴 배율을1.0으로 고정하고 fontScale 변경 시 Activity 재생성을 막았다. 휴대폰 글꼴 설정/화면 밀도/언어를 앱이 전역 변경하지 않는다. 큰 시스템 글꼴의 앱 내 확대는 지원하지 않는다는 한계가 있다.

## 대상

- APK: `app/build/outputs/apk/debug/app-debug.apk`.
- SHA256: `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9`.
- Windows, JDK21/AGP9.4.0/Gradle9.7.1. 실행 대상은 기존 API36 에뮬레이터5558, 1080×2400/density420.
- `gradlew.bat testDebugUnitTest lintDebug assembleDebug` 성공, 단위25개 실패0/오류0, lint 오류0/경고26. 병합 Manifest의 portrait/configChanges=fontScale 검사 통과.

## 실제 실행

`python -X utf8 tools/font_scale_smoke.py --serial emulator-5558` 통과. [검사 결과 JSON](result.json).

| 검사 | 결과 |
| --- | --- |
| 시스템 배율1.3/2.0/0.85 | 제목80px·부제43px 유지, 기준1.0과 동일 |
| 자료 정보 창을 연 채 시스템 배율2.0으로 변경 | 창이 닫히지 않고 같은 bounds 유지 |
| 출발/도착 설명 | contentDescription 유지 |
| 시스템 배율2.0에서 앱 새 시작 | 기준 글꼴 크기 유지 |
| 검사 후 시스템 설정 | 원래 font_scale 값 복원 확인 |

직접 캡처를 확인해 제목·부제·저장 목록 버튼과 자료 정보 본문이 잘리지 않는 것을 확인했다. OS 상태 표시줄은 큰 시스템 글꼴을 따르며 앱 내부 글꼴 고정과 별개다.

- [앱 화면—시스템 배율2.0](fixed-app-system-scale-2.png)
- [자료 정보—시스템 배율2.0](fixed-dialog-system-scale-2.png)
- [큰 시스템 글꼴에서 새 시작](fixed-cold-start-system-scale-2.png)

수정 전 실제 글꼴 증가 [회귀 실패](../font-lock-2026-11-05_161846/failure.txt)와 최초 스크롤 필드 [검사 도구 실패](../font-lock-2026-11-05_161534/failure.txt)는 별도 보존했다. 실패를 성공으로 덮지 않았다.

## 한계

큰 글꼴 요청을 앱에 반영하지 않는 MVP 선택이므로 공개 배포 전 접근성 정책 재검토가 필요하다. 화면 읽기 설명 보존을 확인했지만 TalkBack 실기기 검사는 하지 않았다. 실제 태블릿·다른 OS/제조사, 창 크기/프로세스 재생성 복원, 최신 APK의 전체 검색/Room·0거리·사용자 최종 디자인 인수는 미완료다. 이전 [세로 고정 검사](../portrait-lock-2026-11-05_155732/verification.md)의 태블릿 크기 결과는 이전 APK의 근거다.

관련: [작업 로그](../../../log/log-2026-11-05-font-lock.md), [로드맵](../../../ROADMAP.md).

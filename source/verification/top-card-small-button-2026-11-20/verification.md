# 최소화 버튼 크기·위치 보완

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 시간 기준: Asia/Seoul

사용자 피드백으로 상태 문구 옆의 큰 최소화 버튼을 저장 목록 바로 왼쪽으로 옮겼다. 보이는 버튼32dp/아이콘16dp, 투명 부모의 터치 영역48dp. 상태 문구는 기존 독립 줄로 복구했고, 버튼 배치로 줄어든 공간에서 부제가 여러 줄로 늘어나지 않도록 한 줄 말줄임을 적용했다. 변경은 view_toolbar.xml 리소스에 한정하며 Kotlin 상태 동작/확대 버튼/DB/점수는 바꾸지 않았다.

## 2026-11-20 실제 검사

- 환경: Windows/JDK21.0.11/Gradle9.7.1, API35 Pixel_3a emulator-5556 host GPU.
- APK SHA-256: `f3a952dbf6a799575639dc68ef0757e0e79a0f32faaa18d4bee0350f66de3eba`. 설치 APK 해시 일치.
- assembleDebug/testDebugUnitTest/lintDebug: 종료코드0, BUILD SUCCESSFUL(41초). 단위39개/실패0/오류0. lint 오류0·경고50. [실행 기록](../../../log/top-card-small-button-2026-11-20-gradle.txt).
- 일반1080×2220/440dpi 및 작은720×1280/360dpi: 최소화 터치 영역이 저장 목록 왼쪽에 있고 두 영역의 세로 중심이 일치함을 bounds로 검사했다. 최소화/확대 클릭 왕복 성공.
- [검사 결과/측정값](result.json), [일반 화면](standard-button.png), [작은 화면](small-button.png) 직접 시각 검토. 화면 크기/밀도 복원.
- 이번 변경은 배치 보완으로 전체 제스처/DB/API·실기기·TalkBack 검사는 반복하지 않았다. 과거 검사는 각각 당시 APK 결과다.

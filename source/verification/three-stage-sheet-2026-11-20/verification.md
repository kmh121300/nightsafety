# 하단 패널 세 단계 검증

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 시간 기준: Asia/Seoul

## 변경과 대상

사용자 승인 동작: 상세→요약→완전 숨김, 숨긴 뒤 화면 하단48dp 영역에서 위로 스와이프→요약, 다시 위로 스와이프→상세. 숨긴 패널은 화면에 보이지 않는다. 하단 투명 복귀 영역은 탭/접근성 클릭으로도 요약을 연다. Android 시스템 탐색 영역 바로 위에서 동작한다.

Material BottomSheetBehavior 재사용. 상세 상태에서는 hideable을 꺼 한 번의 빠른 하향 제스처로 요약을 건너뛰지 않도록 한다. 요약으로 접으면 내부 스크롤을 처음으로 돌린다. 숨김 상태에는 지도 버튼/지도 가시 영역을 아래까지 확장하고 전체화면에서는 복귀 영역도 숨긴다. 태블릿의 기존 고정 패널은 변경하지 않았다.

대상: source의 이 변경 직후 APK. SHA-256 `d7ea7742c62c098598efd9022c12d6da6576935b9f6092e49daac495ee6e4d09`. 설치 APK 해시 대조 통과.

환경: Windows / JDK21.0.11 / Gradle9.7.1 / compileSdk36 / Pixel_3a AVD emulator-5556 Android15(API35) host GPU.

## 실제 검사

- 변경 전 [실패 기록](../android-2026-11-20_102608_038611/three-stage-result.json): `Summary did not hide`. 기존 APK의 미지원 동작을 먼저 재현했다.
- 최종 `assembleDebug testDebugUnitTest lintDebug --console=plain`: 종료코드0 / BUILD SUCCESSFUL(42초). 단위39개, 실패0/오류0. lint 오류0·경고50. [실행 기록](../../../log/three-stage-sheet-2026-11-20-final-gradle.txt).
- 일반1080×2220/440dpi [회귀 PASS](../android-2026-11-20_102931_327047/three-stage-result.json): 요약→숨김→하단 스와이프 요약→상세→빠른 하향 요약→숨김, 숨긴 상태 전체화면 진입/복귀, 복귀 영역 클릭 성공.
- 일반 화면 [숨김](../android-2026-11-20_102931_327047/hidden.png), [요약](../android-2026-11-20_102931_327047/summary.png), [상세](../android-2026-11-20_102931_327047/detail.png) 캡처 직접 검토.
- 작은720×1280/360dpi(320×568dp) [동일 회귀 PASS](../android-2026-11-20_103045_292374/three-stage-result.json). [숨김 캡처](../android-2026-11-20_103045_292374/hidden.png) 직접 검토. 완료 후 원래1080×2220/440dpi 복원.
- [DB health](db-health.json): database.verified=true, PostGIS startup_snapshot. 기기8765→호스트8766 reverse를 사용. 새 APK의 검색 완료 및 [요약 표시](db-search-summary.png) 확인. DB는 시작 시 읽고 경로는 메모리에서 계산한다. DB 쓰기는 수행하지 않았다.

## 한계

실기기/제조사별 제스처·TalkBack 실제 실행·태블릿 고정 패널·전체 명세 인수는 미검증. 이전 상태바 대비/상단 겹침·작은 화면 부제/출처 문제는 이번 변경 범위 밖이며 해결로 기록하지 않는다. 점수/DB/서버/자산 데이터 변경 없음. 새 단위 로직 테스트 대신 실제 제스처 회귀 검사를 추가했다.

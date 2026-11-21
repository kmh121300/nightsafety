# 지도 UI 겹침/요약 잘림/가독성 수정

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

사용자가 현재 캡처에서 확인한3개 문제 수정을 승인했다. [수정 전 캡처 검토](../source/verification/ui-review-2026-11-06/verification.md), [계획](../source/docs/superpowers/plans/2026-11-06-map-sheet-fixes.md).

범위: 공통 map_panel/toolbar·phone/pane inset 처리·실제 요약 높이 기반 BottomSheet.peekHeight와 버튼 행 배치. h720dp에 남은 이전 map_panel을 제거한다. 호출자 MainActivity의 applyServerData 시트 접기와 전체화면/복귀도 함께 유지한다. 기존 ViewBinding/지도 인스턴스·서버/DB/Room/점수는 유지한다.

새 tools/map_sheet_smoke.py가 설치/빌드 APK 해시·버튼48dp/헤더 겹침·접힌 요약/탐색 막대 여백·시트 드래그·전체화면/뒤로·화면 설정 복원을 확인한다. 현재 APK 실패 검증을 진행 중이다. 실기기/전체 기능 인수는 별도다.

## 실패 재현과 구현

기존 APK에서 새 UI 회귀가 `Map buttons overlap search/header`로 실패했다. [수정 전 결과](../source/verification/android-2026-11-06_231559_899973/map-sheet-result.json). 실패 캡처/해시·화면 설정 복원 기록 보존.

h720dp map_panel을 제거해 공통 ViewBinding 배치를 사용한다. map_actions48dp 가로 행을 접힌 시트 위에 배치하고, 전체화면/고정 pane에서는 탐색/출처 여백 위에 놓는다. 요약의 실제 descendant rect 하단+12dp+탐색 inset으로 peekHeight를 계산하고 layout 변경 시 갱신한다. 기존 server-result 접기는 nullable sheet를 재사용한다. 툴바는 ui_card/10dp padding, phone은 top_container 바깥 margin에 상태바 inset을 적용하며 pane은 루트 안전 padding을 유지한다. 지도 view/카메라·경로/필터·DB/Room/서버/점수 변경 없음. 새 빌드/검증은 진행 중.

## 첫 빌드/실행 실패 보존

빌드·단위/lint는 성공했지만 첫 새 APK UI 검사는 홈 화면에서 Control ScrollView missing으로 실패했다. 앱 crash buffer를 로컬 메모리에서 예외 종류/프로젝트 stack만 추려 확인했고 ViewMapPanelBinding.bind의 RuntimeException/NullPointerException을 확인했다. SDK 원문/키/URL은 출력/저장하지 않았다. 소스에서 h720dp가 제거됐는데 AGP merged_res에 layout-h720dp-v13_view_map_panel.xml.flat이 남아 새 필수 map_actions와 맞지 않았다. 앱 빌드 산출물을 Gradle clean으로 재생성해 확인한다. 실패는 성공으로 덮지 않는다. [실패 UI](../source/verification/android-2026-11-06_231942_288409/map-sheet-result.json), [당시 빌드](../source/verification/ui-sheet-fixes-2026-11-06/build-before-clean.json). 원본 소스/DB/사용자 데이터 삭제는 하지 않는다.

## clean 후 일반 화면 통과, 작은 화면 추가 보완

Gradle clean 후 merged_res에서 삭제된 h720dp flat이 사라졌고 새 APK 일반 화면 회귀 통과. [당시 결과](../source/verification/android-2026-11-06_232446_116324/map-sheet-result.json), [당시 빌드](../source/verification/ui-sheet-fixes-2026-11-06/build-clean-intermediate.json). 직접 캡처에서 상단 겹침 해소·흰 카드·요약 전체 표시를 확인했다. 다만 다음 heading이 탐색 막대 아래로 비쳐 요약 뒤 여백을8dp로 줄이고 phone 하단에 탐색 inset 높이의 흰 scrim을 추가한다. 전체화면에서는 scrim을 숨겨 SDK 출처 표시를 가리지 않는다.

작은 화면의 펼친 시트 top이 상태바에 닿아 닫기 swipe가 OS 알림창을 여는 실패를 확인했다. [실패](../source/verification/android-2026-11-06_232536_601053/map-sheet-result.json). sheet 상단 margin에 status inset+12dp를 적용해 확장 손잡이를 상태바 아래에 둔다. 새 테스트도 손잡이 안전 높이를 검사하고 시험 알림창을 collapse로 정리한다. 원래3개 UI/시스템 막대 겹침 수정 범위의 보완이며 새 기능/서버 변경은 없다.

## 시트 상단 제한 방식 보완

상단 margin 방식은 Material BottomSheet의 위치 offset에 margin이 추가돼 접힌 시트까지 아래로 밀리는 회귀를 만들었다. 새 검사에서 Summary collides with navigation bar로 실패했으며 [당시 결과](../source/verification/android-2026-11-06_232929_454556/map-sheet-result.json)/[빌드](../source/verification/ui-sheet-fixes-2026-11-06/build-margin-intermediate.json)를 보존했다. margin을 제거하고 공식 maxHeight로 root 높이-status inset-12dp를 제한한다. 루트 실제 크기/요약 layout 변경 시 계산하며 같은 높이/버튼 여백일 때는 requestLayout을 반복하지 않는다. [Material1.10 원본](https://raw.githubusercontent.com/material-components/material-components-android/1.10.0/lib/java/com/google/android/material/bottomsheet/BottomSheetBehavior.java)의 onMeasureChild/onLayoutChild/setMaxHeight 동작을 확인했다. 설정/버전/추가 의존성 변경 없음.

## 최종 높이 제한/제스처 확인

maxHeight 수정 APK의 첫 small 자동 검사는 Sheet did not expand로 실패했다. [기록](../source/verification/android-2026-11-06_233322_411588/map-sheet-result.json). 같은 APK를 별도 직접 제스처로 확인해 expanded y81/collapsed y865 전환을 관찰했다. [진단](../source/verification/android-2026-11-06_233825_773924/drag-diagnosis.json). 캡처 대기 동안 레이아웃/시트 위치가 바뀔 수 있는데 자동 스와이프가 이전 bounds를 사용했다. 캡처 뒤 최신 bounds를 다시 읽고 일반600ms 스와이프로 검사하도록 고쳤다. 앱 코드는 추가 변경하지 않았다. 최종 small 회귀는 통과했고 expanded 손잡이가 상태바 아래에 있는 캡처를 직접 확인했다. [최종 small](../source/verification/android-2026-11-06_234052_220447/map-sheet-result.json). standard/pane 검사 진행 중.

최종 코드의 maxHeight/peekHeight/버튼 여백 변경 guard와 scrim의 phone-only/fullscreen 숨김을 별도 검토했고 중요한 지적 없음. 런타임 검증은 별도 근거를 따른다.

## 최종 완료 2026-11-06 23:46 KST

최종 APK `259dec689c428456ac244bff7333400533d94eaf80e6e86a6152881e19310fd3`의 small/standard/pane3개 프로필 회귀 통과, 각각 cleanup_errors0/종료0. 표준 기본/전체화면·작은 화면 펼침·대화면 고정 패널 캡처를 직접 확인해 겹침/요약/흰 배경·안전 손잡이·전체화면 출처를 확인했다. [종합 검증](../source/verification/ui-sheet-fixes-2026-11-06/verification.md), [설치 묶음](../source/delivery/2026-11-06-ui-sheet-fixes/README.md).

최종 단위27개 실패0/오류0·도구13·빌드 성공, lint 오류0/경고38. 독립 최종 코드 검토 중요 지적 없음. ROADMAP/source README/DEVICE-TEST·APK/manifest/checksum/계획 체크를 갱신했다. 과거 APK 묶음/성공/실패를 보존한다. 서버/DB/Room/점수 정책은 변경하지 않았으며 전체 API/Room·GPS/권한/실기기·임의 창 크기·성능·사용자 최종 UI 인수는 이번에 재검증하지 않았다.

최종 대조 2026-11-06 23:47 KST: 변경 문서7개 수정일/내부 링크 통과(기존 무관한 발표 문서 누락2개 제외), 빌드/보관/설치 APK·manifest·checksum 해시 일치, 최종 UI3개 PASS/cleanup0·PNG 형식 확인. 단위27/실패0/오류0·lint 오류0·ViewBinding 직접 검색0·단일 map_panel 및 stale h720 flat 없음 재확인. 화면1080×2220/density440 복원, reverse8765 구성, 앱 PID11704 실행. 서버 health/API/DB는 이번에 검사하지 않았다. 이후 앱 코드 변경 없음.

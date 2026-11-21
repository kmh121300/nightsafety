# 변경 UI 캡처 검토

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

사용자 요청: 바꾼 UI를 현재 APK에서 새로 캡처해 확인. 코드 변경/수정 요청은 아님.

대상 APK: source/app/build/outputs/apk/debug/app-debug.apk, 2026-11-06 14:01:49 빌드 파일, SHA256 039efba8118cdc538581bb4aebd49a900b609d54ca3f5640597c0fc8ddf870b9. 이후 더 최신 Kotlin/XML 소스가 없는 것을 확인했다. 현재 UI는 CoordinatorLayout 전체 지도·플로팅 상단 검색·NestedScrollView/Material BottomSheet 구조다.

22:37 KST 검사 시작 시 연결된 기기/에뮬레이터가 없었다. 기존 API35 Pixel_3a 임시 데이터를 read-only로 실행했으나 Google 부팅 화면에서 지연되고 APK 설치에 실패했다. 앱 UI 오류로 분류하지 않는다. 해당 VM만 종료하고 원래 데이터는 보존했으며 별도 새 임시 datadir로 재시도 중이다. 새 환경도 API35이며 과거 UI 로그의 API36.1 표기를 이번 검증 환경으로 인용하지 않는다.

기존 verification/naver_map_style.png·naver_map_collapsed.png·naver_map_bottomsheet_expanded.png는 이미지 도구에서 열리지 않았고 PNG signature 검사3개 모두 실패했다. 원본을 변경하지 않고 새 캡처를 바이너리 subprocess 출력으로 저장한다. 현재 UI 성공을 이전 손상 캡처로 판단하지 않는다. [당시 UI 로그](log-2026-11-06-naver-map-ui.md)는 당시 기록으로 보존한다.

현재 새 캡처/시각 검토는 진행 중. 빌드/DB 재가져오기·서버 변경은 하지 않았다. 실기기나 전체 기능/성능 인수 검사가 아니다.

## 22:53 KST 캡처 검토 완료 — 결함 미수정

새 SwiftShader VM도 검은 화면/외부 System UI ANR이 발생했다. 해당 시험 VM만 종료하고 동일 임시 datadir를 host GPU로 재시작한 뒤 앱 화면을 확보했다. 앱 설치/빌드 SHA256 일치, API35 확인. 지도 준비 완료 이후 기본/펼친 캡처와 전체화면/복귀를 직접 확인했다. [검토 보고서](../source/verification/ui-review-2026-11-06/verification.md), [기본](../source/verification/android-2026-11-06_225004_601791/ui-ready-collapsed.png), [펼침](../source/verification/android-2026-11-06_225004_601791/ui-ready-expanded.png).

발견: 상단 버튼/저장 목록/상태바 겹침, 120dp 접힌 시트 하단 요약 잘림, 투명 툴바 문구와 지도 라벨 겹침. h720dp 지도 레이아웃에 이전 버튼 구조가 남아 있는 것을 확인했다. 사용자 요청은 확인이므로 앱 코드를 수정하지 않았으며 UI 인수 완료로 표시하지 않는다. 시작/펼침/전체화면/복귀 캡처와 measured bounds/해시/외부 시스템 창1회는 날짜 폴더 visual-review.json에 보존했다. 최초 로딩 중 캡처도 보존했고, 최종 캡처와 구분한다.

현재 에뮬레이터는 기본 접힌 화면으로 복귀해 실행 중이다. 서버/DB/Room 전체 흐름·실기기·다른 화면·성능은 이번에 검사하지 않았다. 이전 실제 데이터와 설치 묶음은 보존했다.

# 지도 전체화면 전환

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

사용자가 전체 보기 버튼을 전체화면으로 바꾸고 지도만 화면에 나오도록 요청했다. 기존 MainActivity listener는 preview.reset/map.reset만 호출하며, TMAP reset은 고정 중심/zoom14 복귀다. 확대 UI는 구현돼 있지 않았다.

범위: 기존 ViewBinding/지도 인스턴스를 유지하고 toolbar/search/results를 GONE 처리, 루트 여백과 pane 지도 margin을 임시 제거한다. 지도 위 내 위치·로컬 전환·전체화면 해제 및 SDK/OSM 출처는 유지한다. 해제 버튼/시스템 뒤로로 복귀, 선택 경로/필터/검색 결과 보존. 시스템 상태/탐색 막대는 유지한다. 서버·DB·Room·점수 정책은 변경하지 않는다.

검증 계획: 먼저 기존 APK에서 새 UI smoke의 명칭/확장 실패를 기록한 뒤 구현한다. 빌드·단위/lint와 API35 표준/작은/pane에서 TMAP/로컬 진입·해제/뒤로·패널 숨김/지도 크기·결과 보존을 확인한다. 실기기/사용자 최종 판단은 별도다. 기존 ViewBinding APK와 근거는 보존한다.

구현: MainActivity setMapFullscreen에서 패널 visibility·pane margin·루트 inset 여백·버튼 문구를 전환한다. 지도 view를 다시 만들거나 camera reset을 호출하지 않는다. savedInstanceState에 fullscreen 여부를 보존하고 Android33+ dispatcher/이전 OS onBackPressed로 해제한다. API 참고: https://developer.android.com/reference/android/window/OnBackInvokedDispatcher . 새 전체화면 smoke는 기존 APK에서 Fullscreen button label missing으로 실패한 뒤 변경했다. 새 빌드/UI 검증은 진행 중이다.

## 빌드와 중간 관찰

최초 빌드의 lint는 구형 onBackPressed fallback에 GestureBackNavigation 오류1개를 보고했다. Android33+는 이미 OnBackInvokedCallback 등록/해제로 처리하므로 이전 OS fallback 메서드에만 사유를 적은 SuppressLint를 적용했다. 전체 lint를 끄지 않았다. 이후 빌드 성공, 최종 해제 문구 줄바꿈 반영 빌드도 성공했다. 최종 단위27개 실패0/오류0, lint 오류0/경고41, 도구13개 통과. [빌드 기록](../source/verification/fullscreen-2026-11-06/build-result.json).

독립 read-only 코드 검토에서 중요한 결함 없음. 일반 화면 중간 APK에서 TMAP·로컬 진입/버튼 해제·뒤로 복귀/결과 유지 통과. 해제 문구가 좁은 버튼에서 어색하게 나뉘는 캡처를 확인해 명시적 두 줄로 정리했다. 이 중간 검사 중 빌드 산출물이 바뀌어 도구의 종료 시점 해시와 설치 해시가 달랐다. 설치본 SHA256을 별도로 확인해 원래 기록값/정정 이유를 함께 보존했고, 새 도구는 검사 시작 전 설치본과 빌드본 해시를 일치 확인한 뒤 해당 값을 고정한다. [중간 보고서](../source/verification/android-2026-11-06_112124_491485/fullscreen-result.json). 최종 APK의 standard/small/pane 재검사는 진행 중이다.

## 캡처 기반 복귀 문구 보완

중간 두 줄 `전체화면/해제` 문구는 작은 화면48dp 버튼에서 아래 글자가 잘릴 가능성을 캡처로 확인했다. 한 줄 `화면 복귀`로 최종 변경했다. 진입 문구 `전체화면`은 유지한다. 이전 문구 APK의 standard/small/pane 각 TMAP/로컬2개씩 총6개 UI 흐름은 통과했고 결과/해시를 보존했다. 최종 APK와 이 직전 APK의 모든 DEX가 동일함을 직접 비교했다. 마지막 변경은 strings 리소스만이며 최종 빌드 성공, 단위27개는 동일 코드의 UP-TO-DATE, lint 오류0/경고41. [최종 빌드](../source/verification/fullscreen-2026-11-06/build-final-result.json). 최종 APK에서 small/pane 문구·지도 확장/숨김·버튼/뒤로 복귀를 별도 확인 중이다.

최종 문구의 빠른 재검사1회는 `Return caption missing`으로 실패했다. 실패 캡처는 전체화면이 아닌 정상 화면이며, 초기 지도 준비 직후 캐시된 bounds로 한 번 tap한 방식이었다. 실패와 설정 복원0오류를 [당시 기록](../source/verification/android-2026-11-06_113236_719693/final-caption-result.json)으로 보존한다. 앱 코드 추가 변경 없이 기존 Smoke.click의 화면 안정화/좌표 재확인을 사용해 최종 small/pane 전체 경로 흐름 검사를 다시 수행한다. 재검사 전에는 실패 원인을 앱 결함 해결로 단정하지 않는다.

## 최종 완료

최종 APK `eb23f011afd8758722af2eaee31164216dbaa997b89b450771963d88034cc38d` 설치 해시 일치 후 small/pane 각각 TMAP/로컬 진입·지도 확장·패널 숨김·버튼/뒤로 복귀·검색 결과 유지4개 통과, 두 검사 종료0/cleanup_errors0. 앱 추가 수정 없이 안정화 click helper로 초기 빠른 tap 미진입 이후 재검사했다. 최종 small/pane 캡처를 직접 확인해 한 줄 화면 복귀와 지도·출처 표시를 확인했다. [최종 검증](../source/verification/fullscreen-2026-11-06/verification.md).

설치 묶음/manifest/해시·ROADMAP·source README·DEVICE-TEST 갱신. 이전 ViewBinding/다른 APK 묶음과 중간 성공/실패를 보존했다. 일반 화면은 동일 DEX 직전 문구 근거이며 최종 APK에서 동일 전체 UI8개/오류권한/API36/구형 OS/실기기·프로세스 재생성을 반복한 것은 아니다. 실제 사용자 최종 UI·GPS/제조사 인수는 별도다.

최종 대조 2026-11-06 11:40 KST: 변경 문서6개의 수정일/내부 링크 통과(기존 발표 문서 누락2개 제외), 빌드·보관·설치본·manifest·checksum 해시 일치, 최종 UI 보고서2개 PASS/cleanup0·lint 오류0 확인. 화면1080×2220/density440 복원, reverse8765·health ready·앱 PID18478 실행 확인. 이후 앱 코드 변경 없음.

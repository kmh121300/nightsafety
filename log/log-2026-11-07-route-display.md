# 경로 표시 가독성 개선

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

사용자가 선택 경로 강조·후보 흐리기·출발/도착 핀·시설 밀도 낮추기를 승인했다. [계획](../source/docs/superpowers/plans/2026-11-07-route-display.md). 기존 코드는 모든 후보를 동시에 그리고 등급선을 같은7f 두께로 덮었다. TMAP에는 endpoint 핀이 없고 필터를 통과한 시설1381개를 모두 그렸다. 실제 지도 좌표 변경이나 경로 연결 검증 완료로 해석하지 않는다.

변경 도달 범위: TmapPilotMap/PilotPreviewView·PilotData의 표시 전용 캐시·MainActivity 요약/시설 목록·지도 캡처/회귀/설치 안내. SDK의 outline/priority/marker anchor public API는 현재 AAR의 javap로 확인했고 공식 TMAP 업데이트/가이드도 참조했다. 기존 segment 등급/취약 표시·점수/DB/Room·정식3유형 정책은 유지한다. 시설100m 제한은 표시 전용이며 보유 기록 수와 표시 수를 구분한다.

RouteDisplayTest4개를 먼저 추가해 미구현 facilitiesNearRoute/mapFacilities/routeEndpoints 참조 실패를 확인했다. 공통 필터와 캐시/endpoint helper 구현 후 지정4개가 통과했다. 경로 중간 근접/100m 밖·polygon 교차/내부·캐시/필터/선택 변경·점수/원본 좌표 불변·미완결요청 endpoint/0거리/경로 없음 검사를 포함한다. 전체 앱/SDK 검증은 아직 진행 중이다.

## 렌더링 구현과 첫 캡처 보완

TMAP/로컬 지도 모두 공통100m 목록·선택 선/흰 테두리·옅은 후보·출발/도착 핀을 적용했다. 등급은 선택 선 안쪽4f(TMAP)/2dp(로컬), 취약은 주황6f/3dp로 유지한다. MainActivity는 보유 필터 기록 수와 지도100m 표시 수를 분리하고 시설 목록/로컬 hit-test도 같은 목록을 사용한다. 경로 변경 시만 근접 계산을 캐시하며 기존 오버레이 배치/diff 큐를 유지한다.

첫 캡처에서 기본 경로 시설1381→49개 표시와 로컬 핀/흰 테두리는 확인했다. [첫 캡처](../source/verification/android-2026-11-07_003310_118784/route-display-preview.json). TMAP 첫 표시의 도착 핀이 카드에 가리고, 선이 출발 라벨 위에 겹쳐 추가 보완했다. 공식 SDK 문서(https://tmapapi.tmapmobility.com/androidVSM/docs/androidDoc.html)와 AAR 공개 API를 확인해 낮은 priority가 위에 그려지도록 핀1/취약2/등급3/선택4/흰 테두리5/후보9 순으로 지정했다. 흰 테두리는 동일 원본 좌표의 별도 casing 선으로 표시한다.

선택/검색 경로가 바뀌거나 보이는 지도 영역이 바뀌면 SDK fitBounds+Insets로 카드/시트/버튼 여백을 고려해 전체 경로와 요청 endpoint를 맞춘다. 같은 필터/취약 토글은 경로를 재맞추는 조건에 넣지 않았다. 아주 짧은 화면에서 카드 사이 공간이 부족하면 전체 지도 여백으로 fallback하므로 전체화면으로 전체 경로를 확인한다. 이 카메라 맞춤은 새 표시 정책이며 이전 카메라 유지 방식에서 변경된 범위다. Native 뷰의 실제 크기 변경/닫힘도 검사한다. 경로 좌표/점수/연결 상태는 변경하지 않는다.

서버는 처음 health 미응답이어서 기존 설정의 로컬 Python 서버를 숨김 실행했다. DB 가져오기/변경은 수행하지 않았다. 실제 API/UI 검증은 이어서 진행한다.

## 최종 검증과 설치 대상

검사일2026-11-07 KST. API35 Pixel_3a emulator-5556, Intel Arc host GPU, 별도 read-only 시험 환경. 단위31 실패0/오류0·빌드 성공8s, lint 오류0/경고39. 도구14개 통과. 새 회귀는 펼친 시트에 가린 입력을 접고 조작하는지를 검증한다. 앱 준비 이전 ScrollView 조회와 시트 뒤 입력 클릭으로 실패한 두 번의 UI 보고서를 보존하고 자동 검사에 앱 준비 대기/시트 접기를 반영했다. 앱 코드 재변경 없이 최종 APK로00:57 KST 서버 검색·anchor/공식 점수·취약 상세/토글·필터·Room 저장/재시작/오프라인/수정/재조회/삭제8개 모두 통과했다. 시험용 즐겨찾기만 삭제했다.

01:04~01:07 KST small/standard/pane3개 회귀 모두 PASS, cleanup_errors0. 화면 크기/밀도 복원. 일반/native 전체화면·로컬 전체화면 최종 캡처를 직접 열어 선/핀/후보/시설 감소를 확인했다. 약한 지표 토글 동작은 UI8에서 확인했으나 해당 자동 캡처는 결과 패널이 펼쳐져 있어 지도 취약선 외관 확인 근거로 쓰지 않는다. 독립 코드 검토는 필터/캐시/endpoint/overlay queue/viewport 및 현재 위치 focus guard에 중요 회귀 지적 없음. 앱 소유 findViewById 없음 유지.

[최종 검증/실패/캡처 링크](../source/verification/route-display-2026-11-07/verification.md), [설치 APK/해시](../source/delivery/2026-11-07-route-display/README.md). ROADMAP R4/현재 위치/별도 변경 이력과 README/DEVICE-TEST/계획을 갱신했다. 이전 APK/실패/작성·검증일은 보존했다. 서버 health ready이며 DB 재가져오기/전체 복원·서버 단위/성능 검사는 반복하지 않았다. 실제 도로 정합성·현장/실기기 GPS/OEM·일반 창/프로세스 복원·전체 명세/운영 인수는 미완료다.

최종 정합성 검사: 변경 문서 수정일/내부 링크(기존 발표 문서2개 누락 제외), 빌드 APK/설치 APK/보관 APK/manifest/SHA256SUMS 해시 일치 PASS. 화면1080×2220/density440 복원, 앱 실행 중·서버 health ready, 앱 소유 findViewById0개 확인. 코드 추가 변경 없이 문서/설치 복사본만 정리했으므로 재빌드는 반복하지 않았다.

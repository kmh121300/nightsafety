# 겹친 시설 마커 묶음 검증

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

검사일2026-11-07 20:14~20:18 KST. API35 Android15 Pixel_3a emulator-5556/host GPU, 기존 별도 임시 read-only VM. 최종 debug APK SHA256 `ac7590cf9b55f28ddddb06fbed4b23bf723ca13e56447c7d8441ea5b2cc87d89`. 실제 기기/현장 검증은 수행하지 않았다.

## 구현

사용자 요청대로 겹친 시설은 대표 아이콘 하나+총개수(+2/+3)로 표시한다. 묶음을 누르면 종류/이름 목록, 항목을 누르면 기존 상세. 단일 시설은 바로 상세다. 대표는 ID 순 첫 시설의 실제 좌표이며 좌표/자료/점수/DB/Room을 변경하지 않는다. 지도/목록100m 주변 및 보유 기록 수 정책은 유지한다. polygon은 기존 영역 렌더링을 유지한다.

양 지도에서 실제 화면 좌표로 단일28×28dp/묶음48×36dp 배지의 사각 영역 겹침을 검사한다. 숫자 배지가 커져 이웃과 재충돌하면 다시 병합하며 모든 표시 배지가 분리될 때까지 반복한다. 대표 아이콘의 종류와 무관하게 목록에는 묶인 모든 종류를 포함한다. 숫자는 다른 추가 시설 수가 아니라 묶음 전체 시설 기록 수다.

Native는 설치 tmap-sdk-3.7.aar 공개 getMapX/YForPoint(latitude,longitude)와 zoom/pan/rotation listener를 javap로 확인했다. [공식 SDK 안내](https://tmapapi.tmapmobility.com/main_stg.html)에서도 vector 좌표 API를 교차 확인했다(이전 raster API는 인자 순서가 다름). 카메라/크기/경로/필터 변경 시120ms 후 다시 묶고 기존 FacilityOverlayQueue의 diff/8개씩 frame 삽입·취소를 유지한다. synthetic overlay는 화면 전용이며 원본 PilotData에 저장하지 않는다. 실제로 화면에 남은 묶음과 새 대상을 구분해 비동기 제거 중 클릭 정보를 유지한다.

Local은 동일 알고리즘과 숫자 bitmap을 사용한다. 시설 목록 identity/fit/zoom/화면 크기별 계산을 캐시하며 pan은 그리기/터치 좌표에만 더한다. 시설 목록 콜백은 MainActivity에서 공통 처리한다. native priority1.5/local route 이후 draw로 숫자를 경로선 위에 표시하고 출발·도착/현재 위치는 그보다 위에 둔다.

## 결과

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| 전체 Android 단위/lint/debug APK | 36개 실패0/오류0, BUILD SUCCESSFUL29s, lint 오류0/경고41 | [빌드](build-result.json) |
| 새 순수 회귀5개 | 최초 미구현 참조 실패 후 통과. 혼합 종류/구성원 보존·배지 확대 재충돌·확대/필터/입력순서·density/경계/polygon/빈 목록·동일 overlay의 최신 상세 갱신 포함 | [로그](../../../log/log-2026-11-07-facility-clusters.md) |
| Native +3 목록→상세 | 표시 수3과 목록3행 일치, 항목 상세 열기 통과 | [목록](../android-2026-11-07_201437_353951/clusters-tmap-list.png), [상세](../android-2026-11-07_201437_353951/clusters-tmap-detail.png) |
| Local +5 목록→상세 | 표시 수5와 목록5행 일치, 항목 상세 열기 통과 | [목록](../android-2026-11-07_201437_353951/clusters-local-list.png), [상세](../android-2026-11-07_201437_353951/clusters-local-detail.png) |
| 필터 | CCTV off 보유 기록1111 / on1381 복구, 묶음 재계산 | [필터 캡처](../android-2026-11-07_201437_353951/clusters-local-without-cctv.png), [결과](../android-2026-11-07_201437_353951/cluster-result.json) |
| Native 확대 | SDK double tap 후 지도 확대/묶음 재분리, +2 터치 목록2행 일치 | [확대 캡처](../android-2026-11-07_201437_353951/clusters-tmap-zoomed.png), [결과](../android-2026-11-07_201437_353951/cluster-result.json) |
| 독립 코드 검토 | 동일 membership의 오래된 상세 유지 문제 지적을 보완, 재검토 중요 지적 없음. priority/그리기 순서 확인 | [로그](../../../log/log-2026-11-07-facility-clusters.md) |

[Native 전체화면](../android-2026-11-07_201437_353951/clusters-tmap.png)과 [Local 전체화면](../android-2026-11-07_201437_353951/clusters-local.png), 두 목록을 직접 열어 겹친 시설 감소·읽을 수 있는 +숫자·혼합 종류 목록을 확인했다. 최종 설치/빌드/보관 APK 해시는 일치한다. 필터를 원복하고 native 전체화면 확대 상태로 남겼다.

## 중간 기록과 미검증

[첫 표시 캡처](../android-2026-11-07_201152_044636/cluster-result.json)는 경로선이 숫자를 가려 시설 priority와 local 그리기 순서를 보완하기 전 APK다. 독립 검토에서 synthetic overlay가 같아도 비대표 시설의 이름/상세가 바뀔 수 있음을 확인해, SDK 재삽입과 별개로 기존 묶음의 최신 구성원 정보를 갱신했다. 새 helper 미구현 참조 실패 후36개 통과했다. 과거 캡처/실패/검증을 성공으로 덮어쓰지 않았다.

실기기 GPS/OEM·다른 OS/3종 화면 크기 전체 회귀·서버 검색/Room 전체8개·DB 복원/재가져오기·대량 시설 성능·native 회전과 local 실제 두 손가락 확대 동작·현장 도로 정합성/전체 인수는 이번에 재검증하지 않았다. 확대/밀도에 따른 묶음 분리는 순수 단위에서 확인했고 native 확대는 실제 SDK 화면으로 확인했다. 출발·도착 핀은 별도 시설이 아니므로 묶지 않으며 시설 배지를 가릴 수 있다. 같은 좌표의 시설은 확대해도 묶음에 남고 목록으로 확인한다. 이전 전체 검증은 [당시 APK](../route-display-2026-11-07/verification.md) 근거다.

[최종 APK](../../delivery/2026-11-07-facility-clusters/README.md), [실기기 절차](../../DEVICE-TEST.md), [계획](../../docs/superpowers/plans/2026-11-07-facility-clusters.md).

확대 후 [+2 목록](../android-2026-11-07_201437_353951/clusters-tmap-zoomed-plus2-list.png)도 정확히2개 행으로 확인했다.

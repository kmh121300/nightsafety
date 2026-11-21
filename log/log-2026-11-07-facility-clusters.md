# 겹친 시설 마커 묶음

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

사용자가 대표 마커+총개수(+2/+3)와 터치 목록/시설 상세를 요청했다. TMAP/로컬 모두 화면 투영을 기준으로 묶는다. [계획](../source/docs/superpowers/plans/2026-11-07-facility-clusters.md). 점수/자료/DB/Room·100m 표시 범위를 유지하고 영역 polygon은 기존 렌더링을 유지한다. 순수 묶음 회귀4개를 먼저 추가했다. 구현/검증 진행 중.

## 구현과 검증

처음4개 테스트는 clusterFacilities 미구현 참조로 실패한 뒤 구현 후35개 전체 단위가 통과했다. 화면 배지28×28/48×36dp 겹침을 반복 병합하고 ID 순 실제 시설을 대표로 보존한다. polygon/원본 자료·점수는 변경하지 않는다. TMAP은 SDK 실제 화면 좌표/zoom/pan/rotation callback+120ms 지연, 기존 overlay diff/8개 frame 배치·revision 취소를 재사용한다. Local은 fit/zoom/시설/화면 크기 캐시와 pan offset을 사용한다. 공통 숫자 bitmap을 종류/개수별 재사용하고 MainActivity 목록/상세 콜백을 공유한다.

독립 검토가 동일 구성원 ID/대표 정보라도 비대표 시설 title/detail이 달라지면 synthetic overlay가 같아 과거 shownGroups가 남는 문제를 지적했다. surviving shown group 메타데이터를 SDK 삽입과 별개로 최신 desired group으로 바꾸는 helper를 추가했다. 제거 중인 그룹은 실제 SDK 제거 시점까지 유지한다. 5번째 회귀는 helper 미구현 참조 실패 후 통과했고 재검토 중요 지적 없음. 첫 실제 캡처에서 경로선이 숫자를 가려 native priority1.5/local route 뒤·endpoint 앞 그리기로 보완했다. 검토자는 최종 순서도 확인했다.

최종2026-11-07 20:14~20:18 KST API35 Android15 Pixel_3a emulator-5556/host GPU/기존 임시 read-only VM. 전체36개 단위 실패0/오류0, 빌드29s 성공, lint 오류0/경고41. 최종 APK에서 Native +3 목록3행/Local +5 목록5행과 각각 항목 상세를 확인했다. CCTV off1111/on1381 복구 및 두 지도 캡처·목록을 직접 열어 확인했다. SDK double-tap 확대 후 묶음 재분리도 캡처 확인했다. 필터 원복/native 전체화면으로 복귀했고 이후 확대 상태로 남겼다. [최종 검증/캡처/해시](../source/verification/facility-clusters-2026-11-07/verification.md), [APK](../source/delivery/2026-11-07-facility-clusters/README.md).

과거 APK/중간 캡처는 보존했다. 서버/DB 재가져오기/Room 전체 흐름·다른 화면 크기·실기기/GPS/현장·대량 데이터 성능·native회전/local 실제 pinch는 재검증하지 않았다. 순수 zoom/밀도/필터 재계산은 단위로 확인했다. 같은 좌표의 시설은 확대해도 묶음이고 endpoint 핀과는 묶지 않는다. 구현/지정 검증과 사용자 최종 UI/전체 인수는 구분한다.

확대 후 +2를 직접 눌러 목록2행 일치도 PASS. 최종 변경 문서 날짜/내부 링크(기존 발표 문서2개 누락 제외)·APK 빌드/설치/보관/manifest/checksum/UI 결과 해시 일치 확인. 문서/설치 복사본만 정리해 불필요한 재빌드/DB 검사는 반복하지 않았다.

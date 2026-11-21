# 경로 표시 가독성 개선 검증

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

대상 APK SHA256 `05fb61fac4d40eeb0a6bc25f20a88cb2a558dc8af994b7896a08b892cb35549f`. API35 Android15 Pixel_3a emulator-5556, Intel Arc host GPU, 기존 별도 read-only 시험 VM. 실제 기기는 사용하지 않았다. 검증일2026-11-07, UI8 완료00:57 KST, 화면3프로필01:04~01:07 KST, 로컬 캡처01:08 KST.

## 구현 범위

선택 경로를 파란 선/흰 casing으로 강조하고 후보는 옅은 회색으로 표시한다. 기존 구간 등급과 취약 선을 안쪽에 유지한다. 출발/도착 핀은 요청 좌표를 나타내며 미완결 구간에 가상 연결선을 만들지 않는다. 0거리에는 출발·도착 핀 하나, 경로 없음에는 핀 없음. 원본 geometry/점수/서버/DB/Room은 변경하지 않았다.

시설은 선택 경로100m 주변만 지도와 목록에 표시한다. 보유 필터 기록 수와 표시 수를 구분한다. 기본 자료는1381개 중49개 표시이며 고유 시설 수/공식 지표 수와 다른 개념이다. 근접 계산은 파일럿 범위의 평면 근사로 표시에만 사용하고 경로/종류별 캐시와 기존 overlay diff/배치를 유지한다.

Native SDK는 낮은 priority가 위에 오도록 핀1/취약2/등급3/파랑4/흰 casing5/후보9를 사용한다. 현재 위치는0. [공식 SDK 문서](https://tmapapi.tmapmobility.com/androidVSM/docs/androidDoc.html)와 설치 AAR의 공개 API를 확인했다. fitBounds+Insets로 선택 경로/요청 핀을 카드·시트 여백에 맞춘다. 새 위치에 초점을 맞춘 뒤에는 다음 경로 선택/검색 전까지 유지한다. 아주 짧은 화면은 전체 지도 여백으로 fallback하므로 전체화면에서 양 끝을 확인한다. 로컬 미리보기는 기존 고정 파일럿 투영이다.

## 검사 결과

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| Android 단위/lint/debug APK | 단위31 실패0/오류0, 빌드 성공8s, lint 오류0/경고39 | [빌드](build-result.json) |
| 새 geometry/캐시/endpoint 회귀 | 4개 먼저 미구현 참조 실패 후 통과. 중간 선분/100m 경계/polygon/캐시 변경/원본 보존/미완결 요청점/0거리/빈 경로 포함 | [로그](../../../log/log-2026-11-07-route-display.md) |
| 도구 회귀 | 14개 통과, 펼친 시트에 가린 입력 처리 회귀 포함 | [로그](../../../log/log-2026-11-07-route-display.md) |
| 실제 로컬 서버 연동 UI | 8개 통과: 검색·완결 anchor·공식 점수·취약 상세/토글·필터·Room 재시작/오프라인/수정/재조회/삭제 | [00:57 결과](../android-2026-11-07_005224_417355/integration-ui.md) |
| small720×1280/density360 | 버튼/요약/시트/전체화면·뒤로 통과 | [결과](../android-2026-11-07_010450_398535/map-sheet-result.json) |
| standard1080×2220/density440 | 동일 회귀 통과 | [결과](../android-2026-11-07_010532_516753/map-sheet-result.json) |
| pane1200×1920/density320 | 좌우 고정 패널·전체화면/뒤로 통과 | [결과](../android-2026-11-07_010615_272513/map-sheet-result.json) |
| 독립 코드 검토 | 필터/캐시/endpoint 제거/overlay queue/viewport/location focus 중요 회귀 지적 없음 | [로그](../../../log/log-2026-11-07-route-display.md) |

세 화면 검사는 모두 동일 최종 APK 해시이며 cleanup_errors0, 원래 크기/밀도로 복원했다. [일반 지도](../android-2026-11-07_010532_516753/standard-collapsed.png), [TMAP 전체화면](../android-2026-11-07_010532_516753/standard-fullscreen.png), [로컬 전체화면](../android-2026-11-07_010800_845550/route-local-fullscreen.png)을 직접 열어 파란/흰 선·끝점 핀·회색 후보·시설 감소를 확인했다. 서버 UI의 integration-weak-tmap.png는 펼친 결과 패널 캡처라 지도 취약선 외관의 독립 시각 검증 근거로 삼지 않는다. 토글/상세 동작은 UI8 검사 근거다.

## 중간 실패 보존과 한계

[초기 캡처](../android-2026-11-07_003310_118784/route-display-preview.json)는 핀 위 선 겹침/도착 핀 카드 가림이 있어 priority·별도 casing·fitBounds를 보완한 전 APK다. [첫 실행 실패](../android-2026-11-07_004444_667287/failure.md)는 cold start에서 제어 패널을 너무 일찍 조회했고, [두 번째 실패](../android-2026-11-07_004628_741368/failure.md)는 펼친 시트 뒤 입력을 눌렀다. 도구에 앱 준비 대기/겹침 시 시트 접기를 반영하고 같은 최종 APK로 UI8 통과했다. 실패는 덮어쓰지 않았다.

이번은 표시 개선과 지정 회귀 검증이다. 실제 도로와 경로 정합성/현장 보행·실기기 GPS/OEM·다른 OS/일반 창 크기/프로세스 복원·과거 API36.1 소실 원인·전체38개 명세/운영 인수는 미완료다. DB 전체 복원/재가져오기·성능 검사는 반복하지 않았다. 사용자의 최종 UI 판단은 별도다.

[최종 설치 묶음](../../delivery/2026-11-07-route-display/README.md), [실기기 절차](../../DEVICE-TEST.md), [구현 로그](../../../log/log-2026-11-07-route-display.md).

# 최신 고정 글꼴 APK의 0거리 UI 회귀 확인

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 최종 확인 시각: 21:12 KST · 시간 기준: Asia/Seoul

## 대상과 환경

- Windows, Pixel_3a/API35/SwiftShader/read-only 임시 에뮬레이터5556. 기존 `%TEMP%\safenight-mvp-20261104` 데이터를 사용했고 기본 AVD를 초기화하지 않았다.
- APK SHA256 `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9`. 설치 파일의 sha256sum도 일치했다. 새 Kotlin/서버/DB 변경이나 APK 빌드는 하지 않았다.
- 127.0.0.1:8765 서버는 DB startup_snapshot configured/verified true, bundle `local-mvp-3types-v1`로 준비됐다. adb reverse tcp:8765 연결을 확인했다.

## 실행과 결과

`python -X utf8 tools/zero_route_smoke.py --serial emulator-5556` 종료 코드0. 기존 도구를 강화해 정상 경로 검색의 전체/평균/취약 숫자 점수를 먼저 확인한 뒤 같은 보행 anchor를 양쪽에 선택했다.

- 정상 경로 세 점수가 숫자0~100 범위인 단계 통과.
- 같은 대학 옆문 anchor를 출발·도착으로 선택 후0m/약0.0분 표시 통과.
- 동일 보행 지점/이동 없는 경로/시설지표 미산출 안내 통과.
- 기존 세 숫자 점수가 모두 `—`로 초기화되는 것 통과.
- 캡처에서 이전 경로선이 사라지고 시설 마커만 남은 것을 직접 확인했다. 단순히 API 성공을 앱 성공으로 대신하지 않았다.

[UI 실제 값](zero-route-result.json), [0거리·세 점수 함께 캡처](integration-zero-route-metrics.png), [이동 없는 경로 안내와 지도](integration-zero-route.png).

별도로 [DB snapshot 기반 API 검사](../zero-route-api-2026-11-05/verification.md)도 후보1개/already_at_destination/0m/0초/세 지표null/geometry·구간·간선 없음으로 통과했다.

## 중간 실패와 한계

설치 완료 전 패키지 조회·실행 실패, [API36.1 시스템 창 오분류](../zero-route-2026-11-05-startup/failure.md), [같은 환경의 앱 화면 소실](../zero-route-2026-11-05-input/failure.md), [API35 Pixel Launcher 창](../zero-route-2026-11-05-api35-startup/failure.md)은 보존한다. API36.1 입력 단계에서 앱 PID가 사라진 정확한 원인은 미확정이며 이 API35 성공으로 해소됐다고 주장하지 않는다.

Process system 문구를 외부 시스템 창으로 인식하고 Wait를 우선하는 helper 회귀를 수정했다. 우리 앱 ANR은 계속 실패시키는 검사도 포함해 도구9개 통과. 이 작업에서 일반 창 크기/프로세스 복원·최신 Room 전체 흐름·실기기/GPS·사용자 최종 UI·명세 전체 인수를 검사하지 않았다.

최종 서버 health ready·DB snapshot verified true·ADB device/reverse를 재확인했다. 사용자 요청의 다음 검사를 이어갈 수 있도록 서버와 이번5556 에뮬레이터는 연결된 상태로 유지한다. [작업 로그](../../../log/log-2026-11-05-zero-route.md), [로드맵](../../../ROADMAP.md).

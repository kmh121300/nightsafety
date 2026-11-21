# 보안등 파일럿 연결 검증

작성일: 2026-11-03 · 최종 수정일: 2026-11-03 · 시간 기준: Asia/Seoul

후속 결과: **2026-11-03 15:31 KST DB 재활성화 후 보안등 실제 import·DB 복원/API 대조 통과.** 아래 연결 실패와 당시 미완료 범위는 최초 검사 기록이다. 새 결과는 [DB 반영 재검증](../database-security-lights-2026-11-03.md)에 별도로 남긴다.

## 변경 범위

원본 CP949 CSV를 검사해 파일럿용 [별도 GeoJSON](../../app/src/main/assets/pilot-security-lights.geojson)을 생성했다. 기존 CCTV/비상벨/OSM 산출물은 보존했다. 전체9,265행 중 파일럿870행(고유 좌표533개)을 표시하며, 좌표 비정상/누락53행·파일럿 밖8,342행의 CSV 레코드 번호는 [감사 JSON](audit-7c441fea2d6e.json)에 남긴다. 같은 좌표의 행은 보존하고 공유 개수를 기록한다. ID는 원본 해시 앞12자리+CSV 레코드 번호로 snapshot 내 고유하며 행 순서 변경은 새 snapshot이다.

서버 시설 API와 일반 DB import/hydrate 경로에 `security_lamp`를 연결했고, Android에서는 `lamp` 마커·필터·상세로 표시한다. 스마트가로등과 다른 유형이다. 원본 속성·출처 URL·기준일2026-02-24를 보존한다. 점수 대상 grid와 CCTV/비상벨 공통 점수 기준에는 넣지 않는다. 공식 점수와 현재 안전/균형 추천은 null, 스마트가로등은 unavailable을 유지한다. 앱 시설 표시는 기존과 같이 고정 번들 asset 기반이며 새 viewport 동기화 구현을 뜻하지 않는다.

## 2026-11-03 검사 결과

환경: Windows, 프로젝트 `.venv` Python3.10.11, JDK21, Gradle9.7.1, Android SDK36. Git 커밋 식별자는 미기록(현재 폴더는 Git 저장소 아님).

| 검사 | 실행 / 결과 |
| --- | --- |
| 변환기 | `python -X utf8 -m unittest discover -s tools -p test_security_lights.py -v`: 기능 모듈 미존재로 실패 후 구현, 2개 통과. 같은 이름/좌표 보존·ID 분리·결측/NaN/Infinity/범위 밖 격리·날짜/열 검증·재현성 확인 |
| 서버 | `python -X utf8 -m unittest discover -s server -v`: 보안등0건으로 신규 검사 실패 후 연결, 최종 전체18개 통과. HTTP 시설1,378건/보안등870건, 점수 제외·source state·기존 경로/API 회귀 포함. 보안등 없는 baseline과 모든 간선의 비용·점수 표본·구간·토폴로지 동일 대조 통과 |
| 도구 | `python -X utf8 -m unittest discover -s tools -p "test*.py" -v`: 전체5개 통과. 증거 보존 테스트의 의도된 `FAIL: fixed UI failure` 출력은 실제 suite 실패가 아님 |
| Android | `gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug --offline`: 빌드 성공, 단위14개 실패0, lint 오류0/경고44. 기존 inset deprecated 컴파일 경고 있음 |
| APK | SHA256 `57d3fc82978f492e38de66a8938e469a68d81ef4b630f2a5e7ea3f9f7ffedb17`. APK 안 보안등 asset과 작업 폴더 asset 바이트 일치 |
| 감사 합계 | 870+53+8,342=9,265, 원본 SHA256 `7c441fea2d6e651320aca98c178127e1078c8cd5d0b384797f2631a2273941ed` |
| 별도 코드 검토 | 읽기 전용 검토에서 Critical/Important 지적 없음. 변환기2개 독립 실행 통과. 실제 DB/화면 검증을 대신하지 않음 |
| 실제 DB | `server/postgis.py` 읽기 조회가 제한 환경과 권한 확장 환경 모두 실패. 비밀정보를 제거한 서버 사유는 `ENOTFOUND tenant/user not found`. 신규 import는 실행하지 않음. 이전2026-10-26 DB 성공 기록을 현재 성공으로 재사용하지 않음 |

## 출처와 미검증 범위

사용자가2026-11-03 제공한 다운로드 출처: 경기데이터드림 [보안등정보현황(제공표준)](https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId=VEY71398U2941WM4E7PV21507518&infSeq=1). 웹 조회는 timeout/cache miss로 상세 확인 실패. 이용허락범위는 미확인으로 유지한다. 실제 다운로드 시각은 미기록이다.

기준일로부터252일 경과했고 기존180일 정책을 바꾸지 않았다. 위치 정확도·중복 원인·시흥 전수성·스마트 기능·실제 점등/접근성·공식 점수 활성화·물리 기기 GPS는 미검증이다. DB 프로젝트 상태/로컬 연결 정보가 복구된 후 신규 bundle import와 전체 DB/API 동등성 검사가 필요하다. 비밀번호/연결 문자열은 기록하지 않았다.

관련: [계획](../../docs/superpowers/plans/2026-11-03-security-lights.md), [개발 로그](../../../log/log-2026-11-03-security-lights.md), [로드맵](../../../ROADMAP.md).

## 2026-11-03 화면 검사 진행 기록

Pixel_3a API35를 read-only/no-snapshot/headless/SwiftShader/3072MB로 실행해 기존 AVD 자료를 보존했다. emulator-5554에 새 APK 설치 성공. 명시적으로 `Engine()` 로컬 파일 서버를 사용했다. 제품의 configured DB 실패 시 fallback 금지 동작은 변경하지 않았다.

- [최신 전체 UI 검사](../android-2026-11-03_144825_157655/failure.md)는 최초 지도 상태 문구 대기에서 실패했다. 마지막 상태는 'TMAP 인증 성공 · 지도 준비 중'이었다. 캡처에는 실제 배경지도·보안등/기존 시설 마커와1,381개 표시가 보였으며 시각 확인했다. 앱 실행 전후 외부 System UI ANR 창3회 닫기가 기록됐다. 특정 SDK/드라이버 원인은 확정하지 않는다.
- 별도 보안등 범위 검사 첫 실행에서 ON/OFF1,381→511→1,381은 통과했고 [ON/OFF 캡처](../android-2026-11-03_145238_529297/security-lights-on.png)를 남겼다. 이어 보안등만870개를 기대한 단계는 실패했다. 후속 관찰에서 CCTV/경찰은 OFF, 비상벨은 ON인1,108개 상태였다. 각 갱신을 기다리도록 검사 조작을 보완했다. 이 실패를 전체 UI 통과로 바꾸지 않는다.

### 2026-11-03 15:11 KST 보안등 범위 검사 통과

[완료 보고서](../android-2026-11-03_150042_324475/security-lights-ui.md): 보안등 ON/OFF1,381→511→1,381, 보안등만870개 목록, 상세 기준일/점수 제외/공유좌표 안내, 로컬 서버 검색과 과거 CCTV/비상벨 지표·공식 점수 미산출 안내가 모두 통과했다. 검사 종료코드0. [마커 ON](../android-2026-11-03_150042_324475/security-lights-on.png), [마커 OFF](../android-2026-11-03_150042_324475/security-lights-off.png), [상세](../android-2026-11-03_150042_324475/security-light-detail.png)를 시각 검토했다. 이 결과는 실제 DB 기반 전체 UI/Room/실기기 인수를 뜻하지 않는다. 이전 실패 기록은 보존한다.


# API36.1 입력 안정성·필수 명세 대조 검증

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 검증일: 2026-11-05 · 시간 기준: Asia/Seoul

## 결론과 제한

사전 검사3번의 API36.1 재현 조사·핵심38개 기능 대조와 경로 비교 수치 누락 보완을 수행했다. 새 APK에서 입력/시설 수/원천 누락·복구/0거리 흐름5개를2+3회로 검증했다. **과거 API36.1 앱 소실의 정확한 원인은 여전히 미확정이며, 명세 전체38개 인수 완료가 아니다.**

[38개 기능 대조표](functional-matrix.md)에 구현·부분 검증·명세와 차이·미구현을 구분했다. 지도 pin/viewport별 시설 갱신/구간별 이유·시설 연결/같은 선 재평가/429 정책 등은 남아 있다. 현재 제한된 파일럿 기본 통합 범위와 명세 전체 인수 범위를 혼동하지 않는다.

## APK와 빌드

최종 APK SHA256 `b50ae48ddaaa76ea933ad9f86821963f2f3d0aa3e9132f11b994012f2886084d`. Windows/JDK21/Gradle9.7.1/AGP9.4.0. [빌드 기록](build-result.json): Android27개 실패0/오류0, lint 오류0/경고31, APK 빌드 성공. 도구12개 통과. 최신 APK는 API35/5556·API36.1/5558에 모두 설치 후 해시를 대조했다.

경로 시설 개수의 [수정 전 회귀 실패](counts-red.json)를 보존했다. 서버 facility_counts를 모델/파서/비교 패널로 전달하고 음수·분수·범위 초과·미확보 유형의 숫자를 거절한다. 정상0과 null/이전 snapshot 누락을 구분해 null은 —로 표시한다. 전체 지도 시설 수와 구분하고 필터로 바꾸지 않는다. 원천 누락 이유를 부분 지표 안내에 붙였다. 서버 계산·DB·Room schema 변경 없음.

## API36.1 조사

환경: Medium_Phone_API_36.1, API36 system image36.1, read-only/no-snapshot/swiftshader/3072MB. 기존 AVD 초기화 없음. 별도의 API35와 DB startup snapshot 서버도 유지했다.

- 과거 ebf2 APK 파일과 당시 VM의 종료 이력이 보존되어 있지 않아 동일 과거 바이너리로 재현하지 못했다. 이번 결과를 과거 원인 해결로 바꾸지 않는다.
- 현재 위치 crash 수정본 f1d1 APK 첫 시도는 uiautomator XML 부재로 중단됐다. [실패 캡처](../android-2026-11-05_230621_930178/failure.md)에 지도 준비 완료 화면과 PID5689가 존재했다. 이 실패는 앱 종료가 아니다.
- 준비 뒤 동일 f1d1의 정상→동일 anchor0거리 검사가 종료0으로 통과했다. [runtime 기록](../android-2026-11-05_230731_876077/api36-runtime.json). PID5689→5986은 검사 스크립트의 명시 force-stop에 따른 변화이고 해당 종료 사유도 FORCE STOP이었다.
- b50a APK로 업데이트 후 아래 검사를 PID7125로 수행했다. [종료 이력](../android-2026-11-05_231337_494618/exit-info-sanitized.json)에 앱 crash/ANR 종료가 없고 이전 설치/명시 강제 종료 기록만 있다. 이 한정 검사에서 재현되지 않았다는 뜻이며 장시간/실기기 안정성 보장이 아니다.

## 새 APK 실행 결과

[첫 실행](../android-2026-11-05_231337_494618/spec-ui-result.json)은 아래2개 통과 뒤 자동 스크롤 실패로 FAIL 그대로 보존했다. [이어 검사](../android-2026-11-05_232011_195591/spec-continuation-result.json)에서 같은 PID/동일 APK의 남은3개를 통과했다. 단일 실행 전체 성공으로 합쳐 쓰지 않는다.

- PASS: Three route counts match live API and remain unchanged by map filtering
- PASS: Repeated endpoint input dialogs open without app disappearance
- PASS: missing lighting
- PASS: live recovery
- PASS: zero route same PID

부분 자료 UI는 실제 DB를 바꾼 것이 아니라 선택한 에뮬레이터의 adb reverse만 임시 로컬 fixture 서버로 연결해 검사했다. 실제 보안등 자료를 미확보로 바꾸거나 계산된 부분 점수의 실데이터 정확도를 검증한 것이 아니다. finally에서 원래 서버 reverse를 복원했고 fixture 서버를 종료했다.

[부분 자료 캡처](../android-2026-11-05_232011_195591/missing-lighting.png)에서 보안등 —·평균/취약 —·자료 미확보 안내를, [복구 캡처](../android-2026-11-05_232011_195591/restored-counts.png)에서16/16/12와9.1/13.0/0.0을 직접 확인했다. [0거리 캡처](../android-2026-11-05_232011_195591/api36-zero-route.png)에서0m/0분·세 점수 —·이전 경로선 제거를 확인했다.

중간 실패는 Smoke.visible의 긴 스와이프가 새 짧은 수치 행을 건너뛴 문제다. 당시 화면/PID는 정상 앱이었고,760px 이동>400px 허용 assert 실패 후 반 화면씩 겹치는 느린 스크롤로 수정했다. 도구12개와 실제 수치 행 재발견을 확인했으며 이 문제 때문에 앱 기능을 다시 수정하지 않았다.

## 미검증과 다음 작업

명세 전체 교차TC·일반 창 크기/프로세스 복원·실기기 GPS/제조사·현장 보행·이용조건·운영 배포는 남아 있다. 사용자가 고른 세로 고정/글꼴1.0과 CSV 기간 상한 제거·보안등 조명 정책은 유지했다. UI8개·오류/권한8개는 각각 당시 APK의 근거로 보존하며 이번 APK에 새로 전부 실행했다고 주장하지 않는다. 다음은4번 작은 화면/설치 준비·실기기 검사표다.

[로그](../../../log/log-2026-11-05-api36-spec-audit.md), [로드맵](../../../ROADMAP.md).

API35 추가 영향 검사: [단일 정상 검색·개수 표시](../android-2026-11-05_232945_178999/api35-counts-result.json) 종료0·16/16/12 표시 통과. 전체 UI8개 재실행과 구분한다.

마감 연결 근거: [최종 상태](final-state.json). 서버/두 에뮬레이터를 유지했고 임시 fixture 연결은 복원했다. 변경 문서 날짜·신규 링크·38개 대조표 확인 완료. 기존 발표 자료 링크2개 누락은 별도 미해결이다.

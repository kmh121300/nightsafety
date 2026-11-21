# API36.1 앱 소실 분리 및 필수 명세 대조

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자 승인으로 사전 검사3번 착수. 기존 Ponytail·systematic debugging·TDD 지침 적용. 기존 graphify 산출물은 없고 이번 작업은 지정 명세·호출부 대조이므로 새 대규모 그래프/의존성을 만들지 않고 직접 근거를 연결한다.

## 범위와 실행 방침

- API36.1 Medium_Phone AVD를 read-only/no-snapshot/swiftshader/3072MB로 재사용한다. 기존 API35와 서버는 보존한다. 당시 APK ebf2...는 파일로 남지 않았고 API36.1 base에도 설치되어 있지 않았다. 현재 f1d1...를 설치해 재현하되 과거 동일 바이너리 재현 또는 원인 해결로 주장하지 않는다.
- API35에서 수정된 위치 SDK crash와 API36.1 과거 입력창 소실의 원인이 같다고 추측하지 않는다. 새 실행은 PID·단계·앱 종료 이력/실패 캡처로 분리한다.
- 기능 명세의 핵심38개를 우선순위·구현·실행 근거·미충족 TC로 대조한다. 기존 승인된 세로/글꼴 고정·공공 CSV 정책·파일럿 범위를 유지한다. P2/시흥 전체/운영 호스팅을 자동 추가하지 않는다.

## 필수 보완 설계

F-05-02의9개 비교 지표 중 경로 주변 유형별 고유 시설3개가 서버 facility_counts에는 있으나 앱 파서/모델/UI에서 누락됐다. 서버 값을 그대로 모델에 전달하고 기존 비교 패널에 세 숫자를 표시한다. 필터로 바뀌는 지도 시설 수와 구분한다. null/이전 snapshot의 누락 필드는0으로 바꾸지 않고 —로 표시하며 원천 미확보 이유를 안내한다. 변경 범위: PilotRoute/PilotData, ServerBundleParser, MainActivity, 공통 result XML, 파서 회귀·영향 UI 검사. DB/서버 계산·Room schema·외부 의존성 변경 없음. 구현 전 null/0/잘못된 개수의 실패 검사를 추가한다.

지도 pin·viewport bbox·API 세부 계약 등 현재 MVP 대체/미구현 범위는 대조표에 그대로 남기며 전체 명세 인수 완료로 바꾸지 않는다. 결과·검증 단계는 아래 후속 기록으로 갱신한다. [로드맵](../ROADMAP.md), [명세](../md/night-safety-functional-specification-ko.md).

## 중간 실행과 보완 (2026-11-05)

- API36.1 f1d1 APK 최초 자동 검사는 UI dump 파일이 없어 시작 단계 실패. [캡처/실패](../source/verification/android-2026-11-05_230621_930178/failure.md)에는 지도 준비 완료 화면과 PID5689가 있어 앱 종료로 분류하지 않는다.
- 준비 뒤 동일 f1d1 APK의 정상→동일 anchor0거리 검사 종료0. [runtime 기록](../source/verification/android-2026-11-05_230731_876077/api36-runtime.json). PID5689→5986은 스크립트의 명시 force-stop/restart에 따른 변화이며 종료 이력도 FORCE STOP이다. 과거 ebf2 APK 소실 원인은 여전히 미확정이다.
- 경로 시설 개수 회귀2개는 초기 미정의 필드 compile 실패 후 모델 필드 추가 상태에서9개 중2개 assert 실패를 확인했다. [실패 근거](../source/verification/spec-audit-2026-11-05/counts-red.json). 파서/모델/UI·미확보 안내 보완 후 Android27개 실패0/오류0·빌드 성공, lint 오류0/경고31. [빌드 기록](../source/verification/spec-audit-2026-11-05/build-result.json). APK b50ae48ddaaa76ea933ad9f86821963f2f3d0aa3e9132f11b994012f2886084d.
- 새 APK API36.1 [UI 시도](../source/verification/android-2026-11-05_231337_494618/spec-ui-result.json)는 경로 수16/16/12와 필터 불변·반복 입력창2회를 PID7125로 통과한 뒤 partial 응답의 수치 행을 자동 스크롤이 건너뛰어 중단했다. [종료 이력](../source/verification/android-2026-11-05_231337_494618/exit-info-sanitized.json)에도 crash/ANR 없이 설치/강제 종료만 있다. 실패 화면은 정상 앱 하단 필터 패널이다.
- Smoke.visible의 화면 대부분을 한 번에 스와이프하는 방식이 짧은 행을 건너뛰는 문제를760px 이동>허용400px assert로 재현했다. 겹치는 반 화면씩 느리게 이동하도록 최소 수정, 도구12개 통과. 실제 같은 화면에서 'CCTV16/비상벨16/보안등—' 행을 다시 찾았다. 앱 코드는 이 실패 때문에 수정하지 않았다. 완료한 앞2개는 보존하고 남은 부분/복구/0거리만 같은 PID로 이어서 확인한다.

[38개 기능 대조표](../source/verification/spec-audit-2026-11-05/functional-matrix.md)는 명세의 P0/P1 누락·미검증을 그대로 구분했다. 지도 pin·viewport 시설 재조회·유형 기여/이유 상세·같은 선 재평가·429 정책 등은 남아 있으며 이번 지정 검사 완료를 전체 명세 인수 완료와 혼동하지 않는다.

## 2026-11-05 결과 정리

같은 PID7125·새 APK b50a에서 앞2개+후속3개를 확인해 지정 API36.1 입력/수치/부분 자료/복구/0거리 흐름5개 완료. [후속 실행](../source/verification/android-2026-11-05_232011_195591/spec-continuation-result.json), [종합 검증](../source/verification/spec-audit-2026-11-05/verification.md). 부분/복구/0거리 캡처를 직접 확인했다. fixture 서버 종료·adb reverse 복원. 최신 APK를 API35에도 설치해 양쪽 해시 일치를 확인했다. 도구12개 재실행 통과. 과거 API36.1 원인은 미확정 유지, 명세 전체38개/현장/실기기 인수와 구분한다. 다음은4번 화면/설치 준비다.

마감 확인: API35 최신 APK 정상 검색·16/16/12 표시도 통과(전체 UI8개 아님). 변경6개 문서 날짜/UTF-8·신규 내부 링크·대조표38개 고유 행과 실제 빌드/분리 실행 결과 일치 확인. 기존 발표 문서 링크2개 누락은 보존했다. 서버 ready/DB verified, 두 에뮬레이터 최신 설치 해시/PID/reverse는 source/verification/spec-audit-2026-11-05/final-state.json에 기록했다. 서버/5556/5558은 유지한다.

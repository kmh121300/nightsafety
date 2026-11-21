# 오류·복구 및 위치 권한 모의 검사

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

사용자 지시로 실기기 연결 전2번 검사에 착수했다. 기존 API35 Pixel_3a 임시 read-only 에뮬레이터5556과 DB snapshot 서버 재사용. 시작 health ready/DB verified, 로컬·설치 APK SHA256 `ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9` 일치.

기존 Smoke 도구를 재사용하는 `source/tools/error_recovery_smoke.py`를 추가했다. 빈/무결과 검색·범위 밖 좌표·교환·이전 결과 저장 차단·연결 실패/복구·강제 종료 후 미저장 입력·OS 권한 거부·대략 위치 권한의 무수신 시간 초과·모의 위치·위치 OFF를 assert로 확인한다. 설정 원복은 finally에서 처리하고 결과 JSON에 완료 단계·실패·복원 오류를 남긴다. 새 의존성 없음. 앱/서버/DB 변경·재빌드 없음.

검사 전 위치 권한 둘 다 denied, USER_SET. 시스템 위치 ON, shell mock operation default deny. 검사 중 진행은 완료와 구분한다. 실제 GPS/제조사·API36.1 현상/전체 명세 인수는 범위 밖이다. [로드맵](../ROADMAP.md), [검사 순서](log-2026-11-05-pre-device-checks.md).

## 중간 실패와 수정 (2026-11-05)

- 첫 시도: [실패 보고서](../source/verification/android-2026-11-05_221538_586047/failure.md). EditText 오류 popup이 XML에 없어 잘못 대기한 도구 문제와 appops 기본값 표기/빈 예외 처리 문제를 수정했다. 당시 캡처 보존. 도구11개 통과.
- 두 번째 시도: [결과 JSON](../source/verification/android-2026-11-05_222019_313588/error-recovery-result.json). 입력/교환/서버 실패·복구/재시작/권한 거부/대략 권한 시간 초과6개 통과 후 모의 위치에서 실패. 정밀 위치를 처음 수신할 때 실제 앱 crash를 확인했다. [비밀값을 제외한 stack](../source/verification/android-2026-11-05_222019_313588/location-crash-sanitized.txt): SDK TMapLocationLayer.setVisibleIcon의 null marker → TmapPilotMap.update. 알림 패널 캡처만으로 환경 문제라고 결론내리지 않았다.
- SDK AAR 바이트코드 확인: setLocationPoint는 좌표만 저장하고 setIconVisibility는 tracking marker 존재를 가정한다. 일회성 수신에 지속 추적을 켜는 대신 기존 TMapMarkerItem 방식으로 현재 위치 점을 추가·갱신하고 위치 변경 시 재중심하도록 수정했다. 일반 시설 필터와 ID가 충돌하지 않는다. 위치 이력 영구 저장 없음.
- 검색0건의 상단 상태가 무한 '찾는 중'으로 남는 문제는 [수정 전 assert 실패](../source/verification/android-2026-11-05_223025_607460/no-results-status-red.json) 확인 후 완료 상태 문구를 추가했다.
- 두 번째 도구의 복원 검사는 appops의 `default; time=...` 표기를 인식 못해 실패했지만 별도 확인에서 두 권한 denied/USER_SET, 위치 ON, shell mock default로 실제 복원을 확인했다. 기본값 표기에 사용 시각이 추가되는 경우도 회귀 검사에 포함했다.

앱 수정은 지도 현재 위치 표시와 검색0건 상태 두 곳이다. 수정 APK의 단위/lint/빌드 및 영향 범위 재검사를 진행한다. 이전 APK의 성공6개를 새 APK 전체 통과로 바꾸지 않는다.

## 수정 APK 검증 진행 (2026-11-05)

빌드 `:app:testDebugUnitTest :app:lintDebug :app:assembleDebug` 성공. Android25개 실패0/오류0, 도구11개 통과, lint 오류0/경고27(추가1개는 기존 Bitmap 생성 방식의 UseKtx 권장). 새 APK SHA256 `f1d1a7c84d926be070ceb1b0447de95c8dfbf261d23ed1b479ed58324aa673ef`, 설치 후 해시 일치 확인. [빌드 기록](../source/verification/android-2026-11-05_223346_459677/build-result.json).

[새 APK 실행](../source/verification/android-2026-11-05_223346_459677/error-recovery-result.json)에서7개 통과: 검색0건 상태 수정·입력/교환·연결 복구·재시작·권한 거부·대략 권한 시간 초과·첫 모의 정밀 위치 수신 후 검색. [위치 캡처](../source/verification/android-2026-11-05_223346_459677/mock-location.png)에서 흰 테두리 파란 위치 점과 재중심·현재 위치 출발지를 직접 확인했다. 마지막 위치 OFF 때 Android의 No location access 안내창이 버튼을 가려 도구가 실패했다. 실제 앱 crash나 이미 통과한7개 실패로 덮지 않는다. 권한/위치/모의 위치/ADB reverse 복원 오류0. 안내창 Close를 명시 처리하고 마지막 항목만 재검사해 불필요한 전체 반복을 피한다.

1번 전체 UI8개/0거리 검사는 수정 전 APK의 근거로 보존한다. 이번 새 APK에는 위 두 곳만 수정했으며 영향 범위 오류·위치 흐름을 재검사한다. Room/점수 정책/DB 변경 없음.

## 2026-11-05 22:43 KST 완료

마지막 위치 OFF 한정 재검사 종료 코드0·1개 PASS, 기존 출발지 유지/실패 안내/수동 검색 통과. 새 APK의 앞7개와 합쳐2번 지정 항목8개 완료. [종합 검증](../source/verification/error-recovery-2026-11-05/verification.md), [최종 한정 실행](../source/verification/android-2026-11-05_224138_022854/error-recovery-result.json). 첫7개 실행의 전체 FAIL은 OS 안내창 당시 결과로 그대로 둔다. 안내창 처리 후 도구11개 재실행 통과. 위치 OFF 및 모의 위치 캡처 직접 확인. 마지막 두 실행의 설정 복원 오류0. 다음은3번 API36.1 현상 분리·필수 명세 대조다. 실기기 연결은 아직 필요 없다.

마감 확인: 변경5개 문서 날짜/UTF-8·신규 내부 링크·7+1개/실제 APK 해시 일치 확인. 기존 발표 문서 링크2개 누락은 미해결로 보존했다. 최종 앱 지도 준비·서버 ready/DB verified·권한/위치/mock 기본값/reverse 복원은 verification/error-recovery-2026-11-05/final-state.json에 기록했다.

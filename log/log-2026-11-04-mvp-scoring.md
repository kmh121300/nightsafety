# MVP 3유형 점수 실제 적용

작성일: 2026-11-04 · 최종 수정일: 2026-11-04 · 시간 기준: Asia/Seoul

사용자가 문서 정리에서 멈춘 점을 지적하고 실제 적용을 지시했다. [정책](../md/night-safety-mvp-scoring-policy-ko.md)을 서버·DB·앱·검사 도구에 직접 반영한다. 이전 정책 문서 작업/로그와 과거 검증은 당시 기록으로 보존한다.

## 구현 범위

- 서버: 필수 유형 cctv/emergency_bell/security_lamp, 보안등 eligibility, 기간 차단 제거, 구간 등급·정식 평균/취약/전체 점수, 완결 경로의 실제 safe/balanced 선택. 0거리와 미완결 연결 상태는 별도 유지.
- 원천: 형식·좌표·범위·ID 검사, 잘못된 유형/도형은 실패 처리. 정상 빈 원천과 없는 보안등 파일 구분. 사전 점수의 원천 기준이 바뀌면 rebuild 없이 사용하지 않음. 내부 operational_status/accessibility unknown 보존.
- DB: 새 scoring/routing/facility/bundle 버전, source metadata 저장·복원. 기존 bundle은 append-only 방식으로 보존. 구 계산 설정을 새 계산 설정으로 읽지 않음.
- Android: 정식 score/average/weak 검증·표시, 구 부분 snapshot 구분, 보안등 점수 제외/작동 미확인 문구 제거, 구간 등급 색·범례, 서버 최종 roles를 기준으로 제목·즐겨찾기 선호 선택.
- 도구: 변환기·생성 asset·DB/API 대조·전체 UI/0거리 검사 기대값 갱신. 원본 CSV는 수정하지 않음.

## 검증 진행 기록

- 최초 새 서버 회귀4개는 기존 코드에서 실패/오류 후 구현을 통해 통과했다. 보안등 변환기 eligibility 검사도 기존 false에서 실패한 뒤 새 정책으로 수정했다.
- 앱의 정식 점수 파싱·잘못된 계산 기준 회귀2개는 기존 코드에서 실패 후 수정했다. 첫 수정본 Android19개·단위/빌드/lint 통과. lint 오류0/경고45. 이전44개와 섞어 기록하지 않는다.
- 서버 전체23개·도구5개 통과. 추가 검토 회귀 후 최종 수는 완료 시 아래에 기록한다.
- 새 DB import 종료코드0: 시설1,378·노드27,607·간선8,208·구간22,256. `tools/db_smoke.py --verify-import` 종료코드0: 전체 노드/시설/간선/점수 표본·도형/SRID·RLS·HTTP 계약·3유형 점수와 safe 선택·재평가·0거리, 같은 import 행수 불변과 잘못된 도형 트랜잭션 rollback 통과.
- 읽기 전용 코드 검토에서 Important2건: generated_profiles 대신 서버 최종 roles 사용, 잘못된 조명 입력이 ready/0건으로 처리되는 경계 차단. 각각 앱 회귀1개와 서버 두 입력 subtest의 실패를 확인하고 수정했다. 최종 suite와 APK 재검증 진행 중.
- 첫 UI 실행은 지도/시설 준비 통과 후 위 검토 수정본으로 바꾸기 위해 중단했다. 이를 전체 UI 통과로 세지 않는다. 검토 전 APK SHA256은 `684ec5526ce85f0725f95b911bf66dcf5ebd2944047f8991c7834be2e1da43c8`이며 최종 APK와 구분한다.

환경: Windows, Python3.10.11, JDK21/Gradle9.7.1, Pixel_3a Android15 API35 임시 이미지·headless SwiftShader·3072MB/emulator-5556, 실제 PostGIS startup_snapshot. Git 커밋은 미기록(작업 폴더는 Git 저장소 아님). 키·연결 문자열·원본 SDK/logcat은 기록하지 않았다.

## 남은 확인

최종 결과: 서버24개·도구5개·Android20개, 빌드/lint 오류0·경고45 통과. 최종 설치 APK 해시 `973ebc2d10dff824cbc98bbc6cdf074d7a84d400c47b7a569ad7d1adb6d703fc` 일치. DB 기반 전체 UI8개(23:09:47 KST)·별도 보안등 상세(23:10~23:13)·0거리 화면(23:14~23:15) 모두 종료코드0. 캡처4개를 시각 검토했고 주황 ON1,969/OFF0픽셀도 대조했다. [검증 보고서](../source/verification/mvp-scoring-2026-11-04/verification.md)에 환경·버전·명령·실제 점수·캡처를 모았다.

코드 검토2건은 각각 실패 재현→수정→전체 suite 통과로 닫았다. 재검토를 별도 통과했다고 주장하지 않는다. 새 기능·추가 의존성·구조 변경을 더하지 않았다. 새 정책은 실제 서버/DB/앱에 적용됐으며 로드맵/실행 안내의 문서 단계 미적용 상태를 갱신했다. 실기기 GPS·성능·현장 보행·명세 전체 TC·운영 배포는 이 작업에서 완료로 기록하지 않는다.

최종 대조: 정책·명세·로드맵·실행 안내·계획·로그·검증9개 문서의 날짜와 내부 링크/anchor147개, 전체 UI8개·최종 APK 해시·단위20개 결과·원본 CSV 해시·상세/0거리 증거가 모두 일치했다. 검사 후 이번에 시작한 서버와 임시 에뮬레이터를 종료했다. 원래 AVD/CSV·기존 bundle·검증 자료는 삭제하지 않았다.

관련: [로드맵](../ROADMAP.md), [적용 계획](../source/docs/superpowers/plans/2026-11-04-mvp-scoring.md).

# ViewBinding 전환 검증

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

검사일: 2026-11-06. MainActivity·공통 패널·경로 행·입력 대화상자3개의 앱 소유 뷰 접근을 ViewBinding으로 전환했다. 기존 화면 구조·검증·Room 저장·서버/점수 정책은 유지했다. SDK/Canvas 동적 뷰와 framework AlertDialog 기본 버튼/목록 API는 라이브러리 소유 동작으로 유지한다.

대상: debug APK SHA256 `4c14fb98ad4346c1ce0863d6ef843f132ac0b825f082bec56bb5a0968b646db7`, JDK21·API35 에뮬레이터 emulator-5556, 기존 DB snapshot 로컬 서버. 실기기는 사용하지 않았다.

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| testDebugUnitTest / lintDebug / assembleDebug | BUILD SUCCESSFUL, 단위27개 실패0/오류0, lint 오류0/경고41 | [빌드 기록](build-result.json) |
| 도구 회귀 | 13개 통과 | [빌드 기록](build-result.json) |
| 생성 바인딩/소스 | 생성 클래스10개, 앱 Java/Kotlin findViewById·synthetic 참조0, 독립 코드 검토 중요 지적 없음 | [구현 로그](../../../log/log-2026-11-06-viewbinding.md) |
| 전체 통합 UI | 기능8개 통과, 종료0. 지도/검색·점수·취약구간·필터·Room 저장/재시작/오프라인/수정/재조회/삭제 | [전체 보고서](../android-2026-11-06_105047_109432/integration-ui.md) |
| 작은 화면 | 720×1280 density360, 지도 버튼48dp·검색/시설 수·좌표 입력 통과 | [화면 결과](../android-2026-11-06_110514_450523/viewbinding-layout-result.json) |
| 대화면 pane | 1200×1920 density320, 좌우 패널·검색/시설 수·입력·TMAP/로컬 전환·자료 정보 통과 | [화면 결과](../android-2026-11-06_110514_450523/viewbinding-layout-result.json) |

전체 보고서의 PASS9행 중1행은 외부 Android system ANR 창 Wait 처리이며 기능 검사는8개다. 앱 ANR을 성공으로 숨기지 않는다. 부팅 전 외부 System UI 지연도 로그에 별도 기록했다. lint 경고41개 중 새 XML 입력 필드의 Autofill 권장6개가 포함되며 오류는 없다.

일반 지도/취약 표시, 작은 화면/입력창, pane 결과/좌표 입력 캡처를 직접 확인했다. [대화면 결과](../android-2026-11-06_110514_450523/pane-counts.png), [입력창](../android-2026-11-06_110514_450523/pane-place-dialog.png). 화면 설정은 원래1080×2220/density440으로 복원했고 cleanup_errors는0개다. 서버 reverse도 복원했다. 설치 APK와 빌드/보관 APK 해시 일치 확인.

[검증 APK 묶음](../../delivery/2026-11-06-viewbinding/README.md), [설치·실기기 검사표](../../DEVICE-TEST.md).

실제 GPS·제조사별 동작/성능·사용자 최종 UI 판단·현장·전체 명세 인수는 미검증이다. 과거 API36.1 앱 소실 원인과 일반 창 크기 변경 시 미저장 상태 복원은 이번 전환으로 해결했다고 주장하지 않는다. 화면별 검사는 새 실행 기준이다. [명세 차이](../spec-audit-2026-11-05/functional-matrix.md)는 유지한다. 과거 APK/검증 문서는 당시 결과로 보존한다.

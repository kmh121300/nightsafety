# 앱 ViewBinding 전환

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

사용자가 코드 전체의 ViewBinding 전환을 명시 승인했다. MainActivity/RouteWorkflow의 모든 직접 뷰 검색, 공통 레이아웃 include·대화면 variant, 직접 만든3개 입력 dialog와 custom route row를 전환한다. [구현 계획](../source/docs/superpowers/plans/2026-11-06-viewbinding.md). 작성 시점 구현/검증은 진행 중이다. 기존 b863 APK/검증/설치 묶음은 당시 결과로 보존한다. DB·서버·Room schema·세로/글꼴 고정 정책 변경 없음.

## 구현과 생성 코드 확인

ViewBinding 활성화와 include ID를 추가하고 MainActivity/RouteWorkflow의 모든 findViewById를 제거했다. 동적 ID 배열은 실제 CheckBox/TextView 참조 목록으로 바꿨고 필터 순서는 기존 CCTV/비상벨/경찰/보안등과 동일하다. custom route row는 ViewRouteOptionBinding.inflate/bind로 생성/재사용한다. 입력 body3개를 XML로 옮기고 DialogPlace/DialogFavoriteName/DialogFavoriteEditBinding을 사용한다. 기존 ID/순서/힌트/16dp 수평 padding/숫자 입력/검증·저장 로직을 보존했다. framework AlertDialog 기본 버튼/목록 API와 SDK/Canvas 동적 뷰 생성은 라이브러리 소유 범위로 유지한다.

AGP 생성 ActivityMainBinding은 View root와 phone/pane nullable 필드를 만들었다. include ID를 재귀 검색하므로 일반/land/sw600dp의 공통 패널을 안전하게 찾으며 fallback도 생성 타입에 맞는다. 생성 이름/루트 타입을 실제 파일로 확인했다. 별도 read-only 코드 검토에서 중요한 문제 없음. 검토자는 빌드/ADB/UI를 실행하지 않았으므로 런타임 검증은 별도 진행한다.

시작 시 에뮬레이터가 없어 기존 API35 read-only 임시 데이터를 재기동했다. 부팅 후 System UI 응답 지연 창을 실제 제목으로 확인해 Wait만 선택했다. 새 바인딩 APK 실행 전 환경 관찰이며 앱 오류로 간주하지 않는다. 서버 health ready/DB verified 확인. 기존 데이터 초기화/DB 재가져오기 없음.

## 새 APK 빌드

2026-11-06 testDebugUnitTest/lintDebug/assembleDebug 성공(7분23초), 단위27개 실패0/오류0·도구13개 통과. AGP 생성 binding10개. lint 오류0/경고41(새 XML 입력 필드6개의 Autofill 권장 등 포함). 사용자 지정 데이터 입력을 보존하는 전환이며 자동완성 정책/새 의존성 버전을 임의 변경하지 않았다. [빌드 기록](../source/verification/viewbinding-2026-11-06/build-result.json).

APK SHA256 4c14fb98ad4346c1ce0863d6ef843f132ac0b825f082bec56bb5a0968b646db7. API35/5556 설치 Success와 실제 설치 해시 일치 확인 후 전체 UI 검사에 착수했다. 아직 전체 UI 인수 완료로 표기하지 않는다.

## 전체 UI 기능8개 완료

2026-11-06 11:03 KST [전체 UI 보고서](../source/verification/android-2026-11-06_105047_109432/integration-ui.md) 종료0. 지도/시설1381개·후보3개·anchor/숫자3지표·취약 상세/강조·필터·Room 저장/재시작/오프라인/이름·선호 수정/최신 재조회/본 시험항목 삭제8개 통과. 새 XML 장소/즐겨찾기 입력3개와 바인딩 행의 실제 흐름을 확인했다. 보고서에는 외부 Android system ANR Wait 처리1개가 추가 항목으로 남아 있으며 기능 검사를9개라고 세지 않는다. 앱별 ANR은 도구가 실패 처리한다.

일반 지도/점수 및 취약 강조 캡처를 직접 확인했다. 작은 화면과 pane 설정의 바인딩 inflate/핵심 UI 검사는 별도로 진행 중이다. 현재 새 APK의 실제 GPS/최종 사용자 UI·명세 전체 인수 완료는 아니다.

## 작은 화면/pane 완료와 설치 기록

2026-11-06 small720×1280/density360와 pane1200×1920/density320에서 binding inflate·48dp 버튼·검색/시설 수·좌표 입력 통과. pane은 좌우 패널과 TMAP/로컬 전환·자료 정보도 확인했다. 검사 종료0, cleanup_errors0, 원래1080×2220/density440 및 reverse 복원. 작은 화면/입력 및 pane 결과/좌표 입력 캡처를 직접 확인했다. [화면 결과](../source/verification/android-2026-11-06_110514_450523/viewbinding-layout-result.json).

[종합 검증](../source/verification/viewbinding-2026-11-06/verification.md)과 별도 [ViewBinding 설치 묶음](../source/delivery/2026-11-06-viewbinding/README.md)을 작성했다. APK 복사본 해시 일치, ROADMAP·README·DEVICE-TEST의 최신 대상과 계획 체크를 갱신했다. 과거 APK/검증은 보존했다. 실제 GPS·제조사·사용자 최종 UI/전체 명세·현장 인수는 미완료다.

최종 확인 2026-11-06 11:14 KST: 변경 문서8개의 수정일/내부 링크 검사 통과(기존 무관한 발표 문서 누락2개 제외). 빌드/보관/설치 APK·manifest·checksum 해시 일치, 소스 직접 검색0, 단위27/실패0/오류0 재확인. 앱 PID13189 실행, health ready, reverse8765 및 원래 화면 설정 확인. 이후 코드/설정 변경 없음.

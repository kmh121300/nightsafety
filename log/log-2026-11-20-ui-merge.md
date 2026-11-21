# UI 담당자 수정본 병합

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 시간 기준: Asia/Seoul

## 백업과 반영 범위

사용자 요청으로 현재 프로젝트를 백업한 뒤 UI 담당자 수정본을 병합했다.

- 수신 폴더: `C:/Users/kmh12/Downloads/night_safety_ui/night_safety_ui`
- 비교 기준: 프로젝트 루트 `night_safety_ui.zip`.
- 백업: `C:/2026591004/source/1-2/moblie-backups/moblie-before-ui-merge-2026-11-20_094850.zip`
- 백업574파일, 342,834,668바이트. ZIP CRC와 포함 파일 전부 SHA-256 원본 대조 통과.
- 소스·설정·문서·기존 검증/배포 자료 포함. 생성물/환경 폴더 `.git`, `.gradle`, `.kotlin`, `.idea`, `.venv`, `build`, `__pycache__` 제외. 로컬 복원용 백업이다.

UI 리소스13개 수정·4개 추가. 수정 대상13개가 현재 프로젝트와 전송 원본에서 동일하고 신규4개 이름이 겹치지 않음을 확인한 뒤 복사했다. 짙은 남색/민트 팔레트, 검색창·툴바·바텀시트·시설 팝업 스타일을 반영했다.

기본 테마를 `Theme.Material.NoActionBar`로 변경하고 상태바/탐색바의 밝은 배경용 아이콘 설정을 해제했다(기존 styles2개). 새 어두운 배경에 기본 대화상자와 시스템 아이콘 색상을 맞추는 병합 호환 보완이다. Kotlin·서버·DB·자산 데이터·local.properties·빌드 설정은 변경하지 않았다.

- drawable 수정5개: `ui_bottom_sheet_bg.xml`, `ui_button.xml`, `ui_card.xml`, `ui_field.xml`, `ui_metric.xml`
- drawable 추가4개: `ui_dot_amber.xml`, `ui_dot_mint.xml`, `ui_glass_card.xml`, `ui_route_card_bg.xml`
- layout 수정7개: `activity_main.xml`, `dialog_facility_cluster.xml`, `dialog_place.xml`, `view_map_panel.xml`, `view_result_panel.xml`, `view_search_card.xml`, `view_toolbar.xml`
- values 수정1개: `colors.xml`
- 호환 보완2개: `values/styles.xml`, `values-v27/styles.xml`

## 2026-11-20 검증

환경: Windows / JDK21.0.11 / Gradle9.7.1 / compileSdk36. 대상은 이 병합 직후 source 코드와 아래 APK다.

- 수신 레이아웃 기존 ID/위젯 종류 보존 확인. 병합 후 XML35개 파싱 통과.
- 백업 대비 기존 소스 수정 파일이 UI13개+styles2개뿐임을 확인했다. 신규4개는 수신본과 일치한다.
- `assembleDebug testDebugUnitTest lintDebug --console=plain`: 종료코드0, BUILD SUCCESSFUL(2분43초).
- 단위39개 성공, 실패/오류/skip0. lint 오류0·경고50.
- [Gradle 실행 기록](ui-merge-2026-11-20-gradle.txt)
- [APK](../source/app/build/outputs/apk/debug/app-debug.apk): 44,724,410바이트.
- APK SHA-256: `e3aa9b935e3e95419c69b38ba1f5ea7499de9464cfc9f4cfd3e81bab55d0ff2f`
- [lint 보고서](../source/app/build/reports/lint-results-debug.html): 작은 글자, 하드코딩 문구, 미사용 리소스 등 경고가 남는다. 경고 전체 해소는 이번 병합 범위에 포함하지 않았다.

에뮬레이터/실기기 화면 캡처·GPS·전체 명세 인수·DB/API 재검사는 수행하지 않았다. 작은 버튼(32~44dp), 긴 텍스트/작은 화면 가독성과 화면 크기별 레이아웃은 실행 확인이 필요하다. 과거 UI 검사 성공을 이번 APK의 성공으로 재사용하지 않는다.

## 2026-11-20 후속 에뮬레이터 검사

사용자 요청으로 API35/emulator-5556에 동일 해시 APK를 설치하고 화면 검사했다. 로컬 원본 서버 경로 검색·시트·필터·입력창·자료 정보·저장 목록·시설 묶음·전체화면/복귀를 확인하고, 최종 TMAP 실제 배경지도 표시를 확인했다. 작은 화면720×1280/360dpi 관찰 후 기본1080×2220/440dpi 복원. 상태바 대비/로컬 안내 겹침·작은 화면 부제 줄바꿈/출처 가림을 발견했다. 앱 추가 수정 없음. DB 서버 시작 실패 후 로컬 Engine으로 검사했으므로 DB/전체 인수 성공이 아니다. [검증/캡처](../source/verification/ui-merge-2026-11-20/verification.md).


## 2026-11-20 DB 재활성화 후 검사

DB health configured/verified=true, startup_snapshot 로딩 및 API35 앱 경로 검색 성공. 전체9.1/평균13.0/취약0.0, CCTV16/비상벨16/보안등12 확인. DB 쓰기/전체 인수는 미검증. [결과/캡처](../source/verification/ui-merge-2026-11-20/verification.md).

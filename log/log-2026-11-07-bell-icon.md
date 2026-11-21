# 비상벨을 종과 울림 아이콘으로 변경

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

사용자가 기존 비상벨 아이콘이 배터리처럼 보인다고 지적하고 빨간 원형 배지 안 흰색 클래식 종/양옆 소리 파동을 요청했다. 공통 facility_bell.xml만 변경해28dp 크기와 공유 bitmap 로더/양 지도 호출부·필터·상세·좌표/점수/DB는 유지했다. 빨강 #D32F2F 원형, 흰 테두리/종/클래퍼와 좌우 울림 선을 적용했다. 신규 코드/의존성은 없다.

검사일2026-11-07 20:03 KST, API35 Android15 Pixel_3a emulator-5556/host GPU/기존 별도 read-only 임시 VM. assembleDebug BUILD SUCCESSFUL in11s. install-r 후 재시작하여 TMAP 지도 준비 완료와 전체화면을 확인했다. [TMAP 캡처](../source/verification/android-2026-11-07_200300_734018/bell-tmap.png)와 [로컬 캡처](../source/verification/android-2026-11-07_200300_734018/bell-local.png)를 직접 열어 빨간 배지/흰 종/양옆 울림 표시를 확인했다. 검사 후 native 전체화면으로 복귀했다. [대상 APK/해시 결과](../source/verification/android-2026-11-07_200300_734018/bell-result.json), [새 설치 묶음](../source/delivery/2026-11-07-bell-icon/README.md).

APK SHA256 `052d11c7d90727adfdb3edd1ed5e29d30935ec60c6fb9509a7c661f2f81a432f`. 설치/빌드/보관/manifest/checksum 일치 확인. ROADMAP 현재/R4/별도 이력과 README/DEVICE-TEST 최신 설치 대상을 갱신했다. 과거 APK/검증을 덮어쓰지 않았다. 단일 vector 리소스 변경으로 단위/lint·상세/필터·서버/DB/Room 전체 재검사는 반복하지 않았다. 직전31개 단위/lint 오류0/경고40·상세/필터 성공은 당시 APK 근거다. 밀집 마커 겹침·실기기/GPS·사용자 최종 UI/전체 인수는 미완료다.

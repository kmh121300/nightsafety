# 시설 아이콘 마커 변경

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

사용자가 제안된 CCTV 카메라·비상 호출 버튼·보안등 가로등·경찰 방패 아이콘과 흰 배경/테두리를 승인했다. 기존 색은 보조로 유지한다. 28dp vector badge4종을 TMAP/로컬 미리보기에서 같은 bitmap helper로 초기화 때만 생성한다. native 중심 anchor/priority6으로 경로/출발·도착 핀을 우선 표시한다. 기존100m 필터·overlay diff/배치·시설 상세·polygon·경로/점수/서버/DB/Room을 유지한다. 추가 의존성/이미지 생성/클러스터링은 도입하지 않는다. 검증은 진행 중이다.

## 검증 결과

2026-11-07 KST API35 Pixel_3a emulator-5556/host GPU, 새 임시 datadir read-only VM에서 검사했다. 기존 user AVD/즐겨찾기는 보존했다. 첫 offline VM은 해당 시험 프로세스만 종료했고 재시작 부팅 전 설치의 package/activity 미준비 실패 후 부팅 완료를 대기해 install-r 성공했다.

최종 빌드3m59s·단위31 실패0/오류0, lint 오류0/경고40. 4개 vector path 고유성/28dp/흰 배경 정적 검사 PASS. 새 helper의 호환 drawable 로딩 권장 및 기존 Bitmap KTX/기타 경고가 남으며 lint 오류는 없다. TMAP/로컬 최종 전체화면을 캡처하고 직접 열어 CCTV/비상벨/보안등 아이콘과 경로/끝점 우선 표시를 확인했다. 양 지도에서 비상벨 마커 직접 터치로 상세를 열었고 CCTV 필터 off1111→on1381 복구를 통과했다. 첫 임시 상세 검사가 실제 닫기 대신 확인 문구를 기대해 대기했으나 상세 자체는 열려 있었으며 검사만 바로잡았다. 검사 마지막에는 native 전체화면으로 돌아왔다.

[검증·캡처·빌드·UI 결과](../source/verification/facility-icons-2026-11-07/verification.md), [새 APK/해시](../source/delivery/2026-11-07-facility-icons/README.md). ROADMAP 현재/R4/별도 이력, README/DEVICE-TEST를 갱신했다. 이전 APK/전체 UI8/화면3프로필 기록은 당시 근거로 보존했다. 이번에는 서버/DB·Room 전체 흐름/다른 화면 크기를 반복하지 않았다. 경찰 방패는 resource 검증이며 기본100m 안에 객체가 없어 실제 지도 캡처 검증은 하지 않았다. 정왕역 밀집 지점의 아이콘 겹침은 남고 확대/필터로 구분한다. 클러스터링은 추가하지 않았다. 실기기/현장/사용자 최종 UI·전체 인수는 미완료다.

최종 정합성: 설치/빌드/보관 APK·manifest/checksum/UI 결과 해시 일치, 변경 문서 수정일/내부 링크(기존 발표 문서2개 누락 제외) PASS. 코드 변경 없이 설치 복사본/문서만 정리해 재빌드하지 않았다.

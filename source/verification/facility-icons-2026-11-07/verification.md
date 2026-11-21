# 시설 아이콘 마커 검증

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

검사일2026-11-07 KST. 대상 debug APK SHA256 `73c803010d855b7177f2724851388a5dac1b72b765f2905b50f7edf94c46b4c0`. API35 Android15 Pixel_3a emulator-5556, host GPU, 별도 임시 datadir의 read-only 환경. 기존 사용자 AVD/즐겨찾기는 변경하지 않았다. 실제 휴대폰 검사는 수행하지 않았다.

CCTV 카메라·비상 호출 버튼·보안등 가로등·경찰 방패4개 vector를 같은28dp 흰 배지/테두리로 만들었다. 색은 종류를 보조한다. bitmap은 renderer 초기화 때 생성해 재사용하고 TMAP 중심 anchor와 priority6으로 선택 경로/출발·도착 핀을 우선 보인다. 로컬 그림/터치 처리와 native overlay diff/배치·시설 상세 경로는 유지한다. polygon은 기존 면/선 표시를 유지한다. 신규 의존성·클러스터링·좌표 이동은 추가하지 않았다.

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| testDebugUnitTest / lintDebug / assembleDebug | BUILD SUCCESSFUL in3m59s, 단위31 실패0/오류0, lint 오류0/경고40 | [빌드](build-result.json) |
| vector 정적 검사 | 4종 고유 path·28dp 크기·흰 배경 XML 확인 PASS | [빌드](build-result.json) |
| TMAP/로컬 | 최종 APK의 전체화면 아이콘을 직접 캡처/열어 확인 | [TMAP](../android-2026-11-07_194656_556943/facility-icons-tmap.png), [로컬](../android-2026-11-07_194656_556943/facility-icons-local.png) |
| 마커 상세/필터 | 별도 최종 결과 참조 | [UI 결과](../android-2026-11-07_194656_556943/marker-result.json), [native 상세](../android-2026-11-07_194656_556943/facility-tmap-detail.png), [로컬 상세](../android-2026-11-07_194656_556943/facility-local-detail.png) |

첫 read-only VM이 offline 상태여서 해당 시험 프로세스만 종료하고 임시 datadir로 재시작했다. 부팅 완료 전 첫 설치 시도는 package/activity service 미준비로 실패했고 부팅 완료 후 install-r 성공했다. 첫 임시 상세 검사에서 실제 닫기 버튼에 확인 문구를 기대해 대기한 오류가 있었으며 UI에는 비상벨536 상세가 정상 열려 있었다. 검사 문구를 닫기로 바로잡아 재확인했다. 앱 수정은 필요하지 않았다.

주변 시설이 밀집한 정왕역 쪽에서는 아이콘끼리 겹친다. 확대/시설 필터로 구분하며 자동 클러스터링은 이번 범위에 없다. 경찰 방패는 resource 검사 완료이나 기본100m corridor에 경찰 객체가 없어 이 캡처에서 실제 마커를 확인하지 않았다. 구간 등급/안전점수·서버 검색/Room 전체8개·다른 화면 크기 회귀·실기기 GPS/OEM·실제 도로 정합성·전체 인수는 이번 변경에서 재검증하지 않았다. 이전 전체 검증은 [당시 APK 기록](../route-display-2026-11-07/verification.md)으로 보존한다.

[설치 묶음](../../delivery/2026-11-07-facility-icons/README.md), [작업 로그](../../../log/log-2026-11-07-facility-icons.md).

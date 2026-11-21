# 시설 종류와 주소 표시 검증

작성일: 2026-11-07 · 최종 수정일: 2026-11-07 · 시간 기준: Asia/Seoul

검사일2026-11-07 20:37~20:39 KST. API35 Android15 Pixel_3a emulator-5556/host GPU/기존 임시 read-only VM. 최종 debug APK SHA256 `c02aed75eea3ab417c023d702ec7aa6a60d53311228fadb6578c0aff52582f4a`.

## 범위와 자료 근거

CSV 행 번호를 종류+주소로 바꾸라는 사용자 승인을 적용했다. PilotData의 공통 title을 도로명주소 우선→지번→주소 정보 없음으로 만들고 상세에도 같은 주소 선택 함수를 사용한다. 원본 csv_row와 식별 ID는 내부에서 유지한다. 경찰 후보 표기/알려진 시설명은 상세에서 보존한다. 보안등도 기존 관리번호 형태의 name 대신 주소 제목을 사용한다.

기존 앱 CCTV/비상벨 GeoJSON에는 주소 컬럼이 누락돼 있었다. 원본 csv와 과거 연구 source 복사본의 bytes가 같은지 확인하고, 헤더 포함 csv_row(첫 데이터 행2)로 접근해 모든508개 행의 WGS84 좌표(오차1e-8 미만)/기준일/파일명을 대조했다. CCTV270/비상벨238 모두 일치·주소 보유를 확인한 뒤 도로명/지번2개 필드만 앱 자료에 추가했다. 주소2개 필드를 제거하면 이전 JSON과 완전히 같음을 assert했다. 원본 CSV·과거 연구 GeoJSON·DB는 수정하지 않았다. 기존 audit_facilities.py exporter에도 동일2개 컬럼 보존을 추가해 다음 생성 시 누락되지 않게 했으며 문법 검사를 통과했다. 해당 exporter 전체 실행/과거 산출물 재생성은 하지 않았다.

[자료 대조 결과/원본·앱 자료 해시](address-provenance.json). 좌표/기록 수/날짜/점수/시설 유형/경로/서버/Room schema는 변경하지 않는다. 서버/즐겨찾기 복원도 현재 앱 facilities 목록을 재사용하므로 동일 제목 생성 경로다(호출부 코드 확인, 전체 재실행은 아님).

| 검사 | 결과 | 근거 |
| --- | --- | --- |
| testDebugUnitTest/lintDebug/assembleDebug | 단위38 실패0/오류0, 빌드32s 성공, lint 오류0/경고41 | [빌드](build-result.json) |
| 새 제목 회귀2개 | 변경 전 지정9개 중 새2개 ComparisonFailure 확인 후 전체38개 통과. 도로명/지번/blank/null fallback·이전 숫자 name 숨김·ID 유지·실제 CSV 주소/상세 포함 검증 | [로그](../../../log/log-2026-11-07-facility-address-titles.md) |
| Native 묶음→상세 | CSV 행 번호 대신 종류+실제 주소 목록·상세 제목/본문 주소 확인 | [목록](../android-2026-11-07_203755_421773/addresses-tmap-list.png), [상세](../android-2026-11-07_203755_421773/addresses-tmap-detail.png) |
| Local 묶음→상세 | 같은 제목/주소 확인 | [목록](../android-2026-11-07_203755_421773/addresses-local-list.png), [상세](../android-2026-11-07_203755_421773/addresses-local-detail.png) |

[최종 UI 결과/해시](../android-2026-11-07_203755_421773/address-result.json). 두 지도 목록에서 종류 뒤 순수 숫자 형식이 없고 실제 주소가 포함되는지 자동 검사했으며 캡처도 직접 열어 확인했다. 최종 설치/빌드/보관/manifest/checksum 해시는 일치한다. 검사 후 native 전체화면으로 복귀했다.

실기기/GPS/OEM·다른 화면 크기·서버/Room 전체 UI8·DB 재가져오기·전체 명세/운영 인수는 이번에 반복하지 않았다. 동일 주소의 시설 기록이 여러 개면 종류/주소가 같게 보일 수 있으며 별개 기록/묶음 수는 유지한다. 자료 기반 주소이며 현장 위치 검증은 별도다. 이전 묶음 동작/확대/필터 검증은 [당시 APK 기록](../facility-clusters-2026-11-07/verification.md)으로 보존한다.

[설치 APK](../../delivery/2026-11-07-facility-addresses/README.md), [개발 로그](../../../log/log-2026-11-07-facility-address-titles.md).

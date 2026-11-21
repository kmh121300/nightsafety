# 오류 검사 첫 시도 실패

작성일: 2026-11-05 · 최종 수정일: 2026-11-05 · 시간 기준: Asia/Seoul

API35 emulator-5556, 최신 APK 해시 ebf2b079d96fccd74381278cb98b9648c3caaf7081f63ddaacf02d1296bf91d9.

빈 검색 후 도구가 `검색어를 입력하세요`를 XML에서 찾지 못해 실패. failure.png에는 오류 아이콘이 있고, 별도 field focus 후 blank-focus.png에서 해당 안내 문구를 직접 확인했다. Android EditText 오류 popup이 UIAutomator XML에 없으므로 도구를 캡처 확인 방식으로 수정했다. 앱 코드 오류로 단정하지 않는다.

복원 후 appops가 `MOCK_LOCATION: default`를 반환했는데 도구는 `Default mode: deny` 표기만 허용했다. 이어 빈 AssertionError의 splitlines()[0] 처리까지 실패해 최초 자동 JSON이 남지 않았다. 이 보고서와 당시 캡처를 별도 보존한다. 설정은 실제 기본값으로 돌아갔고 위치 권한 원상복원 확인은 재실행에서 별도로 검사한다. mock 표기/빈 오류 처리 회귀2개를 추가했다.

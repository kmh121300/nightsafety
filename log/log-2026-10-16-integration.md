# 밤길 지킴이 통합 개발 로그 — 2026-10-16

작성일: 2026-10-16 · 최종 수정일: 2026-10-26 (문서 안내 추가) · 작업/검증 기준일: 2026-10-16

DB 미연결과 다음 우선순위 등 아래 내용은 당시 기록입니다. 현재 상태와 순서는 [전체 로드맵](../ROADMAP.md), 이후 DB 결과는 [2026-10-26 DB 로그](log-2026-10-26-database.md)를 확인합니다.

## 요청과 범위

팀 TMAP 앱키 설정 후 앞서 남긴 다음 작업 전체를 진행했다. 사용자가 DB는 아직 없는 상태를 선택해 로컬 서버와 PostGIS 준비 도구로 진행했다. 외부 DB 생성·배포는 하지 않았다.

## 구현

1. **TMAP 실제 지도:** 팀 키 인증·배경지도·511개 시설 기록·기존 두 경로·시설 필터 실행 확인. 키를 로그·채팅에 출력하지 않음.
2. **Python 서버:** localhost:8765 HTTP API, 실제 OSM 그래프의 동적 Dijkstra 탐색, 빠른/시설 비용/균형/보행선 후보, 중복 제거·추가시간 상한. 기존 연구 결과 파일을 덮어쓰지 않음.
3. **시설 지표:** 20m 이하 segment, 5m 이하 길이 가중 표본, 유형별 최대 기여·20/50/100m kernel, 약한10% 길이·0.3 가중 조합. 실제 시설 비용이 후보 탐색에 반영됨.
4. **앱 입력·통신:** 직접 좌표·OSM 장소명 검색, 출발/도착 교환, 서버 결과 표시·최신 요청만 반영·취소·오류·timeout. 개발용 평문 HTTP는 debug loopback만 허용.
5. **구간 표시:** 정확한 과거 표본 하위10% 길이를 주황색으로 표시하고 구간 설명 제공. 부분 자료의 grade는 unknown 유지.
6. **Room:** 즐겨찾기 저장·목록·이름/선호유형 수정·삭제·과거 snapshot 오프라인 복원·최신 재검색. 사용자/OSM endpoint와 자체 결과만 보관.
7. **PostGIS 준비:** schema/index, 명시적 가져오기·읽기 전용 확인 도구. 실제 DB 연결은 미실행이며 현재 HTTP 탐색은 메모리 그래프 사용.

## 상태와 데이터 정책

- CCTV2026-01-20·비상벨2026-01-22는180일 정책을 넘은 과거 자료다. historical_experimental 모드로만 비교한다.
- 가로등 누락과 과거 자료 때문에 공식 점수·현재 safe/balanced 추천은 null. 별도 과거 CCTV·비상벨 지표와 비교 후보만 제공한다.
- 선택한 실제 그래프 지점까지의 complete와 현장 보행 verified는 별개다. 실제 역 출구와12.56m 연결은 여전히 미검증이다.
- 동일 보행 anchor는 geometry=null·거리/시간0·점수null이다. SDK에 빈 선을 전달하지 않게 처리했다.
- marker511기록은 CCTV270+비상벨238+OSM 경찰시설3객체다. 서버 집계·점수는 CCTV/비상벨만 사용한다.

## 검토에서 수정한 문제

- 즐겨찾기 저장 중 입력 변경 시 다른 즐겨찾기의 ID를 덮어쓸 수 있던 경쟁 상태: ID 반영을 UI의 같은 revision에 한정.
- 저장 대화상자 도중 위치 변경으로 이전 snapshot과 새 endpoint가 섞이는 문제: endpoint·유형·ID·revision 캡처 및 확인.
- 선호유형을 재조회 후 빠른 유형으로 바꾸던 문제와 삭제한 ID가 남던 문제 수정.
- 후보를 하나도 못 계산한 timeout은 no_route가 아닌 HTTP504. 이전 후보가 있으면 partial_success 유지.
- Android의 label/source 포함 endpoint와 서버의 strict 좌표 계약 불일치 수정. metadata로 연결 검증을 승격하지 않음.
- 정책 응답에 실제 추가시간 상한·Dijkstra·탐색 계수를 기록. 단절 탐색 완료 플래그와0거리 계약 검증.
- lint의 loopback domain 속성을 명시해 오류 제거. 자료와 연결 한계는 조작 패널 밖에 표시.

## 검증

- Android 단위 테스트14개: 원본 파서5, 서버 응답/timeout/0거리4, Room 입력 검증5. 실패0.
- 서버 테스트11개: 공식 점수 null·fixture61.25·kernel 경계·중복 기여·가중 약한 구간·동적 탐색·시설 위험 비용·우회 상한·입력·HTTP 경계·참조 위조·timeout·0거리 등. 실패0.
- Android lint: 오류0 / 경고47. Debug APK 빌드 성공.
- TMAP 실제 인증·지도·기존 두 경로와 필터 검증 완료.
- 최종 통합 UI 검사 통과: TMAP 실지도, 서버 후보3개, anchor 검색, 연결/과거자료 안내, 주황색 구간 표시, 시설511→241→511 필터.
- Room 저장 후 앱 강제종료·재시작 및 서버 연결 제거 상태의 오프라인 복원 통과. 이름/선호유형 수정, 보행선 우선으로 최신 재조회, 삭제 후 목록 반영까지 통과.
- 자동화 도구는 키보드 닫힘 후 대기와 native 확인 버튼 식별을 보완했다. 이전 자동 클릭 실패는 수동 저장 성공 및 보완 후 전체 재실행으로 확인했다.
- 서버 테스트 최종 재실행:11개 통과(17.464초). 0거리 추가 회귀 통과: 동일 OSM anchor 선택 시0m/0.0분, 공식점수 미산출, 빈 경로선을 SDK에 전달하지 않고 앱 정상 동작.

## 가로등 원천 재확인

2026-10-05 HTTP502와 달리 이번에는 Smartstlamp HTTP200·정상 JSON과 좌표 필드를 확인했다. 다만 무인증 pSize100 요청은 총71건 중 만안구5건을 반환했고, 시흥시 커버리지·전수 조회는 검증되지 않았다. 해당 샘플은 앱이나 공식 점수에 넣지 않았다.

근거: [원천 재확인](../source/verification/data-source-review-2026-10-16.md), [호출 기록](../source/verification/lamp-source-check-2026-10-16.json).

## 주요 파일과 실행

- [최신 실행 안내](../source/README.md)
- [서버 API·DB 준비](../source/server/README.md)
- [TMAP 인증 증거](../source/verification/tmap-auth.md)
- [통합 UI 검사](../source/verification/integration-ui.md)
- [APK](../source/app/build/outputs/apk/debug/app-debug.apk)

```powershell
python -X utf8 server/app.py
.\gradlew.bat :app:testDebugUnitTest :app:lintDebug :app:assembleDebug
python -X utf8 -m unittest discover -s server -p "test*.py" -v
python -X utf8 tools/integration_smoke.py
```

## 외부 조건이 남은 항목

실제 PostgreSQL/PostGIS 연결·성능·운영 배포, 시흥 가로등과 최신 시설 snapshot, 원본 CSV 이용조건, 교문·출구·보도·횡단·접근성 현장 조사, 실제 기기 GPS 허용 흐름은 별도 확인이 필요하다. 이 로그를 현재 안전 안내 서비스의 완성·현장 검증 증거로 해석하지 않는다.

## 최종 전달 상태

Debug APK 생성·에뮬레이터 설치와 통합 확인 완료. 로컬 서버는127.0.0.1:8765에서 실행 중이며 외부 DB는 연결하지 않았다. 다음 우선순위는 실제 DB 연결 검증 → 시흥 가로등/최신 시설 자료 확보 → 교문·출구와 보행 현장 검증 → 실제 기기 GPS 및 HTTPS 운영 서버 확인이다.

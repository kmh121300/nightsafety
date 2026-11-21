# 지도 길게 누르기·가까운 보행 지점 선택 가능성 확인

작성일: 2026-11-20 · 최종 수정일: 2026-11-20 · 시간 기준: Asia/Seoul

## 요청과 범위

사용자가 구현 전 지원 여부 확인을 요청했고, 보행망에서 멀면 가까운 보행 지점으로 연결하는 방향을 제시했다. 이번 작업은 정적 조사만 수행했으며 앱/서버 동작을 구현하거나 빌드·DB/UI 검사를 실행하지 않았다.

## 실제 확인한 근거

- 현재 `source/app/libs/tmap-sdk-3.7.aar`의 classes.jar를 임시 폴더에서 javap(JDK21.0.11)으로 조사했다.
- `TMapView.setOnLongClickListenerCallback(TMapView.OnLongClickListenerCallBack)` 존재 확인.
- `OnLongClickListenerCallBack.onLongPressEvent(ArrayList<TMapMarkerItem>, ArrayList<TMapPOIItem>, TMapPoint)` 존재 확인. 길게 누른 좌표를 받는 콜백을 현재 SDK가 지원한다.
- 앱 TmapPilotMap.kt는 현재 일반 누름/해제 콜백만 등록하므로 길게 누르기 메뉴 연결은 새로 구현해야 한다. 로컬 PilotPreviewView의 터치 처리는 별도이므로 동등 지원을 원하면 그쪽 좌표 변환/길게 누르기도 필요하다.
- 서버 Engine.anchor는 가까운 graph node를 고르지만 간격30m 초과를 거절한다. 먼 지점 자동 보정은 현재 제공하지 않는다. 입력 좌표는 파일럿 BBOX 밖도 거절한다.
- RouteWorkflow는 이미 좌표 기반 출발/도착과 경로 검색을 사용한다. 지도 선택을 이 흐름에 연결할 수 있다.
- [기능 명세](../md/night-safety-functional-specification-ko.md)의 요청점/anchor 구분(본문157행, F-03-02)은 미검증 간격을 실제 보행 연결로 간주하지 않는다. 선택 지점을 가까운 보행 지점으로 보정해 그 anchor부터/까지 검색하고 원래 좌표 및 보정 거리를 안내하는 방식은 이를 유지할 수 있다. 가까운 점이 서로 단절된 그래프에 속하면 경로 없음 처리는 여전히 필요하다.
- [TMAP 공식 API 안내](https://tmapapi.tmapmobility.com/main_stg.html)에서도 길게 누르기 콜백/좌표 전달 설명을 교차 확인했다. 실제 설치 SDK 인터페이스의 철자와 형식은 위 javap 결과를 기준으로 한다.

## 구현 시 적용할 방향과 미지원 범위

지도 길게 누르기→출발지/도착지 선택→필요하면 가까운 사용 가능한 보행 지점으로 보정→핀/입력값·보정 거리 표시→기존 경로 검색으로 연결하는 방식이 가능하다. 보정은 실제 도로를 새로 생성하거나 클릭 위치와 보행망 사이의 직선을 보행 가능한 구간으로 승인하는 것이 아니다. 필터 없는 무제한 원거리 보정·파일럿 밖 서비스 확대는 이번 조사로 승인/구현된 것이 아니다.

SDK의 실제 터치 발생/좌표 정확도·지형/장애물·그래프 component 기반 후보 선택·보정 거리 상한은 구현 및 검증 전이다. 현재 기능 상태는 미구현 유지. 앱 코드/키/설정/DB 변경 없음.

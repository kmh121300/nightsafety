# ViewBinding Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan inline.

작성일: 2026-11-06 · 최종 수정일: 2026-11-06 · 시간 기준: Asia/Seoul

**Goal:** 사용자 요청대로 앱 소유 XML/대화상자/행의 뷰 접근을 ViewBinding으로 전환하고 화면/동작을 유지한다.
**Architecture:** ActivityMainBinding으로 inflate한다. phone/land/sw600dp include에 ID를 붙이고 생성된 nullable pane 바인딩을 onCreate에서 한 번 선택해 toolbar/search/map/result의 타입 안전 바인딩으로 사용한다. RouteWorkflow는 필요한3개 패널 바인딩을 받는다. SDK/Canvas 뷰는 기존처럼 바인딩된 container에 붙이며 framework AlertDialog의 built-in 버튼/목록 API는 유지한다.
**Tech Stack:** 기존 Kotlin/XML·AGP ViewBinding, Room·서버·SDK 버전 변경 없음.

- [x] buildFeatures.viewBinding 활성화, 공통 include ID와 pane include ID 추가. 실제 Gradle 바인딩 생성 결과로 qualifier 타입/누락을 확인한다.
- [x] MainActivity의 모든 findViewById/ID 목록을 패널 바인딩/실제 뷰 목록으로 바꾼다. custom route row도 ViewRouteOptionBinding으로 inflate/reuse한다.
- [x] RouteWorkflow의 뷰 접근을 전달받은 바인딩으로 바꾸고, 장소 입력/즐겨찾기 이름/수정 본문을3개 XML+바인딩으로 옮긴다. 기존 ID·필드 순서·padding·입력 유형·validation/비동기/저장 동작을 보존한다.
- [x] source의 findViewById와 programmatic form 생성이 남지 않는지 확인한다. 단위27개·도구 검사·lint·APK 빌드 및 생성 바인딩을 검사한다. 별도 구현 복제 테스트는 추가하지 않는다.
- [x] 현재 서버/시험 AVD에 새 APK를 설치하고 검색·필터·구간·Room 저장/재시작/복원/수정/삭제 전체 UI를 검사한다. small/standard와 대화면 pane의 inflate/핵심 흐름을 확인한다.
- [x] 새 APK는 기존 설치 묶음을 덮지 않고 별도 viewbinding 묶음으로 보존한다. ROADMAP·로그·설치 안내의 최신 대상을 바꾸고 날짜/링크/해시를 확인한다.

Activity가 바인딩과 workflow를 소유한다. 기존 close/handler·executor 취소·isDestroyed 검사를 보존하며 Fragment용 해제 패턴이나 새 아키텍처는 추가하지 않는다. 세로/글꼴 고정·안전 지표 정책/DB/Room schema는 변경하지 않는다. 전체 명세·실기기/현장/최종 사용자 UI 인수는 별도다.

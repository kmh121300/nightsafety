# GitHub 팀 공유용 보안 정리

작성일: 2026-11-21 · 최종 수정일: 2026-11-21 · 시간 기준: Asia/Seoul

사용자 승인으로 [이전 점검](log-2026-11-21-github-ignore-review.md)의 누락을 보완했다. root gitignore 추가/source 규칙 보완으로 실제 키가 있던 ZIP1개와 APK10개 및 개인 환경·키·서명/백업·생성물을 제외했다. 기존 파일/설정 값은 삭제하거나 수정하지 않았다. SDK/래퍼/앱 자산/보행망 입력은 포함하고, 값이 비어 있는 설정 예시2개와 팀 실행 안내를 준비했다.

변경 문서 링크 검사에서 root README/ROADMAP의 기존 발표 문서 링크2종이 존재하지 않는 이름을 가리켜 실제 `md/슬라이드별.md`, `md/해설.md`로 복구했다. 과거 결과/날짜/문서 본문은 변경하지 않았다.

## 2026-11-21 검증

Windows/Python/Git. 프로젝트 밖 임시 저장소로 전역 ignore 영향을 제거해 check-ignore/ls-files/실제 git add를 검사했다. 최초 정제 후 후보701개 약132MB, 알려진 현지 키/DB 비밀값 및 일반 비밀 패턴0건, SDK/JAR 중첩 archive7개 검사. 필수18개 포함/문제 산출물과 민감 경로28개 제외 및 임시 인덱스 일치 통과. [상세 환경·근거·범위](../source/verification/github-share-2026-11-21/verification.md), [기계 판정](../source/verification/github-share-2026-11-21/verification.json).

문서 정리 후 UTF-16 출력17개와 중첩 archive7개를 포함해 다시 검사했다. 최종 검사 시점704개/132,252,895바이트, 비밀값/패턴0건·실제 임시 Git 추가 일치·문서 링크/날짜·빈 설정 예시 검증 통과. [최종 결과](../source/verification/github-share-2026-11-21/final.json).

업로드/프로젝트 git init/커밋은 하지 않았다. 앱/DB 변경이 없어 빌드/DB/API 재검사를 하지 않았고 앱 상태 기준일은2026-11-20을 유지한다. 과거 원격 이력·SDK/데이터 재배포 조건·모든 미지의 비밀값 탐지는 미검증이다.


## 2026-11-21 대상 저장소 확인

사용자가 지정한 https://github.com/kmh121300/nightsafety 는 익명 웹 접근에서 빈 저장소로 표시됐고 git ls-remote에서도 참조가 반환되지 않았다. 작업 폴더 root/source는 Git 저장소로 초기화되지 않은 상태다. 최상위 폴더에서 main 초기화→origin 연결→제외 규칙이 적용된 파일 추가/확인→최초 커밋/푸시 순서를 안내했다. Git 초기화/커밋/푸시·원격 설정 변경은 실행하지 않았다. 삭제된 과거 이력/재배포 조건까지 확인한 것은 아니다.

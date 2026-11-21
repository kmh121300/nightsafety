# GitHub 공유 전 gitignore 점검

작성일: 2026-11-21 · 최종 수정일: 2026-11-21 · 시간 기준: Asia/Seoul

## 범위와 결론

사용자가 팀원들이 GitHub에서 프로젝트를 내려받을 수 있도록 현재 gitignore 상태 확인을 요청했다. 앱/서버/제외 규칙 수정, 프로젝트 git init, 커밋/업로드는 하지 않았다. Git 제외 판정과 알려진 현지 비밀 설정값의 포함 여부만 점검했다. 앱 구현·인수 상태는 변경하지 않는다.

현재 그대로 공유하기에는 제외 규칙이 부족하다. 실제로 현재 TMAP 키가 포함된 ZIP1개와 APK10개가 업로드 후보에 남는다. 키/비밀번호/DB 연결 문자열 값은 이 문서와 검사 결과에 기록하지 않았다.

## 환경과 방법

- Windows/PowerShell, 프로젝트 root와 source에서 `git rev-parse --show-toplevel` 확인: 모두 Git 저장소 아님. 로컬 추적 파일/커밋/원격 이력은 조회할 수 없다.
- root `.gitignore` 없음, `source/.gitignore` 있음.
- 프로젝트 밖 임시 bare 저장소와 `--work-tree`/`check-ignore --no-index`를 사용해 실제 `.gitignore` 규칙을 판정했다. 전역 Git 제외 규칙은 비운 상태로 확인했다. 프로젝트에는 `.git`를 만들지 않았다.
- source의 명시적으로 제외된 빌드/가상환경/IDE/cache 폴더를 순회에서 생략했다. 그 밖의710개 파일 중708개가 제외되지 않았다. 총596,482,872바이트(약569MiB)이며 검사 산출물을 만들기 전 시점의 수치다.
- 현지 local.properties와 .env.local의 알려진 설정값을 메모리에서 읽어 코드/문서 등 대상 텍스트 및 ZIP/APK11개의 local.properties/.env.local/DEX 멤버와 대조했다. 출력은 경로/키 종류/일치 여부뿐이다. 다른 미지의 비밀값·이미지 OCR·암호화/난독화된 값의 완전 탐지를 보증하지 않는다.
- [값을 제외한 검사 결과](../source/verification/gitignore-review-2026-11-21/audit.json).

## 확인 결과

정상 제외:

- source/local.properties → source/.gitignore의 local.properties 규칙.
- source/.env.local → .env.local 규칙.
- source/app/build/outputs/apk/debug/app-debug.apk → **/build/ 규칙.
- .gradle/.kotlin/.venv/.idea/pycache 등 생성물 제외 규칙 존재.

공유 전 보완 필요:

1. `night_safety_ui.zip`은 root에 있어 제외되지 않는다. 내부 `night_safety_ui/local.properties`에 현재 TMAP 키가 포함된 것을 확인했다.
2. `source/delivery/`의 APK9개와 `source/verification/fullscreen-2026-11-06/caption-preview.apk`1개가 제외되지 않는다. 모두 classes3.dex에 현재 TMAP 키가 포함된 것을 확인했다. `build/`만 제외하면 폴더 밖으로 복사한 APK는 보호하지 못한다.
3. 후보 용량의 대부분이 source/delivery 약402MB와 source/verification 약144MB다. 개별100MiB 초과 후보 파일은 없었지만 과거 배포/검증 바이너리를 소스와 함께 관리할 필요는 별도 판단해야 한다. APK·기존 전달 ZIP을 root에서 제외하는 규칙을 우선 보완해야 한다. 파일 삭제는 필요 없다.

팀 실행 관련 확인:

- 서버 engine.py는 source 바깥 `night-safety-project-readiness/osm_poc_v2`를 참조한다. source 폴더만 올리면 서버 입력/PoC 모듈이 빠진다. 팀 공유는 현재 프로젝트의 상대 경로 구조를 유지해야 한다.
- source/README.md에 키를 직접 넣지 않은 local.properties 설정 예시가 이미 있다. 팀원은 제외된 설정을 각자 구성해야 한다.
- source/app/libs의 SDK2개는 빌드 의존성이며 현재 포함 대상이다. 해당 README는 TMAP 이용/배포 조건 적용을 명시한다. SDK/공공데이터 재배포 허용 여부는 이번 gitignore 점검에서 검증하지 않았다.

## 근거와 미검증 범위

[Git gitignore 공식 문서](https://git-scm.com/docs/gitignore)는 이미 추적 중인 파일에는 제외 규칙이 적용되지 않음을 설명한다. 추후 기존 GitHub 저장소와 연결한다면 그 이력은 별도 확인해야 한다. [GitHub 대용량 파일 안내](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)는 일반 Git의100MiB 초과 파일 제한을 설명한다. 이번 검사 후보에는 이를 초과하는 개별 파일이 없었다.

외부 저장소/과거 업로드 이력·전반적인 자격 증명 탐지·SDK/데이터 재배포 조건은 미검증. 코드 변경이 없어 앱 빌드·DB/API 검사는 실행하지 않았다. .gitignore 보완과 업로드는 아직 하지 않았다.

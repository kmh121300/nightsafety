# 보안등 UI 범위 검사

작성일: 2026-11-03 · 최종 수정일: 2026-11-03 · 시간 기준: Asia/Seoul

검사 시각: 2026-11-03 15:11:41

환경: Pixel_3a API35, read-only/no-snapshot/headless/SwiftShader/3072MB, emulator-5554. 명시적 로컬 파일 서버 사용, 실제 DB 검증 아님.

APK SHA256: `57d3fc82978f492e38de66a8938e469a68d81ef4b630f2a5e7ea3f9f7ffedb17`

- PASS: Security light toggle: 1381 -> 511 -> 1381
- PASS: Security-light-only list and detail retain date, scoring exclusion, shared-coordinate caveat
- PASS: Local-file API route search works with unchanged CCTV/bell scoring basis and official score unavailable

전체 UI/Room/실기기/현장 인수는 이 검사 범위가 아니다. 전체 UI 검사 실패 기록은 별도 보존한다.

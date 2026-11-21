# Android integration smoke

Created: 2026-11-05 · Last updated: 2026-11-05 · Timezone: Asia/Seoul

Verified 2026-11-05 13:21:44 (local).

APK SHA256: `1b4d9a5e19eaa43174bbb8ebc864b44f60c671952ff81d8a9713946ee6a3e6ad`

- PASS: TMAP map ready and 1381 facility records including 870 security-light records
- PASS: Default search returns three incomplete candidates and official three-type facility metrics
- PASS: Anchor place lookup and complete graph route retain physical connection caveat and three-type scores
- PASS: Weak facility segment details open and overlay toggles
- PASS: CCTV/security-light filters change 1381 to 1111/511 and restore 1381
- PASS: Room favorite survives process restart and restores offline snapshot
- PASS: Rename and preferred walking profile persist and latest requery selects profile
- PASS: Favorite deletion is reflected by refreshed list

Screenshots: `integration-tmap.png`, `integration-weak-tmap.png`.

Map tile and orange overlay appearance require visual review of the captured screenshots. No key, raw logcat, SDK URL, or TMAP REST request was collected.

# Android integration smoke

Created: 2026-11-07 · Last updated: 2026-11-07 · Timezone: Asia/Seoul

Verified 2026-11-07 00:57:23 (local).

APK SHA256: `05fb61fac4d40eeb0a6bc25f20a88cb2a558dc8af994b7896a08b892cb35549f`

- PASS: TMAP ready; 1381 source facility records; map shows selected-route 100m corridor
- PASS: Default search returns three incomplete candidates and official three-type facility metrics
- PASS: Anchor place lookup and complete graph route retain physical connection caveat and three-type scores
- PASS: Weak facility segment details open and overlay toggles
- PASS: CCTV/security-light filters change available records to 1111/511 and restore 1381; scoring counts stay independent
- PASS: Room favorite survives process restart and restores offline snapshot
- PASS: Rename and preferred walking profile persist and latest requery selects profile
- PASS: Favorite deletion is reflected by refreshed list

Screenshots: `integration-tmap.png`, `integration-weak-tmap.png`.

Map tile and orange overlay appearance require visual review of the captured screenshots. No key, raw logcat, SDK URL, or TMAP REST request was collected.

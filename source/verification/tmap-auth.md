# TMAP Android runtime verification

Created: 2026-10-16 · Last updated: 2026-10-26 (document navigation only) · Actual verification: 2026-10-16

Historical authentication/rendering evidence. For latest whole-app verification status, see [Roadmap](../../ROADMAP.md) and [2026-10-26 DB/UI checks](database-integration-2026-10-26.md). No authentication or rendering test was rerun for this documentation update.

Verified on 2026-10-16 (Asia/Seoul) with the Pixel_3a Android emulator (`emulator-5554`), a cold boot, and the debug APK built by the main task before this runtime check. Installed with `adb install -r`; launched `kr.ac.tukorea.nightsafety/.MainActivity`.

## Results

| Check | Observed result |
| --- | --- |
| SDK authentication | Initial UI: `TMAP 인증 성공 · 지도 준비 중` |
| Map readiness | UI changed to `TMAP 지도 · 파일럿 실데이터` |
| Actual map tiles | Visually confirmed labeled roads, buildings, parks, university, Jeongwang Station, and TMAP attribution; facilities and both route polylines overlay the tiles |
| Facilities | All three categories enabled: `시설 기록 511개 표시` |
| Distance-priority route | 1572m, about 21.8 minutes, dedicated walking line 0.2%; selected route is drawn thick blue |
| Walking-line-priority route | Toggling updates the UI to 1933m, about 26.8 minutes, dedicated walking line 76.4%; thick selected route switches to the alternate geometry |
| CCTV filter | Turning CCTV off changes its checked state to false and the displayed count from 511 to 241; turning it back on restores 511 |
| Final emulator state | App remains open with TMAP tiles, all three facility categories enabled, distance-priority route selected |

Screenshots:

- [TMAP map, 511 records, distance-priority route](pilot-tmap.png)
- [TMAP map, walking-line-priority route](pilot-tmap-walking.png)

One UI hierarchy dump during route redraw returned a transient null root. A later dump and screenshot succeeded after waiting. Route redraws were slow on this software-rendered emulator; no app crash or app ANR dialog was observed during these checks. This is a functional rendering/authentication check, not a latency or field-navigation measurement.

The UI continues to disclose the 12.56m unverified station-exit connection, unavailable streetlight data, uncomputed safety score, fixed experimental routes, and assumed walking speed of 1.2m/s. The two routes were exercised as existing pilot route overlays; no TMAP REST routing request was made.

The key was neither read nor printed. No raw logcat or authentication URLs were collected. Only actual app SDK initialization was used for authentication, with no standalone key probe. This runtime task changed no Android source/build configuration or `local.properties`.

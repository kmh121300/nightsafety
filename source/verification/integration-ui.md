# Android integration smoke

Created: 2026-10-16 · Last updated: 2026-10-26 (document navigation only) · Actual verification: 2026-10-16

Historical PASS for the environment below. The 2026-10-26 DB-backed full UI run did not complete; this header does not certify a new UI pass. See [latest DB/UI evidence](database-integration-2026-10-26.md) and [Roadmap](../../ROADMAP.md).

Verified 2026-10-16 15:41:00 (local).

- PASS: TMAP map ready and 511 facility records
- PASS: Default search returns three incomplete candidates and qualified historical metrics
- PASS: Anchor place lookup and complete graph route retain physical/stale-data caveats
- PASS: Weak historical segment details open and overlay toggles
- PASS: Facility filtering changes 511 to 241 and restores 511
- PASS: Room favorite survives process restart and restores offline snapshot
- PASS: Rename and preferred walking profile persist and latest requery selects profile
- PASS: Favorite deletion is reflected by refreshed list

Screenshots: `integration-tmap.png`, `integration-weak-tmap.png`.

Map tile and orange overlay appearance require visual review of the captured screenshots. No key, raw logcat, SDK URL, or TMAP REST request was collected.

Visual review: TMAP tiles, facility dots, route lines, orange historical weak-range overlay, attribution/logo, and persistent data/physical-verification caveats were inspected in screenshots.

Additional regression PASS: identical OSM graph endpoints produce0m/0.0min with null official score and no drawable line/crash. Screenshot: `integration-zero-route.png` (visually reviewed).

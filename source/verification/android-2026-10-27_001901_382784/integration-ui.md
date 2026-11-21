# Android integration smoke

Created: 2026-10-27 · Last updated: 2026-10-27 · Timezone: Asia/Seoul

Verified 2026-10-27 00:34:45 (local).

APK SHA256: `dd91a5167f6e060abb426f126c9ae74ccf6c86a2dea4c7769f706995bbda7927`

- PASS: TMAP map ready and 511 facility records
- PASS: Default search returns three incomplete candidates and qualified historical metrics
- PASS: Anchor place lookup and complete graph route retain physical/stale-data caveats
- PASS: Weak historical segment details open and overlay toggles
- PASS: Facility filtering changes 511 to 241 and restores 511
- PASS: Room favorite survives process restart and restores offline snapshot
- PASS: Rename and preferred walking profile persist and latest requery selects profile
- PASS: Favorite deletion is reflected by refreshed list

Screenshots: `integration-tmap.png`, `integration-weak-tmap.png`.

No key, raw logcat, SDK URL, or TMAP REST request was collected.

Visual review completed on 2026-10-27: TMAP tiles/attribution, facility markers, route geometry, orange historical weak ranges, and persistent stale-data/physical-verification caveats were inspected. In map crop (40,350)-(1040,1040), exact weak-overlay RGB(205,85,15) pixels changed from 2039 ON to 0 OFF, confirming the overlay was removed after the toggle.

Installed APK bytes were independently read and SHA256 matched the local APK hash above on 2026-10-27. Only emulator-5554 was connected; no physical-device GPS verification is claimed. This proves the tested eight emulator flows, not all functional-spec acceptance cases or field walking safety.

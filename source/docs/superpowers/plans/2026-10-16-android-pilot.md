# Android Pilot Implementation Plan

Created: 2026-10-16 · Last updated: 2026-10-26 (document navigation only) · Verification date: 2026-10-16

Historical task plan. Its checked tasks apply to this pilot scope and date. For current whole-project status, see [Roadmap](../../../../ROADMAP.md); this header update does not rerun the build or tests.

> **For agentic workers:** Use superpowers:executing-plans to implement this plan in this session. No parallel agent work is needed.

**Goal:** Build an installable Kotlin Android pilot showing existing CCTV/bell data and two OSM review routes.

**Architecture:** One Android module using XML/platform views. Parse bundled GeoJSON and route JSON off the UI thread. Use TMAP Vector SDK 3.7 when a local app key is configured; otherwise show an explicitly labeled offline geometry preview without background tiles.

**Tech Stack:** Kotlin, Android SDK 36, AGP 9.4.0, Gradle 9.7.1, JUnit 4, TMAP Vector SDK 3.7.

**Spec:** ../../../../md/night-safety-functional-specification-ko.md (F-01 initial map, F-05 route display, F-06 facility display only).

## Global Constraints

- Pilot: Korea Polytechnic University–Jeongwang Station, existing OSM snapshot and public CSV-derived assets.
- Keep `route_incomplete`, unverified exit connection, unavailable lamps, and uncomputed safety score visible.
- No server credentials, background location, new routing claims, or synthetic facility records.
- Local app key is optional and excluded from source control; no external project creation.

## Review Focus

- Longitude/latitude inversion: parser tests assert real pilot coordinates and reject invalid/out-of-pilot points.
- Corrupt assets: parser fails with a useful message; UI presents retry.
- Absent or rejected map key: visible state and offline preview remain available.
- Activity recreation: selected route and facility filters survive saved instance state.
- Route endpoint gap: no invented connector or complete route claim.

## Tasks

- [x] 1. Create the Gradle wrapper/module and parser tests. Confirm failure before implementing `PilotData.parse(facilitiesJson, routesJson, geometryJson)`; cover row counts, coordinate order, route metrics, missing score, corrupt data.
- [x] 2. Implement parser/model and bundle exact existing pilot facilities and route results, keeping source metadata. Run unit tests.
- [x] 3. Implement XML screen, offline preview, TMAP overlay, route selection, facility filters/details, loading/error/retry and SDK lifecycle. Use foreground location permission only on request; retain manual pilot selection when denied.
- [x] 4. Run unit tests, lint and debug build, install/run on available emulator, exercise filters/route selection/recreation and inspect crash logs. Record evidence and limitations in README.

## Execution notes

- User authorized the previously proposed Android first step with “어 다음 작업 진행 해봐”. Existing functional specification supplies the design; proceed inline within that scope.
- The folder is not an established Android/Git project; create files in the requested empty source directory.
- SDK/key authentication and physical walking verification are separate acceptance gates; a successful debug build cannot prove them.
- Verification: 5 unit tests passed, lint 0 errors/30 warnings, APK build successful. Pixel_3a/API 35 smoke test passed after cold boot. See verification/README.md.
- Review fixes: reserve a weighted share for both the map and scrolling controls; clear location loading state on timeout, completion and cancellation.

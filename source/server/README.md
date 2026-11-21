# Local public-facility walking index

작성일: 2026-10-16 · 최종 수정일: 2026-11-04 · 시간 기준: Asia/Seoul

Project status and priorities: [Roadmap](../../ROADMAP.md). On 2026-11-04 the three-type scoring implementation, append-only DB import/restore/HTTP parity and new Android basic UI passed. [Current verification](../verification/mvp-scoring-2026-11-04/verification.md). Prior records retain their original dates.

Python 3.10+. Local-file mode uses the standard library; DB mode additionally uses `server/requirements.txt`. From the source root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s server -v
.\.venv\Scripts\python.exe server/app.py
adb reverse tcp:8765 tcp:8765
```

Use `http://127.0.0.1:8765` from the emulator after `adb reverse`. Startup loads the latest committed safenight DB snapshot when DATABASE_URL is set; otherwise it prepares local graph scores. A configured but unavailable or incomplete DB fails startup; it never silently falls back. The process binds only IPv4 loopback; remote deployment is not supported. It writes no source artifacts and exposes no data modification API. Body limit is 64 KiB, concurrent connections 4, per-IP quota 60/minute, socket timeout 15s, route search budget 10s. Browser Origin requests and foreign Host headers are rejected. Coordinates, payloads and URLs are not logged. The cache retains at most 128 route objects and disappears on restart.

The service polygon is the **local pilot rectangle** `[126.719,37.334,126.751,37.359]`, not the Siheung municipal boundary. The loaded OSM snapshot includes disconnected components; no geometric crossing creates a topology join. `poc.py` is imported only for pure topology helpers; neither `run()` nor its artifact-writing analysis is called. Local-file mode and explicit import read `../night-safety-project-readiness/osm_poc_v2/raw.osm` and `app/src/main/assets/pilot-facilities.geojson`. DB runtime loads nodes/tags, directed edges, facilities, and scoring samples from safenight in one read-only repeatable-read transaction. Request-time Dijkstra runs in memory; restart the server to load a newly imported bundle.

Sources are CCTV (2026-01-20), emergency bells (2026-01-22) and security lights (2026-02-24). There is no age cutoff. Valid source types/mapping, point coordinates, coverage, IDs and score/config versions are checked. Crime-prevention CCTV and non-toilet bells retain their eligibility rules; security_lamp is included as lighting. Unknown access/operation metadata is preserved internally with the existing experimental q=0.5 and equal weights. Three ready types produce official safety_score/average_safety/weak_safety. A missing lighting file produces partial metrics and null official scores; a validated empty lighting collection is ready/zero. Malformed type/geometry is rejected instead of silently becoming zero. Smartstlamp is not required.

Scores use <=20m segments, <=5m midpoint cells weighted by actual cell length, 20/50/100m continuous distance kernel, maximum influence per type, lower 10% length with boundary-cell fractions, and 0.3 weak weight. Dedicated pedestrian percentage means OSM footway/pedestrian/steps/path geometry, not verified sidewalk coverage. ETA is distance/1.2m/s and contains no invented crossing delay. Four Dijkstra profiles use actual integrated facility risk: fast beta0, balanced beta2, safe beta8, pedestrian beta2 plus road-geometry penalty4; alpha1, gamma0, common denominator60 (omitted in Dijkstra because it cannot change ordering). The candidate pool is limited to these four profiles. `candidate_search_complete=true` means all four searches finished, not exhaustive exploration of all possible paths; timeout returns earlier candidates with false and a warning. exact geometry duplicates merge and alternatives over fast ETA+requested cap (0..600s) are removed. At most three geometries are returned. Official safe selection ranks this candidate pool by available-data final score, weak score, average, time and distance; this does not prove a globally optimal final score. Complete nonzero routes with all required sources receive final safe/balanced roles; date age does not disable them. Historical-only selection fields are no longer generated. Final length limit is10km.

Endpoints require named `{latitude,longitude}` objects in the pilot polygon. Optional `label` (string1..100) and `source` (`user_coordinate` or `osm`) are accepted as display metadata; other fields are rejected. Metadata never establishes connector evidence. A nearby OSM node within30m is a candidate anchor only. Every nonzero requested-to-anchor gap is `unverified_gap`, geometry stops at anchors, route is incomplete, and safe/balanced roles are null. Select the explicit returned anchor coordinate to obtain a route to that coordinate. Complete routes still have `physical_verification=unverified`. Identical exact graph anchors return `already_at_destination` and null metrics.

## API

All successful responses use `{schema_version:"1.0",request_id:<uuid>,status,data,warnings}`. Data includes `versions`, `source_states`, `score_basis_types`, `missing_types`, `routes`, `selected_roles`, and `candidate_search_complete`. Each route contains GeoJSON lon/lat geometry, anchors, `edge_references`, length/time, counts, segments and policy. `available_data_metrics` is `{average,weak,score}`; `available_data_score` equals its score. Segment grades remain unknown for partial data. Public segments omit internal samples, include segment_id, reason_codes and up to20 nearby_facilities IDs. weak_member_ranges contains the exact weighted lowest10% sample-cell portions with geometry, including the fraction of a boundary cell. Route `generated_profiles` records candidate generators; `roles` records actual selections. Invalid JSON is400; invalid coordinates/unknown references422; oversized body413; rate limit429; busy503. Route computation timeout without any completed candidate is504; earlier completed candidates remain partial_success with candidate_search_complete=false. Socket read timeout is408.

- `GET /health`: reports database configured/verified state and mode (`startup_snapshot` or `local_files`). Verified means the startup snapshot was read successfully, not a continuous connection or field-safety check. `/v1/config` reports the same state.
- `GET /v1/config`: versions, pilot polygon, source state and experimental configuration.
- `GET /v1/facilities?bbox=126.719,37.334,126.751,37.359`: `data.facilities` GeoJSON FeatureCollection, raw fields retained with provenance/eligibility annotations.
  This API returns1,378 CCTV/bell/security-light records. Lighting is included in scoring; police overlay objects are Android-only and excluded from scoring.
- `GET /v1/places?q=anchor`: `data.places` array of `{label,latitude,longitude,source:"osm",anchor_node_id,entrance_verified:false}`. Names search local OSM nodes; these are not TMAP REST results. `q=anchor` returns the two explicitly identified pilot graph anchors.
- `POST /v1/routes/compare`:

```json
{"region_id":"siheung","origin":{"latitude":37.34,"longitude":126.73},"destination":{"latitude":37.35,"longitude":126.74},"max_extra_time_s":600}
```

Use exact local place anchor coordinates for connected examples; illustrative arbitrary coordinates above may have no anchor within30m. Optional `profiles` is currently ignored; all four fixed profiles are always searched.

- `POST /v1/routes/evaluate`: `{"route_id":"<returned uuid>","edge_references":["<returned way:from:to>"]}`. Requires the **entire exact array**, including order, and a route still in the current server cache. Geometry, scores and anchors supplied by a client are never trusted. Re-evaluation rebuilds all metrics from server-owned edge references and anchors, then rechecks source state. Unknown/forged/expired references return422; replan via compare after restart. Evaluation returns one route with original route_id and no new role selection.

## PostgreSQL/PostGIS integration

Actual import and DB-loaded API parity were verified on 2026-10-26. PostGIS 3.3.7 is installed in `extensions`; application tables are in the existing `safenight` schema. This tool does not create projects, schemas or extensions.

From the source directory, prepare a dedicated environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r server/requirements.txt
```

Put `DATABASE_URL=<PostgreSQL URI>` in `source/.env.local` (Git ignored), or supply DATABASE_URL through the process environment, which takes precedence. URI-encode password characters. Never put DB credentials in Android configuration. Connections require TLS. The current development connection has import privileges; a deployed server should use a separate read-only role.

```powershell
# Read-only PostGIS/schema/count inspection
.\.venv\Scripts\python.exe -X utf8 server/postgis.py
# Explicit authorized development writes: tables, indexes and one immutable bundle
.\.venv\Scripts\python.exe -X utf8 server/postgis.py --apply
# Full source/DB equality, geometry validity, and Android HTTP contract check
.\.venv\Scripts\python.exe -X utf8 tools/db_smoke.py
# Runtime: startup DB snapshot; no request-time database writes
.\.venv\Scripts\python.exe -X utf8 server/app.py
```

Import creates `ns_bundle`, `ns_node`, `ns_facility`, `ns_edge`, `ns_segment`, spatial indexes and foreign keys. Row-level security is enabled on all five tables; this implementation adds no public client policy or grant. Import runs in one transaction, preserves existing versions, ignores duplicate primary keys and validates row counts before commit. Retrying the same import leaves row counts unchanged. No deletion or replacement is performed. The most recently imported bundle is selected at startup and must match the supported scoring/routing configuration. Incomplete bundles fail startup. Floating-point output precision is set explicitly for exact reconstruction of stored graph costs.

The current pilot has 27,607 nodes, 1,378 facilities (508 CCTV/bell +870 lighting), 8,208 directed edges and22,256 scoring segments. Lighting contributes to the grid, source states and versioned scores. Shared coordinates remain separate raw records with type-max score influence. The three police overlay objects remain Android-only. Source metadata is stored with the immutable DB bundle; unsupported old scoring/routing configurations cannot be used as new scores.

On 2026-11-03 the DB initially rejected connections with `ENOTFOUND tenant/user not found`. After the user reactivated the DB, the 15:29–15:31 KST append-only import and `tools/db_smoke.py --verify-import` passed: 1,378 facilities, 27,607 nodes, 8,208 directed edges and 22,256 segments; source/DB/HTTP parity, idempotence and failed-import rollback verified. Restart an existing runtime to load the new bundle. Earlier connection failures remain historical evidence. See [DB re-verification](../verification/database-security-lights-2026-11-03.md). This does not claim a new Android full-UI pass.

Evidence: [DB integration](../verification/database-integration-2026-10-26.md). Runtime remains a loopback development server. No pgRouting execution, live per-request DB routing, cloud API deployment, production performance or backup verification is claimed.

## 2026-11-04 policy implementation

New scoring_config_version=mvp-3types-20-5-k2050100-q05-equal-v1 and routing_config_version=dijkstra-3types-risk-v1. Age does not null scores. Complete nonzero anchor routes with all three sources can receive safe/balanced roles; gaps still prevent safety recommendation and zero-distance scores remain null. Android uses final roles rather than generated_profiles for preferences and merged role labels. Old saved results remain explicitly historical. [Evidence](../verification/mvp-scoring-2026-11-04/verification.md).

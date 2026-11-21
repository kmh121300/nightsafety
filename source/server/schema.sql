-- Existing development schema; PostGIS is installed in extensions.
CREATE TABLE IF NOT EXISTS safenight.ns_bundle (
  bundle_id text PRIMARY KEY, versions jsonb NOT NULL,
  source_states jsonb NOT NULL, manifest jsonb NOT NULL,
  experimental boolean NOT NULL DEFAULT true,
  imported_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS safenight.ns_node (
  bundle_id text NOT NULL REFERENCES safenight.ns_bundle, node_id bigint NOT NULL,
  location extensions.geometry(Point,4326) NOT NULL, tags jsonb NOT NULL,
  routable boolean NOT NULL, PRIMARY KEY(bundle_id,node_id)
);
CREATE TABLE IF NOT EXISTS safenight.ns_facility (
  bundle_id text NOT NULL REFERENCES safenight.ns_bundle, facility_id text NOT NULL,
  facility_type text NOT NULL, location extensions.geometry(Point,4326) NOT NULL,
  properties jsonb NOT NULL, PRIMARY KEY(bundle_id,facility_id)
);
CREATE INDEX IF NOT EXISTS ns_facility_location_gix ON safenight.ns_facility USING gist(location);
CREATE TABLE IF NOT EXISTS safenight.ns_edge (
  bundle_id text NOT NULL REFERENCES safenight.ns_bundle, edge_reference text NOT NULL,
  from_node bigint NOT NULL, to_node bigint NOT NULL, osm_way bigint NOT NULL,
  geometry extensions.geometry(LineString,4326) NOT NULL,
  distance_m double precision NOT NULL CHECK(distance_m >= 0),
  duration_s double precision NOT NULL CHECK(duration_s >= 0),
  risk_time_s double precision NOT NULL CHECK(risk_time_s >= 0),
  pedestrian boolean NOT NULL, nearby jsonb NOT NULL,
  PRIMARY KEY(bundle_id,edge_reference),
  FOREIGN KEY(bundle_id,from_node) REFERENCES safenight.ns_node,
  FOREIGN KEY(bundle_id,to_node) REFERENCES safenight.ns_node
);
CREATE INDEX IF NOT EXISTS ns_edge_geometry_gix ON safenight.ns_edge USING gist(geometry);
CREATE TABLE IF NOT EXISTS safenight.ns_segment (
  bundle_id text NOT NULL, edge_reference text NOT NULL, segment_index integer NOT NULL,
  geometry extensions.geometry(LineString,4326) NOT NULL, length_m double precision NOT NULL,
  start_fraction double precision NOT NULL, end_fraction double precision NOT NULL,
  samples jsonb NOT NULL, grade text NOT NULL DEFAULT 'unknown',
  PRIMARY KEY(bundle_id,edge_reference,segment_index),
  FOREIGN KEY(bundle_id,edge_reference) REFERENCES safenight.ns_edge
);
ALTER TABLE safenight.ns_bundle ENABLE ROW LEVEL SECURITY;
ALTER TABLE safenight.ns_node ENABLE ROW LEVEL SECURITY;
ALTER TABLE safenight.ns_facility ENABLE ROW LEVEL SECURITY;
ALTER TABLE safenight.ns_edge ENABLE ROW LEVEL SECURITY;
ALTER TABLE safenight.ns_segment ENABLE ROW LEVEL SECURITY;

"""Versioned PostGIS snapshots; HTTP requests never write to the database."""
import collections
import json
import os
import pathlib
import threading

from engine import Engine, ROOT, metrics, TYPES, SCORING_VERSION, ROUTING_VERSION

EXPECTED_CONFIG = {
    'scoring_config_version': SCORING_VERSION,
    'routing_config_version': ROUTING_VERSION,
}
TABLES = ('ns_node', 'ns_facility', 'ns_edge', 'ns_segment')


def load_environment(path=ROOT / '.env.local'):
    """Load only the server DSN; process environment takes precedence."""
    if 'DATABASE_URL' in os.environ or not path.exists():
        return
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        key, separator, value = line.strip().partition('=')
        if separator and key.strip() == 'DATABASE_URL':
            os.environ['DATABASE_URL'] = value.strip().strip('\"\'')
            return


def connect():
    import psycopg
    if not os.getenv('DATABASE_URL'):
        raise ValueError('DATABASE_URL is required')
    return psycopg.connect(os.environ['DATABASE_URL'], connect_timeout=10,
                          application_name='safenight', sslmode='require')


def validate_counts(expected, actual):
    if not expected or expected != actual:
        raise ValueError('Incomplete database bundle; import a complete snapshot first')


def bundle_id(engine):
    return ':'.join(engine.versions[key] for key in sorted(engine.versions))


def table_counts(connection, bundle):
    return {table: connection.execute(
        f'SELECT count(*) FROM safenight.{table} WHERE bundle_id=%s', (bundle,)
    ).fetchone()[0] for table in TABLES}


def hydrate(snapshot):
    """Restore the exact directed topology and precomputed scoring samples."""
    if any(snapshot['versions'].get(k) != v for k, v in EXPECTED_CONFIG.items()):
        raise ValueError('Unsupported database scoring/routing version')
    engine = Engine.__new__(Engine)
    engine.versions = snapshot['versions']
    engine.sources = snapshot.get('source_states', {kind: {'status': 'unavailable', 'source_as_of': None} for kind in TYPES})
    engine.basis = [kind for kind in TYPES if engine.sources[kind]['status'] == 'ready']
    engine.nodes = {node: ((lat, lon), tags) for node, lon, lat, tags, _ in snapshot['nodes']}
    engine.graph = {node: [] for node, _, _, _, routable in snapshot['nodes'] if routable}
    engine.features = snapshot['features']
    engine.facility_types = {f['properties']['facility_id']: f['properties']['facility_type'] for f in engine.features}
    engine.type_record_counts = collections.Counter(engine.facility_types.values())
    engine.grid = collections.defaultdict(list)
    for feature in engine.features:
        if feature['properties']['scoring_eligible']:
            lon, lat = feature['geometry']['coordinates']
            engine.grid[(int(lat*1000), int(lon*1000))].append(feature)
    engine.edges = {}
    for key, a, b, way, distance, duration, risk, pedestrian, nearby in snapshot['edges']:
        if a not in engine.graph or b not in engine.graph:
            raise ValueError('Edge endpoint missing from database graph')
        engine.graph[a].append((b, distance, way))
        engine.edges[key] = {'a': a, 'b': b, 'way': way, 'distance': distance,
                             'time': duration, 'risk_time': risk, 'pedestrian': pedestrian,
                             'nearby': set(nearby), 'samples': [], 'segments': []}
    for key, index, geometry, length, start, end, samples, grade in snapshot['segments']:
        edge = engine.edges[key]
        if index != len(edge['segments']):
            raise ValueError('Missing or unordered database scoring segment')
        local = [(sample['score'], sample['length_m']) for sample in samples]
        edge['samples'].extend(local)
        avg = metrics(local)['average'] if engine.basis else None
        edge['segments'].append({'edge_reference': key, 'start_fraction': start, 'end_fraction': end,
                                 'geometry': geometry, 'length_m': length, 'grade': grade,
                                 'partial': len(engine.basis) != len(TYPES),
                                 'safety_score': avg if len(engine.basis) == len(TYPES) else None,
                                 'available_data_score': avg,
                                 'samples': samples})
    if not engine.graph or not engine.edges or any(not e['segments'] for e in engine.edges.values()):
        raise ValueError('Database graph/scoring samples are empty')
    engine.cache = collections.OrderedDict()
    engine.lock = threading.Lock()
    engine.database = {'configured': True, 'verified': True, 'schema': 'safenight',
                       'mode': 'startup_snapshot', 'message': 'PostGIS snapshot loaded at startup; Dijkstra runs in memory'}
    return engine


def load_database_engine():
    try:
        with connect() as connection:
            connection.execute('SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY')
            # Some hosted roles default to 15-digit float output; retain exact costs.
            connection.execute('SET LOCAL extra_float_digits = 3')
            connection.execute("SET LOCAL statement_timeout = '60s'")
            row = connection.execute('SELECT bundle_id, versions, manifest, source_states FROM safenight.ns_bundle ORDER BY imported_at DESC, bundle_id DESC LIMIT 1').fetchone()
            if not row:
                raise ValueError('No database bundle')
            bundle, versions, manifest, source_states = row
            validate_counts(manifest, table_counts(connection, bundle))
            snapshot = {'versions': versions, 'source_states': source_states}
            snapshot['nodes'] = connection.execute('SELECT node_id, extensions.ST_X(location), extensions.ST_Y(location), tags, routable FROM safenight.ns_node WHERE bundle_id=%s ORDER BY node_id', (bundle,)).fetchall()
            snapshot['features'] = [{'type': 'Feature', 'geometry': geometry, 'properties': props} for geometry, props in connection.execute('SELECT extensions.ST_AsGeoJSON(location, 17)::jsonb, properties FROM safenight.ns_facility WHERE bundle_id=%s ORDER BY facility_id', (bundle,))]
            snapshot['edges'] = connection.execute('SELECT edge_reference, from_node, to_node, osm_way, distance_m, duration_s, risk_time_s, pedestrian, nearby FROM safenight.ns_edge WHERE bundle_id=%s ORDER BY edge_reference', (bundle,)).fetchall()
            snapshot['segments'] = connection.execute('SELECT edge_reference, segment_index, extensions.ST_AsGeoJSON(geometry, 17)::jsonb, length_m, start_fraction, end_fraction, samples, grade FROM safenight.ns_segment WHERE bundle_id=%s ORDER BY edge_reference, segment_index', (bundle,)).fetchall()
        return hydrate(snapshot)
    except Exception:
        raise RuntimeError('PostGIS snapshot load failed. Check connection, schema and imported bundle; credentials suppressed.') from None


def create_engine():
    load_environment()
    return load_database_engine() if os.getenv('DATABASE_URL') else Engine()


def import_engine(connection, engine):
    """One transaction, append-only versioned import; no existing bundle is overwritten."""
    connection.execute("SET LOCAL statement_timeout = '120s'")
    connection.execute((pathlib.Path(__file__).parent / 'schema.sql').read_text(encoding='utf-8'))
    bundle = bundle_id(engine)
    manifest = dict(zip(TABLES, [len(engine.nodes), len(engine.features), len(engine.edges), sum(len(e['segments']) for e in engine.edges.values())]))
    connection.execute('INSERT INTO safenight.ns_bundle (bundle_id,versions,source_states,manifest) VALUES(%s,%s::jsonb,%s::jsonb,%s::jsonb) ON CONFLICT DO NOTHING',
                       (bundle, json.dumps(engine.versions), json.dumps(engine.source_states()), json.dumps(manifest)))
    with connection.cursor() as cursor:
        cursor.executemany('INSERT INTO safenight.ns_node VALUES(%s,%s,extensions.ST_SetSRID(extensions.ST_MakePoint(%s,%s),4326),%s::jsonb,%s) ON CONFLICT DO NOTHING',
                           ((bundle, node, point[1], point[0], json.dumps(tags), node in engine.graph) for node, (point, tags) in engine.nodes.items()))
        cursor.executemany('INSERT INTO safenight.ns_facility VALUES(%s,%s,%s,extensions.ST_SetSRID(extensions.ST_GeomFromGeoJSON(%s),4326),%s::jsonb) ON CONFLICT DO NOTHING',
                           ((bundle, f['properties']['facility_id'], f['properties']['facility_type'], json.dumps(f['geometry']), json.dumps(f['properties'])) for f in engine.features))
        cursor.executemany('INSERT INTO safenight.ns_edge VALUES(%s,%s,%s,%s,%s,extensions.ST_SetSRID(extensions.ST_GeomFromGeoJSON(%s),4326),%s,%s,%s,%s,%s::jsonb) ON CONFLICT DO NOTHING',
                           ((bundle, key, e['a'], e['b'], e['way'], json.dumps({'type': 'LineString', 'coordinates': [list(reversed(engine.nodes[n][0])) for n in (e['a'], e['b'])]}), e['distance'], e['time'], e['risk_time'], e['pedestrian'], json.dumps(sorted(e['nearby']))) for key, e in engine.edges.items()))
        cursor.executemany('INSERT INTO safenight.ns_segment VALUES(%s,%s,%s,extensions.ST_SetSRID(extensions.ST_GeomFromGeoJSON(%s),4326),%s,%s,%s,%s::jsonb,%s) ON CONFLICT DO NOTHING',
                           ((bundle, key, i, json.dumps(s['geometry']), s['length_m'], s['start_fraction'], s['end_fraction'], json.dumps(s['samples']), s['grade']) for key, e in engine.edges.items() for i, s in enumerate(e['segments'])))
    actual = table_counts(connection, bundle)
    validate_counts(manifest, actual)
    return actual

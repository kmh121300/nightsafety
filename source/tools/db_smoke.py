"""DB/HTTP parity check. --verify-import also tests idempotence and rollback."""
import copy
import json
import pathlib
import sys
import threading
import urllib.request
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'server'))
from database import bundle_id, connect, create_engine, import_engine, load_environment, table_counts
from engine import Engine
from app import LocalServer


def main():
    load_environment()
    local = Engine()
    if '--verify-import' in sys.argv:
        with connect() as connection:
            before = table_counts(connection, bundle_id(local))
        with connect() as connection:
            assert import_engine(connection, local) == before, 'Repeated import changed counts'
        broken = copy.copy(local)
        broken.versions = {**local.versions, 'active_bundle_id': 'rollback-check-' + uuid.uuid4().hex}
        broken.nodes, broken.edges = {}, {}
        broken.features = [{'geometry': {'type': 'invalid'}, 'properties': {'facility_id': 'rollback-check', 'facility_type': 'cctv'}}]
        rejected = False
        try:
            with connect() as connection:
                import_engine(connection, broken)
        except Exception as error:
            if getattr(error, 'sqlstate', None) not in ('XX000', '22023'):
                raise
            rejected = True
        assert rejected, 'Invalid import unexpectedly accepted'
        with connect() as connection:
            connection.execute('SET TRANSACTION READ ONLY')
            count = connection.execute('SELECT count(*) FROM safenight.ns_bundle WHERE bundle_id=%s', (bundle_id(broken),)).fetchone()[0]
            assert count == 0, 'Failed import left a bundle behind'
            assert table_counts(connection, bundle_id(local)) == before
        print('PASS: repeated import is idempotent; invalid geometry import rolled back without changing existing bundle', flush=True)
    db = create_engine()
    assert db.database['verified'], 'Database mode required'
    assert db.versions == local.versions
    assert db.nodes == local.nodes, 'Node coordinates/tags changed'
    assert {n: sorted(edges) for n, edges in db.graph.items()} == {n: sorted(edges) for n, edges in local.graph.items()}, 'Directed topology changed'
    assert {f['properties']['facility_id']: f for f in db.features} == {f['properties']['facility_id']: f for f in local.features}
    assert db.edges == local.edges, 'Scoring samples/geometry/costs changed'
    with connect() as connection:
        connection.execute('SET TRANSACTION READ ONLY')
        for table, column in [('ns_node', 'location'), ('ns_facility', 'location'), ('ns_edge', 'geometry'), ('ns_segment', 'geometry')]:
            # Table/column names are constants above, never user input.
            invalid = connection.execute(f'SELECT count(*) FROM safenight.{table} WHERE NOT extensions.ST_IsValid({column}) OR extensions.ST_SRID({column}) != 4326').fetchone()[0]
            assert invalid == 0, 'Invalid geometry/SRID'
        rls = connection.execute("SELECT count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='safenight' AND c.relname IN ('ns_bundle','ns_node','ns_facility','ns_edge','ns_segment') AND c.relrowsecurity").fetchone()[0]
        assert rls == 5, 'RLS missing'
    server = LocalServer(('127.0.0.1', 0), db)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_port}'

    def request(path, body=None):
        raw = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(base + path, data=raw, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.load(response)

    try:
        assert request('/health')['data']['database']['verified']
        assert request('/v1/config')['data']['database']['schema'] == 'safenight'
        facilities = request('/v1/facilities')['data']['facilities']['features']
        assert len(facilities) == 1378
        assert sum(f['properties']['facility_type'] == 'security_lamp' for f in facilities) == 870
        places = request('/v1/places?q=anchor')['data']['places']
        assert len(places) >= 2
        body = {'origin': {k: places[0][k] for k in ('latitude','longitude')},
                'destination': {k: places[1][k] for k in ('latitude','longitude')}, 'max_extra_time_s': 600}
        expected = local.compare(body)['data']
        actual = request('/v1/routes/compare', body)['data']
        fields = ('geometry', 'edge_references', 'distance_m', 'duration_s', 'available_data_metrics', 'facility_counts', 'generated_profiles', 'route_status', 'safety_score', 'average_safety', 'weak_safety', 'score_status')
        assert [{k: r[k] for k in fields} for r in actual['routes']] == [{k: r[k] for k in fields} for r in expected['routes']], 'Route parity mismatch'
        assert actual['selected_roles']['safe'] is not None
        for route in actual['routes']:
            assert route['safety_score'] is not None and route['score_status'] == 'complete'
            assert abs(sum(r['end_m']-r['start_m'] for r in route['weak_member_ranges']) - route['distance_m']*.1) < 1e-6
        route = actual['routes'][0]
        evaluated = request('/v1/routes/evaluate', {'route_id': route['route_id'], 'edge_references': route['edge_references']})['data']['routes'][0]
        assert evaluated['available_data_metrics'] == route['available_data_metrics']
        zero = request('/v1/routes/compare', {'origin': body['origin'], 'destination': body['origin']})
        assert zero['status'] == 'already_at_destination'
        print(json.dumps({'result': 'PASS', 'checks': ['all nodes/tags', 'all directed edges', 'all facilities', 'all scoring samples', 'valid SRID4326 geometries', 'RLS on 5 tables', 'health/config/facilities/places HTTP', 'route parity', 'evaluate HTTP', 'weak10% length', 'three-type official scores and safety selection', 'zero-length HTTP'], 'counts': {'nodes': len(db.nodes), 'facilities': len(db.features), 'edges': len(db.edges), 'segments': sum(len(e['segments']) for e in db.edges.values())}, 'routes': len(actual['routes'])}))
    finally:
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        # Assertions contain only fixed diagnostic labels, never DSNs.
        message = str(error) if isinstance(error, AssertionError) else type(error).__name__
        raise SystemExit('DB smoke failed: ' + message) from None

import hashlib
import pathlib
import unittest
import copy
import json
import threading
import urllib.error
import urllib.request
from unittest.mock import patch
from engine import Engine, kernel, metrics, validate_coordinate
from app import LocalServer


class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine()

    def test_fixture(self):
        self.assertEqual(metrics([(90, 5), (85, 5), (35, 5), (80, 5)])['score'], 61.25)

    def test_security_lights_are_scored_with_distinct_source_state(self):
        lamps = [f for f in self.engine.features if f['properties']['facility_type'] == 'security_lamp']
        self.assertEqual(len(lamps), 870)
        self.assertEqual(len({f['properties']['facility_id'] for f in self.engine.features}), 1378)
        self.assertTrue(all(f['properties']['scoring_eligible'] for f in lamps))
        self.assertTrue(any(f['properties']['facility_type'] == 'security_lamp' for values in self.engine.grid.values() for f in values))
        states = self.engine.config()['data']['source_states']
        self.assertEqual(states['security_lamp']['source_as_of'], '2026-02-24')
        self.assertTrue(states['security_lamp']['official_scoring_eligible'])
        self.assertNotIn('smart_lamp', states)
        self.assertEqual(self.engine.config()['data']['score_basis_types'], ['cctv', 'emergency_bell', 'security_lamp'])
        server = LocalServer(('127.0.0.1', 0), self.engine)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{server.server_port}/v1/facilities') as response:
                facilities = json.load(response)['data']['facilities']['features']
            self.assertEqual(len(facilities), 1378)
            self.assertEqual(sum(f['properties']['facility_type'] == 'security_lamp' for f in facilities), 870)
        finally:
            server.shutdown()
            server.server_close()

    def test_lamps_change_precomputed_scores_without_changing_graph(self):
        read_bytes = pathlib.Path.read_bytes
        empty_lamps = json.dumps({'type': 'FeatureCollection', 'features': []}).encode()
        with patch.object(pathlib.Path, 'read_bytes', lambda path: empty_lamps if path.name == 'pilot-security-lights.geojson' else read_bytes(path)):
            baseline = Engine()
        self.assertTrue(any(e['risk_time'] != baseline.edges[key]['risk_time'] for key,e in self.engine.edges.items()))
        self.assertEqual(self.engine.graph, baseline.graph)
        self.assertEqual(baseline.source_states()['security_lamp']['status'], 'ready')
        self.assertEqual(baseline.source_states()['security_lamp']['records'], 0)
        self.assertNotEqual(self.engine.versions['facility_version'], baseline.versions['facility_version'])

    def test_kernel_continuity(self):
        for d, expected in [(20, 1), (50, .5), (100, 0)]:
            self.assertAlmostEqual(kernel(d), expected)
            self.assertAlmostEqual(kernel(d - 1e-7), kernel(d + 1e-7), places=7)

    def test_type_max_and_weighted_weak_boundary(self):
        e = Engine.__new__(Engine)
        e.basis = ['cctv', 'emergency_bell', 'security_lamp']
        f = lambda kind, id: {'geometry': {'coordinates': [126.73, 37.34]}, 'properties': {'facility_type': kind, 'facility_id': id}}
        e.grid = {(37340, 126730): [f('cctv', str(i)) for i in range(100)]}
        self.assertAlmostEqual(e.point_score((37.34, 126.73))[0], 100 * .5 / 3)
        result = metrics([(0, 1), (100, 19)])
        self.assertEqual(result['weak'], 50)

    def test_cost_risk_and_time_cap(self):
        e = copy.copy(self.engine)
        e.nodes = {1: ((37.34, 126.73), {}), 2: ((37.3401, 126.73), {}), 3: ((37.3402, 126.73), {})}
        e.graph = {1: [(3, 12, 1), (2, 24, 2)], 2: [(3, 24, 3)], 3: []}
        e.edges = {}
        for a, b, way, seconds, risk, score in [(1, 3, 1, 10, 10, 0), (1, 2, 2, 20, 0, 100), (2, 3, 3, 20, 0, 100)]:
            e.edges[f'{way}:{a}:{b}'] = {'a': a, 'b': b, 'way': way, 'distance': seconds*1.2, 'time': seconds, 'risk_time': risk,
                                       'samples': [(score, seconds*1.2)], 'segments': [], 'nearby': set(), 'pedestrian': True}
        body = {'origin': e.coordinate(1), 'destination': e.coordinate(3), 'max_extra_time_s': 0}
        capped = e.compare(body)['data']
        self.assertEqual(len(capped['routes']), 1)
        self.assertEqual(capped['routes'][0]['policy']['max_extra_time_s'], 0)
        self.assertEqual(capped['routes'][0]['policy']['algorithm'], 'Dijkstra')
        self.assertEqual(capped['routes'][0]['policy']['profiles']['safe']['beta'], 8)
        self.assertEqual(capped['routes'][0]['policy']['profiles']['pedestrian']['non_pedestrian_time_penalty_multiplier'], 4)
        route = capped['routes'][0]
        evaluated = e.evaluate({'route_id': route['route_id'], 'edge_references': route['edge_references']})['data']['routes'][0]
        self.assertEqual(evaluated['policy']['max_extra_time_s'], 0)
        body['max_extra_time_s'] = 600
        result = e.compare(body)['data']
        self.assertIsNotNone(result['selected_roles']['safe'])
        selected = next(r for r in result['routes'] if r['route_id'] == result['selected_roles']['safe'])
        self.assertEqual(selected['duration_s'], 40)
        self.assertEqual(selected['available_data_score'], 100)

    def test_exhausted_disconnected_search_and_zero_route(self):
        e = copy.copy(self.engine)
        e.nodes = {1: ((37.34, 126.73), {}), 2: ((37.341, 126.73), {})}
        e.graph = {1: [], 2: []}
        e.edges = {}
        result = e.compare({'origin': e.coordinate(1), 'destination': e.coordinate(2)})
        self.assertEqual(result['status'], 'no_route')
        self.assertTrue(result['data']['candidate_search_complete'])
        self.assertEqual(result['data']['routes'], [])
        result = e.compare({'origin': e.coordinate(1), 'destination': e.coordinate(1)})
        self.assertEqual(result['status'], 'already_at_destination')
        route = result['data']['routes'][0]
        self.assertIsNone(route['geometry'])
        self.assertEqual(route['segments'], [])
        self.assertEqual(route['distance_m'], 0)
        self.assertEqual(route['duration_s'], 0)
        self.assertIsNone(route['available_data_score'])

    def test_http_contract_and_payload_boundary(self):
        server = LocalServer(('127.0.0.1', 0), self.engine)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = 'http://127.0.0.1:' + str(server.server_port)
        try:
            with urllib.request.urlopen(base + '/v1/config') as response:
                self.assertEqual(json.load(response)['data']['versions'], self.engine.versions)
            with urllib.request.urlopen(base + '/v1/places?q=anchor') as response:
                places = json.load(response)['data']['places']
                self.assertTrue(places)
                self.assertEqual(places[0]['source'], 'osm')
            a = next(n for n in self.engine.graph if self.engine.graph[n])
            b = self.engine.graph[a][0][0]
            body = json.dumps({'origin': self.engine.coordinate(a), 'destination': self.engine.coordinate(b)}).encode()
            request = urllib.request.Request(base + '/v1/routes/compare', data=body, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request) as response:
                data = json.load(response)['data']
                self.assertTrue(data['candidate_search_complete'])
                self.assertTrue(data['routes'])
                self.assertNotIn('samples', data['routes'][0]['segments'][0])
                self.assertIsNotNone(data['selected_roles']['safe'])
            named_origin = {**self.engine.coordinate(a), 'label': '출발 보행 지점', 'source': 'osm'}
            named_origin['latitude'] += .000001
            named_destination = {**self.engine.coordinate(b), 'label': '목적 보행 지점', 'source': 'user_coordinate'}
            named_body = {'origin': named_origin, 'destination': named_destination}
            request = urllib.request.Request(base + '/v1/routes/compare', data=json.dumps(named_body).encode(), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request) as response:
                route = json.load(response)['data']['routes'][0]
                self.assertEqual(route['route_status'], 'incomplete')
                self.assertEqual(route['origin_anchor']['connector_status'], 'unverified_gap')
            named_origin['source'] = 'verified'
            with self.assertRaises(ValueError):
                validate_coordinate(named_origin)
            for raw, status in [(b'{', 400), (b'{}', 422), (b'x'*65537, 413)]:
                request = urllib.request.Request(base + '/v1/routes/compare', data=raw, headers={'Content-Type': 'application/json'})
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(request)
                self.assertEqual(error.exception.code, status)
        finally:
            server.shutdown()
            server.server_close()

    def test_timeout_returns_completed_candidates(self):
        e = copy.copy(self.engine)
        a = next(n for n in e.graph if e.graph[n])
        b = e.graph[a][0][0]
        original = e.shortest
        calls = []
        def limited(s, t, role, deadline):
            calls.append(role)
            if len(calls) > 1:
                raise TimeoutError()
            return original(s, t, role, deadline)
        e.shortest = limited
        result = e.compare({'origin': e.coordinate(a), 'destination': e.coordinate(b)})
        self.assertEqual(result['status'], 'partial_success')
        self.assertFalse(result['data']['candidate_search_complete'])
        self.assertTrue(result['data']['routes'])

    def test_timeout_without_candidate_is_http_504(self):
        e = copy.copy(self.engine)
        def timed_out(*args):
            raise TimeoutError('No completed candidate')
        e.shortest = timed_out
        a = next(n for n in e.graph if e.graph[n])
        b = e.graph[a][0][0]
        body = {'origin': e.coordinate(a), 'destination': e.coordinate(b)}
        with self.assertRaises(TimeoutError):
            e.compare(body)
        server = LocalServer(('127.0.0.1', 0), e)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            request = urllib.request.Request('http://127.0.0.1:' + str(server.server_port) + '/v1/routes/compare',
                                             data=json.dumps(body).encode(), headers={'Content-Type': 'application/json'})
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            self.assertEqual(error.exception.code, 504)
        finally:
            server.shutdown()
            server.server_close()

    def test_invalid_inputs(self):
        for value in [None, {}, {'latitude': True, 'longitude': 126.73}, {'latitude': float('nan'), 'longitude': 126.73}, {'latitude': 126.73, 'longitude': 37.34}]:
            with self.assertRaises(ValueError):
                validate_coordinate(value)
        for metadata in [{'label': ''}, {'label': 'x'*101}, {'label': 1}, {'source': 'verified'}, {'connector_status': 'on_graph'}]:
            with self.assertRaises(ValueError):
                validate_coordinate({'latitude': 37.34, 'longitude': 126.73, **metadata})

    def test_dynamic_route_and_no_mutation(self):
        e = self.engine
        before = hashlib.sha256(e.raw_path.read_bytes()).hexdigest()
        a = next(n for n in e.graph if n != 9799703999 and e.graph[n])
        b = e.graph[a][0][0]
        result = e.compare({'origin': e.coordinate(a), 'destination': e.coordinate(b), 'max_extra_time_s': 0})
        self.assertTrue(result['data']['routes'])
        routes = result['data']['routes']
        self.assertEqual(len({str(r['geometry']) for r in routes}), len(routes))
        self.assertTrue(all(r['duration_s'] <= routes[0]['duration_s'] + 1e-6 for r in routes))
        self.assertTrue(all(r['safety_score'] is not None and r['score_status'] == 'complete' for r in routes))
        self.assertEqual(result['data']['missing_types'], [])
        for route in routes:
            self.assertAlmostEqual(sum(r['end_m']-r['start_m'] for r in route['weak_member_ranges']), route['distance_m']*.1)
            self.assertNotIn('samples', route['segments'][0])
        self.assertEqual(before, hashlib.sha256(e.raw_path.read_bytes()).hexdigest())
        route = routes[0]
        self.assertEqual(e.evaluate({'route_id': route['route_id'], 'edge_references': route['edge_references']})['data']['routes'][0]['route_id'], route['route_id'])
        with self.assertRaises(ValueError):
            e.evaluate({'route_id': route['route_id'], 'edge_references': ['forged']})

    def test_gap_not_recommended(self):
        e = self.engine
        a = next(n for n in e.graph if e.graph[n])
        b = e.graph[a][0][0]
        origin = e.coordinate(a)
        origin['latitude'] += .000001
        result = e.compare({'origin': origin, 'destination': e.coordinate(b)})
        self.assertEqual(result['data']['routes'][0]['route_status'], 'incomplete')
        self.assertIsNone(result['data']['selected_roles']['safe'])


if __name__ == '__main__':
    unittest.main()

import copy
import datetime as dt
import unittest
import pathlib
import json
from unittest.mock import patch

from engine import Engine, TYPES, metrics


class MvpScoringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = Engine()

    def body(self, engine=None):
        e = engine or self.engine
        a = next(n for n in e.graph if e.graph[n])
        return {'origin': e.coordinate(a), 'destination': e.coordinate(e.graph[a][0][0])}

    def test_security_lights_are_a_required_scoring_type(self):
        self.assertEqual(TYPES, ['cctv', 'emergency_bell', 'security_lamp'])
        lamps = [f for f in self.engine.features if f['properties']['facility_type'] == 'security_lamp']
        self.assertEqual(len(lamps), 870)
        self.assertTrue(all(f['properties']['scoring_eligible'] for f in lamps))
        self.assertTrue(any(f['properties']['facility_type'] == 'security_lamp'
                            for group in self.engine.grid.values() for f in group))

    def test_age_does_not_block_official_scores_or_recommendations(self):
        class Future(dt.datetime):
            @classmethod
            def now(cls, tz=None):
                return cls(2035, 1, 1, tzinfo=tz)
        before = self.engine.compare(self.body())['data']
        with patch('engine.dt.datetime', Future):
            after = self.engine.compare(self.body())['data']
        self.assertEqual(after['missing_types'], [])
        for state in after['source_states'].values():
            self.assertEqual(state['status'], 'ready')
            self.assertTrue(state['official_scoring_eligible'])
            self.assertNotIn('max_snapshot_age_days', state)
        route = after['routes'][0]
        self.assertEqual(route['score_status'], 'complete')
        self.assertIsNotNone(route['safety_score'])
        self.assertEqual(route['safety_score'], before['routes'][0]['safety_score'])
        self.assertEqual(route['safety_score'], metrics(self.engine.edges[route['edge_references'][0]]['samples'])['score'])
        self.assertIsNotNone(after['selected_roles']['safe'])
        self.assertTrue(all(s['grade'] != 'unknown' and not s['partial'] for s in route['segments']))

    def test_missing_source_uses_partial_basis_and_zero_route_has_no_scores(self):
        e = copy.copy(self.engine)
        e.sources = copy.deepcopy(self.engine.sources)
        e.sources['security_lamp']['status'] = 'unavailable'
        # Rebuild is required before publishing a changed source basis.
        with self.assertRaises(ValueError):
            e.compare(self.body(e))
        body = self.body()
        body['destination'] = body['origin']
        result = self.engine.compare(body)
        self.assertEqual(result['status'], 'already_at_destination')
        route = result['data']['routes'][0]
        self.assertTrue(all(route[k] is None for k in ('safety_score', 'average_safety', 'weak_safety')))
        self.assertIsNone(result['data']['selected_roles']['safe'])

    def test_type_max_prevents_duplicate_lamps_inflating_score(self):
        e = Engine.__new__(Engine)
        e.basis = list(TYPES)
        point = (37.34, 126.73)
        lamp = {'geometry': {'coordinates': list(reversed(point))},
                'properties': {'facility_type': 'security_lamp', 'facility_id': 'lamp', 'quality_factor': .5}}
        e.grid = {(37340, 126730): [lamp]}
        single = e.point_score(point)[0]
        e.grid[(37340, 126730)] = [copy.deepcopy(lamp) for _ in range(100)]
        self.assertAlmostEqual(single, 100 * .5 / 3)
        self.assertEqual(e.point_score(point)[0], single)

    def test_unavailable_lighting_builds_partial_scores_without_claiming_zero_records(self):
        read_bytes = pathlib.Path.read_bytes
        def read(path):
            if path.name == 'pilot-security-lights.geojson':
                raise FileNotFoundError()
            return read_bytes(path)
        with patch.object(pathlib.Path, 'read_bytes', read):
            partial = Engine()
        result = partial.compare(self.body(partial))['data']
        self.assertEqual(result['missing_types'], ['security_lamp'])
        route = result['routes'][0]
        self.assertEqual(route['score_status'], 'partial')
        self.assertIsNone(route['safety_score'])
        self.assertIsNone(route['facility_counts']['security_lamp'])
        self.assertIsNotNone(route['available_data_score'])
        self.assertIsNone(result['selected_roles']['safe'])

    def test_invalid_lighting_type_or_geometry_is_not_a_ready_zero_source(self):
        read_bytes = pathlib.Path.read_bytes
        for kind, geometry in [('security_lamp', {'type': 'Point', 'coordinates': [126.73, 37.34]}),
                               ('lamp', {'type': 'Polygon', 'coordinates': []})]:
            raw = json.dumps({'type': 'FeatureCollection', 'features': [
                {'type': 'Feature', 'geometry': geometry, 'properties': {'kind': kind, 'csv_row': 1}}
            ]}).encode()
            with self.subTest(kind=kind, geometry=geometry['type']):
                with patch.object(pathlib.Path, 'read_bytes', lambda p: raw if p.name == 'pilot-security-lights.geojson' else read_bytes(p)):
                    with self.assertRaises(ValueError):
                        Engine()


if __name__ == '__main__':
    unittest.main()

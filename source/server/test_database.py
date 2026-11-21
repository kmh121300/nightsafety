import os
import pathlib
import tempfile
import unittest
from unittest.mock import patch

from engine import Engine
import database


class DatabaseTests(unittest.TestCase):
    def test_environment_file_and_existing_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / '.env.local'
            path.write_text('# local secret\nDATABASE_URL="postgresql://test"\n', encoding='utf-8')
            with patch.dict(os.environ, {}, clear=True):
                database.load_environment(path)
                self.assertEqual(os.environ['DATABASE_URL'], 'postgresql://test')
                os.environ['DATABASE_URL'] = 'external'
                database.load_environment(path)
                self.assertEqual(os.environ['DATABASE_URL'], 'external')

    def test_snapshot_preserves_directed_graph_samples_and_places(self):
        versions = dict(database.EXPECTED_CONFIG, graph_version='test', facility_version='test', active_bundle_id='test')
        nodes = [(1, 126.73, 37.34, {'name': 'test'}, True), (2, 126.7301, 37.34, {}, True), (3, 126.74, 37.35, {}, False)]
        edges = [('7:1:2', 1, 2, 7, 8.0, 8/1.2, 4.0, True, ['f1'])]
        segments = [('7:1:2', 0, {'type': 'LineString', 'coordinates': [[126.73, 37.34], [126.7301, 37.34]]}, 8.0, 0.0, 1.0, [{'score': 40, 'length_m': 8}], 'unknown')]
        snapshot = {'versions': versions, 'nodes': nodes, 'edges': edges, 'segments': segments, 'features': []}
        engine = database.hydrate(snapshot)
        self.assertEqual(engine.graph, {1: [(2, 8.0, 7)], 2: []})
        self.assertEqual(engine.nodes[3][1], {})
        self.assertEqual(engine.edges['7:1:2']['samples'], [(40, 8)])
        self.assertEqual(engine.edges['7:1:2']['nearby'], {'f1'})
        route = engine.compare({'origin': engine.coordinate(1), 'destination': engine.coordinate(2)})['data']['routes'][0]
        self.assertEqual(route['distance_m'], 8)
        self.assertIsNone(route['safety_score'])
        self.assertTrue(engine.config()['data']['database']['verified'])
        self.assertEqual(engine.config()['data']['database']['mode'], 'startup_snapshot')
        reverse = engine.compare({'origin': engine.coordinate(2), 'destination': engine.coordinate(1)})
        self.assertEqual(reverse['status'], 'no_route')
        snapshot['versions'] = {**versions, 'scoring_config_version': 'unsupported'}
        with self.assertRaises(ValueError):
            database.hydrate(snapshot)

    def test_manifest_rejects_partial_bundle(self):
        with self.assertRaises(ValueError):
            database.validate_counts({'ns_node': 2}, {'ns_node': 1})
        database.validate_counts({'ns_node': 2}, {'ns_node': 2})

    def test_configured_database_failure_does_not_fall_back(self):
        with patch.dict(os.environ, {'DATABASE_URL': 'secret'}):
            with patch.object(database, 'load_database_engine', side_effect=RuntimeError('safe error')):
                with self.assertRaises(RuntimeError):
                    database.create_engine()

    def test_connection_error_does_not_expose_credentials(self):
        with patch.object(database, 'connect', side_effect=ValueError('private-password-and-host')):
            with self.assertRaises(RuntimeError) as error:
                database.load_database_engine()
        self.assertNotIn('private-password-and-host', str(error.exception))


if __name__ == '__main__':
    unittest.main()

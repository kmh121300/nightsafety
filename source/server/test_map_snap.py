import json
import threading
import unittest
import urllib.request
import urllib.error

from engine import Engine
from app import LocalServer


class MapSnapTests(unittest.TestCase):
    def setUp(self):
        self.engine = Engine.__new__(Engine)
        self.engine.nodes = {1: ((37.34, 126.73), {}), 2: ((37.349, 126.74), {}),
                             3: ((37.35, 126.74), {})}
        self.engine.graph = {1: [(2, 100, 1)], 2: []}
        self.engine.envelope = lambda **extra: {'status': 'success', 'data': extra}
        self.point = {'latitude': 37.35, 'longitude': 126.74}

    def test_far_point_snaps_only_to_graph_without_approving_connector(self):
        with self.assertRaises(ValueError):
            self.engine.anchor(self.point)
        result = self.engine.snap(self.point)['data']
        self.assertEqual(result['place']['node_id'], 2)
        self.assertEqual(result['requested'], self.point)
        self.assertGreater(result['gap_m'], 100)
        self.assertEqual(result['connector_status'], 'unverified_gap')
        self.assertEqual(self.engine.graph, {1: [(2, 100, 1)], 2: []})
        exact = self.engine.snap(self.engine.coordinate(2))['data']
        self.assertEqual(exact['gap_m'], 0)
        self.assertEqual(exact['connector_status'], 'on_graph')

    def test_rejects_invalid_or_outside_point(self):
        for bad in [None, {}, {'latitude': True, 'longitude': 126.74},
                    {'latitude': float('nan'), 'longitude': 126.74},
                    {'latitude': 37.5, 'longitude': 127}]:
            with self.subTest(bad=bad), self.assertRaises((ValueError, TypeError)):
                self.engine.snap(bad)

    def test_http_snap_and_invalid_boundary(self):
        server = LocalServer(('127.0.0.1', 0), self.engine)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            def request(point):
                return urllib.request.Request(f'http://127.0.0.1:{server.server_port}/v1/places/snap',
                    data=json.dumps(point).encode(), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request(self.point)) as response:
                self.assertEqual(json.load(response)['data']['place']['node_id'], 2)
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request({'latitude': 0, 'longitude': 0}))
            self.assertEqual(error.exception.code, 422)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()

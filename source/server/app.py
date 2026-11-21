"""Run: python server/app.py. Loopback only; no external service writes."""
import argparse
import collections
import json
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from engine import BBOX, RouteSearchTimeout
from database import create_engine


class LocalServer(ThreadingHTTPServer):
    daemon_threads = True
    request_queue_size = 8

    def __init__(self, address, engine):
        super().__init__(address, Handler)
        self.engine = engine
        self.slots = threading.BoundedSemaphore(4)
        self.quota = collections.defaultdict(collections.deque)
        self.quota_lock = threading.Lock()

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            request.sendall(b'HTTP/1.1 503 Service Unavailable\r\nContent-Length: 0\r\nConnection: close\r\n\r\n')
            self.shutdown_request(request)
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            request.settimeout(15)
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class Handler(BaseHTTPRequestHandler):
    server_version = 'NightSafetyLocal/1.0'

    def log_message(self, *args):
        pass  # Do not log coordinates, query strings, or request payloads.

    def send_json(self, status, value):
        payload = json.dumps(value, ensure_ascii=False, allow_nan=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(payload)

    def error(self, status, message):
        value = self.server.engine.envelope()
        value['status'] = 'error'
        value['error'] = {'code': str(status), 'message': message}
        self.send_json(status, value)

    def dispatch(self, post=False):
        try:
            host = self.headers.get('Host', '').split(':')[0]
            if host not in {'localhost', '127.0.0.1'} or self.headers.get('Origin'):
                return self.error(403, 'Loopback native clients only')
            with self.server.quota_lock:
                queue = self.server.quota[self.client_address[0]]
                now = time.monotonic()
                while queue and now-queue[0] > 60:
                    queue.popleft()
                if len(queue) >= 60:
                    return self.error(429, '60 requests per minute limit')
                queue.append(now)
            url = urlsplit(self.path)
            if len(self.path) > 2048:
                return self.error(414, 'URL too long')
            engine = self.server.engine
            if post:
                if self.headers.get('Transfer-Encoding'):
                    return self.error(400, 'Chunked requests unsupported')
                if self.headers.get('Content-Type', '').split(';')[0] != 'application/json':
                    return self.error(415, 'Expected application/json')
                size = int(self.headers.get('Content-Length', '-1'))
                if not 0 < size <= 65536:
                    return self.error(413, 'Body must be 1-65536 bytes')
                raw = self.rfile.read(size)
                if len(raw) != size:
                    return self.error(400, 'Incomplete body')
                body = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON')))
                if url.path == '/v1/routes/compare':
                    result = engine.compare(body)
                elif url.path == '/v1/routes/evaluate':
                    result = engine.evaluate(body)
                elif url.path == '/v1/places/snap':
                    result = engine.snap(body)
                else:
                    return self.error(404, 'Unknown endpoint')
            elif url.path == '/health':
                result = engine.envelope(health='ready', mode='local_public_facility_index',
                                         database=engine.database)
            elif url.path == '/v1/config':
                result = engine.config()
            elif url.path == '/v1/places':
                result = engine.places(parse_qs(url.query).get('q', [''])[0])
            elif url.path == '/v1/facilities':
                bbox = [float(v) for v in parse_qs(url.query).get('bbox', [','.join(map(str, BBOX))])[0].split(',')]
                if len(bbox) != 4 or not all(__import__('math').isfinite(v) for v in bbox) or not -180 <= bbox[0] <= bbox[2] <= 180 or not -90 <= bbox[1] <= bbox[3] <= 90:
                    raise ValueError('bbox must be west,south,east,north')
                features = [f for f in engine.features if bbox[0] <= f['geometry']['coordinates'][0] <= bbox[2] and bbox[1] <= f['geometry']['coordinates'][1] <= bbox[3]]
                result = engine.envelope(facilities={'type': 'FeatureCollection', 'features': features})
            else:
                return self.error(404, 'Unknown endpoint')
            self.send_json(200, result)
        except json.JSONDecodeError:
            self.error(400, 'Malformed JSON')
        except (ValueError, TypeError, KeyError, UnicodeDecodeError):
            self.error(422, 'Invalid input, unavailable anchor, or expired/forged route references')
        except RouteSearchTimeout:
            self.error(504, 'Route search budget expired before completing a candidate')
        except socket.timeout:
            self.error(408, 'Request time budget exceeded')
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            self.error(500, 'Local processing error')

    def do_GET(self):
        self.dispatch()

    def do_POST(self):
        self.dispatch(True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    print('Preparing historical routing snapshot...', flush=True)
    try:
        engine = create_engine()
    except RuntimeError as error:
        raise SystemExit(str(error)) from None
    server = LocalServer(('127.0.0.1', args.port), engine)
    print(f'Local development server ready at http://127.0.0.1:{args.port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

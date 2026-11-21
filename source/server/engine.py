"""Versioned public-facility scoring for the local pilot. Source files are read-only."""
import collections
import copy
import datetime as dt
import hashlib
import heapq
import importlib.util
import json
import math
import pathlib
import threading
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
POC = ROOT.parent / 'night-safety-project-readiness/osm_poc_v2'
spec = importlib.util.spec_from_file_location('osm_helpers', POC / 'poc.py')
poc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(poc)
TYPES = ['cctv', 'emergency_bell', 'security_lamp']
SCORING_VERSION = 'mvp-3types-20-5-k2050100-q05-equal-v1'
ROUTING_VERSION = 'dijkstra-3types-risk-v1'


def grade(score):
    return 'unknown' if score is None else 'vulnerable' if score < 40 else 'caution' if score < 70 else 'normal'
BBOX = [126.719, 37.334, 126.751, 37.359]
PROFILES = {
    'fast': {'alpha': 1, 'beta': 0, 'gamma': 0},
    'safe': {'alpha': 1, 'beta': 8, 'gamma': 0},
    'balanced': {'alpha': 1, 'beta': 2, 'gamma': 0},
    'pedestrian': {'alpha': 1, 'beta': 2, 'gamma': 0, 'non_pedestrian_time_penalty_multiplier': 4},
}


class RouteSearchTimeout(TimeoutError):
    """No route candidate completed within the computation budget."""


def kernel(d):
    if d <= 20:
        return 1.0
    if d <= 50:
        return 1 - .5 * (d - 20) / 30
    return max(0, .5 * (100 - d) / 50)


def metrics(samples):
    total = sum(length for _, length in samples)
    if not total:
        return {'average': None, 'weak': None, 'score': None}
    average = sum(s * length for s, length in samples) / total
    remaining = total * .1
    weighted = 0
    for score, length in sorted(samples, key=lambda p: p[0]):
        taken = min(remaining, length)
        weighted += score * taken
        remaining -= taken
        if remaining <= 1e-9:
            break
    weak = weighted / (total * .1)
    return {'average': average, 'weak': weak, 'score': .7 * average + .3 * weak}


def validate_coordinate(value):
    if not isinstance(value, dict) or not {'latitude', 'longitude'} <= set(value) or set(value) - {'latitude', 'longitude', 'label', 'source'}:
        raise ValueError('Coordinate requires latitude and longitude')
    if 'label' in value and (not isinstance(value['label'], str) or not 1 <= len(value['label']) <= 100):
        raise ValueError('Optional label must contain 1-100 characters')
    if 'source' in value and value['source'] not in ('user_coordinate', 'osm'):
        raise ValueError('Unsupported coordinate source metadata')
    lat, lon = value['latitude'], value['longitude']
    if any(type(v) not in (float, int) or not math.isfinite(v) for v in (lat, lon)):
        raise ValueError('Coordinates must be finite numbers')
    if not BBOX[0] <= lon <= BBOX[2] or not BBOX[1] <= lat <= BBOX[3]:
        raise ValueError('Outside local pilot service polygon')
    return (lat, lon)


class Engine:
    def __init__(self):
        self.database = {'configured': False, 'verified': False, 'mode': 'local_files',
                         'message': 'Runtime uses local OSM and facility files'}
        self.raw_path = POC / 'raw.osm'
        raw = self.raw_path.read_bytes()
        tree = ET.fromstring(raw)
        self.nodes = {int(e.attrib['id']): ((float(e.attrib['lat']), float(e.attrib['lon'])), poc.tags(e)) for e in tree.findall('node')}
        self.ways = {int(e.attrib['id']): ([int(n.attrib['ref']) for n in e.findall('nd')], poc.tags(e)) for e in tree.findall('way')}
        self.graph, _, _ = poc.build(self.nodes, self.ways, 'inferred')
        covered = {n for n in self.graph if BBOX[0] <= self.nodes[n][0][1] <= BBOX[2] and BBOX[1] <= self.nodes[n][0][0] <= BBOX[3]}
        self.graph = {a: [(b, d, w) for b, d, w in edges if b in covered] for a, edges in self.graph.items() if a in covered}
        facility_raw = (ROOT / 'app/src/main/assets/pilot-facilities.geojson').read_bytes()
        try:
            lamp_raw = (ROOT / 'app/src/main/assets/pilot-security-lights.geojson').read_bytes()
        except FileNotFoundError:
            lamp_raw = None
        documents = [json.loads(facility_raw)] + ([json.loads(lamp_raw)] if lamp_raw is not None else [])
        if any(d.get('type') != 'FeatureCollection' or not isinstance(d.get('features'), list) for d in documents):
            raise ValueError('Invalid facility source document')
        for document, allowed in zip(documents, [{'cctv', 'bell', 'police_osm_candidate'}, {'lamp'}]):
            for feature in document['features']:
                if not isinstance(feature, dict) or feature.get('type') != 'Feature' or not isinstance(feature.get('properties'), dict) or not isinstance(feature.get('geometry'), dict):
                    raise ValueError('Invalid facility record')
                kind = feature['properties'].get('kind')
                if kind not in allowed or (kind != 'police_osm_candidate' and feature['geometry'].get('type') != 'Point'):
                    raise ValueError('Invalid facility source type or geometry')
        features = [f for d in documents for f in d['features']]
        self.sources = {kind: {'status': 'ready' if kind != 'security_lamp' or lamp_raw is not None else 'unavailable',
                               'source_as_of': None, 'collected_at': None, 'source_url': None}
                        for kind in TYPES}
        self.basis = [kind for kind in TYPES if self.sources[kind]['status'] == 'ready']
        self.features = []
        self.grid = collections.defaultdict(list)
        for f in features:
            if f['geometry']['type'] != 'Point':
                continue
            p = f['properties']
            kind = {'cctv': 'cctv', 'bell': 'emergency_bell', 'lamp': 'security_lamp'}.get(p.get('kind'))
            if not kind:
                continue
            f = copy.deepcopy(f)
            p = f['properties']
            coordinates = f['geometry']['coordinates']
            if not isinstance(coordinates, list) or len(coordinates) != 2 or any(type(v) not in (int, float) or not math.isfinite(v) for v in coordinates):
                raise ValueError('Invalid facility coordinate')
            lon, lat = coordinates
            if not BBOX[0] <= lon <= BBOX[2] or not BBOX[1] <= lat <= BBOX[3]:
                raise ValueError('Facility outside pilot coverage')
            date = p.get('data_as_of')
            if date is not None:
                dt.date.fromisoformat(date)
                old = self.sources[kind]['source_as_of']
                self.sources[kind]['source_as_of'] = min(old, date) if old else date
            self.sources[kind]['source_url'] = p.get('source_url') or self.sources[kind]['source_url']
            eligible = ('방범' in p.get('설치목적구분', '')) if kind == 'cctv' else kind == 'security_lamp' or p.get('설치장소유형') != '화장실'
            p.update(facility_id=p.get('facility_id', f"siheung:{kind}:{p['csv_row']}"), facility_type=kind, scoring_eligible=eligible,
                     exclusion_reason=None if eligible else p.get('exclusion_reason', 'non_crime_prevention_cctv_or_indoor_bell'),
                     source_status='ready', historical_experimental=False, operational_status='unknown',
                     accessibility='unknown', source_as_of=p.get('data_as_of'), collected_at=None,
                     quality_factor=.5, police_linked=p.get('경찰연계유무', 'unknown'))
            self.features.append(f)
            if eligible:
                lon, lat = f['geometry']['coordinates']
                self.grid[(int(lat * 1000), int(lon * 1000))].append(f)
        if len({f['properties']['facility_id'] for f in self.features}) != len(self.features):
            raise ValueError('Duplicate facility ID')
        self.facility_types = {f['properties']['facility_id']: f['properties']['facility_type'] for f in self.features}
        self.type_record_counts = collections.Counter(self.facility_types.values())
        self.versions = {'graph_version': 'osm-' + hashlib.sha256(raw).hexdigest()[:12],
                         'facility_version': 'pilot-' + hashlib.sha256(facility_raw + (lamp_raw or b'') + SCORING_VERSION.encode()).hexdigest()[:12],
                         'scoring_config_version': SCORING_VERSION,
                         'routing_config_version': ROUTING_VERSION, 'active_bundle_id': 'local-mvp-3types-v1'}
        self.edges = {}
        for a, adjacent in self.graph.items():
            for b, distance, way in adjacent:
                key = f'{way}:{a}:{b}'
                start, end = self.nodes[a][0], self.nodes[b][0]
                segments, samples, nearby = [], [], set()
                count = math.ceil(distance / 20)
                for i in range(count):
                    length = distance / count
                    cells = max(1, math.ceil(length / 5))
                    local = []
                    seg_nearby = set()
                    for j in range(cells):
                        fraction = (i + (j + .5) / cells) / count
                        point = tuple(x + (y-x)*fraction for x, y in zip(start, end))
                        score, ids = self.point_score(point)
                        local.append((score, length / cells))
                        nearby.update(ids)
                        seg_nearby.update(ids)
                    samples.extend(local)
                    coords = [[start[1] + (end[1]-start[1])*f, start[0] + (end[0]-start[0])*f] for f in (i/count, (i+1)/count)]
                    avg = metrics(local)['average']
                    segments.append({'edge_reference': key, 'start_fraction': i/count, 'end_fraction': (i+1)/count,
                                     'geometry': {'type': 'LineString', 'coordinates': coords}, 'length_m': length,
                                     'grade': grade(avg) if len(self.basis) == len(TYPES) else 'unknown',
                                     'partial': len(self.basis) != len(TYPES), 'safety_score': avg if len(self.basis) == len(TYPES) else None,
                                     'available_data_score': avg if self.basis else None,
                                     'samples': [{'score': s, 'length_m': l} for s, l in local],
                                     '_nearby_facilities': sorted(seg_nearby)[:20]})
                pedestrian = self.ways[way][1].get('highway') in poc.PED
                self.edges[key] = {'a': a, 'b': b, 'way': way, 'distance': distance, 'time': distance/1.2,
                                   'risk_time': sum((1-s/100)*l/1.2 for s, l in samples),
                                   'samples': samples, 'segments': segments, 'nearby': nearby, 'pedestrian': pedestrian}
        self.cache = collections.OrderedDict()
        self.lock = threading.Lock()

    def point_score(self, point):
        lat, lon = point
        influences = dict.fromkeys(self.basis, 0.0)
        nearby = set()
        base_y, base_x = int(lat*1000), int(lon*1000)
        for y in range(base_y-2, base_y+3):
            for x in range(base_x-2, base_x+3):
                for f in self.grid.get((y, x), ()):
                    coords = f['geometry']['coordinates']
                    f_lon, f_lat = coords[0], coords[1]
                    if abs(lat - f_lat) > 0.00091 or abs(lon - f_lon) > 0.00115:
                        continue
                    d = poc.hav(point, (f_lat, f_lon))
                    if d < 100:
                        p = f['properties']
                        nearby.add(p['facility_id'])
                        ftype = p['facility_type']
                        val = p.get('quality_factor', .5) * kernel(d)
                        if val > influences[ftype]:
                            influences[ftype] = val
        return (100 * sum(influences.values()) / len(self.basis) if self.basis else 0.0), nearby

    def coordinate(self, node):
        lat, lon = self.nodes[node][0]
        return {'latitude': lat, 'longitude': lon}

    def source_states(self):
        today = dt.datetime.now(dt.timezone.utc).date()
        result = {k: dict(v) for k, v in self.sources.items()}
        counts = getattr(self, 'type_record_counts', None)
        if counts is None or sum(counts.values()) != len(self.features):
            counts = collections.Counter(f['properties']['facility_type'] for f in self.features)
            self.type_record_counts = counts
        for kind, state in result.items():
            date = state.get('source_as_of')
            state.update(age_days=(today-dt.date.fromisoformat(date)).days if date else None,
                         official_scoring_eligible=state['status'] == 'ready',
                         historical_experimental=False, display_only=False,
                         records=counts[kind])
        return result

    def envelope(self, routes=None, status='success', **extra):
        return {'schema_version': '1.0', 'request_id': str(uuid.uuid4()), 'status': status,
                'data': {'versions': self.versions, 'source_states': self.source_states(),
                         'score_basis_types': self.basis, 'missing_types': [kind for kind in TYPES if kind not in self.basis], 'routes': routes or [],
                         'selected_roles': {}, 'candidate_search_complete': False, **extra},
                'warnings': []}

    def config(self):
        polygon = [[BBOX[0], BBOX[1]], [BBOX[2], BBOX[1]], [BBOX[2], BBOX[3]], [BBOX[0], BBOX[3]], [BBOX[0], BBOX[1]]]
        return self.envelope(service_area={'type': 'Polygon', 'coordinates': [polygon]}, region_id='siheung',
                             mode='local_public_facility_index', database=self.database,
                             walking_speed_mps=1.2, max_extra_time_s=600, endpoint_snap_radius_m=30,
                             required_types=TYPES, facility_weights=dict.fromkeys(TYPES, 1),
                             analysis_segment_length_m=20, sample_interval_m=5, weak_fraction=.1, weak_weight=.3)

    def public_route(self, route):
        result = dict(route)
        result['roles'] = list(route.get('roles', ()))
        if 'generated_profiles' in route:
            result['generated_profiles'] = list(route['generated_profiles'])
        cells = []
        offset = 0.0
        reason_codes = ['public_facility_proximity'] + ['missing_' + kind for kind in TYPES if kind not in self.basis]
        out_segments = []
        for index, orig_seg in enumerate(route['segments']):
            segment = dict(orig_seg)
            samples = segment.pop('samples', [])
            cached_nearby = segment.pop('_nearby_facilities', None)
            start, end = segment['geometry']['coordinates']
            seg_len = segment['length_m']
            local = 0.0
            nearby = set() if cached_nearby is None else None
            edge = self.edges.get(segment.get('edge_reference'))
            has_edge_nearby = edge is None or bool(edge.get('nearby'))
            for sample in samples:
                length = sample['length_m']
                a, b = local / seg_len, (local + length) / seg_len
                coords = [[start[0]+(end[0]-start[0])*a, start[1]+(end[1]-start[1])*a],
                          [start[0]+(end[0]-start[0])*b, start[1]+(end[1]-start[1])*b]]
                cells.append((sample['score'], offset + local, length, coords))
                if nearby is not None and has_edge_nearby:
                    midpoint = ((coords[0][1]+coords[1][1])/2, (coords[0][0]+coords[1][0])/2)
                    nearby.update(self.point_score(midpoint)[1])
                local += length
            if cached_nearby is None:
                cached_nearby = sorted(nearby)[:20]
                orig_seg['_nearby_facilities'] = cached_nearby
            offset += seg_len
            segment['segment_id'] = f"{result['route_id']}:{index}"
            segment['reason_codes'] = list(reason_codes)
            segment['nearby_facilities'] = list(cached_nearby)
            out_segments.append(segment)
        result['segments'] = out_segments
        remaining = result['distance_m'] * .1 if self.basis else 0
        ranges = []
        for score, start_m, length, coords in sorted(cells, key=lambda c: (c[0], c[1])):
            if remaining <= 1e-9:
                break
            take = min(remaining, length)
            ratio = take / length
            endpoint = [coords[0][0]+(coords[1][0]-coords[0][0])*ratio, coords[0][1]+(coords[1][1]-coords[0][1])*ratio]
            ranges.append({'start_m': start_m, 'end_m': start_m+take, 'available_data_score': score,
                           'safety_score': score if len(self.basis) == len(TYPES) else None,
                           'historical_experimental': False, 'geometry': {'type': 'LineString', 'coordinates': [coords[0], endpoint]}})
            remaining -= take
        result['weak_member_ranges'] = sorted(ranges, key=lambda r: r['start_m'])
        return result

    def snap(self, value):
        point = validate_coordinate(value)
        node = min(self.graph, key=lambda n: poc.hav(point, self.nodes[n][0]))
        gap = poc.hav(point, self.nodes[node][0])
        return self.envelope(place={**self.coordinate(node), 'node_id': node,
                                    'label': '가까운 보행 지점', 'source': 'osm'},
                             requested={'latitude': point[0], 'longitude': point[1]}, gap_m=gap,
                             connector_status='on_graph' if gap == 0 else 'unverified_gap')

    def anchor(self, value):
        point = validate_coordinate(value)
        lat, lon = point
        near = [n for n in self.graph if abs(self.nodes[n][0][0] - lat) <= 0.00035 and abs(self.nodes[n][0][1] - lon) <= 0.00045]
        candidates = near or self.graph
        node = min(candidates, key=lambda n: poc.hav(point, self.nodes[n][0]))
        gap = poc.hav(point, self.nodes[node][0])
        if gap > 30:
            raise ValueError('No mapped walking anchor within 30m; choose an explicit anchor')
        exact = point == self.nodes[node][0]
        return node, {'requested': dict(value), 'coordinate': self.coordinate(node), 'node_id': node,
                      'gap_m': gap, 'connector_status': 'on_graph' if exact else 'unverified_gap'}

    def shortest(self, origin, destination, role, deadline):
        queue = [(0, origin)]
        dist, previous = {origin: 0}, {}
        while queue:
            if time.monotonic() > deadline:
                raise TimeoutError('Route search budget exceeded')
            cost, a = heapq.heappop(queue)
            if cost != dist[a]:
                continue
            if a == destination:
                path = []
                while a != origin:
                    key = previous[a]
                    path.append(key)
                    a = self.edges[key]['a']
                return list(reversed(path))
            for b, _, way in self.graph[a]:
                key = f'{way}:{a}:{b}'
                e = self.edges[key]
                profile = PROFILES[role]
                step = profile['alpha']*e['time'] + profile['beta']*e['risk_time']
                if not e['pedestrian']:
                    step += profile.get('non_pedestrian_time_penalty_multiplier', 0)*e['time']
                new = cost + step
                if new < dist.get(b, math.inf):
                    dist[b], previous[b] = new, key
                    heapq.heappush(queue, (new, b))
        return None

    def route(self, refs, origin, destination, max_extra_time_s):
        edges = [self.edges[key] for key in refs]
        complete = all(a['connector_status'] == 'on_graph' for a in (origin, destination))
        distance = sum(e['distance'] for e in edges)
        samples = [s for e in edges for s in e['samples']]
        available = metrics(samples) if self.basis else metrics([])
        scored = len(self.basis) == len(TYPES) and distance > 0
        ids = set().union(*(e['nearby'] for e in edges)) if edges else set()
        facility_types = getattr(self, 'facility_types', None)
        if facility_types is None or len(facility_types) != len(self.features):
            facility_types = {f['properties']['facility_id']: f['properties']['facility_type'] for f in self.features}
            self.facility_types = facility_types
        id_counts = collections.Counter(facility_types[i] for i in ids if i in facility_types)
        counts = {kind: id_counts[kind] if kind in self.basis else None for kind in TYPES}
        node_ids = [origin['node_id']] + [e['b'] for e in edges]
        coords = [list(reversed(self.nodes[n][0])) for n in node_ids]
        return {'route_id': str(uuid.uuid4()), 'roles': [], 'geometry': {'type': 'LineString', 'coordinates': coords} if distance else None,
                'route_status': ('complete' if complete else 'incomplete') if distance else ('already_at_destination' if complete else 'incomplete'),
                'physical_verification': 'unverified', 'origin_anchor': origin, 'destination_anchor': destination,
                'distance_m': distance, 'duration_s': sum(e['time'] for e in edges),
                'pedestrian_percent': 100*sum(e['distance'] for e in edges if e['pedestrian'])/distance if distance else None,
                'safety_score': available['score'] if scored else None,
                'average_safety': available['average'] if scored else None, 'weak_safety': available['weak'] if scored else None,
                'available_data_score': available['score'], 'available_data_metrics': available,
                'score_status': 'complete' if scored else 'partial' if distance and self.basis else 'unavailable', 'score_basis_types': self.basis,
                'missing_types': [kind for kind in TYPES if kind not in self.basis], 'historical_experimental': False,
                'data_coverage': {'geographic_scope': 'local pilot polygon', 'source_coverage_complete': scored},
                'facility_counts': counts, 'policy': {'versions': self.versions, 'count_radius_m': 100, 'quality_factor': .5,
                                                    'basis': 'public_facility_index', 'max_extra_time_s': max_extra_time_s,
                                                    'algorithm': 'Dijkstra', 'profiles': {k: dict(v) for k, v in PROFILES.items()}, 'time_reference_s': 60},
                'edge_references': list(refs), 'segments': [s for e in edges for s in e['segments']],
                'reasons': ['Public facility proximity index'] + ([] if complete else ['Unverified endpoint gap; no safety recommendation'])}

    def compare(self, body):
        if not isinstance(body, dict) or body.get('region_id', 'siheung') != 'siheung':
            raise ValueError('Expected local siheung request object')
        if self.basis != [kind for kind in TYPES if self.sources[kind]['status'] == 'ready']:
            raise ValueError('Source basis changed; rebuild the scoring bundle')
        extra = body.get('max_extra_time_s', 600)
        if type(extra) not in (float, int) or not math.isfinite(extra) or not 0 <= extra <= 600:
            raise ValueError('max_extra_time_s must be between 0 and 600')
        s, origin = self.anchor(body.get('origin'))
        t, destination = self.anchor(body.get('destination'))
        deadline = time.monotonic()+10
        candidates = []
        search_complete = True
        for role in ['fast', 'safe', 'balanced', 'pedestrian']:
            try:
                refs = self.shortest(s, t, role, deadline)
            except TimeoutError:
                search_complete = False
                break
            if refs is None:
                continue
            route = self.route(refs, origin, destination, extra)
            if route['distance_m'] > 10000:
                continue
            if candidates and route['duration_s'] > candidates[0]['duration_s'] + extra + 1e-8:
                continue
            duplicate = next((r for r in candidates if r['geometry'] == route['geometry']), None)
            if duplicate:
                duplicate['roles'].append(role)
            else:
                route['roles'].append(role)
                candidates.append(route)
        if not candidates:
            if not search_complete:
                raise RouteSearchTimeout('Search timed out before completing any candidate')
            return self.envelope(status='no_route', candidate_search_complete=True)
        selected = {'fast': candidates[0]['route_id'], 'safe': None, 'balanced': None, 'pedestrian': None}
        selected['pedestrian'] = next((r['route_id'] for r in candidates if 'pedestrian' in r['roles']), None)
        complete = [r for r in candidates if r['route_status'] == 'complete' and r['safety_score'] is not None]
        if complete:
            ranked = sorted(complete, key=lambda r: (-r['available_data_score'], -r['available_data_metrics']['weak'], -r['available_data_metrics']['average'], r['duration_s'], r['distance_m'], str(r['edge_references'])))
            selected['safe'] = ranked[0]['route_id']
            for role in ['balanced', 'pedestrian']:
                selected[role] = next((r['route_id'] for r in candidates if role in r['roles']), None)
        keep = {v for v in selected.values() if v}
        candidates = sorted(candidates, key=lambda r: r['route_id'] not in keep)[:3]
        present = {r['route_id'] for r in candidates}
        selected = {role: value if value in present else None for role, value in selected.items()}
        for route in candidates:
            route['generated_profiles'] = route['roles']
            route['roles'] = [role for role, value in selected.items() if value == route['route_id']]
        status = 'already_at_destination' if candidates[0]['route_status'] == 'already_at_destination' else 'success' if search_complete and all(r['route_status'] == 'complete' and r['score_status'] == 'complete' for r in candidates) else 'partial_success'
        with self.lock:
            for route in candidates:
                self.cache[route['route_id']] = {
                    'route_id': route['route_id'],
                    'edge_references': list(route['edge_references']),
                    'origin_anchor': copy.deepcopy(route['origin_anchor']),
                    'destination_anchor': copy.deepcopy(route['destination_anchor']),
                    'policy': {'max_extra_time_s': route['policy']['max_extra_time_s']},
                    'roles': list(route['roles']),
                    'generated_profiles': list(route['generated_profiles']),
                }
            while len(self.cache) > 128:
                self.cache.popitem(last=False)
        result = self.envelope([self.public_route(r) for r in candidates], status, selected_roles=selected,
                               candidate_search_complete=search_complete)
        if not search_complete:
            result['warnings'].append('Search budget expired; only completed candidate searches are shown')
        return result

    def evaluate(self, body):
        if not isinstance(body, dict):
            raise ValueError('Expected object')
        with self.lock:
            entry = self.cache.get(body.get('route_id'))
            trusted = copy.deepcopy(entry) if entry else None
        if not trusted or body.get('edge_references') != trusted['edge_references']:
            raise ValueError('Unknown route or forged references; compare again after server restart/cache expiry')
        route = self.route(trusted['edge_references'], trusted['origin_anchor'], trusted['destination_anchor'], trusted['policy']['max_extra_time_s'])
        route['route_id'], route['roles'] = trusted['route_id'], trusted['roles']
        route['generated_profiles'] = trusted['generated_profiles']
        status = 'already_at_destination' if route['route_status'] == 'already_at_destination' else 'success' if route['route_status'] == 'complete' and route['score_status'] == 'complete' else 'partial_success'
        return self.envelope([self.public_route(route)], status)

    def places(self, query):
        if not query or len(query) > 100:
            raise ValueError('q must contain 1-100 characters')
        q_folded = query.casefold()
        aliases = {'tukorea': '한국공학대학교', 'gate': '정문', 'jeongwang': '정왕', 'station': '정왕역', 'hospital': '시화병원사거리', 'mart': '대부할인마트'}
        match_terms = [q_folded] + [v for k, v in aliases.items() if k in q_folded]
        results = []
        for node, (point, tags) in self.nodes.items():
            name = tags.get('name')
            if name and any(term in name.casefold() for term in match_terms):
                near = [n for n in self.graph if abs(self.nodes[n][0][0] - point[0]) <= 0.00035 and abs(self.nodes[n][0][1] - point[1]) <= 0.00045]
                cand = near or self.graph
                nearest = min(cand, key=lambda n: poc.hav(point, self.nodes[n][0]))
                if poc.hav(point, self.nodes[nearest][0]) <= 30:
                    results.append({'label': name, 'latitude': point[0], 'longitude': point[1], 'source': 'osm',
                                    'anchor_node_id': nearest, 'entrance_verified': False})
        explicit_targets = [
            (poc.START, '대학 옆문 보행 지점 (현장 미검증)'),
            (poc.DEST, '정왕역 주변 보행 지점 (출구 연결 미검증)'),
            (4841812402, '한국공학대학교 1캠퍼스 정문 (보행 지점)'),
        ]
        for ref_node, label in explicit_targets:
            if q_folded in label.casefold() or query in ('anchor', '보행') or any(term in label.casefold() for term in match_terms):
                target_node = ref_node if ref_node in self.graph else min(self.graph, key=lambda n: poc.hav(self.nodes[n][0], self.nodes[ref_node][0]))
                results.append({'label': label, **self.coordinate(target_node), 'source': 'osm', 'anchor_node_id': target_node, 'entrance_verified': False})
        return self.envelope(places=results[:30], provider='local_osm_snapshot')

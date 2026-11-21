"""Preserve source records; security lights are display-only, not smart lamps."""
import collections
import csv
import datetime as dt
import hashlib
import io
import math

SOURCE_URL = 'https://data.gg.go.kr/portal/data/service/selectServicePage.do?infId=VEY71398U2941WM4E7PV21507518&infSeq=1'
FIELDS = ['보안등위치명', '설치개수', '소재지도로명주소', '소재지지번주소', '위도', '경도', '설치연도', '설치형태', '관리기관전화번호', '관리기관명', '데이터기준일자']


def convert(raw, bbox):
    digest = hashlib.sha256(raw).hexdigest()
    reader = csv.DictReader(io.StringIO(raw.decode('cp949'), newline=''))
    if reader.fieldnames != FIELDS:
        raise ValueError('Unexpected security-light CSV schema')
    features, invalid, outside, dates = [], [], [], collections.Counter()
    total = 0
    for row_number, row in enumerate(reader, 2):
        total += 1
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f'Invalid security-light CSV width at record {row_number}')
        date = row['데이터기준일자']
        if len(date) != 8 or not date.isascii() or not date.isdigit():
            raise ValueError(f'Invalid source date at record {row_number}')
        as_of = dt.datetime.strptime(date, '%Y%m%d').date().isoformat()
        dates[as_of] += 1
        try:
            lat, lon = float(row['위도']), float(row['경도'])
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError('Invalid coordinate')
        except ValueError:
            invalid.append(row_number)
            continue
        if not (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]):
            outside.append(row_number)
            continue
        features.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
                         'properties': {**row, 'kind': 'lamp', 'csv_row': row_number,
                                        'facility_id': f'siheung:security_lamp:{digest[:12]}:{row_number}',
                                        'facility_type': 'security_lamp', 'name': '보안등 · ' + row['보안등위치명'],
                                        'data_as_of': as_of, 'source_as_of': as_of, 'source_url': SOURCE_URL,
                                        'source_sha256': digest, 'collected_at': None,
                                        'scoring_eligible': True, 'exclusion_reason': None,
                                        'operational_status': 'unknown', 'accessibility': 'unknown',
                                        'notice': '보안등 · 공공시설 기반 안전지표의 조명 자료'}})
    coordinates = collections.Counter(tuple(f['geometry']['coordinates']) for f in features)
    for feature in features:
        feature['properties']['same_coordinate_records'] = coordinates[tuple(feature['geometry']['coordinates'])]
    audit = {'source_url': SOURCE_URL, 'source_sha256': digest, 'encoding': 'cp949', 'source_rows': total,
             'source_dates': dict(dates), 'pilot_bbox': bbox, 'pilot_rows': len(features),
             'pilot_unique_coordinates': len(coordinates), 'invalid_coordinate_rows': invalid,
             'outside_pilot_rows': outside, 'duplicate_policy': 'preserve_records_with_shared_coordinate_count',
             'license': 'unverified', 'complete_municipal_coverage': 'unverified'}
    return {'type': 'FeatureCollection', 'features': features}, audit

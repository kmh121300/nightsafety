import csv
import io
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / 'server'))
from security_lights import convert

BBOX = [126.719, 37.334, 126.751, 37.359]


class SecurityLightTests(unittest.TestCase):
    def raw(self, records):
        output = io.StringIO(newline='')
        writer = csv.writer(output)
        writer.writerow(['보안등위치명', '설치개수', '소재지도로명주소', '소재지지번주소', '위도', '경도', '설치연도', '설치형태', '관리기관전화번호', '관리기관명', '데이터기준일자'])
        for name, lat, lon, date in records:
            writer.writerow([name, '1', '', '경기도 시흥시 정왕동', lat, lon, '2025', '', '', '경기도 시흥시청', date])
        return output.getvalue().encode('cp949')

    def test_preserves_shared_coordinates_and_names_but_quarantines_invalid_rows(self):
        raw = self.raw([('같은이름', '37.34', '126.73', '20260224'), ('같은이름', '37.34', '126.73', '20260224'),
                        ('누락', '', '', '20260224'), ('NaN', 'nan', '126.73', '20260224'),
                        ('범위밖', '37.4', '126.8', '20260224'), ('Infinity', '37.34', 'inf', '20260224')])
        geo, audit = convert(raw, BBOX)
        features = geo['features']
        self.assertEqual(len(features), 2)
        self.assertEqual(features[0]['geometry']['coordinates'], [126.73, 37.34])
        self.assertNotEqual(features[0]['properties']['facility_id'], features[1]['properties']['facility_id'])
        self.assertEqual(features[0]['properties']['same_coordinate_records'], 2)
        self.assertEqual(features[0]['properties']['data_as_of'], '2026-02-24')
        self.assertTrue(features[0]['properties']['scoring_eligible'])
        self.assertIsNone(features[0]['properties']['exclusion_reason'])
        self.assertNotIn('미검증', features[0]['properties']['notice'])
        self.assertEqual(features[0]['properties']['보안등위치명'], '같은이름')
        self.assertEqual(audit['invalid_coordinate_rows'], [4, 5, 7])
        self.assertEqual(audit['outside_pilot_rows'], [6])
        self.assertEqual(convert(raw, BBOX), (geo, audit))

    def test_rejects_missing_schema_or_invalid_date(self):
        with self.assertRaises(ValueError):
            convert('위도,경도\n37.34,126.73'.encode('cp949'), BBOX)
        with self.assertRaises(ValueError):
            convert(self.raw([('등', '37.34', '126.73', '20260230')]), BBOX)


if __name__ == '__main__':
    unittest.main()

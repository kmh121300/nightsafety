"""Regenerate the pilot lighting asset and coordinate quarantine audit."""
import json
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'server'))
from engine import BBOX
from security_lights import convert


def main():
    source = ROOT.parent / 'csv/보안등정보현황(제공표준).csv'
    geo, audit = convert(source.read_bytes(), BBOX)
    (ROOT / 'app/src/main/assets/pilot-security-lights.geojson').write_text(
        json.dumps(geo, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    date = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).date().isoformat()
    target = ROOT / 'verification' / ('security-lights-' + date)
    target.mkdir(parents=True, exist_ok=True)
    (target / ('audit-' + audit['source_sha256'][:12] + '.json')).write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: audit[key] for key in ('source_rows', 'pilot_rows', 'pilot_unique_coordinates')}))


if __name__ == '__main__':
    main()

"""Explicit development import; default invocation is read-only."""
import argparse
import json
from database import connect, import_engine, load_environment, table_counts
from engine import Engine


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true', help='Create safenight tables and import the local pilot in one transaction')
    args = parser.parse_args()
    load_environment()
    try:
        engine = Engine() if args.apply else None
        with connect() as connection:
            if args.apply:
                result = {'mode': 'import', 'counts': import_engine(connection, engine)}
            else:
                connection.execute('SET TRANSACTION READ ONLY')
                version = connection.execute('SELECT extensions.PostGIS_Version()').fetchone()[0]
                tables = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='safenight' AND table_name LIKE 'ns_%' ORDER BY table_name").fetchall()
                result = {'mode': 'read_only', 'schema': 'safenight', 'postgis_version': version, 'tables': [t[0] for t in tables]}
                if 'ns_bundle' in result['tables']:
                    row = connection.execute('SELECT bundle_id FROM safenight.ns_bundle ORDER BY imported_at DESC, bundle_id DESC LIMIT 1').fetchone()
                    result['counts'] = table_counts(connection, row[0]) if row else {}
        # Report success only after the transaction has committed.
        print(json.dumps(result))
    except Exception:
        raise SystemExit('PostGIS operation failed; transaction rolled back. Check connection, extensions and schema. Credentials suppressed.') from None


if __name__ == '__main__':
    main()

-- 밤길 지킴이: 사용자 Supabase SQL Editor에서 실행할 읽기전용 확인.
-- 이 파일은 작성 환경/사용자 Supabase에서 실행되지 않았음.
-- 확장 설치, 테이블 생성, 계정 생성, 키 조회를 하지 않는다.
BEGIN TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '5s';

SELECT version() AS postgres_build,
       current_setting('server_version') AS postgres_version;

SELECT name, default_version, installed_version, comment
FROM pg_available_extensions
WHERE name IN ('postgis', 'pgrouting')
ORDER BY name;

SELECT e.extname, e.extversion, n.nspname AS extension_schema
FROM pg_extension e
JOIN pg_namespace n ON n.oid = e.extnamespace
WHERE e.extname IN ('postgis', 'pgrouting')
ORDER BY e.extname;

-- 실제 제공 버전과 overload/default/result를 확인한다.
SELECT n.nspname AS function_schema, p.proname AS function_name,
       pg_get_function_identity_arguments(p.oid) AS identity_arguments,
       pg_get_function_arguments(p.oid) AS arguments_and_defaults,
       pg_get_function_result(p.oid) AS result_type
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE lower(p.proname) IN
      ('pgr_version', 'postgis_full_version', 'pgr_dijkstra', 'pgr_ksp', 'pgr_astar')
ORDER BY n.nspname, p.proname, identity_arguments;

SELECT pg_size_pretty(pg_database_size(current_database())) AS current_database_size;
ROLLBACK;

-- 아래 두 쿼리는 위 catalog 결과에서 one-to-one signature 및 schema를 확인한 뒤
-- routing_schema를 실제 schema로 바꾸고 별도 실행한다. 현재는 주석/미실행.
-- 확장이 비활성화되어 있으면 위 결과에 함수가 없다. 이 파일은 활성화하지 않는다.
-- expected: Dijkstra 1->2->4, terminal agg_cost=2; KSP 두 경로 비용 2, 4.
-- negative reverse_cost=-1 means reverse arc absent, not a safety reward.
/*
BEGIN TRANSACTION READ ONLY;
SET LOCAL statement_timeout = '5s';
SELECT * FROM routing_schema.pgr_dijkstra(
  'SELECT * FROM (VALUES
    (1::bigint,1::bigint,2::bigint,1::float8,-1::float8),
    (2,2,4,1,-1), (3,1,3,2,-1), (4,3,4,2,-1)
  ) AS e(id,source,target,cost,reverse_cost)',
  1::bigint,4::bigint,true);
SELECT * FROM routing_schema.pgr_ksp(
  'SELECT * FROM (VALUES
    (1::bigint,1::bigint,2::bigint,1::float8,-1::float8),
    (2,2,4,1,-1), (3,1,3,2,-1), (4,3,4,2,-1)
  ) AS e(id,source,target,cost,reverse_cost)',
  1::bigint,4::bigint,2::integer,true,false);
ROLLBACK;
*/

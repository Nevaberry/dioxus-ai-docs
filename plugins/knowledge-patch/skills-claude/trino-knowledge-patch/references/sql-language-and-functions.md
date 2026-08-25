# SQL Language and Functions

Use this reference when writing SQL, migrating queries, or checking semantic and
correctness changes.

## DDL, DML, views, and table versions

- `ALTER TABLE ... ADD COLUMN` accepts `FIRST`, `AFTER`, and `LAST` for Iceberg,
  MariaDB, and MySQL tables (469).
- `WITH SESSION` applies session properties to one `SELECT` (470). Inline
  properties are honored by `EXPLAIN` (475), time-travel clauses accept bound
  parameters (480), and parameters can also be bound in `WITH SESSION`, `SET
  SESSION`, and `CALL` (481).
- Materialized-view owners can be changed with `ALTER MATERIALIZED VIEW ... SET
  AUTHORIZATION`; ordinary views support `ALTER VIEW ... REFRESH` (477).
- Column defaults can be declared by `CREATE TABLE` and `ALTER TABLE ... ADD
  COLUMN` (477), then changed with `ALTER TABLE ... ALTER COLUMN ... SET DEFAULT`
  or `DROP DEFAULT` (479). The Memory connector supports all of these operations.
- Table branches can be managed and queried (477).
- `SHOW CREATE MATERIALIZED VIEW` includes `GRACE PERIOD` (479). Within that
  period, an Iceberg materialized view remains usable when a base table is
  missing or corrupt (479). Freshness checks now handle nondeterministic
  functions correctly (481).
- Delta Lake supports `FOR TIMESTAMP AS OF` (476). `VERSION AS OF` and
  `TIMESTAMP AS OF` accept query parameters (480).
- `DESCRIBE OUTPUT (<query>)` no longer requires `PREPARE`, including for queries
  with version or timestamp time travel (481).
- `INSERT`, `UPDATE`, and `MERGE` accept compatible nested character values for
  `array`, `map`, and `row` columns (482).

## Query syntax and relational operations

- Negative hexadecimal, octal, and binary literals parse correctly (469), and
  array literals are supported (473-474).
- `UNION`, `INTERSECT`, and `EXCEPT` accept `CORRESPONDING` to align columns by
  name, and `GROUP BY AUTO` groups by every non-aggregate select expression
  (475).
- Row literals can name fields inline, for example `row(1 AS a, 2 AS b)` (479).
- Joins support `NEAREST` for approximate matching (481).
- The expanded predicate syntax includes `MATCH`, `UNIQUE`, symmetric and
  asymmetric `BETWEEN`, and `IS [NOT] TRUE|FALSE|UNKNOWN`. A simple `CASE` can
  use predicates such as `<`, `BETWEEN`, and `IS NULL` directly in `WHEN` (482).
- Function calls accept named arguments (`name => value`). String functions can
  use instance syntax such as `value.length()` or static syntax such as
  `varchar::chr(65)`; `ROW::fields(value)` returns field names (482).
- `AT LOCAL` is available for temporal expressions (482).
- `PIVOT` turns distinct row values into output columns (483), and `OVERLAPS`
  tests whether two temporal periods share an instant (483).
- Very wide `SELECT` lists no longer fail (472), and table functions can return
  large pass-through columns (482).

## Types, casts, arrays, and JSON

- `array_histogram` accepts null elements (470). `cosine_distance` and
  `cosine_similarity` handle arrays containing nulls (472), and
  `cosine_distance` accepts sparse vectors (477).
- `number` is a native type (480), usable in Iceberg materialized views.
  `boolean` casts to `number`, `number` casts to and from `json`, and Python UDFs
  can use it (481). Queries, equality, grouping, and distinctness correctly
  handle `number` values containing `NaN` or exceeding supported precision
  (482).
- Decimal arithmetic uses revised precision/scale inference; set
  `deprecated.legacy-arithmetic-decimal-operators=true` only as a temporary
  compatibility measure (477).
- `char` casts to numeric, boolean, varbinary, and temporal types. Its implicit
  coercion now goes to `varchar`, strips trailing spaces, and uses `varchar`
  comparisons; `deprecated.legacy-varchar-to-char-coercion=true` restores the
  old blank-padded behavior temporarily (482).
- Rows and arrays containing null elements now support comparison, range
  predicates, ordering, `DISTINCT`, `min`, and `max` (482). Ordering and
  aggregating rows wider than 64 fields is also corrected (482).
- `json_parse`, JSON literals, and JSON reads through MongoDB, MySQL, Pinot,
  PostgreSQL, and SingleStore preserve decimals with more than 16 significant
  digits (481).
- JSON fields and elements support dotted and subscript access, typed accessor
  methods, and `j.*` expansion to a JSON array of top-level members (483).
- SQL/JSON paths add `like_regex` (482) and `datetime()` (483). `JSON_QUERY`
  rejects `OMIT QUOTES` when returning `json` (482). SQL also adds `OVERLAY`
  (482).

## Functions and geospatial behavior

- `ST_GeomFromKML` constructs geometry from KML (469), and geometry values are
  comparable (476).
- `array_first(array, predicate)` returns the first matching element (480), and
  DataSketches functions are available (480).
- Text-oriented AI functions can call supported AI services, and Python UDFs
  have a larger library set (471). SQL UDF variables can be uppercase (470) and
  can have structural defaults such as arrays (482).
- The geometry engine moved from Esri to JTS (481): WKT must follow OGC syntax;
  empty-input `ST_Union` returns an empty geometry collection, not `NULL`; and a
  point-on-line union no longer inserts intersection vertices.
- Spatial additions in 483 include `ST_Transform`, `ST_TransformXY`, three- and
  four-argument `ST_Point`, `ST_Z`, `ST_Force2D`, `ST_Force3D`,
  `ST_GeomFromEWKT`, `ST_PointOnSurface`, `ST_MakePolygon`, `ST_Multi`,
  `ST_LineMerge`, `ST_Normalize`, `ST_ReducePrecision`, `ST_VoronoiPolygons`,
  `ST_MinimumBoundingCircle`, `ST_OrientedEnvelope`, `ST_Collect`,
  `ST_MakeLine`, `ST_Polygonize`, and `geometry_collect_agg`. SRID and Z metadata
  survive supported serialization, format conversion, and operations.

## Planning, lineage, and correctness

- `EXPLAIN ANALYZE` includes split count and total split-distribution time (471)
  and executes the same plan as the analyzed query (478). `EXPLAIN` types
  `LOGICAL` and `DISTRIBUTED` are deprecated; omit the type clause (479).
- Lineage includes `UNNEST` inputs (478), `SELECT` output columns (479), and
  recursive CTE aliases (482).
- Correctness fixes cover window functions with `DISTINCT` (475), spilled
  `GROUP BY` (477), row-typed queries and row-pattern `FIRST` (478), and
  spatial joins using `ST_Contains`, `ST_Intersects`, or `ST_Distance` plus full
  coverage in `geometry_to_bing_tiles` (477).
- Scalar corrections include `localtimestamp` at precisions 3, 7, and 8;
  `date_add` values above `Integer.MAX_VALUE`; undersized `varchar(n)` casts from
  JSON, time, boolean, and interval; decimal-to-double conversion below
  precision 19; and floating-point underflow rounding (480, 482).
- The removed `prefer_streaming_operators` session property must not appear in
  current sessions (479). The old hash-generation session/configuration controls
  `optimize_hash_generation` and `optimizer.optimize-hash-generation` were
  removed earlier (470).

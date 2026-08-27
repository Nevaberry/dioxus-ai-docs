# SQL language and functions

This reference groups SQL changes by the task being expressed rather than by
release. Connector support can still limit DDL and DML capabilities.

## Query properties, preparation, and explanation

### Per-query and parameterized settings

`WITH SESSION` applies a session property to one `SELECT` (470):

```sql
WITH SESSION query_max_execution_time = '2m'
SELECT * FROM system.runtime.queries;
```

Inline session properties are honored by `EXPLAIN` (475). Parameters can be
bound in `WITH SESSION`, `SET SESSION`, and `CALL` (481):

```sql
SET SESSION query_max_execution_time = ?;
```

`DESCRIBE OUTPUT` accepts an inline query without `PREPARE`, including a query
with `VERSION AS OF` or `TIMESTAMP AS OF` (481):

```sql
DESCRIBE OUTPUT (SELECT * FROM nation);
```

`EXPLAIN ANALYZE` reports split count and total split distribution time (471).
It executes the same plan as the analyzed query (478). The `LOGICAL` and
`DISTRIBUTED` `EXPLAIN` types are deprecated; omit the type clause (479).

## Relational query syntax

### Set operations and grouping

Set operations accept `CORRESPONDING` to align columns by name, and `GROUP BY
AUTO` groups on every non-aggregated output column (475):

```sql
SELECT orderkey, totalprice FROM current_orders
UNION CORRESPONDING
SELECT orderkey, totalprice FROM archived_orders;

SELECT region, status, count(*)
FROM orders
GROUP BY AUTO;
```

Array literals are supported (batch 473-474). Queries with very large
`SELECT` expression lists no longer fail (472).

### Joins, reshaping, and predicates

- `NEAREST` joins perform approximate matching (481).
- `PIVOT` turns distinct row values into columns (483).
- `MATCH` and `UNIQUE` predicates are supported (482).
- `BETWEEN` accepts `SYMMETRIC` and `ASYMMETRIC` (482).
- `IS [NOT] TRUE`, `IS [NOT] FALSE`, and `IS [NOT] UNKNOWN` are supported
  (482).
- Simple `CASE` accepts predicates such as `<`, `BETWEEN`, and `IS NULL`
  directly in `WHEN` clauses (482).
- Two row-valued time periods can be compared with `OVERLAPS` (483):

```sql
SELECT (start_time, end_time) OVERLAPS (window_start, window_end)
FROM events;
```

Rows and arrays containing null elements support comparison and ordering in
range predicates, `ORDER BY`, `DISTINCT`, `min`, and `max` (482).

### Lineage

Column lineage includes columns used in `UNNEST` expressions (478), output
columns of `SELECT` queries (479), and correctly aliased recursive CTE columns
(482).

## DDL, defaults, and metadata

### Column placement and defaults

`ALTER TABLE ... ADD COLUMN` accepts `FIRST`, `AFTER`, and `LAST` for Iceberg
and through the MariaDB and MySQL connectors (469):

```sql
ALTER TABLE customers
ADD COLUMN middle_name varchar AFTER first_name;
```

Defaults can be declared on table creation or column addition (477), then set
or dropped with `ALTER COLUMN` (479):

```sql
CREATE TABLE orders (id bigint, status varchar DEFAULT 'pending');
ALTER TABLE orders ADD COLUMN priority integer DEFAULT 0;
ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending';
ALTER TABLE orders ALTER COLUMN status DROP DEFAULT;
```

The Memory connector supports these default operations. SPI metadata builders
also preserve defaults as described in the plugin-development reference.

### Views, materialized views, and ownership

- Change materialized-view ownership with
  `ALTER MATERIALIZED VIEW ... SET AUTHORIZATION` (477).
- Refresh a view with `ALTER VIEW ... REFRESH`; the Memory connector supports
  the operation (477).
- `SHOW CREATE MATERIALIZED VIEW` includes `GRACE PERIOD` (479).
- Freshness checks handle non-deterministic materialized-view definitions
  correctly (481).
- During an Iceberg materialized view's grace period, a missing or corrupted
  base table does not prevent queries from using the view (479).

### Branches and protected metadata

Trino can manage and query table branches (477). The `system` catalog cannot
be dropped (475). Ownership metadata is available in
`system.metadata.tables_authorization`,
`system.metadata.schemas_authorization`, and
`system.metadata.functions_authorization` (477).

## Time travel and temporal expressions

Delta Lake supports timestamp-based time travel (476):

```sql
SELECT *
FROM delta.sales.orders
FOR TIMESTAMP AS OF TIMESTAMP '2025-06-01 00:00:00 UTC';
```

`VERSION AS OF` and `TIMESTAMP AS OF` accept query parameters (480):

```sql
SELECT * FROM iceberg.sales.orders FOR VERSION AS OF ?;
```

The `AT LOCAL` operator is supported (482). `localtimestamp` is correct at
precision 3 and is available at precisions 7 and 8; `date_add` accepts values
larger than `Integer.MAX_VALUE` (480).

## JSON, variant, and structured values

### Direct JSON access

JSON fields and array elements support dotted and subscripted notation, typed
accessor methods, and `j.*` expansion to a single JSON array of top-level
members (483):

```sql
SELECT j.customer.name, j.items[0].price.decimal(18,2), j.*
FROM orders;
```

SQL/JSON paths support `like_regex` (482) and `datetime()` (483).
`JSON_QUERY` cannot use `OMIT QUOTES` when its return type is `json` (482).
SQL also supports the `OVERLAY` string function (482).

High-precision decimal content is preserved by `json_parse` and JSON literals,
including when JSON is read through MongoDB, MySQL, Pinot, PostgreSQL, and
SingleStore (481).

### Structured assignment

`INSERT`, `UPDATE`, and `MERGE` can assign compatible values to `array`, `map`,
and `row` columns that contain nested character types (482). Row literals can
name fields inline (479):

```sql
SELECT row(1 AS a, 2 AS b);
```

## Numeric and collection functions

### Number

The `number` type is available, including in Iceberg materialized views (480).
Boolean values cast to `number`, `number` casts to and from `json`, and Python
UDFs accept `number` (481):

```sql
SELECT CAST(true AS number), CAST(JSON '123.45' AS number);
```

Queries, equality, `DISTINCT`, and `GROUP BY` correctly handle `number` values
that contain `NaN` or exceed supported precision (482).

### Arrays, vectors, and sketches

- `array_first(array, predicate)` returns the first matching element (480):

  ```sql
  SELECT array_first(ARRAY[1, 2, 3], x -> x > 1);
  ```

- DataSketches functions are available (480).
- `array_histogram` accepts null elements (470).
- `cosine_distance` and `cosine_similarity` handle null-containing arrays
  correctly (472).
- `cosine_distance` accepts sparse vectors (477).

### Literals, casts, and arithmetic

- Negative hexadecimal, octal, and binary literals parse correctly (469).
- `char` casts to numeric, boolean, varbinary, and temporal types (482).
- Implicit coercion is from `char` to `varchar`, removes trailing spaces, and
  compares with `varchar` semantics. Set
  `deprecated.legacy-varchar-to-char-coercion=true` only for temporary old
  blank-padded behavior (482).
- Decimal arithmetic uses revised precision and scale inference. The temporary
  compatibility property is
  `deprecated.legacy-arithmetic-decimal-operators=true` (477).
- Decimal-to-double casts below precision 19, floating-point rounding into
  underflow, and ordering or aggregating rows wider than 64 fields are
  corrected (482).
- Casts from `json`, `time`, `boolean`, or `interval` to too-small
  `varchar(n)` values do not return silently incorrect values (480).

## Function invocation and UDFs

Function calls accept named arguments as `name => value` (482). String
functions can use instance or static method syntax, and row field names can be
retrieved as follows:

```sql
SELECT value.length();
SELECT varchar::chr(65);
SELECT ROW::fields(row_value);
```

SQL UDF variables accept upper-case names (470) and structural defaults such
as arrays (482). Python UDFs have additional library support (471) and accept
the `number` type (481).

Textual AI-task functions can apply tasks to data using OpenAI, Anthropic, or
other language models served through Ollama (471). Treat provider credentials,
network access, and function availability as deployment concerns.

## Spatial SQL

- Construct geometry from KML with `ST_GeomFromKML` (469).
- Geometry values support comparisons (476).
- PostgreSQL `point` maps to Trino `geometry` for reads and writes (482).
- Iceberg v3 supports `geometry` and `geography` (482).

The geometry implementation changed from Esri to JTS (481). WKT must be valid
OGC syntax. `ST_Union` returns an empty geometry collection rather than `NULL`
for empty input and does not add intersection vertices for point-on-line
unions.

The spatial API expands substantially in 483:

- `ST_Transform` and `ST_TransformXY` transform coordinate reference systems.
- Three- and four-argument `ST_Point`, `ST_Z`, `ST_Force2D`, `ST_Force3D`, and
  `ST_GeomFromEWKT` support SRID and Z-aware construction and conversion.
- Serialization, format conversion, and supported operations preserve SRID and
  Z metadata.
- Additional operations are `ST_PointOnSurface`, `ST_MakePolygon`, `ST_Multi`,
  `ST_LineMerge`, `ST_Normalize`, `ST_ReducePrecision`,
  `ST_VoronoiPolygons`, `ST_MinimumBoundingCircle`, `ST_OrientedEnvelope`,
  `ST_Collect`, `ST_MakeLine`, `ST_Polygonize`, and
  `geometry_collect_agg`.

Release 477 corrects spatial joins involving `ST_Contains`, `ST_Intersects`,
and `ST_Distance`, and makes `geometry_to_bing_tiles` cover the full geometry.

## Session authorization behavior

`SET SESSION AUTHORIZATION` and `RESET SESSION AUTHORIZATION` preserve active
roles (472). Impersonation checks honor role-derived access (475), and group
grants remain effective while session authorization is active (477).

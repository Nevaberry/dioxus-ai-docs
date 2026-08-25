# SQL and DataFrames

## Query correctness and compatibility fixes

- Aggregate expressions can be the left operand of an `IN` subquery without
  failing (`3.5.5`):

  ```sql
  SELECT sum(value) IN (SELECT allowed_value FROM allowed_values)
  FROM measurements;
  ```

- `Catalog.listTables` handles temporary tables even when the active session
  catalog is not `V2SessionCatalog`.
- Affected partition-pruning queries no longer fail with
  `Expected only partition pruning predicates` (`3.5.6`).
- Complete user-defined-type `catalogString` values are returned rather than
  truncated (`3.5.7`).
- Hints no longer alter the result of affected semi joins. `CUBE` no longer
  returns incorrect results in the affected aggregation path, and Spark keeps
  a required global lower aggregation.
- `ROUND` no longer returns `NULL` for low-runtime-precision decimal values
  (`3.5.8`).

## Commands, writes, and dynamic SQL

Spark SQL adds the following command capabilities in `4.0.0`:

- `DESCRIBE TABLE` can return JSON.
- `EXECUTE IMMEDIATE` executes dynamic SQL.
- One command can alter multiple columns.
- `INSERT` accepts write options, and dynamic table options use
  `WITH OPTIONS`.
- `MERGE` supports schema evolution. `DataFrameWriterV2` adds `MergeInto`, and
  PySpark adds `DataFrame.mergeInto`.

In `4.2.0`, `INSERT` adds `WITH SCHEMA EVOLUTION` for V2 append and overwrite,
including sources with fewer columns or nested fields. Replacement forms
include `INSERT INTO ... REPLACE ON/USING` and `BY NAME` with
`REPLACE WHERE`.

## Complex values and equality

- `GROUP BY` supports maps, maps nested in complex values, and calendar
  intervals (`4.0.0`).
- `parse_json` permits duplicate keys.
- Negative `array_insert` positions are one-based.
- Unlimited JSON size is restored in `4.0.1`. `from_json` and `to_json`
  correctly handle Variant values, and `VariantBuilder.appendFloat` returns
  the correct value.
- `array_distinct`, `array_union`, `array_intersect`, `array_except`, and
  `arrays_overlap` normalize `-0.0` and `NaN` under Spark equality semantics
  (`4.2.0`). `collect_set` uses the same rules.
- `reverse` accepts `BinaryType` and reverses its bytes.

## SQL UDFs, TVFs, and scripting

- Cyclic SQL UDF use is rejected, as are persistent SQL UDFs that reference
  temporary objects (`4.0.1`).
- `CREATE OR REPLACE` works for SQL table-valued functions, and SQL UDTVFs
  resolve under view-consistent configuration.
- A scripting scope cannot declare duplicate `SQLEXCEPTION` or `NOT FOUND`
  handlers. Conditions handle `NULL`; `FOR` iterator variables are quoted and
  cannot clash with enclosing labels.
- SQL scripting is GA, enabled by default, supports `CONTINUE HANDLER`, and
  allows multiple variables in one `DECLARE` (`4.1.0`).
- SQL scripting adds cursors in `4.2.0`.
- `DESCRIBE FUNCTION` understands SQL UDFs, and SQL UDF definitions can carry
  a default collation.

## Views, caching, and collations

- New views persist their creation-time ANSI setting (`4.0.1`). When an older
  view lacks that setting, Spark assumes ANSI mode during query.
- String hashes do not depend on collation. Python UDF parameters and JSON
  serialization support collated strings, and view references plus
  `ALTER COLUMN TYPE STRING` retain their intended collation.
- `CACHE TABLE` is atomic on command failure.
- Table creation no longer falls back to a Hive-incompatible path after a
  Thrift exception.
- Tables can set a schema-level collation, and views can inherit it (`4.1.0`).
- Collations extend to `CHAR`, `VARCHAR`, CTAS, and RTAS in `4.2.0`;
  `SHOW COLLATIONS` lists available choices.

## Variant, geospatial, and time types

- `VARIANT` is GA and enabled by default (`4.1.0`). CSV and XML scans support
  it, colon syntax accesses fields, Parquet writers can infer shredding schema
  and annotate the logical type, and readers recognize that annotation.
- Native `GEOMETRY` and `GEOGRAPHY` types are enabled by default in `4.2.0`.
  Spark includes `ST_*` operations, WKT/WKB and Parquet I/O, and an SRID
  registry based on PROJ 9.7.1 data. `ST_GeomFromWKB` accepts an SRID,
  `ST_AsBinary` accepts endianness, and geography values can be cast to
  geometry and returned through Hive or Thrift Server.
- Spark accepts `TIMESTAMP WITH LOCAL TIME ZONE` syntax and implicit
  string-to-`TIME` casts. JSON, XML, and CSV conversion functions understand
  `TIME`; ORC and Avro read and write it; numeric time conversions are
  available.

## Query composition

Spark `4.1.0` adds:

- recursive common table expressions;
- query parameter markers throughout queries through a pre-parser;
- DataFrame `IN` subqueries;
- observations containing complex types in PySpark; and
- direct passthrough partitioning in Dataset.

Spark `4.2.0` adds:

- SQL and DataFrame top-K `NEAREST BY` joins;
- metric views through `CREATE VIEW ... WITH METRICS`;
- `QUALIFY`;
- `TABLESAMPLE SYSTEM` block sampling with V2 and JDBC pushdown;
- aliases on `PIVOT`;
- aggregates and `GROUP BY` in pipe-operator queries;
- `|` as an alternative to `|>`; and
- `DROP TABLE` support for dropping a view.

## Aggregate, vector, sketch, and time functions

- `4.1.0` adds `approx_top_k` accumulation, estimation, and combination with
  null counting; KLL quantile sketches; Theta Sketch support;
  `BITMAP_AND_AGG`; `try_to_date`; and seeded `uuid`.
- `4.2.0` adds `time_bucket`. `array_agg`, `collect_list`, and `collect_set`
  accept explicit `IGNORE NULLS` or `RESPECT NULLS`.
- Vector expressions cover similarity, distance, norm, normalization, sum,
  and average. `MaxBy` and `MinBy` gain top-K overloads.
- Native Apache Tuple Sketches, Tuple/Theta set operations, and the
  `sketch_funcs` grouping are available.
- Window aggregate functions accept filter predicates.

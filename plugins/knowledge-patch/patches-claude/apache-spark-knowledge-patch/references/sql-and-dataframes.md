# SQL and DataFrame behavior

Use this reference when migrating SQL semantics, parser behavior, types,
expressions, views, scripting, and DataFrame query APIs.

## Default changes and compatibility settings

### ANSI mode (4.0-migration)

`spark.sql.ansi.enabled` defaults to `true`, changing invalid-operation and
overflow behavior. Set it to `false`, or set `SPARK_ANSI_SQL_MODE=false`, for
non-ANSI behavior. New views persist the ANSI value present at creation; when
an older view lacks a stored value, Spark assumes ANSI mode while querying it
(4.0.1).

### Bare table creation (4.0-migration)

`CREATE TABLE` without `USING` or `STORED AS` uses
`spark.sql.sources.default`, not Hive. Restore the old default with
`spark.sql.legacy.createHiveTableByDefault=true` or
`SPARK_SQL_LEGACY_CREATE_HIVE_TABLE=true`.

### Map keys and partition sizing (4.0-migration)

`create_map`, `map_from_arrays`, `map_from_entries`, and `map_concat` normalize
`-0.0` keys to `0.0`. Set
`spark.sql.legacy.disableMapKeyNormalization=true` to keep distinct
negative-zero keys. `spark.sql.maxSinglePartitionBytes` defaults to `128m`
instead of `Long.MaxValue`; use `9223372036854775807` for the old unlimited
value.

### Timestamp overflow and character coding (4.0-migration)

In non-ANSI mode, casting an overflowing timestamp to `byte`, `short`, or
`int` returns `NULL` instead of a wrapped value. `encode()` and `decode()` now
allow only US-ASCII, ISO-8859-1, UTF-8, UTF-16BE, UTF-16LE, UTF-16, and UTF-32.
Unmappable input raises `MALFORMED_CHARACTER_CODING` instead of inserting
replacement characters. `spark.sql.legacy.javaCharsets=true` restores JDK
charsets; `spark.sql.legacy.codingErrorAction=true` restores replacement.

### Parser policies and syntax (4.0-migration)

`spark.sql.legacy.ctePrecedencePolicy` defaults to `CORRECTED`, so an inner CTE
shadows an outer CTE. `spark.sql.legacy.timeParserPolicy` also defaults to
`CORRECTED`; failures raise `CANNOT_PARSE_TIMESTAMP` under ANSI and return
`NULL` otherwise.

Forms such as `expr ! IN (...)`, `expr ! BETWEEN ...`, and `col ! NULL` fail
parsing; use `NOT`. `spark.sql.legacy.bangEqualsNot=true` temporarily restores
the old acceptance. `spark.sql.legacy.allowZeroIndexInFormatString` is
deprecated, so `format_string` positional arguments must be one-based (`1$`,
`2$`).

### View schema compensation (4.0-migration)

Views tolerate underlying column-type changes by inserting casts instead of
allowing only up-casts. Use `spark.sql.legacy.viewSchemaCompensation=false` for
the earlier behavior. `spark.sql.legacy.viewSchemaBindingMode=false` disables
the new binding mode and removes its clause from descriptions and DDL.

### Locale-sensitive sentences (4.0-migration)

When `language` is provided but `country` is null, `sentences` uses
`Locale(language)` rather than `Locale.US`; tokenization can change.

## Correctness fixes

### Aggregates in `IN` subqueries (3.5.5)

An aggregate expression can be the left operand of an `IN` subquery:

```sql
SELECT sum(value) IN (SELECT allowed_value FROM allowed_values)
FROM measurements;
```

### JSON, Variant, and collation fixes (4.0.1)

Spark again allows unlimited JSON size. `from_json` and `to_json` handle
variant values, and `VariantBuilder.appendFloat` produces the correct result.
String hashing is collation-agnostic, Python UDFs accept collated-string
parameters, and collated strings serialize correctly through `toJson`. View
reference types with a default collation and `ALTER COLUMN TYPE STRING` on an
existing `StringType` retain the intended collation.

### UDF, TVF, and scripting validation (4.0.1)

Spark detects cyclic SQL UDF use and rejects persistent SQL UDFs that refer to
temporary objects. `CREATE OR REPLACE` works for SQL table-valued functions,
and SQL UDTVFs resolve configurations consistently with views. Scripts reject
duplicate `SQLEXCEPTION` or `NOT FOUND` handlers in one scope, handle `NULL`
conditions correctly, quote `FOR` iterator variables, and prevent iterator
names from clashing with enclosing labels.

### Atomic cache operations (4.0.1)

`CACHE TABLE` is atomic on execution failure, avoiding partial cache state.

### Join and aggregation fixes (3.5.7)

A hint no longer changes the result of an affected semi join. Affected `CUBE`
queries return correct results, and a required global lower aggregation is no
longer removed.

### Decimal rounding (3.5.8)

`ROUND` no longer returns `NULL` for a decimal value whose runtime precision is
low.

### Empty grouping sets (4.2-migration)

`GROUP BY GROUPING SETS (())`, empty `CUBE()`, and empty `ROLLUP()` behave like
aggregation without `GROUP BY`, returning one grand-total row over empty input.
Set `spark.sql.analyzer.lowerEmptyGroupingSetToGlobalAggregate.enabled=false`
for the previous zero-row result.

## Namespaces and resolution

### Virtual system catalog (4.2-migration)

`system.builtin` exposes built-in and extension-injected functions.
`system.session` exposes temporary views, temporary functions, and session
variables. Two-part `builtin.*` and `session.*` references try those system
namespaces before the current catalog. To reach a conflicting persistent
object, use an explicit catalog such as `spark_catalog.session.x`, or set
`spark.sql.legacy.persistentCatalogFirst=true`.

Temporary view and function `CREATE` and `DROP` accept `session` and
`system.session` qualifiers, including the pattern
`CREATE TEMPORARY VIEW system.session.v AS ...`, for example:

```sql
CREATE TEMPORARY VIEW system.session.v AS SELECT 1;
```

Other qualifiers fail with `INVALID_TEMP_OBJ_QUALIFIER`.

### SQL path resolution (4.2-migration)

`SET PATH`, `current_path()`, and path-based resolution apply to unqualified
routines, tables, views, and session variables. Enable them with
`spark.sql.path.enabled=true`; optionally set `spark.sql.defaultPath`. When the
feature is disabled, `SET PATH` fails with
`UNSUPPORTED_FEATURE.SET_PATH_WHEN_DISABLED`.

### Ambiguous identifiers (4.2-migration)

Duplicate names in one `WITH` clause are rejected at parse time with
`DUPLICATED_CTE_NAMES`, even if they differ only by case and regardless of
`spark.sql.caseSensitive`. By contrast, `NATURAL JOIN` honors
`spark.sql.caseSensitive` when finding common columns.

In a SQL UDF body, bare `current_user`, `current_date`, `current_time`,
`current_timestamp`, `user`, `session_user`, and `grouping__id` resolve to the
parameterless built-in rather than an identically named parameter. Rename the
parameter or use
`spark.sql.legacy.allowUdfParameterToShadowParameterlessFunction=true`.

An unquoted name in `SET CATALOG name` resolves as a session variable first,
using its value as the catalog. It is a literal only if no variable exists.
Write `SET CATALOG 'name'` to force literal interpretation.

## SQL and DataFrame capabilities

### Commands and schema-aware writes (4.0.0)

`DESCRIBE TABLE` can return JSON, `EXECUTE IMMEDIATE` supports dynamic SQL, one
command can alter multiple columns, and `INSERT` accepts write options. Dynamic
table options use `WITH OPTIONS`.

SQL `MERGE` can enable schema evolution. `DataFrameWriterV2` has `MergeInto`,
and PySpark has `DataFrame.mergeInto`, allowing schema-aware merges without
connector-specific commands.

### Complex values (4.0.0)

`GROUP BY` supports `MapType`, including maps nested in complex values, and
calendar intervals. `parse_json` permits duplicate keys. Negative positions in
`array_insert` are one-based.

### SQL scripting and query grammar (4.1.0)

SQL scripting is GA and enabled by default. It adds `CONTINUE HANDLER` and
allows multiple variables in one `DECLARE`. Spark SQL supports recursive CTEs,
and query parameter markers are accepted throughout queries through a
pre-parser.

### Variant and collations (4.1.0)

`VARIANT` is GA and enabled by default. CSV and XML scans support it, colon
syntax accesses fields, and Parquet writers can infer a shredding schema and
annotate the Variant logical type for readers. Tables can define a schema-level
collation, and views can inherit the schema default.

### Sketches, aggregates, and built-ins (4.1.0)

Spark adds `approx_top_k` accumulate, estimate, and combine operations; it also
counts nulls. KLL quantile sketches, Theta Sketch functions,
`BITMAP_AND_AGG`, `try_to_date`, and seeded `uuid` are available.

### DataFrame coverage and encoders (4.1.0)

The DataFrame API supports `IN` subqueries. PySpark observations accept complex
types. Dataset supports direct passthrough partitioning. Scala adds
`Encoders.udtAPI`, and `TransformingEncoder` supports primitive types.

### Geospatial and ranking queries (4.2.0)

Enabled-by-default `GEOMETRY` and `GEOGRAPHY` types include `ST_*` functions,
WKT/WKB and Parquet I/O, and an SRID registry based on PROJ 9.7.1 data.
`ST_GeomFromWKB` takes an optional SRID, `ST_AsBinary` takes optional
endianness, and geography can be cast to geometry and returned through Hive or
Thrift Server.

SQL and DataFrame APIs support top-K `NEAREST BY` joins. Metric views provide
declarative semantic models through `CREATE VIEW ... WITH METRICS`.

### Query syntax expansion (4.2.0)

Spark SQL adds `QUALIFY`, `TABLESAMPLE SYSTEM` block sampling with Data Source
V2 and JDBC pushdown, aliases on `PIVOT`, and aggregates plus `GROUP BY` in
pipe-operator queries. A single `|` can replace `|>`. `DROP TABLE` can also
drop a view.

### Time, collation, and inspection (4.2.0)

Spark accepts `TIMESTAMP WITH LOCAL TIME ZONE` syntax and implicit string casts
to `TIME`. JSON, XML, and CSV `from_*`/`to_*` functions understand `TIME`; ORC
and Avro read and write it, and numeric time-conversion functions are
available.

Collations apply to `CHAR`, `VARCHAR`, CTAS, and RTAS. `SHOW COLLATIONS` lists
them. SQL scripting adds cursors. `DESCRIBE FUNCTION` supports SQL UDFs, whose
definitions can specify a default collation.

### Aggregate, vector, and sketch functions (4.2.0)

`time_bucket` is available. `array_agg`, `collect_list`, and `collect_set`
accept `IGNORE NULLS` or `RESPECT NULLS`. Vector expressions cover similarity,
distance, norm, normalization, sum, and average aggregation. `MaxBy` and
`MinBy` have top-K overloads. Native Apache Tuple Sketches, Tuple/Theta set
operations, and a `sketch_funcs` function group are available.

Window aggregates accept filter predicates. `reverse` reverses bytes for
`BinaryType`.

### Floating-point set equality (4.2.0)

`array_distinct`, `array_union`, `array_intersect`, `array_except`, and
`arrays_overlap` normalize `-0.0` and `NaN` under Spark equality semantics.
`collect_set` likewise deduplicates floating-point `NaN` and negative zero
consistently.

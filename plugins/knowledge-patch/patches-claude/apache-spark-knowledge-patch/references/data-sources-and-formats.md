# Data sources, catalogs, and file formats

Use this reference for connector implementation, JDBC mapping, Data Source V2,
catalog behavior, schema evolution, and storage-format compatibility.

## Core data-path fixes

### Columnar timestamps and materialized expressions (3.5.5)

`ColumnarRow` and `MutableColumnarRow` support `TimestampNTZType`, allowing
timestamp-without-time-zone values through those paths. Data Source V2
relations no longer retain unresolved cast expressions after
`current_timestamp()` is materialized.

### Temporary tables and non-default catalogs (3.5.5)

`Catalog.listTables` handles temporary tables when the active session catalog
is not `V2SessionCatalog`.

### Writer paths and catalog locations (3.5.6)

`DataFrameWriterV2` honors its `path` option. `CatalogStorageFormat.locationUri`
is decoded instead of retaining an encoded representation. The affected
identifier is `description_file`, not `description-file`; integrations that
name it directly must use the underscore spelling.

### User-defined type strings (3.5.7)

A user-defined type's `catalogString` is complete rather than truncated, so
schema and catalog consumers receive the full description.

## File-read and write compatibility

### Corrupt and missing files (4.0-migration)

SQL table reads consult `spark.sql.files.ignoreCorruptFiles` and
`spark.sql.files.ignoreMissingFiles`, not the corresponding `spark.files.*`
settings. `AccessControlException` and `BlockMissingException` always fail a
task even when corrupt files are ignored.

As of 4.1-migration, `java.lang.InternalError` during a file read is ignored
when either `spark.sql.files.ignoreCorruptFiles=true` or the data-source
`ignoreCorruptFiles=true` option is active.

### Per-query table options (4.0-migration)

Every read of a file-source table honors that query's options, such as
delimiters, instead of reusing options cached with the first plan. Set
`spark.sql.legacy.readFileSourceTableCacheIgnoreOptions=true` for the old
caching behavior.

### Hive and compression changes (4.0-migration)

Hive metastores older than 2.0.0 are unsupported. `hive-llap-common` is no
longer bundled and must be added when needed. Parquet accepts `lz4_raw`, not
`lz4raw`; ORC compression defaults to `zstd` instead of `snappy`.

The legacy-prefixed datetime-rebase settings were removed. Use:

- `spark.sql.parquet.int96RebaseModeInWrite`
- `spark.sql.parquet.datetimeRebaseModeInWrite`
- `spark.sql.parquet.int96RebaseModeInRead`
- `spark.sql.avro.datetimeRebaseModeInWrite`
- `spark.sql.avro.datetimeRebaseModeInRead`

### File-source write semantics (4.2.0)

V1 file-source inserts enforce `NOT NULL`. Per-write file options override
session settings. With `PathOutputCommitProtocol`, dynamic partition overwrite
replaces affected partitions instead of appending. A Parquet compatibility
flag can ignore the `UNKNOWN` type annotation to restore earlier behavior.

## JDBC behavior

### Mapping changes (4.0-migration)

JDBC mappings preserve database-native types more closely:

- PostgreSQL `TIMESTAMP WITH TIME ZONE` reads as `TimestampType` regardless of
  `preferTimestampNTZ`; `TimestampType` writes as `TIMESTAMP WITH TIME ZONE`.
  Use `spark.sql.legacy.postgres.datetimeMapping.enabled=true` for both old
  mappings.
- MySQL `TIMESTAMP` reads as `TimestampType`; `TimestampNTZType` writes as
  `DATETIME`. The timestamp compatibility flag is
  `spark.sql.legacy.mysql.timestampNTZMapping.enabled=true`. `SMALLINT`,
  `MEDIUMINT UNSIGNED`, `FLOAT`, and `BIT(n > 1)` now read as `ShortType`,
  `IntegerType`, `FloatType`, and `BinaryType`; `ShortType` writes as
  `SMALLINT`. Use `spark.sql.legacy.mysql.bitArrayMapping.enabled=true` for the
  old BIT mapping.
- Oracle `TimestampType` writes as `TIMESTAMP WITH LOCAL TIME ZONE`; use
  `spark.sql.legacy.oracle.timestampMapping.enabled=true` to write `TIMESTAMP`.
- SQL Server `TINYINT` and `DATETIMEOFFSET` read as `ShortType` and
  `TimestampType`. Compatibility flags are
  `spark.sql.legacy.mssqlserver.numericMapping.enabled` and
  `spark.sql.legacy.mssqlserver.datetimeoffsetMapping.enabled`.
- DB2 `SMALLINT` reads as `ShortType`; `BooleanType` writes as `BOOLEAN`.
  Compatibility flags are `spark.sql.legacy.db2.numericMapping.enabled` and
  `spark.sql.legacy.db2.booleanMapping.enabled`.

### Read and pushdown behavior (4.2.0)

The PostgreSQL dialect supplies a default fetch size so reads do not load the
entire result into memory. Oracle `TRUNC` pushdown maps Spark truncation formats
to the corresponding Oracle formats.

Derby as a JDBC data source is deprecated (4.2-migration).

## Data Source V2 capabilities

### Catalog and table surface (4.0.0)

Data Source V2 adds clustering, APIs for loading stored procedures, CTAS,
create-table support, `ALTER NAMESPACE ... UNSET PROPERTIES`, and percentile
pushdown. The configured `spark_catalog` can select the built-in catalog using
its new magic value.

### Connector surface (4.1.0)

Data Source V2 adds table constraints, join pushdown, DML metrics,
`listTableSummaries`, and a `BOOLEAN_EXPRESSION` predicate. JDBC join pushdown
supports Oracle, PostgreSQL, MySQL, and SQL Server.

### Transactions, views, and DDL (4.2.0)

Connectors can implement transactions that atomically commit multiple
operations. V2 catalogs add `MetadataOnlyTable`, view creation and alteration,
the remaining view DDL and inspection commands, `CREATE TABLE LIKE`,
partition-aware `DESCRIBE TABLE`, and column defaults in writes.

`SimpleProcedure` and `SimpleFunction` let connector authors implement
procedures and functions without custom bind logic.

### Partition predicates (4.2.0)

`PartitionPredicate` supports nested partition columns, participates in runtime
filtering, and can drive metadata-only `DELETE` operations.

### Change Data Capture (4.2.0)

The connector CDC API is available through the SQL `CHANGES` clause and
DataFrame, PySpark, and Spark Connect `changes()` APIs. CDC reads work in batch
and streaming, including streaming `netChanges`.

## Schema evolution and inserts

### Merge evolution (4.0.0)

SQL `MERGE`, `DataFrameWriterV2.MergeInto`, and PySpark `DataFrame.mergeInto`
support schema-aware merge workflows.

### Evolving and replacement inserts (4.2.0)

`INSERT ... WITH SCHEMA EVOLUTION` handles sources with fewer columns or
nested fields on Data Source V2 append and overwrite paths. Spark also supports
`INSERT INTO ... REPLACE ON/USING` and `BY NAME` with `REPLACE WHERE`.

## Format-specific behavior

### CSV, ORC, and Avro features (4.0.0)

CSV writers accept a file-extension option, duplicate column names, and binary
values with configurable output styling. ORC supports Brotli compression.
Avro supports logical-type registration, custom union-field prefixes,
xz/Zstandard compression levels, `schema_of_avro`, and SQL-callable
`to_avro`/`from_avro`.

### Parquet schema correctness (4.0.1)

`ParquetToSparkSchemaConverter` matches fields by Parquet field ID rather than
depending only on names or order.

### XML binary values (4.0.1)

`BinaryType` values convert to XML without the former conversion error.

### ORC and Parquet read fixes (3.5.7)

ORC filter pushdown returns correct results for DataFrame `eqNullSafe` and SQL
`<=>` predicates. The vectorized Parquet delta-length byte-array reader no
longer fails affected reads with
`ParquetDecodingException: Failed to read X bytes`.

### Missing projected struct fields (4.1-migration)

If every requested field of a struct is absent from a Parquet file, Spark reads
an additional present field to determine whether the struct itself is null.
Set `spark.sql.legacy.parquet.returnNullStructIfAllFieldsMissing=true` to keep
assuming the struct is null.

### File-source types (4.1.0)

File-source readers support Zstandard. Parquet supports `NullType` and its
`VOID` or `UNKNOWN` representations. Spark can use Hive Metastore 4.1.

### Time, Variant, and geospatial I/O (4.1.0, 4.2.0)

CSV and XML scans support `VARIANT`; Parquet supports Variant shredding and
logical-type annotations (4.1.0). JSON, XML, CSV, ORC, and Avro support `TIME`,
while Parquet supports native geospatial types and their SRIDs (4.2.0).

## Hive and Thrift compatibility

### Table-creation fallback (4.0.1)

When table creation fails with a Thrift exception, Spark does not fall back to
a Hive-incompatible creation path.

### Column ordinals (4.1-migration)

Spark Thrift Server `GetColumns` reports one-based `ORDINAL_POSITION` values.
Use `spark.sql.legacy.hive.thriftServer.useZeroBasedColumnOrdinalPosition=true`
for clients that still require zero-based ordinals.

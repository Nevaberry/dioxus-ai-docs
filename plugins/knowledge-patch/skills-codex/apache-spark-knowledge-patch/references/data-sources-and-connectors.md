# Data Sources and Connectors

## Core row, relation, and write behavior

- `ColumnarRow` and `MutableColumnarRow` support `TimestampNTZType`
  (`3.5.5`).
- Data Source V2 relations do not retain unresolved casts after
  `current_timestamp()` is materialized.
- `ReplaceTableAsSelect` overwrites the replacement table rather than
  appending to it (`3.5.6`).
- `DataFrameWriterV2` honors its `path` option.
- `CatalogStorageFormat.locationUri` is decoded rather than left encoded.
- The affected identifier is `description_file`, not `description-file`;
  direct integrations must use the underscore spelling.

## Data Source V2 catalog and connector API

The `4.0.0` connector surface includes:

- clustering;
- stored-procedure loading;
- CTAS and create-table support;
- `ALTER NAMESPACE ... UNSET PROPERTIES`;
- percentile pushdown; and
- a magic value that lets configured `spark_catalog` select the built-in
  catalog.

The `4.1.0` surface adds:

- table constraints, join pushdown, and DML metrics;
- `listTableSummaries`;
- a `BOOLEAN_EXPRESSION` predicate; and
- JDBC join pushdown for Oracle, PostgreSQL, MySQL, and SQL Server.

The `4.2.0` surface adds:

- CDC connector APIs exposed by SQL `CHANGES` and DataFrame, PySpark, and
  Connect `changes()` methods, for both batch and streaming reads including
  streaming `netChanges`;
- transactions that commit multiple connector operations atomically;
- `MetadataOnlyTable`;
- V2 view creation, alteration, remaining view DDL, and inspection;
- `CREATE TABLE LIKE`, partition-aware `DESCRIBE TABLE`, and column defaults
  in writes;
- `SimpleProcedure` and `SimpleFunction` helpers that avoid custom bind logic;
  and
- `PartitionPredicate` support for nested partition columns, runtime filters,
  and metadata-only `DELETE`.

## Python data sources

- Python data sources add V2 table creation and writes, Arrow writers, custom
  metrics, and session-scoped registration in `4.0.0`.
- Filter pushdown, an Arrow writer for streaming sources, and overwrite of a
  statically registered source arrive in `4.1.0`.
- Streaming readers add admission control and `Trigger.AvailableNow` in
  `4.2.0`.
- Returned Arrow types must match the declared schema; mismatches fail with
  `DATA_SOURCE_RETURN_SCHEMA_MISMATCH`.
- `SimpleDataSourceStreamReader` must advance its offset whenever it returns
  records.

## CSV, XML, JSON, ORC, Avro, and Parquet

### CSV, XML, and JSON

- CSV writers add a file-extension option, allow duplicate column names, and
  write binary values with configurable styling (`4.0.0`).
- `BinaryType` converts to XML without the earlier failure (`4.0.1`).
- Unlimited JSON size is restored, and Variant values round-trip through
  `from_json` and `to_json`.

### ORC

- ORC 1.9.6 is bundled in `3.5.6`.
- ORC writers support Brotli in `4.0.0`.
- Null-safe ORC filter pushdown produces correct results for DataFrame
  `eqNullSafe` and SQL `<=>` (`3.5.7`).
- File-source readers support Zstandard in `4.1.0`.
- ORC can read and write `TIME` in `4.2.0`.

### Avro

- Avro 1.11.4 is bundled in `3.5.5`.
- `4.0.0` adds logical-type registration, custom union-field prefixes,
  xz/Zstandard compression levels, `schema_of_avro`, and SQL-callable
  `to_avro` and `from_avro`.
- Avro can read and write `TIME` in `4.2.0`.

### Parquet

- `ParquetToSparkSchemaConverter` matches by Parquet field ID (`4.0.1`).
- The vectorized delta-length byte-array reader no longer fails affected files
  with `ParquetDecodingException: Failed to read X bytes` (`3.5.7`).
- Parquet supports `NullType` and its `VOID` or `UNKNOWN` forms (`4.1.0`).
- Variant shredding schema and logical-type annotations are written and read.
- A compatibility flag can ignore the Parquet `UNKNOWN` type annotation and
  restore earlier behavior (`4.2.0`).

### Hive Metastore

Spark can use Hive Metastore 4.1 as of `4.1.0`.

## File-write semantics

As of `4.2.0`:

- V1 file-source inserts enforce `NOT NULL`.
- Per-write file options take precedence over session configuration.
- Dynamic partition overwrite with `PathOutputCommitProtocol` replaces the
  affected partitions rather than appending.
- SQL insert schema evolution covers missing source columns and nested fields
  on V2 append and overwrite paths.

## JDBC

- Spark `4.1.0` supports connector join pushdown for Oracle, PostgreSQL, MySQL,
  and SQL Server.
- The PostgreSQL dialect supplies a default fetch size in `4.2.0`, preventing
  reads from loading the full result into memory.
- Oracle `TRUNC` pushdown maps Spark truncation formats to Oracle equivalents.
- Refer to the migration reference for changed PostgreSQL, MySQL, Oracle,
  SQL Server, and DB2 type mappings.

## Bundled dependency alignment

When an application overrides Spark dependencies, align exclusions with the
artifacts in the deployed Spark distribution:

- `3.5.5`: Avro 1.11.4.
- `3.5.6`: ORC 1.9.6.
- `4.0.1`: Kafka 3.9.1, ORC 2.1.3, and ORC Format 1.1.1.
- `3.5.7`: ORC 1.9.7 and Jetty 9.4.58.v20250814.
- `3.5.8`: Avro 1.11.5, Jersey 2.47, and ORC 1.9.8.
- `4.2.0`: Arrow Java 19.0.0, Hadoop 3.5.0, Jakarta Servlet 6.0.0,
  Jersey 3.1.11, Kubernetes client 7.6.1, Log4j 2.25.4, Netty 4.2.13,
  ORC 2.3.0, Parquet 1.17.0, and Scala 2.13.18.

The `gcs-connector` entry is removed in `4.2.0`, while `hadoop-gcp` 3.5.0 is
added.

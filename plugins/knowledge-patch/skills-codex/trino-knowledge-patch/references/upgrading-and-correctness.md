# Upgrading and correctness

Use this reference before changing the server release or investigating results
that differ across releases. Later behavior supersedes an earlier warning when
the text explicitly says a defect was fixed or a behavior was reversed.

## Release selection and runtime prerequisites

- Do not deploy release 473. `GROUP BY` and `DISTINCT` with more than 33
  million unique groups can return incorrect results. Release 474 fixes the
  result defect. Release 474 can instead overcount memory and raise
  `EXCEEDED_LOCAL_MEMORY_LIMIT`; release 475 fixes that accounting defect
  (batch 473-474 and 475).
- The JDBC driver and CLI require Java 11 or newer (470).
- The release 473-474 Docker image uses JDK 24. The server itself requires
  JDK 24 from 476.
- The release 478 Docker image uses JDK 25.0.0 build 36. Building and running
  the server requires JDK 25 from 479.
- BigQuery and Snowflake require the JVM option
  `--sun-misc-unsafe-memory-access=allow` (476).
- Ignite requires `--add-opens=java.base/java.util=ALL-UNNAMED` (483).
- RPM packages are no longer published (471). Use the tarball or container
  image, or build an RPM using the setup from the `trino-packages` repository.

## Removed connectors, integrations, and packaging

- The Kinesis connector was removed (470).
- The deprecated `glue-v1` metastore type was removed from Delta Lake, Hive,
  and Hudi, and the deprecated Databricks Unity Catalog integration was
  removed from Delta Lake and Hive (473-474).
- Kudu and Phoenix were removed (473-474).
- Vertica was removed (480).
- The HTTP server event-listener plugin is no longer included in the server
  binary distribution or Docker container (477); install it separately if it
  remains part of the deployment.
- Every catalog must be deployed on every node (477).
- Failed catalogs were hidden from `system.metadata.catalogs` in 477. Starting
  with 478 they appear in that table and can be dropped; this later behavior
  intentionally reverses the earlier one.

## Removed and renamed server properties

- Replace HTTP client prefixes `workerInfo` and `memoryManager` with
  `worker-info` and `memory-manager` (472).
- `optimizer.optimize-hash-generation` and `optimize_hash_generation` were
  removed (470).
- `task.statistics-cpu-timer-enabled` is defunct and must be removed (479).
- `prefer_streaming_operators` was removed (479).
- `enable-large-dynamic-filters`, `enable_large_dynamic_filters`,
  `dynamic-filtering.small*`, and `dynamic-filtering.large-broadcast*` were
  removed (480).
- `deprecated.http-server.authentication.oauth2.groups-field` was removed
  (480).
- `EXPLAIN (TYPE LOGICAL)` and `EXPLAIN (TYPE DISTRIBUTED)` are deprecated;
  use `EXPLAIN` without a type clause (479).
- Alluxio-backed fault-tolerant exchange storage was removed (482).

## Connector and storage configuration migrations

- Legacy Azure Storage, GCS, IBM Cloud Object Storage, S3, and S3-compatible
  file systems were deprecated for Delta Lake, Hive, Hudi, and Iceberg in 470.
  Legacy support is removed for Delta Lake, Hive, Iceberg, and Lakehouse in
  481; those catalogs must use native file systems, and `fs.hadoop.enabled`
  applies only to HDFS.
- Alluxio file-system support was removed from Delta Lake, Hive, Hudi, and
  Iceberg (482). The Alluxio file-system cache remains supported.
- Replace `s3.socket-read-timeout` with `s3.socket-timeout` (477).
- `gcs.use-access-token` was deprecated in favor of `gcs.auth-type` (478) and
  removed in 480. `gcs.auth-type=APPLICATION_DEFAULT` is supported (479);
  `SERVICE_ACCOUNT` no longer implies anonymous access.
- For native S3, use `s3.auth-type` (483): `ANONYMOUS` for public buckets,
  `IAM_ROLE` when `s3.iam-role` is configured, and `WEB_IDENTITY` instead of
  removed `s3.use-web-identity-token-credentials-provider`.
- `hive.s3.storage-class-filter` became `hive.s3-glacier-filter` (475).
- `fs.cache.preferred-hosts-count` became the coordinator-wide
  `node-scheduler.cache-preferred-hosts-count` (481).
- `hive.parquet.max-split-size` controls Parquet splits, while
  `hive.max-split-size` is for other formats. Remove
  `hive.max-initial-splits` and `hive.max-initial-split-size` (482).
- Replace shared lakehouse writer properties
  `parquet.optimized-writer.validation-percentage`,
  `hive.parquet.writer.block-size`, and `hive.parquet.writer.page-size` with
  `parquet.writer.validation-percentage`, `parquet.writer.block-size`, and
  `parquet.writer.page-size`. Remove `hive.write-validation-threads`,
  `gcs.use-access-token`, and `hive.fs.new-file-inherit-ownership` (480).
- Delta Lake's `metadata.live-files.cache-size`,
  `metadata.live-files.cache-ttl`, and `checkpoint-filtering.enabled` are
  defunct because the live-files cache was removed (480).
- Delta Lake renamed `s3.exclusive-create` to
  `delta.s3.transaction-log-conditional-writes.enabled` (479). The temporary
  need for `PutObjectTagging` permission was removed in 480.
- Replace the listed database connectors'
  `join-pushdown.with-expressions` with
  `deprecated.join-pushdown.with-expressions`; the replacement is itself
  temporary (479).
- Iceberg REST SigV4 uses `iceberg.rest-catalog.security=SIGV4`; remove
  `iceberg.rest-catalog.sigv4-enabled` (477).
- Iceberg reads table compression from the `compression_codec` table property;
  the `compression_codec` session property was removed (477).
- Remove `iceberg.extended-statistics.enabled` and
  `extended_statistics_enabled` (480).
- Iceberg split-size configuration uses `iceberg.max-split-size` or
  `max_split_size`, replacing `experimental_split_size` (482).
- Iceberg write sizing uses `target_max_file_size` and
  `parquet_writer_row_group_size`, persisted as
  `write.target-file-size-bytes` and
  `write.parquet.row-group-size-bytes`. Equivalent session properties and the
  `parquet_writer_block_size` alias were removed (482).

## Core query-result fixes

- Negative hexadecimal, octal, and binary literals parse correctly (469).
- SQL UDFs accept upper-case variable names (470), and structural defaults
  such as arrays (482).
- `array_histogram` accepts null elements (470).
- Wide `SELECT` lists no longer fail (472).
- `cosine_distance` and `cosine_similarity` handle arrays containing nulls
  correctly (472); `cosine_distance` also accepts sparse vectors (477).
- Window functions used with `DISTINCT` return correct results (475).
- Spilled `GROUP BY` queries no longer return incorrect results (477).
- Spatial joins using `ST_Contains`, `ST_Intersects`, or `ST_Distance` return
  correct results, and `geometry_to_bing_tiles` covers the full geometry
  (477).
- Queries using `row` no longer risk incorrect results (478).
- `EXPLAIN ANALYZE` executes the same plan used by the analyzed query (478).
- Row-pattern `FIRST` logical navigation returns correct results (478).
- `localtimestamp` is correct at precision 3 and works at precisions 7 and 8;
  `date_add` accepts values beyond `Integer.MAX_VALUE`; and casts from `json`,
  `time`, `boolean`, or `interval` to undersized `varchar(n)` no longer return
  incorrect values (480).
- High-precision JSON parsing and literals preserve decimal portions beyond
  16 significant digits. The fix also applies to JSON read through MongoDB,
  MySQL, Pinot, PostgreSQL, and SingleStore (481).
- `number` handles `NaN` and over-precision values correctly in queries,
  equality, `DISTINCT`, and `GROUP BY`. Decimal-to-double conversion below
  precision 19, floating-point rounding into underflow, and ordering or
  aggregation of rows wider than 64 fields are also corrected (482).
- Recursive CTE column lineage is correct when column aliases are used (482).
- Connector custom types spool correctly, and table functions can return
  large pass-through columns (482).

## Connector and file-format correctness

### Delta Lake

- Deletion-vector reads and updates are corrected (469).
- `vacuum` no longer risks table corruption (470).
- Large checkpoint files can be written (471).
- Highly concurrent modifications have improved support (472).
- Malformed deletion-vector checkpoints and special characters in
  deletion-vector partition paths no longer cause bad results (477).
- `IS NOT DISTINCT FROM` produces correct results (479).
- `CREATE OR REPLACE` changes to table definitions no longer risk corruption
  (480).
- `DELETE` against indexed Parquet files no longer removes the wrong rows,
  especially for Spark-written tables (481).
- Failed-write cleanup no longer deletes active files from deletion-vector
  tables (482).

### Hive, Hudi, and shared formats

- Hive prevents invalid JSON writes for `NaN` and positive or negative
  infinity (469).
- Partitioned OpenX JSON SerDe results and timestamps surrounded by spaces in
  Regex or OpenX JSON input are corrected (475).
- Old-PyArrow Parquet files and decimals whose declared precision differs from
  Parquet metadata read correctly in Delta Lake, Hive, Hudi, and Iceberg
  (477).
- Hive honors `partition_projection_format` for date projection (477).
- Google Sheets delegated-user queries no longer fail intermittently (478).
- Hive ORC writes preserve dates and timestamps before `1582-10-15` for
  Apache Hive interoperability (478).

### Iceberg

- `table_changes` returns complete results (469).
- Equality deletes containing nested fields are readable, and `$entries` and
  `$all_entries` work with equality deletes (470).
- Columns containing dots can be added (470).
- Reads after deletes return correct results (472).
- Concurrent `MERGE` conflict detection avoids needless failures (471).
- `add_files_from_table` accepts matching tables without a false column-count
  error, and `optimize_manifests` works without a snapshot (478).
- Avro files migrated from Hive read correctly (478).
- `SHOW CREATE SCHEMA` tolerates unsupported properties in REST, Glue, and
  Nessie catalogs; `EXPLAIN` and `EXPLAIN ANALYZE` work for `OPTIMIZE` (478).
- `IS NOT DISTINCT FROM` produces correct results (479).
- Setting a partition spec preserves existing partition columns; LZ4 Parquet
  compression is readable; and written `compression-codec` metadata is
  spec-compliant (480).
- Partition-filtered `optimize` cleans partition-scoped equality deletes
  (480).
- `CREATE OR REPLACE MATERIALIZED VIEW` preserves data at fixed storage
  locations, and view replacement preserves custom REST or JDBC catalog
  locations (482).
- `OPTIMIZE` detects nulls in `NOT NULL` columns and fails instead of
  corrupting the table (483).

### Database and service connectors

- MySQL prevents invalid negative date writes (470).
- MongoDB case-sensitive table-name conflicts no longer fail queries (471).
- Loki connects to versions higher than 3.2.0 (472).
- SQL Server case-insensitive-collation `LIKE` results are corrected (475).
- MySQL and PostgreSQL return correct `IS NOT DISTINCT FROM` results (479).
- Multi-bit `BIT(n)` columns are no longer exposed by MySQL or SingleStore
  because the earlier mapping was incorrect (480).
- MySQL and SQL Server do not push character inequality or range predicates,
  avoiding trailing-space errors. SQL Server `DELETE` or `UPDATE` operations
  that require this pushdown fail; Oracle trims blank padding when pushing a
  `char`-to-`varchar` cast (482).

## Semantic compatibility changes

- Decimal arithmetic uses revised precision and scale inference. Set
  `deprecated.legacy-arithmetic-decimal-operators=true` to temporarily restore
  the old behavior (477).
- Geometry moved from Esri to JTS (481). WKT must conform to OGC syntax.
  `ST_Union` returns an empty geometry collection, not `NULL`, for empty input
  and no longer inserts intersection vertices for point-on-line unions.
- `char` now coerces to `varchar`, trims trailing spaces, and compares with
  `varchar` semantics. Use
  `deprecated.legacy-varchar-to-char-coercion=true` only as a migration bridge
  to the old blank-padded behavior (482).
- Iceberg `$files.lower_bounds` and `upper_bounds` are typed rows, not
  `map(integer, varchar)`. Replace numeric subscripts such as
  `lower_bounds[1]` and JSON casts (482).
- TPC-DS generated data and statistics change because the connector uses
  generator version 1.7 (482).


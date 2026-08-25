# Upgrade and Correctness

Use this reference first during an upgrade or incident review. It consolidates
unsafe releases, runtime floors, removed components, and fixes where old results
or writes can be wrong.

## Release selection

- Do not deploy release 473. `GROUP BY` and `DISTINCT` with more than 33 million
  unique groups can return incorrect results; release 474 fixes that defect
  (473-474).
- Release 474 can overcount memory and reject queries with
  `EXCEEDED_LOCAL_MEMORY_LIMIT`; release 475 fixes the accounting problem
  (473-474, 475).
- Use JDK 25 to build and run current Trino (479). JDBC and CLI require Java 11+
  (470). BigQuery and Snowflake also need
  `--sun-misc-unsafe-memory-access=allow` (476), while Ignite needs
  `--add-opens=java.base/java.util=ALL-UNNAMED` (483).

## Removed distributions, connectors, and integrations

- RPMs are no longer distributed (471); use the tarball/container or build from
  the `trino-packages` setup.
- Remove Kinesis catalogs (connector removed in 470), Kudu and Phoenix catalogs
  (removed in 473-474), and Vertica catalogs (removed in 480).
- Remove `glue-v1` metastore configuration and deprecated Databricks Unity
  Catalog integration where applicable (473-474).
- Deploy every catalog on every node (477), and separately install the HTTP
  server event-listener plugin if used because it is no longer bundled (477).

## Configuration removals and renames

- Rename `workerInfo`/`memoryManager` HTTP prefixes to
  `worker-info`/`memory-manager` (472), Hive Glacier filtering to
  `hive.s3-glacier-filter` (475), and `s3.socket-read-timeout` to
  `s3.socket-timeout` (477).
- Migrate `gcs.use-access-token` to `gcs.auth-type` (deprecated in 478, removed
  in 480), and select native S3 credentials with `s3.auth-type` (483).
- Remove `optimize_hash_generation` and `optimizer.optimize-hash-generation`
  (470), `prefer_streaming_operators` and `task.statistics-cpu-timer-enabled`
  (479), and obsolete dynamic-filter/OAuth settings listed in the operations
  reference (480).
- Remove the Delta live-files cache settings and old shared Parquet writer
  settings (480). Migrate Iceberg's removed extended-statistics settings (480),
  typed `$files` bounds and write/split-size settings (482).
- Native object-store clients are mandatory for Delta Lake, Hive, Iceberg, and
  Lakehouse (481). Alluxio exchange and file-system support was removed (482).

## Query-result correctness fixes

- Delta deletion vectors no longer produce incorrect reads/updates (469) or
  malformed checkpoints and bad partition-path reads (477). Indexed-Parquet
  `DELETE` no longer removes wrong rows (481).
- Iceberg `table_changes` is complete (469), equality-delete metadata supports
  nested fields (470), and post-delete reads are correct (472).
- Window `DISTINCT` results are correct (475); spilling no longer corrupts
  `GROUP BY` (477); row types, row-pattern `FIRST`, and the analyzed plan are
  correct in 478.
- Hive OpenX JSON/Regex timestamps were corrected (475), as were old-PyArrow and
  mismatched-precision Parquet reads across lakehouse connectors (477).
- `IS NOT DISTINCT FROM` was corrected for Delta Lake, Iceberg, MySQL, and
  PostgreSQL (479). SQL Server case-insensitive `LIKE` was corrected in 475.
- High-precision JSON decimals are preserved by SQL parsing and MongoDB, MySQL,
  Pinot, PostgreSQL, and SingleStore reads (481).
- `number` values with `NaN` or excess precision, narrow-decimal casts,
  underflow rounding, and wide-row ordering/aggregation were corrected (482).
- Spatial joins and `geometry_to_bing_tiles` were corrected (477). The JTS
  migration changes WKT and `ST_Union` semantics (481), so regression-test
  geospatial workloads.

## Write and metadata safety fixes

- Delta `vacuum` corruption was fixed in 470; replacement-definition corruption
  in 480; deletion-vector failed-write cleanup in 482.
- Iceberg concurrent `MERGE`, partition writer limits, and partition-property
  preservation are corrected (471, 480). `OPTIMIZE` now fails safely on nulls in
  `NOT NULL` columns (483).
- `CREATE OR REPLACE` preserves fixed/custom locations for Iceberg materialized
  views and REST/JDBC views (482).
- The `system` catalog cannot be dropped (475). Failed catalogs are visible and
  droppable after the explicit 478 reversal of 477 behavior.

## Client and plugin compile checks

- Plugin code must absorb the page-source migration, connector lifecycle
  changes, type-parameter replacement, `Optional<String>` column metadata,
  dynamic-filter snapshot API, provider removals, and bit-packed block validity.
  See [spi-and-plugins.md](spi-and-plugins.md) for exact APIs.
- JDBC metadata class names were corrected in 480; scientific-notation
  `BigDecimal` binding and persistent/refreshable OAuth tokens arrived in 481.

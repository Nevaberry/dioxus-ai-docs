# Lakehouse and object storage

This reference covers shared file-system behavior and the Delta Lake, Hive,
Hudi, Iceberg, and Lakehouse connectors. Property names are catalog
properties unless identified as session or table properties.

## Shared native file systems

### Migration and supported backends

Legacy Azure Storage, GCS, IBM Cloud Object Storage, S3, and S3-compatible
file-system support was deprecated in Delta Lake, Hive, Hudi, and Iceberg
(470). It is removed for Delta Lake, Hive, Iceberg, and Lakehouse (481);
those catalogs must use native file systems. `fs.hadoop.enabled` now applies
only to HDFS.

Delta Lake, Hive, Hudi, and Iceberg support the local file system (471).
Alluxio file-system support was removed from those four connectors (482),
although the Alluxio file-system cache remains available.

### S3

- S3 security mappings support SSE-C in Delta Lake, Hive, Hudi, and Iceberg
  (469).
- `s3.storage-class` selects the write storage class for these connectors
  (471). Native S3 in Delta Lake, Hive, and Iceberg can retrieve cross-region
  data and write all storage classes (475).
- Delta Lake and Iceberg support native S3 signer selection; Hive can select
  the AWS signing protocol (476).
- Replace `s3.socket-read-timeout` with `s3.socket-timeout` (477).
- Select authentication with `s3.auth-type` (483). Use `ANONYMOUS` for public
  buckets, `IAM_ROLE` whenever `s3.iam-role` is configured, and
  `WEB_IDENTITY` instead of removed
  `s3.use-web-identity-token-credentials-provider`.

### Google Cloud Storage

- Set `gcs.endpoint` to choose the Google Storage endpoint (469).
- Anonymous GCS access is supported (477).
- Replace deprecated `gcs.use-access-token` with `gcs.auth-type` (478); the old
  property was removed in 480.
- `gcs.auth-type=APPLICATION_DEFAULT` is supported (479). `SERVICE_ACCOUNT`
  does not permit unauthenticated access.

### Azure

Delta Lake, Hive, Hudi, and Iceberg can authenticate to AzureFS with a
user-assigned managed identity (476). Those connectors plus Lakehouse expose
`azure.connection-pool-max-idle-time` and `azure.http-request-timeout` (481).

### Shared Parquet settings and cache metrics

`EXPLAIN ANALYZE VERBOSE` reports file-system cache reads for Delta Lake, Hive,
and Iceberg (477). Delta Lake, Hive, Iceberg, and Lakehouse can cap rows per
Parquet writer row group with `parquet.writer.block-row-count` or
`parquet_writer_block_row_count` (482).

Replace these shared writer properties (480):

| Removed property | Replacement |
| --- | --- |
| `parquet.optimized-writer.validation-percentage` | `parquet.writer.validation-percentage` |
| `hive.parquet.writer.block-size` | `parquet.writer.block-size` |
| `hive.parquet.writer.page-size` | `parquet.writer.page-size` |

Also remove `hive.write-validation-threads`, `gcs.use-access-token`, and
`hive.fs.new-file-inherit-ownership` (480).

Parquet files written by old PyArrow versions and decimals whose declared
precision differs from Parquet metadata read correctly in Delta Lake, Hive,
Hudi, and Iceberg (477).

## Delta Lake

### Defaults, types, and time travel

New Delta Lake table data uses `ZSTD` rather than `SNAPPY` compression by
default (469). The connector reads `variant` and cloned tables (471).
Timestamp time travel is supported (476):

```sql
SELECT *
FROM delta.sales.orders
FOR TIMESTAMP AS OF TIMESTAMP '2025-06-01 00:00:00 UTC';
```

Version and timestamp time-travel clauses accept parameters (480).

The `$properties` table includes the table location, and new Delta Lake tables
cannot partition on `varbinary` (482).

### S3 transaction-log writes

`s3.exclusive-create` was renamed to
`delta.s3.transaction-log-conditional-writes.enabled` (479). At that point S3
writes required `PutObjectTagging` unless the replacement was false. That
permission is no longer required from 480.

### Caches and maintenance

The live-files metadata cache was removed (480). Remove
`metadata.live-files.cache-size`, `metadata.live-files.cache-ttl`, and
`checkpoint-filtering.enabled`.

The `vacuum` corruption risk is fixed (470). Large checkpoint writes work
(471), and highly concurrent modifications have improved support (472).

### Correctness-sensitive operations

- Deletion-vector reads and updates are corrected (469).
- `MERGE` works on cloned tables (batch 473-474).
- Malformed deletion-vector checkpoints and special characters in partition
  paths no longer produce incorrect results (477).
- `IS NOT DISTINCT FROM` is correct (479).
- `CREATE OR REPLACE` table-definition changes no longer risk corruption
  (480).
- `DELETE` no longer selects the wrong rows in Parquet files with column
  indexes, especially Spark-written tables (481).
- Failed-write cleanup does not delete active files from deletion-vector
  tables (482).
- `map(..., json)` columns can contain null map values (478).

## Hive

### File formats and timestamps

Hive prevents invalid JSON writes for `NaN` and infinities (469). It can read:

- restored S3 Glacier objects when
  `hive.s3.storage-class-filter=READ_NON_GLACIER_AND_RESTORED` in 471; the
  property was renamed to `hive.s3-glacier-filter` in 475;
- Esri JSON, Twitter Elephantbird protobuf, text formats using
  `extended_boolean_literal`, and OpenCSV with quoting and escaping disabled
  (477);
- encrypted Parquet files (478);
- Esri GeoJSON (481), in addition to Esri JSON.

Hive ORC writes preserve dates and timestamps before `1582-10-15` for Apache
Hive readers (478). Nanosecond Parquet timestamps can be read into
`timestamp(p) with time zone`, and `INSERT` and `ANALYZE` support timestamp
columns with Hive Metastore 4 (480).

### Metadata, views, and projection

- Hive views expose column comments (475).
- Injected partition-projection columns accept multiple predicates (475).
- `partition_projection_format` works for date partition projection (477).
- `flush_metadata_cache` works with metastore impersonation (478).
- Table creation works with Hive Metastore 3.1 (481).
- Exclude selected tables from the directory cache with
  `hive.file-status-cache.excluded-tables` (476).

Partitioned OpenX JSON SerDe results and timestamps with surrounding spaces
from Regex or OpenX JSON deserializers are corrected (475).

### Split sizing

`hive.parquet.max-split-size` controls Parquet splits, while
`hive.max-split-size` controls other formats (482). Remove
`hive.max-initial-splits` and `hive.max-initial-split-size`.

## Hudi

Configure Parquet read batch size with `parquet.max-read-block-row-count` or
the `parquet_max_read_block_row_count` session property (477).
`hudi.max-split-size` caps read split size (483).

Hudi shares the SSE-C, GCS endpoint, local file-system, Azure identity, GCS
authentication, Alluxio removal, Azure timeout, S3 authentication, and common
Parquet behavior described above.

## Iceberg catalogs and authentication

### REST catalog sessions and security

REST catalogs expose (batch 473-474):

```properties
iceberg.rest-catalog.session-timeout=1h
iceberg.rest-catalog.oauth2.token-refresh-enabled=true
```

The values shown are the defaults. REST catalogs support IAM role
authentication (475). For SigV4, set
`iceberg.rest-catalog.security=SIGV4`; remove
`iceberg.rest-catalog.sigv4-enabled` (477).

`iceberg.rest-catalog.oauth2.token-exchange-enabled` controls the REST
catalog's OAuth `token-exchange-enabled` setting (479).

REST catalog integrations include the BigLake metastore and temporary GCS
credentials supplied by the catalog (480). REST catalogs also support Azure
vended credentials, caller-specified HTTP headers, and refreshable S3, GCS,
and Azure credentials (481).

Prefixed-path storage credentials are accepted, and REST and JDBC catalogs can
take a `location` when creating a view (482). With
`iceberg.rest-catalog.security=GOOGLE`, `gcs.json-key-file-path` is optional,
allowing Application Default Credentials (483).

Iceberg supports Amazon S3 Tables (471). The Glue catalog ID from
`hive.metastore.glue.catalogid` is applied (475).

## Iceberg table creation and layout

- Configure Parquet and ORC bloom-filter columns with
  `parquet_bloom_filter_columns` and `orc_bloom_filter_columns` (469).
- New tables set the applicable `write.<filetype>.compression-codec` table
  property (batch 473-474).
- The table `compression_codec` property controls the read codec; its session
  counterpart was removed (477).
- `data_location` does not require `object_store_layout_enabled`, and
  `write.object-storage.partitioned-paths` is supported (482).
- `target_max_file_size` and `parquet_writer_row_group_size` persist as
  `write.target-file-size-bytes` and
  `write.parquet.row-group-size-bytes`. Equivalent session properties and
  `parquet_writer_block_size` were removed (482).
- `iceberg.parquet-footer-cache.type` enables footer caching.
  `iceberg.max-split-size` and `max_split_size` replace
  `experimental_split_size` (482).
- `max_commit_retry` controls commit retries (470):

  ```sql
  ALTER TABLE lake.analytics.events SET PROPERTIES max_commit_retry = 8;
  ```

- `max_partitions_per_writer` corresponds to
  `iceberg.max-partitions-per-writer` (476):

  ```sql
  SET SESSION iceberg.max_partitions_per_writer = 100;
  ```

Partitioned writes honor `task.max-writer-count` (471). Metadata caching is
available when the Hive metastore backs the catalog (470).

## Iceberg v3 and schema evolution

Iceberg can create, write, and delete from v3 tables, including column
defaults and row lineage; `optimize`, `expire_snapshots`, and
`remove_orphan_files` support v3 (480). V3 capabilities also include:

- experimental `variant` support, with the variant type defined in SPI (481);
- `timestamp(9)` and `timestamp(9) with time zone` reads and writes (481);
- `geometry` and `geography` reads and writes (482);
- variant metadata up to 128 MB instead of 16 MB (482).

`ALTER ... SET DATA TYPE` can change nested types inside Iceberg `map` and
`array` columns (480). Adding a column whose name contains a dot works (470).

## Iceberg metadata tables

- `$entries` and `$all_entries` are available (469). They handle equality
  deletes with nested fields (470).
- The hidden `$partition` column is available (472):

  ```sql
  SELECT "$partition", count(*)
  FROM iceberg.sales.orders
  GROUP BY 1;
  ```

- `system.iceberg_tables` lists only Iceberg tables (475).
- `$partitions` reports statistics for newly added columns (475).
- `$all_manifests` adds delete-file counts and `reference_snapshot_id` (476).
- `$manifests` and `$all_manifests` add `content` (480).
- `$files` adds metadata including `added_snapshot_id` (481).
- `$files.lower_bounds` and `upper_bounds` are typed rows rather than
  `map(integer, varchar)` (482). Replace numeric subscripts and JSON casts.
- Metadata tables such as `$files`, `$snapshots`, and `$partitions` can be
  queried for materialized views (483).

## Iceberg maintenance

### Snapshot and metadata retention

Use the table-level `rollback_to_snapshot`; the
`system.rollback_to_snapshot` procedure is deprecated (469).
`write.metadata.delete-after-commit.enabled=true` removes the oldest tracked
version metadata files (469).

The `expire_snapshots` command accepts `retain_last` and
`clean_expired_metadata` (479). Table properties
`delete_after_commit_enabled` and `max_previous_versions` are available (480).

Refreshing an Iceberg materialized view cleans old snapshots (475). Within its
grace period, a missing or corrupt base Iceberg table can be ignored in favor
of the materialized view (479).

### Optimization and file management

Optimize manifests with (470):

```sql
ALTER TABLE lake.analytics.events EXECUTE optimize_manifests;
```

The procedure works even without a snapshot (478). `EXPLAIN` and
`EXPLAIN ANALYZE` support Iceberg `OPTIMIZE` (478).

`remove_orphan_files` returns execution metrics (478). `add_files`,
`add_files_from_table`, and `optimize` return execution metrics (481).
`add_files_from_table` no longer reports a false column-count mismatch (478).

Partition-filtered `optimize` removes partition-scoped equality-delete files
(480). `OPTIMIZE` fails safely rather than corrupting a table when a
`NOT NULL` column contains nulls (483).

## Iceberg correctness and interoperability

- `table_changes` returns complete results (469).
- Equality deletes with nested fields are readable (470).
- Reads after deletes return correct results (472).
- Concurrent `MERGE` conflict detection avoids unnecessary failures (471).
- Avro files migrated from Hive read correctly (478).
- `SHOW CREATE SCHEMA` tolerates unsupported properties in REST, Glue, and
  Nessie catalogs (478).
- Setting a partition specification preserves existing partition columns,
  `write.parquet.compression-codec=LZ4` is readable, and written
  `compression-codec` metadata is spec-compliant (480).
- `IS NOT DISTINCT FROM` returns correct results (479).
- `CREATE OR REPLACE MATERIALIZED VIEW` preserves data at fixed storage
  locations. `CREATE OR REPLACE VIEW` preserves custom storage locations in
  REST and JDBC catalogs (482).
- Iceberg and Lakehouse can read Iceberg tables backed by encrypted Parquet
  (483).

## Lakehouse connector

The Lakehouse connector is available (477). It participates in the native
object-storage requirement, Azure timeout settings, Parquet writer row-group
limits, native S3 authentication, and encrypted Iceberg Parquet support
described above.


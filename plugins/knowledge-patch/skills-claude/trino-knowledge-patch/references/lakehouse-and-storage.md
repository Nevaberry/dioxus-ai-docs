# Lakehouse and Storage

Use this reference for Delta Lake, Hive, Hudi, Lakehouse, shared object storage,
Parquet, ORC, and fault-tolerant exchange storage. Iceberg-specific behavior is
in [iceberg.md](iceberg.md).

## Native file-system migration

- Legacy Azure, GCS, IBM Cloud Object Storage, S3, and S3-compatible support was
  deprecated for Delta Lake, Hive, Hudi, and Iceberg in 470. It was removed for
  Delta Lake, Hive, Iceberg, and Lakehouse in 481; use native file systems.
  `fs.hadoop.enabled` now applies only to HDFS.
- Local-file-system support arrived for Delta Lake, Hive, Hudi, and Iceberg in
  471. Alluxio exchange storage and the Alluxio file system were removed in 482,
  although the Alluxio file-system cache remains supported.
- SSE-C is available through S3 security mappings for Delta Lake, Hive, Hudi,
  and Iceberg, and `gcs.endpoint` selects a Google Storage endpoint (469).
- `s3.storage-class` selects the class of newly written S3 objects (471). Native
  S3 later gained cross-region reads and all storage classes for Delta Lake,
  Hive, and Iceberg (475), plus signer selection for Delta Lake and Iceberg and
  AWS signing-protocol selection for Hive (476).
- Anonymous GCS access is supported (477). `gcs.use-access-token` was deprecated
  in favor of `gcs.auth-type` (478) and removed in 480. Use
  `gcs.auth-type=APPLICATION_DEFAULT` for application-default credentials;
  `SERVICE_ACCOUNT` no longer implies anonymous access (479).
- Native S3 authentication uses `s3.auth-type` (483): choose `ANONYMOUS` for
  public buckets, `IAM_ROLE` whenever `s3.iam-role` is configured, and
  `WEB_IDENTITY` instead of the removed
  `s3.use-web-identity-token-credentials-provider`.
- AzureFS supports user-assigned managed identities (476). Shared Azure clients
  accept `azure.connection-pool-max-idle-time` and `azure.http-request-timeout`
  (481).
- The catalog-local `fs.cache.preferred-hosts-count` moved to coordinator config
  as `node-scheduler.cache-preferred-hosts-count` (481).

## Shared Parquet and writer configuration

- Reads no longer return incorrect data for Parquet written by old PyArrow or
  for decimals whose declared precision differs from Parquet metadata (477).
- Delta Lake, Hive, Hudi, and Iceberg removed `hive.write-validation-threads`,
  `gcs.use-access-token`, and `hive.fs.new-file-inherit-ownership` in 480.
  Rename `parquet.optimized-writer.validation-percentage`,
  `hive.parquet.writer.block-size`, and `hive.parquet.writer.page-size` to
  `parquet.writer.validation-percentage`, `parquet.writer.block-size`, and
  `parquet.writer.page-size`.
- Delta Lake, Hive, Iceberg, and Lakehouse can cap rows per writer row group with
  `parquet.writer.block-row-count` or session property
  `parquet_writer_block_row_count` (482).
- `EXPLAIN ANALYZE VERBOSE` reports file-system-cache bytes for Delta Lake, Hive,
  and Iceberg (477).

## Fault-tolerant execution and exchange storage

- S3-compatible fault-tolerant exchange storage became more interoperable in
  470. For an HDFS-like exchange, set
  `exchange.hdfs.skip-directory-scheme-validation=true` when scheme validation
  must be bypassed (470).
- Azure-backed exchange storage works with workload identity (471).
- The Exchange Manager configuration file location is configurable (479).
- Azure exchange spooling exposes `exchange.azure.max-connections`,
  `exchange.azure.pending-acquire-max-count`, and
  `exchange.azure.connection-acquisition-timeout` (483).

## Delta Lake

- New table data uses ZSTD rather than SNAPPY by default (469). Delta can read
  `variant` and cloned tables (471), and `MERGE` works on clones (473-474).
- Maps with JSON values can be read when individual map values are `NULL` (478).
- Correctness and safety fixes include deletion-vector reads/updates (469),
  corruption risk in `vacuum` (470), large checkpoint writes (471), concurrent
  modifications (472), malformed deletion-vector checkpoints and special
  partition paths (477), indexed-Parquet deletes (481), and failed-write cleanup
  for deletion-vector tables (482).
- `CREATE OR REPLACE` operations that change a table definition no longer risk
  corruption (480).
- The live-files metadata cache was removed in 480. Delete
  `metadata.live-files.cache-size`, `metadata.live-files.cache-ttl`, and
  `checkpoint-filtering.enabled` from catalogs.
- The `$properties` table includes table location, and new tables reject
  `varbinary` partition columns (482).
- `s3.exclusive-create` became
  `delta.s3.transaction-log-conditional-writes.enabled` in 479. That release
  required `PutObjectTagging` unless the replacement was false; as of 480,
  Delta writes no longer require `PutObjectTagging`.

## Hive

- Hive prevents invalid JSON output for `NaN` and positive/negative infinity
  (469). AWS retry metrics distinguish logical client retries from HTTP retries
  (469).
- Restored Glacier objects can be read. The 471 setting
  `hive.s3.storage-class-filter=READ_NON_GLACIER_AND_RESTORED` was renamed to
  `hive.s3-glacier-filter` in 475.
- Views expose column comments, and injected partition-projection columns accept
  multiple predicates (475). Date partition projection correctly honors
  `partition_projection_format` (477).
- OpenX JSON SerDe partition reads and Regex/OpenX timestamp parsing with
  surrounding spaces were corrected in 475.
- `hive.file-status-cache.excluded-tables` bypasses directory-list caching for
  selected tables (476), and `flush_metadata_cache` works with metastore
  impersonation (478).
- Hive reads Esri JSON, Esri GeoJSON (481), Twitter Elephantbird protobuf,
  `extended_boolean_literal` text data, and OpenCSV with quoting/escaping
  disabled (477). It also reads encrypted Parquet (478) and writes pre-Gregorian
  ORC dates/timestamps compatibly with Apache Hive (478).
- Nanosecond Parquet timestamps can populate `timestamp(p) with time zone`;
  `INSERT` and `ANALYZE` timestamp operations work with Hive Metastore 4 (480).
  Table creation works with Hive Metastore 3.1 (481).
- `hive.parquet.max-split-size` now controls Parquet; `hive.max-split-size`
  controls other formats. Remove `hive.max-initial-splits` and
  `hive.max-initial-split-size` (482).

## Hudi and Lakehouse

- Hudi exposes `parquet.max-read-block-row-count` and session property
  `parquet_max_read_block_row_count` for read-batch sizing (477), and
  `hudi.max-split-size` for split sizing (483).
- The Lakehouse connector was introduced in 477. It shares the native storage,
  Azure timeout, Parquet row-group, and S3 authentication guidance above.
- Lakehouse and Iceberg can read encrypted Parquet-backed Iceberg tables (483).

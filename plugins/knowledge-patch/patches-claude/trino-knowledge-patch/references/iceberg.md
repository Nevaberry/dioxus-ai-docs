# Iceberg

Use this reference for Iceberg catalogs, table properties, metadata tables,
maintenance procedures, v3 tables, and correctness-sensitive operations.

## Metadata tables and inspection

- `$entries` and `$all_entries` are available (469) and handle equality deletes,
  including nested fields (470). `$partition` is a hidden column (472).
- Query `system.iceberg_tables` to list only Iceberg tables (475). `$partitions`
  includes statistics for newly added columns (475).
- `$all_manifests` adds delete-file counts and `reference_snapshot_id` (476).
  `$manifests` and `$all_manifests` add `content` (480).
- `$files` includes `added_snapshot_id` (481). In 482, `lower_bounds` and
  `upper_bounds` changed from `map(integer, varchar)` to typed rows; update
  numeric subscripts and JSON casts.
- Metadata tables such as `$files`, `$snapshots`, and `$partitions` can be queried
  for materialized views (483).

## Table creation, properties, and schema evolution

- Configure Parquet and ORC bloom filters with
  `parquet_bloom_filter_columns` and `orc_bloom_filter_columns` (469).
- Adding dotted column names works (470). New tables record the applicable
  `write.<filetype>.compression-codec` property (473-474).
- `max_commit_retry` configures commit retries (470). Catalog property
  `iceberg.max-partitions-per-writer` maps to session property
  `max_partitions_per_writer` (476).
- `compression_codec` is the table property for the read codec; the session
  property of the same name was removed (477). Tables using
  `write.parquet.compression-codec=LZ4` are readable, and Trino emits a
  spec-compliant `compression-codec` value (480).
- `delete_after_commit_enabled` and `max_previous_versions` control table
  metadata retention (480). The older catalog behavior
  `write.metadata.delete-after-commit.enabled=true` removes the oldest tracked
  version metadata files (469).
- Nested types inside `map` and `array` can be changed with `ALTER ... SET DATA
  TYPE` (480). Altering partition properties preserves existing partition
  columns (480).
- `data_location` no longer requires `object_store_layout_enabled`, and tables
  accept native `write.object-storage.partitioned-paths` (482).
- `target_max_file_size` and `parquet_writer_row_group_size` persist as
  `write.target-file-size-bytes` and `write.parquet.row-group-size-bytes`.
  Their session properties and the deprecated `parquet_writer_block_size` alias
  were removed (482).
- `iceberg.parquet-footer-cache.type` enables footer caching.
  `iceberg.max-split-size` and `max_split_size` replace experimental session
  property `experimental_split_size` (482).
- The old `iceberg.extended-statistics.enabled` config option and
  `extended_statistics_enabled` session property were removed (480).

## Procedures and maintenance

- Use the table-level `rollback_to_snapshot`; `system.rollback_to_snapshot` is
  deprecated (469).
- `optimize_manifests` is available (470), works without an existing snapshot
  (478), and can be used with `EXPLAIN` and `EXPLAIN ANALYZE` (478).
- Partition-filtered `optimize` removes equality-delete files in that partition
  (480). In 483 it fails safely, rather than corrupting a table, if a `NOT NULL`
  column contains nulls.
- `remove_orphan_files` returns live execution metrics (478). `add_files`,
  `add_files_from_table`, and `optimize` expose execution metrics (481), and
  `add_files_from_table` no longer fails on a column-count mismatch (478).
- `expire_snapshots` accepts `retain_last` and `clean_expired_metadata` (479).
- Refreshing an Iceberg materialized view cleans old snapshots (475).

## Catalogs, credentials, and storage placement

- Table metadata can be cached with the Hive metastore (470). Glue catalog IDs
  honor `hive.metastore.glue.catalogid` (475).
- Amazon S3 Tables are supported (471).
- REST catalogs support session timeout and OAuth refresh controls:
  `iceberg.rest-catalog.session-timeout` defaults to `1h`, and
  `iceberg.rest-catalog.oauth2.token-refresh-enabled` defaults to `true`
  (473-474).
- REST catalogs support IAM role authentication (475). Use
  `iceberg.rest-catalog.security=SIGV4`; the separate
  `iceberg.rest-catalog.sigv4-enabled` switch was removed (477).
- `iceberg.rest-catalog.oauth2.token-exchange-enabled` controls OAuth token
  exchange (479).
- REST integration supports BigLake and temporary GCS credentials (480), Azure
  vended credentials, custom HTTP headers, and refreshable S3/GCS/Azure vended
  credentials (481).
- REST catalogs accept prefixed-path storage credentials; both REST and JDBC
  catalogs accept `location` when creating a view (482).
- With `iceberg.rest-catalog.security=GOOGLE`, `gcs.json-key-file-path` is
  optional so Application Default Credentials can be used (483).
- `SHOW CREATE SCHEMA` tolerates unsupported REST, Glue, or Nessie properties
  (478).

## Version 3, variants, and spatial data

- Trino can create, write, delete, and maintain Iceberg v3 tables, including
  column defaults and row lineage. `optimize`, `expire_snapshots`, and
  `remove_orphan_files` support v3 (480).
- The CLI and JDBC client support `variant`, the SPI defines the Iceberg variant
  type, and v3 tables have experimental variant support (481). Older CLI clients
  render variant as JSON. Variant metadata can be up to 128 MB (482).
- V3 tables read and write `timestamp(9)` and `timestamp(9) with time zone`
  (481), plus `geometry` and `geography` (482).

## Concurrency, replacement, and correctness

- `table_changes` no longer returns incomplete results (469). Equality-delete
  metadata works with nested fields (470), and reads after deletes are correct
  (472).
- Concurrent `MERGE` conflict detection and partitioned-writer enforcement of
  `task.max-writer-count` were corrected in 471.
- Avro files migrated from Hive read correctly (478).
- `IS NOT DISTINCT FROM` results are correct (479).
- `CREATE OR REPLACE MATERIALIZED VIEW` preserves data at fixed storage
  locations, and `CREATE OR REPLACE VIEW` preserves custom REST/JDBC catalog
  locations (482).
- Encrypted Parquet-backed tables can be read by Iceberg and Lakehouse (483).

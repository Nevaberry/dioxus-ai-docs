# Spark Integration

## Catalog and table access

`SparkSessionCatalog` supports views as of 1.8.0.

Spark 4.1 manifest metadata tables include key metadata in 1.11.0. Consumers
that inspect manifest rows can use the additional metadata but should remain
compatible with runtimes where it is absent.

## Table path and snapshot actions

### Rewrite table path

Spark adds the `RewriteTablePath` procedure in 1.8.0. In 1.10.0, incremental
table-path rewrite can filter content files by snapshot ID. In 1.11.0,
`RewriteTablePath` also rewrites partition-statistics files.

Treat the path rewrite as an artifact-set operation: do not move ordinary
content and metadata while leaving partition statistics at the old path.

### Snapshot table

`SnapshotTableAction` validates source/destination location overlap in 1.11.0.
An invalid overlapping layout is rejected rather than copied.

## Statistics procedures

Spark adds `ComputeTableStats` in 1.8.0. Iceberg 1.10.0 adds both a Spark
action and a procedure for computing partition statistics.

## Data-file rewrites

The 1.8.0 rewrite-data-files procedure accepts configurable case-sensitive
filtering, and Spark adds a configurable delete-file ratio.

In 1.10.0:

- Core can cap the number of files in a rewrite.
- Incremental table-path rewrite filters content by snapshot ID.
- `RewriteManifest` accepts a custom partition order.
- File-deletion work can disable the executor cache.

The 1.11.0 `rewrite_data_files` procedure can target a branch instead of being
limited to the main branch. Confirm the intended branch before executing the
rewrite.

## Manifest rewrites and orphan removal

`rewrite_manifests` adds a `sort_by` parameter in 1.11.0 for selecting the
order of rewritten manifests.

Spark's remove-orphan-files operation adds `stream-results` in 1.11.0. Use it
when results should be returned incrementally instead of collected into one
response.

## Format-v3 deletes and lineage

Spark can write deletion vectors for format-v3 tables in 1.8.0 and exposes
them through the `position_deletes` metadata table.

In 1.9.0, Spark can rewrite format-v2 deletes as format-v3 deletion vectors.
Readers expose `_row_id` and `_last_updated_sequence_number`.

The 1.10.0 Spark integration adds row-lineage support to Avro and vectorized
Arrow-backed Parquet readers. Spark 4.0 uses conditional nullification for
lineage and preserves lineage during compaction.

## Schema evolution and defaults

Spark reports `ADD COLUMN` with a default value as unsupported in 1.10.0.
Do not assume that core default-value support makes that SQL operation valid.

The `1.11.0-guides` integration can evolve a schema during `MERGE INTO` when
the controlling table property is enabled. Spark schema conversion supports
Iceberg default values in 1.11.0.

## Types and file reads

Spark can use the Comet vectorized Parquet reader with Iceberg tables in 1.8.0,
but the Comet integration is removed from the Spark module in the
`1.11.0-guides` behavior.

In Iceberg 1.8.0, Spark Parquet reads can apply Iceberg defaults. In 1.10.0,
Spark can read dictionary-encoded UUID values and Variant values. The Spark
4.0 integration can read and write the unknown type.

Spark 4.0 and 4.1 can write shredded Variant values in the
`1.11.0-guides` behavior. Both runtimes expose session configuration for
adaptive split sizing.

`SparkZOrderUDF` supports `TimestampNTZ` values in 1.11.0.

## Streaming

`maxRecordPerMicrobatch` is a soft limit starting in 1.10.0. A microbatch can
exceed the configured value; code must not treat it as a strict cap.

## Migration and identifier fields

Spark explicitly rejects migration of bucketed tables in 1.11.0 rather than
attempting an unsupported conversion.

A 1.11.0 table property lets Spark operations explicitly rely on identifier
fields. Enable that reliance only where the operation's identity semantics
match the table definition.

## Procedure review checklist

1. Resolve the table and branch explicitly.
2. Check snapshot filters and case sensitivity.
3. Account for deletion vectors and lineage during file rewrites.
4. Include partition-statistics artifacts during path rewrites.
5. Decide whether manifest order matters.
6. Stream large orphan-removal result sets.
7. Reject bucketed migration and overlapping snapshot destinations early.

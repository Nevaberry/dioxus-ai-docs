# Spark integration

Use this reference for Spark runtime selection, procedures and actions,
format-v3 lineage, Variant handling, streaming, schema evolution, and
rewrite controls.

## Runtime transitions

- Spark 3.3 support is deprecated in Iceberg 1.8.0 and removed in 1.9.0.
- Spark 4.0 support is added in 1.10.0.
- Spark 4.1 support is added and Spark 3.4 is deprecated in
  1.11.0-guides.
- The Apache DataFusion Comet integration is removed from the Spark module in
  1.11.0-guides, after Comet vectorized Parquet reads were supported in
  1.8.0.

Select the Iceberg runtime artifact that matches the deployed Spark runtime;
do not infer compatibility from a nearby Spark minor version.

## Table and metadata procedures

### Table-path rewrites

Spark adds the `RewriteTablePath` procedure in 1.8.0. Incremental table-path
rewrites can filter content files by snapshot ID as of 1.10.0. In 1.11.0,
`RewriteTablePath` also rewrites partition-statistics files along with the
other table artifacts.

### Table and partition statistics

`ComputeTableStats` is available in 1.8.0 for table statistics. Spark adds
both an action and a procedure for partition statistics in 1.10.0. Do not
confuse the general table-statistics procedure with partition-statistics
maintenance.

### Snapshot expiration and orphan removal

Spark `expire_snapshots` accepts `cleanupLevel=None` in 1.11.0 when snapshot
expiration must skip cleanup. Remove-orphan-files adds `stream-results` in
1.11.0 so results can be returned without first collecting them into one
response.

## Data-file and manifest rewrites

The rewrite-data-files procedure gains configurable case-sensitive filtering
in 1.8.0, and Spark adds a configurable delete-file ratio.

Spark can rewrite format-v2 deletes as format-v3 deletion vectors as of
1.9.0.

In 1.10.0:

- Incremental table-path rewrite can filter content files by snapshot ID.
- Data-file rewrite and compaction preserve row lineage.
- Core rewrite facilities can cap file counts; apply the cap when exposed by
  the Spark operation.

In 1.11.0:

- `rewrite_data_files` can target a branch rather than only the table's main
  branch.
- `rewrite_manifests` accepts `sort_by` to choose manifest ordering.

Treat branch, filter, case-sensitivity, delete ratio, file cap, snapshot, and
manifest order as independent controls.

## Row lineage and deletion vectors

Spark writes deletion vectors for format-v3 tables as of 1.8.0 and exposes
them in the `position_deletes` metadata table.

Spark readers expose `_row_id` and `_last_updated_sequence_number` in 1.9.0.
In 1.10.0, Spark adds lineage handling to Avro and vectorized Arrow-backed
Parquet readers. Spark 4.0 uses conditional nullification for lineage and
preserves lineage through compaction.

When upgrading a table to format v3, verify every read and rewrite path used
by the application; lineage is required for upgraded v3 tables too.

## Variant, unknown, UUID, and key metadata

- Spark reads Variant in 1.10.0.
- Spark 4.0 and 4.1 write shredded Variant data in 1.11.0-guides.
- Spark 4.0 reads and writes Iceberg's unknown type in 1.10.0.
- Spark reads dictionary-encoded UUID values in 1.10.0.
- Spark 4.1 manifest metadata tables include key metadata in 1.11.0.

Reader, writer, vectorized, and metadata-table support should be tested
separately.

## Defaults and schema evolution

Spark Parquet reads can materialize Iceberg default values as of 1.8.0.

Spark reports `ADD COLUMN` with a default value as unsupported in 1.10.0.
This engine restriction remains distinct from Iceberg's ability to store and
apply defaults.

In 1.11.0-guides, Spark can evolve schema during `MERGE INTO` when enabled by
a table property. In 1.11.0, Spark schema conversion supports Iceberg default
values.

Use the table property only where schema evolution during merge is intended;
validate the resulting Iceberg schema and defaults after the merge.

## Streaming and split sizing

`maxRecordPerMicrobatch` becomes a soft limit in 1.10.0. A microbatch may
exceed it, so it is unsuitable as a strict memory, latency, or billing guard.

Spark 4.0 and 4.1 expose session configuration for adaptive split sizing in
1.11.0-guides. Apply it at the appropriate session scope and confirm its
effect on the actual scan plan.

## Catalog views

`SparkSessionCatalog` supports views as of 1.8.0. Coordinate its view behavior
with the catalog's view-override property and any REST or Hive view semantics.

## Migration and validation safeguards

Spark explicitly rejects bucketed-table migration in 1.11.0 instead of
attempting an unsupported conversion.

`SnapshotTableAction` validates location overlap in 1.11.0. Source and
destination layouts that overlap invalidly are rejected.

Spark adds a table property in 1.11.0 that lets operations explicitly state
that they rely on identifier fields. Enable reliance only when identifier
fields are defined and the operation is designed around their guarantees.

## Ordering support

`SparkZOrderUDF` supports `TimestampNTZ` values as of 1.11.0. Include these
values in Z-order expressions only on a runtime carrying that support.

## Procedure review checklist

Before executing a Spark maintenance procedure, resolve:

1. Catalog and branch.
2. Snapshot scope and filters.
3. Case sensitivity.
4. Delete-file ratio and deletion-vector handling.
5. File-count and streaming-result controls.
6. Partition or manifest ordering.
7. Cleanup level.
8. Location overlap and identifier-field assumptions.


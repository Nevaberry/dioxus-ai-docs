# Maintenance, statistics, and I/O

Use this reference when expiring snapshots, rewriting files or manifests,
maintaining statistics, selecting Parquet/Avro behavior, or integrating the
pluggable file-format APIs.

## Snapshot expiration and cleanup

Core snapshot expiration can remove unused partition specs as of 1.8.0, and
the Flink integration gains snapshot-expiration support in that batch.

Cleanup becomes explicitly configurable:

- `ExpireSnapshots.cleanExpiredMetadata` in 1.10.0 controls whether expired
  metadata is cleaned.
- Core snapshot expiration exposes `cleanupMode` in 1.11.0.
- Spark `expire_snapshots` accepts `cleanupLevel=None` in 1.11.0 when the
  operation should expire snapshots without performing cleanup.

Choose a cleanup mode deliberately. Expiration, metadata cleanup, orphan-file
deletion, and deletion-vector reconciliation are related operations but not
interchangeable.

## Append and rewrite planning

A single fast append can contain files from multiple partition specs as of
1.8.0. Do not split an append solely because its files use different specs.

Core separates rewrite planning from execution in 1.9.0 with a
`FileRewritePlanner` implementation and distinct planner and runner
interfaces. This permits planning policies and execution mechanics to evolve
independently.

Core adds a cap on the number of files in a rewrite in 1.10.0. That batch also
adds:

- A custom partition order for `RewriteManifest`.
- An option for file-deletion work to disable the executor cache.
- Snapshot-ID filtering for Spark's incremental table-path rewrite.

Manifest rewrites emit an update event and commit metrics as of 1.9.0.
`SnapshotManager` can report metrics through `MetricsReporter`; preserve this
observability when wrapping or scheduling maintenance.

## Deletion-vector-aware maintenance

Starting with the 1.10.0 lifecycle rules, a data-file rewrite must propagate
relevant deletion vectors and remove dangling vectors. Cleanup tracks
affected data files, and partition statistics understand deletion vectors.

For every rewrite plan:

1. Identify rewritten data files and their deletion vectors.
2. Preserve applicable vectors for surviving data or translate them according
   to the rewrite.
3. Remove vector files that no longer reference live content.
4. Refresh affected statistics.
5. Include vector files in orphan-prevention and cleanup validation.

## Partition and content statistics

Core gains readers and writers for partition statistics in 1.9.0.

In 1.10.0:

- Partition statistics can be refreshed incrementally.
- Core corrects the field IDs written to partition-statistics files.
- Spark provides both an action and a procedure for computing partition
  statistics.
- Partition statistics account for deletion vectors.

In 1.11.0-guides:

- The Content Stats API exposes file-level values such as bounds and null
  counts.
- A composable, filterable Partition Stats Scan API replaces the single-shot
  reader.
- Table registration can explicitly overwrite.
- Statistics scans can expose their `FileIO`.

In 1.11.0, `RewriteTablePath` includes partition-statistics files when
rewriting table artifacts.

## Metrics bounds

Iceberg 1.10.0 preserves the original value type of lower and upper metrics
bounds. For special geo objects, follow the specification's clarified bound
behavior. Consumers should not coerce a bound to a generic representation
that loses its original type.

## Parquet statistics and writer configuration

A 1.10.0 table property can use a column prefix to enable Parquet column
statistics only for selected columns. Use this to balance pruning information
against statistics size for wide schemas.

Parquet writers can select their page version through
`write.parquet.page-version` as of 1.11.0.

Generic Parquet writes can configure Variant shredding through
`Parquet.DataWriteBuilder.variantShreddingFunc()` as of 1.11.0.

## Vectorized and Arrow-backed Parquet reads

The Arrow-backed Parquet readers in 1.10.0 add:

- Table format-v2 coverage.
- `DELTA_BINARY_PACKED` support.
- Nanosecond-timestamp support.

Spark can read dictionary-encoded UUID values in that batch. Parquet uses the
Variant logical annotation from Parquet 1.16.0.

Vectorized Parquet reads add `DELTA_LENGTH_BYTE_ARRAY`, `DELTA_BYTE_ARRAY`,
and `BYTE_STREAM_SPLIT` encodings in 1.11.0. Select a vectorized path only
after confirming that every encoding produced by the writer is supported.

## Avro reads

Parquet and Avro readers can apply Iceberg default values as of 1.8.0. Core
Avro readers additionally accept Avro's `timestamp-millis` logical type as of
1.11.0.

## Pluggable File Format API

The 1.11.0-guides batch introduces `FormatModel`, which describes a file
format's identifier, readers, writers, configuration, and capabilities.
`FormatModelRegistry` decouples engines from registered Parquet, ORC, Avro,
Arrow, and future implementations.

Core operations include:

```java
FormatModelRegistry.register(FormatModel)
FormatModelRegistry.readBuilder(fileFormat, clazz, inputFile)
FormatModelRegistry.dataWriteBuilder(fileFormat, clazz, outputFile)
FormatModelRegistry.equalityDeleteWriteBuilder(fileFormat, clazz, outputFile)
FormatModelRegistry.positionDeleteWriteBuilder(fileFormat, clazz, outputFile)
```

The API and generic-engine integrations are complete in that batch, but the
compatibility test kit is still in progress. A custom format implementation
must therefore validate every advertised capability directly rather than
relying on a complete common conformance suite.

## Operational verification

After maintenance:

- Confirm the active snapshot and referenced manifests.
- Confirm unused partition specs and expired metadata match the selected
  cleanup mode.
- Check that deletion vectors and rewritten data files have no dangling
  references.
- Read partition-statistics files with the corrected schema and field IDs.
- Verify metrics events reached the configured reporter.
- Exercise each Parquet encoding and logical type that production writers
  emit.


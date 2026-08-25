# Flink and Kafka integrations

Use this reference for Flink runtime compatibility, sinks, maintenance,
lineage and type handling, plus Kafka Connect ingestion and commit safety.

## Flink runtime support

- Iceberg 1.10.0 adds Flink 2.0 support and removes Flink 1.18 support.
- The 1.11.0-guides batch adds Flink 2.1 support and removes Flink 1.19.

Use the matching Iceberg Flink runtime artifact and validate state/savepoint
compatibility when changing engine versions.

## Catalog, SQL, and watermarks

The Flink catalog supports `CREATE TABLE LIKE` as of 1.9.0. Flink SQL can use
source watermarks in window operations in the same batch.

Flink maintenance options and Dynamic Sink options become configurable from
SQL in later updates. Keep SQL configuration aligned with equivalent builder
settings rather than defining conflicting behavior in both places.

## Defaults, timestamps, unknown values, and UUID

- Flink Parquet reads apply Iceberg defaults as of 1.8.0.
- Flink Avro and Parquet paths support `timestamp(9)` and unknown values as of
  1.9.0.
- The Flink Avro path adds default-value support in 1.9.0.
- Flink 2.1 adds Variant and nanosecond-timestamp support in
  1.11.0-guides.
- Flink 2.1 Avro and Parquet readers and writers add UUID support in
  1.11.0-guides.

Confirm both serialization directions for every type; a reader capability
does not imply the corresponding writer path exists.

## Row lineage

Flink can read `_row_id` and `_last_updated_sequence_number` as of
1.11.0-guides and preserves them through `RewriteDataFiles`.

Because lineage is mandatory for format-v3 tables, check ordinary reads,
rewrites, compaction, and sink writes before upgrading a Flink-managed table
to v3.

## Dynamic Sink

The Flink Dynamic Sink introduced in 1.10.0 can:

- Handle dynamic schema evolution.
- Handle dynamic partition evolution.
- Fan writes out across multiple tables.
- Create tables as needed.

The 1.11.0-guides extensions add:

- Deletion-vector writes.
- Column drops.
- Case-insensitive field matching.
- SQL-configurable options.
- Arbitrary post-commit maintenance tasks registered through the
  `IcebergSink` builder.

Guard automatic table creation and column dropping with catalog authorization
and schema policy. Choose case-insensitive matching explicitly because it can
change how ambiguous field names resolve.

## IcebergSink v2

The `IcebergSink` v2 writer defaults task parallelism to the input stream's
parallelism as of 1.10.0. It also supports compaction, data-file rewrites, and
range distribution.

Do not assume the default parallelism is optimal for file size or downstream
commit pressure; override it where workload sizing requires a different
writer topology.

Flink writers add `uid-suffix` in 1.11.0 to prevent operator UID hash
collisions. Use stable, unique suffixes where multiple Iceberg writers would
otherwise derive the same identity.

## Table maintenance

Flink gains snapshot-expiration support in 1.8.0.

In 1.10.0, Flink table maintenance supports:

- ZooKeeper locking.
- Orphan-file deletion.
- Filters on `RewriteDataFiles`.

In 1.11.0-guides, maintenance gains:

- A coordinator lock, configurable from Flink SQL.
- Dynamic filters for `RewriteDataFiles`.
- Branch-specific maintenance.

Choose one coherent lock strategy for each table and deployment. Scope
orphan deletion and rewrite filters carefully, and pass the intended branch
through every task rather than defaulting silently to main.

## Kafka Connect prefixes and transforms

Kafka Connect adds configuration for the control consumer-group prefix in
1.8.0.

In 1.9.0, it adds:

- Single-message transforms for Debezium records.
- Single-message transforms for AWS DMS records.
- Configuration for the transactional-ID prefix.

Make these prefixes unique enough for the deployment and use the transforms
that match the source record envelope before Iceberg schema conversion.

## Kafka Connect Variant and identity safety

The 1.11.0-guides batch lets Kafka Connect ingest semi-structured JSON
directly into Iceberg Variant columns.

Kafka Connect also validates the table UUID at commit time. This prevents an
in-flight writer from committing to a stale or replaced table that happens to
reuse the same catalog identifier. Treat a UUID mismatch as a table-identity
failure requiring reload and reassessment, not as a transient commit retry.

## Operational checklist

1. Match the Flink runtime artifact to the deployed engine.
2. Assign stable writer UIDs and appropriate parallelism.
3. Verify type behavior in both Avro and Parquet paths.
4. Test lineage across reads, rewrites, and sink commits.
5. Authorize Dynamic Sink table creation and destructive schema evolution.
6. Configure a single effective maintenance lock and explicit branch.
7. Give Kafka control groups and transactions collision-resistant prefixes.
8. Stop and reload on Kafka table-UUID mismatch.


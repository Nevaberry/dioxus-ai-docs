# Flink, Kafka Connect, and Streaming Ingestion

## Flink source and catalog behavior

The Flink catalog supports `CREATE TABLE LIKE` as of 1.9.0. Flink SQL can use
source watermarks in window operations.

Flink gains snapshot-expiration support in 1.8.0.

## Flink type and schema support

Flink Parquet reads apply Iceberg defaults in 1.8.0.

In 1.9.0, the Flink Avro and Parquet paths support `timestamp(9)` and unknown
values. The Flink Avro path also supports Iceberg default values.

The `1.11.0-guides` behavior adds these Flink capabilities:

- Readers expose `_row_id` and `_last_updated_sequence_number`.
- `RewriteDataFiles` preserves lineage.
- Flink 2.1 supports Variant and nanosecond timestamps.
- Flink Avro and Parquet readers and writers support UUID values.

## Dynamic Sink

The 1.10.0 Flink Dynamic Sink:

- Handles dynamic schema evolution.
- Handles dynamic partition evolution.
- Fans writes out across multiple tables.
- Creates tables when needed.

The `1.11.0-guides` extensions add:

- Deletion-vector writes.
- Column drops.
- Case-insensitive field matching.
- Options configurable through Flink SQL.
- Arbitrary post-commit maintenance tasks registered through the
  `IcebergSink` builder.

When enabling automatic table creation or evolution, validate table identity
and the incoming schema before the fan-out write.

## IcebergSink v2

In 1.10.0, the `IcebergSink` v2 writer defaults task parallelism to the input
stream's parallelism. It supports compaction, data-file rewrites, and range
distribution.

Do not assume a fixed default parallelism independent of the upstream stream.

## Flink table maintenance

The 1.10.0 maintenance integration supports ZooKeeper locking and orphan-file
deletion. `RewriteDataFiles` accepts filters.

The `1.11.0-guides` behavior adds a coordinator lock, including configuration
from Flink SQL. `RewriteDataFiles` accepts a dynamic filter, and maintenance
can target a specific branch.

Choose the locking mechanism and branch deliberately so two maintenance jobs
do not rewrite the same table state concurrently.

## Stable operator identities

Flink writers add the `uid-suffix` option in 1.11.0. Use distinct suffixes to
prevent operator UID hash collisions when otherwise-similar writers occur in
the same job graph.

## Kafka Connect controls

### Consumer and producer identity

Kafka Connect adds a control consumer-group prefix setting in 1.8.0. In 1.9.0
it adds configuration for the transactional-ID prefix.

Set these prefixes to keep independently deployed connectors from colliding in
shared Kafka infrastructure.

### Record transforms

The 1.9.0 integration adds single-message transforms for Debezium and AWS DMS
records.

### Variant ingestion and table identity

In the `1.11.0-guides` behavior, Kafka Connect can ingest semi-structured JSON
directly into Iceberg Variant columns. It also validates the table UUID at
commit time, preventing a connector from committing to a stale or replaced
table identity.

Do not bypass the table-UUID check when catalog entries may be dropped and
recreated under the same name.

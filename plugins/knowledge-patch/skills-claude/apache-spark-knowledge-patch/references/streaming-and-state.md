# Structured Streaming and state

Use this reference for trigger behavior, checkpoint compatibility, stateful
operators, state inspection, stream joins, real-time processing, and Python
streaming data sources.

## Trigger and execution behavior

### `AvailableNow` fallback (4.0-migration)

An `AvailableNow` query falls back to single-batch execution if any source does
not support `Trigger.AvailableNow`. Relative `DataStreamWriter` output paths
are resolved on the driver rather than executors.

### Kafka retry correctness (3.5.7)

Retrying an uncommitted Kafka source batch with an `AvailableNow` trigger no
longer enters a crash loop.

### Stateless AQE (4.1-migration)

Adaptive Query Execution is supported and enabled by default for stateless
Structured Streaming. It can change partitioning and skew handling after an
upgrade. Disable it with
`spark.sql.adaptive.streaming.stateless.enabled=false` when compatibility or a
regression requires the earlier execution plan.

### Real-time mode (4.1.0, 4.2.0)

Structured Streaming's first official real-time mode targets continuous
sub-second processing for stateless Scala queries (4.1.0). PySpark adds a
real-time-mode trigger in 4.2.0.

### Stream-stream joins (4.2.0)

Non-outer stream-stream joins can run in Update mode. Stream-stream join state
format V4 is supported.

## Checkpoints

### Checkpoint deletion headroom (4.0-migration)

`spark.sql.streaming.ratioExtraSpaceAllowedInCheckpoint` defaults to `0.3`,
leaving extra space for stale version files awaiting batched deletion. Set it
to `0` for the former behavior.

### Metadata verification (4.2-migration)

Restarting from a checkpoint that contains offset or commit logs but lacks a
metadata file fails with `STREAMING_CHECKPOINT_MISSING_METADATA_FILE`. This
prevents an unnoticed new query ID and possible duplicate writes. Restore the
metadata file, use a new checkpoint, or temporarily set
`spark.sql.streaming.checkpoint.verifyMetadataExists.enabled=false`.

### Stable source and sink identity (4.2.0)

`DataStreamReader.name()` and SQL `IDENTIFIED BY` give sources stable
identities. Sources can then be added, removed, or reordered without
invalidating checkpoints. Streaming sinks also have `.name()`, persisted in
the V3 commit log. Keep these names stable once deployed.

## TransformWithState

### Arbitrary state API v2 (4.0.0)

`TransformWithState` supports multiple state variables and column families,
batch execution, initial state, timers, and Avro-backed schema evolution.
Python has value, list, and map state; timer handling; list-state TTL; operator
chaining; and batch `TransformWithStateInPandas`.

### Nested Python state (4.0.1)

Python value state supports composite and nested `StructType` values.

### Row-based Python state and joins (4.1.0)

Python adds row-based `transformWithState`. Stream-stream joins can use virtual
column families, including through the state data-source reader.

## State inspection and resilience

### State data source (4.0.0)

The state data source can read snapshots, change feeds, operator metadata,
registered timers, and value, list, or map state. Snapshot start batch and
partition options and collection-flattening options refine these reads.

### Trigger and RocksDB controls (4.0.0)

Streaming adds `maxBytesPerTrigger`, RocksDB compression controls, and a switch
to disable `fallocate` selectively.

### Iterator lifecycle (4.0.1)

RocksDB state-store iterators expose an explicit close API. Close iterators to
release resources deterministically.

### Snapshot repair and checksums (4.2.0)

State stores can repair snapshots automatically and record row checksums for
corruption detection. Snapshot upload on lag is enabled by default, forcing
the next commit to create a snapshot for both RocksDB and HDFS providers.

## Python streaming data sources

### Writers and registration (4.0.0, 4.1.0)

Python data sources support Data Source V2 table creation and writes,
Arrow-based writers, metrics, and session-scoped registration (4.0.0). They
add filter pushdown, an Arrow writer for streaming sources, and overwrite of a
statically registered Python data source in 4.1.0.

### Reader capabilities (4.2.0)

Python data-source readers support admission control and
`Trigger.AvailableNow`.

### Offset advancement requirement (4.2-migration)

`SimpleDataSourceStreamReader.read()` fails with
`SIMPLE_STREAM_READER_OFFSET_DID_NOT_ADVANCE` if it returns a non-empty batch
without moving the end offset past the start. The reader must advance the end
offset beyond the final emitted record.

### Arrow schema enforcement (4.2-migration)

A Python data source fails with `DATA_SOURCE_RETURN_SCHEMA_MISMATCH` when its
Arrow column types differ from its declared schema. This extends the existing
column-count and column-name validation.

## CDC in streaming workloads

Data Source V2 `CHANGES` and `changes()` reads work in batch and streaming,
including streaming `netChanges` (4.2.0). Declarative Pipelines adds Auto CDC
flows for streaming SCD Type 1 upserts; see the pipelines reference for its
client APIs.

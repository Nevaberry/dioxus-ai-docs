# Structured Streaming and State

## Trigger and execution behavior

- `AvailableNow` falls back to a single batch when any source lacks native
  `Trigger.AvailableNow` support (`4.0-migration`).
- Relative `DataStreamWriter` output paths resolve on the driver rather than
  executors.
- Retrying an uncommitted Kafka batch under `AvailableNow` no longer enters a
  crash loop (`3.5.7`).
- AQE is supported and enabled by default for stateless streaming
  (`4.1-migration`). Disable
  `spark.sql.adaptive.streaming.stateless.enabled` when fixed planning is
  required.
- Spark `4.1.0` introduces official stateless real-time mode for Scala,
  targeting continuous sub-second processing.
- PySpark adds a real-time-mode trigger in `4.2.0`.
- Non-outer stream-stream joins can use Update mode, and stream-stream joins
  support state format V4.

## TransformWithState v2

The `4.0.0` arbitrary-state API supports:

- multiple state variables and column families;
- batch execution and initial state;
- timers;
- Avro-backed schema evolution;
- Python value, list, and map state;
- Python timer handling and list-state TTL;
- operator chaining; and
- batch `TransformWithStateInPandas`.

Composite and nested `StructType` values work correctly in Python value state
as of `4.0.1`.

Spark `4.1.0` adds a row-based Python `transformWithState` API. Stream-stream
joins can use virtual column families, including when inspected with the state
data-source reader.

## State inspection

The state data source can read:

- snapshots and change feeds;
- operator metadata;
- registered timers;
- value, list, and map state; and
- selected snapshot start batches and partitions.

Collection-flattening options refine state reads. Use these inspection paths
to validate schema evolution and timer behavior before resuming a copied
checkpoint.

## Checkpoint safety and identity

- `spark.sql.streaming.ratioExtraSpaceAllowedInCheckpoint` defaults to `0.3`
  in the 4.0 migration, allowing stale version files to await batched deletion.
- Restarting a checkpoint with offset or commit logs but no metadata file fails
  with `STREAMING_CHECKPOINT_MISSING_METADATA_FILE` in `4.2-migration`.
  Restore metadata or choose a new checkpoint. Disabling
  `spark.sql.streaming.checkpoint.verifyMetadataExists.enabled` restores the
  old behavior but can create a new query ID and duplicate writes.
- `DataStreamReader.name()` and SQL `IDENTIFIED BY` provide stable source
  identity in `4.2.0`, allowing sources to be added, removed, or reordered
  without invalidating checkpoints.
- Streaming sinks gain `.name()`, stored in the V3 commit log.

## Source controls

- Streaming adds `maxBytesPerTrigger` in `4.0.0`.
- Python data-source readers gain admission control and
  `Trigger.AvailableNow` in `4.2.0`.
- `SimpleDataSourceStreamReader.read()` fails with
  `SIMPLE_STREAM_READER_OFFSET_DID_NOT_ADVANCE` when it returns a non-empty
  batch without moving the end offset past the start.
- Data Source V2 CDC reads work in both batch and streaming, including
  streaming `netChanges`.

## State-store lifecycle and resilience

- RocksDB state-store iterators have an explicit close API (`4.0.1`); close
  them deterministically.
- `RemoveFiles` shuffle cleanup works when AQE is disabled.
- RocksDB compression and selective `fallocate` disabling are configurable in
  `4.0.0`.
- State stores can repair snapshots automatically and record row checksums for
  corruption detection (`4.2.0`).
- Snapshot upload on lag defaults on. The next commit forces a snapshot for
  both RocksDB and HDFS state-store providers.

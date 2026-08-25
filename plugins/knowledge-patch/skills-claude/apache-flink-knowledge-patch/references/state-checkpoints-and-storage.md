# State, Checkpoints, and Storage

Use this reference for async state, serializer/state compatibility, savepoint
inspection, checkpoint recovery, RocksDB/ForSt behavior, and native S3.

Batch attribution: `2.0-migration`, `2.0.0`, `1.20.3`, `2.0.1`,
`2.1-migration`, `2.0.2`, `2.2.1`, `2.3-migration`, `2.3.0`.

## Disaggregated and asynchronous state

- Flink 2.0 introduces remote primary state storage, an asynchronous execution
  model, a disaggregated state backend, and SQL operators that access state
  asynchronously in parallel.
- DataStream `process()` operators support async state access as of 2.0.1.
- ForSt supports `GROUP BY` operators using asynchronous state execution as of
  2.0.2; earlier affected jobs fail in that combination.
- DataStream V2 state lookup returns V2 state objects directly rather than an
  `Optional` wrapping legacy state. See the migration reference for each state
  family and broadcast-state behavior.
- A SQL connector can inspect keyed state directly from checkpoints and
  savepoints for debugging and migration validation without custom tooling.

## State compatibility and removed surfaces

- Built-in `Map`, `List`, and `Set` serializers are enabled by default, and
  Kryo is upgraded to 5.6. Never assume a 1.x state/savepoint restores
  unchanged on 2.x.
- Serializer compatibility is snapshot-to-snapshot; custom snapshots must
  implement `resolveSchemaCompatibility(TypeSerializerSnapshot<T>)`.
- Legacy memory/filesystem state backend classes and the State Processor API's
  savepoint reader/writer surface are removed, as are many programmatic
  checkpoint/environment setters and simple savepoint-trigger/stop overloads.

## Unaligned checkpoint scope and recovery

- Expanded sink topologies disable unaligned checkpoints on every internal
  pre-commit, committer, and post-commit connection so committables exist when
  `notifyCheckpointComplete` runs.
- This does not justify disabling unaligned checkpoints across all job
  connections. That broad 2.0 regression is corrected in 2.0.1.
- Recovery from an unaligned checkpoint after rescaling works when a task has
  multiple exchanges (fixed in 1.20.3).
- Data sent through a custom partitioner is preserved under unaligned
  checkpointing as of 2.2.1; earlier affected versions could corrupt it.
- Flink 2.3 can checkpoint while restored channel state is still being
  consumed, avoiding a full replay after another restart or rescale. This is
  disabled by default and requires both:

```yaml
execution.checkpointing.unaligned.recover-output-on-downstream.enabled: true
execution.checkpointing.unaligned.during-recovery.enabled: true
```

## Commit and checkpoint durability fixes

- In 1.20.3, `GlobalCommitterOperator` commits correctly after writer or
  committer scaling, and `CommitterOperator` includes pending committables in
  checkpoints.
- File-merged checkpoint recovery no longer hits the affected failover NPE,
  and lost RPC messages no longer cause the file-merging manager to delete its
  directory unexpectedly (1.20.3).
- `SinkWriter` no longer mistakes rescaling for end of input. State Processor
  API jobs using an exactly-once Kafka sink no longer fail with
  `InvalidPidMappingException` (2.0.1).
- Delayed checkpoint notification no longer reuses SST files that have since
  been re-uploaded (2.0.2).

## RocksDB and ForSt

- RocksDB null serialization is symmetric and no longer raises the affected
  null-pointer (1.20.3).
- Native RocksDB compaction threads can use the user class loader for state
  TTL. `rocksdb.use-ingest-db-restore-mode` no longer intermittently throws
  `IndexOutOfBoundsException` during restore (2.0.1).
- ForSt copying honors `maxTransferBytes`, removes half-uploaded checkpoint
  files, and preserves pre-existing directories (2.0.1).
- Tiered Storage works with Buffer Debloating enabled (2.0.1).

## Native S3 filesystem

- `flink-s3-fs-native` is an AWS SDK v2-based plugin that avoids Hadoop and
  Presto dependencies. Put it in the plugins directory.
- It provides `FileSystem` and `RecoverableWriter` implementations for
  exactly-once streaming sinks and supports modern authentication, including
  IAM Roles for Service Accounts.
- Configure `s3.region`, `s3.endpoint`, `s3.path-style-access`,
  `s3.access-key`, `s3.secret-key`, `s3.upload.min.part.size`,
  `s3.upload.max.concurrent.uploads`, `s3.bulk-copy.enabled`,
  `s3.async.enabled`, `s3.read.buffer.size`, and `s3.entropy.key`, plus the
  SSE-KMS, chunked-encoding, and checksum-validation controls.
- The plugin registers `s3://` and `s3a://`. It is functionally complete but
  still experimental in 2.3.0.

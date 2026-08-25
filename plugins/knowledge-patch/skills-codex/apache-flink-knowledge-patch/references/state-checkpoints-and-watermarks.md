# State, Checkpoints, and Watermarks

## State architecture and async access (`2.0-migration`)

Flink 2.0 introduces remote storage as primary state storage, asynchronous
execution, a disaggregated backend, and SQL operators that perform asynchronous
state access in parallel. This architectural change does not imply automatic
state compatibility with Flink 1.x: new collection serializers and Kryo 5.6 are
enabled, while compatibility for existing state and savepoints is not guaranteed.

## Async state follow-up fixes

- DataStream `process()` operators support async state access in Flink 2.0.1.
  User async-function timeout callbacks no longer trigger unintended retries
  (`2.0.1`).
- ForSt supports `GROUP BY` operators using async state execution without the
  prior backend error in Flink 2.0.2 (`2.0.2`).

## Local recovery and adaptive scheduling (`2.0-migration`)

Adaptive Scheduler local recovery is controlled by
`execution.state-recovery.from-local`, default `false`. Enable it explicitly when
task-local recovery is required:

```yaml
execution.state-recovery.from-local: true
```

`jobmanager.adaptive-scheduler.executing.resource-stabilization-timeout`
controls how long the JobManager waits after resource changes before scaling.
`jobmanager.adaptive-scheduler.min-parallelism-increase` is deprecated.

## Sink checkpoint topology (`2.0-migration`, `2.0.1`)

Flink disables unaligned checkpoints on connections inside a sink's expanded
pre-commit, committer, or post-commit topology. This ensures committables exist
when `notifyCheckpointComplete` runs. Flink 2.0.1 fixes a regression that disabled
unaligned checkpoints on every connection; unrelated eligible connections keep
the feature.

## Commit and exactly-once correctness

- Flink 1.20.3 fixes `GlobalCommitterOperator` failing to commit after writer or
  committer scaling and `CommitterOperator` omitting pending committables from
  checkpoints (`1.20.3`).
- Flink 2.0.1 prevents `SinkWriter` from inferring end-of-input during rescaling.
  State Processor API jobs with an exactly-once Kafka sink also avoid
  `InvalidPidMappingException` (`2.0.1`).
- Flink 2.2.1 prevents custom-partitioned data corruption with unaligned
  checkpointing (`2.2.1`).

## Recovery and file handling

### Flink 1.20.3 repairs (`1.20.3`)

- Unaligned-checkpoint recovery works after rescaling when one task has multiple
  exchanges.
- File-merged checkpoints no longer hit a recovery-time NPE after failover.
- Lost RPC messages no longer cause the checkpoint file-merging manager to
  delete its directory unexpectedly.
- RocksDB serializes and deserializes null state consistently instead of
  throwing an NPE or applying asymmetric logic.

### Flink 2.0.x repairs (`2.0.1`, `2.0.2`)

- Tiered Storage works with Buffer Debloating.
- ForSt copies paths with `maxTransferBytes`, removes half-uploaded checkpoint
  files, and preserves a directory that already existed.
- RocksDB native compaction threads have the user class loader for state TTL,
  and `rocksdb.use-ingest-db-restore-mode` avoids an intermittent restore
  `IndexOutOfBoundsException`.
- A delayed checkpoint notification no longer reuses SST files that have since
  been re-uploaded.

## Checkpoint during unaligned recovery (`2.3-migration`)

Flink can preserve progress while restored channel state is still being
consumed, reducing replay after another restart or rescale. It is disabled by
default and requires both options:

```yaml
execution.checkpointing.unaligned.recover-output-on-downstream.enabled: true
execution.checkpointing.unaligned.during-recovery.enabled: true
```

## Idleness and input activity (`2.0-migration`)

Watermark idleness excludes time in which a source or split is backpressured or
blocked by watermark alignment. This avoids premature idle status and erroneous
late data. Custom generators can use the same activity clock through
`WatermarkGeneratorSupplier.Context#getInputActivityClock()`.

## Split-level watermark metrics (`2.1-migration`)

Each source split exposes:

- `currentWatermark`;
- per-second `activeTimeMsPerSecond`, `pausedTimeMsPerSecond`, and
  `idleTimeMsPerSecond` gauges;
- cumulative `accumulatedActiveTimeMs`, `accumulatedPausedTimeMs`, and
  `accumulatedIdleTimeMs` gauges.

Paused time is time stopped by watermark alignment; idle time is time classified
by idleness detection.

## Watermark fixes and buffering

- A custom `WatermarkStrategy` can use `MetricGroup` without a stack overflow,
  and alignment no longer deadlocks after no more source splits remain to assign
  (`2.0.1`).
- Flink 2.3 delays the alignment pause decision by
  `pipeline.watermark-alignment.buffer-size` update intervals. Its default `3`
  improves backlog processing at the cost of slightly later pauses and modestly
  more operator state. Set it to `0` for the Flink 2.2 timing
  (`2.3-migration`).

## State inspection (`2.1-migration`)

A SQL connector can query keyed state directly from checkpoints and savepoints.
Use it for state inspection, debugging, and migration validation without custom
state-reading tools.

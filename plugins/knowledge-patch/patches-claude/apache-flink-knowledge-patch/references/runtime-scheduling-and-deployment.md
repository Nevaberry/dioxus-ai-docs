# Runtime, Scheduling, and Deployment

Use this reference for schedulers, resources, partitioning, watermarks,
Kubernetes/YARN, application lifecycle, REST contracts, and the Web UI.

Batch attribution: `1.20.1`, `2.0-migration`, `1.20.2`, `1.20.3`, `2.0.1`,
`2.2-migration`, `1.20.4`, `2.3-migration`, `2.3.0`.

## Classpath and deployment migration

- Flink 1.20.1 follows symlinks in `usrlib`, so linked files participate in
  user-library loading.
- Per-job deployment is removed in 2.0. Use application mode. SQL Gateway can
  execute SQL jobs in that mode.
- Kubernetes application submission uses
  `flink run -t kubernetes-application`; the `run-application` action is gone.
- Native Kubernetes starts jobs whose JAR is on the system classpath as of
  2.0.1. The embedded-mode SQL Client deployment script also avoids the
  affected Kubernetes `FileNotFoundException`.
- `flink run -sae` no longer kills the submitted task on the 1.20 line after
  the 1.20.3 fix.
- Python CLI arguments work for session-mode submission as of 1.20.4; see the
  connector/Python reference for packaged environments.

## Adaptive Scheduler and TaskManagers

- Adaptive Scheduler local recovery follows
  `execution.state-recovery.from-local`, default `false`. Set it to `true`
  when task-local recovery is required.
- `jobmanager.adaptive-scheduler.executing.resource-stabilization-timeout`
  controls the delay after a resource change while sufficient resources
  stabilize. `jobmanager.adaptive-scheduler.min-parallelism-increase` is
  deprecated.
- On Kubernetes, downscaling prefers maximum TaskManager utilization and thus
  fewer active TaskManagers by default as of 1.20.2. Set
  `jobmanager.adaptive-scheduler.prefer-minimal-taskmanagers: false` to retain
  the earlier strategy.
- A balanced scheduling strategy can spread task load across TaskManagers to
  reduce bottlenecks.
- The 1.20.4 failover fix prevents slot reallocation from launching extra
  TaskManagers and releasing a wanted TaskManager as failed.

## Network partitioning and batch edges

- The adaptive partitioner is opt-in through
  `taskmanager.network.adaptive-partitioner.enabled` (default `false`). It
  selects the least-loaded downstream channel when a subtask is slow.
- `taskmanager.network.adaptive-partitioner.max-traverse-size` controls how
  many channels are examined and defaults to `4`.
- Adaptive target selection applies to both `RebalancePartitioner` and
  `RescalePartitioner` in 2.3.0.
- Batch jobs with broadcast edges in their `JobGraph` execute correctly, and
  binary shuffle keys route records correctly after the 2.0.1 fixes.

## Watermarks, idleness, and source assignment

- Idleness does not count time when a source or split is backpressured or
  blocked by watermark alignment. This prevents premature idle marking and
  false late data. Custom generators can use
  `WatermarkGeneratorSupplier.Context#getInputActivityClock()`.
- Watermark alignment no longer deadlocks when no more splits remain to assign
  (fixed in 2.0.1). A custom `WatermarkStrategy` can use `MetricGroup` without
  stack overflow.
- Watermark alignment delays its pause decision by
  `pipeline.watermark-alignment.buffer-size` update intervals. The default `3`
  improves backlog processing at the cost of a slightly later pause and
  modestly more operator state; `0` restores the 2.2 behavior.
- Split enumerators can inspect current runtime split distribution and rebalance
  assignments while running.

## Kubernetes, YARN, and containers

- On dual-network YARN deployments, explicit `rest.bind-address` is honored as
  of 1.20.4.
- Affected Kubernetes deployment resources are released rather than leaked as
  of 1.20.4.
- Docker images use the Dockerfile `USER` instruction instead of `gosu` as of
  1.20.4. Update derived images and entrypoints that invoked or depended on
  `gosu`.

## Applications as lifecycle resources

- Flink applications can contain multiple batch jobs and are visible in an
  Applications Web UI. Incomplete session-mode applications can re-execute
  during HA recovery.
- REST supports `GET /applications/overview`,
  `GET /applications/:applicationid`,
  `POST /applications/:applicationid/cancel`, and asynchronous submission via
  `POST /jars/:jarid/run-application`.
- Application REST data includes failures and JobManager configuration.
- `execution.terminate-application-on-any-job-terminated-exceptionally`
  defaults to `true`; `cluster.id` defaults to an all-zero UUID.
- `historyserver.archive.clean-expired-applications` defaults to `false`, and
  `historyserver.archive.retained-applications` defaults to `-1`.

## REST and Web UI compatibility

- TaskManager REST responses no longer contain
  `metrics.memorySegmentsAvailable` or `metrics.memorySegmentsTotal`.
- `/jobs/:jobid/config` no longer returns `execution-mode`; vertex, subtask,
  and TaskManager response families no longer expose `host`.
- The internal `/jars/:jarid/run` `claimMode` and `restoreMode` type is
  `RecoveryClaimMode`; their JSON representation is unchanged.
- Set `web.adaptive-scheduler.rescale-history.size` above default `0` to retain
  per-job rescale records. They include vertex parallelism, slot allocation,
  scheduler transitions, and termination reasons.
- Rescale data appears in the Web UI **Rescales** tab and at
  `/jobs/:jobid/rescales/overview`, `/history`, `/details/:rescaleuuid`, and
  `/summary` beneath the same job rescale path.
- Job-graph nodes remain clickable in Chrome 144 and later. Job overview
  business, backpressure, and skew metrics no longer show `N/A` solely because
  some nodes have finished (1.20.4).

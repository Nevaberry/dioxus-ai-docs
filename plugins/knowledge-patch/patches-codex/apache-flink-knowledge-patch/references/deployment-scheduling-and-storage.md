# Deployment, Scheduling, and Storage

## Application deployment

### Flink 2.0 application mode (`2.0-migration`)

Per-job deployment is removed. Use application mode, including for SQL Gateway
jobs. On Kubernetes, submit with:

```bash
flink run -t kubernetes-application ...
```

The old `run-application` action and legacy Hybrid Shuffle mode are removed.

### First-class applications (`2.3-migration`)

Flink introduces a cluster-application-job hierarchy. Applications can contain
multiple batch jobs, and incomplete session-mode applications can be re-executed
during HA recovery. The lifecycle surface includes:

- `GET /applications/overview`;
- `GET /applications/:applicationid`;
- `POST /applications/:applicationid/cancel`;
- asynchronous `POST /jars/:jarid/run-application` submission;
- an Applications Web UI, application failures, and JobManager configuration.

Defaults to account for:

- `execution.terminate-application-on-any-job-terminated-exceptionally: true`;
- `cluster.id`: an all-zero UUID;
- `historyserver.archive.clean-expired-applications: false`;
- `historyserver.archive.retained-applications: -1`.

## Adaptive Scheduler and resource placement

### Downscaling and stabilization (`1.20.2`, `2.0-migration`)

On Kubernetes, Flink 1.20.2 makes Adaptive Scheduler downscaling prefer maximum
TaskManager utilization so fewer TaskManagers remain active. Preserve the
earlier strategy with:

```yaml
jobmanager.adaptive-scheduler.prefer-minimal-taskmanagers: false
```

`jobmanager.adaptive-scheduler.executing.resource-stabilization-timeout` controls
the delay after a resource change while waiting for sufficient resources.
`jobmanager.adaptive-scheduler.min-parallelism-increase` is deprecated.

### Balanced scheduling and failover (`2.2-migration`, `1.20.4`)

- A balanced task scheduling strategy can spread task load across TaskManagers
  to reduce bottlenecks.
- Flink 1.20.4 avoids starting extra TaskManagers and releasing a wanted one as
  failed during slot reallocation after failover.

### Rescale history (`2.3-migration`)

Set `web.adaptive-scheduler.rescale-history.size` above its default `0` to retain
per-job rescale records. They include vertex parallelism, slots, scheduler
transitions, and termination reasons, shown under the Web UI **Rescales** tab and
at:

- `/jobs/:jobid/rescales/overview`;
- `/jobs/:jobid/rescales/history`;
- `/jobs/:jobid/rescales/details/:rescaleuuid`;
- `/jobs/:jobid/rescales/summary`.

## Network and source distribution

### Lookup and split placement (`2.0-migration`, `2.2-migration`)

- Lookup connectors can tell the planner their desired input distribution or
  partitioning, allowing lookup joins to place records for a smaller, more
  effective cache.
- `SplitEnumerator` can inspect the runtime split distribution and balance new
  assignments accordingly.

### Source rate limiting (`2.2-migration`)

The `RateLimiter` interface lets Scan Source connectors protect constrained
external systems with request-limiting strategies. This facility is currently
limited to DataStream API sources.

### Adaptive downstream selection (`2.3-migration`, `2.3.0`)

The opt-in adaptive partitioner chooses a less-loaded downstream channel when a
subtask is slow. It applies to `RebalancePartitioner` and `RescalePartitioner`.

```yaml
taskmanager.network.adaptive-partitioner.enabled: true
taskmanager.network.adaptive-partitioner.max-traverse-size: 4
```

The feature defaults to disabled; maximum traversal defaults to four channels.

Flink 2.0.1 also fixes batch jobs with broadcast edges and incorrect routing by
generated code for binary shuffle keys (`2.0.1`).

## Kubernetes and YARN fixes

- Native Kubernetes jobs can start when the job JAR is on the system classpath,
  and the embedded SQL Client deployment script avoids a Kubernetes
  `FileNotFoundException` (`2.0.1`).
- Flink 1.20.4 releases affected leaked Kubernetes deployment resources
  (`1.20.4`).
- On dual-network YARN deployments, explicitly configured `rest.bind-address`
  is honored in Flink 1.20.4 (`1.20.4`).
- `flink run -sae` no longer kills the submitted job on the 1.20 branch
  (`1.20.3`).

## Distribution and local user libraries

- Flink 1.20.1 follows symlinks under `usrlib`, so linked content participates
  in user-library loading (`1.20.1`).
- Flink 1.20.1's Pekko upgrade replaces Netty 3 with Netty 4. Netty 4 allocates
  slightly more memory by default; review memory settings on constrained
  deployments (`1.20.1`).
- Flink 1.20.4 Docker images select runtime identity with Dockerfile `USER`
  rather than `gosu`. Update derived images or entrypoints that call or depend
  on `gosu` (`1.20.4`).

## Native S3 filesystem (`2.3-migration`, `2.3.0`)

`flink-s3-fs-native` uses AWS SDK v2 and does not depend on Hadoop or Presto. It
registers both `s3://` and `s3a://` and supplies `FileSystem` plus
`RecoverableWriter` for exactly-once streaming sinks. It is functionally complete
but experimental in Flink 2.3.0.

Install the plugin in the Flink plugins directory. Its `s3.*` configuration
includes:

- `s3.region`, `s3.endpoint`, and `s3.path-style-access`;
- `s3.access-key` and `s3.secret-key`, plus modern authentication such as IAM
  Roles for Service Accounts;
- `s3.upload.min.part.size` and `s3.upload.max.concurrent.uploads`;
- `s3.bulk-copy.enabled`, `s3.async.enabled`, and `s3.read.buffer.size`;
- `s3.entropy.key`;
- SSE-KMS, chunked-encoding, and checksum-validation controls.

Test credentials, endpoint semantics, multipart recovery, and sink commits in
the target object store.

## Other filesystem repair (`2.1.3`)

The Google Cloud Storage filesystem retries affected HTTP 503 responses that
the older GCS library dependency did not retry.

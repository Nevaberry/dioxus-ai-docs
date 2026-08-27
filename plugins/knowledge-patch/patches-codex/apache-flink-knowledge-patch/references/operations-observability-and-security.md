# Operations, Observability, and Security

## REST compatibility

### Removed response fields (`2.0-migration`)

- TaskManager responses omit `metrics.memorySegmentsAvailable` and
  `metrics.memorySegmentsTotal`.
- `/jobs/:jobid/config` omits `execution-mode`.
- Vertex, subtask, and TaskManager response families no longer expose `host`.
- `/jars/:jarid/run` uses `RecoveryClaimMode` internally for `claimMode` and
  `restoreMode`; their JSON shape is unchanged.

Update clients that deserialize removed fields or assume they are present.

### Application and rescale endpoints (`2.3-migration`)

Applications have overview, detail, cancel, and asynchronous JAR submission
endpoints plus their own Web UI. Adaptive Scheduler rescale records are available
through overview, history, detail, and summary endpoints when
`web.adaptive-scheduler.rescale-history.size` is greater than zero.

## HistoryServer retention

- Flink 2.1.1 cleans HistoryServer local files instead of allowing indefinite
  disk growth (`2.1.1`).
- `historyserver.archive.retained-ttl` supplies time-based archive retention and
  combines with `historyserver.archive.retained-jobs` for age-and-count policies
  (`2.2-migration`).
- Application archive defaults are separate:
  `historyserver.archive.clean-expired-applications` defaults to `false`, and
  `historyserver.archive.retained-applications` defaults to `-1`
  (`2.3-migration`).

## Metrics, traces, and events

### Source and operator metrics (`2.1-migration`, `2.2-migration`)

- Source splits expose watermark and active, paused, and idle time metrics in
  both per-second and cumulative forms.
- Operators and transformations can define custom metric variables; reporters
  convert them into tags or labels to distinguish otherwise similar metrics.

### Checkpoint spans and event reporting (`2.2-migration`)

- `traces.checkpoint.span-detail-level` controls checkpoint trace detail. At the
  highest levels it reports task/subtask span trees.
- User-reported spans may contain child spans.
- EventReporters receive built-in system events as well as custom user events.

### Reporter repairs and OTel controls

- Flink 2.1.2 passes correct configuration and ports to Prometheus reporters,
  and `MetricConfig` accepts native-typed values (`2.1.2`).
- Flink 2.0.1 packages all classes required by the OpenTelemetry reporter
  (`2.0.1`).
- For the OTel gRPC exporter, set
  `metrics.reporter.otel.exporter.compression: gzip` instead of default `none`.
  `metrics.reporter.otel.batch.size` splits large exports; default `0` disables
  batching (`2.3-migration`).

## Web UI and HTTP behavior

- Flink 1.20.4 keeps job-graph nodes clickable in Chrome 144 and later. Its job
  overview no longer shows `N/A` for business, backpressure, and data-skew
  metrics solely because some nodes have finished (`1.20.4`).
- Flink 2.1.3 sends `Connection: close` on affected `304 Not Modified` responses,
  preventing reuse from poisoning proxy connection pools (`2.1.3`).

## Logging and sensitive data

- Flink 1.20.3 fixes a PyFlink logging vulnerability in `PythonEnvUtils.java`;
  all users of that branch should use 1.20.3 or later (`1.20.3`).
- Flink 1.20.4 stops TaskManager and JobManager debug logs from printing
  sensitive data-security cookie certification information (`1.20.4`).

## TLS and dependency security

- Flink 1.20.4 changes the default cipher-suite value in `SecurityOptions`.
  Deployments relying on the implicit default should revalidate TLS policy and
  peer interoperability (`1.20.4`).
- Flink 2.0.1 updates Log4j to 2.24.3 to address critical vulnerabilities
  (`2.0.1`).
- Flink 2.1.1 upgrades `org.apache.commons:commons-lang3` from 3.12.0 to 3.18.0
  to mitigate CVE-2025-48924 (`2.1.1`).

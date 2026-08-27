# Observability, Security, and Operations

Use this reference for metrics, traces, events, retention, packaged dependency
changes, security remediation, TLS, and operational diagnostics.

Batch attribution: `1.20.1`, `1.20.3`, `2.0.1`, `2.1-migration`, `2.1.1`,
`2.2-migration`, `1.20.4`, `2.1.2`, `2.1.3`, `2.3-migration`.

## Metrics, labels, traces, and events

- Each source split exposes `currentWatermark` plus per-second
  `activeTimeMsPerSecond`, `pausedTimeMsPerSecond`, and
  `idleTimeMsPerSecond`, and cumulative `accumulatedActiveTimeMs`,
  `accumulatedPausedTimeMs`, and `accumulatedIdleTimeMs`. Paused time means a
  watermark-alignment pause; idle time comes from idleness detection.
- Operators and transformations can define custom metric variables. Reporters
  render them as tags or labels to distinguish otherwise similar metrics.
- `traces.checkpoint.span-detail-level` controls checkpoint trace detail. The
  highest levels report task/subtask span trees, and custom reported spans can
  have child spans.
- EventReporters receive built-in system events as well as user-reported
  custom events.
- `MetricConfig` accepts native-typed values. Prometheus reporter setup passes
  the correct configuration and port after the 2.1.2 fix.

## OpenTelemetry reporting

- The packaged OpenTelemetry reporter contains all required classes as of
  2.0.1.
- For the OTel gRPC exporter,
  `metrics.reporter.otel.exporter.compression` accepts `gzip`; its default is
  `none`.
- `metrics.reporter.otel.batch.size` splits large exports across calls. The
  default `0` disables batching.

## HistoryServer retention and cleanup

- `historyserver.archive.retained-ttl` adds age-based archive retention and can
  combine with `historyserver.archive.retained-jobs` to constrain both age and
  count.
- The HistoryServer cleans up affected local files as of 2.1.1, avoiding
  unbounded disk growth in long-lived deployments.
- Application archive cleanup has separate defaults:
  `historyserver.archive.clean-expired-applications` is `false` and
  `historyserver.archive.retained-applications` is `-1`.

## Security fixes and sensitive output

- Flink 1.20.3 fixes a vulnerability in PyFlink logging in
  `PythonEnvUtils.java`; users on the 1.20 line should run 1.20.3 or later.
- Log4j is updated to 2.24.3 in Flink 2.0.1 to address critical
  vulnerabilities.
- `org.apache.commons:commons-lang3` moves from 3.12.0 to 3.18.0 in 2.1.1 to
  mitigate CVE-2025-48924.
- TaskManager and JobManager debug logs no longer emit sensitive data-security
  cookie certification information as of 1.20.4.

## Networking, dependency, and TLS changes

- Flink 1.20.1 upgrades Apache Pekko from 1.0.1 to 1.1.2, moving its transport
  dependency from Netty 3 to Netty 4 and removing Netty 3. Netty 4 allocates
  slightly more memory by default; recheck memory-constrained deployments.
- Protobuf Java moves from 3.21.7 to 4.32.1 (Protocol Buffers 32). It supports
  editions 2023 and 2024 while retaining proto2/proto3 compatibility. Proto3
  optional presence no longer requires `protobuf.read-default-values: true`.
- The default `SecurityOptions` cipher-suite value changes in 1.20.4. Revalidate
  interoperability and security policy if the deployment relied on the
  implicit TLS default.
- Google Cloud Storage retries the affected 503 responses and affected HTTP
  304 responses close their connection to protect proxy pools as of 2.1.3.

## Operational patch checks

- Use 1.20.4 when the Web UI must support Chrome 144+, finished-node overview
  metrics, dual-network YARN REST binding, corrected Kubernetes cleanup, or
  failover without excess TaskManager churn.
- Use the applicable fixed patch for RocksDB/ForSt recovery, unaligned
  checkpointing, sink commit, join/planner, or mini-batch correctness rather
  than masking those failures with operational retries.

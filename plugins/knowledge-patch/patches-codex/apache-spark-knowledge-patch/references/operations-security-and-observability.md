# Operations, Security, and Observability

## Checkpoints, decommissioning, and shuffle service

- `spark.checkpoint.dir` provides a configuration-level checkpoint location in
  `4.0.0`.
- `spark.stage.ignoreDecommissionFetchFailure` defaults to enabled, changing
  recovery when stage fetch failures involve decommissioned executors.
- The external shuffle service can fetch remote-disk RDD blocks as of `3.5.6`.
- Shuffle cleanup `RemoveFiles` mode works with AQE disabled in `4.0.1`.
- Order-independent shuffle checksum validation and dependent-stage rollback
  are described in the migration reference.

## Metrics, profiling, and logging

- `spark.metrics.appStatusSource.enabled` and
  `spark.ui.prometheus.enabled` default to enabled in `4.0.0`.
- Spark adds an OpenTelemetry push sink, executor and driver JVM profiling, and
  a log throttler.
- Python worker diagnostics in `4.1.0` cover pandas and Arrow UDFs, UDTFs, and
  driver-side workers. Periodic traceback dumps, iterator-UDF profiling,
  stdout/stderr logging redirection, and a VizTracer enablement script are
  available.
- Procfs metrics parse process names containing spaces correctly (`3.5.7`).
- PySpark exposes a UDF processing-time metric, SQL reports last-attempt
  metrics, and the UI displays query IDs (`4.2.0`).
- The task-name MDC key is `task_name`; the migration reference describes the
  legacy switch.

## Event logs, History Server, and UI

- Event-log rolling and compression defaults are covered in the migration
  reference.
- `spark.eventLog.excludedPatterns` filters matching event-log content
  (`4.1.0`), and the History Server can load rolling logs on demand.
- History UI processing no longer fails with `StreamConstraintsException` for
  an affected string over 20,000,000 characters (`3.5.7`).
- History pages escape application and user names (`3.5.8`).
- The `4.2.0` UI adds dark mode, searchable and zoomable SQL plans,
  side-by-side initial/final AQE plans, highlighting of non-default
  configuration, and configuration export.
- The History Server can read multiple log directories and exclude scan paths
  by pattern.
- Connect executions appear in a History Server tab.

## RPC and transport security

- RPC encryption supports AES-GCM (`4.0.0`).
- JKS-backed RPC SSL can use a private-key password different from the
  keystore password.
- `spark.ui.jetty.sniHostCheckEnabled` controls Jetty SNI host validation
  (`4.2.0`).
- `spark.ui.contentSecurityPolicy.enabled` adds a Content-Security-Policy
  header.
- `spark.ui.showErrorStacks` can suppress UI error-page stack traces.

## Sensitive output

Spark `4.2.0`:

- redacts credentials embedded in JDBC URLs;
- applies `spark.sql.redaction.string.regex` to descriptions on job and SQL
  pages;
- redacts environment variables and Java options in standalone Worker JSON;
  and
- creates temporary files with owner-only permissions.

The History Server output-escaping fix in `3.5.8` prevents application and user
names from being interpreted as markup.

## Kubernetes

- The documented default for `spark.kubernetes.configMap.maxSize` is corrected
  in `3.5.5`. Configure it explicitly where the ceiling matters.
- `spark.kubernetes.executor.useDriverPodIP` allows executors to use the driver
  pod IP (`4.1.0`).
- `spark.kubernetes.driver.annotateExitException` controls driver exit-error
  annotations.
- Spark `4.2.0` adds Deployment API support and
  `spark.kubernetes.scheduler.volcano.podGroupTemplateJson`.
- `ExecutorResizePlugin` and `ExecutorPVCResizePlugin` support heterogeneous
  executors. Kubernetes also supports recovery-mode executors and reuse of
  resized PVCs.
- The resource-manager API, including `SparkPod`, configuration utilities,
  driver specifications, and builders, is Stable with Java-friendly factories
  and getters.
- Executor allocation defaults to batches of 20 and a generated
  `NetworkPolicy` limits ingress to the driver and same-job peers
  (`4.2-migration`). The migration reference gives both controls.
- The Kubernetes image moves to a Java `25-jre` base in `4.2.0`.

## YARN, launcher, and process behavior

- The YARN external shuffle service JAR contains `scala-library` in `4.0.1`.
- Launcher remote-mode detection respects properties files and
  `--load-spark-defaults`.
- JPMS arguments are applied even to processes not launched through
  `SparkSubmit`.
- An opt-in SparkSubmit flag can call `System.exit` after the user
  application's main method returns (`4.1.0`).
- YARN accepts `spark.yarn.am.defaultJavaOptions` in `4.2.0`.
- JDK 8 `jmap` discovery prefers the Java home selected by `JAVA_HOME`
  (`3.5.8`).
- Spark builds and runs on Java 25, including SparkR; R 3.x is unsupported in
  `4.2.0`.

## Source builds and packaging

- The `sbt/package` path recognizes `NO_PROVIDED_SPARK_JARS` to control
  collection of `spark-avro.jar` and `spark-protobuf.jar` (`4.0.1`).
- Align dependency overrides and exclusions with the bundled versions listed
  in the data-sources reference.
- Configuration byte sizes accept `KiB`, `MiB`, `GiB`, `TiB`, and `PiB`
  suffixes as of `4.2.0`.

## Operational correctness fixes

- The incorrect SPARK-49699 configuration follows graceful deprecation rather
  than abrupt removal in `3.5.5`; retain it only for the transition window.
- `Observation` no longer deadlocks and has a safety check preventing blocking
  (`3.5.8`).
- `Observation.get` surfaces the underlying Scala or Python collection failure
  rather than returning an empty result (`4.2-migration`).

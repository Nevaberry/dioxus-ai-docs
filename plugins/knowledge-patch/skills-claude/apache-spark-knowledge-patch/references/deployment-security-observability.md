# Deployment, security, and observability

Use this reference for Kubernetes, standalone and YARN deployment changes,
RPC protection, event logs, metrics, profiling, worker diagnostics, the web UI,
and the History Server.

## Kubernetes deployment

### ConfigMap size (3.5.5)

The documented default for `spark.kubernetes.configMap.maxSize` was corrected.
Do not depend on the value in older 3.5 documentation; configure it explicitly
when the limit matters.

### Executor and PVC defaults (4.0-migration)

Executor pods are allocated in batches of 10 rather than 5. PVCs use
`ReadWriteOncePod` rather than `ReadWriteOnce`, and executor status checks
include every container in the pod. Restore earlier behavior with:

```properties
spark.kubernetes.allocation.batch.size=5
spark.kubernetes.legacy.useReadWriteOnceAccessMode=true
spark.kubernetes.executor.checkAllContainers=false
```

### Allocation and network isolation (4.2-migration)

Executor allocation grows from 10 to 20 pods per batch. Spark also creates a
`NetworkPolicy` that limits executor ingress to the driver and peer executors
in the same job. Use `spark.kubernetes.allocation.batch.size=10` for the
earlier batch size. To disable the policy, exclude
`org.apache.spark.deploy.k8s.features.NetworkPolicyFeatureStep` through
`spark.kubernetes.driver.pod.excludedFeatureSteps`.

### Driver networking and exit annotations (4.1.0)

`spark.kubernetes.executor.useDriverPodIP` lets executors connect through the
driver pod IP. `spark.kubernetes.driver.annotateExitException` controls
annotation of driver exit exceptions.

### Deployment and executor management (4.2.0)

Kubernetes supports the Deployment API and
`spark.kubernetes.scheduler.volcano.podGroupTemplateJson`. The built-in
`ExecutorResizePlugin` and `ExecutorPVCResizePlugin` support heterogeneous
executors. Kubernetes also supports recovery-mode executors and reuse of
resized PVCs.

The Kubernetes resource-manager API is Stable. `SparkPod`, configuration
utilities, driver specifications, and builders expose Java-friendly factories
and getters.

## Standalone, shuffle, and YARN operations

### Worker and external shuffle defaults (4.0-migration)

Workers periodically clean worker and stopped-application directories. The
external shuffle service defaults to RocksDB rather than LevelDB and removes
shuffle blocks belonging to deallocated executors. The runtime reference lists
the compatibility flags.

### Master REST API (4.1-migration, 4.2-migration)

The Master REST API is enabled by default; disable it with
`spark.master.rest.enabled=false` (4.1-migration). On Java 21 or newer its
default executor uses virtual threads; disable them with
`spark.master.rest.virtualThread.enabled=false` (4.2-migration).

### YARN controls (4.0.1, 4.2.0)

The YARN external shuffle-service JAR includes `scala-library`, eliminating a
separate missing-runtime dependency (4.0.1). YARN accepts
`spark.yarn.am.defaultJavaOptions` as of 4.2.0.

## RPC and UI security

### RPC transport (4.0.0)

RPC encryption supports AES-GCM. JKS-backed RPC SSL supports a private-key
password distinct from the keystore password, so stores with separate
credentials work correctly.

### Jetty and web UI controls (4.2.0)

`spark.ui.jetty.sniHostCheckEnabled` controls Jetty SNI host checking.
`spark.ui.contentSecurityPolicy.enabled` adds a Content-Security-Policy header.
`spark.ui.showErrorStacks` can suppress stack traces on UI error pages.

### Redaction and temporary files (4.2.0)

Spark redacts credentials embedded in JDBC URLs. It applies
`spark.sql.redaction.string.regex` to job descriptions on job and SQL pages.
Standalone Worker JSON redacts environment variables and Java options.
Temporary files use owner-only permissions.

## Logging, metrics, and profiling

### Task-name MDC key (4.0-migration)

The task-name MDC key changed from `mdc.taskName` to `task_name`. Set
`spark.log.legacyTaskNameMdc.enabled=true` for processors that require the old
key.

### Metrics and telemetry defaults (4.0.0)

`spark.metrics.appStatusSource.enabled` and `spark.ui.prometheus.enabled`
default to enabled. Spark adds an OpenTelemetry push sink, executor and driver
JVM profiling, and a log throttler.

### Python worker diagnostics (4.1.0)

Worker logging covers pandas and Arrow UDFs, UDTFs, and driver-side workers.
Periodic traceback dumps, iterator-UDF profiling, stdout/stderr redirection,
and a helper for enabling VizTracer improve Python diagnostics.

### Query and UDF observability (4.2.0)

PySpark exposes UDF processing time. SQL reports last-attempt metrics, and the
web UI displays query IDs.

## Event logs and History Server

### Rolling and compression (4.0-migration)

Event logs roll incrementally and are compressed by default. Set
`spark.eventLog.rolling.enabled=false` and
`spark.eventLog.compress=false` for the earlier behavior.

### Large strings and escaped names (3.5.7, 3.5.8)

The History UI handles affected strings larger than 20,000,000 characters
without `StreamConstraintsException` (3.5.7). History pages escape application
and user names so those values cannot be interpreted as markup (3.5.8).

### Filtering and on-demand loading (4.1.0)

`spark.eventLog.excludedPatterns` excludes matching event-log content. The
History Server can load rolling logs on demand.

### UI and History Server operations (4.2.0)

The web UI adds dark mode, searchable and zoomable SQL plans, side-by-side
initial and final AQE plans, non-default configuration highlighting, and
configuration export. The History Server reads multiple log directories and
can exclude paths from directory scanning by pattern.

Spark Connect executions are visible on a dedicated History Server tab.

## Host metrics correctness

Procfs metrics no longer split the `comm` field incorrectly when a process name
contains spaces (3.5.7).

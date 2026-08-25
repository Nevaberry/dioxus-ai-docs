---
name: apache-flink-knowledge-patch
description: Apache Flink
version: 2.3.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Flink Knowledge Patch

Use this skill when upgrading or operating Flink, writing DataStream or Table
API jobs, changing SQL, implementing connectors, or diagnosing state,
checkpoint, scheduling, and deployment behavior. Start with the quick checks,
then open the topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [Migration, APIs, and Configuration](references/migration-apis-and-configuration.md) | Java/runtime requirements, removed APIs, typed configuration, SPI changes, serialization compatibility |
| [SQL, Table API, and Planning](references/sql-table-and-planning.md) | SQL syntax and types, materialized tables, inference, joins, PTFs, compiled plans, planner corrections |
| [State, Checkpoints, and Storage](references/state-checkpoints-and-storage.md) | Async/disaggregated state, savepoints, RocksDB, ForSt, unaligned checkpoints, native S3 |
| [Runtime, Scheduling, and Deployment](references/runtime-scheduling-and-deployment.md) | Adaptive Scheduler, partitioning, watermarks, Kubernetes, YARN, applications, REST and Web UI |
| [Connectors, Formats, and Python](references/connectors-formats-and-python.md) | Source/Sink V2, connector migration, batching, formats, PyFlink, filesystems and HTTP behavior |
| [Observability, Security, and Operations](references/observability-security-and-operations.md) | Metrics, traces, events, HistoryServer retention, logging, dependencies, TLS and operational fixes |

## Upgrade triage

Before changing a job or cluster:

1. Identify the exact Flink line and every external connector version.
2. Inventory removed DataSet, Scala, Source/Sink V1, legacy Table, state,
   serialization, deployment, and configuration surfaces.
3. Treat state and savepoint restoration across the 1.x/2.x boundary as a
   compatibility project, not an assumed in-place restore.
4. Convert `flink-conf.yaml` to standard-YAML `config.yaml` before starting a
   2.x distribution.
5. Validate the Java runtime: Java 11 is the minimum, Java 17 is the default
   and recommended runtime, and Java 21 is supported.
6. Rehearse checkpoints, failover, rescaling, and sink commits with the target
   patch release and production serializers.

## Highest-impact removals

Flink 2.0 removes these major families:

- Java DataSet and Scala DataStream/DataSet APIs. Prefer Java DataStream or
  Table API/SQL.
- `SourceFunction`, `SinkFunction`, Sink V1, `TableSource`, `TableSink`,
  `TableSchema`, `TableColumn`, and `Types`. Move to Source/Sink V2, dynamic
  table sources/sinks, `Schema`, `Column`, and `DataTypes`.
- Positional/string `keyBy` and `partitionCustom`, iterations, legacy
  watermark assignment, convenience file writers/readers, and
  `DataStreamUtils.collect*`.
- `ParameterTool` and its abstract/multiple variants.
- Explicit `TimeCharacteristic` selection and old Flink `Time` overloads.
- Per-job deployment and legacy Hybrid Shuffle. Use application mode; submit
  Kubernetes applications with `flink run -t kubernetes-application`.
- The SQL Client `-u/--update` option. Put updates in a file and use `-f`.

Open the migration reference before resolving compilation errors: several
replacement APIs change lifecycle contexts or return types rather than simply
renaming a method.

## Configuration quick reference

Use typed options:

```java
configuration.set(option, value);
T value = configuration.get(option);
```

`RichFunction.open(Configuration)` becomes `open(OpenContext)`. UDFs obtain
serializer, global-parameter, and object-reuse facilities from
`RuntimeContext`; they no longer receive the full `ExecutionConfig` surface.

For Adaptive Scheduler local recovery, opt in explicitly:

```yaml
execution.state-recovery.from-local: true
```

On Kubernetes, disable minimal-TaskManager preference only when the prior
downscaling strategy is required:

```yaml
jobmanager.adaptive-scheduler.prefer-minimal-taskmanagers: false
```

Do not copy removed 1.x options into 2.x configuration. In particular, review
state-backend, Kryo/POJO registration, SSL, heap, web/backpressure, network,
adaptive-batch, and Hybrid Shuffle settings against the typed 2.x options.

## SQL and Table quick reference

Use `QUALIFY` to filter window-function results:

```sql
SELECT *
FROM orders
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer_id ORDER BY order_time DESC
) = 1;
```

Table functions may appear directly in `FROM`; the outer `TABLE(...)` wrapper
remains valid. SQL also supports C-style escape strings and casts from
`DOUBLE` to `BOOLEAN`.

For semi-structured data, `VARIANT` preserves scalar, array, and string-keyed
map types. Convert JSON text with `PARSE_JSON` or `TRY_PARSE_JSON`.

For catalog-defined real-time inference, use `ML_PREDICT`; Table API can also
define models and run inference. `VECTOR_SEARCH` adds online vector similarity
search. Keep provider-specific availability separate from the core API.

Materialized tables support declarative refresh pipelines, cross-cluster YARN
and Kubernetes submission, Paimon integration, schema/query evolution,
bucketing, discovery, explicit columns, watermarks, primary keys, and selectable
refresh start positions. A physical-plan replacement can still require full
reprocessing.

## Join and process-function cautions

The multi-join operator is experimental. It is opt-in:

```sql
SET 'table.optimizer.multi-join.enabled' = 'true';
```

Its state keys changed from upsert keys to unique keys after its initial
release. Use a patch release containing the relevant OR-predicate,
heap-backend, mixed-source, and row-kind fixes before relying on it.

Process Table Functions support managed state, timers, event time,
changelogs, late-record handling, and ordered table arguments:

```sql
MyPtf(input => TABLE t PARTITION BY k ORDER BY ts)
```

When an upsert key differs from the sink primary key, choose an explicit
`ON CONFLICT` action: `DO NOTHING`, `DO ERROR`, or `DO DEDUPLICATE`.

## State and checkpoint quick reference

Flink's disaggregated state architecture uses remote primary storage and
parallel asynchronous access. DataStream `process()` supports async state, and
DataStream V2 state lookup returns V2 state objects directly rather than
legacy state wrapped in `Optional`.

Sink expansion disables unaligned checkpoints only within expanded
pre-commit, committer, or post-commit connections. A broad disablement on all
connections was a regression corrected in 2.0.1.

To checkpoint progress while restored channel state is still being consumed,
enable both controls:

```yaml
execution.checkpointing.unaligned.recover-output-on-downstream.enabled: true
execution.checkpointing.unaligned.during-recovery.enabled: true
```

This recovery mode is off by default. Also validate custom partitioners,
rescaling, multiple exchanges, and file-merged checkpoints against the patch
fixes in the state reference.

## Native S3 quick reference

The experimental `flink-s3-fs-native` plugin uses AWS SDK v2, needs neither
Hadoop nor Presto, and registers `s3://` and `s3a://`. Install it in the
plugins directory. It provides `FileSystem` and `RecoverableWriter` support,
including exactly-once streaming sinks and modern role-based authentication.

Configure it through `s3.*`; review region, endpoint, path style, credentials,
multipart upload, bulk copy, async I/O, read buffers, entropy, SSE-KMS, chunked
encoding, and checksum validation. Its experimental status matters even though
the implementation is functionally complete.

## Scheduling and watermark quick reference

`jobmanager.adaptive-scheduler.executing.resource-stabilization-timeout`
delays scaling after resource changes. The old minimum-parallelism-increase
control is deprecated.

The adaptive network partitioner is disabled by default. Enable it with
`taskmanager.network.adaptive-partitioner.enabled`; its channel search limit is
`taskmanager.network.adaptive-partitioner.max-traverse-size`, default `4`.
Adaptive selection applies to rebalance and rescale partitioners.

Watermark idleness excludes time blocked by backpressure or alignment. Custom
generators can read the same clock from
`WatermarkGeneratorSupplier.Context#getInputActivityClock()`.

Watermark alignment waits three update intervals by default before pausing.
Set `pipeline.watermark-alignment.buffer-size: 0` only to recover the earlier
pause behavior.

## Applications and observability quick reference

Applications are lifecycle resources with asynchronous REST submission,
overview/detail/cancel endpoints, a Web UI, multi-job membership, failure
reporting, and HA re-execution for incomplete session applications. Review the
termination, cluster-ID, and HistoryServer application-retention defaults
before enabling this lifecycle.

Adaptive Scheduler rescale history is disabled at its default size `0`.
Set `web.adaptive-scheduler.rescale-history.size` above zero to populate the
Web UI **Rescales** tab and rescale REST resources.

For OpenTelemetry gRPC metrics, `metrics.reporter.otel.exporter.compression`
supports `gzip` instead of default `none`; `metrics.reporter.otel.batch.size`
defaults to `0`, meaning batching is disabled.

## Patch-release discipline

Do not treat a feature-level upgrade as sufficient when a listed patch release
fixes correctness, recovery, security, planner, connector, or deployment
behavior relevant to the job. Match symptoms to the topic references and test
on the newest compatible patch release before adding workarounds.

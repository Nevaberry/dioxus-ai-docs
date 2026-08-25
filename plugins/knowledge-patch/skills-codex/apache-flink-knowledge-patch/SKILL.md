---
name: apache-flink-knowledge-patch
description: Apache Flink
version: 2.3.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Flink Knowledge Patch

Use this skill when upgrading, configuring, extending, or troubleshooting Apache
Flink, especially across major API boundaries. Check the project's pinned Flink
version before applying version-specific guidance. Treat project code, connector
compatibility, deployed configuration, and restore tests as the final authority.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/migration-and-java-apis.md](references/migration-and-java-apis.md) | Flink 2.0 removals, Java/runtime requirements, DataStream and connector API migrations, configuration changes |
| [references/sql-table-and-models.md](references/sql-table-and-models.md) | SQL syntax and correctness, Table API, materialized tables, models, PTFs, joins, compiled plans |
| [references/state-checkpoints-and-watermarks.md](references/state-checkpoints-and-watermarks.md) | State backends, async state, serializers, checkpoints, savepoints, sinks, watermarks |
| [references/deployment-scheduling-and-storage.md](references/deployment-scheduling-and-storage.md) | Application deployment, schedulers, Kubernetes, YARN, Docker, filesystems, S3, source and network distribution |
| [references/operations-observability-and-security.md](references/operations-observability-and-security.md) | REST, Web UI, metrics, traces, events, HistoryServer, logging, TLS, dependency and security fixes |
| [references/python-and-connector-compatibility.md](references/python-and-connector-compatibility.md) | PyFlink, Python packaging, connector compatibility, lookup and async connectors, Protobuf |

## Start with the breaking changes

### Plan stateful upgrades explicitly

Do not assume a Flink 1.x savepoint or state snapshot restores unchanged on
Flink 2.x. Flink 2.0 enables new collection serializers, upgrades Kryo, removes
legacy state-backend and savepoint APIs, and does not guarantee 1.x-to-2.x state
compatibility.

Before changing the runtime:

1. Inventory every state serializer and connector serializer.
2. Verify connector releases support Source/Sink V2.
3. Exercise savepoint creation and restore with production-like state.
4. Keep a rollback path that does not require reading newly rewritten state.

### Replace removed API families

Flink 2.0 removes the Java DataSet API, Scala DataStream/DataSet APIs,
`SourceFunction`, `SinkFunction`, Sink V1, legacy Table sources and sinks, and
many convenience methods. Prefer Java DataStream, Table API/SQL, Source/Sink V2,
`DynamicTableSource`/`DynamicTableSink`, `Schema`, `Column`, and `DataTypes`.

Common compile-time migrations include:

| Removed surface | Replacement or action |
| --- | --- |
| `Configuration.getInteger(...)`, `setLong(...)`, and peers | `get(ConfigOption<T>)` and `set(ConfigOption<T>, T)` |
| `RichFunction.open(Configuration)` | `open(OpenContext)` |
| `Sink.createWriter(Sink.InitContext)` | `createWriter(WriterInitContext)` |
| `OutputFormat.open(int, int)` | `open(OutputFormat.InitializationContext)` |
| `FinalizeOnMaster.finalizeGlobal(int)` | `finalizeGlobal(FinalizationContext)` |
| Windowed join/co-group `.with(...)` | `.apply(...)` |
| Explicit `TimeCharacteristic` selection | Remove it; use event-time and watermark APIs |
| `ParameterTool` family | Use another argument parser |

Read the API reference before mechanically replacing calls: runtime task
metadata getters, serializer compatibility signatures, provider contexts,
projection pushdown, and UDF execution facilities also changed.

### Migrate cluster configuration

Flink 2.0 reads standard-YAML `config.yaml`; it no longer ships or parses
`flink-conf.yaml`. Convert the file with the migration tool and audit removed
options rather than renaming the old file. In particular, legacy state-backend,
SSL, heap, network, web, adaptive-batch, Kryo/POJO registration, and Hybrid
Shuffle settings may have no accepted equivalent under their old keys.

Java 11 is the minimum runtime, Java 17 is the default and recommended runtime,
and Java 21 is supported. Java 8 is unsupported. Recheck Docker images and source
builds because their default Java runtime changes with the distribution.

### Replace removed deployment modes

Per-job mode is removed. Use application mode, including SQL Gateway application
mode. Submit Kubernetes applications with:

```bash
flink run -t kubernetes-application ...
```

The `run-application` CLI action is removed. The SQL Client's `-u/--update`
option is also removed; place statements in a file and run:

```bash
sql-client.sh -f updates.sql
```

## High-value SQL and Table features

### Filter window results with `QUALIFY`

Use `QUALIFY` for Top-N and deduplication after window evaluation:

```sql
SELECT *
FROM orders
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer_id ORDER BY order_time DESC
) = 1;
```

Flink SQL also supports C-style escape strings, direct table-function calls in
`FROM`, and `DOUBLE`-to-`BOOLEAN` casts.

### Handle semi-structured and model-backed data

Use `VARIANT` for typed JSON-like scalars, arrays, and string-keyed maps. Convert
JSON text with `PARSE_JSON` or `TRY_PARSE_JSON`. Catalog models can be managed
through SQL or Table API, applied with `ML_PREDICT`, and used for streaming
similarity search with `VECTOR_SEARCH`.

### Treat experimental joins and APIs as unstable

DataStream API V2 and the streaming multi-join operator are experimental. The
multi-join operator is opt-in:

```sql
SET 'table.optimizer.multi-join.enabled' = 'true';
```

Its state key changed after its first release, and later maintenance releases
fixed source-type, row-kind, OR-predicate, parallelism, and heap-state issues.
Do not adopt it without upgrade and restore tests.

### Make sink key conflicts explicit

When a query upsert key differs from the sink primary key, planning fails by
default in Flink 2.3. Add an `ON CONFLICT` policy choosing `DO NOTHING`,
`DO ERROR`, or `DO DEDUPLICATE`; do not rely on implicit full-history retention.

## High-value state and checkpoint behavior

### Enable local recovery intentionally

The Adaptive Scheduler honors `execution.state-recovery.from-local`, which
defaults to `false`:

```yaml
execution.state-recovery.from-local: true
```

### Understand unaligned-checkpoint boundaries

Expanded sink topologies disable unaligned checkpoints on their internal
pre-commit, committer, and post-commit connections so committables exist at
checkpoint completion. Flink 2.0.1 corrected a regression that disabled them on
unrelated connections. Later fixes cover rescaling, file merging, custom
partitioners, and checkpointing while restored channel state is consumed.

To checkpoint during unaligned recovery in Flink 2.3, enable both:

```yaml
execution.checkpointing.unaligned.recover-output-on-downstream.enabled: true
execution.checkpointing.unaligned.during-recovery.enabled: true
```

### Account for the input-activity clock

Idleness excludes time blocked by backpressure or watermark alignment. Custom
watermark generators can use
`WatermarkGeneratorSupplier.Context#getInputActivityClock()`. Flink 2.3 delays
alignment pausing by three update intervals by default; set
`pipeline.watermark-alignment.buffer-size: 0` to restore the earlier timing.

## High-value deployment and operations behavior

### Use native S3 deliberately

The experimental `flink-s3-fs-native` plugin uses AWS SDK v2, handles both
`s3://` and `s3a://`, and provides `FileSystem` plus `RecoverableWriter` without
Hadoop or Presto. Install it under `plugins/`, configure `s3.*`, and validate
authentication, multipart upload, encryption, checksums, and exactly-once sink
recovery before production use.

### Opt into load-aware partitioning

Enable the adaptive partitioner when slow downstream channels make round-robin
delivery a bottleneck:

```yaml
taskmanager.network.adaptive-partitioner.enabled: true
taskmanager.network.adaptive-partitioner.max-traverse-size: 4
```

It applies to rebalance and rescale partitioners. The feature is disabled by
default.

### Retain rescale history explicitly

`web.adaptive-scheduler.rescale-history.size` defaults to `0`. Set it above zero
to expose scheduler transitions, parallelism, slots, and termination reasons in
the Web UI and rescale REST endpoints.

### Revalidate defaults during maintenance upgrades

Maintenance releases include correctness, security, and operational fixes that
can matter as much as feature releases: PyFlink logging, checkpoint recovery,
sink commits, RocksDB/ForSt restores, SQL result correctness, Kubernetes resource
cleanup, HistoryServer retention, TLS defaults, and observability packaging.
Consult the topic references for the exact affected branch and behavior before
choosing an upgrade target.

## Working method

1. Read the manifest or dependency management to identify the exact Flink and
   connector versions.
2. Open the topic reference that matches the code or operational surface.
3. Separate intentional compatibility changes from maintenance-release fixes.
4. Confirm configuration defaults in the deployed artifact, especially for
   opt-in scheduler, checkpoint, partitioning, and observability features.
5. Compile connector and UDF extensions against the target APIs.
6. Test SQL plans, compiled-plan round trips, savepoint restore, failover,
   rescaling, and sink commit behavior before rollout.

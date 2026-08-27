# Operations, integrations, and tooling

Use this reference for background processing, workload scheduling, shard-failure policy, message queues, Keeper, dictionaries, server documentation, local listeners, and experimental execution surfaces.

## Distributed shard failure policy

`skip_unavailable_shards_mode` is available as either a query setting or a `Distributed` engine setting. When `skip_unavailable_shards` is enabled, the mode selects which remote-shard exception categories are suppressed.

Do not treat shard skipping as a single all-or-nothing behavior. Choose a mode that suppresses only the failures the workload can tolerate, and preserve visibility into omitted shards so partial results are not mistaken for complete ones.

## Background activity controls

Engine-agnostic controls cover Kafka, RabbitMQ, NATS, S3Queue, AzureQueue, and refreshable-view background work:

```sql
SYSTEM STOP ...;
SYSTEM START ...;
SYSTEM PAUSE ...;
SYSTEM CANCEL ...;
SYSTEM REFRESH ...;
```

Their `ALL BACKGROUND` forms target all matching background activity. The precise target follows the command grammar and engine. Treat broad forms as service-impacting operations, especially during ingestion or refresh backlogs.

### NATS JetStream acknowledgment

JetStream messages are acknowledged only after a successful insertion. Two settings refine direct consumption:

- `nats_wait_for_flush_interval` can keep consumption open for the configured flush interval.
- `nats_commit_on_select` makes direct `SELECT` reads acknowledge the messages they consume.

Use `nats_commit_on_select` only when a direct read is intended to advance the consumer; exploratory queries otherwise become destructive from the queue's perspective.

## Kafka authentication

Set the Kafka SASL mechanism to authenticate an Amazon MSK integration with IAM roles:

```text
kafka_sasl_mechanism = AWS_MSK_IAM
```

This replaces SASL/SCRAM user credentials with IAM-based authentication for that integration. Ensure the runtime identity and policy are available wherever the Kafka client executes.

## Workload scheduling

Create memory as a schedulable resource:

```sql
CREATE RESOURCE memory (MEMORY RESERVATION);
```

Workload hierarchies accept `max_memory` limits and `weight` shares. Route a query explicitly:

```sql
SELECT * FROM events SETTINGS workload = 'interactive';
```

The former `resources` and `workload_classifiers` server-config sections are ignored; keep scheduling definitions in `CREATE RESOURCE` and `CREATE WORKLOAD` DDL.

## Generated and asynchronous query execution

### `QueryRunner` table engine

Rows inserted into a `QueryRunner` table represent queries for the engine to execute. This supports asynchronous or generated batches, remote-cluster routing, benchmarks, fuzzing, and shadow-traffic testing.

Because inserts cause query execution rather than passive storage, restrict write access and keep generated query text auditable. Apply normal read, write, and resource controls to the work each row triggers.

### Continuous queries

Enable the experimental feature:

```sql
SET enable_streaming_queries = 1;
```

Appending `STREAM` leaves a query open and emits newly inserted rows:

```sql
SELECT id, msg FROM live_events STREAM;
```

A `CURSOR` clause can resume at explicit `block_number` and `block_offset` positions. Persist both coordinates together when building a resumable consumer.

## `clickhouse-local` listeners

The current `clickhouse-local` session can serve native and HTTP clients:

```sql
SYSTEM START LISTEN TCP;
SYSTEM START LISTEN HTTP;
```

Stop the listeners explicitly:

```sql
SYSTEM STOP LISTEN TCP;
SYSTEM STOP LISTEN HTTP;
```

Starting a listener changes a local one-shot process into a reachable server surface. Bind and expose it only within the intended trust boundary.

## Dictionaries

### Per-dictionary lazy loading

Set `dictionary_lazy_load` inside an individual dictionary definition to override the global `dictionaries_lazy_load` setting. This permits eager and lazy dictionaries to coexist instead of forcing one policy on the entire server.

### Unload without dropping

Release dictionary memory while preserving its definition:

```sql
SYSTEM UNLOAD DICTIONARY dictionary_name;
SYSTEM UNLOAD DICTIONARIES;
```

An unloaded dictionary reloads lazily on its next access. Plan for the reload latency and source availability on that first query.

### Keeper-backed serial IDs

`generateSerialID(name)` allocates IDs from a named, batched distributed counter stored in Keeper. It is safe under parallel and distributed execution and can be used in a table default:

```sql
CREATE TABLE events
(
    id UInt64 DEFAULT generateSerialID('events'),
    payload String
)
ENGINE = MergeTree
ORDER BY id;
```

The name identifies the counter, so reuse it only where a shared sequence is intended.

## Keeper protocol compatibility

After every member of a Keeper ensemble has been upgraded, enable the default-off `create_container` feature flag to accept ZooKeeper `CreateContainer` opcode 19 and garbage-collect childless container nodes.

This flag provides server-protocol compatibility for external ZooKeeper clients. ClickHouse's own client still cannot create container nodes. Do not enable it midway through a mixed-version ensemble upgrade.

## Documentation discovery

### Server HTTP documentation

The HTTP interface exposes `/docs`. It is backed by `system.documentation` and provides searchable rendered reference documentation.

### Interactive client help

The interactive client accepts `help topic` and renders the matching documentation inline:

```text
help Geometry;
```

Use these discovery surfaces to confirm locally available syntax and function details on the running installation.

## PromQL dialect

Select the client dialect and the time-series table:

```sql
SET dialect = 'promql';
SET promql_table_name = 'metrics';
```

The initial dialect supports `rate`, `delta`, and `increase` in 25.8. SQL can invoke a PromQL expression through `prometheusQuery('up', ...)`. Keep PromQL client settings scoped so ordinary SQL sessions are not parsed under the alternate dialect.

## WebAssembly UDFs

WebAssembly UDFs run sandboxed with Wasmtime and can be written in any language that compiles to WASM. Enable the experimental server feature explicitly:

```text
allow_experimental_webassembly_udf = true
webassembly_udf_engine = wasmtime
```

Registered modules appear in `system.webassembly_modules`. Treat module registration, resource limits, and upgrade compatibility as operational policy even though execution is sandboxed.

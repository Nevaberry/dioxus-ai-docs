---
name: clickhouse-knowledge-patch
description: ClickHouse
version: "26.7"
license: MIT
metadata:
  author: Nevaberry
---


# ClickHouse Knowledge Patch

Use this skill when writing, reviewing, upgrading, or operating ClickHouse SQL and server configurations. Start with the compatibility-sensitive items below, then load the topic reference that matches the task.

## How to apply this skill

1. Inspect the target server version, table engines, client settings, and relevant feature flags before generating SQL.
2. For upgrades, review changed defaults and removed compatibility paths before adopting new syntax.
3. Treat experimental features as explicit opt-ins and keep their configuration easy to remove.
4. For distributed or object-storage work, distinguish query settings, engine settings, server settings, named collections, and access-control grants.
5. Validate optimizer choices with `EXPLAIN`; do not assume a projection, index, cache, or parallel-replica path is selected merely because it exists.
6. Preserve operational safety around background work, credential inheritance, deduplication, and remote-query execution.

## Reference index

| Reference | Topics |
|---|---|
| [Upgrades, security, and settings](references/upgrades-security-and-settings.md) | Credential inheritance, removed settings, deduplication migration, changed defaults, access changes, terminal output |
| [Query language and functions](references/query-language-and-functions.md) | CTEs, `EXPLAIN`, time functions, aggregates, query parameters, dictionary lookup, hashing, JSON extraction |
| [Tables, indexes, and views](references/tables-indexes-and-views.md) | `MergeTree`, projections, text and hypothetical indexes, semi-structured types, constraints, refresh chains |
| [External data and formats](references/external-data-and-formats.md) | Object storage, lakehouse catalogs, URL dispatch, remote databases, Arrow Flight, GeoJSON, PNG |
| [Operations, integrations, and tooling](references/operations-integrations-and-tooling.md) | Background controls, workloads, Kafka and NATS, Keeper, dictionaries, PromQL, local listeners, streaming |
| [Vectors, geometry, and classifiers](references/vectors-geometry-and-classifiers.md) | `QBit`, quantization, Hadamard transforms, embedding generation, Naive Bayes, geometry and vector tiles |

## Breaking and security-sensitive changes

### Do not assume user queries inherit server cloud credentials

User SQL that accesses S3 must supply credentials or use `NOSIGN`. Named collections default `use_environment_credentials` to `0`. Restoring environment lookup requires both:

```text
use_environment_credentials = 1
s3_allow_server_credentials_in_user_queries = 1
```

The second setting is off by default. Persistent S3-backed objects denied server credentials load anonymously during startup or `RESTORE` while `s3_load_table_anonymously_if_credentials_restricted` remains enabled.

### Complete the insert-deduplication migration before upgrading

Only the unified insert hash is accepted. A server configured with `old_separate_hashes` or `compatible_double_hashes` fails at startup. Before the final upgrade from a legacy setting:

1. Run an intermediate release with `compatible_double_hashes`.
2. Keep it active for at least `replicated_deduplication_window_seconds` on replicated tables, or for `non_replicated_deduplication_window` inserts on non-replicated tables.
3. Remove `insert_deduplication_version` or set it to `new_unified_hash`.

### Replace removed and changed SQL behavior

- Replace `snowflakeToDateTime`, `snowflakeToDateTime64`, `dateTimeToSnowflake`, and `dateTime64ToSnowflake` with the corresponding names containing `SnowflakeID`; the deprecated-function switch no longer restores the old names.
- `toTime` returns `Time` with the default `use_legacy_to_time = 0`. Use `toTimeWithFixedDate` or explicitly enable the legacy behavior when fixed-date output is required.
- Use only `hasColumnInTable(database, table, column)`; the remote overload with host and credentials is gone.
- `DateTime64` has a much wider calendar range, but precisions 8 and 9 remain bounded by `Int64` ticks and nanosecond precision still tops out at `2262-04-11`.

### Update server and table configuration

- Server-config `resources` and `workload_classifiers` sections are ignored with a warning. Define scheduling through `CREATE RESOURCE` and `CREATE WORKLOAD`.
- `AggregatingMergeTree` rejects ordinary columns that are neither sorting-key dimensions nor aggregate-state measures. Use `allow_dimensions_outside_sorting_key = 1` only as a deliberate compatibility escape hatch.
- Asynchronous inserts are enabled by default; verify latency, acknowledgment, buffering, and deduplication assumptions in small-insert clients.
- Direct object-storage backups do not accept `zip` or `zipx`; choose a tar-based archive such as `tar.gz`.

## Query planning and indexing essentials

### Measure plans, not just estimates

`EXPLAIN ANALYZE SELECT ...` executes the query and adds runtime metrics to the standard plan. For static inspection, `pretty=1` renders a tree and `compact=1` collapses expression steps:

```sql
EXPLAIN indexes=1, pretty=1, compact=1
SELECT number FROM numbers(10);
```

### Reuse expensive CTEs

Enable `enable_materialized_cte`, then force one evaluation into a temporary table:

```sql
WITH expensive AS MATERIALIZED (
    SELECT key, sum(value) AS total FROM source GROUP BY key
)
SELECT * FROM expensive AS a JOIN expensive AS b USING (key);
```

### Test and target data skipping

- Filtered projections may include `WHERE`; the optimizer can use one when the query predicate implies the projection predicate.
- `CREATE HYPOTHETICAL INDEX` plus `EXPLAIN WHATIF` evaluates a session-local skip index without persisting it. Candidate construction reads data and counts against limits and quotas.
- A granularity-1 MinMax index can be generated for every numeric column with `add_minmax_index_for_numeric_columns = 1`.
- Text indexes require an explicit tokenizer and `enable_full_text_index = 1`; token postprocessors can normalize tokens after tokenization.

## External data and lakehouse essentials

### Route URLs by scheme deliberately

The `URL` engine and `url` function dispatch `file://`, standard S3-family, Azure, and `hdfs://` schemes to specialized implementations after applying `url_base`; HTTP(S) stays on `URL`. Non-default S3-compatible schemes still require the `s3` engine or function.

### Use remote queries as read-only sources

The `mysql`, `postgresql`, and `sqlite` engines and table functions accept `(SELECT ...)` or `query('SELECT ...')` instead of a table name. ClickHouse infers the result structure, and the resulting source is read-only.

### Account for object-storage path and access behavior

- `data/**/file.txt` now matches `data/file.txt` as well as deeper paths.
- `extra_credentials(role_arn = '...')` selects an IAM role for `s3`; grants can be scoped to an `S3('url-pattern')` resource.
- `partition_strategy = 'hive'` plus `PARTITION BY` writes Hive-style directories.
- Parallel replicas can automatically distribute cluster file processing; set `parallel_replicas_for_cluster_engines = 0` to opt out.

## Operations and streaming essentials

### Control background activity consistently

Use engine-agnostic `SYSTEM STOP`, `START`, `PAUSE`, `CANCEL`, and `REFRESH`, including `ALL BACKGROUND` forms, for queue engines and refreshable views. Treat these as service-impacting commands.

For NATS JetStream, acknowledgment follows successful insertion. `nats_wait_for_flush_interval` keeps consumption open through a flush interval, while `nats_commit_on_select` makes direct reads acknowledge consumed messages.

### Define workload memory through SQL

```sql
CREATE RESOURCE memory (MEMORY RESERVATION);
```

Workload hierarchies accept `max_memory` limits and `weight` shares; route queries with `SETTINGS workload = 'name'`.

### Use local and continuous execution intentionally

- In `clickhouse-local`, `SYSTEM START LISTEN TCP` and `SYSTEM START LISTEN HTTP` expose the current session; stop each listener explicitly when finished.
- With `enable_streaming_queries = 1`, `SELECT ... STREAM` remains open for new rows. A `CURSOR` can resume from `block_number` and `block_offset`.
- `QueryRunner` executes queries represented by inserted rows, which suits generated batches, benchmarks, fuzzing, routing, and shadow traffic.

## Common SQL additions

### Typed settings parameters

```sql
SELECT count()
FROM events
SETTINGS max_threads = {threads:UInt64};

SET max_threads = {threads:UInt64};
```

### Tuple aggregation and time-zone postfixes

```sql
SELECT sumTuple((a, b)) FROM t;
SELECT ts AT TIME ZONE 'UTC', ts AT LOCAL FROM t;
```

The `-Tuple` combinator aggregates corresponding tuple elements independently and preserves element names. Multi-argument aggregates pair positions across input tuples.

### Schema changes without restating definitions

```sql
ALTER TABLE events
    MODIFY CONSTRAINT IF EXISTS positive_value CHECK value > 0;

ALTER TABLE events
    MODIFY COLUMN kind ADD ENUM VALUES('archived' = 5);
```

### Preserve unrelated access settings

`ALTER USER`, `ALTER ROLE`, and `ALTER SETTINGS PROFILE` accept `SET name = value` as an alias for `MODIFY SETTING name = value`. Unlike a bare `SETTINGS` clause, this form leaves all other settings intact.

## Vector and geometry guardrails

- `QBit(Int8)` stores quantized vectors; strided `QBit(T, dimension, stride)` separates dimension groups into streams so transposed searches can read only an initial `used_dims` subset.
- Transposed and quantized distance functions are approximate. Keep the original precision available when recall or exact reranking matters.
- `randomHadamardTransform` is deterministic for a fixed seed and preserves norm; optional output truncation provides random projection before quantization.
- Experimental embedding functions require an explicit server-side credential collection and `allow_experimental_ai_functions = 1`.
- `geometryIntersectCartesian` and `geometryIntersectSpherical` accept differing supported geometry types, including the generic `Geometry` type.

Open the indexed references for complete syntax, settings, defaults, feature gates, and edge behavior before implementing a production change.

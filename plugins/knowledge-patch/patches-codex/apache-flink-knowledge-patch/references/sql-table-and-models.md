# SQL, Table API, and Models

## SQL syntax and core behavior

### Casting and query syntax (`1.20.1`, `2.0-migration`, `2.0.0`)

- `DOUBLE` values can be cast to `BOOLEAN`.
- C-style escape strings are supported.
- `QUALIFY` filters window-function results and is useful for Top-N and
  deduplication.
- A table function may appear directly in `FROM`; the older outer `TABLE(...)`
  wrapper remains valid.

```sql
SELECT *
FROM orders
QUALIFY ROW_NUMBER() OVER (
  PARTITION BY customer_id ORDER BY order_time DESC
) = 1;
```

### SQL correctness repairs

- Flink 2.0.1 makes `COUNT(*) FILTER (...)` honor the filter, serializes
  `LocalTime` values without seconds as valid SQL literals, and makes duplicate
  keys in `MAP` expressions deterministic. `Table.explainSql` also supports
  general `Catalog` implementations rather than casting to `AbstractCatalog`
  (`2.0.1`).
- Flink 2.1.1 fixes unbounded-preceding non-time range windows throwing an NPE,
  and fixes filtered `STDDEV` and `VAR` results (`2.1.1`).
- Flink 1.20.4 preserves SQL hints when multiple `SELECT` statements share a
  source, avoids validation stack overflow for functions under `SELECT`, allows
  programs containing `JSON_OBJECT` to compile, and supports default escape
  characters in `LIKE` settings (`1.20.4`).
- Flink 2.0.2 preserves `TIMESTAMP(3) ROWTIME` typing in streaming over-
  aggregates and restores SQL jobs using `CURRENT_TIMESTAMP` without a
  `CodeGenException` (`2.0.2`).
- Flink 2.2.1 supports `UNNEST` in a `LEFT JOIN` over a `NOT NULL` array, avoids
  duplicate `ORDER BY` generation for window-TVF views, handles custom types and
  serializers in joins, and permits queries over views containing
  `MATCH_RECOGNIZE` (`2.2.1`).
- Flink 2.1.3 prevents mini-batch group aggregation from silently dropping
  records and makes unordered `limit()` generate valid SQL (`2.1.3`).

## Catalog models, inference, and vector search

### Model definitions and inference (`2.0.0`, `2.1-migration`, `2.2-migration`)

- Flink CDC 3.3 Transform expressions can invoke supported chat and embedding
  models dynamically on captured changes. Flink SQL's separate model-definition
  and function syntax was still being refined in Flink 2.0.0.
- Java and Python Table APIs can define and manage model catalog objects.
- `ML_PREDICT` is a table-valued function for real-time inference over streaming
  data. It supports a built-in provider and custom provider interfaces.
- Model inference is also available directly in Table API pipelines.
- `VECTOR_SEARCH` performs online vector similarity search and real-time context
  retrieval, avoiding a separate persist-then-search-only workflow.

## Semi-structured and structured types (`2.1-migration`)

`VARIANT` holds typed scalars, arrays, and maps with string keys. Convert
JSON-formatted `VARCHAR` with `PARSE_JSON` or `TRY_PARSE_JSON`; Paimon supports
the type. User-defined objects can be declared with `STRUCTURED TYPE` directly
inside `CREATE TABLE` DDL, avoiding prior API type-equivalence problems.

```sql
SELECT PARSE_JSON('{"id": 1, "tags": ["new"]}');
```

### Nested nullability and casts (`2.2-migration`)

SQL row types enforce nested `NOT NULL` constraints rather than ignoring them.
Update queries that relied on nullable nested values, or temporarily restore the
old behavior with `table.legacy-nested-row-nullability`. Casts to `TIME` accept
precision 0 through 3 and reject invalid time strings. `BINARY` and `VARBINARY`
casts honor the requested target length.

## Materialized tables

### Operations and Paimon integration (`2.0-migration`, `2.0.0`)

Materialized Tables support schema and query updates and refresh-job submission
to YARN and Kubernetes. Native Paimon integration lets real-time and historical
refreshes share one declarative pipeline. In Flink 2.0.0, Paimon is the only
supported catalog for Materialized Tables. SQL can call Paimon maintenance
procedures for compaction and snapshot, branch, or tag management; procedures
accept named parameters and any subset of optional parameters.

### Defaults, bucketing, and discovery (`2.2-migration`)

- `FRESHNESS` is optional in `CREATE MATERIALIZED TABLE` and
  `CREATE OR ALTER MATERIALIZED TABLE`.
- `MaterializedTableEnricher` can supply customizable defaults.
- `DISTRIBUTED BY` and `DISTRIBUTED INTO` define bucketing.
- `SHOW MATERIALIZED TABLES` lists these objects.

### Explicit schema and evolution (`2.3-migration`, `2.3.0`)

- `CREATE MATERIALIZED TABLE` accepts an explicit column list, including
  watermarks and primary keys, before the `AS` query.
- `ALTER MATERIALIZED TABLE` can add, modify, or drop metadata and computed
  columns, and can rename with `RENAME TO`.
- `START_MODE` on create/alter chooses `FROM_BEGINNING`,
  `FROM_NOW[(interval)]`, `FROM_TIMESTAMP(timestamp)`, or a corresponding
  `RESUME_OR_*` form that reuses offsets when available. The default is
  `FROM_BEGINNING`.
- An evolution that creates a completely new physical plan still requires full
  reprocessing. Compatible changes such as adding a nullable column can often
  avoid historical re-ingestion.

## Process Table Functions

### Stateful operators (`2.1.0`)

`ProcessTableFunction` combines table arguments and emitted rows with managed
state, event time, timers, and changelogs. A set-semantics table argument can be
partitioned at the call site to scope processing and state by key.

```java
public static class GreetingWithMemory extends ProcessTableFunction<String> {
    public static class CountState { public long counter; }

    public void eval(
            @StateHint CountState state,
            @ArgumentHint(SET_SEMANTIC_TABLE) Row input) {
        state.counter++;
        collect("Hello " + input.getFieldAs("name") + ", visit " + state.counter);
    }
}
```

Flink 2.2.1 also allows `ProcessTableFunction` UDFs to load through
`CompiledPlan` (`2.2.1`).

### Late data and ordering (`2.3-migration`)

PTFs can react to late records rather than silently dropping them. Table
arguments accept `ORDER BY` after partitioning for deterministic temporal order:

```sql
MyPtf(input => TABLE t PARTITION BY k ORDER BY ts)
```

## Join planning

### Async lookup joins (`2.1-migration`)

For changelog input, async lookup joins can preserve record order inside each
planner-derived upsert key while processing different keys concurrently.

### Experimental streaming multi-join (`2.1.0`, `2.1.1`, `2.2-migration`, `2.1.2`)

Pipelines with multiple `INNER` or `LEFT` joins sharing a join key can opt into
one operator rather than materializing intermediate join results:

```sql
SET 'table.optimizer.multi-join.enabled' = 'true';
```

Its evolution matters:

- Flink 2.1.1 adds support for different source types and fixes row-kind use
  while manipulating state.
- Flink 2.2 changes state management from upsert keys to unique keys, which is a
  breaking state change for adopters of the experimental 2.1 operator.
- Flink 2.1.2 fixes OR-predicate results at parallelism greater than one and
  corrects `RowData` use with `HeapStateBackend`.

### Delta joins (`2.2-migration`, `2.1.2`)

Delta joins can consume CDC sources without `DELETE`, tolerate projections and
filters after the source, and cache lookups. Flink 2.1.2 also recognizes joins
whose key includes a source index and fixes a lookup-cache `ClassCastException`.

## Changelog conversion and sink conflicts (`2.3-migration`)

- `FROM_CHANGELOG` converts an append-only stream with an operation column into
  a dynamic table. `op_mapping` maps custom CDC formats and controls unmapped
  codes.
- `TO_CHANGELOG` converts retract or upsert tables to append-only streams for
  sinks, audit, or archival.
- Flink 2.3 supports basic conversions but not the planned `PARTITION BY`,
  `invalid_op_handling`, or `produces_full_deletes` extensions.
- When the query upsert key differs from the sink primary key, planning fails by
  default. `ON CONFLICT` must select `DO NOTHING`, `DO ERROR`, or
  `DO DEDUPLICATE`.

## Functions and compiled plans

- `CREATE FUNCTION ... USING ARTIFACT` is supported, with `ARTIFACT`
  interchangeable with `JAR`; both keywords may occur in one statement and old
  `USING JAR` statements remain valid (`2.3-migration`).
- Compiled plans use JSON by default and can use Smile via
  `CompiledPlan#asSmileBytes` and `PlanReference#fromSmileBytes`
  (`2.1-migration`).
- Flink 2.0.1 loads `AsyncScalarFunction` UDFs from compiled plans and preserves
  sink option hints through plan compilation (`2.0.1`).

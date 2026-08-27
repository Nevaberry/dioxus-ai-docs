# SQL, Table API, and Planning

Use this reference for SQL syntax and types, materialized tables, inference,
joins, Process Table Functions, compiled plans, and planner correctness.

Batch attribution: `1.20.1`, `2.0-migration`, `2.0.0`, `2.1-migration`,
`2.1.0`, `2.0.1`, `2.1.1`, `2.2-migration`, `2.0.2`, `2.1.2`, `2.2.1`,
`2.1.3`, `1.20.4`, `2.3-migration`, `2.3.0`.

## Syntax, types, and schema behavior

- SQL permits `DOUBLE` to `BOOLEAN` conversion (since 1.20.1), despite older
  documentation that marked it unsupported.
- C-style escape strings and `QUALIFY` are available. Use `QUALIFY` after
  window evaluation for Top-N, deduplication, and similar filters.
- A table function may appear directly in `FROM`; the older outer `TABLE(...)`
  wrapper remains valid.
- `VARIANT` preserves typed scalars, arrays, and string-keyed maps in a
  JSON-like value. Convert JSON-formatted `VARCHAR` with `PARSE_JSON` or
  `TRY_PARSE_JSON`; Paimon supports the type.
- Declare user-defined object types with `STRUCTURED TYPE` directly in
  `CREATE TABLE` DDL to avoid API/DDL type-equivalence mismatches.
- Nested row `NOT NULL` constraints are enforced. Update data and queries that
  depended on ignored nested nullability, or temporarily use
  `table.legacy-nested-row-nullability`.
- Casts to `TIME` enforce precision 0 through 3 and reject invalid strings.
  `BINARY` and `VARBINARY` casts honor target length.
- `ResolvedSchema#getPrimaryKeyIndexes()` reports physical-column indexes
  only. `ResolvedSchema` column inspection no longer fails because
  `getDataType` is missing (fixed in 2.2.1).
- `CREATE FUNCTION` accepts `USING ARTIFACT`; `ARTIFACT` and `JAR` are
  interchangeable and may both occur in one statement. Existing `USING JAR`
  statements remain valid.

## Materialized tables and Paimon

- Materialized tables support schema and query updates, real-time and
  historical refreshes in one declarative pipeline, YARN/Kubernetes refresh
  submission, and native Paimon integration.
- Paimon is the only supported materialized-table catalog in 2.0.0. SQL call
  procedures can invoke Paimon compaction and snapshot, branch, or tag
  maintenance with named parameters and any subset of optional parameters.
- `FRESHNESS` is optional in `CREATE MATERIALIZED TABLE` and
  `CREATE OR ALTER MATERIALIZED TABLE`. `MaterializedTableEnricher` can supply
  defaults. `DISTRIBUTED BY`/`DISTRIBUTED INTO` adds bucketing, and
  `SHOW MATERIALIZED TABLES` provides discovery.
- `CREATE MATERIALIZED TABLE` accepts an explicit column list—including
  watermarks and primary keys—before the `AS` query.
- `ALTER MATERIALIZED TABLE` can add, modify, or drop metadata/computed
  columns and rename a table with `RENAME TO`.
- `START_MODE` on create-or-alter and alter statements selects
  `FROM_BEGINNING`, `FROM_NOW[(interval)]`, `FROM_TIMESTAMP(timestamp)`,
  `RESUME_OR_FROM_BEGINNING`, `RESUME_OR_FROM_NOW`, or
  `RESUME_OR_FROM_TIMESTAMP`. Resume forms reuse offsets when available;
  `FROM_BEGINNING` remains the default.
- A query evolution that creates a completely new physical plan still needs
  full reprocessing. Compatible changes such as a nullable-column addition can
  often avoid historical re-ingestion.

## Inference and semi-structured workloads

- Java and Python Table API can define and manage catalog model DDL objects.
- `ML_PREDICT` applies a catalog-defined model to streaming SQL data using the
  built-in provider or a custom provider interface. Table API can also perform
  inference directly.
- `VECTOR_SEARCH` provides online vector similarity search and real-time
  context retrieval, extending workflows that previously stopped after
  embedding generation and persistence.
- Flink CDC 3.3 Transform expressions can invoke supported chat and embedding
  models on captured changes. This is distinct from Flink SQL's evolving model
  definition/function syntax.

## Lookup, delta, and multi-join planning

- Lookup connectors may request planner input distribution so lookup joins can
  partition records for a smaller, more effective connector cache.
- Async lookup joins over changelog input can preserve order within each
  planner-derived upsert key while processing different keys concurrently.
- Delta joins accept CDC sources without `DELETE`, allow projections and
  filters after the source, and can cache external lookups.
- A delta join is eligible when its join key includes one source index; cached
  delta joins no longer fail with `ClassCastException` (fixed in 2.1.2).
- The experimental multi-join operator combines cascaded `INNER`/`LEFT` joins
  sharing at least one key and avoids materializing intermediates. Enable
  `table.optimizer.multi-join.enabled` explicitly.
- Its state keys changed from upsert keys to unique keys in the 2.2 migration.
  Treat state from the earlier experimental form as incompatible.
- Patch fixes add mixed source types, stable row-kind handling, correct OR
  predicates above parallelism one, and correct `RowData` handling with
  `HeapStateBackend`.

## Process Table Functions and changelog conversion

- `ProcessTableFunction` combines table arguments and emitted rows with
  managed state, event time, timers, and changelogs. A set-semantics argument
  can be partitioned at the call site to scope state and processing by key.
- PTFs can react to late records instead of dropping them silently. Table
  arguments accept `ORDER BY` after `PARTITION BY` for deterministic temporal
  order.
- Compiled plans can load Process Table Function UDFs (fixed in 2.2.1).
- `FROM_CHANGELOG` converts an append-only stream with an operation column to a
  dynamic table. `op_mapping` supports custom CDC codes and controls unmapped
  operation values.
- `TO_CHANGELOG` converts retract or upsert tables to append-only streams for
  sinks, audits, or archives. Flink 2.3 supports basic cases only; planned
  `PARTITION BY`, `invalid_op_handling`, and `produces_full_deletes` extensions
  are not yet present.
- If the query upsert key differs from the sink primary key, planning fails by
  default. Choose `ON CONFLICT DO NOTHING`, `DO ERROR`, or `DO DEDUPLICATE`
  instead of relying on implicit full-history retention.

## Compiled plans and SQL correctness fixes

- Compiled plans use JSON by default and optionally Smile via
  `CompiledPlan#asSmileBytes` and `PlanReference#fromSmileBytes`.
- Async scalar UDFs load from compiled plans and sink option hints survive plan
  compilation (fixed in 2.0.1).
- `COUNT(*) FILTER (...)` honors its filter; `LocalTime` without seconds
  serializes as a valid SQL literal; duplicate-key `MAP` expressions are
  deterministic (fixed in 2.0.1).
- PyFlink `TO_TIMESTAMP_LTZ` accepts columns and other expressions, not just
  literals. `Table.explainSql` supports general catalog implementations rather
  than assuming `AbstractCatalog`.
- Unbounded-preceding non-time range windows no longer throw a null-pointer,
  and filtered `STDDEV`/`VAR` aggregates return correct results (2.1.1).
- Streaming over-aggregates accept `TIMESTAMP(3) ROWTIME` where
  `TIMESTAMP(3)` is expected, and restored jobs using `CURRENT_TIMESTAMP` no
  longer fail code generation (2.0.2).
- `UNNEST` works in a left join with a non-null array. Window-TVF views retain
  one `ORDER BY`; custom types/serializers no longer crash joins; views using
  `MATCH_RECOGNIZE` can be queried; user Scala libraries coexist with the
  table planner (2.2.1).
- Mini-batch group aggregation no longer silently drops affected records, and
  unordered `limit()` generates valid SQL (2.1.3).
- Shared-source planning preserves per-statement SQL hints. Function calls
  under `SELECT` no longer overflow validation, `JSON_OBJECT` programs compile,
  and `LIKE` settings accept default escape characters (1.20.4).

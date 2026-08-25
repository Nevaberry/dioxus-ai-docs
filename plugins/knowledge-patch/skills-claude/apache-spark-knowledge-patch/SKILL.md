---
name: apache-spark-knowledge-patch
description: Apache Spark
version: 4.2.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Spark Knowledge Patch

Use this skill when upgrading, configuring, extending, or debugging modern
Apache Spark applications. Check the application's Spark version before using
version-specific advice, and prefer the application's manifests, code, and
tests when they demonstrate different behavior.

## Reference index

| Reference | Topics |
| --- | --- |
| [references/migration-and-runtime.md](references/migration-and-runtime.md) | Core runtime defaults, compatibility switches, API corrections, and upgrade hazards |
| [references/sql-and-dataframes.md](references/sql-and-dataframes.md) | SQL semantics, parser and DDL changes, expressions, types, views, and DataFrame behavior |
| [references/data-sources-and-formats.md](references/data-sources-and-formats.md) | Data Source V2, JDBC, catalogs, file formats, schema evolution, and connector APIs |
| [references/streaming-and-state.md](references/streaming-and-state.md) | Structured Streaming triggers, checkpoints, state APIs, joins, and Python streaming sources |
| [references/python-and-pandas.md](references/python-and-pandas.md) | PySpark requirements, Arrow execution, pandas API on Spark, UDFs, exceptions, and inference |
| [references/connect-ml-and-pipelines.md](references/connect-ml-and-pipelines.md) | Spark Connect, Spark ML, Declarative Pipelines, client modes, and remote lifecycle APIs |
| [references/deployment-security-observability.md](references/deployment-security-observability.md) | Kubernetes, YARN, standalone deployment, security, metrics, logging, web UI, and History Server |
| [references/dependencies-and-packaging.md](references/dependencies-and-packaging.md) | Bundled libraries, language runtimes, build flags, packaging, and dependency alignment |

## Upgrade triage

Before changing code, identify whether the failure comes from a new default,
a removed compatibility alias, a stricter correctness check, or a genuinely
new API. Use the following order:

1. Pin the exact Spark runtime used by driver and executors.
2. Compare SQL, Python, streaming, storage, and deployment compatibility flags.
3. Confirm bundled dependency overrides match Spark's own dependency line.
4. Re-run query-result and checkpoint-restart tests, not only compilation.
5. Use a legacy switch only as a temporary migration step and document it.

## Breaking runtime and deployment defaults

- Servlet-facing integrations must use `jakarta`, not `javax`.
- Mesos support is removed.
- Event-log rolling and compression, worker cleanup, RocksDB shuffle-service
  storage, and deletion of deallocated-executor shuffle blocks are enabled by
  default. See the runtime reference for rollback settings.
- Kubernetes executor allocation grew first to 10 and then to 20 pods per
  batch. PVC access mode, all-container status checks, and executor network
  isolation also changed.
- Speculation is less aggressive: multiplier `3`, quantile `0.9`.
- The Master REST API is enabled by default; on Java 21 or later its REST
  handling uses virtual threads by default.
- Native Netty I/O, compressed RDD checkpoints, and the S3A Magic Committer
  are enabled by default.
- Alternative configuration aliases containing `*.blacklist.*` are ignored;
  migrate to the current names.
- Spark configuration byte sizes accept IEC suffixes such as `MiB` and `GiB`.

## Breaking SQL defaults

- ANSI mode defaults to enabled. Invalid operations and overflow may raise
  instead of returning permissive results. pandas API on Spark has separate
  ANSI compatibility controls.
- Bare `CREATE TABLE` uses `spark.sql.sources.default`, not Hive.
- `spark.sql.maxSinglePartitionBytes` defaults to `128m`.
- SQL file reads use `spark.sql.files.ignoreCorruptFiles` and
  `spark.sql.files.ignoreMissingFiles`; some security and missing-block errors
  remain hard failures.
- Negative-zero map keys normalize to positive zero, and array set operations
  now apply consistent `NaN` and negative-zero equality.
- CTE precedence and time parsing use corrected policies. Bang-negation forms
  such as `! IN` no longer parse.
- Format-string argument indexes are one-based.
- Empty grouping sets produce one grand-total row over empty input.
- `NATURAL JOIN` honors case sensitivity, while duplicate CTE names are
  rejected case-insensitively.
- System namespaces can take precedence over persistent objects named
  `builtin` or `session`; qualify the catalog or use the legacy setting when
  resolving a collision.

## Data and connector migration checks

- Revalidate JDBC type mappings for PostgreSQL, MySQL, Oracle, SQL Server, and
  DB2; compatibility flags exist for the previous mappings.
- Hive metastores older than 2.0.0 are unsupported. Hive Metastore 4.1 is
  supported by newer runtimes.
- Parquet uses `lz4_raw`, not `lz4raw`; ORC defaults to `zstd` rather than
  `snappy`.
- Datetime-rebase settings no longer use the legacy-prefixed names.
- Per-query file-source options are honored, and newer per-write options take
  precedence over session configuration.
- Connector `CustomTaskMetric` implementations must override `mergeWith` for
  non-additive metrics.
- Python data sources must return Arrow column types matching their declared
  schema and must advance streaming offsets for every non-empty batch.

## PySpark migration checks

- Do not rely on wildcard imports to provide `DataFrame`, `Column`, or Spark
  SQL types; import them from their owning modules.
- `PySparkException.getCondition()` replaces the deprecated
  `getErrorClass()`, and exceptions can expose SQLSTATE.
- Binary values map to Python `bytes` by default.
- Safe Arrow conversion is enabled, and regular Python exchange, UDF, and
  UDTF paths increasingly default to Arrow.
- NumPy-array DataFrame creation converts through PyArrow; review schema
  inference where NumPy dtype behavior mattered.
- Spark Connect defers invalid-column checks for both `__getitem__` and
  attribute access. Use `PYSPARK_VALIDATE_COLUMN_NAME_LEGACY=1` only while
  migrating code that depends on eager failures.
- pandas API on Spark removals follow current pandas names: prefer `items`,
  `concat`, `bfill`, `ffill`, and the current index and option APIs.
- Missing labels in pandas API `drop` now raise `KeyError` if any requested
  label is absent; use `errors="ignore"` where appropriate.

## Streaming and state checkpoints

- `AvailableNow` falls back to a single batch if any source lacks native
  support.
- Stateless streaming has AQE enabled by default.
- A checkpoint containing offset or commit logs but no metadata file is
  rejected; restore metadata, choose a new checkpoint, or temporarily disable
  verification.
- Stable source and sink names allow sources to be reordered without
  invalidating checkpoints. Names must remain stable after deployment.
- State stores can repair snapshots and use row checksums. Snapshot upload on
  lag forces the next commit to create a snapshot.
- Close RocksDB state-store iterators explicitly.
- Python simple stream readers must advance their end offset after emitting a
  non-empty batch.

## High-value feature selection

Use the narrowest API that matches the workload:

- Use SQL `EXECUTE IMMEDIATE` for dynamic SQL and SQL scripting for procedural
  control flow; recursive CTEs, cursors, and query parameter markers cover
  common orchestration needs.
- Use `MERGE` schema evolution or writer `mergeInto` for merge workloads.
  Newer inserts support schema evolution, replacement predicates, and
  by-name replacement.
- Use `VARIANT` for semi-structured values and native `GEOMETRY` or
  `GEOGRAPHY` for geospatial data.
- Use `CHANGES` or `changes()` for Data Source V2 change-data-capture reads.
- Use `NEAREST BY` for top-K nearest-neighbor joins and metric views for
  declarative semantic metrics.
- Use `TransformWithState` APIs for multiple state variables, timers, TTL,
  initial state, and schema evolution. Use the state data source for
  inspection and change feeds.
- Use stable streaming names when changing a deployed topology.
- Use Spark Connect mode when a thin remote client is desired; classic mode
  remains available through `spark.api.mode`.
- Use Declarative Pipelines when Spark should derive graph ordering,
  parallelism, checkpointing, and retries; Auto CDC supplies SCD Type 1 flows.

## Connector-author checklist

- Test catalog, procedure, function, namespace, view, constraint, transaction,
  join-pushdown, CDC, and partition-predicate capabilities independently.
- Verify append, overwrite, replacement, schema evolution, defaults, and
  metadata-only operations through both SQL and DataFrame writers.
- Preserve temporary-object behavior when the session catalog is not
  `V2SessionCatalog`.
- Treat paths as decoded values and honor `DataFrameWriterV2`'s `path` option.
- Validate Parquet field-ID mapping, missing-struct projections, annotations,
  and nested partition predicates.
- Exercise time travel, metadata columns, clustering, grouping sets, and
  stored-procedure loading where supported.
- For Java callers of Scala-facing APIs, verify Java varargs forwarders and
  Java-friendly factory/getter surfaces.

## Operational verification

After an upgrade, run targeted checks for:

- query results involving maps, floating point, grouping sets, semi joins,
  cubes, decimals, timestamps, collations, and nulls;
- file reads with corrupt or missing inputs and overridden query options;
- JDBC round trips for native timestamp, integer, bit, and boolean types;
- restart from every production streaming checkpoint and state-store provider;
- event-log ingestion, rolling-log loading, redaction, and large values;
- shuffle cleanup with and without AQE, remote-disk RDD blocks, and executor
  decommissioning;
- Kubernetes allocation, PVC behavior, network policy, pod status, and
  heterogeneous executor resizing;
- Python UDF/UDTF Arrow types, nullability, overflow, binary values, and worker
  logging;
- Connect operation retry, cancellation, session release, and History Server
  visibility;
- UI error-stack policy, SNI host checking, CSP headers, and secret redaction.

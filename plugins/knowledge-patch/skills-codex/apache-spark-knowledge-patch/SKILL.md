---
name: apache-spark-knowledge-patch
description: Apache Spark
version: 4.2.0
license: MIT
metadata:
  author: Nevaberry
---


# Apache Spark Knowledge Patch

Use this skill when upgrading Spark applications, changing Spark SQL or
PySpark code, implementing Data Source V2 connectors, operating Structured
Streaming, using Spark Connect, or adjusting deployment and security
configuration. Start with the migration hazards below, then open the reference
whose topic matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [migration-and-configuration.md](references/migration-and-configuration.md) | Changed defaults, compatibility switches, removed settings, SQL semantics, Python requirements |
| [sql-and-dataframes.md](references/sql-and-dataframes.md) | SQL syntax and functions, types, views, scripting, DataFrame behavior, query correctness |
| [data-sources-and-connectors.md](references/data-sources-and-connectors.md) | Data Source V2, file formats, JDBC, catalogs, file writes, bundled dependencies |
| [python-and-pandas.md](references/python-and-pandas.md) | PySpark, pandas API on Spark, Arrow, Python UDFs and UDTFs, packaging |
| [streaming-and-state.md](references/streaming-and-state.md) | Structured Streaming, checkpoints, state APIs, state stores, source and sink identity |
| [connect-ml-and-extensions.md](references/connect-ml-and-extensions.md) | Spark Connect, ML, Declarative Pipelines, encoders, extension-facing APIs |
| [operations-security-and-observability.md](references/operations-security-and-observability.md) | Kubernetes, YARN, event logs, metrics, UI, build controls, redaction and transport security |

## Upgrade triage

Before changing application code, identify the Spark line used by the driver,
executors, clients, connectors, shuffle service, and History Server. Mixed
components make changed defaults and bundled dependency versions especially
important.

1. Audit removed runtime support and namespace changes.
2. Compare all explicitly set legacy switches with the changed defaults.
3. Re-run SQL tests with ANSI mode, parser, collation, view, map-key, and JDBC
   mapping behavior in mind.
4. Exercise checkpoints and state stores from a copy of production metadata.
5. Test Python schemas and UDF results through the Arrow path actually used in
   deployment.
6. Recompile connector and extension code against the target artifacts.
7. Review externally visible REST, UI, logging, and Kubernetes behavior.

## Highest-impact breaking changes

### Application and runtime boundaries

- Servlet-facing integrations must use the `jakarta` namespace after the 4.0
  migration; `javax` servlet types no longer match Spark's interfaces.
- Mesos resource-manager support is removed.
- PySpark drops Python 3.8 in 4.0, Python 3.9 in 4.1, and official PyPy support
  in 4.2. Check pandas, NumPy, and PyArrow floors in the migration reference.
- Spark 4.2 can build and run on Java 25, while R 3.x is no longer supported.
- The old `*.blacklist.*` configuration aliases are ignored in 4.1; use their
  current names.

### SQL behavior

- `spark.sql.ansi.enabled` defaults to `true` in 4.0. Invalid operations,
  overflow, parsing, and pandas API on Spark behavior may now fail rather than
  return permissive results.
- Bare `CREATE TABLE` follows `spark.sql.sources.default` instead of defaulting
  to Hive. Use `spark.sql.legacy.createHiveTableByDefault=true` only as a
  transition.
- File table reads use `spark.sql.files.ignoreCorruptFiles` and
  `spark.sql.files.ignoreMissingFiles`; `AccessControlException` and
  `BlockMissingException` remain hard failures.
- Floating-point map keys normalize `-0.0` to `0.0`; array set operations and
  `collect_set` later apply consistent Spark equality to negative zero and
  `NaN`.
- SQL's `system.builtin` and `system.session` namespaces can take precedence
  over persistent two-part names. Qualify the catalog or enable
  `spark.sql.legacy.persistentCatalogFirst` where collisions exist.
- Duplicate CTE names are rejected case-insensitively, while `NATURAL JOIN`
  key matching honors `spark.sql.caseSensitive`.

### Python and Arrow

- Columnar PySpark exchange and regular Python UDFs and UDTFs use Arrow by
  default in 4.2. Disable the individual Arrow settings only while resolving a
  compatibility issue.
- Safe Arrow conversion defaults on in 4.1, turning integer overflow,
  truncation, and precision loss into errors.
- Binary SQL values map consistently to Python `bytes` in 4.1 rather than
  `bytearray`.
- NumPy `ndarray` DataFrame creation goes directly through Arrow in 4.2 and
  requires PyArrow; inferred schemas can differ from the old path.
- Spark Connect delays Python column validation in `__getitem__` and later
  `__getattr__`. Use `PYSPARK_VALIDATE_COLUMN_NAME_LEGACY=1` temporarily when
  callers require eager errors.

### Streaming and state

- An `AvailableNow` query falls back to a single batch when any source lacks
  native support.
- AQE defaults on for stateless streaming in 4.1. Disable
  `spark.sql.adaptive.streaming.stateless.enabled` when validating a
  partitioning regression.
- A checkpoint containing commit or offset logs but no metadata file fails in
  4.2. Restore the metadata or start from a new checkpoint; bypass verification
  only with an explicit duplicate-write risk assessment.
- Python simple stream readers must advance their end offset whenever they
  return a non-empty batch.
- Stable source and sink names allow streaming graph reordering without
  invalidating checkpoints; name nodes before evolving a durable query.

## Changed-default quick reference

| Area | Current behavior | Compatibility control |
| --- | --- | --- |
| Event logs | Rolling and compression enabled | `spark.eventLog.rolling.enabled=false`, `spark.eventLog.compress=false` |
| Worker cleanup | Periodic cleanup enabled | `spark.worker.cleanup.enabled=false` |
| Shuffle service | RocksDB and removal of obsolete blocks | `spark.shuffle.service.db.backend=LEVELDB`, `spark.shuffle.service.removeShuffle=false` |
| Kubernetes allocation | Batch 10 in 4.0, then 20 in 4.2 | Set `spark.kubernetes.allocation.batch.size` explicitly |
| Kubernetes PVC access | `ReadWriteOncePod` | `spark.kubernetes.legacy.useReadWriteOnceAccessMode=true` |
| Speculation | Multiplier `3`, quantile `0.9` | Set the earlier `1.5` and `0.75` values explicitly |
| Single partition | `spark.sql.maxSinglePartitionBytes=128m` | Set `9223372036854775807` for the prior unlimited value |
| ORC compression | `zstd` | Set the codec explicitly when readers require another format |
| CTE precedence | `CORRECTED` | Set `spark.sql.legacy.ctePrecedencePolicy` only for transition |
| Time parsing | `CORRECTED` | Set `spark.sql.legacy.timeParserPolicy` only for transition |
| Master REST API | Enabled in 4.1 | `spark.master.rest.enabled=false` |
| RDD checkpoints | Compressed in 4.1 | `spark.checkpoint.compress=false` |
| S3A Magic Committer | Enabled for all buckets in 4.1 | `spark.hadoop.fs.s3a.committer.magic.enabled=false` |
| Netty I/O | Native mode in 4.1 | `spark.io.mode.default=NIO` |
| Arrow safety | Checked conversion in 4.1 | `spark.sql.execution.pandas.convertToArrowArraySafely=false` |
| Master REST threads | Virtual threads on Java 21+ in 4.2 | `spark.master.rest.virtualThread.enabled=false` |

## High-value SQL and connector additions

- SQL scripting is enabled and GA, with handlers, multiple-variable
  declarations, and later cursor support.
- Recursive CTEs, query parameter markers, `QUALIFY`, metric views, and
  `NEAREST BY` expand native query composition.
- `VARIANT` is GA with file-format support, shredding metadata, and colon field
  access. Spark 4.2 also adds native `GEOMETRY` and `GEOGRAPHY` types.
- Schema-evolving `MERGE` and `INSERT`, replacement inserts, and
  `DataFrameWriterV2.MergeInto` reduce connector-specific write logic.
- Data Source V2 gains CDC reads, multi-operation transactions, broader view
  DDL, metadata-only tables, partition-stat predicates, procedures, functions,
  constraints, and join pushdown.
- V1 inserts enforce `NOT NULL`; per-write options override session settings;
  dynamic partition overwrite with `PathOutputCommitProtocol` replaces the
  affected partitions.

## High-value streaming and Python additions

- `TransformWithState` v2 supports multiple state variables, column families,
  timers, initial state, TTL, batch operation, and Avro-backed evolution.
- The state data source can inspect snapshots, change feeds, timers, operator
  metadata, and value, list, or map state.
- Stateless real-time mode begins with Scala and later gains a PySpark trigger.
- Python data sources support DSv2 writes, Arrow writers, filter pushdown,
  streaming writes, admission control, and `AvailableNow`.
- Arrow-native decorators and iterator APIs cover scalar, table, grouped, and
  grouped-aggregate UDF or UDTF workloads.
- PySpark can interrupt tagged operations, add artifacts, create DataFrames
  from PyArrow tables, and perform schema-evolving `mergeInto`.

## High-value Connect, deployment, and security additions

- `spark.api.mode` selects Connect or classic behavior. Connect provides a
  lightweight Python client, Java compatibility, Scala Dataset parity, a JDBC
  driver, ML support, status APIs, and remote lifecycle controls.
- Declarative Pipelines manage graph ordering, parallelism, checkpoints, and
  retries; Auto CDC flows implement streaming SCD Type 1 upserts.
- Kubernetes gains Deployment API support, heterogeneous executor and PVC
  resize plugins, and a Stable resource-manager API.
- RPC supports AES-GCM and separate JKS key passwords.
- UI controls cover SNI host checks, Content-Security-Policy headers, and
  stack-trace suppression. JDBC URLs, job descriptions, Worker JSON, and
  temporary files receive stronger sensitive-output handling.

## Validation focus

For an upgrade, validate behavior rather than only compilation:

- Compare query results for ANSI errors, null handling, `NaN`, negative zero,
  collations, grouping sets, natural joins, and JDBC type mappings.
- Inspect physical plans for AQE, pushdown, runtime filters, and partition
  behavior.
- Verify file writes with null constraints, dynamic overwrite, schema
  evolution, compression, and format annotations.
- Restart streaming queries from representative checkpoints and inspect state
  repair, source identity, and commit behavior.
- Test UDF and data-source boundaries with nulls, nested UDTs, multiple Arrow
  batches, nullable integer dtypes, and declared-schema mismatches.
- Confirm log processors, metrics consumers, REST exposure, network policy,
  History Server loading, redaction, and dependency overrides.

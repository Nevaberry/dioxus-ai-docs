---
name: trino-knowledge-patch
description: Trino
version: 483
license: MIT
metadata:
  author: Nevaberry
---


# Trino Knowledge Patch

Use this skill when upgrading, configuring, querying, extending, or
troubleshooting Trino. Start with the upgrade hazards below, then open the
topic reference that matches the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrading-and-correctness.md](references/upgrading-and-correctness.md) | Unsafe releases, runtime requirements, removals, renamed or defunct settings, and correctness fixes |
| [sql-language-and-functions.md](references/sql-language-and-functions.md) | SQL syntax, types, functions, DDL, time travel, authorization statements, and query semantics |
| [server-operations-security-observability.md](references/server-operations-security-observability.md) | Cluster configuration, exchange managers, resource groups, Web UI, authentication, logging, metrics, tracing, and listeners |
| [clients-and-drivers.md](references/clients-and-drivers.md) | JDBC, CLI, protocol spooling, authentication tokens, headers, and client-visible types and statistics |
| [lakehouse-and-object-storage.md](references/lakehouse-and-object-storage.md) | Delta Lake, Hive, Hudi, Iceberg, Lakehouse, native object storage, metadata tables, and maintenance |
| [connectors-and-integrations.md](references/connectors-and-integrations.md) | Database and service connectors, type mappings, pushdown, connector-specific configuration, additions, and removals |
| [spi-and-plugin-development.md](references/spi-and-plugin-development.md) | Connector, block, type, event-listener, function, dynamic-filter, and materialized-view SPI migrations |

## Upgrade blockers first

### Avoid release 473

Release 473 can return incorrect `GROUP BY` and `DISTINCT` results when a query
has more than 33 million unique groups. Use release 474 or later. Release 474
can overcount memory and raise `EXCEEDED_LOCAL_MEMORY_LIMIT`; that defect is
fixed in release 475.

### Match the Java runtime

- The JDBC driver and CLI require Java 11 or newer.
- The server requires JDK 24 starting with release 476.
- Building and running the server requires JDK 25 starting with release 479.
- The BigQuery and Snowflake connectors require
  `--sun-misc-unsafe-memory-access=allow` on the applicable runtime.
- The Ignite connector requires
  `--add-opens=java.base/java.util=ALL-UNNAMED`.

### Remove unavailable components

- Kinesis was removed.
- Kudu and Phoenix were removed.
- Vertica was removed.
- RPM packages are no longer published; use a tarball, container image, or a
  locally built RPM.
- The HTTP server event-listener plugin is no longer bundled with the server
  or container.
- Every catalog must be deployed on every node.

### Complete object-storage migration

Delta Lake, Hive, Iceberg, and Lakehouse catalogs must use native Azure, GCS,
S3, or S3-compatible file-system support. Legacy object-store support was
removed; `fs.hadoop.enabled` now applies only to HDFS. Hudi also uses the
current native storage properties described in the lakehouse reference.

For native S3 authentication, set `s3.auth-type` explicitly:

```properties
s3.auth-type=WEB_IDENTITY
```

Use `ANONYMOUS` for public buckets and `IAM_ROLE` whenever `s3.iam-role` is
configured. Remove `s3.use-web-identity-token-credentials-provider`.

### Purge defunct configuration

Before starting an upgraded cluster, remove or replace these high-impact
settings:

- Replace HTTP client prefixes `workerInfo` and `memoryManager` with
  `worker-info` and `memory-manager`.
- Remove `optimizer.optimize-hash-generation` and the
  `optimize_hash_generation` session property.
- Remove `task.statistics-cpu-timer-enabled`.
- Remove `prefer_streaming_operators`.
- Replace `s3.socket-read-timeout` with `s3.socket-timeout`.
- Replace `gcs.use-access-token` with `gcs.auth-type`; use
  `APPLICATION_DEFAULT` when appropriate.
- Replace `hive.s3.storage-class-filter` with `hive.s3-glacier-filter`.
- Replace `fs.cache.preferred-hosts-count` with the coordinator setting
  `node-scheduler.cache-preferred-hosts-count`.
- Remove the dynamic-filter settings, Delta Lake live-files cache settings,
  removed shared lakehouse properties, and removed Iceberg extended-statistics
  settings listed in the upgrade reference.

## SQL quick reference

### Query-scoped properties

Use `WITH SESSION` to apply properties to one `SELECT`; parameters are accepted
in `WITH SESSION`, `SET SESSION`, and `CALL`.

```sql
WITH SESSION query_max_execution_time = '2m'
SELECT * FROM system.runtime.queries;
```

### Name-aligned and automatic grouping

```sql
SELECT orderkey, totalprice FROM current_orders
UNION CORRESPONDING
SELECT orderkey, totalprice FROM archived_orders;

SELECT region, status, count(*)
FROM orders
GROUP BY AUTO;
```

### New relational forms

- `PIVOT` turns distinct row values into columns.
- `NEAREST` performs approximate join matching.
- `MATCH` and `UNIQUE` predicates, `BETWEEN SYMMETRIC` and
  `BETWEEN ASYMMETRIC`, and truth-value predicates are available.
- Simple `CASE` can place predicates directly in `WHEN`.
- `(start_time, end_time) OVERLAPS (other_start, other_end)` tests temporal
  overlap.

### JSON access

Use dotted and subscripted access on `json`, typed accessor methods for
conversion, and `j.*` to collect top-level members:

```sql
SELECT j.customer.name, j.items[0].price.decimal(18,2), j.*
FROM orders;
```

SQL/JSON paths also support `like_regex` and `datetime()`. `JSON_QUERY` cannot
use `OMIT QUOTES` when returning `json`.

### Defaults, ownership, and refresh

```sql
CREATE TABLE orders (id bigint, status varchar DEFAULT 'pending');
ALTER TABLE orders ALTER COLUMN status SET DEFAULT 'pending';
ALTER TABLE orders ALTER COLUMN status DROP DEFAULT;
ALTER MATERIALIZED VIEW lake.sales.monthly SET AUTHORIZATION USER analyst;
ALTER VIEW reporting.orders REFRESH;
```

Column defaults are connector-dependent; the Memory connector implements the
documented create, add, set, and drop operations.

### Time travel and branches

Delta Lake supports `FOR TIMESTAMP AS OF`. Version and timestamp time-travel
clauses accept query parameters. Trino can also manage and query table
branches; connector access control receives the selected branch.

## Lakehouse quick reference

### Prefer safe maintenance APIs

- Use Iceberg's table-level `rollback_to_snapshot`; the
  `system.rollback_to_snapshot` procedure is deprecated.
- `optimize_manifests`, `expire_snapshots`, `remove_orphan_files`, `add_files`,
  and `add_files_from_table` have the capabilities and metrics documented in
  the lakehouse reference.
- Iceberg `OPTIMIZE` fails safely if a `NOT NULL` column contains nulls.
- Delta Lake `vacuum`, replacement, deletion-vector, checkpoint, and indexed
  Parquet fixes matter when repairing or validating affected tables.

### Treat metadata schemas as versioned APIs

Iceberg metadata tables gained new columns and, in the case of `$files`
`lower_bounds` and `upper_bounds`, changed types. Review dependent SQL before
upgrading dashboards or maintenance jobs. Materialized views can be queried
through Iceberg metadata tables.

### Tune writer and split limits deliberately

Lakehouse connectors expose Parquet row-group row caps. Hive and Iceberg now
have format-specific split settings, and Iceberg write-size properties persist
under Iceberg-native property names. Removed aliases and session properties
must not remain in automation.

## Connector quick reference

- ClickHouse requires ClickHouse 24.3 or newer, or Altinity 22.3 or newer.
- PostgreSQL requires version 12 or newer.
- DuckDB, Loki, and Lakehouse connectors are available.
- `MERGE` support includes Ignite and MySQL; PostgreSQL supports it with
  `retry_policy=TASK`.
- Updates assigning `NULL` work across the listed relational connectors.
- Character range pushdown is intentionally restricted for MySQL and SQL
  Server to preserve trailing-space semantics.

## SPI quick reference

Plugin upgrades require a coordinated source migration:

- Implement `Connector.shutdown()` and use
  `ConnectorPageSource.getNextSourcePage()`.
- Remove connector-level event listeners and obsolete event-listener methods.
- Replace removed type-parameter classes with `TypeParameter`.
- Stop using removed `Type.getObject`, `Type.appendTo`, and the old
  `Type.getObjectValue` signature.
- Adapt dynamic-filter split APIs to columns and `DynamicFilterSnapshot`.
- Direct block construction must use bit-packed validity; builder-based code
  does not require that direct representation change.

Read the SPI reference before compiling a connector because several related
interfaces changed together.

## Working method

1. Identify the deployed server release, Java runtime, and affected catalogs.
2. Read the upgrade and correctness reference before changing configuration.
3. Open the task-specific reference and search for the exact property, method,
   connector, SQL construct, or metadata table.
4. Prefer the newest stated behavior when a later release reverses or removes
   an earlier one.
5. Validate changed SQL against representative nulls, high precision values,
   old file encodings, and connector pushdown boundaries where relevant.
6. Validate configuration on every node, especially catalog files, JVM
   options, authentication selection, and removed properties.

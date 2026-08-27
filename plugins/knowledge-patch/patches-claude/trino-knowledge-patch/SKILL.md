---
name: trino-knowledge-patch
description: Trino
version: "483"
license: MIT
metadata:
  author: Nevaberry
---


# Trino Knowledge Patch

Use this skill when a task involves Trino SQL, upgrades, configuration,
connectors, clients, or plugin development. Start with the quick references
below, then open the topic file that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [upgrade-and-correctness.md](references/upgrade-and-correctness.md) | Unsafe releases, runtime requirements, removals, migrations, and correctness fixes |
| [sql-language-and-functions.md](references/sql-language-and-functions.md) | SQL syntax, types, functions, JSON, geospatial behavior, planning, and lineage |
| [lakehouse-and-storage.md](references/lakehouse-and-storage.md) | Delta Lake, Hive, Hudi, Lakehouse, object storage, exchange storage, Parquet, and ORC |
| [iceberg.md](references/iceberg.md) | Iceberg catalogs, table properties, metadata, maintenance, v3, and safety |
| [connectors.md](references/connectors.md) | Database, analytics, synthetic-data, messaging, and specialized connectors |
| [operations-security-and-clients.md](references/operations-security-and-clients.md) | Runtime, config, auth, resource groups, observability, Web UI, JDBC, and CLI |
| [spi-and-plugins.md](references/spi-and-plugins.md) | Connector SPI, event APIs, types, blocks, functions, pushdown, and pruning |

## How to apply this patch

1. Determine the deployed Trino version and the versions of clients and plugins.
2. For upgrades, read the upgrade reference before changing configuration.
3. For SQL behavior, check both syntax and correctness notes; several changes
   alter results rather than merely enabling new syntax.
4. For lakehouse catalogs, separate shared native-file-system settings from
   connector-specific settings.
5. For custom plugins, compile against the target SPI and migrate removed APIs;
   deprecated compatibility paths are not sufficient for current releases.
6. Prefer the repository's manifests, configuration, code, and tests if they
   show behavior more specific than this general guidance.

## Breaking changes first

### Avoid release 473

Do not deploy release 473. Large `GROUP BY` or `DISTINCT` operations with more
than 33 million unique groups can return incorrect results. Release 474 fixes
that defect, but 474 can overcount memory and raise
`EXCEEDED_LOCAL_MEMORY_LIMIT`; release 475 fixes the memory accounting.

### Use the required Java runtime

Build and run current Trino with JDK 25. JDBC and CLI need Java 11 or newer.
When BigQuery or Snowflake is installed, include:

```text
--sun-misc-unsafe-memory-access=allow
```

When Ignite is installed, also include:

```text
--add-opens=java.base/java.util=ALL-UNNAMED
```

### Remove retired components

- Kinesis, Kudu, Phoenix, and Vertica connectors have been removed.
- The `glue-v1` metastore type and deprecated Databricks Unity Catalog
  integrations have been removed.
- RPM packages are not distributed.
- The HTTP server event-listener plugin is not bundled with the server or image.
- Every catalog must be installed on every node.

### Migrate native object storage

Delta Lake, Hive, Iceberg, and Lakehouse catalogs must use native clients for
Azure Storage, GCS, IBM Cloud Object Storage, S3, and S3-compatible storage.
`fs.hadoop.enabled` applies only to HDFS. Alluxio exchange and file-system
support is gone, although its file-system cache remains supported.

For S3, make authentication explicit:

```properties
s3.auth-type=WEB_IDENTITY
```

Use `ANONYMOUS` for public buckets and `IAM_ROLE` whenever `s3.iam-role` is set.
Replace `s3.use-web-identity-token-credentials-provider`; it is removed.

For GCS, use `gcs.auth-type`, not removed `gcs.use-access-token`. Application
default credentials use:

```properties
gcs.auth-type=APPLICATION_DEFAULT
```

### Remove defunct core settings

Delete the following before or during migration:

- `optimize_hash_generation` and `optimizer.optimize-hash-generation`
- `prefer_streaming_operators`
- `task.statistics-cpu-timer-enabled`
- `enable-large-dynamic-filters` and `enable_large_dynamic_filters`
- `dynamic-filtering.small*` and `dynamic-filtering.large-broadcast*`
- `deprecated.http-server.authentication.oauth2.groups-field`

Also rename HTTP client prefixes `workerInfo` and `memoryManager` to
`worker-info` and `memory-manager`.

## Correctness triage

When investigating suspicious results, first check the fixes involving:

- Delta deletion vectors, `vacuum`, replacement DDL, indexed-Parquet deletes,
  and failed-write cleanup
- Iceberg change tables, equality deletes, concurrent `MERGE`, partition
  evolution, and optimization of invalid `NOT NULL` data
- spilled grouping, row types, row-pattern `FIRST`, window `DISTINCT`, and
  `IS NOT DISTINCT FROM`
- high-precision JSON, `number` values, decimal casts, floating underflow, and
  rows wider than 64 fields
- spatial joins, geometry tiling, and the Esri-to-JTS geometry migration
- old-PyArrow Parquet, mismatched decimal metadata, and Hive SerDe timestamps

Read the full correctness matrix before attributing these symptoms to data
corruption.

## SQL quick reference

Per-query properties use `WITH SESSION`:

```sql
WITH SESSION query_max_execution_time = '2m'
SELECT * FROM system.runtime.queries;
```

Columns can be positioned where the connector supports it:

```sql
ALTER TABLE customers
ADD COLUMN middle_name varchar AFTER first_name;
```

Name-aligned sets and automatic grouping are available:

```sql
SELECT orderkey, totalprice FROM current_orders
UNION CORRESPONDING
SELECT orderkey, totalprice FROM archived_orders;

SELECT region, status, count(*)
FROM orders
GROUP BY AUTO;
```

Recent relational and expression syntax includes `PIVOT`, `NEAREST` joins,
`MATCH`, `UNIQUE`, `OVERLAPS`, `AT LOCAL`, named function arguments, method-style
functions, predicate `CASE` arms, and named row fields.

JSON supports dotted and subscript access with typed methods:

```sql
SELECT j.customer.name, j.items[0].price.decimal(18,2), j.*
FROM orders;
```

`number` interoperates with boolean, JSON, Python UDFs, and Iceberg materialized
views. Character coercion now flows from `char` to trimmed `varchar` semantics;
use the legacy coercion setting only as a temporary bridge.

## Iceberg quick reference

- Prefer table-level `rollback_to_snapshot`; the system procedure is deprecated.
- Use `optimize_manifests`; it works on tables without snapshots.
- Iceberg v3 supports writes, deletes, maintenance, column defaults, row lineage,
  nanosecond timestamps, spatial types, and experimental variants.
- `$files` bounds are typed rows, so update numeric subscripts and JSON casts.
- REST catalogs support IAM/SigV4, OAuth exchange, BigLake, vended credentials,
  custom headers, prefixed paths, and Application Default Google credentials.
- `OPTIMIZE` now fails safely when invalid nulls occur in `NOT NULL` columns.

## Operations quick reference

- The redesigned Web UI is at `/ui`; the former UI is at `/ui/legacy` and needs
  `web-ui.legacy.enabled=true`.
- `log.console-format=JSON` enables structured console logging.
- `tracing.exporter.protocol=http/protobuf` selects HTTP protobuf trace export.
- `retry-policy.allowed` restricts user-selectable retry policies.
- `query.max-write-physical-size` caps physical writes.
- ANNOUNCE discovery can automatically provision internal TLS.
- OAuth domain filtering uses `http-server.authentication.oauth2.domain-hint`.
- Persistent JDBC external-auth tokens use
  `externalAuthenticationTokenCache=SYSTEM`.

## Plugin migration quick reference

Current plugin code must account for these removals and replacements:

- `ConnectorPageSource.getNextPage()` to `getNextSourcePage()` and `SourcePage`
- `TypeSignatureParameter` family to `TypeParameter`
- `Type.getObject` and `Type.appendTo`
- connector-scoped event listeners and several event-listener statistics
- old connector page/sink/table-function provider methods
- old dynamic-filter parameters to columns plus `DynamicFilterSnapshot`
- boolean null arrays to bit-packed block validity

Java functions can expose static and instance method syntax with `@StaticMethod`
and `@InstanceMethod`, and name arguments with `@Name`. Connector expression
pushdown supports `COALESCE` and lambdas.

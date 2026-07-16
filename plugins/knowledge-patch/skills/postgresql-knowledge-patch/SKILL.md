---
name: postgresql-knowledge-patch
description: PostgreSQL 18.0 compatibility. Use for PostgreSQL work.
license: MIT
version: "18.0"
metadata:
  author: Nevaberry
---

# PostgreSQL Knowledge Patch

Use this skill when writing SQL, planning an upgrade, operating a cluster, building
a client, or maintaining an extension. Start with the checks below, then open the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Clients, Authentication, and Command-Line Tools](references/clients-and-cli.md) | MD5 migration, OAuth, TLS, libpq, wire protocol, psql, pgbench, notification failures |
| [COPY, Backup, and Maintenance](references/copy-backup-and-maintenance.md) | Safe maintenance paths, inheritance-aware vacuum, tolerant COPY, incremental backup, dump/restore, file operations |
| [Extensions, Modules, and Foreign Data Wrappers](references/extensions-and-fdw.md) | Extension discovery and APIs, injection points, bundled modules, postgres_fdw, file_fdw, pgcrypto |
| [SQL/JSON and JSON Processing](references/json.md) | SQL-standard JSON query functions, JSON_TABLE, constructors, path conversions, null handling |
| [Migration and Compatibility](references/migration-and-compatibility.md) | Removed settings, catalog changes, checksums, pg_upgrade, security repairs, build requirements, release availability |
| [Observability, Statistics, and Planning](references/observability-and-planning.md) | Asynchronous I/O, vacuum progress, statistics, EXPLAIN, logging, NUMA |
| [Replication and Recovery](references/replication-and-recovery.md) | Failover slots, standby synchronization, replica conversion, generated-column publication, apply conflicts |
| [SQL, Types, and Schema Design](references/sql-and-schema.md) | UUIDv7, generated columns, RETURNING, MERGE, temporal constraints, privileges, collations, PL/pgSQL |

## Check breaking changes before migration

### Checksums now start enabled

`initdb` enables data checksums by default. If an unchecked cluster is
intentional, say so explicitly:

```sh
initdb --no-data-checksums -D new-cluster
```

Source and destination checksum settings must match for `pg_upgrade`.

### Generated columns now default to virtual

An omitted storage keyword means compute-on-read. Add `STORED` when the value must be materialized during writes:

```sql
CREATE TABLE line_item (
  quantity integer,
  unit_price numeric,
  total numeric GENERATED ALWAYS AS (quantity * unit_price) STORED
);
```

### Parent maintenance includes children

`VACUUM` and `ANALYZE` on an inheritance parent process child relations. Use `ONLY` when parent-only behavior is required:

```sql
VACUUM (ONLY, ANALYZE) measurements;
```

### Maintenance uses a safe search path

Functions invoked by expression indexes or materialized views must qualify non-default objects or set their own path:

```sql
ALTER FUNCTION app.normalize(text)
  SET search_path = pg_catalog, app;
```

### Authentication and cluster definitions need review

- MD5 password authentication is deprecated; migrate password storage and
  `pg_hba.conf` rules.
- Unlogged partitioned tables are rejected.
- Session time-zone abbreviations take precedence over
  `timezone_abbreviations` entries.
- Deferred `AFTER` triggers run as the role active when the event was queued.
- Full-text-search and `pg_trgm` indexes may need reindexing after a
  default-collation-provider change.

Read [Migration and Compatibility](references/migration-and-compatibility.md)
before running upgrade automation; it includes removed settings, catalog
renames, constraint repair, and changed statistics preservation.

## Use new schema primitives

### Create time-ordered UUIDs

`uuidv7()` generates a time-ordered identifier. An optional interval shifts its
embedded timestamp:

```sql
SELECT uuidv7(), uuidv7(interval '-1 hour');
```

Use `uuid_extract_timestamp()` for version 1 or 7 timestamps and
`uuid_extract_version()` for RFC 9562 versions. Either returns `NULL` when the
UUID form does not support the requested metadata.

### Enforce temporal keys

`WITHOUT OVERLAPS` makes the final primary/unique-key range non-overlapping.
`PERIOD` on the final foreign-key column requires referenced ranges to cover
the referencing range:

```sql
CREATE TABLE room_prices (
  room_id bigint,
  valid_at daterange,
  UNIQUE (room_id, valid_at WITHOUT OVERLAPS)
);

CREATE TABLE bookings (
  room_id bigint,
  stay daterange,
  FOREIGN KEY (room_id, PERIOD stay)
    REFERENCES room_prices (room_id, PERIOD valid_at)
);
```

### Return row images directly

Data-changing statements expose `old` and `new` in `RETURNING`:

```sql
UPDATE products
SET price = price * 1.05
RETURNING id, old.price AS before, new.price AS after;
```

`MERGE` also supports updatable views, `WHEN NOT MATCHED BY SOURCE`,
`RETURNING`, and `merge_action()`.

## Ingest imperfect data deliberately

`COPY FROM ... ON_ERROR ignore` skips conversion failures. Add `REJECT_LIMIT` so a bad file cannot discard an unlimited number of rows:

```sql
COPY staging_orders FROM '/imports/orders.csv'
WITH (
  FORMAT csv,
  ON_ERROR ignore,
  REJECT_LIMIT 100,
  LOG_VERBOSITY silent
);
```

Monitor skipped rows through `pg_stat_progress_copy.tuples_skipped`. Be careful
with `\.` in CSV: server-side files treat it as data, while psql recognizes an
otherwise empty `\.` line as the end of `STDIN`.

## Build incremental physical backups

Turn on WAL summaries, take an incremental relative to a prior manifest, then
combine the chain into a synthetic full backup:

```conf
summarize_wal = on
```

```sh
pg_basebackup -D /backup/inc \
  --incremental=/backup/full/backup_manifest
pg_combinebackup /backup/full /backup/inc -o /backup/combined
```

Set `wal_summary_keep_time` for the backup cadence. Validate the result with `pg_verifybackup`; tar backups are accepted.

## Query JSON with standard SQL

Use `JSON_EXISTS` for path existence, `JSON_VALUE` for one scalar, and
`JSON_QUERY` for JSON results and wrappers:

```sql
SELECT JSON_EXISTS(
         payload,
         'strict $.items[*] ? (@.qty > $minimum)'
         PASSING 10 AS minimum
       ),
       JSON_VALUE(payload, '$.customer.id' RETURNING bigint)
FROM orders;
```

Use `JSON_TABLE` for lateral relational projection with typed columns,
`FOR ORDINALITY`, `EXISTS`, and nested paths. Its sibling nested paths form a
union rather than a cross product.

## Keep logical replication available through failover

Create a failover-capable subscription and synchronize its slot to a standby:

```sql
CREATE SUBSCRIPTION orders_sub
  CONNECTION 'host=publisher dbname=app'
  PUBLICATION orders_pub
  WITH (failover = true);
```

Coordinate `sync_replication_slots` with `synchronized_standby_slots` so
decoded changes do not outrun the required physical standby. Bound abandoned
slots with `idle_replication_slot_timeout`.

Generated columns are published when named in a publication column list.
Without a list, control them with `publish_generated_columns`.

## Tune and observe asynchronous I/O

Select the implementation with `io_method` and inspect active handles through
`pg_aios`. Tune combining with `io_combine_limit` and
`io_max_combine_limit`.

`EXPLAIN ANALYZE` includes buffer statistics automatically and exposes richer
memory, disk, WAL, window, bitmap-cache, and index-lookup details. Add `MEMORY`
for planner memory and `SERIALIZE` to measure result conversion:

```sql
EXPLAIN (ANALYZE, MEMORY, SERIALIZE TEXT)
SELECT * FROM orders;
```

Statistics consumers must account for I/O and WAL data moving between views,
new per-backend reset functions, one-based memory-context levels, and renamed
`pg_stat_statements` timing columns.

## Secure client connections

For immediate TLS negotiation, use `sslnegotiation=direct` only when ALPN and
the server version support it:

```text
host=db.example dbname=app sslmode=require sslnegotiation=direct
```

OAuth authentication uses `oauth` in `pg_hba.conf` and server validators from
`oauth_validator_libraries`. Source builds that enable it need libcurl.

Wire protocol 3.2 supports 256-bit cancel keys. Bound acceptable protocol
versions when compatibility matters, and use the current libpq cancellation
API when cancellation must retain encrypted transport.

## Follow task-specific references

Do not infer old defaults for generated-column storage, checksums, I/O
concurrency, subscription streaming, or vacuum inheritance. Open the indexed
reference whenever code, configuration, monitoring queries, or migration
automation depends on one of these behaviors.

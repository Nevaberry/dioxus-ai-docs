---
name: timescaledb-knowledge-patch
description: TimescaleDB
version: 2.28.0
license: MIT
metadata:
  author: Nevaberry
---


# TimescaleDB Knowledge Patch

Use this skill when writing, reviewing, debugging, upgrading, or operating
TimescaleDB. Determine the installed TimescaleDB and PostgreSQL versions before
applying version-sensitive advice. Prefer public APIs and informational views
over private catalog objects.

## Reference index

| Reference | Topics |
|---|---|
| [Columnstore and Compression](references/columnstore-and-compression.md) | Columnstore APIs, compression, sparse indexes, Direct Compress, recompression |
| [Continuous Aggregates](references/continuous-aggregates.md) | Refresh, invalidation, definitions, GapFill, maintenance |
| [Hypertables, Chunks, and DDL](references/hypertables-chunks-and-ddl.md) | Declarative hypertables, chunk operations, constraints, UUIDv7, triggers |
| [Operations, Jobs, and Query Behavior](references/operations-jobs-and-query-behavior.md) | Jobs, configuration, publications, planner behavior, correctness fixes |
| [Upgrades and Compatibility](references/upgrades-and-compatibility.md) | Breaking changes, removals, PostgreSQL support, required migrations |

## Upgrade blockers and removals

### Remove the Hypercore access method before a 2.22+ upgrade

The experimental `hypercore` table access method was deprecated in 2.21 and
removed in 2.22. The upgrade is blocked while any relation still uses it.
Convert every such relation back to `heap` first:

```sql
DO $$
DECLARE
    relid regclass;
BEGIN
    FOR relid IN
        SELECT cl.oid
        FROM pg_class AS cl
        JOIN pg_am AS am ON am.oid = cl.relam
        WHERE am.amname = 'hypercore'
    LOOP
        EXECUTE format('ALTER TABLE %s SET ACCESS METHOD heap', relid);
    END LOOP;
END
$$;
```

Do not confuse the removed table access method with the supported columnstore
feature. See the upgrade and columnstore references for their separate
lifecycle.

### Respect PostgreSQL support boundaries

- TimescaleDB 2.19 is the last minor release supporting PostgreSQL 14.
- TimescaleDB 2.23 supports PostgreSQL 15, 16, 17, and 18.
- TimescaleDB 2.28.x is the final minor series supporting PostgreSQL 15;
  TimescaleDB 2.29 supports PostgreSQL 16, 17, and 18 only.

Upgrade PostgreSQL before crossing either support boundary.

### Handle sparse-index upgrade hazards

Before upgrading to 2.27, drop bloom sparse indexes on compressed `int2`
columns; affected indexes can omit matching rows and block the upgrade. After
moving from 2.26 to 2.27, run the timescaledb-extras
`utils/2.27.x-fix-composite-bloom-columns.sql` migration so 2.27 can use 2.26
composite bloom metadata. This catalog-only migration needs no recompression.

Bloom indexes created before 2.24 use a build-dependent hash format and are
disabled after upgrade. Decompress and recompress affected chunks, except that
official APT AMD64 installations whose hash scheme did not change may enable
`timescaledb.read_legacy_bloom1_v1 = on` for reads.

### Replace removed APIs and behavior

- Adaptive chunking is removed as a backward-incompatible change in 2.28.
- WAL-based continuous-aggregate invalidation is removed in 2.25; return to
  trigger-based invalidation.
- `time_bucket_ng` and `_timescaledb_debug` are removed in 2.25.
- `_timescaledb_functions.create_chunk_table` is removed in 2.20.
- The deprecated partial continuous-aggregate format and experimental policy
  helpers were scheduled for removal after 2.24; migrate with `cagg_migrate`
  and use the Jobs API.
- `_timescaledb_catalog.chunk_constraint` became a temporary compatibility view
  in 2.28 and will itself disappear; move integrations to informational views.

## Columnstore quick reference

### Use columnstore names

Prefer `convert_to_rowstore`, `convert_to_columnstore`,
`add_columnstore_policy`, and `remove_columnstore_policy`. Prefer
`hypertable_columnstore_stats`, `chunk_columnstore_stats`, the corresponding
`*_columnstore_settings` views, and `columnstore_settings`. Use the reloptions
`timescaledb.enable_columnstore`, `timescaledb.segmentby`, and
`timescaledb.orderby`. Their compression-named predecessors are deprecated for
removal in the next major release.

The `tsdb` reloption prefix aliases `timescaledb`, and `columnstore` aliases
`enable_columnstore` where supported:

```sql
ALTER TABLE metrics SET (tsdb.enable_columnstore = true);
ALTER TABLE metrics SET (timescaledb.chunk_time_interval = '1 day');
```

### Choose current compression behavior deliberately

Recompression is nonblocking by default. Set
`timescaledb.enable_exclusive_locking_recompression = on` only to restore
legacy exclusive locking. Boolean compression became enabled by default in
2.20; data created with the early 2.19 format must be prepared with the
timescaledb-extras `utils/2.19.0-downgrade_new_compression_algorithms.sql`
script before downgrading below 2.19.

Composite bloom indexes are created by default where supported. Use
`timescaledb.enable_composite_bloom_indexes` to control them and inspect
`EXPLAIN` for batch-pruning and false-positive statistics.

### Recompress after layout changes

`convert_to_columnstore(..., recompress := true)` can recompress in memory when
`timescaledb.enable_in_memory_recompression` is enabled. Later behavior also
supports unordered chunks and changes to `orderby` or index settings.
`VACUUM FULL` can therefore include recompression work.

## Continuous-aggregate quick reference

### Batch refresh work

Refresh policies process recent data first and can split work into smaller
batches. The policy default `buckets_per_batch` is `10` as of 2.25. Manual
refresh also accepts batching controls:

```sql
CALL refresh_continuous_aggregate(
    'hourly_metrics',
    '2026-01-01'::timestamptz,
    '2026-06-01'::timestamptz,
    buckets_per_batch => 24,
    max_batches_per_execution => 5,
    refresh_newest_first => true
);
```

Non-overlapping ranges can refresh concurrently, and forced refreshes consume
their invalidations. Use `force => true` for an explicit historical backfill.

### Add an aggregate without rebuilding

An aggregate can be added as a stored generated column. Existing materialized
rows start as `NULL`; new rows populate it. Force-refresh the historical range
to backfill:

```sql
ALTER MATERIALIZED VIEW hourly_metrics
ADD COLUMN max_value double precision
GENERATED ALWAYS AS (max(value)) STORED;
```

`VACUUM` and `ANALYZE` on the continuous aggregate redirect to its
materialization hypertable.

### Suppress invalidations only with a refresh plan

`timescaledb.skip_cagg_invalidation` skips DML and DDL invalidation tracking in
the current session or transaction and defaults to off. It can reduce bulk-load
overhead, but changes made while it is enabled require an explicit refresh.

```sql
BEGIN;
SET LOCAL timescaledb.skip_cagg_invalidation = on;
INSERT INTO metrics SELECT * FROM staging_metrics;
COMMIT;
```

## Hypertable and DDL quick reference

### Prefer declarative creation

Create a hypertable and enable columnstore through reloptions. The partition
column may be inferred where supported, and enabling columnstore declaratively
also creates its policy:

```sql
CREATE TABLE metrics (
    time timestamptz NOT NULL,
    device_id bigint,
    value double precision
) WITH (
    tsdb.hypertable,
    tsdb.columnstore
);
```

Use `ALTER TABLE ONLY` when reloption changes should affect future chunks only.
PostgreSQL and TimescaleDB reloptions can coexist in one `ALTER TABLE SET`.

### Treat Direct Compress as an explicit path

Direct Compress can write `COPY`, `INSERT`, and continuous-aggregate refresh
input directly in compressed form. Its primary enablement GUCs default off.
Batch sorting is safer than declaring client-sorted input; only enable a
`*_client_sorted` mode when the source order is guaranteed. Earlier releases
had a data-loss path for client-ordered `INSERT ... SELECT` from a compressed
hypertable, fixed in 2.26.

## Query correctness quick reference

- Require 2.29.2 before relying on compressed SkipScan for affected `DISTINCT`
  queries over mixed compressed and uncompressed data.
- Require the fixed sparse-index behavior before relying on `IS NULL` min/max
  pushdown over compressed data.
- Keep columnar filter pushdown enabled by default; disable it only for targeted
  diagnosis with `timescaledb.enable_columnar_scan_filter_pushdown = off`.
- `time_bucket_gapfill` requires a constant timezone argument as of 2.26,
  although other GapFill arguments can later arrive as executor parameters.
- `compressed_data_column_size` returns `bigint`; update casts and clients that
  assumed a narrower integer.

Consult the topic references before implementing migrations or enabling
experimental paths; they retain all version-specific defaults, limitations,
and operational caveats.

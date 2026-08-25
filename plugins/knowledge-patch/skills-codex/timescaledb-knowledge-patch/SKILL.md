---
name: timescaledb-knowledge-patch
description: TimescaleDB
version: 2.28.0
license: MIT
metadata:
  author: Nevaberry
---


# TimescaleDB Knowledge Patch

Use this skill when designing, migrating, or debugging TimescaleDB schemas,
columnstore storage, continuous aggregates, chunk operations, or background
jobs. Check the installed extension and PostgreSQL versions before applying
version-sensitive SQL. Prefer public informational views and APIs over private
catalog objects.

## Reference index

| Reference | Topics |
| --- | --- |
| [Columnstore and ingest](references/columnstore-and-ingest.md) | Columnstore terminology, compression, sparse indexes, Direct Compress, recompression, and scan correctness |
| [Continuous aggregates](references/continuous-aggregates.md) | Refresh batching, invalidations, functions, rewrites, GapFill, and maintenance |
| [Hypertables and chunks](references/hypertables-and-chunks.md) | Declarative DDL, dimensions, triggers, chunk split/merge/attach, UUIDv7, and publications |
| [Jobs and observability](references/jobs-and-observability.md) | Job names, history retention, memory, cancellation, and progress reporting |
| [Upgrades and compatibility](references/upgrades-and-compatibility.md) | PostgreSQL support, blocked upgrades, removed APIs, image migration, and correctness fixes |

## Start with upgrade blockers

Before changing extension versions:

1. Find relations that still use the experimental `hypercore` table access
   method. Convert them to `heap`; upgrades to 2.22 or later reject them.
2. Match PostgreSQL to the target TimescaleDB release. PostgreSQL 14 ends with
   2.19, and PostgreSQL 15 ends with the 2.28.x series.
3. Remove sparse bloom indexes on compressed `int2` columns before a 2.27
   upgrade. The upgrade is intentionally blocked while affected indexes exist.
4. Repair composite bloom metadata created by 2.26 before expecting 2.27 to
   use it. Run the provided `2.27.x-fix-composite-bloom-columns.sql` utility;
   it is catalog-only and does not require recompression.
5. Rebuild bloom sparse indexes on chunks compressed before 2.24 unless the
   documented AMD64 APT-package exception applies.
6. Remove dependencies on adaptive chunking before 2.28, where that facility
   is gone.
7. Replace WAL-based continuous-aggregate invalidation before 2.25, where the
   experimental path is removed.

See [Upgrades and compatibility](references/upgrades-and-compatibility.md) for
the complete preflight, downgrade, and removed-API guidance.

## Use current columnstore terminology

Write new code with the columnstore API names:

| Deprecated compression name | Columnstore name |
| --- | --- |
| `compress_chunk` | `convert_to_columnstore` |
| `decompress_chunk` | `convert_to_rowstore` |
| `add_compression_policy` | `add_columnstore_policy` |
| `remove_compression_policy` | `remove_columnstore_policy` |
| `timescaledb.compress` | `timescaledb.enable_columnstore` |
| `timescaledb.compress_segmentby` | `timescaledb.segmentby` |
| `timescaledb.compress_orderby` | `timescaledb.orderby` |

The stats and settings views were renamed similarly. Treat the compression
aliases as compatibility shims scheduled for removal in a major release. The
short `tsdb` reloption prefix is accepted in `WITH` and `SET` clauses.

## Create declarative hypertables

The declarative API can enable both hypertabling and columnstore storage at
creation time:

```sql
CREATE TABLE metrics (
    time timestamptz NOT NULL,
    device_id text,
    value double precision
) WITH (
    tsdb.hypertable,
    tsdb.partition_column = 'time',
    tsdb.columnstore
);
```

The partition-column option can be omitted in newer definitions. Enabling
columnstore in declarative DDL also creates the columnstore policy. Use `ALTER
TABLE ONLY` when a reloption change should apply only to future chunks.

## Configure continuous-aggregate refreshes

Refresh work can be split into smaller transactions and ordered newest-first.
For a manual refresh:

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

Policy refreshes default to incremental operation, and non-overlapping ranges
can refresh concurrently. Policy `buckets_per_batch` defaults to `10`. Use the
optional `force` argument when a range must be recomputed; a forced refresh
also consumes its invalidations.

When bulk loading with `timescaledb.skip_cagg_invalidation = on`, explicitly
refresh every affected aggregate afterward. The setting deliberately avoids
recording changes and defaults to off.

## Add aggregates without rebuilding a view

Add an aggregate as a stored generated column, then force-refresh history:

```sql
ALTER MATERIALIZED VIEW hourly_metrics
ADD COLUMN max_value double precision
GENERATED ALWAYS AS (max(value)) STORED;

CALL refresh_continuous_aggregate(
    'hourly_metrics',
    '2025-01-01'::timestamptz,
    '2026-01-01'::timestamptz,
    force => true
);
```

Existing materialized rows are `NULL` until refreshed; newly materialized rows
populate the column immediately.

## Treat Direct Compress as guarded behavior

Direct Compress can write `COPY`, `INSERT`, and continuous-aggregate refresh
input directly to columnstore. Each path has its own enablement GUC. Batch
sorting is the safe default; declare client-sorted input only when its ordering
is guaranteed.

Do not use client-ordered Direct Compress for `INSERT ... SELECT` from a
compressed hypertable on versions before the 2.26 fix, because that combination
has a data-loss path. Tuple-sort limits separately bound `COPY` and `INSERT`
memory use. Automatic `segmentby` selection is deferred until flush in newer
Direct Compress behavior.

## Handle sparse-index transitions

Columnstore chunks create bloom sparse indexes automatically. Composite bloom
indexes are enabled by default and support multi-column pushdown. Keep these
version-specific hazards in upgrade and query plans:

- Old bloom hashing can silently miss matches after changing package builds;
  decompress and recompress affected pre-2.24 chunks.
- Bloom indexes on compressed `int2` columns can omit matching rows and block a
  2.27 upgrade until dropped.
- Earlier min/max sparse-index pushdown can return wrong results for `IS NULL`;
  rely on the 2.29.2 correction before using that predicate path.
- Compressed SkipScan before 2.29.2 can lose uncompressed rows when sort and
  distinct keys differ.

Use `EXPLAIN` to inspect batch pruning, bloom false positives, and pushed-down
filters. See [Columnstore and ingest](references/columnstore-and-ingest.md) for
GUCs and repair procedures.

## Choose recompression and locking deliberately

Recompression is nonblocking by default. Enable the legacy exclusive-locking
GUC only when that behavior is required. `convert_to_columnstore(...,
recompress := true)` can recompress entirely in memory when its GUC is enabled;
newer behavior also accepts unordered chunks and changed order/index settings.
`VACUUM FULL` may therefore include recompression work.

Compression can fall back from `TRUNCATE` to `DELETE` when locks are
unavailable, can limit batch size, and emits poor-ratio warnings by default.
Plan operational headroom for these choices.

## Validate query semantics after upgrades

- A `time_bucket_gapfill` timezone must be constant.
- `DATE` input rejects sub-day `time_bucket` offsets.
- Chunk intervals cannot be negative, and continuous-aggregate bucket widths
  must be positive.
- UUIDv7 can be the partition key and can be passed to `time_bucket`.
- Cross-type comparisons against partition columns are safe in corrected
  versions; verify plans when older servers are still present.
- Compressed column `WHERE` comparisons and vectorized aggregates follow
  PostgreSQL NaN semantics.

## Keep administration on public surfaces

The database owner can configure hypertables and policies. `VACUUM` and
`ANALYZE` accept a continuous aggregate and redirect to its materialization
hypertable. Avoid building integrations on `_timescaledb_catalog` objects:
`chunk_constraint` is already only a temporary compatibility view, and the
background-job catalog has moved. Prefer informational views and supported job
APIs.

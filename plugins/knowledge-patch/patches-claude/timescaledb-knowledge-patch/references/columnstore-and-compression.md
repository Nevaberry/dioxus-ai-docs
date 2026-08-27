# Columnstore and Compression

## Naming and access methods

TimescaleDB 2.18.0 introduced the `hypercore` table access method and allowed
secondary indexes, including indexes on `orderby` columns, over columnstore
data:

```sql
ALTER TABLE metrics SET ACCESS METHOD hypercore;
CREATE INDEX metrics_device_id_idx ON metrics (device_id);
```

That experimental access method was deprecated in 2.21.0 and removed in
2.22.0. It is not the current way to enable columnstore; convert remaining
relations to `heap` before upgrading. The 2.18.0
`hypercore_use_access_method` GUC selected the then-current default, while a
separate GUC controlled segmentwise recompression.

Columnstore terminology also replaced compression terminology in 2.18.0.
Prefer the following names because the old aliases are deprecated for removal
in the next major release:

| Deprecated | Preferred |
|---|---|
| `decompress_chunk` | `convert_to_rowstore` |
| `compress_chunk` | `convert_to_columnstore` |
| `add_compression_policy` | `add_columnstore_policy` |
| `remove_compression_policy` | `remove_columnstore_policy` |
| `hypertable_compression_stats` | `hypertable_columnstore_stats` |
| `chunk_compression_stats` | `chunk_columnstore_stats` |
| `hypertable_compression_settings` | `hypertable_columnstore_settings` |
| `chunk_compression_settings` | `chunk_columnstore_settings` |
| `compression_settings` | `columnstore_settings` |
| `timescaledb.compress` | `timescaledb.enable_columnstore` |
| `timescaledb.compress_segmentby` | `timescaledb.segmentby` |
| `timescaledb.compress_orderby` | `timescaledb.orderby` |

The shorter `tsdb` prefix is accepted as an alias for `timescaledb` in `WITH`
and `SET` clauses since 2.19.0. Existing hypertables accept `columnstore` as an
alias for `enable_columnstore` since 2.20.0.

## Compression algorithms and downgrade safety

The custom boolean compression algorithm arrived as early access in 2.19.0,
disabled by default behind `timescaledb.enable_bool_compression`. Its compressed
type was unreadable by earlier releases and could change incompatibly. Before
downgrading data created with it below 2.19, run timescaledb-extras
`utils/2.19.0-downgrade_new_compression_algorithms.sql`.

Boolean compression became enabled by default in 2.20.0. UUID compression was
experimental and disabled by default behind
`timescaledb.enable_uuid_compression` in 2.22.0; it works best with UUIDv7 but
also supports other UUID versions, and its backward compatibility was not
guaranteed. UUIDv7 compression became enabled by default in 2.23.0.

In 2.22.0, default compression settings began to apply at compression time,
compression settings gained `ALTER TABLE RESET`, and downgrade is blocked when
the `orderby` setting is `NULL`.

## Recompression and locking

Since 2.19.0, chunk recompression does not block concurrent `INSERT`, `UPDATE`,
and `DELETE` by default. `enable_exclusive_locking_recompression` defaults to
`OFF`; turn it on only to restore legacy exclusive locking.

TimescaleDB 2.24.0 added fully in-memory recompression:

```sql
SET timescaledb.enable_in_memory_recompression = on;
SELECT convert_to_columnstore('metrics_chunk'::regclass, recompress := true);
```

In 2.25.0, in-memory recompression also accepts unordered chunks and
recompression is allowed after `orderby` or index settings change. `VACUUM
FULL` now recompresses affected chunks and may do substantial recompression
work.

## Automatic layouts and DDL

Automatic `segmentby` and `orderby` selection improved in 2.20.0; an explicit
`orderby` prevents default `segmentby` selection. In 2.24.0, automatic
`segmentby` selection stopped choosing date and time columns. Direct Compress
changed again in 2.27.0: it defers automatic `segmentby` selection, analyzes
the data, and chooses the default at flush time.

Compressed continuous aggregates received new automatic `segmentby` and
`orderby` defaults in 2.25.0, so an aggregate relying on automatic selection
may acquire a different layout after upgrade.

Columnstore DDL evolved as follows:

- Since 2.18.0, compressed hypertables accept `DROP NOT NULL`.
- Since 2.19.0, compressed chunks accept `SET NOT NULL`.
- Since 2.20.0, columnstore tables permit foreign keys, compressed chunks
  permit `CHECK` constraints and columns carrying them, and `ADD COLUMN` may
  include a unique constraint.
- Since 2.24.0, `ALTER COLUMN TYPE` is allowed on a columnstore-enabled
  hypertable only when it has no compressed chunks.
- Since 2.25.0, compressed columns accept any immutable constant expression as
  a default value.
- Since 2.28.0, unsafe updates to unique columns on compressed chunks are
  rejected.

## Sparse indexes

Columnstore chunks began creating `bloom1` sparse indexes by default in 2.20.0.
Disable their creation with `timescaledb.enable_sparse_index_bloom = off`.
Explicit sparse-index configuration, including multicolumn indexes through
`ALTER TABLE`, arrived in 2.22.0.

Bloom indexes on chunks compressed before 2.24.0 are disabled after upgrade:
their previous hashing could depend on build options and silently miss rows
after a package change. Decompress and recompress affected chunks to rebuild
them. The official APT AMD64 package did not change hashing, so those
installations may instead set this server parameter for `SELECT`:

```ini
timescaledb.read_legacy_bloom1_v1 = on
```

Composite bloom indexes are created by default since 2.26.0, controlled by
`timescaledb.enable_composite_bloom_indexes` (default `true`). Multicolumn
predicates can be pushed into compressed scans for `SELECT` and `UPSERT`, and
`EXPLAIN` shows batch-pruning and false-positive statistics.

Before upgrading to 2.27.0, drop bloom sparse indexes on compressed `int2`
columns: they may omit matching rows and block the upgrade. Composite bloom
filters created by 2.26 use metadata names that 2.27 does not automatically
recognize. Run timescaledb-extras
`utils/2.27.x-fix-composite-bloom-columns.sql` to rename the legacy metadata;
the migration is catalog-only and requires no recompression.

Min/max sparse-index pushdown for `IS NULL` is correct in 2.29.2. Earlier
releases can return wrong results, so do not rely on that pushdown until
upgraded.

## Compression controls and diagnostics

Poor-compression-ratio warnings are enabled by default since 2.20.0 through
`timescaledb.enable_compression_ratio_warnings`. The
`timescaledb.compress_truncate_behaviour` GUC controls end-of-compression
truncation and defaults to `truncate_only`. Compression may use `DELETE` when
the locks needed by `TRUNCATE` are unavailable, and batch-size limiting is
supported.

`timescaledb.enable_columnar_scan_filter_pushdown` controls whether columnar
filters are pushed to the compressed scan and defaults to on since 2.27.0.
Disable it only for focused diagnosis. `compressed_data_column_size` returns
`bigint` since 2.27.0; widen explicit casts and client decoding.

`timescaledb.stats_max_chunks` sets the per-database capacity of the in-memory
compressed-chunk statistics cache since 2.28.0. It defaults to `1024`; set it
to `0` to disable the cache.

## Direct Compress

Direct Compress is an explicit path that compresses input in memory and writes
it directly to disk instead of waiting for a background job.

- In 2.21.0, tech-preview `COPY` support was disabled by default.
  `timescaledb.enable_direct_compress_copy` enables it, batch sorting defaults
  on, and `timescaledb.enable_direct_compress_copy_client_sorted` defaults off.
  Enable client-sorted mode only for correctly sorted input.
- In 2.23.0, experimental `INSERT` support arrived with separate enablement,
  batch-sort, and client-sorted GUCs; client-sorted mode defaults off.
- In 2.24.0, it began supporting hypertables that feed continuous aggregates,
  recording invalidation ranges at transaction commit. The
  `timescaledb.direct_compress_copy_tuple_sort_limit` and
  `timescaledb.direct_compress_insert_tuple_sort_limit` GUCs cap tuples sorted
  at once.
- In 2.25.0, continuous-aggregate refresh gained an experimental path behind
  `timescaledb.enable_direct_compress_on_cagg_refresh`, default off.
- In 2.26.0, a data-loss bug was fixed for client-ordered Direct Compress with
  `INSERT ... SELECT` from a compressed hypertable. Avoid that combination on
  earlier versions.

## Scan and aggregation semantics

Vectorized aggregation and `WHERE` comparisons on compressed data follow
PostgreSQL NaN semantics after the 2.18.0 fixes.

Compressed SkipScan in 2.29.2 preserves uncompressed rows when sort keys differ
from distinct keys. The planner also avoids attaching SkipScan to mismatched
index-scan paths under `MergeAppend`. Upgrade before relying on affected
`DISTINCT` queries across mixed compressed and uncompressed data.

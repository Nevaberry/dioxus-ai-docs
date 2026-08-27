# Columnstore and ingest

Use this reference for columnstore configuration, compression and
recompression, Direct Compress, sparse indexes, and compressed-query behavior.

## Terminology and table options

### Columnstore API names

The columnstore vocabulary introduced in 2.18.0 replaces these deprecated
compression names:

| Deprecated | Replacement |
| --- | --- |
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

The old names remain aliases but are deprecated for removal in the next major
release. Since 2.19.0, `tsdb` is an accepted alias for the `timescaledb`
reloption prefix:

```sql
ALTER TABLE metrics SET (tsdb.enable_columnstore = true);
```

Since 2.20.0, existing hypertables also accept `columnstore` as an alias for
`enable_columnstore`. Since 2.23.0, one `ALTER TABLE SET` can combine ordinary
PostgreSQL options with TimescaleDB options:

```sql
ALTER TABLE metrics SET (
    fillfactor = 90,
    timescaledb.columnstore = true
);
```

Use `ALTER TABLE ONLY` when a reloption change should affect future chunks but
not existing ones:

```sql
ALTER TABLE ONLY metrics SET (timescaledb.orderby = 'time DESC');
```

### Hypercore access-method lifecycle

In 2.18.0, hypertables could be converted to the experimental `hypercore` table
access method, and secondary indexes—including indexes on `orderby` columns—
could be created over its columnstore data:

```sql
ALTER TABLE metrics SET ACCESS METHOD hypercore;
CREATE INDEX metrics_device_id_idx ON metrics (device_id);
```

That access method was deprecated in 2.21.0 and removed in 2.22.0. Convert
every remaining relation to `heap` before upgrading; the upgrade is blocked
while a relation still uses `hypercore`. Earlier Hypercore configuration also
included GUC controls for the `hypercore_use_access_method` default and for
segmentwise recompression.

## Schema changes on columnstore hypertables

- Since 2.18.0, compressed hypertables accept `DROP NOT NULL`.
- Since 2.19.0, compressed chunks accept `SET NOT NULL`.
- Since 2.20.0, columnstore tables permit foreign keys; compressed chunks
  permit `CHECK` constraints and columns carrying them; and `ADD COLUMN` can
  include a unique constraint.
- Since 2.24.0, `ALTER COLUMN TYPE` is allowed while columnstore is enabled if
  the hypertable has no compressed chunks.
- Since 2.25.0, a compressed column can use any immutable constant expression
  as its default:

  ```sql
  ALTER TABLE metrics ADD COLUMN scale integer DEFAULT (2 * 3);
  ```

- Since 2.28.0, an update that would unsafely modify a unique column on a
  compressed chunk is rejected rather than allowed to proceed.

## Compression and recompression behavior

### Layout selection and settings

The boolean compression algorithm was early access and disabled by default in
2.19.0. Data encoded with it could not be read by older releases. Before
downgrading such data below 2.19, run the migration below. Its original opt-in
was `SET timescaledb.enable_bool_compression = on`.

```text
timescaledb-extras/utils/2.19.0-downgrade_new_compression_algorithms.sql
```

Boolean compression became enabled by default in 2.20.0. That release also
improved automatic `segmentby` and `orderby` selection; specifying `orderby`
prevents automatic selection of a default `segmentby`. Since 2.24.0, automatic
`segmentby` selection excludes date and time columns.

Default compression settings are applied when compression actually runs as of
2.22.0. Settings support `ALTER TABLE RESET`; an `orderby` value of `NULL`
blocks downgrade. Compressed continuous aggregates gained new automatic
`segmentby` and `orderby` defaults in 2.25.0, so a layout that relies on
automatic selection can change after upgrade.

Specialized UUID compression was experimental and disabled by default behind
`timescaledb.enable_uuid_compression` in 2.22.0. It works best with UUIDv7 but
also accepts other UUID versions, and its encoded format was not guaranteed to
remain backward compatible. UUIDv7 compression became enabled by default in
2.23.0.

### Locking, truncation, and diagnostics

Chunk recompression is nonblocking by default since 2.19.0. Concurrent
`INSERT`, `UPDATE`, and `DELETE` continue while it runs. The
`enable_exclusive_locking_recompression` GUC defaults to `OFF`; enable it only
to restore legacy exclusive locking.

Since 2.20.0, poor-ratio warnings default on under
`timescaledb.enable_compression_ratio_warnings`. The
`timescaledb.compress_truncate_behaviour` GUC defaults to `truncate_only` and
controls end-of-compression truncation. Compression can use `DELETE` if the
locks for `TRUNCATE` are unavailable, and it can limit batch size.

`convert_to_columnstore` supports in-memory recompression since 2.24.0:

```sql
SET timescaledb.enable_in_memory_recompression = on;
SELECT convert_to_columnstore('metrics_chunk'::regclass, recompress := true);
```

Since 2.25.0, in-memory recompression accepts unordered chunks and can run
after `orderby` or index settings change. `VACUUM FULL` also recompresses
affected chunks, so include that work in maintenance estimates.

### Compressed-query semantics

Vectorized aggregation and `WHERE` comparisons on compressed data follow
PostgreSQL NaN behavior as of 2.18.0. Since 2.27.0,
`compressed_data_column_size` returns `bigint`; update SQL casts and client
decoders that assumed a narrower integer type.

## Sparse indexes and scan pushdown

### Creation and configuration

Columnstore chunks create `bloom1` sparse indexes by default since 2.20.0.
Disable automatic creation with:

```sql
SET timescaledb.enable_sparse_index_bloom = off;
```

Since 2.22.0, `ALTER TABLE` can explicitly configure sparse indexes, including
multi-column indexes, rather than relying only on internal heuristics.

Composite bloom indexes are created by default since 2.26.0. The
`timescaledb.enable_composite_bloom_indexes` GUC defaults to `true`.
Multi-column predicates can be pushed into compressed scans for both `SELECT`
and `UPSERT`; `EXPLAIN` reports batch-pruning and false-positive statistics.

`timescaledb.enable_columnar_scan_filter_pushdown` controls compressed-scan
filter pushdown and defaults on as of 2.27.0.

### Upgrade repairs and correctness boundaries

Bloom sparse indexes on chunks compressed before 2.24.0 are disabled after
upgrade because the old hash could vary with build options and silently miss
matching rows after a package change. Decompress and recompress those chunks.
Chunks compressed after upgrade are unaffected. On the official AMD64 APT
package, the hash did not change; legacy indexes can instead be enabled for
reads in server configuration:

```ini
timescaledb.read_legacy_bloom1_v1 = on
```

Bloom sparse indexes over compressed `int2` columns can omit matching rows.
The 2.27.0 upgrade is blocked while affected indexes exist; drop them manually
before upgrading.

Composite bloom filters created by 2.26.0 use metadata names that 2.27.0 does
not automatically recognize. Run the catalog-only migration below; no
recompression is required:

```text
timescaledb-extras/utils/2.27.x-fix-composite-bloom-columns.sql
```

In 2.29.2, min/max sparse-index pushdown was corrected for `IS NULL`.
Earlier releases can return wrong results, so upgrade before relying on this
predicate over compressed data.

Compressed SkipScan was also corrected in 2.29.2. Earlier behavior can drop
uncompressed rows when sort keys differ from distinct keys, and can attach
SkipScan to mismatched index paths under `MergeAppend`. Upgrade before relying
on affected `DISTINCT` queries over mixed compressed and uncompressed data.

## Direct Compress ingest

### `COPY`

The 2.21.0 tech-preview path can compress `COPY` input in memory and write it
directly to disk. It is off by default. Batch sorting defaults on;
client-sorted mode defaults off and is safe only when input is correctly
ordered:

```sql
SET timescaledb.enable_direct_compress_copy = on;
SET timescaledb.enable_direct_compress_copy_sort_batches = on;
SET timescaledb.enable_direct_compress_copy_client_sorted = off;
```

### `INSERT` and continuous-aggregate sources

Since 2.23.0, Direct Compress also accepts `INSERT`, including inserts directly
into a chunk:

```sql
SET timescaledb.enable_direct_compress_insert = on;
SET timescaledb.enable_direct_compress_insert_sort_batches = on;
SET timescaledb.enable_direct_compress_insert_client_sorted = off;
```

Since 2.24.0, directly compressed batches can feed continuous aggregates;
their invalidation ranges are recorded at transaction commit. The
`timescaledb.direct_compress_copy_tuple_sort_limit` and
`timescaledb.direct_compress_insert_tuple_sort_limit` GUCs separately cap the
number of tuples sorted at once.

Continuous-aggregate refresh gained its own experimental Direct Compress path
in 2.25.0, disabled by default:

```sql
SET timescaledb.enable_direct_compress_on_cagg_refresh = on;
```

The 2.26.0 release fixes a data-loss path involving client-ordered Direct
Compress with `INSERT ... SELECT` from a compressed hypertable. Avoid that
combination on earlier versions. Since 2.27.0, Direct Compress defers automatic
`segmentby` selection, analyzes data, and chooses the default during flush.

## Cache sizing

Since 2.28.0, `timescaledb.stats_max_chunks` controls the per-database capacity
of the in-memory compressed-chunk statistics cache. It defaults to `1024`; use
`0` to disable the cache:

```sql
SET timescaledb.stats_max_chunks = 0;
```

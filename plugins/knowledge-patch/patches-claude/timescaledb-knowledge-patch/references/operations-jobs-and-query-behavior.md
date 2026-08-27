# Operations, Jobs, and Query Behavior

## Background jobs

Background jobs gained custom names in 2.20.0, and continuous-aggregate jobs
show the aggregate name in the jobs informational view. Per-job history in
2.23.0 can independently cap retained successful and failed executions.

The `bgw_job` table moved to `_timescaledb_catalog` in 2.25.0, with a `bgw_job`
alias retained for compatibility. Background jobs also gained configurable
`work_mem`.

Background jobs stopped using advisory locks and gained graceful cancellation
in 2.26.0. Long index builds became observable through index-creation progress
reporting in 2.27.0.

## Container deployments

TimescaleDB stopped building Bitnami images in 2.18.0. Move container
deployments to the official `timescale/timescaledb-ha` image.

## Runtime configuration

Several GUCs materially affect operations:

- `timescaledb.enable_event_triggers` gates chunk-creation event triggers and
  defaults to `OFF` since 2.20.0.
- `timescaledb.enable_compression_ratio_warnings` defaults on since 2.20.0.
- `timescaledb.compress_truncate_behaviour` defaults to `truncate_only`;
  compression can fall back to `DELETE` when `TRUNCATE` locks are unavailable.
- `timescaledb.default_chunk_time_interval` is an expert default for new
  hypertables since 2.26.0; leave it unchanged without a specific reason.
- `timescaledb.stats_max_chunks` controls the per-database compressed-chunk
  statistics cache since 2.28.0. It defaults to `1024`; zero disables it.

## Planner and scan correctness

Vectorized aggregation and `WHERE` comparisons over compressed data follow
PostgreSQL NaN semantics after fixes in 2.18.0.

Composite bloom indexes in 2.26.0 enable multicolumn predicate pushdown for
both `SELECT` and `UPSERT`. `EXPLAIN` reports batch-pruning and false-positive
statistics.

The 2.26.0 release fixed cross-type comparisons against partitioning columns
that could return wrong results or crash. It also fixed a data-loss path when
client-ordered Direct Compress handled `INSERT ... SELECT` from a compressed
hypertable; avoid that combination on earlier releases.

`timescaledb.enable_columnar_scan_filter_pushdown` defaults on since 2.27.0.
It controls whether columnar-scan filters are pushed into compressed scans.

Compressed SkipScan in 2.29.2 no longer loses uncompressed rows when sort keys
differ from distinct keys, and the planner avoids mismatched index-scan paths
under `MergeAppend`. Upgrade before depending on affected `DISTINCT` queries
over mixed storage.

Also in 2.29.2, min/max sparse-index pushdown returns correct results for `IS
NULL`. Earlier releases can return wrong results for these predicates over
compressed data.

## Query validation and result types

The timezone argument to `time_bucket_gapfill` must be constant since 2.26.0;
queries deriving it from a non-constant expression are rejected. Other GapFill
arguments may come from executor parameters sourced by subqueries since
2.28.0.

Validation became stricter in 2.27.0: `time_bucket` rejects sub-day offsets for
`DATE`, negative `chunk_interval` values are rejected, and
continuous-aggregate definitions reject non-positive bucket widths.

`compressed_data_column_size` returns `bigint` since 2.27.0. Adjust SQL casts
and client result decoding that assumed a narrower type.

Hypertables correctly execute `MERGE WHEN NOT MATCHED BY SOURCE` since 2.28.0.
Unsafe updates to unique columns on compressed chunks are rejected rather than
allowed to proceed.

## Maintenance and bulk loading

`VACUUM FULL` recompresses affected chunks since 2.25.0, so plan for additional
recompression work. `VACUUM` and `ANALYZE` accept a continuous aggregate since
2.28.0 and redirect to its materialization hypertable.

For bulk loads, `timescaledb.skip_cagg_invalidation` can skip
continuous-aggregate invalidation tracking within a session or transaction and
defaults off. It reduces tracking overhead at the cost of requiring an
explicit refresh to make affected aggregates current.

Unlogged hypertables are available since 2.23.0 when import speed matters more
than durability. Newly created chunks of a published hypertable join the
publication automatically since 2.25.0.

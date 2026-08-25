# Continuous Aggregates

## Refresh controls and batching

Since 2.18.0, `refresh_continuous_aggregate` accepts optional `force`, and
`add_continuous_aggregate_policy` accepts `include_tiered_data`.

Incremental policy refreshes arrived in 2.19.0. Policies can split work into
smaller batches and materialize newest data before older data, bringing recent
results current sooner while reducing per-run memory and disk pressure. The
`refresh_newest_first` policy option became explicit in 2.20.0. In 2.21.0,
incremental policies became enabled by default and non-overlapping refresh
ranges could run concurrently, including through concurrent policies.

The default `buckets_per_batch` became `10` in 2.25.0, producing smaller
transactions unless explicitly overridden. A forced refresh consumes its
associated invalidations since 2.26.0 instead of leaving them pending.

Manual `refresh_continuous_aggregate()` gained incremental batching in 2.28.0:

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

Invalidation-log processing in 2.28 uses a lighter lock, so that phase no
longer blocks unrelated operations on the same aggregate.

## Definitions and supported SQL

Continuous aggregates accept non-immutable functions since 2.20.0. Window
functions were experimental and disabled by default behind
`timescaledb.enable_cagg_window_functions`.

Set-returning functions such as `unnest` became valid in 2.23.0:

```sql
CREATE MATERIALIZED VIEW hourly_tags
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', m.time) AS bucket,
       u.tag,
       count(*) AS samples
FROM metrics AS m
CROSS JOIN LATERAL unnest(m.tags) AS u(tag)
GROUP BY bucket, u.tag
WITH NO DATA;
```

Since 2.24.0, `time_bucket` accepts UUIDv7 values and returns timezone-aware
timestamps, allowing continuous aggregates on UUIDv7-partitioned hypertables.
UUIDv7 ranges in the chunks informational view are displayed as timestamps.

Exact-match query rewrites can use an existing continuous aggregate since
2.27.0. Rewrites and diagnostics are both disabled by default:

```sql
SET timescaledb.enable_cagg_rewrites = on;
SET timescaledb.cagg_rewrites_debug_info = on;
```

Time validation is stricter in 2.27.0: continuous-aggregate definitions reject
non-positive bucket widths, and `time_bucket` rejects a sub-day offset for
`DATE` input.

## Invalidation processing

In 2.21.0, hypertable invalidations could be processed through an explicit
function or scheduled policy, with an option to leave them unprocessed.

TimescaleDB 2.22.0 added the tech-preview `timescaledb.invalidate_using`
option, choosing trigger-based collection or WAL collection through logical
decoding. If omitted on a continuous aggregate, it inherited the source
hypertable's method. Processing could cover aggregates involving multiple
hypertables. WAL processing used these defaults:

- `cagg_processing_wal_batch_size = 10000`
- `cagg_processing_low_work_mem = '38.4MB'`
- `cagg_processing_high_work_mem = '51.2MB'`

An explicit `timescaledb.enable_cagg_wal_based_invalidation` GUC arrived in
2.23.0. The experimental WAL path was removed in 2.25.0; use trigger-based
continuous-aggregate invalidation instead.

The 2.28.0 `timescaledb.skip_cagg_invalidation` setting skips invalidation
tracking for DML and DDL in the current session or transaction and defaults to
off. It can reduce bulk-load overhead, but explicitly refresh all affected
aggregates afterward:

```sql
BEGIN;
SET LOCAL timescaledb.skip_cagg_invalidation = on;
INSERT INTO metrics SELECT * FROM staging_metrics;
COMMIT;
```

## Compression and storage

Direct Compress supports hypertables feeding continuous aggregates since
2.24.0; invalidation ranges for directly compressed batches are recorded at
transaction commit. Continuous-aggregate refresh gained an experimental Direct
Compress path in 2.25.0, default off behind
`timescaledb.enable_direct_compress_on_cagg_refresh`.

Compressed continuous aggregates received new automatic `segmentby` and
`orderby` defaults in 2.25.0. Layouts may change when automatic selection is
used. Refresh policies for compressed continuous aggregates can perform
compression as part of refresh since 2.27.0.

Continuous aggregates accept ordinary PostgreSQL storage parameters since
2.25.0:

```sql
ALTER MATERIALIZED VIEW hourly_metrics SET (fillfactor = 90);
```

`ALTER TABLE ... RESET` is supported on their materialization hypertables since
2.27.0, restoring reloptions to defaults.

## Adding aggregates and maintenance

Since 2.28.0, add an aggregate to an existing continuous aggregate as a stored
generated column without rebuilding the view:

```sql
ALTER MATERIALIZED VIEW hourly_metrics
ADD COLUMN max_value double precision
GENERATED ALWAYS AS (max(value)) STORED;
```

Existing materialized rows initially contain `NULL`; new rows populate the
column. Backfill a historical range with a forced refresh:

```sql
CALL refresh_continuous_aggregate(
    'hourly_metrics',
    '2025-01-01'::timestamptz,
    '2026-01-01'::timestamptz,
    force => true
);
```

`VACUUM` and `ANALYZE` accept a continuous aggregate since 2.28.0 and redirect
to its materialization hypertable.

## GapFill

Since 2.26.0, `time_bucket_gapfill` requires its timezone argument to be
constant; a value derived from a non-constant expression is rejected. Since
2.28.0, other GapFill arguments may come from subquery results represented as
executor parameters, enabling parameterized query shapes that were previously
rejected.

## Deprecated formats and policy helpers

TimescaleDB 2.24.0 announced that its next release would remove the deprecated
partial continuous-aggregate format. Migrate any remaining aggregate with:

```sql
SELECT cagg_migrate('<CONTINUOUS_AGGREGATE_NAME>');
```

The same announcement covered the experimental
`timescaledb_experimental.policies` view and its `add_policies`,
`alter_policies`, `show_policies`, `remove_policies`, and
`remove_all_policies` functions. Replace those helpers with the Jobs API.

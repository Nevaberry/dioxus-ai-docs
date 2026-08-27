# Continuous aggregates

Use this reference for refresh execution, invalidation handling, supported SQL
shapes, compressed materializations, and maintenance commands.

## Refresh execution and batching

### Policy refreshes

Since 2.18.0, `refresh_continuous_aggregate()` accepts an optional `force`
argument, while `add_continuous_aggregate_policy` accepts
`include_tiered_data`.

Incremental refresh policies can split work into smaller batches since 2.19.0.
They materialize newest data before older data so recent queries become current
sooner and each run uses less memory and disk. The refresh-policy API gained
`refresh_newest_first` in 2.20.0.

Since 2.21.0, refreshes over non-overlapping ranges can run concurrently,
concurrent refresh policies can be created, and incremental policies default
to enabled. Since 2.25.0, policy `buckets_per_batch` defaults to `10`, yielding
smaller transactions unless explicitly overridden.

Refresh policies for compressed continuous aggregates can perform compression
during refresh as of 2.27.0. Automatic `segmentby` and `orderby` defaults for
compressed aggregates changed in 2.25.0; pin them explicitly when layout
stability matters.

### Manual batched refreshes

Since 2.28.0, manual refresh can use `buckets_per_batch`,
`max_batches_per_execution`, and `refresh_newest_first`:

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

Invalidation processing now takes a lighter lock and no longer blocks unrelated
operations on the same aggregate during that phase. A forced refresh consumes
its associated invalidations as of 2.26.0 rather than leaving them pending.

### Direct compression during refresh

The experimental Direct Compress refresh path arrived in 2.25.0 and defaults
off:

```sql
SET timescaledb.enable_direct_compress_on_cagg_refresh = on;
```

Directly compressed source hypertables have been supported since 2.24.0;
invalidation ranges for their batches are recorded at transaction commit.

## Invalidation methods and controls

Explicit functions and scheduled policies can process hypertable invalidations
since 2.21.0, including an option that leaves invalidations unprocessed.
Information APIs for the hypertable invalidation log and materialization
invalidations were added in 2.20.0.

The 2.22.0 tech-preview `timescaledb.invalidate_using` option selected trigger
collection or WAL collection through logical decoding. Without a view-specific
setting, the continuous aggregate inherited its hypertable's method. The path
also supported aggregates over multiple hypertables. Its processing GUCs
defaulted as follows:

- `cagg_processing_wal_batch_size = 10000`
- `cagg_processing_low_work_mem = 38.4MB`
- `cagg_processing_high_work_mem = 51.2MB`

The WAL path gained `timescaledb.enable_cagg_wal_based_invalidation` in
2.23.0, then was removed in 2.25.0. Return deployments to trigger-based
invalidation before that upgrade.

For controlled bulk loads, 2.28.0 adds
`timescaledb.skip_cagg_invalidation`. It defaults off and can be scoped to a
session or transaction. Continuous-aggregate invalidations for DML and DDL
while it is on are not tracked, so run an explicit refresh afterward:

```sql
BEGIN;
SET LOCAL timescaledb.skip_cagg_invalidation = on;
INSERT INTO metrics SELECT * FROM staging_metrics;
COMMIT;
```

## Supported query definitions

### Functions and expansion

Continuous aggregates accept non-immutable functions since 2.20.0. Window
functions are experimental and default off behind:

```sql
SET timescaledb.enable_cagg_window_functions = on;
```

Set-returning functions such as `unnest` are supported since 2.23.0:

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

### UUIDv7 and GapFill

Since 2.24.0, `time_bucket` accepts UUIDv7 values and returns timezone-aware
timestamps. This supports continuous aggregates over UUIDv7-partitioned
hypertables, and chunk informational views display UUIDv7 ranges as timestamps.

Since 2.26.0, the timezone passed to `time_bucket_gapfill` must be constant;
queries that derive it from a nonconstant expression are rejected. Since
2.28.0, GapFill arguments may come from subquery results represented as
executor parameters.

Validation tightened in 2.27.0: `DATE` input rejects sub-day `time_bucket`
offsets, and continuous-aggregate definitions reject non-positive bucket
widths.

### Exact aggregate rewrites

Since 2.27.0, a query whose aggregation exactly matches a continuous aggregate
can be rewritten to use it. Rewrites and diagnostics both default off:

```sql
SET timescaledb.enable_cagg_rewrites = on;
SET timescaledb.cagg_rewrites_debug_info = on;
```

## Altering and maintaining materializations

Continuous aggregates accept ordinary PostgreSQL storage parameters since
2.25.0:

```sql
ALTER MATERIALIZED VIEW hourly_metrics SET (fillfactor = 90);
```

Since 2.27.0, `ALTER TABLE ... RESET` works on a continuous aggregate's
materialization hypertable.

Since 2.28.0, an aggregate can be added as a stored generated column without
rebuilding the view. Existing rows initially contain `NULL`, new rows populate
the column, and a forced refresh backfills a selected historical range:

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

`VACUUM` and `ANALYZE` also accept a continuous aggregate as of 2.28.0 and
redirect to the materialization hypertable.

## Removed and replacement APIs

Before moving beyond 2.24.0, migrate any deprecated partial-format aggregate
with `cagg_migrate(<CONTINUOUS_AGGREGATE_NAME>)`:

```sql
SELECT cagg_migrate('<CONTINUOUS_AGGREGATE_NAME>');
```

Also replace `timescaledb_experimental.policies` and the experimental
`add_policies`, `alter_policies`, `show_policies`, `remove_policies`, and
`remove_all_policies` functions with the Jobs API; they were slated for removal
in the following release.

The experimental `time_bucket_ng` function was removed in 2.25.0. Migrate
definitions and calls to supported bucketing functions.

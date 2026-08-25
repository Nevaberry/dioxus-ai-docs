# Jobs and observability

Use this reference for background-job identity, retention, memory,
cancellation, and operation progress.

## Job identity and discovery

Background jobs can have custom names since 2.20.0. Continuous-aggregate jobs
also include the aggregate name in the jobs informational view, making them
easier to identify without consulting private catalogs.

The `bgw_job` table moved into `_timescaledb_catalog` in 2.25.0, with a
`bgw_job` alias retained for compatibility. Treat the alias as a compatibility
surface and prefer supported informational views and APIs for durable tooling.

## History retention

Since 2.23.0, job-history configuration can independently cap the number of
successful and failed executions retained for each background job. Size the two
limits according to diagnostic needs rather than applying a single shared cap.

## Per-job resources

Background workers accept per-job `work_mem` configuration since 2.25.0. Use
it to isolate a memory-intensive maintenance job without changing the session
or server-wide default.

## Cancellation and locking

Background jobs stopped using advisory locks in 2.26.0 and support graceful
cancellation. Call the supported cancellation surface and allow cleanup rather
than assuming an advisory-lock owner represents the job lifecycle.

## Progress and diagnostics

Index creation reports progress since 2.27.0, so long-running builds can be
observed rather than treated as opaque operations.

For compressed scans, 2.26.0 `EXPLAIN` output includes batch-pruning and bloom
false-positive statistics when composite bloom indexes participate. In
2.27.0, `timescaledb.cagg_rewrites_debug_info` can expose exact
continuous-aggregate rewrite diagnostics when both diagnostics and rewrites
are explicitly enabled:

```sql
SET timescaledb.enable_cagg_rewrites = on;
SET timescaledb.cagg_rewrites_debug_info = on;
```

The compressed-chunk statistics cache added in 2.28.0 is sized per database by
`timescaledb.stats_max_chunks`. Its default is `1024`; `0` disables it.

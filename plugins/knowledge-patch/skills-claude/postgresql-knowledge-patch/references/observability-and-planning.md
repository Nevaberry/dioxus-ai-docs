# Observability, Statistics, and Planning

## Apply server safety and timeout controls (17.0)

Set `allow_alter_system = off` to disable `ALTER SYSTEM`.
`transaction_timeout` bounds total transaction duration, and `event_triggers`
can temporarily disable event triggers for debugging. `huge_pages_status`
reports whether huge pages are actually active, which is useful when
`huge_pages = try`.

```conf
allow_alter_system = off
transaction_timeout = '10min'
event_triggers = off
```

## Reset broader statistics scopes (17.0)

Call `pg_stat_reset_shared()` with no argument or `NULL` to reset all shared
statistics. Pass `'slru'`, or call `pg_stat_reset_slru()` with no argument, to
reset every SLRU statistic.

## Inspect additional EXPLAIN dimensions (17.0)

`EXPLAIN MEMORY` reports planner memory. `SERIALIZE` measures conversion of
result rows to wire formats. `BUFFERS` includes local-block read/write timing,
and JIT output contains `deform_counter` details.

```sql
EXPLAIN (ANALYZE, BUFFERS, MEMORY, SERIALIZE TEXT)
SELECT * FROM orders;
```

## Consume pg_stat_statements lifecycle data (17.0)

`pg_stat_statements` adds `local_blk_read_time`, `local_blk_write_time`,
`stats_since`, and `minmax_stats_since`. Pass the fourth `minmax_only` argument
to `pg_stat_statements_reset()` to clear only min/max values. Normalization
replaces `CALL` arguments, savepoint names, two-phase commit GIDs, and tracked
`DEALLOCATE` names with placeholders.

## Configure asynchronous I/O (18.0)

Choose the subsystem with `io_method`; tune request combining with
`io_combine_limit` and `io_max_combine_limit`. `pg_aios` shows active file
handles. `effective_io_concurrency` and `maintenance_io_concurrency` default
to 16 and may be positive even without `fadvise()` support.

## Log connection and maintenance detail (18.0)

`log_connections` accepts granular connection-stage settings as well as
Boolean values. `%L` in `log_line_prefix` prints the client IP address, and
`log_lock_failures` reports failures such as `SELECT ... NOWAIT`.

With `track_cost_delay_timing`, vacuum and analyze delay time appears in
progress views, verbose output, and logs. Table statistics include total-time
columns for manual and automatic vacuum and analyze operations.

## Update I/O, WAL, and checkpoint statistics consumers (18.0)

`pg_stat_get_backend_io()` and `pg_stat_get_backend_wal()` expose per-backend
activity; clear it with `pg_stat_reset_backend_stats()`. `pg_stat_io` adds byte
counts and WAL activity and removes `op_bytes`. WAL timing moves into
`pg_stat_io` from `pg_stat_wal`, whose write and sync columns are removed.
Checkpoint, SLRU, and parallel-worker views add counters.

## Restore or clear optimizer statistics (18.0)

Use `pg_restore_relation_stats()` and `pg_restore_attribute_stats()` to load
per-relation or per-column optimizer statistics. Clear those statistics with
`pg_clear_relation_stats()` and `pg_clear_attribute_stats()`.

## Read expanded EXPLAIN ANALYZE output (18.0)

`EXPLAIN ANALYZE` includes buffer statistics automatically and reports
fractional row counts and per-node index lookup counts. Output also covers full
WAL buffers; memory and disk use for materialization, window, and CTE nodes;
window arguments; parallel bitmap-cache activity; and disabled nodes.

## Inspect operating-system resource requirements (18.0)

`num_os_semaphores` reports the required operating-system semaphore count.
`max_files_per_process` counts only files opened by a backend. NUMA-aware
builds use `--with-libnuma`; inspect their behavior with
`pg_numa_available()`, `pg_shmem_allocations_numa`, and
`pg_buffercache_numa`.

## Track more statement forms (18.0)

`pg_stat_statements` assigns query IDs to `CREATE TABLE AS` and `DECLARE`, and
parameterizes `SET` values to avoid entry bloat. Its view adds requested and
launched parallel-worker counts plus `wal_buffers_full`.

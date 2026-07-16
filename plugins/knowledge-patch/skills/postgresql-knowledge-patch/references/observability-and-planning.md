# Observability, Statistics, and Planning

Batch attribution: `17.0`, `18.0`.

## Contents

- [Server controls](#restrict-server-changes-and-bound-transactions)
- [Asynchronous I/O](#configure-asynchronous-io)
- [SLRU caches](#size-slru-caches)
- [Vacuum monitoring](#monitor-vacuum-and-maintenance)
- [I/O, WAL, checkpoints, and waits](#inspect-io-wal-checkpoints-and-waits)
- [Statistics reset and restore](#reset-and-restore-statistics)
- [EXPLAIN](#interpret-expanded-explain-output)
- [pg_stat_statements](#track-query-lifecycle-with-pg_stat_statements)
- [Logging](#log-connection-and-locking-detail)
- [Memory, files, and NUMA](#inspect-memory-semaphores-files-and-numa-placement)

## Restrict server changes and bound transactions

`allow_alter_system` can disable `ALTER SYSTEM`. `transaction_timeout` limits
the total duration of a transaction. `event_triggers` can temporarily disable
event triggers while debugging.

```conf
allow_alter_system = off
transaction_timeout = '10min'
event_triggers = off
```

`huge_pages_status` reports whether huge pages are actually active, which is
particularly useful with `huge_pages = try`.

## Configure asynchronous I/O

`io_method` selects the asynchronous I/O implementation.
`io_combine_limit` and `io_max_combine_limit` tune request combining.
`pg_aios` shows active asynchronous file handles.

`effective_io_concurrency` and `maintenance_io_concurrency` default to 16 and
may be positive even on systems without `fadvise()` support.

## Size SLRU caches

Configure SLRU cache sizes with `commit_timestamp_buffers`,
`multixact_member_buffers`, `multixact_offset_buffers`, `notify_buffers`,
`serializable_buffers`, `subtransaction_buffers`, and `transaction_buffers`.
When not set explicitly, the commit-timestamp, transaction, and subtransaction
caches scale with `shared_buffers`.

## Monitor vacuum and maintenance

`pg_stat_progress_vacuum` renamed `max_dead_tuples` to
`max_dead_tuple_bytes` and `num_dead_tuples` to `num_dead_item_ids`. It also
adds `dead_tuple_bytes`, `indexes_total`, and `indexes_processed`.

With `track_cost_delay_timing` enabled, vacuum and analyze delay time appears
in progress views, verbose output, and logs. Table statistics contain total-time
columns for manual and automatic vacuum and analyze.

## Inspect I/O, WAL, checkpoints, and waits

Checkpoint statistics live in `pg_stat_checkpointer` rather than
`pg_stat_bgwriter`. `pg_wait_events` provides human-readable wait-event
descriptions.

`pg_stat_get_backend_io()` and `pg_stat_get_backend_wal()` report per-backend
activity. Reset those figures with `pg_stat_reset_backend_stats()`.

`pg_stat_io` includes byte counts and WAL activity and no longer exposes
`op_bytes`. WAL timing moved into `pg_stat_io` from `pg_stat_wal`; the latter's
write and sync columns were removed. Checkpoint, SLRU, and parallel-worker
views expose additional counters.

## Reset and restore statistics

`pg_stat_reset_shared()` with no argument or `NULL` resets all shared
statistics. Pass `'slru'` to reset all SLRU statistics, or call
`pg_stat_reset_slru()` with no argument.

Use `pg_restore_relation_stats()` and `pg_restore_attribute_stats()` to install
optimizer statistics for a relation or column. Use
`pg_clear_relation_stats()` and `pg_clear_attribute_stats()` to remove them.

## Interpret expanded EXPLAIN output

`EXPLAIN` option `MEMORY` reports planner memory. `SERIALIZE` measures the work
of converting result rows to wire formats. `BUFFERS` includes local-block
read/write timings, and JIT output includes `deform_counter` details.

```sql
EXPLAIN (ANALYZE, BUFFERS, MEMORY, SERIALIZE TEXT)
SELECT * FROM orders;
```

`EXPLAIN ANALYZE` includes buffer statistics automatically. Row counts may be
fractional, and plan nodes report index lookup counts. Output also covers full
WAL buffers; memory and disk use for materialization, window functions, and
CTEs; window arguments; parallel bitmap cache activity; and disabled nodes.

## Track query lifecycle with pg_stat_statements

`pg_stat_statements` renamed `blk_read_time` and `blk_write_time` to
`shared_blk_read_time` and `shared_blk_write_time`. It adds
`local_blk_read_time`, `local_blk_write_time`, `stats_since`, and
`minmax_stats_since`.

A fourth `minmax_only` argument to `pg_stat_statements_reset()` resets only
minimum and maximum values. `CALL` arguments, savepoint names, two-phase commit
GIDs, and tracked `DEALLOCATE` names are normalized to placeholders.

`CREATE TABLE AS` and `DECLARE` receive query IDs and can be tracked. `SET`
values are parameterized to avoid entry proliferation. The view includes
parallel-worker request and launch counts plus `wal_buffers_full`.

## Log connection and locking detail

`log_connections` accepts fine-grained connection-stage reporting while still
accepting Boolean values. `log_line_prefix` supports `%L` for the client IP
address. `log_lock_failures` reports failures such as `SELECT ... NOWAIT`.

## Inspect memory, semaphores, files, and NUMA placement

`num_os_semaphores` reports the operating-system semaphore requirement.
`max_files_per_process` counts only files opened by a backend.

NUMA-aware builds use `--with-libnuma`. Inspect availability and placement with
`pg_numa_available()`, `pg_shmem_allocations_numa`, and
`pg_buffercache_numa`.

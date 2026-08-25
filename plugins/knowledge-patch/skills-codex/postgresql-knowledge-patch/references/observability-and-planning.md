# Observability, Statistics, and Planning

Use this reference for server controls, I/O tuning, logging, progress views,
statistics APIs, and plan inspection. It incorporates the operational changes
from `17.0` and `18.0`.

## Apply server safety and timeout controls

PostgreSQL 17 adds:

- `allow_alter_system`, which can disable `ALTER SYSTEM`.
- `transaction_timeout`, which limits total transaction duration.
- `event_triggers`, which can temporarily disable event triggers for
  debugging.
- `huge_pages_status`, which reports whether huge pages are in use and is
  especially useful with `huge_pages = try`.

```conf
allow_alter_system = off
transaction_timeout = '10min'
event_triggers = off
```

PostgreSQL 18 `num_os_semaphores` reports the operating-system semaphore
requirement. `max_files_per_process` now counts only files opened by a backend.

## Configure SLRU caches and built-in collations

PostgreSQL 17 provides platform-independent built-in `C` and `C.UTF-8`
collations. It also makes SLRU caches configurable with
`commit_timestamp_buffers`, `multixact_member_buffers`,
`multixact_offset_buffers`, `notify_buffers`, `serializable_buffers`,
`subtransaction_buffers`, and `transaction_buffers`. Commit-timestamp,
transaction, and subtransaction caches otherwise scale with `shared_buffers`.

## Tune asynchronous I/O

PostgreSQL 18 selects its asynchronous I/O subsystem with `io_method`.
`io_combine_limit` and `io_max_combine_limit` tune request combining, and
`pg_aios` reports active file handles.

`effective_io_concurrency` and `maintenance_io_concurrency` default to 16 and
may be positive even on systems without `fadvise()` support. Do not preserve an
old zero-default assumption in configuration generators.

## Monitor vacuum and analyze

PostgreSQL 17 `pg_stat_progress_vacuum` adds `indexes_total` and
`indexes_processed`. Its compatibility renames are documented in the migration
reference. Checkpoint statistics move from `pg_stat_bgwriter` to
`pg_stat_checkpointer`, and `pg_wait_events` provides descriptions for wait
events.

With PostgreSQL 18 `track_cost_delay_timing` enabled, vacuum/analyze delay time
appears in progress views, verbose output, and logs. Table statistics add total
time columns for manual and automatic vacuum/analyze.

## Reset statistics with the right scope

Since PostgreSQL 17, `pg_stat_reset_shared()` with no argument or `NULL` resets
all shared statistics. Passing `'slru'`, or invoking `pg_stat_reset_slru()` with
no argument, resets every SLRU statistic.

PostgreSQL 18 exposes per-backend work through
`pg_stat_get_backend_io()` and `pg_stat_get_backend_wal()`;
`pg_stat_reset_backend_stats()` resets those values.

## Follow I/O, WAL, and checkpoint view changes

PostgreSQL 18 `pg_stat_io` gains byte counts and WAL activity and removes
`op_bytes`. WAL timing moves into `pg_stat_io` from `pg_stat_wal`, whose
write/sync columns are removed. Checkpoint, SLRU, and parallel-worker views add
further counters. Consumers should select named columns rather than depending
on a historical view shape.

## Log connection and lock behavior

PostgreSQL 18 `log_connections` accepts fine-grained connection stages while
retaining Boolean settings. `log_line_prefix` gains `%L` for the client IP
address, and `log_lock_failures` records failures such as
`SELECT ... NOWAIT`.

## Restore or clear optimizer statistics

PostgreSQL 18 provides `pg_restore_relation_stats()`,
`pg_restore_attribute_stats()`, `pg_clear_relation_stats()`, and
`pg_clear_attribute_stats()` for per-relation and per-column optimizer
statistics. These are distinct from dump/restore utility switches and from
ordinary statistics reset functions.

## Read current EXPLAIN output

PostgreSQL 17 `EXPLAIN` adds `MEMORY` for planner memory and `SERIALIZE` for the
cost of converting rows to wire formats. `BUFFERS` includes local-block
read/write timings, and JIT output includes `deform_counter` details:

```sql
EXPLAIN (ANALYZE, BUFFERS, MEMORY, SERIALIZE TEXT)
SELECT * FROM orders;
```

PostgreSQL 18 `EXPLAIN ANALYZE` includes buffer statistics automatically and
uses fractional row counts. It reports per-node index lookups, complete WAL
buffer information, memory and disk usage for material/window/CTE nodes,
window arguments, parallel bitmap cache activity, and disabled nodes.

## Update pg_stat_statements integrations

PostgreSQL 17 adds `local_blk_read_time`, `local_blk_write_time`, `stats_since`,
and `minmax_stats_since`. A fourth `minmax_only` argument to
`pg_stat_statements_reset()` resets only minimum/maximum values. Normalization
uses placeholders for `CALL` arguments, savepoint names, two-phase commit GIDs,
and tracked `DEALLOCATE` names.

PostgreSQL 18 assigns query IDs to `CREATE TABLE AS` and `DECLARE`, allowing
them to be tracked. `SET` values are parameterized to prevent entry bloat. The
view adds requested/launched parallel-worker counts and `wal_buffers_full`.

## Inspect NUMA placement

For a PostgreSQL 18 build configured with `--with-libnuma`, use
`pg_numa_available()`, `pg_shmem_allocations_numa`, and
`pg_buffercache_numa` to inspect whether NUMA support exists and how shared
memory and buffers are placed.

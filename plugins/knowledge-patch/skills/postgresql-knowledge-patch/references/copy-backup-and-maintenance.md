# COPY, Backup, and Maintenance

Batch attribution: `17.0`, `18.0`.

## Contents

- [Safe maintenance search paths](#make-maintenance-functions-safe-under-restricted-search-paths)
- [Vacuum inheritance and controls](#vacuum-parent-and-child-relations-intentionally)
- [Tolerant COPY](#skip-bad-copy-rows-with-an-explicit-limit)
- [Incremental physical backups](#build-and-combine-incremental-physical-backups)
- [Dump and restore controls](#filter-dumps-and-control-restore-transactions)
- [Initialization and maintenance utilities](#use-initialization-and-maintenance-utility-controls)
- [File behavior](#choose-file-extension-and-file-copy-behavior)

## Make maintenance functions safe under restricted search paths

`ANALYZE`, `CLUSTER`, `CREATE INDEX`, `CREATE MATERIALIZED VIEW`,
`REFRESH MATERIALIZED VIEW`, `REINDEX`, and `VACUUM` invoke functions with a
safe `search_path`. Functions used by expression indexes or materialized views
must schema-qualify non-default objects or declare their own path.

```sql
ALTER FUNCTION app.normalize(text)
  SET search_path = pg_catalog, app;
```

## Vacuum parent and child relations intentionally

`VACUUM` and `ANALYZE` on an inheritance parent process its children. Add
`ONLY` to retain parent-only behavior, especially for a partitioned parent.

```sql
VACUUM (ONLY, ANALYZE) measurements;
```

Large `maintenance_work_mem` and `autovacuum_work_mem` values are no longer
silently capped at 1 GB for `VACUUM`. `vacuum_buffer_usage_limit` defaults to
2 MB.

`vacuum_max_eager_freeze_failure_rate` controls eager freezing of all-visible
pages, and the server-level `vacuum_truncate` controls relation-file
truncation. `autovacuum_worker_slots` is a restart-time ceiling within which
`autovacuum_max_workers` can change at runtime.
`autovacuum_vacuum_max_threshold` caps the fixed dead-tuple trigger.

Progress details include `indexes_total` and `indexes_processed` in
`pg_stat_progress_vacuum`. See
[Observability, Statistics, and Planning](observability-and-planning.md) for
the remaining progress and timing changes.

## Skip bad COPY rows with an explicit limit

`COPY FROM` uses `ON_ERROR stop` by default. Choose `ON_ERROR ignore` to discard
conversion failures and inspect `pg_stat_progress_copy.tuples_skipped`.
`LOG_VERBOSITY` controls rejected-row reporting. In CSV mode,
`FORCE_NULL *` or `FORCE_NOT_NULL *` applies its conversion rule to every
column.

`REJECT_LIMIT` bounds the number of discarded rows. `LOG_VERBOSITY silent`
suppresses rejected-row messages.

```sql
COPY staging_orders FROM '/imports/orders.csv'
WITH (
  FORMAT csv,
  HEADER,
  ON_ERROR ignore,
  REJECT_LIMIT 100,
  LOG_VERBOSITY silent,
  FORCE_NULL *
);
```

Server-side `COPY FROM` does not interpret `\.` as end-of-file in CSV input.
psql still recognizes it for CSV read from `STDIN`, but it must be alone on its
line. Older psql clients can therefore mishandle `\copy` against a PostgreSQL
18 server.

`COPY TO` accepts populated materialized views. `COPY FREEZE` rejects foreign
tables rather than silently ignoring `FREEZE`.

## Build and combine incremental physical backups

Enable WAL summaries with `summarize_wal` and retain enough history with
`wal_summary_keep_time`. Inspect availability and contents through
`pg_available_wal_summaries()`, `pg_wal_summary_contents()`, and
`pg_get_wal_summarizer_state()`.

`pg_basebackup --incremental` takes a backup relative to an earlier manifest.
`pg_combinebackup` merges a full backup and its incrementals into a synthetic
full backup.

```conf
summarize_wal = on
```

```sh
pg_basebackup -D /backup/inc \
  --incremental=/backup/full/backup_manifest
pg_combinebackup /backup/full /backup/inc -o /backup/combined
```

`pg_combinebackup --link` can hard-link eligible files, and
`pg_verifybackup` accepts tar-format backups.

## Filter dumps and control restore transactions

`pg_dump`, `pg_dumpall`, and `pg_restore` accept object include/exclude rules
through `--filter`. `pg_dump --exclude-extension` omits extension-owned
objects. `pg_restore --transaction-size` batches restored objects into bounded
transactions.

`pg_dump --statistics` includes optimizer statistics. Dump and restore tools
support `--statistics-only`, `--no-statistics`, `--no-data`, and `--no-schema`.
`--sequence-data` preserves sequence state that other selection rules would
exclude. `--no-policies` omits row-level-security policy processing when the
destination uses different governance.

## Use initialization and maintenance utility controls

`--sync-method` is shared by `initdb`, `pg_basebackup`, `pg_checksums`,
`pg_dump`, `pg_rewind`, and `pg_upgrade`. `initdb --no-sync-data-files` skips
heap and index syncing without disabling every sync operation as `--no-sync`
does.

`reindexdb`, `vacuumdb`, and `clusterdb` can combine object patterns with
`--all` to process matching objects across databases.
`vacuumdb --missing-stats-only` fills only missing statistics; it must be used
with an analyze mode by a superuser.

`pg_resetwal --char-signedness` changes the recorded default signedness.

## Choose file extension and file-copy behavior

On filesystems where `posix_fallocate()` disables BTRFS compression or causes
spurious XFS `ENOSPC` errors, set `file_extend_method = write_zeros` to restore
zero-block file extension.

```conf
file_extend_method = write_zeros
```

`file_copy_method` selects copying or cloning for
`CREATE DATABASE ... STRATEGY=FILE_COPY` and
`ALTER DATABASE ... SET TABLESPACE`.

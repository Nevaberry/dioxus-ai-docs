# COPY, Backup, and Maintenance

Use this reference when moving data, taking physical backups, running
maintenance, or scripting PostgreSQL utilities. The versioned behavior here is
drawn from the `17.0` and `18.0` batches.

## Make maintenance functions safe

Since PostgreSQL 17, `ANALYZE`, `CLUSTER`, `CREATE INDEX`,
`CREATE MATERIALIZED VIEW`, `REFRESH MATERIALIZED VIEW`, `REINDEX`, and
`VACUUM` invoke functions with a safe `search_path`. Functions used by
expression indexes or materialized views must schema-qualify non-default
objects or declare a suitable path:

```sql
ALTER FUNCTION app.normalize(text)
  SET search_path = pg_catalog, app;
```

The per-table `MAINTAIN` privilege and predefined `pg_maintain` role delegate
`VACUUM`, `ANALYZE`, `REINDEX`, `REFRESH MATERIALIZED VIEW`, `CLUSTER`, and
`LOCK TABLE` without granting ownership or superuser rights:

```sql
GRANT MAINTAIN ON TABLE app.orders TO maintenance_bot;
GRANT pg_maintain TO operations_role;
```

## Account for inherited maintenance

PostgreSQL 18 `VACUUM` and `ANALYZE` process inheritance children when run on
a parent. Use `ONLY` to retain parent-only behavior, especially for a
partitioned parent:

```sql
VACUUM (ONLY, ANALYZE) measurements;
```

`vacuum_max_eager_freeze_failure_rate` controls eager freezing of all-visible
pages, and server-level `vacuum_truncate` controls relation-file truncation.
`autovacuum_worker_slots` is a restart-time ceiling within which
`autovacuum_max_workers` can change at runtime;
`autovacuum_vacuum_max_threshold` caps the fixed dead-tuple trigger.

In PostgreSQL 17, `VACUUM` stopped silently capping its memory at 1 GB when
`maintenance_work_mem` or `autovacuum_work_mem` is larger, and
`vacuum_buffer_usage_limit` changed its default to 2 MB.

## Load imperfect input deliberately

### PostgreSQL 17 controls

`COPY FROM` accepts `ON_ERROR ignore` instead of the default `stop`.
`LOG_VERBOSITY` controls rejected-row reporting,
`pg_stat_progress_copy.tuples_skipped` reports the skipped count, and
`FORCE_NULL *` or `FORCE_NOT_NULL *` applies its CSV conversion rule to every
column:

```sql
COPY staging_orders FROM '/imports/orders.csv'
WITH (
  FORMAT csv,
  HEADER,
  ON_ERROR ignore,
  LOG_VERBOSITY verbose,
  FORCE_NULL *
);
```

### PostgreSQL 18 controls

Add `REJECT_LIMIT` to bound discarded rows and use `LOG_VERBOSITY silent` when
rejection messages are unwanted:

```sql
COPY staging_orders FROM '/imports/orders.csv'
WITH (FORMAT csv, ON_ERROR ignore, REJECT_LIMIT 100, LOG_VERBOSITY silent);
```

`COPY TO` accepts populated materialized views. `COPY FREEZE` rejects foreign
tables instead of silently ignoring `FREEZE`.

### Treat CSV end markers according to the data source

PostgreSQL 18 server-side `COPY FROM` treats `\.` as CSV data rather than EOF.
psql still recognizes an otherwise empty `\.` line as the end of CSV supplied
through `STDIN`. Older psql clients can therefore mishandle `\copy` against an
18 server.

## Build incremental physical backups

PostgreSQL 17 incremental backups depend on WAL summaries:

```conf
summarize_wal = on
```

```sh
pg_basebackup -D /backup/inc \
  --incremental=/backup/full/backup_manifest
pg_combinebackup /backup/full /backup/inc -o /backup/combined
```

Set `wal_summary_keep_time` long enough for the backup cadence.
`pg_available_wal_summaries()`, `pg_wal_summary_contents()`, and
`pg_get_wal_summarizer_state()` expose summary availability, contents, and
summarizer state. `pg_combinebackup` combines the full backup and incrementals
into a synthetic full.

PostgreSQL 18 adds `pg_combinebackup --link` to hard-link eligible files, and
`pg_verifybackup` accepts tar backups.

## Use current initialization and maintenance utilities

PostgreSQL 17 utilities share `--sync-method` across `initdb`,
`pg_basebackup`, `pg_checksums`, `pg_dump`, `pg_rewind`, and `pg_upgrade`.
`reindexdb`, `vacuumdb`, and `clusterdb` can combine object patterns with
`--all` to process matches across databases.

PostgreSQL 18 adds:

- `initdb --no-sync-data-files`, which skips heap/index syncing without
  disabling every sync as `--no-sync` does.
- `vacuumdb --missing-stats-only`, which fills only absent statistics, requires
  an analyze mode, and must run as superuser.
- `pg_resetwal --char-signedness`, which changes the recorded default
  signedness.

## Filter and control dump/restore

PostgreSQL 17 `pg_dump`, `pg_dumpall`, and `pg_restore` accept object
include/exclude rules through `--filter`. `pg_dump` adds
`--exclude-extension`, and `pg_restore --transaction-size` groups objects into
bounded transactions.

PostgreSQL 18 `pg_dump --statistics` includes optimizer statistics. Dump and
restore tools add `--statistics-only`, `--no-statistics`, `--no-data`, and
`--no-schema`; `--sequence-data` retains otherwise excluded sequence state.
`--no-policies` omits row-level-security policy processing for migration into
a differently governed system.

Patched PostgreSQL 17 dump scripts use psql's `\restrict` mode so text emitted
by the source server cannot inject later meta-commands during restore.

## Select file operations for the environment

On updated 17.x servers, `file_extend_method = write_zeros` avoids
`posix_fallocate()` where that call disables BTRFS compression or produces
spurious XFS `ENOSPC` failures:

```conf
file_extend_method = write_zeros
```

In PostgreSQL 18, `file_copy_method` chooses copying versus cloning for
`CREATE DATABASE ... STRATEGY=FILE_COPY` and
`ALTER DATABASE ... SET TABLESPACE`.

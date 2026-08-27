# COPY, Backup, and Maintenance

## Make maintenance functions self-contained (17.0)

`ANALYZE`, `CLUSTER`, `CREATE INDEX`, `CREATE MATERIALIZED VIEW`,
`REFRESH MATERIALIZED VIEW`, `REINDEX`, and `VACUUM` invoke functions with a
safe `search_path`. Functions used by expression indexes or materialized views
must schema-qualify non-default objects or set an explicit path.

```sql
ALTER FUNCTION app.normalize(text)
  SET search_path = pg_catalog, app;
```

## Delegate maintenance without ownership (17.0)

The per-table `MAINTAIN` privilege and predefined `pg_maintain` role authorize
`VACUUM`, `ANALYZE`, `REINDEX`, `REFRESH MATERIALIZED VIEW`, `CLUSTER`, and
`LOCK TABLE` without granting ownership or superuser rights.

```sql
GRANT MAINTAIN ON TABLE app.orders TO maintenance_bot;
GRANT pg_maintain TO operations_role;
```

## Size and monitor VACUUM work (17.0)

`VACUUM` is not silently limited to 1 GB when `maintenance_work_mem` or
`autovacuum_work_mem` is larger. `vacuum_buffer_usage_limit` defaults to 2 MB.
`pg_stat_progress_vacuum` adds `indexes_total` and `indexes_processed`.
Checkpoint statistics moved from `pg_stat_bgwriter` to
`pg_stat_checkpointer`, and `pg_wait_events` describes wait events.

## Build incremental physical backups (17.0)

Enable WAL summaries with `summarize_wal` and retain them long enough with
`wal_summary_keep_time`. Create an incremental relative to an earlier backup
manifest, then combine the full backup and incrementals into a synthetic full.

```conf
summarize_wal = on
```

```sh
pg_basebackup -D /backup/inc \
  --incremental=/backup/full/backup_manifest
pg_combinebackup /backup/full /backup/inc -o /backup/combined
```

Inspect summary state and contents with `pg_available_wal_summaries()`,
`pg_wal_summary_contents()`, and `pg_get_wal_summarizer_state()`.

## Skip malformed COPY rows deliberately (17.0)

`COPY FROM` accepts `ON_ERROR ignore` instead of its default `stop` behavior.
`LOG_VERBOSITY` controls reports for rejected rows, and
`pg_stat_progress_copy.tuples_skipped` reports the count. In CSV mode,
`FORCE_NULL *` and `FORCE_NOT_NULL *` apply their conversion rules to every
column.

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

## Filter dump and maintenance jobs (17.0)

`pg_dump`, `pg_dumpall`, and `pg_restore` accept include/exclude object rules
through `--filter`. `pg_dump` also supports `--exclude-extension`, and
`pg_restore --transaction-size` groups objects into bounded transactions.
The `--sync-method` option is shared by `initdb`, `pg_basebackup`,
`pg_checksums`, `pg_dump`, `pg_rewind`, and `pg_upgrade`. `reindexdb`,
`vacuumdb`, and `clusterdb` may combine object patterns with `--all` to process
matching objects across databases.

Patched dump scripts use psql's `\restrict` mode so text emitted by a source
server cannot execute later meta-commands during restore.

## Work around incompatible file allocation (17.0)

Set `file_extend_method = write_zeros` to avoid `posix_fallocate()` on file
systems where it disables BTRFS compression or causes spurious XFS `ENOSPC`
errors.

```conf
file_extend_method = write_zeros
```

## Include inheritance children during maintenance (18.0)

`VACUUM` and `ANALYZE` on a parent process inheritance children. Use `ONLY` to
retain parent-only behavior, especially for a partitioned parent.

```sql
VACUUM (ONLY, ANALYZE) measurements;
```

Tune eager freezing of all-visible pages with
`vacuum_max_eager_freeze_failure_rate`. The server-level `vacuum_truncate`
controls relation-file truncation. `autovacuum_worker_slots` is a restart-time
ceiling within which `autovacuum_max_workers` can change at runtime;
`autovacuum_vacuum_max_threshold` caps the fixed dead-tuple trigger.

## Treat CSV end markers by input path (18.0)

Server-side `COPY FROM` does not treat `\.` as end-of-file in CSV input. psql
still ends CSV read from `STDIN` when `\.` appears alone on a line. Older psql
clients can therefore mishandle `\copy` against an 18 server.

## Bound tolerant imports and validate COPY targets (18.0)

With `ON_ERROR = 'ignore'`, add `REJECT_LIMIT` to bound discarded rows and use
`LOG_VERBOSITY silent` when rejection messages are unwanted. `COPY TO` accepts
populated materialized views. `COPY FREEZE` rejects foreign tables instead of
silently ignoring `FREEZE`.

```sql
COPY staging_orders FROM '/imports/orders.csv'
WITH (
  FORMAT csv,
  ON_ERROR ignore,
  REJECT_LIMIT 100,
  LOG_VERBOSITY silent
);
```

## Use new initialization and maintenance utility options (18.0)

`initdb --no-sync-data-files` skips heap and index syncing without disabling
all sync operations as `--no-sync` does. `vacuumdb --missing-stats-only` fills
only absent statistics and requires both superuser and an analyze mode.
`pg_combinebackup --link` hard-links eligible files; `pg_verifybackup` accepts
tar backups; and `pg_resetwal --char-signedness` changes the recorded default
signedness.

## Select dump contents precisely (18.0)

`pg_dump --statistics` includes optimizer statistics. Dump and restore tools
also support `--statistics-only`, `--no-statistics`, `--no-data`, and
`--no-schema`. `--sequence-data` retains otherwise excluded sequence state,
and `--no-policies` omits row-level-security policy processing when migrating
to a differently governed system.

## Choose database file-copy behavior (18.0)

`file_copy_method` chooses copying or cloning for
`CREATE DATABASE ... STRATEGY=FILE_COPY` and
`ALTER DATABASE ... SET TABLESPACE`.

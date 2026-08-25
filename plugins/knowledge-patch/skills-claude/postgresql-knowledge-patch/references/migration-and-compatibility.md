# Migration and Compatibility

## Remove obsolete configuration and objects (17.0)

PostgreSQL 17 removes `old_snapshot_threshold`, `db_user_namespace`,
`trace_recovery_messages`, the `adminpack` extension,
`information_schema.element_types.domain_default`, and the Windows
`fsync_writethrough` WAL sync method. Interval input accepts `ago` only at the
end and no longer permits repeated empty units.

## Update catalog and statistics consumers (17.0)

Rename `pg_collation.colliculocale` to `colllocale` and
`pg_database.daticulocale` to `datlocale`. A default `attstattarget` or
`stxstattarget` is represented by `NULL`. In `pg_stat_statements`,
`blk_read_time` and `blk_write_time` became `shared_blk_read_time` and
`shared_blk_write_time`. `pg_stat_progress_vacuum.max_dead_tuples` became
`max_dead_tuple_bytes`, `num_dead_tuples` became `num_dead_item_ids`, and
`dead_tuple_bytes` was added.

At an exact WAL-segment boundary, `pg_walfile_name()` and
`pg_walfile_name_offset()` identify the current segment rather than the
previous segment.

## Apply security-sensitive planner and restore fixes (17.0)

Updated minor releases correctly invalidate role-dependent plans with nested
row-level-security references. Planner permission checks for views,
partitioning, and inheritance occur early enough to keep statistics from
leaky estimators. `SET SESSION AUTHORIZATION` uses the session user's
superuser status when issued, not the status at connection time; patched
minors also limit its `SET ROLE NONE` side effect correctly.

Creating statistics requires `CREATE` on the target schema. Attaching a
non-built-in selectivity estimator to an operator requires superuser. Dump
scripts use psql's `\restrict` mode so source-server text cannot execute later
meta-commands during restore.

## Repair partitioned foreign keys from early releases (17.0)

Early PostgreSQL 17 releases could omit enforcement triggers after attaching
or detaching a referencing partition and incompletely enforce self-referential
foreign keys when partitions were created or attached. After updating, drop
and recreate affected constraints, repair rows revealed by validation, and
then add the constraints again.

## Plan checksum-compatible initialization and upgrades (18.0)

`initdb` enables data checksums by default. Use `--no-data-checksums` only when
an unchecked cluster is intentional. `pg_upgrade` requires matching checksum
settings in the source and destination clusters.

```sh
initdb --no-data-checksums -D new-cluster
```

## Audit authentication, partitions, triggers, and indexes (18.0)

MD5 authentication is deprecated, and setting an MD5 password warns unless
`md5_password_warnings` is disabled. Session time-zone abbreviations take
precedence over `timezone_abbreviations`. Unlogged partitioned tables are
rejected. Deferred `AFTER` triggers execute as the role active when the event
was queued, not the role active when the trigger finally runs.

Full-text search and `pg_trgm` read configuration and dictionaries with the
cluster's default collation provider. After upgrading a cluster whose default
provider is not libc, reindex affected indexes when required.

## Update memory-context consumers (18.0)

`pg_backend_memory_contexts.parent` is removed. `level` and logged memory
context levels are one-based. Use the new `path` and `type` columns for
ancestry and context kind.

## Preserve and transform state with pg_upgrade (18.0)

`pg_upgrade` preserves ordinary optimizer statistics by default, but not
extended statistics; disable preservation with `--no-statistics`. `--jobs`
parallelizes database checks. `--swap` exchanges the old and new data
directories, while `--set-char-signedness` handles clusters built with
different default `char` signedness.

## Meet build and catalog requirements (18.0)

NUMA-aware builds use `--with-libnuma`; inspect support with
`pg_numa_available()`, `pg_shmem_allocations_numa`, and
`pg_buffercache_numa`. Builds require Python 3.6.8 or newer, OpenSSL 1.1.1 or
newer, LLVM 14 or newer when LLVM is enabled, and 32-bit atomics.
`pg_attribute.attcacheoff` is removed. `pg_class.relallfrozen` and new
index-access-method capability fields are available to catalog consumers.

## Check current release availability (release-catalog)

PostgreSQL 19 Beta 1 was released on June 4, 2026 for prerelease testing. The
release archive reaches PostgreSQL 18.4, 17.10, 16.14, 15.18, and 14.23 for the
five newest released major lines.

# Migration and Compatibility

Use this reference before upgrading a cluster or adapting tooling to catalog,
configuration, build, and security changes. It covers compatibility facts from
`17.0` and `18.0`, plus current release availability from `release-catalog`.

## Remove obsolete PostgreSQL 17 settings and objects

PostgreSQL 17 removes:

- `old_snapshot_threshold`
- `db_user_namespace`
- `trace_recovery_messages`
- the `adminpack` extension
- `information_schema.element_types.domain_default`
- the Windows `fsync_writethrough` WAL synchronization method

Interval input also accepts `ago` only at the end and rejects repeated empty
units. Fix stored expressions, tests, and import data that use the old forms.

## Update catalog and statistics consumers

PostgreSQL 17 changes include:

- `pg_collation.colliculocale` is renamed to `colllocale`.
- `pg_database.daticulocale` is renamed to `datlocale`.
- Default `attstattarget` and `stxstattarget` values are represented by `NULL`.
- `pg_stat_statements.blk_read_time` and `blk_write_time` become
  `shared_blk_read_time` and `shared_blk_write_time`.
- `pg_stat_progress_vacuum.max_dead_tuples` becomes `max_dead_tuple_bytes`,
  `num_dead_tuples` becomes `num_dead_item_ids`, and `dead_tuple_bytes` is new.
- At an exact WAL-segment boundary, `pg_walfile_name()` and
  `pg_walfile_name_offset()` name the current segment rather than the previous
  one.

PostgreSQL 18 removes `pg_backend_memory_contexts.parent`; its `level` and
logged levels are one-based, while `path` and `type` describe ancestry and
context type. It also removes `pg_attribute.attcacheoff` and adds
`pg_class.relallfrozen` plus new index-access-method capabilities.

## Account for initialization and checksum defaults

PostgreSQL 18 `initdb` enables data checksums by default. Use the explicit
opt-out only when an unchecked cluster is required:

```sh
initdb --no-data-checksums -D new-cluster
```

`pg_upgrade` requires the old and new clusters to have matching checksum
settings.

## Audit authentication, partitions, triggers, and text search

- MD5 password authentication is deprecated. Setting an MD5 password warns
  unless `md5_password_warnings` is disabled.
- Session time-zone abbreviations take precedence over definitions in
  `timezone_abbreviations`.
- PostgreSQL 18 rejects unlogged partitioned tables.
- Deferred `AFTER` triggers execute as the role active when their events were
  queued, not the role active when they finally run.
- Full-text search and `pg_trgm` read configuration and dictionaries using the
  cluster's default collation provider. When upgrading a cluster whose default
  provider is not libc, reindex affected indexes as needed.

## Repair affected PostgreSQL 17 foreign keys

Early PostgreSQL 17 releases could omit enforcement triggers after attaching
or detaching a referencing partition and could incompletely enforce
self-referential foreign keys when partitions were created or attached. After
updating, drop and recreate affected constraints, repair rows exposed by
validation, and add the constraints again.

## Preserve corrected security boundaries

Updated PostgreSQL 17 releases correctly invalidate role-dependent plans for
nested row-level-security references. Planner permission checks for views,
partitioning, and inheritance occur early enough to prevent leaky estimators
from observing protected statistics.

`SET SESSION AUTHORIZATION` uses the session user's superuser status at command
time rather than connection time; patched minors also restrict its
`SET ROLE NONE` side effect. Creating statistics requires `CREATE` on the
target schema, and assigning a non-built-in selectivity estimator to an
operator requires superuser.

## Plan pg_upgrade behavior explicitly

PostgreSQL 17 `pg_upgrade` carries valid logical slots and full subscription
state forward when the old cluster is PostgreSQL 17 or later.

PostgreSQL 18 preserves ordinary optimizer statistics by default, but not
extended statistics. `--no-statistics` opts out, `--jobs` parallelizes database
checks, `--swap` exchanges data directories, and `--set-char-signedness`
handles clusters built with a different default `char` signedness.

## Check build prerequisites and NUMA support

PostgreSQL 18 requires Python 3.6.8 or newer, OpenSSL 1.1.1 or newer, LLVM 14
or newer when LLVM is enabled, and 32-bit atomic operations. NUMA-aware builds
use `--with-libnuma`; inspect availability and allocation using
`pg_numa_available()`, `pg_shmem_allocations_numa`, and
`pg_buffercache_numa`.

## Track release availability separately from feature compatibility

PostgreSQL 19 Beta 1 was released June 4, 2026 for prerelease testing. The
release archive snapshot dated July 15, 2026 reaches PostgreSQL 18.4, 17.10,
16.14, 15.18, and 14.23 for the five newest stable major lines. Do not infer
PostgreSQL 19 feature behavior from the beta's availability alone.

# Migration and Compatibility

Batch attribution: `17.0`, `18.0`. Release status attribution:
`release-catalog`.

## Contents

- [Removed behavior](#remove-obsolete-settings-objects-and-syntax)
- [Catalog compatibility](#update-catalog-and-statistics-consumers)
- [Checksums and pg_upgrade](#initialize-and-upgrade-checksummed-clusters)
- [Authentication and time zones](#recheck-authentication-and-time-zone-assumptions)
- [Partitions, triggers, and text search](#repair-partition-and-trigger-behavior)
- [Security semantics](#preserve-security-semantics-across-updates)
- [Build prerequisites](#check-build-prerequisites)
- [Release availability](#track-release-availability-separately-from-feature-compatibility)

## Remove obsolete settings, objects, and syntax

Remove uses of `old_snapshot_threshold`, `db_user_namespace`,
`trace_recovery_messages`, the `adminpack` extension,
`information_schema.element_types.domain_default`, and the Windows
`fsync_writethrough` WAL synchronization method.

Interval input accepts `ago` only at the end and rejects repeatedly empty
units.

Unlogged partitioned tables are not allowed.

## Update catalog and statistics consumers

`pg_collation.colliculocale` is now `colllocale`, and
`pg_database.daticulocale` is now `datlocale`. A default `attstattarget` or
`stxstattarget` is represented by `NULL`.

At an exact WAL-segment boundary, `pg_walfile_name()` and
`pg_walfile_name_offset()` identify the current segment rather than the
previous segment.

`pg_backend_memory_contexts.parent` is removed. `level` and levels written to
the log are one-based. The `path` and `type` columns describe ancestry and
memory-context type.

`pg_attribute.attcacheoff` is removed. `pg_class.relallfrozen` and new
index-access-method capability fields are available.

See [Observability, Statistics, and Planning](observability-and-planning.md)
for renamed statistics columns and relocated I/O, WAL, and checkpoint data.

## Initialize and upgrade checksummed clusters

`initdb` enables data checksums by default. Use `--no-data-checksums` only when
an unchecked cluster is intentional. `pg_upgrade` requires matching checksum
settings in the source and destination clusters.

```sh
initdb --no-data-checksums -D new-cluster
```

`pg_upgrade` preserves ordinary optimizer statistics by default, but not
extended statistics. `--no-statistics` disables preservation. `--jobs`
parallelizes database checks.

`pg_upgrade --swap` exchanges the old and new data directories.
`--set-char-signedness` handles clusters built with different default `char`
signedness.

## Recheck authentication and time-zone assumptions

Session time-zone abbreviations take precedence over entries in
`timezone_abbreviations`. Review applications that expect a configured
abbreviation to override the session interpretation.

MD5 authentication migration and TLS setting changes are detailed in
[Clients, Authentication, and Command-Line Tools](clients-and-cli.md).

## Repair partition and trigger behavior

Deferred `AFTER` triggers execute as the role that was active when their events
were queued, not the role active when the trigger eventually runs.

Early PostgreSQL 17 releases could omit enforcement triggers after attaching
or detaching a referencing partition, and could incompletely enforce
self-referential foreign keys when partitions were created or attached. After
updating, drop and recreate affected constraints, repair rows found by
validation, and add the constraints again.

Full-text search and `pg_trgm` read configurations and dictionaries using the
cluster's default collation provider. When upgrading a cluster whose default
provider is not libc, reindex affected indexes.

## Preserve security semantics across updates

Plans depending on roles through nested row-level-security references are
invalidated correctly. Planner permission checks for views, partitioning, and
inheritance occur early enough to keep leaky estimators from observing
protected statistics.

`SET SESSION AUTHORIZATION` evaluates the session user's superuser status when
the command is issued rather than when the connection was opened. Current
maintenance updates also constrain the command's `SET ROLE NONE` side effect.

Creating statistics requires `CREATE` on the target schema. Attaching a
non-built-in selectivity estimator to an operator requires superuser.

Dump scripts use psql's `\restrict` mode so text emitted by a source server
cannot execute later psql meta-commands during restore.

## Check build prerequisites

Source builds require Python 3.6.8 or newer, OpenSSL 1.1.1 or newer, LLVM 14 or
newer when LLVM is enabled, and 32-bit atomic operations.

## Track release availability separately from feature compatibility

PostgreSQL 19 Beta 1 became available for pre-release testing on June 4, 2026.
The release archive snapshot from July 15, 2026 reaches maintenance releases
18.4, 17.10, 16.14, 15.18, and 14.23.

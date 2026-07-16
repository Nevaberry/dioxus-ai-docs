# C APIs and Configuration

## Preparing SQL

Pass `SQLITE_PREPARE_DONT_LOG` to `sqlite3_prepare_v3()` when compiling potentially invalid SQL for validation (since 3.48.0). Errors still return to the caller, but malformed input does not emit warnings to the configured error log.

```c
sqlite3_prepare_v3(db, sql, -1, SQLITE_PREPARE_DONT_LOG, &stmt, 0);
```

`SQLITE_PREPARE_FROM_DDL` allows a virtual-table implementation to prepare SQL derived from the database schema safely (since 3.53.0).

## Runtime limits and function arity

- The minimum accepted `SQLITE_LIMIT_LENGTH` is 30 bytes, rather than 1 (since 3.48.0). Lower requests are clamped.
- The maximum SQL-function argument count increased from 127 to 1000 in 3.48.0, applying to built-in and application-defined calls.
- `SQLITE_LIMIT_PARSER_DEPTH` is a new `sqlite3_limit()` category (since 3.53.0).

## Database configuration

The following `sqlite3_db_config()` controls were added in 3.49.0 and default to enabled:

- `SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE`: whether `ATTACH` may create files.
- `SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE`: whether attached databases are writable.
- `SQLITE_DBCONFIG_ENABLE_COMMENTS`: whether comments are accepted in newly submitted SQL.

`SQLITE_DBCONFIG_FP_DIGITS` selects the significant-digit count used for floating-point-to-text conversion (since 3.53.0). The new default is 17 rather than 15.

## Text input and output

`SQLITE_UTF8_ZT` may be passed as the encoding to `sqlite3_bind_text64()` or `sqlite3_result_text64()` to identify zero-terminated UTF-8 (since 3.53.0).

## Hooks and page access

- Preupdate hooks recognize a non-NULL default on a column added by `ALTER TABLE ADD COLUMN` (since 3.47.0), so consumers observe the effective stored-row value.
- `INSERT` on the `sqlite_dbpage` table-valued function may grow or shrink the database file (since 3.47.0). Treat it as low-level file mutation and preserve page-size/integrity invariants.

## Blocking locks

`sqlite3_setlk_timeout()` configures blocking-lock waits independently from `sqlite3_busy_timeout()` on builds with blocking-lock support (since 3.50.0). Version 3.50.1 covers snapshot-transaction opening and waits behind recovery. Version 3.50.2 fixes mutex handling; use that maintenance release or later.

## Checkpoint and database status

`SQLITE_CHECKPOINT_NOOP` performs no checkpoint work while allowing checkpoint-interface inspection (since 3.51.0). SQL uses `PRAGMA wal_checkpoint=NOOP`.

`SQLITE_DBSTATUS_TEMPBUF_SPILL` reports temporary-buffer spills. Query it with `sqlite3_db_status()` or the new `sqlite3_db_status64()`, which provides 64-bit measurements (since 3.51.0).

## Incremental changegroups

Since 3.53.0, the session API can construct one `sqlite3_changegroup` change at a time:

1. Call `sqlite3changegroup_change_begin()`.
2. Supply typed values through the `change_blob`, `change_double`, `change_int64`, `change_null`, or `change_text` interfaces.
3. Complete the change with `sqlite3changegroup_change_finish()`.

Use `sqlite3changegroup_config()` to configure the changegroup object.

## Source metadata

The amalgamated `sqlite3.h` defines `SQLITE_SCM_BRANCH`, `SQLITE_SCM_TAGS`, and `SQLITE_SCM_DATETIME` for source-check-in metadata as of 3.51.0.

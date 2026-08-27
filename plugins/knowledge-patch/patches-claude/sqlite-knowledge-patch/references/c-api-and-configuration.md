# C APIs and Configuration

## Statement preparation and parser limits

### Validation-only prepares without error-log noise (since 3.48.0)

Pass `SQLITE_PREPARE_DONT_LOG` to `sqlite3_prepare_v3()` when test-compiling
SQL so ill-formed input does not send warning messages to SQLite's error log.

```c
sqlite3_prepare_v3(
    db, sql, -1, SQLITE_PREPARE_DONT_LOG, &stmt, NULL
);
```

### Minimum `SQLITE_LIMIT_LENGTH` (since 3.48.0)

The minimum allowed value is 30 instead of 1. Per-connection limit code must
not request a smaller value.

```c
sqlite3_limit(db, SQLITE_LIMIT_LENGTH, 30);
```

### DDL-derived preparation, UTF-8 text, and parser depth (since 3.53.0)

- `SQLITE_PREPARE_FROM_DDL` lets virtual-table implementations safely prepare
  schema-derived SQL with `sqlite3_prepare_v3()`.
- `SQLITE_UTF8_ZT` marks values passed through the 64-bit text bind/result
  interfaces as UTF-8 and zero-terminated.
- `SQLITE_LIMIT_PARSER_DEPTH` adds a parser-depth category to
  `sqlite3_limit()`.

```c
sqlite3_prepare_v3(
    db, sql, -1, SQLITE_PREPARE_FROM_DDL, &stmt, 0
);
sqlite3_limit(db, SQLITE_LIMIT_PARSER_DEPTH, max_depth);
```

## Per-connection controls

### ATTACH and comments (since 3.49.0)

These options independently control the named SQL capabilities and all
default to enabled:

- `SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE`
- `SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE`
- `SQLITE_DBCONFIG_ENABLE_COMMENTS`

```c
int enabled;
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0, &enabled);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0, &enabled);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_COMMENTS, 0, &enabled);
```

As of 3.50.0, disabling `SQLITE_DBCONFIG_ENABLE_COMMENTS` blocks comments
only in newly submitted SQL; comments already stored in `sqlite_schema`
remain readable. Version 3.50.3 fixes comment handling throughout
`CREATE TRIGGER` statements.

### Floating-point text precision (since 3.53.0)

Floating-point-to-text conversion rounds to 17 significant digits by default
instead of 15. `SQLITE_DBCONFIG_FP_DIGITS` changes the setting per connection.

## Blocking locks, checkpoints, and status

### Separate blocking-lock timeout (since 3.50.0)

`sqlite3_setlk_timeout()` sets a blocking-lock timeout independently of
`sqlite3_busy_timeout()` on builds that support blocking locks. Version
3.50.1 extends it to snapshot-transaction opens and recovery contention;
3.50.2 ensures the call holds the database mutex.

```c
sqlite3_setlk_timeout(db, 5000);
```

### No-op checkpoint and 64-bit status (since 3.51.0)

`PRAGMA wal_checkpoint=NOOP` and `SQLITE_CHECKPOINT_NOOP` request no-op
checkpoint mode. `sqlite3_db_status64()` mirrors `sqlite3_db_status()` with
64-bit results. Both status APIs accept `SQLITE_DBSTATUS_TEMPBUF_SPILL` to
inspect temporary-buffer spills.

```sql
PRAGMA wal_checkpoint=NOOP;
```

## Hooks and custom VFS capabilities

### Added-column defaults in preupdate hooks (since 3.47.0)

Preupdate hooks recognize a non-null default value for a column added with
`ALTER TABLE ADD COLUMN`, allowing change-capture code to observe the row's
effective value.

### Subpage reads in custom VFS implementations (since 3.47.1)

Custom VFS implementations can report `SQLITE_IOCAP_SUBPAGE_READ` to avoid
issues caused by direct overflow reads becoming the default in 3.45.0.

## Incremental session changegroups

As of 3.53.0, applications can add changes to a `sqlite3_changegroup` one at
a time with `sqlite3changegroup_change_begin()`, the typed
blob/double/int64/null/text setters, and
`sqlite3changegroup_change_finish()`. Use `sqlite3changegroup_config()` to
configure the changegroup.

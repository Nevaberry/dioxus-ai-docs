# C APIs and Configuration

Use this reference for connection controls, prepare flags, limits, hooks,
status reporting, changegroups, and low-level text configuration.

## Preparing SQL safely

### Validation without log noise (3.48.0)

Pass `SQLITE_PREPARE_DONT_LOG` to `sqlite3_prepare_v3()` when test-compiling SQL
so invalid input does not emit warning messages to SQLite's error log:

```c
sqlite3_prepare_v3(db, sql, -1, SQLITE_PREPARE_DONT_LOG, &stmt, NULL);
```

### Schema-derived SQL (3.53.0)

Virtual-table implementations that prepare SQL obtained from schema DDL should
pass `SQLITE_PREPARE_FROM_DDL` to `sqlite3_prepare_v3()`.

## Connection controls

### ATTACH and comment controls (3.49.0)

`SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE`,
`SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE`, and
`SQLITE_DBCONFIG_ENABLE_COMMENTS` independently control those capabilities.
All three default to enabled.

```c
int previous;
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0, &previous);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0, &previous);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_COMMENTS, 0, &previous);
```

### Existing schemas when comments are disabled (3.50.0)

Disabling `SQLITE_DBCONFIG_ENABLE_COMMENTS` blocks comments only in newly
submitted SQL. Comments in an existing `sqlite_schema` remain readable. Use
3.50.3 or later for correct comment handling throughout stored
`CREATE TRIGGER` statements.

## Runtime limits and text interfaces

### Length and function-argument limits (3.48.0)

The smallest accepted `SQLITE_LIMIT_LENGTH` is 30, not 1. SQL functions can
accept at most 1000 arguments rather than the former 127.

```c
sqlite3_limit(db, SQLITE_LIMIT_LENGTH, 30);
```

### Parser depth and zero-terminated UTF-8 (3.53.0)

`SQLITE_LIMIT_PARSER_DEPTH` is the parser-nesting category for
`sqlite3_limit()`. `SQLITE_UTF8_ZT` marks values passed through the 64-bit text
bind and result interfaces as UTF-8 and zero-terminated.

## Hooks, status, and changegroups

### Added-column defaults in preupdate hooks (3.47.0)

After `ALTER TABLE ADD COLUMN` adds a non-null default, preupdate hooks report
the existing row's effective default value for that column.

### No-op checkpoints and 64-bit status (3.51.0)

`SQLITE_CHECKPOINT_NOOP` is the C spelling of the no-op WAL checkpoint mode.
`sqlite3_db_status64()` mirrors `sqlite3_db_status()` with 64-bit results. Both
accept `SQLITE_DBSTATUS_TEMPBUF_SPILL` for temporary-buffer spill counts.

### Incremental session changegroups (3.53.0)

Add one change at a time to a `sqlite3_changegroup` with
`sqlite3changegroup_change_begin()`, the typed blob, double, int64, null, and
text setters, then `sqlite3changegroup_change_finish()`. Configure the group
with `sqlite3changegroup_config()`.

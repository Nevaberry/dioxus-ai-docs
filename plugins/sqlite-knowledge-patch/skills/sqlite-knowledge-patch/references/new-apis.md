# New C APIs — SQLite 3.46+

## sqlite3_setlk_timeout() (3.50.0)

Sets a separate timeout for blocking file locks, distinct from `sqlite3_busy_timeout()`. Only effective on builds that support blocking locks.

```c
int sqlite3_setlk_timeout(sqlite3 *db, int ms, unsigned int flags);
```

Use this when you want different timeout behavior for file-level locks vs busy retries.

## sqlite3_set_errmsg() (3.51.0)

Allows extensions to set the database error message. Useful for custom VFS implementations or extension functions that need to report meaningful errors.

```c
void sqlite3_set_errmsg(sqlite3 *db, const char *zFormat, ...);
```

## sqlite3_db_status64() (3.51.0)

64-bit version of `sqlite3_db_status()`. Returns 64-bit current and high-water values.

```c
int sqlite3_db_status64(
  sqlite3 *db,
  int op,
  sqlite3_int64 *pCurrent,
  sqlite3_int64 *pHighwater,
  int resetFlag
);
```

New status option: `SQLITE_DBSTATUS_TEMPBUF_SPILL` — reports temp buffer spills to disk.

## sqlite3changeset_apply_v3() (3.51.0)

Extended version of `sqlite3changeset_apply()` in the session extension.

## DBCONFIG Options (3.49.0)

Three new options for `sqlite3_db_config()`, all default to ON:

```c
// Prevent ATTACH from creating new database files
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0, 0);

// Make ATTACHed databases read-only
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0, 0);

// Disallow SQL comments (security hardening)
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_COMMENTS, 0, 0);
```

Note: `SQLITE_DBCONFIG_ENABLE_COMMENTS` (3.50.0 relaxation) always allows comments when reading schema from `sqlite_schema`.

## SQLITE_PREPARE_DONT_LOG (3.48.0)

Prevents warning messages from being sent to the error log when SQL is ill-formed. Useful for test-compiling SQL to check validity.

```c
sqlite3_stmt *pStmt;
int rc = sqlite3_prepare_v3(db, zSql, -1, SQLITE_PREPARE_DONT_LOG, &pStmt, 0);
if (rc == SQLITE_OK) {
  // SQL is valid
  sqlite3_finalize(pStmt);
}
```

## PRAGMA wal_checkpoint=NOOP (3.51.0)

Check if a WAL checkpoint is needed without actually performing one:

```sql
PRAGMA wal_checkpoint(NOOP);
```

C API equivalent: `SQLITE_CHECKPOINT_NOOP` argument to `sqlite3_wal_checkpoint_v2()`.

## SQLITE_FCNTL_NULL_IO (3.48.0)

File control that discards all writes and returns zeros for all reads. Useful for testing.

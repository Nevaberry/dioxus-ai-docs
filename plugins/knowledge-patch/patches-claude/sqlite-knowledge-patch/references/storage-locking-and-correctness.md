# Storage, Locking, and Correctness

## Withdrawn release

SQLite 3.52.0 was withdrawn because some new features caused backward-
compatibility issues. Its planned features moved to 3.53.0, so applications
should not target 3.52.0.

## Database-page resizing (since 3.47.0)

An `INSERT` on the `sqlite_dbpage` virtual table can increase or decrease the
size of the database file.

## OPFS and VFS compatibility

### `opfs` and `unix-dotfile` fixes (3.47.0)

SQLite 3.47.0 fixes a corruption-causing bug, read-only mode handling, and
browser-specific issues in the JavaScript `opfs` VFS. It also fixes
hot-journal rollback in the seldom-used `unix-dotfile` VFS.

### SAHPool filename-digest compatibility (since 3.50.0)

The JavaScript/WASM OPFS SAHPool VFS corrects its filename-digest calculation.
Version 3.50.0 can read databases made by older versions, but databases
created by 3.50.0 or later cannot be read by older SAHPool VFS versions.

### Web Locks OPFS VFS (since 3.53.0)

The `opfs-wl` JavaScript/WASM VFS is functionally equivalent to `opfs` but
uses Web Locks for fairer lock sharing. It requires `Atomics.waitAsync()` and
therefore newer browsers than `opfs`.

## Query and numeric correctness

### Query-result correctness

- Version 3.47.1 fixes incorrect answers for some `IN` queries caused by
  3.47.0's new optimizations.
- Version 3.49.2 fixes wrong results involving `DISTINCT` count-of-view plans
  or an `IN` operator using a `UNIQUE` constraint that contains the
  primary-key column.
- Version 3.50.2 corrects transitive `IS` constraints on `RIGHT JOIN`.
- Version 3.50.3 fixes incorrect answers caused by over-optimizing an `AND`
  expression.
- Version 3.51.1 fixes wrong results from nested `EXISTS` queries.
- Version 3.51.2 fixes further `EXISTS`-to-join problems.

### Numeric conversion correctness

Version 3.47.2 fixes x64/i386 text-to-floating-point conversion for affected
values whose first 16 significant digits are `1844674407370955`, a regression
introduced in 3.47.0.

## Memory and locking safety

- Version 3.49.1 fixes an out-of-bounds write in `concat_ws()` when its
  separator is larger than two megabytes.
- Version 3.49.2 fixes a memory error in the `NOT NULL` optimization.
- Version 3.51.2 fixes a deadlock in the new broken-POSIX-lock detection.

## WAL and database-file integrity

- Version 3.50.2 prevents checksum-free WAL frames after a savepoint rollback
  with spilled dirty pages.
- Version 3.51.3 fixes the WAL-reset database-corruption bug. Deployments on
  the 3.51 line should use 3.51.3 or later.

## FTS5 correctness

- Version 3.50.2 fixes updates of FTS5 tables containing BLOBs.
- Version 3.51.1 fixes an `fts5vocab` bug exposed by 3.51.0 optimizations.

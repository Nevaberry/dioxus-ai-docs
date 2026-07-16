# Storage, Locking, and Correctness

## Statistics and expression indexes

`PRAGMA optimize` applies a temporary analysis limit automatically and re-analyzes tables without `sqlite_stat1` entries (since 3.46.0). Add mask bit `0x10000` to consider every table, including tables this connection has not recently queried:

```sql
PRAGMA optimize=0x10002;
```

SQLite 3.53.0 adds self-healing support for stale expression indexes. `REINDEX EXPRESSIONS` remains available to rebuild all expression indexes explicitly:

```sql
REINDEX EXPRESSIONS;
```

## WAL and advisory locks

- Version 3.50.2 avoids creating checksumless WAL frames after rolling back a savepoint whose dirty pages had already spilled.
- Version 3.51.3 fixes a database-corruption bug during WAL reset. Use 3.51.3 or later on the 3.51 line.
- SQLite 3.51.0 added protection against corruption when an application breaks POSIX advisory locking by calling `close()` on an associated descriptor. Version 3.51.2 fixes a deadlock in that detection, so use 3.51.2 or later for this protection.
- `SQLITE_CHECKPOINT_NOOP` / `PRAGMA wal_checkpoint=NOOP` invokes checkpoint interfaces without performing checkpoint work (since 3.51.0).

## Vacuum copies and reserved bytes

When the destination is a URI, `VACUUM INTO` accepts `reserve=N` from 0 through 255 and assigns that many reserved bytes per page in the copied database (since 3.53.0):

```sql
VACUUM INTO 'file:copy.db?reserve=32';
```

## Direct page access

`INSERT` operations on `sqlite_dbpage` may grow or shrink the file (since 3.47.0). Code using this low-level interface must preserve database page structure and transactional safety.

## Native VFS compatibility

Custom VFS implementations may report `SQLITE_IOCAP_SUBPAGE_READ` (since 3.47.1). Use it where appropriate to avoid problems associated with direct overflow reads, which became the default in 3.45.0.

## WASM OPFS VFSes

- SQLite 3.46.1 fixes a corruption-causing bug in the JavaScript `opfs` VFS and adds browser-specific OPFS workarounds. OPFS applications should not remain on 3.46.0.
- The OPFS SAHPool VFS corrected its filename-digest calculation in 3.50.0. New SQLite can read databases from older SAHPool releases, but older VFS versions cannot read databases created by 3.50.0 or later.
- The `opfs-wl` VFS uses Web Locks for fairer lock sharing while otherwise matching `opfs` behavior (since 3.53.0). It requires browser support for `Atomics.waitAsync()`.
- Custom JavaScript/WASM builds can target 64-bit WASM through the normal `make` build as of 3.51.0; canonical builds remain 32-bit.

## Maintenance-release correctness

- 3.47.1 fixes wrong answers for some `IN` queries introduced by 3.47.0 optimization work.
- 3.47.2 fixes x64/i386 conversion of text to floating point for a narrow family of 16-significant-digit inputs.
- 3.50.1 fixes a long-standing `jsonb_set()`-family bug exposed by JSONB update optimization.
- 3.50.2 fixes FTS5 updates containing BLOBs and `RIGHT JOIN` queries involving transitive `IS` constraints.
- 3.50.3 fixes incorrect answers from an over-optimized `AND` expression.
- 3.51.1 and 3.51.2 fix wrong answers and related faults in the `EXISTS`-to-join optimization; 3.51.1 also fixes an `fts5vocab` fault exposed by it.

## Withdrawn release

SQLite 3.52.0 was withdrawn because of backward-compatibility issues. All features planned for it moved to 3.53.0. Do not use 3.52.0 as a deployment target.

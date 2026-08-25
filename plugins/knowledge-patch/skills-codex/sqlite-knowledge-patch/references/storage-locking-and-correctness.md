# Storage, Locking, and Correctness

Use this reference for optimizer maintenance, page access, expression indexes,
locking, WAL, `VACUUM`, VFS behavior, and release-specific correctness fixes.

## Analysis and indexes

### Bounded and all-table optimization (3.46.0)

`PRAGMA optimize` temporarily limits analysis work so it does not run too long
on large databases. It also reanalyzes tables that lack `sqlite_stat1` entries.
Add option bit `0x10000` to consider every table rather than only tables used
recently by the connection:

```sql
PRAGMA optimize;
-- Include option bit 0x10000 when every table must be considered.
```

### Expression-index repair (3.53.0)

Rebuild stale expression-index values explicitly with:

```sql
REINDEX EXPRESSIONS;
```

SQLite can also self-heal stale expression indexes during normal operation.

## Database pages and file generation

### Resizing through `sqlite_dbpage` (3.47.0)

An `INSERT` on the `sqlite_dbpage` virtual table may increase or decrease the
database file's size. Treat such writes as low-level file operations and verify
the resulting page layout.

### Reserve bytes in `VACUUM INTO` (3.53.0)

When the output is a URI filename, `reserve=N` sets its reserve amount. `N`
must be from 0 through 255:

```sql
VACUUM INTO 'file:copy.db?reserve=32';
```

## Blocking locks and WAL

### Independent blocking-lock timeout (3.50.0)

On builds that support blocking locks, `sqlite3_setlk_timeout()` controls a
lock-wait timeout independently of `sqlite3_busy_timeout()`. Version 3.50.1
extends it to opening snapshot transactions and waiting behind recovery. Use
3.50.2 or later because it ensures the call holds the database mutex.

```c
sqlite3_setlk_timeout(db, 5000);
```

### WAL maintenance fixes (3.50.0, 3.51.0)

- Version 3.50.2 prevents checksum-free WAL frames after a savepoint rollback
  involving spilled dirty pages.
- Version 3.51.3 repairs a WAL-reset database-corruption bug. Deployments that
  remain on the 3.51 line should use 3.51.3 or later.
- Version 3.51.2 repairs a deadlock in broken POSIX-lock detection.

## Browser and Unix VFS behavior

### OPFS and unix-dotfile correctness (3.47.0)

SQLite 3.47.0 fixes a corruption-causing bug, read-only behavior, and
browser-specific issues in the JavaScript `opfs` VFS. It also fixes hot-journal
rollback in the uncommon `unix-dotfile` VFS.

### Custom VFS subpage reads (3.47.0)

From 3.47.1, a custom VFS can report `SQLITE_IOCAP_SUBPAGE_READ`. Use it when
the VFS safely supports direct overflow reads; this avoids compatibility
problems after direct overflow reads became the default in 3.45.0.

### OPFS SAHPool format boundary (3.50.0)

The corrected filename-digest calculation is backward-readable: 3.50.0 can
read databases made by older SAHPool implementations. The reverse is false;
older implementations cannot read databases created by 3.50.0 or later.

### Web Locks VFS (3.53.0)

The `opfs-wl` JavaScript/WASM VFS is functionally equivalent to `opfs` but
uses Web Locks for fairer sharing. It requires `Atomics.waitAsync()`, so its
browser baseline is newer than that of `opfs`.

## Numeric and query correctness

### Text-to-floating-point conversion (3.47.0)

Version 3.47.2 repairs x64/i386 conversion for affected values whose first 16
significant digits are `1844674407370955`, a regression introduced in 3.47.0.

### Query-planner maintenance fixes (3.47.0, 3.49.0, 3.50.0, 3.51.0)

- 3.47.1 fixes wrong answers in some `IN` queries.
- 3.49.2 fixes a `NOT NULL` optimization memory error, `DISTINCT`
  count-of-view plans, and `IN` plans involving a `UNIQUE` constraint that
  contains the primary-key column.
- 3.50.2 fixes transitive `IS` constraints on `RIGHT JOIN`; 3.50.3 fixes an
  over-optimized `AND` expression.
- 3.51.1 and 3.51.2 repair nested `EXISTS` and `EXISTS`-to-join wrong results.

## Withdrawn target

### Do not deploy 3.52.0

SQLite 3.52.0 was withdrawn because new features caused backward-compatibility
problems. Those planned features moved to 3.53.0; do not target 3.52.0.

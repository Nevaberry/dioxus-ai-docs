---
name: sqlite-knowledge-patch
description: SQLite 3.46.0–3.53.0 compatibility. Use for SQLite work.
license: MIT
version: 3.53.0
metadata:
  author: Nevaberry
---

# SQLite Knowledge Patch

Baseline: SQLite through 3.45. Covered range: SQLite 3.46.0 through 3.53.0, plus current core scalar-function and JSON/JSONB semantics.

## Reference index

| Reference | Topics |
|---|---|
| [SQL language and schema](references/sql-language-and-schema.md) | `ALTER TABLE`, constraints, triggers, literals, query behavior, STRICT tables |
| [Core scalar functions](references/core-scalar-functions.md) | `iif()`, date/time, formatting, string/numeric functions, planner hints |
| [JSON and JSONB](references/json-and-jsonb.md) | Validation, paths, extraction, mutation, traversal, aggregates, JSON5 |
| [C APIs and configuration](references/c-api-and-configuration.md) | Prepare flags, limits, db-config controls, hooks, status, changegroups |
| [Storage, locking, and correctness](references/storage-locking-and-correctness.md) | WAL, locks, indexes, `VACUUM`, page access, VFS and WASM storage |
| [FTS5, sessions, and extensions](references/fts5-sessions-and-extensions.md) | Tokenizers, contentless FTS5, sessions, bundled extensions |
| [CLI, builds, and utilities](references/cli-build-and-utilities.md) | Shell behavior, build systems, Tcl, `sqlite3_rsync`, `sqldiff`, analyzer |

## Release and compatibility warnings

- SQLite 3.52.0 was withdrawn for backward-compatibility problems. Its planned features moved to 3.53.0; do not target the withdrawn release.
- On the 3.51 line, use 3.51.3 or later: 3.51.3 fixes a WAL-reset corruption bug. Version 3.51.2 is also required to avoid a deadlock in POSIX-lock misuse detection.
- For blocking-lock timeouts introduced in 3.50.0, use 3.50.2 or later; that maintenance release corrects mutex handling. For `sqlite3_rsync`, use 3.50.1 or later because 3.50.0 could omit the replica's final page.
- SQLite 3.46.1 fixes a corruption-causing bug in the JavaScript `opfs` VFS. Update WASM applications that use OPFS.
- OPFS SAHPool databases written by 3.50.0 or later cannot be read by older SAHPool VFS versions.
- Floating-point-to-text conversion uses 17 significant digits by default as of 3.53.0, rather than 15. Use `SQLITE_DBCONFIG_FP_DIGITS` when the old presentation is required.
- Generated columns in `STRICT` tables now enforce their declared types. A computed value that cannot be converted is rejected.
- `.indexes PATTERN` now matches index names, not indexed table names. Audit shell scripts that depend on the former behavior.
- `SQLITE_USE_STDIO_FOR_CONSOLE` was removed. Windows command-line builds can use `SQLITE_USE_W32_FOR_CONSOLE_IO` instead.
- Windows RT is no longer supported.

## Schema changes and repair

SQLite 3.53.0 can add or remove `NOT NULL` and `CHECK` constraints directly. Consult the SQLite grammar for the precise constraint form before generating migration SQL. TEMP trigger bodies may now access `main`, and the second argument to trigger `RAISE()` may be an expression:

```sql
CREATE TEMP TRIGGER validate_order
BEFORE INSERT ON main.orders
BEGIN
  SELECT RAISE(ABORT, 'invalid order: ' || NEW.id)
  WHERE NEW.total < 0;
END;
```

Expression indexes have explicit repair and self-healing support in 3.53.0:

```sql
REINDEX EXPRESSIONS;
```

Use this after discovering stale stored expression-index values; automatic self-healing may repair them during normal operation.

## JSON and JSONB essentials

SQLite JSONB is an opaque SQLite BLOB, not a PostgreSQL-compatible encoding and not an O(1) lookup structure. Do not parse or construct it outside SQLite.

Use validation flags deliberately:

```sql
-- Canonical JSON text only:
SELECT json_valid(value);

-- Canonical text, JSON5 text, or superficially valid JSONB:
SELECT json_valid(value, 6);

-- Deep JSONB validation:
SELECT json_valid(value, 8);
```

`jsonb_each()` and `jsonb_tree()` preserve JSONB in `value` for arrays and objects. Their text counterparts convert container values to text JSON.

```sql
SELECT fullkey, value
FROM jsonb_tree(jsonb('{"items":[1,2]}'));
```

New in 3.53.0, `json_array_insert()` and `jsonb_array_insert()` insert values into JSON and JSONB arrays respectively.

Remember the value subtype rule: ordinary SQL text passed to a `value` argument becomes a quoted JSON string. Wrap it in `json()`/`jsonb()` or feed it directly from `->` to insert structured JSON. `->>` yields an SQL scalar.

## Conditional and text functions

`iif()` evolved across two releases. In 3.48.0, it gained the two-argument form and the `if()` alias; in 3.49.0 it became variadic:

```sql
SELECT iif(enabled, 'yes');
SELECT if(enabled, 'yes');
SELECT iif(score >= 90, 'A', score >= 80, 'B', 'other');
```

The variadic form evaluates condition/value pairs in order and may end with a fallback. With no true condition and no fallback, it returns `NULL`.

Use `unistr()` for backslash escapes and `unistr_quote()` for safely quoted text containing control characters. `%#q` and `%#Q` escape controls for `unistr()`:

```sql
SELECT format('%#Q', char(1));
```

As of 3.50.2, `concat_ws()` retains empty-string arguments:

```sql
SELECT concat_ws(',', 'a', '', 'b'); -- a,,b
```

`group_concat()` now preserves an all-empty-string result in both window and ordinary aggregate forms instead of returning `NULL`.

## Connection hardening and validation

Three connection controls, enabled by default, can restrict SQL capabilities:

```c
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0, &oldValue);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0, &oldValue);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_COMMENTS, 0, &oldValue);
```

Disabling comments affects newly submitted SQL, not parsing of an existing `sqlite_schema`. Comments remain ignored throughout a stored `CREATE TRIGGER` statement.

For validation-only prepares, avoid warning-log noise with `SQLITE_PREPARE_DONT_LOG`:

```c
sqlite3_prepare_v3(db, sql, -1, SQLITE_PREPARE_DONT_LOG, &stmt, 0);
```

Virtual-table implementations preparing schema-derived SQL should instead add `SQLITE_PREPARE_FROM_DDL`.

The runtime limits changed: the minimum `SQLITE_LIMIT_LENGTH` is 30 bytes, the SQL-function argument ceiling is 1000, and `SQLITE_LIMIT_PARSER_DEPTH` is a new parser-depth category.

## Locking, WAL, and status

On builds with blocking locks, `sqlite3_setlk_timeout()` sets a lock-wait timeout independently of `sqlite3_busy_timeout()`. Later 3.50 maintenance releases extend it to opening snapshot transactions and waiting behind recovery.

Checkpoint without doing checkpoint work:

```sql
PRAGMA wal_checkpoint=NOOP;
```

The C spelling is `SQLITE_CHECKPOINT_NOOP`. Inspect temporary-buffer spills through `SQLITE_DBSTATUS_TEMPBUF_SPILL` using `sqlite3_db_status()` or the new 64-bit `sqlite3_db_status64()`.

`PRAGMA optimize` now applies a temporary analysis limit and revisits tables missing `sqlite_stat1` entries. Include `0x10000` to consider every table, including those the connection has not queried recently:

```sql
PRAGMA optimize=0x10002;
```

## CLI behavior to account for

- Interactive sessions default to Unicode box output and right-align numbers in tabular modes; batch sessions keep the legacy format.
- Existing non-empty `*.sql` and `*.txt` command-line arguments execute as scripts.
- An unquoted trailing semicolon on a dot-command is ignored.
- `.timer once` times the next statement only; `.progress --timeout S` interrupts after `S` seconds.
- Startup and `.open` accept `--ifexists`.
- `.imposter` is read-only, works with `VACUUM`, and no longer requires `--unsafe-testing`.
- `.dump` uses `unistr()` for special characters unless escape mode is disabled, and the shell suppresses most raw control characters.
- `.width` is capped at 30,000; `.timer` reports microseconds; `box` and `column` modes account for double-wide characters.

Load the topic references before depending on edge semantics, maintenance-release fixes, compile-time options, or utility-specific behavior.

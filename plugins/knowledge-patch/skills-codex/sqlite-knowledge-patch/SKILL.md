---
name: sqlite-knowledge-patch
description: SQLite
version: 3.53.0
license: MIT
metadata:
  author: Nevaberry
---


# SQLite Knowledge Patch

Load this skill when SQLite version differences affect SQL, schema migration,
JSON handling, extension code, storage behavior, command-line automation, or
build configuration. Check the project's pinned SQLite library and runtime,
then apply only guidance available in that version. Prefer the application,
tests, and compiled feature set when they disagree with assumptions.

## Reference index

| Reference | Read for |
|---|---|
| [SQL language and schema](references/sql-language-and-schema.md) | `ALTER TABLE`, defaults, triggers, constraints, queries, and `STRICT` tables |
| [Core scalar functions](references/core-scalar-functions.md) | `iif()`, date/time, formatting, string, numeric, comparison, and planner functions |
| [JSON and JSONB](references/json-and-jsonb.md) | Validation, paths, extraction, mutation, traversal, aggregates, and JSON5 |
| [C APIs and configuration](references/c-api-and-configuration.md) | Prepare flags, limits, db-config controls, hooks, status, and changegroups |
| [Storage, locking, and correctness](references/storage-locking-and-correctness.md) | WAL, locks, indexes, `VACUUM`, page access, VFS behavior, and maintenance fixes |
| [FTS5, sessions, and extensions](references/fts5-sessions-and-extensions.md) | Tokenizers, contentless FTS5, session tracking, and bundled extensions |
| [CLI, builds, and utilities](references/cli-build-and-utilities.md) | Shell behavior, build systems, Tcl, WASM, `sqlite3_rsync`, `sqldiff`, and analyzer |

## Compatibility priorities

Treat these as upgrade blockers or deployment checks before adopting newer
features:

- Do not target SQLite 3.52.0. It was withdrawn for backward-compatibility
  problems; its planned features moved to 3.53.0.
- On the 3.51 line, use 3.51.3 or later. It repairs a WAL-reset corruption bug;
  3.51.2 also fixes deadlock behavior in broken POSIX-lock detection.
- For blocking-lock timeout use, select 3.50.2 or later so
  `sqlite3_setlk_timeout()` holds the database mutex. Its expanded snapshot and
  recovery behavior begins in 3.50.1.
- For `sqlite3_rsync`, avoid 3.50.0 because it can omit the replica's final
  page; use 3.50.1 or later.
- Databases created by the corrected OPFS SAHPool VFS in 3.50.0 or later are
  unreadable by older SAHPool implementations. Coordinate browser deployment
  and rollback plans.
- Generated columns in `STRICT` tables enforce their declared types. Test
  generated expressions against real data before upgrading.
- Floating-point-to-text conversion uses 17 significant digits by default in
  3.53.0. Use `SQLITE_DBCONFIG_FP_DIGITS` when output compatibility requires a
  different setting.
- `.indexes PATTERN` now matches index names rather than indexed table names.
  Audit scripts that parse its results.
- Windows RT is unsupported, and Windows CLI builds must replace removed
  `SQLITE_USE_STDIO_FOR_CONSOLE` usage with
  `SQLITE_USE_W32_FOR_CONSOLE_IO` when Win32 console APIs are wanted.

Read [Storage, locking, and correctness](references/storage-locking-and-correctness.md)
and [CLI, builds, and utilities](references/cli-build-and-utilities.md) before a
production upgrade or cross-version rollback.

## Schema migrations and repair

SQLite can directly add or remove `NOT NULL` and `CHECK` constraints. Confirm
the exact grammar supported by the target runtime before generating a
migration. TEMP trigger bodies may access `main`, and a trigger `RAISE()`
message may be an expression:

```sql
CREATE TEMP TRIGGER validate_order
BEFORE INSERT ON main.orders
BEGIN
  SELECT RAISE(ABORT, 'invalid order: ' || NEW.id)
  WHERE NEW.total < 0;
END;
```

Repair stale stored expression-index values explicitly when necessary:

```sql
REINDEX EXPRESSIONS;
```

SQLite can also self-heal stale expression indexes during ordinary work. Read
[SQL language and schema](references/sql-language-and-schema.md) for defaults,
query correctness, and `STRICT` behavior, and [Storage, locking, and
correctness](references/storage-locking-and-correctness.md) for index repair and
file-level operations.

## JSON and JSONB essentials

Validate JSON and JSONB input according to the accepted formats:

```sql
-- Canonical JSON text only.
SELECT json_valid(value);

-- JSON5 text or superficially valid JSONB.
SELECT json_valid(value, 6);

-- Deep, linear-time JSONB validation.
SELECT json_valid(value, 8);
```

`jsonb()` checks only the outermost element of input that already resembles
JSONB. Malformed JSONB may error or return unreliable answers, although it does
not create memory-safety failures.

Use `jsonb_each()` and `jsonb_tree()` when array and object rows must remain
JSONB in `value`.

```sql
SELECT fullkey, type, value
FROM jsonb_tree(jsonb('{"items":[{"id":1}]}'));
```

`json_array_insert()` and `jsonb_array_insert()` insert into arrays. A negative
integer used with `->>` counts from the end, but a text operand that
looks numeric remains an object label. Read [JSON and
JSONB](references/json-and-jsonb.md) before relying on JSON5 spellings, BLOB
compatibility, duplicate labels, path ordering, or traversal metadata.

## Conditional, text, and formatting functions

Use the two-argument `iif()`/`if()` form for a true value or `NULL`, and the
variadic form for ordered condition/value pairs plus an optional fallback:

```sql
SELECT if(enabled, 'yes');
SELECT iif(score >= 90, 'A', score >= 80, 'B', 'other');
```

`unistr()` interprets backslash escapes; `unistr_quote()` creates safely quoted
SQL text. The `#` flag for `%q` and `%Q` emits control-safe escapes:

```sql
SELECT unistr('\u0041'), format('%#Q', char(1));
```

As of 3.50.2, `concat_ws()` preserves empty-string arguments, and
`group_concat()` preserves a sole empty-string result. Consult [Core scalar
functions](references/core-scalar-functions.md) for formatting defaults,
encoded lengths, collation selection, numeric conversion, substring behavior,
and planner hints.

## Connection hardening and validation

These per-connection controls default to enabled; disable only the capabilities
the connection must not expose:

```c
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0, &old_value);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0, &old_value);
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_COMMENTS, 0, &old_value);
```

Disabling comments affects newly submitted SQL, not an existing
`sqlite_schema`; stored `CREATE TRIGGER` statements remain parseable. For
validation-only prepares, suppress warning-log noise with
`SQLITE_PREPARE_DONT_LOG`. Virtual tables preparing schema-derived SQL should
use `SQLITE_PREPARE_FROM_DDL` instead.

```c
sqlite3_prepare_v3(db, sql, -1, SQLITE_PREPARE_DONT_LOG, &stmt, 0);
```

The minimum `SQLITE_LIMIT_LENGTH` is 30, SQL functions may accept up to 1000
arguments, and `SQLITE_LIMIT_PARSER_DEPTH` controls parser nesting. Read [C
APIs and configuration](references/c-api-and-configuration.md) for hook,
changegroup, text-interface, and status details.

## Locking, WAL, and diagnostics

On builds with blocking-lock support, `sqlite3_setlk_timeout()` controls lock
waiting independently of `sqlite3_busy_timeout()`. Request checkpoint state
without checkpoint work using either spelling:

```sql
PRAGMA wal_checkpoint=NOOP;
```

Use `SQLITE_DBSTATUS_TEMPBUF_SPILL` with `sqlite3_db_status()` or
`sqlite3_db_status64()` to observe temporary-buffer spills. `PRAGMA optimize`
uses a temporary analysis limit and reanalyzes tables missing `sqlite_stat1`;
add `0x10000` when every table must be considered:

```sql
PRAGMA optimize;
-- Include option bit 0x10000 when every table must be considered.
```

## CLI and build behavior

Interactive sessions default to Unicode box output and right-aligned numbers
in tabular modes; batch output retains the legacy format. Existing non-empty
`*.sql` and `*.txt` command-line arguments execute as scripts. A trailing
unquoted semicolon on a dot-command is ignored.

```text
sqlite3 --ifexists app.db setup.sql
.timer once
.progress --timeout 5
```

`.timer once` times one statement, `.progress --timeout S` interrupts after
`S` seconds, and startup plus `.open` accept `--ifexists`. `.imposter` is
read-only, works with `VACUUM`, and does not need `--unsafe-testing`. `.dump`
uses `unistr()` for special characters unless escape mode is disabled. Before
automating the shell or distributing a custom build, read [CLI, builds, and
utilities](references/cli-build-and-utilities.md).

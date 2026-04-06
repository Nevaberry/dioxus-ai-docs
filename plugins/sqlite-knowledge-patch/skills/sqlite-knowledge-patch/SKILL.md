---
name: sqlite-knowledge-patch
description: "SQLite changes since training cutoff (latest: 3.51) — json_pretty, unistr, jsonb_each/jsonb_tree, percentile aggregates, multi-arg iif, numeric underscores, sqlite3_setlk_timeout. Load before working with SQLite."
license: MIT
version: "3.51"
metadata:
  author: Nevaberry
---

# SQLite 3.46+ Knowledge Patch

Claude's baseline knowledge covers SQLite through 3.45. This skill provides changes from 3.46.0 (2024-05-23) onwards.

## New SQL Functions

| Function | Version | Description |
|----------|---------|-------------|
| `json_pretty(X)` / `json_pretty(X,indent)` | 3.46.0 | Pretty-print JSON with optional indent string |
| `unistr(X)` | 3.50.0 | Convert string with `\uXXXX` Unicode escapes to characters |
| `unistr_quote(X)` | 3.50.0 | Quote string using Unicode escape syntax |
| `jsonb_each(X)` | 3.51.0 | Like `json_each()` but returns JSONB for array/object values |
| `jsonb_tree(X)` | 3.51.0 | Like `json_tree()` but returns JSONB for array/object values |
| `median(X)` | 3.47.0 | Median aggregate (CLI extension) |
| `percentile(X,P)` | 3.47.0 | Percentile aggregate (CLI extension) |
| `percentile_cont(X,P)` | 3.47.0 | Continuous percentile (CLI extension) |
| `percentile_disc(X,P)` | 3.47.0 | Discrete percentile (CLI extension) |

## iif() / if() Enhancements

```sql
-- 3.48.0: if() is an alias for iif()
-- 3.48.0: 2-argument form returns NULL when false
SELECT
  if (x > 0, 'positive');

-- NULL when x <= 0
-- 3.49.0: accepts any number of args >= 2 (chained if/elseif)
SELECT
  iif (x > 0, 'positive', x < 0, 'negative', 'zero');
```

## Numeric Literal Underscores (3.46.0)

```sql
SELECT
  1_000_000;

-- 1000000
SELECT
  3.141_592_653;

-- 3.141592653
SELECT
  0xFF_FF;

-- 65535
```

## Date/Time Enhancements (3.46.0)

```sql
-- New strftime format specifiers
SELECT strftime('%G', 'now');  -- ISO 8601 week-numbering year
SELECT strftime('%V', 'now');  -- ISO 8601 week number

-- Ceiling/floor modifiers for ambiguous month shifts
SELECT date('2024-01-31', '+1 month', 'ceiling');  -- 2024-03-01
SELECT date('2024-01-31', '+1 month', 'floor');    -- 2024-02-29
```

## New C APIs

See [references/new-apis.md](references/new-apis.md) for details.

- `sqlite3_setlk_timeout()` (3.50.0) — separate timeout for blocking locks
- `sqlite3_set_errmsg()` (3.51.0) — extensions can set error messages
- `sqlite3_db_status64()` (3.51.0) — 64-bit version of `sqlite3_db_status()`
- `sqlite3changeset_apply_v3()` (3.51.0) — session extension

## DBCONFIG Options

```c
// 3.49.0 — all default to ON
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_CREATE, 0, 0); // prevent ATTACH creating new DBs
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_ATTACH_WRITE, 0, 0);  // make ATTACH read-only
sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_COMMENTS, 0, 0);      // disallow SQL comments
```

## JSON Operator Change (3.47.0)

```sql
-- Negative RHS on ->> accesses from the right of an array
SELECT '[10,20,30]' ->> -1;  -- 30 (last element)
SELECT '[10,20,30]' ->> -2;  -- 20 (second to last)
```

## FTS5 Enhancements

- **3.47.0**: `fts5_tokenizer_v2` API and `locale=1` option for locale-aware tokenizers
- **3.47.0**: `contentless_unindexed=1` for contentless tables with persistent UNINDEXED columns
- **3.48.0**: `insttoken` config option and `fts5_insttoken()` function for prefix queries
- **3.51.0**: STRICT typing enforced on computed columns

## Other Notable Changes

- **3.47.0**: `group_concat()` returns empty string (not NULL) for single empty string input
- **3.47.0**: `sqlite3_rsync` — experimental tool for replicating SQLite databases
- **3.48.0**: Max function arguments increased from 127 to 1000
- **3.48.0**: Build only requires C compiler + make (no TCL dependency)
- **3.50.0**: `%Q`/`%q` printf with `#` flag converts control chars to `unistr()` escapes
- **3.51.0**: `PRAGMA wal_checkpoint=NOOP` — check if checkpoint is needed without doing one
- **3.51.0**: `carray` and `percentile` extensions in amalgamation (compile with `-DSQLITE_ENABLE_CARRAY` / `-DSQLITE_ENABLE_PERCENTILE`)

---
name: sqlite-knowledge-patch
description: "SQLite changes since training cutoff (latest: 3.51.0) — JSON enhancements, new SQL functions, FTS5 locale support, date modifiers, JSONB table functions. Load before working with SQLite."
license: MIT
metadata:
  author: Nevaberry
  version: "3.51.0"
---

# SQLite 3.46–3.51 Knowledge Patch

Claude's baseline knowledge covers SQLite through ~3.45. This skill provides features from 3.46.0 (May 2024) onwards.

## Quick Reference

### JSON Functions & Operators

| Feature | Since | Description |
|---------|-------|-------------|
| `json_pretty(json)` | 3.46.0 | Format JSON with indentation |
| `json_pretty(json, indent)` | 3.46.0 | Custom indent string (spaces, tab) |
| Negative `->>`/`->` indices | 3.47.0 | `'[1,2,3]' ->> -1` → `3` |
| `jsonb_each(json)` | 3.51.0 | Like `json_each()` but returns JSONB for nested values |
| `jsonb_tree(json)` | 3.51.0 | Like `json_tree()` but returns JSONB for nested values |

See `references/json.md` for examples and usage details.

### SQL Functions & Syntax

| Feature | Since | Description |
|---------|-------|-------------|
| Underscore in numeric literals | 3.46.0 | `1_000_000`, `0xFF_FF` |
| `iif()` two-argument form | 3.48.0 | `iif(cond, val)` — returns NULL when false |
| `if()` alias for `iif()` | 3.48.0 | Drop-in replacement |
| Variadic `iif()` | 3.49.0 | `iif(c1, v1, c2, v2, ..., default)` — compact CASE |
| `unistr(str)` | 3.50.0 | Interpret `\uXXXX` escape sequences |
| `unistr_quote(str)` | 3.50.0 | Reverse of `unistr()` — escape non-printable chars |
| `format('%#Q', val)` | 3.50.0 | `%Q`/`%q` with `#` flag escapes control chars via unistr |

See `references/sql-functions.md` for examples and usage details.

### Date/Time Enhancements

| Feature | Since | Description |
|---------|-------|-------------|
| `ceiling` modifier | 3.46.0 | Ambiguous date → next valid date |
| `floor` modifier | 3.46.0 | Ambiguous date → last day of target month |

```sql
-- Jan 31 + 1 month: Feb has no 31st
SELECT
  date ('2024-01-31', '+1 month');

-- 2024-03-03 (default: overflow)
SELECT
  date ('2024-01-31', '+1 month', 'ceiling');

-- 2024-03-01 (next valid date)
SELECT
  date ('2024-01-31', '+1 month', 'floor');

-- 2024-02-29 (last day of target month)
```

### FTS5 & Internals

| Feature | Since | Description |
|---------|-------|-------------|
| FTS5 `locale=1` | 3.47.0 | Locale-aware tokenization via `fts5_locale()` |
| FTS5 `contentless_unindexed=1` | 3.47.0 | Store UNINDEXED column values in contentless tables |
| STRICT computed column enforcement | 3.51.0 | Generated columns in STRICT tables now enforce type affinity |
| `PRAGMA wal_checkpoint(NOOP)` | 3.51.0 | Query WAL checkpoint status without checkpointing |

See `references/fts5-internals.md` for examples and usage details.

## Essentials

### Variadic `iif()` / `if()` — Compact CASE Replacement

The most commonly useful addition. Works like a compact CASE expression:

```sql
-- Two-arg form (3.48.0): returns NULL when false
SELECT iif(score > 90, 'excellent');

-- if() is an alias (3.48.0)
SELECT if(x > 0, 'positive', 'non-positive');

-- Variadic form (3.49.0): cascading conditions like CASE
-- iif(cond1, val1, cond2, val2, ..., default)
SELECT iif(
score > 90,
'excellent',
score > 70,
'good',
'needs work'
);
```

### Underscore in Numeric Literals (3.46.0)

```sql
SELECT 1_000_000;        -- 1000000
SELECT 3.141_592_653;    -- 3.141592653
SELECT 0xFF_FF;           -- 65535
```

### JSON Pretty-Print (3.46.0)

```sql
SELECT json_pretty('{"a":1,"b":[2,3]}');
-- {
--     "a": 1,
--     "b": [
--         2,
--         3
--     ]
-- }
-- Custom indent string (default: 4 spaces)
SELECT json_pretty('{"a":1}', '  ');     -- 2-space indent
SELECT json_pretty('{"a":1}', char(9));  -- tab indent
```

### Negative JSON Array Indexing (3.47.0)

```sql
SELECT '[10,20,30]' ->> -1;   -- 30 (last element)
SELECT '[10,20,30]' ->> -2;   -- 20 (second to last)
-- json_extract already had #-N syntax:
SELECT '{"a":[1,2,3]}' -> '$.a[#-1]';  -- 3
```

### JSONB Table Functions (3.51.0)

More efficient for JSON processing pipelines — nested arrays/objects stay in binary JSONB format:

```sql
SELECT key, value FROM jsonb_each('{"a":1,"b":[2,3]}');
-- key: 'a', value: 1
-- key: 'b', value: (JSONB blob of [2,3]) instead of text '[2,3]'

SELECT * FROM jsonb_tree('{"a":{"b":1}}');
-- Recursively walks JSON tree, nested objects/arrays as JSONB
```

### Unicode String Functions (3.50.0)

```sql
SELECT unistr('Hello\u0021');       -- 'Hello!'
SELECT unistr('\u00e9');             -- 'é'
SELECT unistr_quote('Hello!');      -- 'Hello\u0021'
```

The `format()` function's `%Q`/`%q` with `#` flag escapes control characters:

```sql
SELECT format('%#Q', char(9) || 'tab');  -- unistr('\0009tab') style output
```

### FTS5 Contentless with Stored Columns (3.47.0)

```sql
CREATE VIRTUAL TABLE t1 USING fts5(
  body,
  title UNINDEXED,
  content='',
  contentless_unindexed=1  -- title values are stored, not just indexed
);
```

### WAL Checkpoint Status Without Checkpointing (3.51.0)

```sql
PRAGMA wal_checkpoint(NOOP);  -- returns (busy, log, checkpointed) without doing work
```

## Reference Files

| File | Contents |
|------|----------|
| `json.md` | json_pretty, negative indexing, jsonb_each, jsonb_tree |
| `sql-functions.md` | iif/if variadic, unistr, unistr_quote, format %#Q, underscores in literals |
| `fts5-internals.md` | FTS5 locale, contentless_unindexed, STRICT columns, wal_checkpoint NOOP |

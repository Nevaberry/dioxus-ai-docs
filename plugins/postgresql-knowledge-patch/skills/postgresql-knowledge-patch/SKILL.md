---
name: postgresql-knowledge-patch
description: "PostgreSQL changes since training cutoff (latest: 18.1) — JSON_TABLE, SQL/JSON functions, MERGE RETURNING, virtual generated columns, UUIDv7, temporal PRIMARY KEY. Load before working with PostgreSQL."
license: MIT
version: "18.1"
metadata:
  author: Nevaberry
---

# PostgreSQL 17+ Knowledge Patch

Claude's baseline knowledge covers PostgreSQL through 16. This skill provides features from 17 (Sep 2024) onwards.

**Source**: PostgreSQL release notes at https://www.postgresql.org/docs/release/

## PostgreSQL 17 (Sep 2024)

### SQL/JSON (Major)

| Function | Purpose | Example |
|----------|---------|---------|
| `JSON_TABLE()` | JSON → table rows | `FROM JSON_TABLE(data, '$.items[*]' COLUMNS (id int PATH '$.id'))` |
| `JSON()` | Cast text → json | `JSON('{"a":1}')` |
| `JSON_SCALAR()` | Scalar → JSON | `JSON_SCALAR(42)` |
| `JSON_SERIALIZE()` | JSON → text | `JSON_SERIALIZE(jsonb_col)` |
| `JSON_EXISTS()` | Path exists? boolean | `JSON_EXISTS(data, '$.key')` |
| `JSON_VALUE()` | Extract scalar as SQL type | `JSON_VALUE(data, '$.key' RETURNING int)` |
| `JSON_QUERY()` | Extract JSON fragment | `JSON_QUERY(data, '$.arr')` |

jsonpath type methods: `.bigint()`, `.boolean()`, `.date()`, `.decimal()`, `.integer()`, `.number()`, `.string()`, `.time()`, `.time_tz()`, `.timestamp()`, `.timestamp_tz()`

### MERGE Enhancements

- `WHEN NOT MATCHED BY SOURCE THEN DELETE/UPDATE` — act on unmatched target rows
- `RETURNING merge_action(), *` — returns 'INSERT'/'UPDATE'/'DELETE' per row
- Works on updatable views

### New SQL Syntax

| Feature | Syntax |
|---------|--------|
| COPY error skip | `COPY t FROM file WITH (ON_ERROR ignore)` |
| Change generated expr | `ALTER TABLE t ALTER COLUMN c SET EXPRESSION AS (expr)` |
| Random in range | `random(1, 100)` — works for int, bigint, numeric |
| Interval infinity | `'infinity'::interval`, `'-infinity'::interval` |
| Session timezone | `timestamp_col AT LOCAL` |
| Optimizer memory | `EXPLAIN (MEMORY)` |
| Serialization cost | `EXPLAIN (SERIALIZE)` |

### New Functions

`to_bin(int)`, `to_oct(int)`, `uuid_extract_version(uuid)`, `uuid_extract_timestamp(uuid)`

### DDL Changes

- Identity columns on partitioned tables (previously unsupported)
- Exclusion constraints on partitioned tables (partition key must use equality)
- `MAINTAIN` privilege for VACUUM/ANALYZE/REINDEX/REFRESH/CLUSTER/LOCK
- `transaction_timeout` GUC — limits total transaction duration

For detailed examples and code samples, consult **`references/postgresql-17.md`**.

## PostgreSQL 18 (Sep 2025)

### Virtual Generated Columns (Major)

Generated columns are now **virtual by default** (computed at read time, no disk storage). Use `STORED` for write-time storage.

```sql
CREATE TABLE t (
  a int,
  b int,
  total int GENERATED ALWAYS AS (a + b)
);

-- virtual (PG18 default)
CREATE TABLE t (
  a int,
  b int,
  total int GENERATED ALWAYS AS (a + b) STORED
);

-- stored (PG16-17 behavior)
```

### OLD/NEW in RETURNING (Major)

```sql
UPDATE t SET val = val + 1 RETURNING old.val AS before, new.val AS after;
DELETE FROM t WHERE id = 1 RETURNING old.*;
MERGE INTO t USING s ON t.id = s.id ... RETURNING merge_action(), old.*, new.*;
```

### Temporal Constraints (WITHOUT OVERLAPS)
| Feature | Syntax |
|---------|--------|
| Temporal PK | `PRIMARY KEY (id, range_col WITHOUT OVERLAPS)` |
| Temporal UNIQUE | `UNIQUE (id, range_col WITHOUT OVERLAPS)` |
| Temporal FK | `FOREIGN KEY (id, PERIOD range_col) REFERENCES parent (id, PERIOD range_col)` |

Requires `btree_gist` extension.

### NOT ENFORCED Constraints

```sql
ALTER TABLE t
ADD CHECK (val > 0) NOT ENFORCED;

ALTER TABLE t
ADD FOREIGN KEY (x) REFERENCES r NOT ENFORCED;
```

### New Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `uuidv7()` | Timestamp-ordered UUID | `SELECT uuidv7()` |
| `casefold(text)` | Unicode case folding | `casefold('Straße') = casefold('STRASSE')` |
| `array_sort(anyarray)` | Sort array | `array_sort(ARRAY[3,1,2])` → `{1,2,3}` |
| `array_reverse(anyarray)` | Reverse array | `array_reverse(ARRAY[1,2,3])` → `{3,2,1}` |
| `crc32(bytea)` | CRC32 checksum | `crc32('hello'::bytea)` |
| `crc32c(bytea)` | CRC32C checksum | `crc32c('hello'::bytea)` |

### Data Type Changes

- **jsonb null casting**: `('null'::jsonb)::int` → `NULL` (was error pre-18)
- **Integer ↔ bytea casting**: `255::int2::bytea` → `\x00ff`, `'\x00ff'::bytea::int2` → `255`
- `json{b}_strip_nulls(json, strip_in_arrays)` — optional array null stripping

### New SQL Syntax

| Feature | Syntax |
|---------|--------|
| COPY reject limit | `COPY t FROM file WITH (ON_ERROR ignore, REJECT_LIMIT 100)` |
| VACUUM only parent | `VACUUM (ONLY) partitioned_table` |
| ANALYZE only parent | `ANALYZE (ONLY) partitioned_table` |

### Breaking Changes

- `EXPLAIN ANALYZE` now auto-includes `BUFFERS` output
- `initdb` enables data checksums by default (`--no-data-checksums` to disable)
- `COPY FROM` CSV no longer treats `\.` as EOF marker
- Generated columns default to virtual (not stored)
- NOT NULL constraints now in `pg_constraint`, can have names

For detailed examples and code samples, consult **`references/postgresql-18.md`**.

## Reference Files

For extended documentation with full code examples:
- **`references/postgresql-17.md`** — JSON_TABLE, SQL/JSON functions, MERGE, COPY ON_ERROR, and more with detailed usage examples
- **`references/postgresql-18.md`** — Virtual generated columns, OLD/NEW in RETURNING, temporal constraints, NOT ENFORCED constraints, and more with detailed usage examples

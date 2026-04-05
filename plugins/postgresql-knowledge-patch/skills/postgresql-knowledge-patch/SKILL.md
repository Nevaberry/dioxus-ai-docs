---
name: postgresql-knowledge-patch
description: "PostgreSQL 17–18 features since training cutoff — JSON_TABLE, SQL/JSON functions, uuidv7, virtual generated columns, temporal constraints (WITHOUT OVERLAPS), OLD/NEW in RETURNING, NOT ENFORCED constraints, MERGE enhancements, array_sort/array_reverse, casefold. Load before working with PostgreSQL 17+."
license: MIT
metadata:
  author: Nevaberry
  version: "18.0"
---

# PostgreSQL Knowledge Patch

Covers PostgreSQL 17.0–18.0 (2024-09-26 through 2025-09-25). Claude Opus 4.6 knows PostgreSQL through **16**. It is **unaware** of the 17+ features and 18 breaking changes below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| JSON & jsonpath | [references/json-and-jsonpath.md](references/json-and-jsonpath.md) | `JSON_TABLE`, `JSON_EXISTS`/`JSON_VALUE`/`JSON_QUERY`, `JSON_SCALAR`/`JSON_SERIALIZE`, jsonpath type methods, `jsonb_strip_nulls` array support, jsonb null→SQL NULL cast |
| DML & query features | [references/dml-and-queries.md](references/dml-and-queries.md) | MERGE `NOT MATCHED BY SOURCE` + `RETURNING`, `OLD`/`NEW` in RETURNING, COPY `ON_ERROR`/`REJECT_LIMIT`, EXPLAIN `MEMORY`/`SERIALIZE` |
| Constraints & DDL | [references/constraints-and-ddl.md](references/constraints-and-ddl.md) | Temporal `WITHOUT OVERLAPS`/`PERIOD`, `NOT ENFORCED` constraints, virtual generated columns (default in 18), `ALTER TABLE SET EXPRESSION`, partitioned table identity/exclusion |
| Functions & types | [references/functions-and-types.md](references/functions-and-types.md) | `uuidv7()`/`uuidv4()`, `array_sort`/`array_reverse`, `casefold()`, `crc32()`/`crc32c()`, `random(min,max)`, interval infinity, integer↔bytea cast, `EXTRACT(WEEK ...)` |

---

## Quick Reference — New Functions & Syntax

### PostgreSQL 17 (2024-09-26)

| Feature | Example |
|---|---|
| `JSON_TABLE(json, path COLUMNS(...))` | Convert JSON to relational rows |
| `JSON_EXISTS(json, path)` | Boolean: does path match? |
| `JSON_VALUE(json, path)` | Extract scalar as text |
| `JSON_QUERY(json, path)` | Extract JSON fragment |
| `JSON(text)` / `JSON_SCALAR(val)` | Validate JSON / wrap scalar |
| `JSON_SERIALIZE(json RETURNING text)` | JSON to text |
| `MERGE ... WHEN NOT MATCHED BY SOURCE` | Handle unmatched target rows |
| `merge_action()` in RETURNING | Returns `'INSERT'`/`'UPDATE'`/`'DELETE'` |
| `COPY ... ON_ERROR ignore` | Skip bad rows instead of aborting |
| `ALTER TABLE ... SET EXPRESSION AS (...)` | Change generated column expression |
| `random(min, max)` | Random in range (int/bigint/numeric) |
| `'infinity'::interval` | Interval infinity support |
| `EXPLAIN (MEMORY)` / `EXPLAIN (SERIALIZE)` | New EXPLAIN options |
| jsonpath `.integer()`, `.boolean()`, etc. | Type conversion in path expressions |

### PostgreSQL 18 (2025-09-25)

| Feature | Example |
|---|---|
| `uuidv7()` | Time-sortable UUID v7 |
| `uuidv4()` | Alias for `gen_random_uuid()` |
| Virtual generated columns (default) | `GENERATED ALWAYS AS (expr)` — no longer stored |
| `OLD`/`NEW` in RETURNING | `RETURNING old.price, new.price` |
| `WITHOUT OVERLAPS` in PK/UNIQUE | Temporal non-overlapping ranges |
| `PERIOD` in foreign keys | Temporal foreign key references |
| `NOT ENFORCED` constraints | Metadata-only CHECK/FK constraints |
| `array_sort(arr [, 'desc'])` | Sort arrays |
| `array_reverse(arr)` | Reverse arrays |
| `casefold(text)` | Unicode case folding (`'Straße'` → `'strasse'`) |
| `crc32(bytea)` / `crc32c(bytea)` | CRC checksums |
| `COPY ... REJECT_LIMIT n` | Max bad rows before abort |
| `VACUUM ONLY` / `ANALYZE ONLY` | Skip partition children |
| jsonb `null` → SQL `NULL` cast | `('null'::jsonb)::text` returns NULL |

---

## PostgreSQL 18 Breaking Changes

| Change | Migration |
|---|---|
| Generated columns default to **VIRTUAL** | Add `STORED` explicitly if you need stored columns |
| `initdb` defaults to checksums | Use `--no-data-checksums` to disable |
| MD5 passwords deprecated | Warnings on `CREATE/ALTER ROLE`; suppress with `md5_password_warnings = off` |
| `COPY FROM CSV`: `\.` not end-of-file | No longer treated as EOF marker |
| `EXPLAIN ANALYZE` includes `BUFFERS` | Automatic — no action needed |
| `VACUUM`/`ANALYZE` process partition children | Use `ONLY` keyword for old behavior |

---

## Essential Examples

### JSON_TABLE (17)

```sql
SELECT
  *
FROM
  JSON_TABLE (
    '{"items": [{"name": "A", "qty": 5}, {"name": "B", "qty": 3}]}'::jsonb,
    '$.items[*]' COLUMNS (name text PATH '$.name', qty int PATH '$.qty')
  ) AS jt;
```

### SQL/JSON Query Functions (17)

```sql
SELECT JSON_EXISTS('{"a": 1}', '$.a');           -- true
SELECT JSON_VALUE('{"a": 1}', '$.a');            -- '1' (text)
SELECT JSON_QUERY('{"a": [1,2]}', '$.a');        -- '[1,2]' (json)
SELECT JSON_SCALAR(42);                          -- JSON scalar
SELECT JSON_SERIALIZE('{"a":1}'::jsonb RETURNING text);
```

See [references/json-and-jsonpath.md](references/json-and-jsonpath.md) for jsonpath type conversion methods and jsonb null handling.

### MERGE with RETURNING and merge_action() (17)

```sql
MERGE INTO target t USING source s ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET val = s.val
  WHEN NOT MATCHED BY TARGET THEN INSERT (id, val) VALUES (s.id, s.val)
  WHEN NOT MATCHED BY SOURCE THEN DELETE
  RETURNING merge_action(), t.*;
-- merge_action() returns 'INSERT', 'UPDATE', or 'DELETE'
```

### OLD/NEW in RETURNING (18)

```sql
UPDATE products SET price = price * 1.1
  RETURNING old.price AS old_price, new.price AS new_price;

DELETE FROM logs WHERE created_at < now() - interval '90 days'
  RETURNING old.*;
```

### Temporal Constraints — WITHOUT OVERLAPS (18)

```sql
CREATE TABLE room_bookings (
  room_id int,
  booked_during tstzrange,
  PRIMARY KEY (room_id, booked_during WITHOUT OVERLAPS)
);

-- Temporal foreign key using PERIOD
CREATE TABLE booking_details (
  detail_id int PRIMARY KEY,
  room_id int,
  detail_during tstzrange,
  FOREIGN KEY (room_id, PERIOD detail_during)
    REFERENCES room_bookings (room_id, PERIOD booked_during)
);
```

See [references/constraints-and-ddl.md](references/constraints-and-ddl.md) for unique constraints with `WITHOUT OVERLAPS` and `NOT ENFORCED` constraints.

### NOT ENFORCED Constraints (18)

```sql
ALTER TABLE orders ADD CONSTRAINT positive_qty CHECK (qty > 0) NOT ENFORCED;
ALTER TABLE orders ADD FOREIGN KEY (customer_id) REFERENCES customers NOT ENFORCED;
```

### Virtual Generated Columns — Default in 18

```sql
-- Virtual (default in 18 — computed on read, not stored)
CREATE TABLE orders (
  qty int, price numeric,
  total numeric GENERATED ALWAYS AS (qty * price)
);
-- Stored (old default — must be explicit now)
CREATE TABLE orders2 (
  qty int, price numeric,
  total numeric GENERATED ALWAYS AS (qty * price) STORED
);
```

### uuidv7 (18)

```sql
SELECT uuidv7();  -- time-sortable: '019271a4-5c00-7d3e-8f4a-2b1c3d4e5f60'
SELECT uuidv4();  -- alias for gen_random_uuid()
```

### New Array Functions (18)

```sql
SELECT array_sort(ARRAY[3,1,2]);          -- {1,2,3}
SELECT array_sort(ARRAY[3,1,2], 'desc');  -- {3,2,1}
SELECT array_reverse(ARRAY[1,2,3]);       -- {3,2,1}
```

### COPY Error Handling (17+18)

```sql
-- 17: skip bad rows
COPY my_table FROM '/data.csv' WITH (FORMAT csv, ON_ERROR ignore);
-- 18: limit how many bad rows before abort
COPY my_table FROM '/data.csv' WITH (FORMAT csv, ON_ERROR ignore, REJECT_LIMIT 100);
```

See [references/functions-and-types.md](references/functions-and-types.md) for `casefold`, `crc32`, `random(min,max)`, interval infinity, and bytea casting.

## Reference Files

| File | Contents |
|---|---|
| [json-and-jsonpath.md](references/json-and-jsonpath.md) | JSON_TABLE, SQL/JSON standard functions, jsonpath type methods, jsonb null handling |
| [dml-and-queries.md](references/dml-and-queries.md) | MERGE enhancements, OLD/NEW RETURNING, COPY options, EXPLAIN options |
| [constraints-and-ddl.md](references/constraints-and-ddl.md) | Temporal constraints, NOT ENFORCED, virtual generated columns, partitioned tables |
| [functions-and-types.md](references/functions-and-types.md) | uuidv7, array functions, casefold, crc32, random, interval infinity, bytea casting |

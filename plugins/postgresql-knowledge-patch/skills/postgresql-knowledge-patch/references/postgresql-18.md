# PostgreSQL 18 (Sep 2025) — Detailed Reference

## Virtual Generated Columns

Generated columns are now **virtual by default** (computed at read time, not stored). Use `STORED` keyword for the old behavior.

```sql
-- Virtual (default in PG18) — no disk storage, computed on read
CREATE TABLE orders (
  price numeric,
  qty int,
  total numeric GENERATED ALWAYS AS (price * qty)
);

-- Stored (explicit) — written to disk on INSERT/UPDATE
CREATE TABLE orders (
  price numeric,
  qty int,
  total numeric GENERATED ALWAYS AS (price * qty) STORED
);
```

## OLD/NEW in RETURNING Clauses

DML statements can now reference pre- and post-modification row values in RETURNING.

```sql
-- UPDATE: see before and after values
UPDATE employees
SET
  salary = salary * 1.1
RETURNING
  old.salary AS before,
  new.salary AS
after;

-- DELETE: return deleted row
DELETE FROM items
WHERE
  expired
RETURNING
  old.*;

-- INSERT: old.* is NULL for inserts
INSERT INTO
  t (id, val)
VALUES
  (1, 'x')
RETURNING
  new.*;

-- MERGE: both old and new available
MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN
UPDATE
SET
  val = s.val WHEN NOT MATCHED THEN INSERT (id, val)
VALUES
  (s.id, s.val)
RETURNING
  merge_action (),
  old.*,
  new.*;
```

## Temporal Constraints (WITHOUT OVERLAPS)

Range-based primary keys, unique constraints, and foreign keys for temporal data.

```sql
-- Primary key: no two rows with same room_id can have overlapping time ranges
CREATE TABLE bookings (
  room_id int,
  booked_during tsrange,
  PRIMARY KEY (room_id, booked_during WITHOUT OVERLAPS)
);

-- Unique constraint with range
CREATE TABLE subscriptions (
  user_id int,
  plan text,
valid_during daterange,
UNIQUE (user_id, valid_during WITHOUT OVERLAPS)
);

-- Temporal foreign key using PERIOD
CREATE TABLE booking_details (
  booking_id int,
detail_range tsrange,
FOREIGN KEY (booking_id, PERIOD detail_range)
    REFERENCES bookings (room_id, PERIOD booked_during)
);
```

Requires btree_gist extension for the range column in the constraint.

## NOT ENFORCED Constraints

Define constraints for documentation/query planning without runtime enforcement.

```sql
ALTER TABLE t ADD CONSTRAINT chk CHECK (val > 0) NOT ENFORCED;
ALTER TABLE t ADD FOREIGN KEY (dept_id) REFERENCES depts NOT ENFORCED;
```

## uuidv7() and uuidv4()

```sql
SELECT uuidv7();  -- timestamp-ordered UUID (sortable, k-sortable)
SELECT uuidv4();  -- alias for gen_random_uuid() (random UUID v4)
```

## casefold()

Unicode-aware case folding for case-insensitive comparison. Handles characters where `lower()` is insufficient (e.g., German eszett, Greek sigma).

```sql
SELECT casefold('Straße') = casefold('STRASSE');  -- true
```
## array_sort ()
and array_reverse ()
```sql
SELECT array_sort(ARRAY[3, 1, 2]);       -- {1,2,3}
SELECT array_reverse(ARRAY[1, 2, 3]);    -- {3,2,1}
```

## jsonb Null Casting

JSON null values now cast to SQL NULL instead of raising an error.

```sql
SELECT ('null'::jsonb)::integer;   -- NULL (was error before PG18)
SELECT ('null'::jsonb)::text;      -- NULL
```

## Integer ↔ Bytea Casting

```sql
SELECT 255::int2::bytea;     -- \x00ff  (two's complement)
SELECT 65535::int4::bytea;   -- \x0000ffff
SELECT '\x00ff'::bytea::int2; -- 255
```

## COPY REJECT_LIMIT

Limit how many error rows COPY FROM can skip:

```sql
COPY t FROM '/path/data.csv' WITH (
  FORMAT csv, ON_ERROR ignore, REJECT_LIMIT 100
);
```

## EXPLAIN ANALYZE Auto-BUFFERS

`EXPLAIN ANALYZE` now automatically includes buffer usage statistics (previously required explicit `BUFFERS` option).

## Other Notable Additions

- `crc32(bytea)`, `crc32c(bytea)` — CRC checksum functions
- `gamma(float8)`, `lgamma(float8)` — gamma and log-gamma math functions
- `reverse(bytea)` — reverse bytes
- `json{b}_strip_nulls(json, strip_in_arrays bool)` — optionally strip nulls from arrays too
- `PG_UNICODE_FAST` builtin collation — code-point-order sort with case mapping
- `VACUUM (ONLY)` / `ANALYZE (ONLY)` — process partitioned table without children
- `NOT NULL` constraints now stored in `pg_constraint` and can have names
- `ALTER TABLE ... ALTER CONSTRAINT ... NOT VALID` — mark constraints not validated
- Data checksums enabled by default in `initdb` (use `--no-data-checksums` to disable)
- `COPY FROM` CSV no longer treats `\.` as EOF marker
- `idle_replication_slot_timeout` — auto-invalidate inactive replication slots

# SQL, Types, and Schema Design

Use this reference for keys, constraints, generated values, DML, privileges,
collations, type behavior, and PL/pgSQL syntax. UUID guidance is attributed to
`18-uuid-guide`; other versioned changes come from `17.0` and `18.0`.

## Generate and inspect UUIDv7 values

PostgreSQL 18 `uuidv7([shift interval])` creates time-ordered UUIDs from a
millisecond Unix timestamp, sub-millisecond timestamp data, and randomness.
The optional interval shifts the embedded timestamp:

```sql
SELECT uuidv7(),
       uuidv7(interval '-1 hour');
```

`uuid_extract_timestamp(uuid)` returns `timestamp with time zone` for version
1 or 7 UUIDs and `NULL` for other versions. The recovered timestamp depends on
the generating implementation and need not exactly equal generation time.
`uuid_extract_version(uuid)` returns a `smallint` version for RFC 9562 variants
and `NULL` for other variants.

```sql
WITH generated AS (SELECT uuidv7() AS id)
SELECT uuid_extract_timestamp(id),
       uuid_extract_version(id)
FROM generated;
```

## Design partitioned tables and indexes

PostgreSQL 17 partitioned tables can have identity columns and table access
methods. Their exclusion constraints are allowed when every partition-key
column uses equality; other columns can use the constraint's exclusion
operators.

PostgreSQL 18 unique non-B-tree indexes can support partition keys and
materialized views when the access method provides equality semantics.

## Choose generated-column storage explicitly

PostgreSQL 18 generated columns are virtual by default and compute on read.
Add `STORED` for write-time materialization:

```sql
CREATE TABLE line_item (
  quantity integer,
  unit_price numeric,
  total numeric GENERATED ALWAYS AS (quantity * unit_price) STORED
);
```

For a stored generated column, PostgreSQL 17 allows replacing its expression
with `SET EXPRESSION`:

```sql
ALTER TABLE order_lines
  ALTER COLUMN total SET EXPRESSION AS (quantity * unit_price);
```

`ALTER COLUMN ... SET STATISTICS DEFAULT` replaces the older `-1` spelling,
and `ALTER TABLE ... SET ACCESS METHOD DEFAULT` selects the configured default
table access method.

## Return old and new row images

PostgreSQL 18 `INSERT`, `UPDATE`, `DELETE`, and `MERGE` can reference the
special `old` and `new` aliases in `RETURNING`. Rename the aliases when they
conflict with relation names:

```sql
UPDATE products
SET price = price * 1.05
RETURNING id, old.price AS previous_price, new.price AS current_price;
```

PostgreSQL 17 `MERGE` can target updatable views, use
`WHEN NOT MATCHED BY SOURCE`, and return rows. `merge_action()` identifies
whether each result came from an insert, update, or delete:

```sql
MERGE INTO inventory AS i
USING current_stock AS s ON i.sku = s.sku
WHEN MATCHED THEN UPDATE SET quantity = s.quantity
WHEN NOT MATCHED THEN INSERT (sku, quantity) VALUES (s.sku, s.quantity)
WHEN NOT MATCHED BY SOURCE THEN DELETE
RETURNING merge_action(), i.*;
```

## Enforce temporal relationships

PostgreSQL 18 `WITHOUT OVERLAPS` on the last column of a primary or unique key
rejects overlapping ranges. `PERIOD` on the last foreign-key column requires
referenced ranges to cover the referencing range:

```sql
CREATE TABLE room_prices (
  room_id bigint,
  valid_at daterange,
  price numeric,
  UNIQUE (room_id, valid_at WITHOUT OVERLAPS)
);

CREATE TABLE bookings (
  room_id bigint,
  stay daterange,
  FOREIGN KEY (room_id, PERIOD stay)
    REFERENCES room_prices (room_id, PERIOD valid_at)
);
```

## Control constraint enforcement and inheritance

PostgreSQL 18 `CHECK` and foreign-key constraints can be `NOT ENFORCED`; inspect
`pg_constraint.conenforced`. `NOT NULL` constraints are represented in
`pg_constraint`, can be named or marked `NOT VALID`, and support
`ALTER CONSTRAINT ... [NO] INHERIT`. Partitioned tables also allow `NOT VALID`
foreign keys and parent-only constraint drops.

## Delegate access without ownership

PostgreSQL 18 adds `pg_get_acl()` for ACL details and
`has_largeobject_privilege()` for large-object permissions.
`ALTER DEFAULT PRIVILEGES` can establish large-object defaults. Membership in
`pg_signal_autovacuum_worker` permits signaling autovacuum workers.

For maintenance delegation, PostgreSQL 17 adds table-level `MAINTAIN` and the
predefined `pg_maintain` role.

## Define login event triggers

PostgreSQL 17 event triggers can fire on `login`, and `REINDEX` participates in
event-trigger command reporting:

```sql
CREATE EVENT TRIGGER audit_login
ON login
EXECUTE FUNCTION app.record_login();
```

## Work with interval and enum values

PostgreSQL 17 `interval` accepts positive and negative infinity. An enum value
added in a transaction can be used immediately when the enum type itself was
created earlier in that same transaction; this remains disallowed for a
pre-existing enum type.

## Use current time-zone syntax

PostgreSQL 17 `to_timestamp()` format strings accept `TZ` for abbreviations or
numeric offsets and `OF` for numeric offsets. `AT LOCAL` adds or removes
time-zone information using the session zone:

```sql
SELECT timestamp '2024-09-26 12:00' AT LOCAL;
```

## Use expanded type references and procedural syntax

PostgreSQL 17 `%TYPE` and `%ROWTYPE` references can be followed by array
notation when the base type is not already an array. `%TYPE` can reference a
column declared with a composite type:

```plpgsql
DO $$
DECLARE
  pending app.orders%ROWTYPE[];
  destination app.shipments.address%TYPE;
BEGIN
  NULL;
END $$;
```

PostgreSQL 18 PL/pgSQL cursor arguments accept `=>` as well as `:=`, and the
regular-expression function family accepts named arguments.

## Apply collation and foreign-table capabilities

PostgreSQL 18 `CREATE FOREIGN TABLE ... LIKE` derives a foreign table from a
local one. `LIKE` and text-position functions accept nondeterministic
collations. The built-in `PG_UNICODE_FAST` collation performs case mapping with
code-point-order sorting.

## Use Unicode, aggregate, formatting, and binary additions

PostgreSQL 18 `casefold()` performs Unicode-aware caseless transformation,
including mappings that change length. Unicode case conversion supports
conditional, title-case, and one-to-many mappings. `MIN()` and `MAX()` can
aggregate arrays and composite values.

`to_number()` accepts the `RN` Roman-numeral pattern and `EXTRACT()` accepts
`WEEK`:

```sql
SELECT to_number('XIV', 'RN');
```

Integer-to-`bytea` casts use two's-complement representation, and reverse casts
from `bytea` to integer types are supported.

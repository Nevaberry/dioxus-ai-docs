# SQL, Types, and Schema Design

Batch attribution: `18-uuid-guide`, `17.0`, `18.0`.

## Contents

- [UUIDv7](#generate-and-inspect-uuidv7-values)
- [Generated columns](#choose-virtual-or-stored-generated-columns)
- [RETURNING and MERGE](#return-old-and-new-row-images)
- [Temporal constraints](#model-temporal-uniqueness-and-referential-coverage)
- [Partitions, indexes, and constraints](#design-partitions-indexes-and-constraints)
- [Privileges](#delegate-maintenance-and-inspect-privileges)
- [Collations and foreign tables](#use-portable-and-nondeterministic-collations)
- [Types and conversions](#work-with-expanded-type-and-conversion-behavior)
- [PL/pgSQL](#use-richer-procedural-type-references-and-calls)
- [Event triggers](#audit-logins-with-event-triggers)

## Generate and inspect UUIDv7 values

`uuidv7([shift interval])` generates time-ordered UUIDs from a millisecond Unix
timestamp, sub-millisecond timestamp data, and randomness. The optional interval
shifts the timestamp embedded in the result.

```sql
SELECT uuidv7(),
       uuidv7(interval '-1 hour');
```

`uuid_extract_timestamp(uuid)` returns `timestamp with time zone` for UUID
versions 1 and 7, and `NULL` for other versions. Treat the extracted value as
implementation-dependent metadata; it need not exactly equal the creation
time. `uuid_extract_version(uuid)` returns a `smallint` version for RFC 9562
variants and `NULL` for other variants.

```sql
WITH generated AS (SELECT uuidv7() AS id)
SELECT uuid_extract_timestamp(id),
       uuid_extract_version(id)
FROM generated;
```

## Choose virtual or stored generated columns

Generated columns are virtual by default and compute on read. Add `STORED` for
write-time materialization.

```sql
CREATE TABLE line_item (
  quantity integer,
  unit_price numeric,
  total numeric GENERATED ALWAYS AS (quantity * unit_price)
);

CREATE TABLE stored_line_item (
  quantity integer,
  unit_price numeric,
  total numeric GENERATED ALWAYS AS (quantity * unit_price) STORED
);
```

Replace a stored generated expression without rebuilding the column definition:

```sql
ALTER TABLE order_lines
  ALTER COLUMN total SET EXPRESSION AS (quantity * unit_price);
```

Use `SET STATISTICS DEFAULT` instead of the older `-1` spelling. Likewise,
`ALTER TABLE ... SET ACCESS METHOD DEFAULT` selects the configured default
table access method.

## Return old and new row images

`INSERT`, `UPDATE`, `DELETE`, and `MERGE` can explicitly refer to `old` and
`new` in `RETURNING`. Rename these special aliases when they conflict with
table or column names.

```sql
UPDATE products
SET price = price * 1.05
RETURNING id, old.price AS previous_price, new.price AS current_price;
```

`MERGE` can target an updatable view, act on `WHEN NOT MATCHED BY SOURCE`, and
return affected rows. `merge_action()` reports `INSERT`, `UPDATE`, or `DELETE`
for each output row.

```sql
MERGE INTO inventory AS i
USING current_stock AS s ON i.sku = s.sku
WHEN MATCHED THEN UPDATE SET quantity = s.quantity
WHEN NOT MATCHED THEN
  INSERT (sku, quantity) VALUES (s.sku, s.quantity)
WHEN NOT MATCHED BY SOURCE THEN DELETE
RETURNING merge_action(), i.*;
```

## Model temporal uniqueness and referential coverage

Put `WITHOUT OVERLAPS` on the last column of a primary or unique key to require
non-overlapping ranges. Put `PERIOD` on the last foreign-key column to require
the referenced ranges collectively to cover the referencing range.

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

## Design partitions, indexes, and constraints

Partitioned tables support identity columns and table access methods. They can
also have exclusion constraints when every partition-key column is compared
for equality; non-key columns may use the constraint's other exclusion
operators.

Unique non-B-tree indexes can support partition keys and materialized views
when the index access method provides equality semantics.

`CHECK` and foreign-key constraints may be declared `NOT ENFORCED`. Inspect
that state through `pg_constraint.conenforced`.

`NOT NULL` constraints are represented in `pg_constraint`. They can be named,
marked `NOT VALID`, and changed with `ALTER CONSTRAINT ... [NO] INHERIT`.
Partitioned tables also support `NOT VALID` foreign keys and parent-only
constraint drops.

## Delegate maintenance and inspect privileges

`MAINTAIN` is a per-table privilege for `VACUUM`, `ANALYZE`, `REINDEX`,
`REFRESH MATERIALIZED VIEW`, `CLUSTER`, and `LOCK TABLE`. The predefined
`pg_maintain` role grants maintenance capability without conferring ownership
or general superuser access.

```sql
GRANT MAINTAIN ON TABLE app.orders TO maintenance_bot;
GRANT pg_maintain TO operations_role;
```

Use `pg_get_acl()` to retrieve ACL details and
`has_largeobject_privilege()` to test large-object rights.
`ALTER DEFAULT PRIVILEGES` can establish defaults for large objects.
Membership in `pg_signal_autovacuum_worker` permits signaling autovacuum
workers.

## Use portable and nondeterministic collations

The platform-independent built-in collation provider supplies `C` and
`C.UTF-8`. `PG_UNICODE_FAST` provides Unicode case mapping with code-point-order
sorting.

`LIKE` and text-position functions accept nondeterministic collations.
`CREATE FOREIGN TABLE ... LIKE` can derive a foreign table's columns from a
local table.

## Work with expanded type and conversion behavior

`interval` accepts positive and negative infinity. A newly added enum value can
be used immediately when its enum type was itself created earlier in the same
transaction; immediate use remains disallowed for a pre-existing enum type.

`to_timestamp()` format strings accept `TZ` for abbreviations or numeric offsets
and `OF` for numeric offsets. `AT LOCAL` uses the session time zone while adding
or removing time-zone information.

```sql
SELECT timestamp '2024-09-26 12:00' AT LOCAL;
```

Integer-to-`bytea` casts use two's-complement representation, and reverse casts
are supported.

`casefold()` performs Unicode-aware caseless transformation, including mappings
that change string length. Unicode case conversion supports conditional,
title-case, and one-to-many mappings. `MIN()` and `MAX()` can aggregate arrays
and composite values.

`to_number()` accepts the `RN` Roman-numeral pattern, and `EXTRACT()` accepts
`WEEK`.

```sql
SELECT to_number('XIV', 'RN');
```

## Use richer procedural type references and calls

In PL/pgSQL, `%TYPE` and `%ROWTYPE` may be followed by array notation when the
base reference is not already an array. `%TYPE` can reference a column whose
declared type is composite.

```plpgsql
DO $$
DECLARE
  pending app.orders%ROWTYPE[];
  destination app.shipments.address%TYPE;
BEGIN
  NULL;
END $$;
```

Cursor arguments accept `=>` as well as `:=`. The regular-expression function
family accepts named arguments.

## Audit logins with event triggers

Event triggers can fire on `login`, and event-trigger command reporting covers
`REINDEX`.

```sql
CREATE EVENT TRIGGER audit_login
ON login
EXECUTE FUNCTION app.record_login();
```

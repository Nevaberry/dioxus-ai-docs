# SQL, Types, and Schema Design

## Define richer partitioned tables (17.0)

Partitioned tables may have identity columns and table access methods. They
may also have exclusion constraints when every partition-key column uses
equality, while other columns use the constraint's exclusion operators.

## Change generated expressions and reset DDL choices (17.0)

Replace a stored generated column's expression with `SET EXPRESSION`.
`SET STATISTICS DEFAULT` replaces the older `-1` spelling, and
`ALTER TABLE ... SET ACCESS METHOD DEFAULT` selects the configured default
table access method.

```sql
ALTER TABLE order_lines
  ALTER COLUMN total SET EXPRESSION AS (quantity * unit_price);
ALTER TABLE order_lines
  ALTER COLUMN sku SET STATISTICS DEFAULT;
```

## Audit logins with event triggers (17.0)

Event triggers can fire for the `login` event. `REINDEX` is also included in
event-trigger command reporting.

```sql
CREATE EVENT TRIGGER audit_login
ON login
EXECUTE FUNCTION app.record_login();
```

## Use expanded MERGE semantics (17.0)

`MERGE` can target updatable views, use `WHEN NOT MATCHED BY SOURCE`, and
return rows. In `RETURNING`, `merge_action()` identifies whether an output row
was inserted, updated, or deleted.

```sql
MERGE INTO inventory AS i
USING current_stock AS s ON i.sku = s.sku
WHEN MATCHED THEN UPDATE SET quantity = s.quantity
WHEN NOT MATCHED THEN INSERT (sku, quantity) VALUES (s.sku, s.quantity)
WHEN NOT MATCHED BY SOURCE THEN DELETE
RETURNING merge_action(), i.*;
```

## Represent infinite intervals and add enum values transactionally (17.0)

`interval` accepts positive and negative infinity. A newly added enum value
may be used immediately when its enum type was created earlier in the same
transaction; immediate use remains disallowed for pre-existing enum types.

## Use the session zone without repeating it (17.0)

`to_timestamp()` format strings accept `TZ` for abbreviations or numeric
offsets and `OF` for numeric offsets. `AT LOCAL` uses the session time zone
when adding or removing time-zone information.

```sql
SELECT timestamp '2024-09-26 12:00' AT LOCAL;
```

## Declare arrays from anchored PL/pgSQL types (17.0)

Array notation may follow `%TYPE` or `%ROWTYPE` when the base is not already
an array. `%TYPE` may reference a column whose declared type is composite.

```plpgsql
DO $$
DECLARE
  pending app.orders%ROWTYPE[];
  destination app.shipments.address%TYPE;
BEGIN
  NULL;
END $$;
```

## Use portable built-in collations and configurable SLRUs (17.0)

The built-in collation provider supplies platform-independent `C` and
`C.UTF-8`. SLRU cache sizes are configurable with
`commit_timestamp_buffers`, `multixact_member_buffers`,
`multixact_offset_buffers`, `notify_buffers`, `serializable_buffers`,
`subtransaction_buffers`, and `transaction_buffers`. Commit-timestamp,
transaction, and subtransaction caches otherwise scale with `shared_buffers`.

## Generate and inspect UUIDv7 values (18-uuid-guide)

`uuidv7([shift interval])` creates time-ordered UUIDs from a millisecond Unix
timestamp, sub-millisecond timestamp data, and randomness. Its optional
interval shifts the embedded timestamp.

```sql
SELECT uuidv7(), uuidv7(interval '-1 hour');
```

`uuid_extract_timestamp(uuid)` returns `timestamp with time zone` for UUID
versions 1 and 7 and `NULL` for other versions. The decoded timestamp is
implementation-dependent and need not exactly match generation time.
`uuid_extract_version(uuid)` returns a `smallint` for RFC 9562 variants and
`NULL` for other variants.

```sql
WITH generated AS (SELECT uuidv7() AS id)
SELECT uuid_extract_timestamp(id), uuid_extract_version(id)
FROM generated;
```

## Use equality-capable non-B-tree indexes (18.0)

Unique non-B-tree indexes can support partition keys and materialized views
when their access method supplies equality semantics.

## Grant new object privileges (18.0)

`pg_get_acl()` retrieves ACL details, and `has_largeobject_privilege()` checks
large-object permissions. `ALTER DEFAULT PRIVILEGES` can define large-object
defaults. Membership in `pg_signal_autovacuum_worker` authorizes signaling
autovacuum workers.

## Choose virtual or stored generated columns (18.0)

Generated columns are virtual by default and compute on read. Add `STORED`
when write-time materialization is required.

```sql
CREATE TABLE line_item (
  quantity integer,
  unit_price numeric,
  virtual_total numeric
    GENERATED ALWAYS AS (quantity * unit_price),
  stored_total numeric
    GENERATED ALWAYS AS (quantity * unit_price) STORED
);
```

## Reference old and new row images in RETURNING (18.0)

`INSERT`, `UPDATE`, `DELETE`, and `MERGE` expose `old` and `new` in
`RETURNING`. Rename those aliases when they conflict with identifiers.

```sql
UPDATE products
SET price = price * 1.05
RETURNING id, old.price AS previous_price, new.price AS current_price;
```

## Derive foreign tables and use nondeterministic collations (18.0)

`CREATE FOREIGN TABLE ... LIKE` derives a foreign table from a local table.
`LIKE` and text-position functions accept nondeterministic collations. The
built-in `PG_UNICODE_FAST` collation combines Unicode case mapping with
code-point-order sorting.

## Enforce temporal keys (18.0)

Place `WITHOUT OVERLAPS` on the final column of a primary or unique key to
reject overlapping ranges. Place `PERIOD` on the final foreign-key and
referenced-key columns to require referenced ranges to cover the referencing
range.

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

## Control constraint enforcement and inheritance (18.0)

Declare `CHECK` and foreign-key constraints `NOT ENFORCED`; inspect the result
in `pg_constraint.conenforced`. `NOT NULL` constraints are represented in
`pg_constraint`, can be named or marked `NOT VALID`, and accept
`ALTER CONSTRAINT ... [NO] INHERIT`. Partitioned tables accept `NOT VALID`
foreign keys and parent-only constraint drops.

## Apply Unicode transformations and aggregate complex values (18.0)

`casefold()` performs Unicode-aware caseless transformation, including
mappings that change string length. Unicode case conversion supports
conditional, title-case, and one-to-many mappings. `MIN()` and `MAX()` can
aggregate arrays and composite values.

## Use new formatting and procedural syntax (18.0)

`to_number()` accepts the `RN` Roman-numeral pattern, and `EXTRACT()` has a
`WEEK` option. PL/pgSQL cursor arguments accept `=>` as well as `:=`. The
regular-expression function family accepts named arguments.

```sql
SELECT to_number('XIV', 'RN');
```

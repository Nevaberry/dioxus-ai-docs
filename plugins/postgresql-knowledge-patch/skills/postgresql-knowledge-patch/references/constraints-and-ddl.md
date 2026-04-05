# Constraints & DDL Features

## Temporal Constraints — WITHOUT OVERLAPS / PERIOD (18)

SQL:2011 temporal support. Enforce non-overlapping ranges in primary/unique keys and temporal foreign keys.

```sql
CREATE TABLE room_bookings (
  room_id int,
  booked_during tstzrange,
  PRIMARY KEY (room_id, booked_during WITHOUT OVERLAPS)
);

-- Unique constraint with temporal dimension
CREATE TABLE employee_assignments (
  emp_id int,
  dept_id int,
  valid_during daterange,
  UNIQUE (emp_id, valid_during WITHOUT OVERLAPS)
);

-- Temporal foreign key using PERIOD
CREATE TABLE booking_details (
  detail_id int PRIMARY KEY,
  room_id int,
  detail_during tstzrange,
  FOREIGN KEY (room_id, PERIOD detail_during) REFERENCES room_bookings (room_id, PERIOD booked_during)
);
```

## NOT ENFORCED Constraints (18)

CHECK and foreign key constraints can be declared `NOT ENFORCED` — metadata-only, not validated at runtime. Useful for query optimization hints or documenting intent.

```sql
ALTER TABLE orders ADD CONSTRAINT positive_qty CHECK (qty > 0) NOT ENFORCED;
ALTER TABLE orders ADD FOREIGN KEY (customer_id) REFERENCES customers NOT ENFORCED;
```

## Virtual Generated Columns — Now Default (18)

Generated columns are now **virtual by default** (computed on read, not stored). Use `STORED` for the old behavior.

```sql
CREATE TABLE orders (
  qty int, price numeric,
  total numeric GENERATED ALWAYS AS (qty * price)          -- virtual (default in 18)
);
CREATE TABLE orders2 (
  qty int, price numeric,
  total numeric GENERATED ALWAYS AS (qty * price) STORED   -- stored (old default)
);
```

## ALTER TABLE ... SET EXPRESSION (17)

Change a generated column's expression without dropping/re-adding:

```sql
ALTER TABLE t ALTER COLUMN total SET EXPRESSION AS (qty * price * 1.1);
```

## Partitioned Table Enhancements (17)

- **Identity columns** now allowed on partitioned tables
- **Exclusion constraints** now allowed (partition key columns must use equality)

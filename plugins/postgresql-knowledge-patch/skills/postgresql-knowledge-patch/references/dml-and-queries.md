# DML & Query Features

## MERGE Enhancements (17)

`WHEN NOT MATCHED BY SOURCE` clause and `RETURNING` with `merge_action()`:

```sql
MERGE INTO target t USING source s ON t.id = s.id WHEN MATCHED THEN
UPDATE
SET
  val = s.val WHEN NOT MATCHED BY TARGET THEN INSERT (id, val)
VALUES
  (s.id, s.val) WHEN NOT MATCHED BY SOURCE THEN DELETE
RETURNING
  merge_action (),
  t.*;

-- merge_action() returns 'INSERT', 'UPDATE', or 'DELETE'
```

## OLD/NEW in RETURNING Clauses (18)

`RETURNING` can now explicitly reference old and new row values via `old` and `new` aliases.

```sql
UPDATE products SET price = price * 1.1
  RETURNING old.price AS old_price, new.price AS new_price;

DELETE FROM logs WHERE created_at < now() - interval '90 days'
  RETURNING old.*;

-- Works with MERGE too
MERGE INTO target t USING source s ON t.id = s.id
  WHEN MATCHED THEN UPDATE SET val = s.val
  WHEN NOT MATCHED THEN INSERT VALUES (s.id, s.val)
  RETURNING merge_action(), old.val AS prev, new.val AS curr;
```

## COPY ON_ERROR Option (17)

```sql
COPY my_table FROM '/path/to/data.csv' WITH (FORMAT csv, ON_ERROR ignore);
-- Skips rows with errors instead of aborting. Default: ON_ERROR stop
-- Also: LOG_VERBOSITY option to report skipped rows
```

## COPY REJECT_LIMIT (18)

Control how many bad rows `COPY FROM` can skip (requires `ON_ERROR = 'ignore'`):

```sql
COPY my_table FROM '/data.csv' WITH (FORMAT csv, ON_ERROR ignore, REJECT_LIMIT 100);
```

## EXPLAIN New Options (17)

```sql
EXPLAIN (MEMORY) SELECT ...;     -- report optimizer memory usage
EXPLAIN (SERIALIZE) SELECT ...;  -- report serialization cost for network
```

**Note (18):** `EXPLAIN ANALYZE` now automatically includes `BUFFERS` output.

## VACUUM/ANALYZE ONLY Option (18)

Process only the partitioned table, not its children:

```sql
VACUUM ONLY partitioned_table;
ANALYZE ONLY partitioned_table;
```

**Note (18):** `VACUUM`/`ANALYZE` now processes partition children by default (reversed from prior behavior).

## Named Cursor Arguments with => (18)

PL/pgSQL now accepts `=>` (in addition to `:=`) for named cursor arguments:

```sql
OPEN my_cursor(param1 => 42, param2 => 'hello');
```

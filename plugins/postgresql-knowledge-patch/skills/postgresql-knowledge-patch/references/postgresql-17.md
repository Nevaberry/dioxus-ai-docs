# PostgreSQL 17 (Sep 2024) — Detailed Reference

## JSON_TABLE()

Converts JSON data to a table representation. Used in FROM clause.

```sql
SELECT
  *
FROM
  JSON_TABLE (
    '{"name": "Alice", "items": [{"id": 1, "qty": 5}, {"id": 2, "qty": 3}]}'::jsonb,
    '$.items[*]' COLUMNS (
      row_num FOR ORDINALITY,
      item_id int PATH '$.id',
      quantity int PATH '$.qty',
      has_id boolean EXISTS PATH '$.id'
    )
  ) AS jt;

-- NESTED paths for hierarchical data
SELECT
  *
FROM
  JSON_TABLE (
    '{"depts": [{"name": "Eng", "staff": [{"n": "A"}, {"n": "B"}]}]}'::jsonb,
    '$.depts[*]' COLUMNS (
      dept text PATH '$.name',
      NESTED PATH '$.staff[*]' COLUMNS (person text PATH '$.n')
    )
  ) AS jt;
```

Error handling: `DEFAULT ... ON ERROR`, `DEFAULT ... ON EMPTY`, `ERROR ON ERROR`.

## SQL/JSON Constructor Functions

```sql
SELECT
  JSON('{"a": 1}');

-- casts text to json type
SELECT
  JSON(
    '{"a": 1}'
    RETURNING
      jsonb
  );

-- with target type
SELECT
  JSON_SCALAR (42);

-- wraps scalar as JSON value
SELECT
  JSON_SERIALIZE ('{"a":1}'::jsonb);

-- JSON to text
SELECT
  JSON_SERIALIZE (
    '{"a":1}'::jsonb
    RETURNING
      bytea
  );

-- to bytea
```

## SQL/JSON Query Functions

```sql
-- JSON_EXISTS: returns boolean
SELECT JSON_EXISTS('{"a": 1}', '$.a');         -- true
SELECT JSON_EXISTS('{"a": 1}', '$.b');         -- false

-- JSON_VALUE: extracts scalar as SQL type
SELECT JSON_VALUE('{"a": 42}', '$.a');                    -- '42' (text)
SELECT JSON_VALUE('{"a": 42}', '$.a' RETURNING int);      -- 42
SELECT JSON_VALUE('{"a": null}', '$.a' DEFAULT 0 ON EMPTY); -- 0

-- JSON_QUERY: extracts JSON object/array (not scalars)
SELECT JSON_QUERY('{"a": [1,2]}', '$.a');                 -- [1,2]
SELECT JSON_QUERY('{"a": [1,2]}', '$.a' WITH WRAPPER);   -- [[1,2]]
```

Key difference: JSON_VALUE returns a scalar SQL value, JSON_QUERY returns a JSON fragment.

## jsonpath Type Conversion Methods

New methods on jsonpath expressions: `.bigint()`, `.boolean()`, `.date()`, `.decimal([p [, s]])`, `.integer()`, `.number()`, `.string()`, `.time()`, `.time_tz()`, `.timestamp()`, `.timestamp_tz()`.

```sql
SELECT jsonb_path_query('{"val": "42"}', '$.val.integer()');  -- 42
SELECT jsonb_path_query('{"d": "2024-01-15"}', '$.d.date()'); -- 2024-01-15
```

## MERGE Enhancements

`WHEN NOT MATCHED BY SOURCE` — act on target rows with no matching source row.
`RETURNING` clause with `merge_action()` function reporting which DML fired.

```sql
MERGE INTO target t USING source s ON t.id = s.id
WHEN MATCHED THEN UPDATE SET val = s.val
WHEN NOT MATCHED BY TARGET THEN INSERT (id, val) VALUES (s.id, s.val)
WHEN NOT MATCHED BY SOURCE THEN DELETE
RETURNING merge_action(), t.*;
-- merge_action() returns 'INSERT', 'UPDATE', or 'DELETE'
```

MERGE can now also modify updatable views.

## COPY ON_ERROR
Skip error rows instead of aborting:
```sql
COPY t FROM '/path/data.csv' WITH (FORMAT csv, ON_ERROR ignore);
-- Also: LOG_VERBOSITY to log skipped rows
COPY t FROM '/path/data.csv' WITH (FORMAT csv, ON_ERROR ignore, LOG_VERBOSITY verbose);
```

## ALTER TABLE ... SET EXPRESSION

Change a generated column's expression:

```sql
ALTER TABLE t ALTER COLUMN total SET EXPRESSION AS (price * quantity * 1.1);
```

## Partitioned Table Improvements

- **Identity columns** now supported on partitioned tables
- **Exclusion constraints** now supported (partition key columns must use equality)

## Other Notable Additions

- `random(min, max)` for `integer`, `bigint`, `numeric` — random in range
- `to_bin(int)`, `to_oct(int)` — integer to binary/octal string
- `uuid_extract_version(uuid)`, `uuid_extract_timestamp(uuid)` — extract UUID metadata
- `interval` now supports `'infinity'` / `'-infinity'` values
- `AT LOCAL` — convert timestamps using session timezone: `ts AT LOCAL`
- `transaction_timeout` GUC — limits total transaction duration
- `EXPLAIN (MEMORY)` — reports optimizer memory usage
- `EXPLAIN (SERIALIZE)` — reports cost of result serialization
- `MAINTAIN` privilege — grants VACUUM, ANALYZE, REINDEX, REFRESH MATERIALIZED VIEW, CLUSTER, LOCK TABLE
- `pg_stat_checkpointer` view (checkpoint stats separated from pg_stat_bgwriter)

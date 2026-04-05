# JSON & jsonpath Features

## JSON_TABLE() — Convert JSON to Table Rows (17)

New SQL/JSON standard function in `FROM` clause:

```sql
SELECT
  *
FROM
  JSON_TABLE (
    '{"employees": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}'::jsonb,
    '$.employees[*]' COLUMNS (name text PATH '$.name', age int PATH '$.age')
  ) AS jt;
```

## SQL/JSON Constructor and Query Functions (17)

New standard functions:

```sql
-- Constructors
SELECT JSON('{"a": 1}');              -- validate/cast to json
SELECT JSON_SCALAR(42);               -- wrap scalar as JSON
SELECT JSON_SERIALIZE('{"a":1}'::jsonb RETURNING text);  -- JSON to text

-- Query functions
SELECT JSON_EXISTS('{"a": 1}', '$.a');           -- returns boolean
SELECT JSON_VALUE('{"a": 1}', '$.a');            -- returns scalar as text
SELECT JSON_QUERY('{"a": [1,2]}', '$.a');        -- returns JSON fragment
```

## jsonpath Type Conversion Methods (17)

New jsonpath methods for type casting within path expressions:

`.bigint()`, `.boolean()`, `.date()`, `.decimal([precision [, scale]])`, `.integer()`, `.number()`, `.string()`, `.time()`, `.time_tz()`, `.timestamp()`, `.timestamp_tz()`

```sql
SELECT jsonb_path_query('{"val": "42"}', '$.val.integer()');
```

## jsonb null → Scalar NULL Cast (18)

Previously errored; now `jsonb` `null` values cast to SQL `NULL`:

```sql
SELECT ('null'::jsonb)::text;  -- returns SQL NULL (was an error before 18)
```

## jsonb_strip_nulls — Strip Array Nulls (18)

New optional parameter to also remove nulls from arrays:

```sql
SELECT jsonb_strip_nulls('{"a": [1, null, 2], "b": null}', strip_in_arrays => true);
-- {"a": [1, 2]}
```

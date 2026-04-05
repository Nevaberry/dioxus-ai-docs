# JSON Functions & Operators (3.46–3.51)

## `json_pretty()` (3.46.0)

Formats JSON with indentation for readable output:

```sql
SELECT
  json_pretty ('{"a":1,"b":[2,3]}');

-- {
--     "a": 1,
--     "b": [
--         2,
--         3
--     ]
-- }
-- Optional second argument sets indent string (default 4 spaces)
SELECT
  json_pretty ('{"a":1}', '  ');

-- 2-space indent
SELECT
  json_pretty ('{"a":1}', char(9));

-- tab indent
```

## Negative JSON Array Indexing (3.47.0)

The `->` and `->>` operators now accept negative indices to access array elements from the right:

```sql
SELECT '[10,20,30]' ->> -1;   -- 30 (last element)
SELECT '[10,20,30]' ->> -2;   -- 20 (second to last)
SELECT '{"a":[1,2,3]}' -> '$.a[#-1]';  -- 3 (json_extract already had #-N syntax)
```

## `jsonb_each()` and `jsonb_tree()` (3.51.0)

Work like `json_each()` and `json_tree()` but return JSONB (binary) for the "value" column when the type is 'array' or 'object'. More efficient for pipelines that process JSON without converting to text:

```sql
-- Returns JSONB values for nested arrays/objects instead of text JSON
SELECT key, value FROM jsonb_each('{"a":1,"b":[2,3]}');
-- key: 'a', value: 1
-- key: 'b', value: (JSONB blob of [2,3])

SELECT * FROM jsonb_tree('{"a":{"b":1}}');
-- Recursively walks the JSON tree, nested objects/arrays as JSONB
```

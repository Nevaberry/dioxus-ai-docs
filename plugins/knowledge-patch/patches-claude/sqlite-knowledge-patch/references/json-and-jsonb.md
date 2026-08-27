# JSON and JSONB

## Operators and insertion

### Numeric-looking object keys (since 3.46.0)

For `->` and `->>`, a text right operand that looks numeric remains a string
object label rather than being treated as an integer array index.

```sql
SELECT '{"0":"zero"}' -> '0';
```

### Negative array indexes (since 3.47.0)

A negative integer on the right of `->>` selects an array element by counting
from the end.

```sql
SELECT '["first","middle","last"]' ->> -1; -- last
```

### Array insertion (since 3.53.0)

`json_array_insert()` and `jsonb_array_insert()` provide array insertion for
JSON and JSONB.

## Validation modes for text and JSONB

One-argument `json_valid(X)` accepts only canonical RFC-8259 text. The
optional flag bits are:

- `1`: canonical text.
- `2`: JSON5 text.
- `4`: fast superficial JSONB check.
- `8`: slower linear-time deep JSONB check.

Flag `6` is the usual choice when JSON5 or plausible JSONB should be
accepted.

```sql
SELECT json_valid(value, 6),
       json_valid(value, 8);
```

`jsonb(X)` itself examines only the outermost element when `X` already looks
like JSONB. Malformed JSONB can raise an error or produce unreliable answers,
though it will not cause memory-safety failures.

## Legacy text JSON stored as BLOBs

Since 3.45.1, a BLOB not accepted as JSONB may still be interpreted as text
JSON when its bytes form valid JSON in the database encoding. Some BLOBs are
valid under both interpretations: `x'33343535'` can represent JSONB integer
`456` or text JSON integer `3456`. Convert legacy text JSON and store it as
`TEXT`.

```sql
UPDATE documents
SET payload = CAST(payload AS TEXT)
WHERE typeof(payload) = 'blob';
```

## JSON5 input

### Control characters and escape rejection

JSON5 string literals may contain ASCII control characters as of 3.46.0. As
of 3.50.0, JSON5 input rejects a `\0` escape followed by a digit.

### SQLite-specific spellings

In addition to JSON5, SQLite accepts `Inf` and `Infinity` in any letter case,
and likewise accepts `QNaN` and `SNaN`. Every NaN spelling is interpreted as
JSON `null`. Unquoted object keys may contain any non-whitespace character
above U+007F.

```sql
SELECT json('[QNaN, snan]'); -- [null,null]
```

## Array length result states

`json_array_length(X,P)` returns an array's length, `0` for an existing
non-array, and SQL `NULL` for a missing path. Malformed JSON or a malformed
path raises an error.

```sql
SELECT json_array_length('{"a":[1],"b":2}', '$.a'),
       json_array_length('{"a":[1],"b":2}', '$.b'),
       json_array_length('{"a":[1],"b":2}', '$.c');
```

## Mutation and aggregation

### Sequential removal and root deletion

Paths passed to `json_remove()` are applied left to right, so an earlier
array deletion can change what a later index addresses. With no paths,
`json_remove()` only minifies the input. Removing path `$` returns SQL
`NULL`.

```sql
SELECT json_remove('[0,1,2,3,4]', '$[0]', '$[2]'); -- [1,2,4]
SELECT json_remove('{"x":1}', '$') IS NULL;         -- 1
```

### Null object labels and JSONB update fix (since 3.50.0)

`json_group_object()` omits entries whose label is `NULL`. Version 3.50.1
fixes a long-standing `jsonb_set()`-family bug exposed by the 3.50.0 JSONB
update optimization.

```sql
WITH input(label, value) AS (VALUES(NULL, 1), ('kept', 2))
SELECT json_group_object(label, value) FROM input;
```

### Duplicate object labels

`json()` currently preserves duplicate object labels, and `json_object()`
currently permits them, but neither behavior is guaranteed for future
versions. Code requiring deterministic lookup or round-tripping should reject
or normalize duplicate labels itself.

## Pretty-printing

`json_pretty(X, indentation)` accepts text JSON or JSONB and uses its second
argument as the indentation unit. Omitting it or passing `NULL` selects four
spaces per level.

```sql
SELECT json_pretty(payload, '  ') FROM documents;
```

## Traversal

### JSONB-preserving traversal (since 3.51.0)

`jsonb_each()` and `jsonb_tree()` work like `json_each()` and `json_tree()`
but keep array and object rows as JSONB in the `value` column.

```sql
SELECT fullkey, type, value
FROM jsonb_tree(jsonb('{"items":[{"id":1}]}'));
```

### Traversal metadata

`json_tree()` and `json_each()` expose `key`, `value`, `type`, `atom`, `id`,
`parent`, `fullkey`, and `path`. `id` is internal and may change between
releases; only uniqueness within one result is guaranteed. `fullkey` remains
the absolute path in the original document even when traversal starts at a
root argument. `path` names the containing array or object.

```sql
SELECT jt.fullkey, jt.atom, jt.type
FROM documents AS d, json_tree(d.payload, '$.partlist') AS jt
WHERE jt.type NOT IN ('object', 'array');
```

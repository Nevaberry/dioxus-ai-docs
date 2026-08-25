# JSON and JSONB

Use this reference for JSON/JSONB validation, JSON5 input, extraction, array
operations, traversal, aggregation, and compatibility with legacy storage.

## Validation and stored representations

### Validation modes (json-and-jsonb-functions)

One-argument `json_valid(X)` accepts canonical RFC-8259 text only. The optional
flags are `1` for canonical text, `2` for JSON5 text, `4` for a quick
superficial JSONB check, and `8` for a slower linear-time deep JSONB check.
Flag value `6` is the usual choice for JSON5 text or plausible JSONB.

```sql
SELECT json_valid(value, 6), json_valid(value, 8);
```

`jsonb(X)` checks only the outermost element when `X` already resembles JSONB.
Malformed JSONB may raise an error or return unreliable answers, but will not
cause memory-safety failures.

### Legacy text JSON in BLOBs (json-and-jsonb-functions)

Since 3.45.1, a BLOB rejected as JSONB may still be interpreted as text JSON
when its bytes form valid JSON in the database encoding. Some BLOBs are valid
both ways: `x'33343535'` can mean JSONB integer `456` or text JSON integer
`3456`. Convert legacy text JSON to `TEXT` to remove the ambiguity:

```sql
UPDATE documents
SET payload = CAST(payload AS TEXT)
WHERE typeof(payload) = 'blob';
```

## JSON5 input

### Control characters and object labels (3.46.0)

JSON5 string literals may contain ASCII control characters. For `->` and
`->>`, a text right operand that looks numeric remains an object label rather
than becoming an integer array index:

```sql
SELECT '{"0":"zero"}' -> '0';
```

### SQLite-specific spellings (json-and-jsonb-functions)

SQLite accepts `Inf` and `Infinity` in any letter case, plus `QNaN` and `SNaN`.
All NaN spellings become JSON `null`. Unquoted object keys may contain any
non-whitespace character above U+007F.

### Escape and aggregate edge cases (3.50.0)

JSON5 rejects a `\0` escape followed by a digit. `json_group_object()` omits
entries whose label is SQL `NULL`:

```sql
WITH input(label, value) AS (VALUES(NULL, 1), ('kept', 2))
SELECT json_group_object(label, value) FROM input; -- {"kept":2}
```

Version 3.50.1 repairs a long-standing `jsonb_set()`-family bug exposed by the
3.50.0 JSONB update optimization.

## Extraction and traversal

### Negative array indexes (3.47.0)

A negative integer on the right of `->>` selects from the end of an array:

```sql
SELECT '["first","middle","last"]' ->> -1; -- last
```

### JSONB-preserving table traversal (3.51.0)

`jsonb_each()` and `jsonb_tree()` mirror `json_each()` and `json_tree()` but
retain array and object rows as JSONB in the `value` column.

### Traversal columns and identifiers (json-and-jsonb-functions)

`json_tree()` and `json_each()` expose `key`, `value`, `type`, `atom`, `id`,
`parent`, `fullkey`, and `path`. Treat `id` as internal: only uniqueness within
one result is guaranteed, and values can change between releases. `fullkey`
is the absolute path in the original document even when traversal begins at a
root argument; `path` identifies the containing array or object.

## Array and path operations

### Array length result states (json-and-jsonb-functions)

`json_array_length(X,P)` returns an array's length, `0` for an existing
non-array, and SQL `NULL` for a missing path. Malformed JSON or path syntax
raises an error.

### Sequential removal and root deletion (json-and-jsonb-functions)

`json_remove()` applies paths left to right, so an early array removal can
change what a later index selects. With no paths it only minifies input;
removing `$` returns SQL `NULL`.

```sql
SELECT json_remove('[0,1,2,3,4]', '$[0]', '$[2]'); -- [1,2,4]
SELECT json_remove('{"x":1}', '$') IS NULL;         -- 1
```

### Array insertion (3.53.0)

Use `json_array_insert()` for text JSON and `jsonb_array_insert()` for JSONB
when inserting array elements.

## Object and presentation behavior

### Duplicate labels (json-and-jsonb-functions)

`json()` currently preserves duplicate object labels and `json_object()`
currently permits them, but neither behavior is guaranteed. Reject or
normalize duplicates when deterministic lookup or round-tripping matters.

### Configurable pretty printing (json-and-jsonb-functions)

`json_pretty(X, indentation)` accepts text JSON or JSONB and uses its second
argument as the indentation unit. Omitting it or passing `NULL` selects four
spaces per level.

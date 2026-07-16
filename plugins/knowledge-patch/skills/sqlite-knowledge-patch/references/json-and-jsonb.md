# JSON and JSONB

## Storage format and validation

SQLite JSONB is an opaque internal BLOB. It is not binary-compatible with PostgreSQL JSONB and generally retains O(N) lookup behavior. Malformed JSONB may abort a statement or yield incorrect answers, but will not cause memory-safety failures.

The one-argument `json_valid(X)` accepts canonical RFC 8259 text only. In `json_valid(X,flags)`:

- Bit `1` accepts canonical text JSON.
- Bit `2` accepts JSON5 text.
- Bit `4` performs a quick superficial JSONB check.
- Bit `8` performs a thorough JSONB check.

Flags must be from 1 through 15; other values raise an error. `json_valid(NULL,...)` is `NULL`. Flag value `6` is the practical test for input plausibly usable by another JSON function. JSON nesting beyond 1000 levels is rejected. `jsonb(X)` checks only the outermost element when `X` already appears to be JSONB and is not a deep validator.

```sql
SELECT json_valid('{x:35}'), json_valid('{x:35}', 6); -- 0, 1
```

Since 3.45.1, a BLOB not recognized as JSONB is accepted as text JSON if conversion to the database text encoding yields valid JSON. A BLOB can be valid under both interpretations with different meanings; migrate legacy text-JSON BLOB columns to actual TEXT.

## JSON5 and normalization

`json(X)` validates, minifies, and converts accepted JSON5 input to canonical JSON text. In addition to JSON5, SQLite accepts case-insensitive `Inf`/`Infinity` and `NaN`/`QNaN`/`SNaN`; NaN forms normalize to JSON `null`.

Literal ASCII control characters inside JSON5 strings are accepted since 3.46.0. Since 3.50.0, a JSON5 `\0` escape followed by a digit is rejected.

Duplicate object labels are currently accepted and preserved by `json()` and accepted by `json_object()`, but code must not rely on preservation in future versions.

`json_pretty(X)` returns formatted JSON (since 3.46.0).

## Paths and operators

A path begins with exactly one `$`. Array indexes are zero-based; `[#-N]` counts from the right, and `[#]` addresses the slot after the last element for append operations.

```sql
SELECT json_set('[0,1,2]', '$[#]', 'new');
```

`->` always returns RFC 8259 text JSON, including quoted strings and `null`. `->>` returns an SQL scalar. A bare text label or integer right operand is accepted as PostgreSQL-style shorthand for a path.

Negative integer right operands count backward from the end of an array (since 3.47.0):

```sql
SELECT '["first","last"]' ->> -1; -- last
```

For `->` and `->>`, a text operand that looks numeric is an object label, not an array index (since 3.46.0):

```sql
SELECT '{"1":"one"}' ->> '1'; -- one
```

## JSON arguments and value arguments

A parameter documented as JSON always parses its input. A parameter documented as `value` treats ordinary SQL text as a JSON string even if the text resembles an object or array. A value is inserted as structured JSON only when it comes directly from another JSON function or `->`; `->>` creates ordinary SQL text and is quoted.

```sql
SELECT json_object('a', '[1,2]'), json_object('a', json('[1,2]'));
-- {"a":"[1,2]"} | {"a":[1,2]}
```

Unicode escapes in ordinary SQL text supplied as a value remain literal text rather than being decoded. `json_quote(X)` likewise JSON-quotes an ordinary SQL number/string but is a no-op for a JSON-subtyped value returned by another JSON function.

## Extraction and diagnostics

- `json_array_length(X,P)` returns the length for an array, `0` for an existing non-array value, and `NULL` for a missing path.
- `json_error_position(X)` returns zero for valid JSON/JSON5 or JSONB. Otherwise it gives the 1-based first error character for text or an approximate 1-based byte offset for a BLOB.
- With one path, `json_extract()` returns SQL `NULL`, INTEGER/REAL, or dequoted TEXT for a scalar and text JSON for an array/object. With multiple paths it always returns a text JSON array.
- `jsonb_extract()` differs only for arrays/objects, which it returns as JSONB.
- `json_type(X,P)` returns `null`, `true`, `false`, `integer`, `real`, `text`, `array`, or `object`; it returns SQL `NULL` for a missing path. This distinguishes present JSON `null` from absence.

## Ordered mutation

`json_insert()` creates missing values without overwriting, `json_replace()` overwrites existing values without creating, and `json_set()` does both. Path/value pairs apply left to right, so an early edit may change the resolution of a later path.

```sql
SELECT json_set('{}', '$.a', json('{}'), '$.a.b', 1);
-- {"a":{"b":1}}
```

`json_remove()` ignores absent paths and applies paths left to right; removing an array entry shifts later indexes. With no paths it only minifies. Removing `$` returns SQL `NULL`.

`json_patch(T,P)` implements RFC 7396 MergePatch. A patch object's `null` member deletes the target member, while arrays are atomic and can only be replaced/deleted as a whole. `jsonb_patch()` uses the same semantics and returns JSONB.

`json_array_insert()` and `jsonb_array_insert()` insert into text JSON and JSONB arrays respectively (since 3.53.0).

The `jsonb_set()` family had a long-standing fault exposed by a 3.50.0 JSONB update optimization; it is fixed in 3.50.1.

## Object and array aggregates

- `json_group_object(label,value)` omits an element when `label` is `NULL` (since 3.50.0).
- `jsonb_group_array(X)` and `jsonb_group_object(NAME,VALUE)` mirror the text-returning aggregates but return JSONB.

## Table-valued traversal

`json_each(X[,P])` emits the selected value or its immediate children. `json_tree(X[,P])` recursively emits the subtree. Rows contain `key`, `value`, `type`, `atom`, `id`, `parent`, `fullkey`, and `path`, plus hidden `json` and `root` inputs.

`atom` contains an SQL scalar for primitive rows and is `NULL` for containers. `parent` is always `NULL` in `json_each()` and identifies the parent row in `json_tree()`. `id` is unique per traversal but its computation is not stable across versions.

Since 3.51.0, `jsonb_each()` and `jsonb_tree()` parallel those functions while keeping array/object rows in the `value` column as JSONB rather than converting them to text JSON.

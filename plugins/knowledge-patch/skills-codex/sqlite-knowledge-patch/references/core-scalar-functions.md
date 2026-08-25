# Core Scalar Functions

Use this reference for conditional, date/time, formatting, text, numeric,
comparison, random, and query-planner helper functions.

## Conditional functions

### Short and variadic `iif()` forms (3.48.0, 3.49.0)

The two-argument form `iif(condition, value)` returns `value` when true and
`NULL` otherwise. `if()` is an alias. The later variadic form accepts ordered
condition/value pairs and may end in one fallback value:

```sql
SELECT if(is_active, display_name);
SELECT iif(score >= 90, 'A', score >= 80, 'B', 'other');
```

## Date and time

### Week-year formats and ambiguous shifts (3.46.0)

`strftime()` supports `%G`, `%g`, `%U`, and `%V`. Add `ceiling` or `floor` after
an ambiguous month or year shift to choose its resolution. `utc` and
`localtime` are no-ops when SQLite already knows the value uses that basis.

```sql
SELECT strftime('%G-W%V', '2024-01-01'),
       date('2024-02-29', '+1 year', 'floor');
```

## Aggregation and concatenation

### Empty aggregate strings (3.47.0)

`group_concat()` returns an empty string, not `NULL`, when its only input is an
empty string.

### Empty fields in `concat_ws()` (3.50.0)

Use 3.50.2 or later when empty-string arguments must be retained:

```sql
SELECT concat_ws(',', 'a', '', 'b'); -- a,,b
```

Version 3.49.1 also repairs an out-of-bounds write when the separator is larger
than two megabytes.

## Formatting and quoting

### Unicode escapes and control-safe output (3.50.0)

`unistr()` interprets backslash escapes, and `unistr_quote()` returns a safely
quoted SQL representation. The `#` flag for `%q` and `%Q` converts control
characters to `unistr()`-compatible escapes in SQL `format()`,
`sqlite3_mprintf()`, and related formatters.

```sql
SELECT unistr('\u0041'), unistr_quote(char(1)), format('%#Q', char(1));
```

### Negative zero and floating-point precision (3.51.0, 3.53.0)

For built-in `printf()` and SQL `format()`, a `#` format without `+` suppresses
the minus sign when every displayed digit is zero:

```sql
SELECT format('%#.2f', -0.001); -- 0.00
```

Floating-point-to-text conversion uses 17 significant digits by default in
3.53.0 rather than 15. `SQLITE_DBCONFIG_FP_DIGITS` changes the setting per
connection.

### Missing and special `format()` arguments (core-scalar-functions)

`format()` returns `NULL` when the format is missing or `NULL`. `%n` is ignored
without consuming an argument, `%p` aliases `%X`, and `%z` behaves like `%s`.
Missing values become zero for numeric formats or an empty string for `%s`.

```sql
SELECT format('%s:%d', 'item'); -- item:0
```

### Embedded NULs in `quote()` (core-scalar-functions)

An SQL string literal cannot represent embedded U+0000, so `quote()` silently
truncates text before the first NUL:

```sql
SELECT quote('a' || char(0) || 'b'); -- 'a'
```

## Text, bytes, and numeric representation

### `hex()` converts numeric text (core-scalar-functions)

For integer and floating-point arguments, `hex()` encodes the UTF-8 text form
of the number, not its binary numeric representation:

```sql
SELECT hex(12345678); -- 3132333435363738
```

### Character length versus encoded length (core-scalar-functions)

For text, `length()` counts Unicode code points only through the first U+0000;
`octet_length()` counts bytes in the database encoding. For BLOBs, both count
bytes.

### Negative substring lengths (core-scalar-functions)

A negative third argument to `substr()` or `substring()` returns that many
characters preceding the position given by the second argument:

```sql
SELECT substr('abcdef', 4, -2); -- bc
```

### Ignored separators in `unhex()` (core-scalar-functions)

The second argument lists non-hexadecimal characters that may be ignored, but
the two digits of each decoded byte must remain adjacent. Hexadecimal
characters named in the second argument are never ignored.

```sql
SELECT hex(unhex('CA-FE', '-')); -- CAFE
```

## Comparison and pattern functions

### Direct `like()` and `glob()` calls (core-scalar-functions)

Scalar `like()` and `glob()` take the pattern first and input string second,
the reverse of how their infix expressions read. When overriding `like()`,
register both the two- and three-argument variants to keep `LIKE` with and
without `ESCAPE` consistent.

### Collation selection (core-scalar-functions)

Multi-argument `min()` and `max()` select the first left-to-right argument that
defines a collation, falling back to `BINARY`; `nullif()` does the same. A
one-argument `min()` or `max()` is an aggregate. Scalar `max()` returns `NULL`
if any argument is `NULL`.

## Randomness, offsets, and planner hints

### Random bounds (core-scalar-functions)

`random()` never returns -9223372036854775808, so `abs(random())` is safe.
`randomblob(N)` returns one byte when `N` is less than one rather than an empty
BLOB.

### Physical record offsets (core-scalar-functions)

With `SQLITE_ENABLE_OFFSET_SQL_FUNC`, `sqlite_offset(column)` reports the
database-file offset of the record supplying an ordinary-table column. If an
index supplies the value, this can be an index-record offset.

### Probability hints (core-scalar-functions)

`likelihood(X,Y)` returns `X` unchanged and tells the planner that it is true
with constant probability `Y` from 0.0 through 1.0. `likely(X)` and
`unlikely(X)` use 0.9375 and 0.0625. All three disappear at runtime.

```sql
SELECT * FROM events WHERE likelihood(kind = 'rare', 0.01);
```

## Extension loading

### SQL-level restrictions (core-scalar-functions)

`load_extension()` is disabled by default and returns `NULL` after success. An
SQL-loaded extension may add functions and collations but cannot replace or
delete existing registrations; use the C API when changing registrations is
required.

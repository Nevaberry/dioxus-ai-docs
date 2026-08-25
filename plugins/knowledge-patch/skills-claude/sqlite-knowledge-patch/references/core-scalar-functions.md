# Core Scalar Functions

## Conditional functions and argument capacity

### `iif()` and `if()`

In 3.48.0, `iif(condition, value)` returns `value` when the condition is true
and `NULL` otherwise, and `if()` becomes an alternative spelling of `iif()`.

```sql
SELECT if(is_active, display_name) FROM users;
```

Since 3.49.0, `iif()` accepts any number of arguments greater than or equal
to two. One call can express multiple condition/value branches with an
optional final fallback.

```sql
SELECT iif(score >= 90, 'A', score >= 80, 'B', 'other');
```

### SQL-function argument limit (since 3.48.0)

The maximum number of arguments to an SQL function is 1000 rather than 127.

## Aggregation and concatenation

### Empty `group_concat()` input (since 3.47.0)

`group_concat()` returns an empty string rather than `NULL` when its only
input is an empty string.

```sql
WITH input(value) AS (VALUES(''))
SELECT group_concat(value) FROM input;
```

### `concat_ws()` corrections

Version 3.49.1 fixes an out-of-bounds write when the separator passed to
`concat_ws()` is larger than two megabytes. As of 3.50.2, `concat_ws()`
preserves empty-string arguments instead of dropping them.

```sql
SELECT concat_ws(',', 'a', '', 'b'); -- a,,b
```

## Unicode escaping and safe quoting (since 3.50.0)

`unistr()` interprets backslash escapes. `unistr_quote()` produces a safely
quoted SQL representation. For `%q` and `%Q`, the `#` flag converts control
characters to backslash escapes suitable for `unistr()` in SQL `format()`,
`sqlite3_mprintf()`, and related formatters.

```sql
SELECT unistr('\u0041'),
       unistr_quote(char(1)),
       format('%#Q', char(1));
```

## Formatting rules

### Missing and special `format()` arguments

`format()` returns `NULL` when its format is missing or `NULL`. `%n` is
ignored without consuming an argument, `%p` aliases `%X`, and `%z` acts like
`%s`. Missing value arguments become zero for numeric formats or an empty
string for `%s`.

```sql
SELECT format('%s:%d', 'item'); -- item:0
```

### Negative zero (since 3.51.0)

For built-in `printf()` and SQL `format()`, a `#` format without `+`
suppresses the minus sign when every displayed digit is zero.

```sql
SELECT format('%#.2f', -0.001); -- 0.00
```

## Text, byte, and numeric representation

### Numeric arguments to `hex()`

For an integer or floating-point argument, `hex()` encodes the number's UTF-8
text representation rather than its binary numeric representation.

```sql
SELECT hex(12345678); -- 3132333435363738
```

### Character length versus encoded length

For text, `length()` counts Unicode code points only up to the first U+0000,
whereas `octet_length()` counts bytes in the database encoding. For BLOBs,
both count bytes.

```sql
SELECT length('a' || char(0) || 'b'),
       octet_length('a' || char(0) || 'b');
```

### Embedded NULs in `quote()`

Because an SQL string literal cannot represent an embedded NUL, `quote()`
silently truncates text before the first NUL.

```sql
SELECT quote('a' || char(0) || 'b'); -- 'a'
```

## Pattern functions and collations

### Direct `like()` and `glob()` calls

Scalar calls take the pattern first and input string second, reversing the
corresponding infix expressions. To make `LIKE` with and without `ESCAPE`
behave consistently, overriding `like()` requires registering both its two-
and three-argument forms.

```sql
SELECT like('%on%', 'neon'), glob('*on*', 'neon');
```

### Collation in scalar comparisons

Multi-argument `min()` and `max()` use the first argument from the left that
defines a collation, falling back to `BINARY`; `nullif()` selects its
collation the same way. A one-argument `min()` or `max()` is an aggregate.
Scalar `max()` returns `NULL` if any argument is `NULL`.

```sql
SELECT max('a' COLLATE NOCASE, 'B');
```

## Extension loading

`load_extension()` is disabled by default and returns `NULL` after a
successful load. It can add but cannot replace or delete SQL functions or
collations. Use the C API when an extension must change existing
registrations.

```sql
SELECT load_extension('./extension', 'entry_point');
```

## Random values, substrings, and hex decoding

### Random generator edge bounds

`random()` never returns -9223372036854775808, so its result is always safe
for `abs()`. `randomblob(N)` returns one byte rather than an empty BLOB when
`N` is less than one.

```sql
SELECT abs(random()), length(randomblob(0));
```

### Negative substring lengths

A negative third argument to `substr()` or `substring()` returns the
requested number of characters preceding the position named by the second
argument.

```sql
SELECT substr('abcdef', 4, -2); -- bc
```

### Selectively ignored `unhex()` separators

The second argument to `unhex()` lists non-hexadecimal characters that may be
ignored in the input, but every decoded pair of hexadecimal digits must stay
adjacent. Hexadecimal characters listed in the second argument are never
ignored.

```sql
SELECT hex(unhex('CA-FE', '-')); -- CAFE
```

## Physical offsets and planner probability hints

### `sqlite_offset()`

`sqlite_offset(column)` reports the database-file offset of the record
supplying an ordinary-table column. It may be an index record when the query
reads from an index. The function is available only in builds compiled with
`SQLITE_ENABLE_OFFSET_SQL_FUNC`.

```sql
SELECT sqlite_offset(name) FROM users WHERE name = ?;
```

### `likelihood()`, `likely()`, and `unlikely()`

`likelihood(X,Y)` returns `X` unchanged while telling the planner it is true
with constant probability `Y` from 0.0 through 1.0. `likely(X)` and
`unlikely(X)` are shorthand for 0.9375 and 0.0625. All three are optimized
away at runtime.

```sql
SELECT * FROM events WHERE likelihood(kind = 'rare', 0.01);
```

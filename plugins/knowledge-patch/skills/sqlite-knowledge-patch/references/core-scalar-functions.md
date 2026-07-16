# Core Scalar Functions

## Conditional selection

`iif()` gained a two-argument form and the equivalent `if()` spelling in 3.48.0. `iif(condition, true_value)` returns `NULL` when the condition is false.

Since 3.49.0, `iif()` and `if()` accept any number of arguments greater than or equal to two. They evaluate condition/value pairs from left to right; an unpaired final argument is the fallback, otherwise no matching condition yields `NULL`.

```sql
SELECT iif(score >= 90, 'A', score >= 80, 'B', 'other');
```

## Numeric conversion and randomness

- `abs(X)` returns `0.0` for text or BLOB input that cannot be numeric, but raises integer overflow for `-9223372036854775808`.
- `sign(X)` returns `NULL` for text unless the string converts losslessly to a number.
- `hex(number)` first renders the number as UTF-8 text, then hex-encodes those bytes. `hex(12345678)` is `3132333435363738`, not the number's binary memory representation.
- `random()` ranges from `-9223372036854775807` through `+9223372036854775807`; it deliberately excludes the one integer unsafe for `abs()`.
- `randomblob(N)` returns one byte when `N < 1`.

## Length, substrings, and encodings

- `length(text)` counts Unicode code points only through the first U+0000. `length(blob)` counts bytes.
- `octet_length(text)` counts bytes in the database encoding. For a TEXT or BLOB column, SQLite can often obtain the length from record metadata without reading a large value from disk.
- A negative `substr()` start counts from the right. A negative length returns characters immediately preceding the start: `substr('abcdef', 5, -2)` is `cd`. TEXT indexes count characters; BLOB indexes count bytes.
- `unhex(X,Y)` ignores in `X` only non-hex separator characters listed in `Y`; hex digits must remain adjacent pairs. A hex digit listed in `Y` is never ignored. `hex(unhex('AB-CD','-'))` is `ABCD`; any unlisted non-hex character causes `NULL`.

## Pattern functions and collations

- Direct calls reverse the operands relative to infix syntax: `like(pattern, value[, escape])` implements `value LIKE pattern`, and `glob(pattern, value)` implements `value GLOB pattern`.
- Overriding `like()` or `glob()` also overrides its operator. A replacement `like()` should provide both two- and three-argument forms.
- With two or more arguments, `min()` and `max()` are scalar functions; one argument selects the aggregate form. Scalar forms scan left to right for the first attached collation and use it for all string comparisons. Scalar `max()` returns `NULL` if any argument is `NULL`.

## Formatting and quoting

- Missing `format()` arguments act as `NULL`: numeric conversions see zero and `%s` sees an empty string. `%n` is ignored without consuming an argument, `%p` behaves as `%X`, and `%z` behaves as `%s`.
- For built-in `printf()` and SQL `format()`, `#` removes a leading minus from a floating result when `+` is absent and every displayed digit is zero (since 3.51.0): `format('%#.2f', -0.001)` returns `0.00`.
- `quote(text)` truncates silently before an embedded NUL because SQL string literals cannot encode it. Do not use `quote()` to serialize arbitrary text containing NUL.
- `unistr()` decodes backslash escapes and `unistr_quote()` safely quotes text (since 3.50.0). The `%q` and `%Q` `#` flag emits control characters as backslash escapes suitable for `unistr()`: `format('%#Q', char(1))`.

## Concatenation and date/time

- `concat_ws()` includes empty-string arguments as of 3.50.2: `concat_ws(',', 'a', '', 'b')` returns `a,,b`.
- `strftime()` supports `%G`, `%g`, `%U`, and `%V` since 3.46.0.
- After a month/year shift produces an impossible date, `floor` chooses the last valid day of the prior month and `ceiling` rolls forward. For example, `date('2024-02-29', '+1 year', 'floor')` is `2025-02-28`; `ceiling` gives `2025-03-01`.
- `utc` and `localtime` are no-ops when the input is already known to use the requested time basis.

## Planner hints and optional functions

- `likelihood(X,Y)` returns `X` unchanged while telling the planner that Boolean `X` is true with constant probability `Y` from 0.0 through 1.0.
- `likely(X)` is `likelihood(X,0.9375)` and `unlikely(X)` is `likelihood(X,0.0625)`. All three are optimized away at runtime.
- `sqlite_offset(column)` requires `SQLITE_ENABLE_OFFSET_SQL_FUNC`. It returns the file offset of the supplying record, which may be an index record; non-columns and values outside ordinary tables produce `NULL`.
- `soundex()` requires `SQLITE_SOUNDEX` and is absent from default builds. When enabled, it returns `?000` for `NULL` or input with no ASCII letters.

## Extension loading

SQL `load_extension()` remains disabled until the connection enables extension loading. It may add functions and collations during a statement but cannot replace or delete existing ones; use `sqlite3_load_extension()` from C when replacement or deletion is required.

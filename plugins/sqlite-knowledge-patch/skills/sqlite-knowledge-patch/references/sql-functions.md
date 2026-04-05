# SQL Functions & Syntax (3.46–3.50)

## Underscore in Numeric Literals (3.46.0)

Underscores between digits improve readability (ignored by parser):

```sql
SELECT
  1_000_000;

-- 1000000
SELECT
  3.141_592_653;

-- 3.141592653
SELECT
  0xFF_FF;

-- 65535
```

## Date/Time `ceiling` and `floor` Modifiers (3.46.0)

Control how ambiguous dates are resolved when shifting by months/years:

```sql
-- Jan 31 + 1 month: Feb has no 31st
SELECT date('2024-01-31', '+1 month');              -- 2024-03-03 (default: overflow)
SELECT date('2024-01-31', '+1 month', 'ceiling');   -- 2024-03-01 (next valid date)
SELECT date('2024-01-31', '+1 month', 'floor');     -- 2024-02-29 (last day of target month)
```

## `if()` Alias and Variadic `iif()` (3.48.0 / 3.49.0)

`if()` is now accepted as an alias for `iif()`. Starting in 3.48.0, a two-argument form was added; in 3.49.0 it was extended to accept any number of arguments, working like a compact CASE:

```sql
-- Two-arg form (3.48.0): returns NULL when false
SELECT iif(score > 90, 'excellent');

-- if() alias works the same way
SELECT if(score > 90, 'excellent', 'other');

-- Variadic form (3.49.0): cascading conditions like CASE
-- iif(cond1, val1, cond2, val2, ..., default)
SELECT iif(
  score > 90, 'excellent',
  score > 70, 'good',
  'needs work'
);
```

## `unistr()` and `unistr_quote()` (3.50.0)

`unistr()` interprets Unicode escape sequences in strings. `unistr_quote()` does the reverse — quotes a string with escapes for non-printable/special characters:

```sql
SELECT unistr('Hello\u0021');       -- 'Hello!'
SELECT unistr('\u00e9');             -- 'é'
SELECT unistr_quote('Hello!');      -- 'Hello\u0021' (or similar escaped form)
```

The `format()` function's `%Q`/`%q` now supports `#` flag to escape control characters via `unistr()`:

```sql
SELECT format('%#Q', char(9) || 'tab');  -- unistr('\0009tab') style output
```

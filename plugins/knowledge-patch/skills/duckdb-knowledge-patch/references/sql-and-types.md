# SQL and types

Use this reference for typed heterogeneous values, expression semantics, column
expansion, secrets, and direct DuckDB-file queries. The type and expression
changes span source batches `1.2-1.4` and `1.5.0`.

## Native `VARIANT`

`VARIANT` stores a typed binary value per row rather than JSON text. Different
rows may hold heterogeneous scalars, lists, or structs. Cast values explicitly:

```sql
CREATE TABLE events (id INTEGER, data VARIANT);

INSERT INTO events VALUES
    (1, {'name': 'Alice', 'age': 30}::VARIANT),
    (2, [10, 20, 30]::VARIANT),
    (3, 'plain text'::VARIANT);
```

Use `variant_typeof` to inspect the stored type. Nested values can be accessed
with dot notation or `variant_extract`:

```sql
SELECT
    variant_typeof(data),
    variant_extract(data, 'name')
FROM events;
```

DuckDB reads Parquet `VARIANT` columns, including shredded representations.
DuckLake and Delta support the type in 1.5.0. Iceberg support begins in 1.5.1,
so a 1.5.0 Iceberg workflow must not assume it is present.

Do not treat `VARIANT` as JSON text. Preserve it through typed APIs unless a
textual interchange format is explicitly required.

## Map extraction

Bracket lookup returns a scalar value and is aliased by `map_extract_value`:

```sql
WITH source AS (SELECT map(['k'], ['v']) AS m)
SELECT m['k'], map_extract_value(m, 'k')
FROM source;
```

Use `map_extract` when a single-element list is intentionally required:

```sql
SELECT map_extract(map(['k'], ['v']), 'k'); -- ['v']
```

This distinction affects result schemas, list functions, client decoding, and
generated SQL that assumed bracket lookup returned a list.

## `date_trunc` result typing

`date_trunc` over a `DATE` returns `TIMESTAMP` in 1.5.0:

```sql
SELECT date_trunc('month', DATE '2026-03-27');
SELECT typeof(date_trunc('month', DATE '2026-03-27')); -- TIMESTAMP
```

Cast only at the contract boundary that actually requires `DATE`:

```sql
SELECT date_trunc('month', order_date)::DATE AS order_month
FROM orders;
```

## Computed column expansion with `UNPACK`

`UNPACK` expands a `COLUMNS(*)` expression after transformations. The older
leading `*COLUMNS(...)` form cannot express this ordering:

```sql
SELECT [UNPACK(COLUMNS(*)::VARCHAR)] AS values
FROM tbl;
```

Use this when a set of selected columns must first be cast or otherwise
transformed and then expanded.

## Expressions in `CREATE SECRET`

Secret fields accept scalar expressions, allowing credentials to come from
variables or the process environment rather than literal SQL:

```sql
CREATE SECRET http (
    TYPE http,
    BEARER_TOKEN getenv('MY_SECRET')
);
```

This avoids placing the credential directly in SQL text that may be logged.
Apply normal process-environment and secret-lifecycle controls as well; moving a
value out of a literal does not by itself secure its source.

## Direct DuckDB-file scans

The `read_duckdb` table function reads database files without `ATTACH` and
accepts glob patterns:

```sql
SELECT min(i), max(i)
FROM read_duckdb('numbers*.db');
```

Choose `read_duckdb` for a direct query across files. Use `ATTACH` when the task
requires a persistent catalog name, encryption or storage options, database
copying, or repeated cross-database operations.

## Time and random expressions

`current_time` and `current_date` use the local timezone and require ICU. Verify
that the target build has ICU and that the process timezone is intentional.

Fixed random seeds yield different sequences after the generator-state change.
Rebuild expected test fixtures instead of treating a sequence from an older
engine as the permanent definition of a seed.

## Nested serialization

Strings embedded in serialized nested structures escape quotes so the output
round-trips. Use the serialization when correctness requires a recoverable
representation. Use `array_to_string` when the desired output is specifically
the earlier unquoted display.

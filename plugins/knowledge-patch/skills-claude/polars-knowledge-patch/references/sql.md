# SQL

Use this reference for query scope, operators, functions, aggregates, joins,
null semantics, and SQL validation.

## Query scope

### Frame SQL cannot see global frames (1.0-upgrade)

`DataFrame.sql` and `LazyFrame.sql` query only their own frame and cannot
resolve other global frames. Use top-level SQL for multi-frame queries:

```python
pl.sql("SELECT * FROM df1 CROSS JOIN df2", eager=True)
```

## Operators and scalar functions

### Bit operations (1.10.0)

Polars SQL supports `bit_count` and the bitwise `&`, `|`, and `xor` operators.

### Unicode normalization (1.20.0)

Polars SQL supports the `NORMALIZE` function. The expression counterpart is
`str.normalize`.

### Multiline `LIKE` and `ILIKE` (1.20.0)

`LIKE` and `ILIKE` match across line breaks, so `%` can span newline characters
in multiline strings.

### True division (1.41.0)

The `/` operator uses true-division semantics. Integer inputs can produce a
fractional result: `SELECT 1 / 2` evaluates to `0.5`, not an integer quotient.

## Aggregates

### Discrete quantiles (1.10.0)

`QUANTILE_DISC` is available and uses the supported discrete quantile
interpolation method.

### Correct literal counts (1.40.0)

`COUNT(<literal>)` returns the correct result. Recheck expected output from
queries that count literal expressions.

### Aggregate filters and strings (1.41.0)

Aggregate `FILTER` clauses and `STRING_AGG` are supported:

```sql
SELECT
  SUM(value) FILTER (WHERE keep),
  STRING_AGG(name, ',')
FROM frame
```

### All-null aggregates and `TOTAL` (py-1.43.2-rs-0.55.1-0.55.2)

`SUM` and `CORR` return null for all-null inputs. Polars SQL also provides the
`TOTAL` aggregate.

## Joins, grouping, and subqueries

### Expanded joins and grouping (py-1.43.2-rs-0.55.1-0.55.2)

Polars SQL supports implicit `JOIN` syntax, computed `GROUP` keys in
projections, and `[NOT] IN (subquery)` predicates.

## Validation and errors

### Invalid `HAVING` placement (1.10.0)

Using `HAVING` outside a `GROUP BY` query raises `SQLSyntaxError`.

### Invalid expression rejection (1.40.0)

`sql_expr` rejects invalid input rather than passing it through. Treat parsing
failure as an early validation error.

## Review checklist

When migrating a query suite, test frame visibility, integer division, all-null
aggregates, literal counts, aggregate filters, newline-spanning patterns,
implicit joins, computed grouping keys, and invalid `HAVING` placement.

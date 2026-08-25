# Lazy Execution, Streaming, and SQL

Use this reference for lazy schema planning, optimizer controls, streaming
execution, joins, grouping, sorted merges, and Polars SQL behavior.

## Lazy schema and plan control

### Collect schemas explicitly

Since `1.0-upgrade`, accessing `LazyFrame.schema`, `.dtypes`, `.columns`, or
`.width` emits `PerformanceWarning` because schema resolution can be expensive.
Collect once and inspect the returned `Schema`:

```python
schema = lf.collect_schema()
```

### Match lazy input to an expected schema

Since `1.30.0`, `LazyFrame.match_to_schema` can reconcile a lazy frame before
execution:

```python
lf = lf.match_to_schema({"id": pl.Int64})
```

### Centralize optimization settings

Since `1.30.0`, lazy optimization controls live in `QueryOptFlags`. Pass a flags
object instead of relying on separate controls.

### Do not assume `map_batches` optimizations

Since `1.40.0`, `LazyFrame.map_batches` defaults to no optimizations. Enable
transformations explicitly only when they are safe for the callback.

### Specify graph plan stages

In `py-1.43.2-rs-0.55.1-0.55.2`, calling `show_graph()` without `plan_stage`
became deprecated. Choose the stage explicitly.

## Streaming execution

### Use expanded streaming operations

In `1.20.0`, the new streaming engine gained support for first/last and
additional `group_by` aggregations, plus Parquet sink output.

In `1.40.0`, coverage expanded to grouped as-of joins, native interpolation,
`strptime` with `format=None`, covariance and correlation, and PyArrow dataset
sources.

### Treat the engine as stable

Since `1.41.0`, the streaming engine is stable rather than experimental. Code
that explicitly selects it can treat it as a supported execution engine.

### Preserve null rows in grouped as-of joins

Since `1.40.0`, grouped as-of joins retain null rows instead of dropping them.

## Joins and sorted merges

### Exclude exact as-of matches

Since `1.20.0`, `join_asof` accepts `allow_exact_matches`:

```python
out = left.join_asof(right, on="ts", allow_exact_matches=False)
```

### Resolve overlapping names in conditional joins

Since `1.10.0`, `join_where` correctly resolves columns whose names partially
overlap.

### Merge several sorted frames

Since `1.40.0`, top-level `pl.merge_sorted` can merge multiple already-sorted
frames.

In `py-1.43.2-rs-0.55.1-0.55.2`, `merge_sorted` gained multiple merge keys for
lexicographically sorted frames.

### Keep sortedness annotations narrow

Since `1.0-upgrade`, each `set_sorted` call accepts one column and promises that
column is independently sorted. Chain annotations instead of treating several
columns as a joint key.

## Grouping and global aggregation

### Use `.over()` for a global window

Since `1.30.0`, a window expression may omit `partition_by`; the entire input is
then one window:

```python
df.with_columns(total=pl.col("value").sum().over())
```

### Call `group_by()` without keys

Since `1.40.0`, `group_by()` accepts no key expressions, exposing the group-by
aggregation interface for one global group.

### Group by fixed-size arrays

Since `1.30.0`, fixed-size `Array` columns can be grouping keys.

## SQL context and validation

### Use top-level SQL for multiple frames

Since `1.0-upgrade`, `DataFrame.sql` and `LazyFrame.sql` operate only on their
own frame and cannot resolve other global frames. Use the top-level context for
multi-frame queries:

```python
pl.sql("SELECT * FROM df1 CROSS JOIN df2", eager=True)
```

### Reject misplaced `HAVING`

Since `1.10.0`, using `HAVING` outside a `GROUP BY` query raises
`SQLSyntaxError`.

### Reject invalid expression strings

Since `1.40.0`, `sql_expr` rejects invalid input instead of allowing it through.

## SQL operators and scalar functions

### Use bit operations

Since `1.10.0`, Polars SQL supports `bit_count` and the bitwise `&`, `|`, and
`xor` operators.

### Normalize Unicode

Since `1.20.0`, Polars SQL supports the `NORMALIZE` function.

### Match patterns across line breaks

Since `1.20.0`, SQL `LIKE` and `ILIKE` match across line breaks, so `%` can span
newline characters.

### Account for true division

Since `1.41.0`, SQL `/` uses true-division semantics. Integer operands can
produce fractions: `SELECT 1 / 2` evaluates to `0.5` rather than integer
quotient.

## SQL aggregates

### Use discrete quantiles

Since `1.10.0`, SQL supports `QUANTILE_DISC`, backed by discrete quantile
interpolation.

### Filter and concatenate aggregate inputs

Since `1.41.0`, aggregate `FILTER` clauses and `STRING_AGG` are supported:

```sql
SELECT
  SUM(value) FILTER (WHERE keep),
  STRING_AGG(name, ',')
FROM frame
```

### Count literal expressions correctly

Since `1.40.0`, SQL `COUNT(<literal>)` returns the correct result. This can
change output from queries that count literal expressions.

### Handle all-null aggregates and `TOTAL`

In `py-1.43.2-rs-0.55.1-0.55.2`, `SUM` and `CORR` return null for all-null
inputs, and Polars SQL adds the `TOTAL` aggregate.

## Expanded SQL joins and grouping

In `py-1.43.2-rs-0.55.1-0.55.2`, Polars SQL adds:

- implicit `JOIN` syntax;
- computed `GROUP` keys in projections;
- `[NOT] IN (subquery)` predicates.

## Dynamic windows

Since `1.0-upgrade`, `group_by_dynamic` defaults `offset` to zero rather than
negative `every`. Set a negative offset explicitly when the earlier leading
window is required.

Since `1.10.0`, `rolling_*_by` windows can be based on index count in addition
to time.

## Persisted lazy plans

Since `1.30.0`, deserialization rejects a DSL representation incompatible with
the reader. Persisted expressions and lazy plans require a compatible
representation.

In `py-1.43.2-rs-0.55.1-0.55.2`, lazy frames backed by in-memory bytes became
serializable rather than failing because of their source representation.

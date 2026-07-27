# Tables, indexes, and views

Use this reference for table-definition validation, schema evolution, semi-structured columns, optimizer data structures, and deterministic refreshable-view chains.

## MergeTree table definitions

### `AggregatingMergeTree` dimensions

Table creation rejects columns that are neither sorting-key dimensions nor `AggregateFunction` or `SimpleAggregateFunction` measures. Such ordinary columns would otherwise collapse to an arbitrary value during merges.

Prefer placing every true dimension in the sorting key. Set the following only when retaining the old behavior is intentional and arbitrary merge selection is acceptable:

```sql
SET allow_dimensions_outside_sorting_key = 1;
```

### Table-wide MinMax indexes

A `MergeTree` table can create a granularity-1 MinMax data-skipping index for every numeric column:

```sql
CREATE TABLE readings
(
    ts DateTime,
    sensor_id UInt32,
    value Float64
)
ENGINE = MergeTree
ORDER BY ts
SETTINGS add_minmax_index_for_numeric_columns = 1;
```

Generated indexes are named `auto_minmax_index_<column>`. They are most useful when a numeric column is at least somewhat correlated with row order; verify pruning with `EXPLAIN indexes=1`.

## Schema inference and semi-structured data

### Common schemas for merged tables

The `merge` table function and `Merge` engine infer a common schema across all matched tables rather than adopting the first table's structure. Incompatible column types are represented with `Variant`, such as `Variant(Array(String), String)`. Consumers must therefore handle the inferred union rather than relying on match order.

### JSON, Variant, and Dynamic

The `JSON` data type and its standalone `Variant` and `Dynamic` building blocks are production-ready as of 25.3. Prefer these types over ad hoc serialized strings when typed subcolumns, heterogeneous values, or schema evolution are required.

## Projections and query-result reuse

### Filtered projections

A projection definition may contain `WHERE`; only matching rows are materialized. The cost-based optimizer can choose the projection when the query predicate logically implies the projection predicate. A partial overlap is not sufficient, so inspect the chosen plan.

### Query condition cache

The query condition cache can reuse scan results for an identical selective `WHERE` predicate across different queries. This includes predicates that receive no help from the primary index. Treat identity and selectivity as important: a merely similar predicate does not imply a cache hit, and broad predicates may not justify caching.

## Text indexes

### Required feature flag and tokenizer (`25.1-25.12`)

Text indexes are beta and require:

```sql
SET enable_full_text_index = 1;
```

`default` is not a valid tokenizer. Name one of `splitByNonAlpha`, `splitByString`, `ngrams`, `sparseGrams`, or `array`:

```sql
INDEX inv_idx(text)
TYPE text(tokenizer = 'splitByNonAlpha')
GRANULARITY 128
```

Use `hasToken`, `hasAllTokens`, or `hasAnyTokens` for direct indexed lookup. Predicates such as `LIKE` can use the index only when ClickHouse can extract complete tokens from the search term.

### Token postprocessing (`26.7`)

The text-index definition accepts a `postprocessor` argument containing an expression applied to every token after tokenization. For example, a `lower` expression can normalize case consistently at index time.

### Discover supported stemming languages

Query the system table instead of maintaining a hard-coded language list:

```sql
SELECT * FROM system.stemmers;
```

Its rows enumerate the languages accepted by the `stem` function.

## Hypothetical skip indexes

Session-local candidates can be evaluated without creating persistent metadata:

```sql
CREATE HYPOTHETICAL INDEX town_set
ON uk_price_paid (town)
TYPE set(10)
GRANULARITY 1;

EXPLAIN WHATIF
SELECT * FROM uk_price_paid WHERE town = 'LONDON';
```

The analysis reads table data to build candidates in memory, so it counts against read limits and quotas. Definitions disappear with the session. Use the results to inform a real index decision, not as persistent schema.

## In-place schema changes

### Check constraints

Replace an existing check expression without dropping and recreating the named constraint:

```sql
ALTER TABLE events
MODIFY CONSTRAINT IF EXISTS positive_value CHECK value > 0;
```

`IF EXISTS` suppresses failure when the named constraint is absent; omit it when absence should be treated as a migration error.

### Append enum values

Add a member without restating the existing enum definition:

```sql
ALTER TABLE uk_price_paid
MODIFY COLUMN type ADD ENUM VALUES('royal' = 5);
```

Choose a numeric enum value that does not conflict with the existing mapping.

## Refreshable materialized-view chains

A dependent refreshable materialized view can omit its own timer and refresh only after its parent completes:

```sql
REFRESH DEPENDS ON parent_view
```

This creates deterministic cascading refreshes without independent schedules drifting apart. Keep the dependency graph acyclic and account for parent failures when monitoring downstream freshness.

# Query language and functions

Use this reference when generating SQL expressions, inspecting plans, parameterizing settings, or updating queries for changed function signatures and return types.

## Compatibility-sensitive functions

### Snowflake ID conversions

The legacy conversion names are removed and cannot be restored with `allow_deprecated_snowflake_conversion_functions`. Replace them as follows:

| Removed | Replacement |
|---|---|
| `snowflakeToDateTime` | `snowflakeIDToDateTime` |
| `snowflakeToDateTime64` | `snowflakeIDToDateTime64` |
| `dateTimeToSnowflake` | `dateTimeToSnowflakeID` |
| `dateTime64ToSnowflake` | `dateTime64ToSnowflakeID` |

### `toTime` return type

`use_legacy_to_time = 0` is the default, so `toTime` produces the `Time` data type. Use `toTimeWithFixedDate` for the prior fixed-date conversion, or set `use_legacy_to_time = 1` only when an existing query deliberately depends on the old representation.

### Local-only table-column inspection

Only this overload remains:

```sql
hasColumnInTable(database, table, column)
```

The overload accepting `hostname`, `username`, and `password` is unavailable. Run metadata checks on the target server or use an appropriate distributed query instead of embedding remote credentials in this function.

### Wider `DateTime64` calendar range

`DateTime64` supports dates from `0000-01-01` through `9999-12-31`, rather than clamping values outside `1900-01-01` through `2299-12-31`. Precisions 8 and 9 are still constrained by their `Int64` tick representation. At nanosecond precision, the maximum remains `2262-04-11`.

## Plan inspection and reuse

### Runtime plans

`EXPLAIN ANALYZE SELECT ...` executes the query and annotates the normal plan with actual execution metrics. Because it runs the query, do not use it as a harmless parser check for expensive or mutating query forms.

### Pretty and compact plans

`pretty=1` renders an indented plan tree. `compact=1` collapses `Expression` steps. Options compose:

```sql
EXPLAIN indexes=1, pretty=1, compact=1
SELECT number FROM numbers(10);
```

### Materialized CTEs

Enable the feature for the session:

```sql
SET enable_materialized_cte = 1;
```

Then mark a CTE with `MATERIALIZED` to evaluate it once into a temporary table and reuse the result at every reference:

```sql
WITH summary AS MATERIALIZED (
    SELECT account_id, sum(amount) AS total
    FROM payments
    GROUP BY account_id
)
SELECT *
FROM summary AS current
JOIN summary AS comparison USING (account_id);
```

## Aggregation and formatting

### `groupFormat`

`groupFormat` formats all rows in each group using a requested ClickHouse output format and returns the formatted result as a string. Use it when a grouped result needs format-level serialization rather than ordinary string concatenation.

### `-Tuple` aggregate combinator

The `-Tuple` combinator independently aggregates corresponding tuple elements, preserves element names, and permits different element types:

```sql
SELECT sumTuple((a, b)) FROM t;
```

The result is equivalent in shape to `(sum(a), sum(b))`. For a multi-argument aggregate, positions are paired across tuples:

```sql
SELECT corrTuple((a1, a2), (b1, b2)) FROM t;
```

### Compression-ratio estimation

The parametric aggregate `estimateCompressionRatio(codec)(column)` estimates a codec or codec chain against query data before a table codec is chosen. It also works directly over external data:

```sql
SELECT estimateCompressionRatio('Gorilla, ZSTD')(value)
FROM file('measurements.parquet');
```

## Ordering, limits, and membership

### Natural sorting

`naturalSortKey(value)` generates a human-oriented key for strings containing numbers:

```sql
SELECT introduced_in
FROM features
ORDER BY naturalSortKey(introduced_in);
```

### Negative limits with ties

`WITH TIES` is valid with a negative `LIMIT`. Preserve tie behavior when selecting rows relative to the end of an ordered result rather than rewriting the limit as a positive prefix.

### Row-dependent `IN` arrays

The right side of `IN` may be a non-constant array expression evaluated for each row:

```sql
SELECT *
FROM flights
WHERE airport_id IN (payment_type = 'cash' ? [138] : [132]);
```

## Time-zone operators

Standard postfix syntax maps directly to ClickHouse functions:

```sql
SELECT
    ts AT TIME ZONE 'Europe/Helsinki',
    ts AT LOCAL
FROM events;
```

`expr AT TIME ZONE zone` is equivalent to `toTimeZone(expr, zone)`. `expr AT LOCAL` is equivalent to `toTimeZone(expr, timeZone())`.

## Parameters in settings

Typed query parameters work in both query-level `SETTINGS` and standalone `SET`:

```sql
SELECT *
FROM events
SETTINGS max_threads = {threads:UInt64};

SET max_threads = {threads:UInt64};
```

Keep the declared parameter type compatible with the target setting; parameter substitution does not remove setting type validation.

## Hashing and authentication helpers

### Spark-compatible xxHash64

`xxHash64Spark` accepts `String` and `NULL`, applies Spark's seed-42 semantics, and returns `Int64`. Use this spelling when hash equality with Spark matters; it is not just an alias for every xxHash64 convention.

### HMAC validation

`HMAC(algorithm, message, key)` computes a keyed message authentication code:

```sql
SELECT lower(hex(HMAC('SHA256', raw_payload, 'secret')));
```

An HTTP-ingestion query can compare the result with `getClientHTTPHeader(...)` after explicitly enabling `allow_get_client_http_header = 1`. Keep secrets out of query logs and prefer controlled settings or collections over hard-coded production keys.

## JSON and digit extraction

### Typed JSON input

`JSONExtractString` accepts the `JSON` data type directly; serializing to `String` first is unnecessary:

```sql
SELECT JSONExtractString(
    '{"ClickHouse":{"version":"26.3"}}'::JSON,
    'ClickHouse',
    'version'
);
```

### Digit slices

`digits(n, offset[, length])` starts at a one-based digit offset. It returns the requested number of digits, or the remainder when `length` is omitted.

## Source metadata and dictionaries

### `_table` in ordinary queries

The `_table` virtual column is available in ordinary table and table-function queries, not only inside `merge`. Select it when unioned or dynamically selected sources must retain their table identity.

### Reverse dictionary lookup

`dictGetKeys(dictionary, attribute, value)` returns primary keys whose attribute equals the requested value:

```sql
SELECT dictGetKeys(
    'taxi_zone_dictionary',
    'Borough',
    'Bronx'
);
```

The per-query reverse-lookup cache is bounded by `max_reverse_dictionary_lookup_cache_size_bytes`; account for that limit when a value matches many keys.

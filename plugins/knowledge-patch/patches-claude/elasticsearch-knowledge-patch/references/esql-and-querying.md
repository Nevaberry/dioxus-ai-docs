# ES|QL and Distributed Querying

Check feature maturity and server version before relying on newer commands.
Some commands began as technical previews and changed capability over later
releases.

## Joins, branches, and reusable pipelines

### `LOOKUP JOIN`

`LOOKUP JOIN` began as a technical preview in 8.18.0, enriching ES|QL rows
with matching records from a lookup index. In 9.1.0 it accepts aliases and
mixed numeric join keys. In 9.2.0 it accepts multiple join fields, remote input,
and technical-preview expression predicates:

```esql
FROM index1
| LOOKUP JOIN lookup_index ON field1, field2
```

Search functions are rejected on non-standard index modes. In 9.1.0, remote
`ENRICH` could not follow `LOOKUP JOIN`; 9.2.0 permits that sequence. From
9.3.0, full-text functions and other Lucene-pushable conditions can operate on
lookup-index fields after a join.

### `FORK` and subqueries

Technical-preview `FORK` sends every row through multiple branches, merges the
results, and adds `_fork` (9.1.0):

```esql
FROM test
| FORK
  ( WHERE content:"fox" )
  ( WHERE content:"dog" )
| SORT _fork
```

Cross-cluster `FORK` is released in 9.3.0. In 9.4.0, `FORK` and subquery
branches no longer receive implicit limits.

### Views

Views in 9.4.0 are virtual indices whose fields come from reusable ES|QL
pipelines. `FROM` can mix indices, views, and wildcards; each view executes its
own pipeline. View CRUD is authorized as index actions, and deletion can target
multiple views. Views cannot be queried when document- or field-level security
applies.

## Full-text, inference, and vector querying

### Full-text scoring and query functions

Since 9.0.0, request `METADATA _score` to expose scores. Full-text function
disjunctions score, full-text and non-full-text conditions may share a
disjunction, and scoring is no longer snapshot-only. ES|QL also adds a
technical-preview `KQL` function, a term query, hash functions, options for
`MATCH` and `QSTR`, and non-snapshot named identifier and pattern parameters.

Technical-preview `MATCH_PHRASE` arrives in 9.1.0. Full-text functions work in
`STATS`, and `LIMIT` accepts parameters. In 9.3.0, vector-similarity functions
arrive and KNN accepts `k` and `visit_percentage`.

### Dense vectors, embedding, and reranking

ES|QL adds the `dense_vector` type, a KNN function, `v_hamming`, and
`v_magnitude` in 9.2.0. `CHUNK` and `TOP_SNIPPETS` are technical previews in
9.3.0; `CHUNK` accepts optional `chunking_settings`. `TEXT_EMBEDDING` and
`SCORE` become available in release builds, the inference command supports
cross-cluster search, and `COMPLETION` and `RERANK` have usage limits.

In 9.4.0, dense vectors support equality, inequality, `COALESCE`, arithmetic,
`SUM`, `COUNT`, `PRESENT`, and `ABSENT`. Dense-vector functions,
`TEXT_EMBEDDING`, and `RERANK` are generally available, and an MMR command
diversifies results.

## Time-series and metrics queries

### Sliding windows and timestamp ranges

Time-series aggregations accept an optional window as their second argument in
9.3.0. At first the window had to be a multiple of the `TBUCKET` or `BUCKET`
interval and otherwise defaulted to that interval. `TRANGE` filters a time
range. `DATE_TRUNC`, `BUCKET`, `TBUCKET`, and `DATE_DIFF` accept timezones;
`DATE_PARSE` accepts locale and timezone arguments.

```esql
TS metrics
| WHERE TRANGE(1h)
| STATS avg(rate(requests, 10m)) BY TBUCKET(1m), host
```

In 9.4.0, windows may be smaller than their bucket and need not be exact
multiples. Target-count `TBUCKET` may omit explicit bounds when the request
provides a timestamp range:

```esql
TS metrics | STATS AVG(RATE(requests, 15m)) BY TBUCKET(10m), host
```

### Metric and series discovery

After a `TS` source, `METRICS_INFO` returns one row per metric with data stream,
unit, metric and field types, and dimensions. `TS_INFO` returns one row per
metric-and-series pair and adds a `dimensions` JSON object (9.4.0):

```esql
TS my_data_stream
| TS_INFO
| SORT metric_name, dimensions
```

### PromQL

Technical-preview `PROMQL` in 9.4.0 executes PromQL and pipes the result into
the rest of an ES|QL query:

```esql
PROMQL index=k8s-downsampled start="2026-02-17T08:00:00Z" end="2026-02-17T09:00:00Z" step=30m avg_bytes=(avg(rate(network.total_bytes_in[30m])))
| SORT avg_bytes DESC, step
```

## Analytics, multivalue, and grouping

### Aggregation additions

ES|QL adds `STD_DEV`, spatial extent aggregation, `ST_ENVELOPE`, `ST_XMIN`,
`ST_XMAX`, `ST_YMIN`, and `ST_YMAX` in 9.0.0, plus statistics over some
`aggregate_metric_double` values. It adds `SAMPLE`, random sampling, and
`change_point` processing in 9.1.0. Technical-preview `INLINE STATS` supports
filters and cross-cluster search in 9.2.0.

For `aggregate_metric_double` in 9.4.0, non-native aggregations such as
`STD_DEV` consume the average derived from `sum` and `value_count`. Native
`min`, `max`, `sum`, `avg`, and `count` continue to use their corresponding
subfields.

### Language additions

- 9.1.0: list-form `LIKE`, arbitrary `DATE_TRUNC` intervals, `ROUND_TO`, and
  inline `::date` casts.
- 9.2.0: `ABSENT`, `ABSENT_OVER_TIME`, list-form `RLIKE`, and `MIN`/`MAX` for
  unsigned longs.
- 9.3.0: `MV_INTERSECTION`, `GROUP BY ALL`, `network_direction`, multiple
  `GROK` patterns, parameterized `LIKE`/`RLIKE`, and `TOP outputField`.
- 9.4.0: `JSON_EXTRACT`, `MV_UNION`, `MV_DIFFERENCE`, `MV_INTERSECTS`,
  `USER_AGENT`, `REGISTERED_DOMAIN`, `URI_PART`, and sparkline aggregation.

Histogram is released as a data type in 9.3.0. `MV_EXPAND` is generally
available in 9.4.0.

### Row and per-group controls

Technical-preview `LIMIT BY` limits rows per group in 9.4.0 and accepts
evaluatable grouping functions such as `BUCKET`. `SET approximate` permits
approximate analytics. `ROW` supports references to earlier fields in the same
row. Technical-preview `unmapped_fields="load"` can load partially mapped
fields.

## Date, schema, pattern, and spatial coverage

### Date and schema behavior

In 9.0.0, `date_nanos` works with `IN`, extraction, formatting, differences,
bucketing, millisecond-date comparisons, and implicit casts. `CATEGORIZE`
accepts nulls and multiple groupings. Initial unmapped-field support arrives;
`CASE`, `GREATEST`, and `LEAST` implicitly cast numerics. `RENAME` processes
sequentially like `EVAL`, and text response formats drop null columns.

In 9.4.0, `date_range` fields and timezone-aware formatting, conversion, and
date arithmetic are supported.

### Spatial and pattern coverage

Geohash, geotile, and geohex grid values arrive in 9.2.0, including use in
`ST_INTERSECTS` and `ST_DISJOINT`. In 9.4.0, spatial coverage adds
`ST_DIMENSION`, `ST_GEOMETRYTYPE`, `ST_ISEMPTY`, `ST_BUFFER`, `ST_SIMPLIFY`, and
`ST_SIMPLIFYPRESERVETOPOLOGY`.

## Request controls, output, and distributed execution

### Async and partial query handling

EQL supports partial shard results from 9.0.0. Async ES|QL can return partial
results on demand, async get supports response formatting, and in-progress
cross-cluster responses include CCS metadata. ES|QL cross-cluster querying is
generally available in 8.19.0.

ES|QL permits partial results by default in current behavior. Inspect
`is_partial` or opt out through `allow_partial_results=false`. Async result
retrieval in 9.4.0 adds `return_intermediate_results`; async task status exposes
`keep_alive`.

### Parameters, metadata, and profiling

ES|QL adds `SET`, multivalued query parameters,
`include_execution_metadata`, and `_tsid` metadata in 9.2.0. Profiling is
rejected for text response formats. Query listing/get APIs and slow logging
arrive with technical-preview `COMPLETION` in 9.1.0.

### External sources

External ES|QL sources in 9.4.0 include Azure and Google Cloud Storage plugins,
multi-endpoint Arrow Flight, and ORC alongside Parquet, CSV/TSV, and NDJSON.
Compressed inputs include GZIP, Zstandard, BZIP2, LZ4, Snappy, and Brotli.
Azure, GCS, and S3 may use anonymous `auth=none`. CSV supports bracketed
multivalue parsing and configurable error policies.

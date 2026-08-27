# ES|QL

## Joins, views, and branching

### `LOOKUP JOIN` enrichment (8.18.0)

The technical-preview `LOOKUP JOIN` combines an ES|QL result with records from
a lookup index. Use it to add reference data or correlate events.

### Join aliases, operations, and restrictions (9.1.0)

`LOOKUP JOIN` accepts aliases and mixed numeric join fields. A remote `ENRICH`
cannot follow a `LOOKUP JOIN`, and search functions are rejected on
non-standard index modes. This release also adds a technical-preview
`COMPLETION` command, slow logging, and list/get query APIs.

### Multi-field, expression, and remote joins (9.2.0)

`LOOKUP JOIN` accepts multiple fields and technical-preview expression
predicates. Input may include remote indices, and a remote `ENRICH` may now
follow the join.

```esql
FROM index1
| LOOKUP JOIN lookup_index ON field1, field2
```

### Full-text predicates after joins (9.3.0)

Full-text functions and Lucene-pushable conditions can operate on lookup-index
fields after `LOOKUP JOIN`.

### `FORK` (9.1.0)

Technical-preview `FORK` sends every input row through multiple branches,
merges their output, and adds an `_fork` discriminator.

```esql
FROM test
| FORK
  ( WHERE content:"fox" )
  ( WHERE content:"dog" )
| SORT _fork
```

Cross-cluster `FORK` is supported as of 9.3.0. In 9.4.0, `FORK` and subquery
branches no longer receive implicit limits.

### ES|QL views (9.4.0)

Views are virtual indices whose fields come from reusable ES|QL pipelines.
`FROM` can mix indices, views, and wildcards, and each named view runs its own
pipeline. View CRUD uses index-action authorization; deletion can target
multiple views. Views cannot be queried under document- or field-level
security.

## Full-text, inference, and vector processing

### Full-text scoring (9.0.0)

Use `METADATA _score` to expose scores. ES|QL scores disjunctions of full-text
functions, permits full-text and non-full-text conditions in the same
disjunction, and supports scoring outside snapshot builds.

### Query functions (9.0.0)

ES|QL adds technical-preview `KQL`, a term query, hash functions, and options
for `MATCH` and `QSTR`. Named identifier and pattern parameters are available
outside snapshot builds.

### Full-text expressions (9.1.0)

Technical-preview `MATCH_PHRASE`, list-form `LIKE`, `ROUND_TO`, `::date` inline
casts, and arbitrary `DATE_TRUNC` intervals are available. Full-text functions
work in `STATS`, and `LIMIT` accepts parameters.

### Text and inference functions (9.3.0)

Technical-preview `CHUNK` accepts optional `chunking_settings`, and
technical-preview `TOP_SNIPPETS` returns high-scoring field snippets.
`TEXT_EMBEDDING` and `SCORE` are enabled in release builds; the inference
command supports cross-cluster search; `COMPLETION` and `RERANK` have usage
limits.

### Vector and KNN support (9.2.0)

ES|QL supports `dense_vector`, a KNN function, `v_hamming` for Hamming distance,
and `v_magnitude` for vector magnitude.

### Vector and full-text querying (9.3.0)

Vector-similarity functions are available. KNN accepts `k` and
`visit_percentage`.

### Vector and reranking support (9.4.0)

Dense vectors support equality, inequality, `COALESCE`, arithmetic, `SUM`,
`COUNT`, `PRESENT`, and `ABSENT`. Dense-vector functions, `TEXT_EMBEDDING`, and
`RERANK` are generally available. ES|QL adds an MMR diversification command,
and the MMR retriever accepts `semantic_text`.

## Time-series and metric analysis

### Sliding-window aggregations (9.3.0)

Time-series aggregations accept an optional window as their second argument.
In this release, the window must be a multiple of the `TBUCKET` or `BUCKET`
interval and defaults to that interval. `TRANGE` is available; `DATE_TRUNC`,
`BUCKET`, `TBUCKET`, and `DATE_DIFF` accept timezones; `DATE_PARSE` accepts
locale and timezone arguments.

```esql
TS metrics
| WHERE TRANGE(1h)
| STATS avg(rate(requests, 10m)) BY TBUCKET(1m), host
```

### Flexible windows and counter resets (9.4.0)

Windows may be smaller than their bucket and need not be exact multiples.
Target-count `TBUCKET` may omit bounds when the request provides a timestamp
range.

```esql
TS metrics | STATS AVG(RATE(requests, 15m)) BY TBUCKET(10m), host
```

The default `aggregate` downsampling method stores a counter's first value and
auxiliary reset documents so later rate calculations preserve resets.
`last_value` retains its storage-oriented behavior.

### Metric and series discovery (9.4.0)

After `TS`, `METRICS_INFO` emits one row per metric with data stream, unit,
metric and field types, and dimensions. `TS_INFO` emits one row per metric and
series, with a `dimensions` JSON object for labels.

```esql
TS my_data_stream
| TS_INFO
| SORT metric_name, dimensions
```

### `aggregate_metric_double` semantics (9.4.0)

Non-native aggregations such as `STD_DEV` consume the average derived from the
`sum` and `value_count` subfields. Native `min`, `max`, `sum`, `avg`, and
`count` use their corresponding subfields.

## Analytics, fields, and row behavior

### Analytics and spatial functions (9.0.0)

ES|QL adds `STD_DEV`, spatial extent aggregation, `ST_ENVELOPE`, `ST_XMIN`,
`ST_XMAX`, `ST_YMIN`, and `ST_YMAX`, plus some statistics over
`aggregate_metric_double`.

### `date_nanos` coverage (9.0.0)

`date_nanos` works with `IN`, date extraction, formatting and difference,
bucketing, comparisons with millisecond dates, and implicit casting.

### Schema and output behavior (9.0.0)

`CATEGORIZE` accepts nulls and multiple groupings. Initial unmapped-field
support is present. `CASE`, `GREATEST`, and `LEAST` implicitly cast numbers.
`RENAME` processes sequentially like `EVAL`, and text formats omit null columns.

### Sampling and change detection (9.1.0)

ES|QL adds a `SAMPLE` aggregation, random sampling, and `change_point`.

### `INLINE STATS` (9.2.0)

`INLINE STATS` is available in release builds as a technical preview, with
filters and cross-cluster search.

### Monitoring, patterns, and spatial fields (9.2.0)

Use `ABSENT`, `ABSENT_OVER_TIME`, and list-form `RLIKE`. `MIN` and `MAX` support
unsigned longs. Geohash, geotile, and geohex grids work with spatial processing,
including `ST_INTERSECTS` and `ST_DISJOINT`.

### Language additions (9.3.0)

ES|QL adds `MV_INTERSECTION`, `GROUP BY ALL`, `network_direction`, multiple
patterns for `GROK`, parameterized `LIKE` and `RLIKE`, and `TOP.outputField`.
The histogram type is available in release builds.

### Functions and field coverage (9.4.0)

New functions include `JSON_EXTRACT`, `MV_UNION`, `MV_DIFFERENCE`,
`MV_INTERSECTS`, `USER_AGENT`, `REGISTERED_DOMAIN`, `URI_PART`, and a sparkline
aggregation. Spatial additions are `ST_DIMENSION`, `ST_GEOMETRYTYPE`,
`ST_ISEMPTY`, `ST_BUFFER`, `ST_SIMPLIFY`, and
`ST_SIMPLIFYPRESERVETOPOLOGY`. `date_range` fields and timezone-aware date
formatting, conversion, and arithmetic are supported.

### Group and row behavior (9.4.0)

Technical-preview `LIMIT BY` limits rows per group and accepts evaluatable
grouping functions such as `BUCKET`. `SET approximate` enables approximate
analytics. `ROW` can reference fields created earlier in the same row,
`MV_EXPAND` is generally available, and technical-preview
`unmapped_fields="load"` loads partially mapped fields.

## External sources and Prometheus

### External data sources (9.4.0)

External sources include Azure and Google Cloud Storage plugins,
multi-endpoint Arrow Flight, and ORC in addition to Parquet, CSV/TSV, and
NDJSON. Compression support includes GZIP, Zstandard, BZIP2, LZ4, Snappy, and
Brotli. Azure, GCS, and S3 sources accept anonymous `auth=none`; CSV supports
bracketed multivalues and configurable error policies.

### PromQL and Prometheus-compatible APIs (9.4.0)

Technical-preview `PROMQL` runs PromQL as a source and pipes its result into
the remainder of an ES|QL query.

```esql
PROMQL index=k8s-downsampled start="2026-02-17T08:00:00Z" end="2026-02-17T09:00:00Z" step=30m avg_bytes=(avg(rate(network.total_bytes_in[30m])))
| SORT avg_bytes DESC, step
```

The default-enabled Prometheus plugin provides technical-preview remote write
at `POST /_prometheus/api/v1/write`, plus instant-query, range-query, series,
and label endpoints below `/_prometheus/api/v1/`.

## Request, metadata, and cross-cluster behavior

### Partial query results (9.0.0)

EQL supports partial shard results. Async ES|QL can return partial results on
demand, async get supports formatting, and in-progress cross-cluster responses
include CCS metadata.

### Cross-cluster querying is generally available (8.19.0)

ES|QL cross-cluster querying is generally available rather than technical
preview.

### Request and metadata controls (9.2.0)

ES|QL adds `SET`, multivalued query parameters, and
`include_execution_metadata`; `_tsid` is available through `METADATA`.
Profiling requests are rejected for text response formats.

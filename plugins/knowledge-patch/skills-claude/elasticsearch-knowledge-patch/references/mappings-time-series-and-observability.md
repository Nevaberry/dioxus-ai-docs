# Mappings, Time Series, and Observability

## Time-series index storage

### Nested fields and synthetic source

`nested` fields are supported in `time_series` indices from 9.1.0. Synthetic
recovery source defaults on with synthetic source. Text and `match_only_text`
multi-fields are no longer stored by default for synthetic source.

In 9.4.0, time-series mode adds synthetic IDs that avoid indexing `_id`, use a
Bloom filter for ingest-time duplicate detection, and resolve ID-dependent
operations from timestamps and dimensions. New TSDB indices disable sequence
numbers. Synthetic-ID indices support nested documents and `best_compression`.

### Doc-values skippers

Since 9.3.0, fields with `index: false` and `doc_values: true` can use a sparse
doc-values index when `index.mapping.use_doc_values_skipper` is enabled. It
defaults to `false` generally and `true` for TSDB. In TSDB it replaces separate
indexes for `@timestamp`, dimensions, and `_tsid` unless disabled. LogsDB also
defaults this setting to `true` in 9.4.0.

### Mapping limits and malformed input

The nested-field limit rises to 100 in 9.3.0, while
`index.mapping.nested_parents.limit` can separately limit nested parents. A
mapping can ignore a field whose indexed name exceeds the length limit.

Since 9.4.0, `ignore_malformed` date fields no longer silently ignore object or
array values. Metadata fields no longer accept `type`, `fields`, `copy_to`, or
`boost`; `_source.mode` has no effect.

## Histogram and metric field types

### Native histograms

The `exponential_histogram` field type in 9.3.0 stores OpenTelemetry
exponential histograms and supports ES|QL `PERCENTILES`, `AVG`, `MIN`, `MAX`,
and `SUM`:

```http
PUT metrics
{"mappings":{"properties":{"latency":{"type":"exponential_histogram"}}}}
```

Elasticsearch also adds a dedicated T-Digest field type usable as a metric in
time-series data streams. OTLP now maps histograms to
`exponential_histogram` by default.

### `aggregate_metric_double`

In 9.0.0, some statistical functions can operate on
`aggregate_metric_double`. In 9.4.0, non-native aggregations such as `STD_DEV`
use the average computed from `sum` and `value_count`; native `min`, `max`,
`sum`, `avg`, and `count` use their matching subfields. The `default_metric`
mapping parameter is deprecated.

## General mapping additions

### Pattern and flattened fields

The `pattern_text` mapper is a technical preview in 9.2.0. `_ignored` records
the complete path for ignored dynamic array fields.

In 9.4.0, `flattened` fields can declare `properties`, expose passthrough mapped
subfields, and opt into accurate leaf-array handling.

### Geometry dimensions

WKT geometry can explicitly declare Z and M dimensions from 9.1.0.

### Source and vector defaults

New indices exclude vectors from `_source` by default. Reindex still includes
vectors despite transparent vector removal. Normalized `keyword` fields use
native synthetic source. LogsDB and TSDB text fields omit norms.

## LogsDB and telemetry data modes

### LogsDB sorting and routing

LogsDB can route on sort fields and configure index sorting through index
settings in 9.0.0. The field limit for OpenTelemetry metrics is 10,000.
Eligible `logs-*-*` data streams enable LogsDB by default. Data streams add
`logs.otel` and `logs.ecs` stream types in 9.4.0, while `logs` is deprecated.

### OTLP metrics endpoint

The technical-preview `/_otlp/v1/metrics` endpoint accepts OTLP metrics
directly from 9.2.0. Its histogram default is `exponential_histogram`.

### Prometheus-compatible endpoints

The default-enabled Prometheus plugin adds technical-preview remote write at
`POST /_prometheus/api/v1/write` in 9.4.0. It also exposes instant-query,
range-query, series, and label endpoints beneath `/_prometheus/api/v1/`.

Technical-preview ES|QL `PROMQL` provides a PromQL source command, while
`METRICS_INFO` and `TS_INFO` discover metric metadata and series labels.

## Ingest and indexing observability

### Indexing safeguards

Elasticsearch 9.1.0 adds `IndexingPressureMonitor`, accounts for memory used by
document expansion, and adds a maximum document-size limit. Thread-pool
telemetry includes utilization and queue-latency metrics.

### Security statistics

The `/_security/stats` endpoint in 9.2.0 reports document-level security
statistics, including DLS cache usage and hit, miss, and timing data.

### Query diagnostics

Query logging in 9.4.0 covers `_search`, ES|QL, EQL, and SQL. ES|QL query
logging itself is deprecated from 9.4.2, so avoid making new operational
dependencies on it. A search-task watchdog can log hot threads for slow
searches.

### Operational endpoints

The cat APIs add a circuit-breakers endpoint in 9.3.0. Shard-capacity health
thresholds become configurable. Ingest simulation returns effective mappings,
ignored fields, and asset timestamps where applicable.

## Counter reset preservation

The 9.4.0 aggregate downsampling method stores the first value of a counter and
auxiliary documents for detected resets. Later `RATE` calculations preserve
those resets. `last_value` retains its storage-focused behavior. Time-series
aggregation windows can be smaller than their output bucket, and target-count
`TBUCKET` can infer bounds from the request timestamp range.

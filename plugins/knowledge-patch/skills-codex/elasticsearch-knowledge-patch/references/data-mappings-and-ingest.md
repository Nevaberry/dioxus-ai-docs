# Data Streams, Mappings, and Ingest

## Failure stores and stream controls

### Enable and query failure stores (8.19.0)

Data streams can redirect documents rejected by ingest pipelines or mapping
conflicts into a failure store. Enable an existing stream through its options:

```http
PUT _data_stream/logs-test-apache/_options
{
  "failure_store": {
    "enabled": true
  }
}
```

For a new stream, set `template.data_stream_options.failure_store.enabled` in
a component or index template. Query failure indices with selectors such as
`logs-*::failures` in search or `FROM my_data_stream*::failures` in ES|QL.

### Failure-store lifecycle controls (9.1.0)

Data streams have dedicated failure-store lifecycle configuration and default
retention for failure indices. The get data stream API reports each stream's
index mode.

### Defaults for logs and telemetry (9.2.0)

New `logs-*-*`, OTel, and APM streams enable failure stores by default. When an
invalid document is routed to a new `logs-*-*` failure store, the response is
`201 Created` with `"failure_store": "used"`, not `400 Bad Request`. Existing
streams still require manual enablement.

### Stream restrictions (9.2.0)

Streams can be enabled only when no conflicting indices exist. After enabling
streams, indexing is restricted to child streams.

### New stream types and cross-cluster failure search (9.4.0)

Data streams add `logs.otel` and `logs.ecs` types. Failure-store indices can
participate in cross-cluster search.

## Ingest processors and simulation

### Parse-error source control (9.0.0)

Create, index, update, and bulk requests accept `include_source_on_error` to
control whether parse-error responses include the document source. It defaults
to `true`.

### Reroute metadata and ignored fields (9.0.0)

The reroute processor can set `type`. Simulate ingest responses report ignored
fields.

### Failure recovery and append options (9.2.0)

The append processor adds `copy_from` and an option to ignore empty values.
Use `recover_failure_document` to remediate failure-store documents.
Conditional processors can use the Fields API.

### Simulation mappings and asset timestamps (9.2.0)

The simulate ingest API accepts `merge_type` and returns the effective mapping.
Index templates, component templates, and pipelines expose creation and
modification timestamps.

### CEF parsing (9.3.0)

The `cef` processor parses Common Event Format messages into structured device
vendor, product, version, signature ID, name, severity, and extension fields.

### Analysis and ingest inputs (9.4.0)

The ICU transform analysis plugin accepts custom rulesets. The Grok processor's
`validate_only` option validates without extracting fields. Text-structure
endpoints accept nested NDJSON records.

## Mapping capabilities and guardrails

### Explicit WKT dimensions (9.1.0)

WKT geometries may explicitly declare Z and M attributes.

### Time-series and synthetic-source mappings (9.1.0)

`nested` fields are supported in `time_series` indices. Synthetic recovery
source defaults on when synthetic source is used. Text and `match_only_text`
multi-fields are no longer stored by default under synthetic source.

### Mapping additions (9.2.0)

Mappings add a technical-preview `pattern_text` field. For ignored dynamic
array fields, `_ignored` stores the full field path.

### Native histogram fields (9.3.0)

`exponential_histogram` stores OpenTelemetry exponential histograms and
supports ES|QL `PERCENTILES`, `AVG`, `MIN`, `MAX`, and `SUM`. A dedicated
T-Digest field can serve as a metric in time-series data streams.

```http
PUT metrics
{"mappings":{"properties":{"latency":{"type":"exponential_histogram"}}}}
```

### Doc-values skippers (9.3.0)

Fields with `index: false` and `doc_values: true` can use a sparse doc-values
index when `index.mapping.use_doc_values_skipper` is enabled. The setting
defaults to `false` generally and `true` for TSDB. In TSDB, skippers replace
separate indexes for `@timestamp`, dimensions, and `_tsid` unless disabled.

### Mapping guardrails (9.3.0)

The nested-field limit is 100. Use `index.mapping.nested_parents.limit` to cap
nested parents separately. A mapping can ignore a field whose indexed name
exceeds the length limit.

### Flattened fields and mapping defaults (9.4.0)

`flattened` fields support declared `properties`, passthrough mapped subfields,
and accurate leaf arrays. LogsDB defaults
`index.mapping.use_doc_values_skipper` to `true`. For date fields,
`ignore_malformed` no longer silently ignores object or array values.

## Time-series and LogsDB storage

### LogsDB and OTel data modes (9.0.0)

LogsDB can route on sort fields and configure index sorting through settings.
OTel metrics have a 10,000-field limit.

### Time-series index identity (9.4.0)

Time-series mode supports synthetic IDs that avoid indexing `_id`, use a Bloom
filter for ingest duplicate detection, and resolve ID-dependent operations
from timestamps and dimensions. New TSDB indices disable sequence numbers.
Synthetic-ID indices support nested documents and `best_compression`.

### OTLP metrics ingestion (9.2.0)

The technical-preview `/_otlp/v1/metrics` endpoint directly accepts OTLP
metrics. Its histogram default is described in
[breaking-changes.md](breaking-changes.md).

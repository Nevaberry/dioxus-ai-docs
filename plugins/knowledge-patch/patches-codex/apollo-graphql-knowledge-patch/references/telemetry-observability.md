# Router Telemetry and Observability

## Metric migration and naming

### OpenTelemetry metric replacements (router-v2-migration)

Migrate dashboards and alerts from removed Router-specific metrics:

- `apollo_router_http_request_retry_total`: use `http.client.request.duration` plus
  `http.request.resend_count` and set `default_requirement_level` to
  `recommended`;
- `apollo_router_timeout`: use status 504 on server/client request duration;
- `apollo_router_http_requests_total` and
  `apollo_router_http_request_duration_seconds`: use `http.server.request.duration` and
  `http.client.request.duration`;
- `apollo_router_session_count_total` and `apollo_router_session_count_active`:
  use `apollo.router.open_connections` (2.1+) and
  `http.server.active_requests`;
- `apollo_require_authentication_failure_count`: use server duration with 401;
- `apollo_authentication_failure_count` and
  `apollo_authentication_success_count`: use
  `apollo.router.operations.authentication.jwt` with
  `authentication.jwt.failed`;
- `apollo_router_deduplicated_subscriptions_total`: use
  `apollo.router.operations.subscriptions` with
  `subscriptions.deduplicated`;
- cache hits/misses: derive from `apollo.router.cache.hit.time` and
  `apollo.router.cache.miss.time`;
- `apollo_router_span` and `apollo_router_processing_time`: no direct
  replacement; derive overhead from
  request-span `busy_ns` and `idle_ns`.

### Router metrics use dotted names (router-v2-migration)

Remaining underscore names move to dotted OpenTelemetry namespaces, including
opened subscriptions, cache hit/size/miss time, state changes, exporter span LRU
size, and uplink fetch count/duration:

```text
apollo_router_opened_subscriptions          -> apollo.router.opened.subscriptions
apollo_router_cache_hit_time                -> apollo.router.cache.hit.time
apollo_router_cache_size                    -> apollo.router.cache.size
apollo_router_cache_miss_time               -> apollo.router.cache.miss.time
apollo_router_state_change_total            -> apollo.router.state.change.total
apollo_router_span_lru_size                 -> apollo.router.exporter.span.lru.size
apollo_router_uplink_fetch_count_total      -> apollo.router.uplink.fetch.count.total
apollo_router_uplink_fetch_duration_seconds -> apollo.router.uplink.fetch.duration.seconds
```

### Linux jemalloc metrics (2.5.0)

Linux builds with default `global-allocator` report
`apollo_router_jemalloc_active`, `apollo_router_jemalloc_allocated`,
`apollo_router_jemalloc_mapped`, `apollo_router_jemalloc_metadata`,
`apollo_router_jemalloc_resident`, and `apollo_router_jemalloc_retained`,
distinguishing allocations, active pages, metadata, resident memory, mappings,
and retained virtual mappings.

### Cardinality-overflow telemetry (2.1.0)

`apollo.router.telemetry.metrics.cardinality_overflow` increments when the
default 2,000 attribute combinations are exceeded and extra attributes are
ignored.

### Configurable metric cardinality (2.16.0)

`telemetry.exporters.metrics.common.cardinality_limit` changes the common limit;
`views[].cardinality_limit` overrides one metric. Overflow collapses into
`otel_metric_overflow="true"`; higher limits use more memory. A view lacking
`aggregation` now preserves native counter/gauge aggregation rather than
becoming a histogram; configure histogram aggregation explicitly if dashboards
need `_bucket`, `_sum`, and `_count` series. Monitor
`apollo.router.telemetry.metrics.cardinality_overflow`.

### Duration instruments honor configured units (2.8.0)

Duration instruments convert to configured `s`, `ms`, `us`, or `ns` instead of
always recording seconds. Seconds remain preferred unless the backend requires
another unit.

### Histogram buckets should cover configured timeouts (2.11.0)

Default buckets span 0.001 through 10.0 seconds. Configure
`telemetry.exporters.metrics.common.buckets` for longer timeouts or long
observations accumulate at the top boundary and appear indistinguishable.

### State-change metric event names (2.9.0)

Values in `apollo.router.state.change.total` drop `_redacted` (for example,
`updateconfiguration_redacted` becomes `updateconfiguration`); `UpdateLicense`
still appends license state.

## Built-in and custom instruments

### Active pipeline gauge (2.1.0)

`apollo.router.pipelines`, labeled by `schema.id`, optional `launch.id`, and
`config.hash`, reveals old pipelines retained by long requests/subscriptions
after reload.

### Value-completion error metrics (2.1.0)

Value-completion failures absent from the GraphQL errors array count in
`apollo.router.graphql.error` and `apollo.router.operations.error` with
`code="RESPONSE_VALIDATION_FAILED"`.

### Direct router-overhead metric (2.8.0)

Enable `apollo.router.overhead` to measure Router processing excluding subgraph
and Connector wait; coprocessor request time is currently included.

### GraphOS-only subgraph fetch histogram (2.6.0)

`telemetry.apollo.experimental_subgraph_metrics` enables an experimental
subgraph fetch histogram delivered only to GraphOS and not customizable through
third-party OpenTelemetry. Use `http.client.request.duration` for customization.

### Subgraph Insights flag renamed (2.7.0)

Rename `experimental_subgraph_metrics` to `preview_subgraph_metrics`.

### Subgraph Insights metrics are generally available (2.8.0)

Rename `preview_subgraph_metrics` to GA `telemetry.apollo.subgraph_metrics`.

### Redis cache operational metrics (2.6.0)

Stable query-plan Redis metrics are `apollo.router.cache.redis.connections`,
`apollo.router.cache.redis.command_queue_length`,
`apollo.router.cache.redis.commands_executed`,
`apollo.router.cache.redis.redelivery_count`, and
`apollo.router.cache.redis.errors`. Experimental metrics are
`experimental.apollo.router.cache.redis.network_latency_avg`,
`experimental.apollo.router.cache.redis.latency_avg`,
`experimental.apollo.router.cache.redis.request_size_avg`, and
`experimental.apollo.router.cache.redis.response_size_avg`. `metrics_interval` controls
collection and defaults to one second; experimental names or behavior may
change.

### Redis clients metric replaces connections (2.8.0)

`apollo.router.cache.redis.connections` is removed. Use
`apollo.router.cache.redis.clients`, which counts clients and has no `kind`.

### Connection acquisition telemetry (2.15.0)

`apollo.router.connection.acquire.duration` measures creation of new TCP or
Unix connections to subgraphs, Connectors, or coprocessors; pool hits are not
recorded. Attribute with `network.transport` and `subgraph.name`,
`connector.source.name`, or `coprocessor`.

### Active subgraph requests selector (2.9.0)

Custom telemetry may use `active_subgraph_requests`.

### Router request-duration selector (2.14.0)

The router-service `request_duration` selector measures elapsed time from
arrival and may drive attributes or conditions. Units are floating-point
`seconds` or integer `milliseconds`/`nanoseconds`.

## Selectors, attributes, and events

### Response selectors are split by payload part (router-v2-migration)

Replace removed `subgraph_response_body` with `subgraph_response_data` or
`subgraph_response_errors`; each treats the selected part as its JSONPath root.

### Custom metric attributes moved (router-v2-migration)

Move static attributes from `telemetry.exporters.metrics.common.attributes` to
`common.resource`; put dynamic selectors on individual instruments under
`telemetry.instrumentation.instruments`.

### Conditional logging uses telemetry events (router-v2-migration)

Replace `telemetry.exporters.logging.experimental_when_header` with conditions
on `telemetry.instrumentation.events` at router, supergraph, or subgraph
request/response stages. A subgraph condition reads the original client header
through `supergraph_request_header`.

### Router response bodies are available to telemetry (2.3.0)

Use `response_body: true` to capture a Router response body in an attribute;
consider the exposure and cardinality cost.

### Router response-error selector (2.7.0)

`response_errors` selects only GraphQL errors from a Router response, with the
errors array as JSONPath root, avoiding capture of the whole body.

### Response-error telemetry aggregates (2.16.0)

`response_errors_count` counts JSONPath matches over the error array;
`response_errors_field` evaluates per error and returns matched values as a
string array.

### Connector custom-instrument selectors (2.6.0)

Connector instruments can select `supergraph_operation_name`,
`supergraph_operation_kind`, a named `request_context`, and
`connector_on_response_error`. The last is true when `is_successful` fails or,
without that condition, status is non-200. `connector_request_mapping_problems`
and `connector_response_mapping_problems` also accept a boolean that reports any
problem.

### Outgoing HTTP header span attributes (2.8.0)

The `http_client` span can record headers added by Rhai through `request_header`
selectors.

### HTTP client attributes move spans (2.12.0)

Configured `telemetry.instrumentation.spans.http_client` attributes now attach
to `http_request` rather than `subgraph_request`; update span queries/processors.

### Outbound HTTP spans expose response status (2.11.0)

Every `http_request` span, including Router-to-subgraph requests, carries
`http.response.status_code`; unsuccessful responses also carry `error.type`.

### `http_client` span attributes have selector restrictions (2.13.0)

Attributes on `telemetry.instrumentation.spans.http_client` do not support
conditions or `static`; either causes startup failure.

### Aliases for standard router-span attributes (2.14.0)

Router spans can alias `client.name`, `client.version`, `http.route`, and
`http.request.method`; default emission is unchanged.

### Router client attributes accept selectors (2.16.0)

Standard router metric attributes `client.name` and `client.version` again
accept selectors as well as boolean/alias forms.

### `http.route` excludes the query string (2.3.0)

Router spans set `http.route` to only the matched path, preventing query-string
cardinality.

### Router-service client metadata changes reach telemetry (2.3.0)

Router-service plugins that update `apollo::telemetry::client_name` or
`apollo::telemetry::client_version` now affect subsequent spans and traces.

### Request context IDs in telemetry (2.13.0)

`context_id: true` exposes the unique request ID at router, supergraph,
subgraph, and Connector stages, allowing log/span/event correlation. Rhai
already exposes it as `request.id`.

### HTTP response-body size metrics use compressed bytes (2.13.0)

Client, subgraph, and Connector `http.client.response.body.size` and
`http.server.response.body.size` report compressed size when compression is
used, even without `Content-Length`.

### Native values in JSON logs (2.14.0)

For stdout/file JSON formatters, `expand_json_string_values: true` emits string
attributes containing valid JSON objects/arrays as native JSON. OTLP is
unchanged.

## Error telemetry

### Error codes on connector and demand-control spans (2.1.0)

Connector and demand-control error spans contain events with the GraphQL error
code.

### Connector and demand-control traces include error details (2.3.0)

GraphOS traces include original message and path in addition to code.

### Extended error telemetry preview (2.1.0)

Rename `telemetry.apollo.errors.experimental_otlp_error_metrics` to
`telemetry.apollo.errors.preview_extended_error_metrics`. Extended metrics honor
per-subgraph `send`; each
`telemetry.apollo.errors.subgraph.[all|(subgraph name)].redaction_policy` may be
`ErrorRedactionPolicy.Strict` or `ErrorRedactionPolicy.Extended`. With
`redact: true`, Extended allows `extensions.code` to reach Studio.

### Entity errors retain service attribution (2.7.0)

Apollo error metrics for `_entities` fetches identify the responsible subgraph
or Connector rather than the Router.

### Counted GraphQL errors emit code span events (2.16.0)

With `telemetry.apollo.errors.preview_extended_error_metrics: enabled`, counted subgraph, supergraph,
execution, parse, and validation errors emit events containing
`graphql.error.extensions.code`, extending Connector/demand-control coverage.

## Exporters and delivery

### Telemetry defaults changed (router-v2-migration)

Defaults are `telemetry.instrumentation.spans.mode: spec_compliant`,
`telemetry.apollo.signature_normalization_algorithm: enhanced`, and
`telemetry.apollo.metrics_reference_mode: extended`. GraphOS operation-usage
reporting over OTLP is enabled under `otlp_tracing_sampler`; replace pre-v1.61
`experimental_otlp_tracing_sampler`.

### Jaeger export moves to OTLP (router-v2-migration)

The dedicated Jaeger exporter is removed. Keep Jaeger propagation if needed but
export through OTLP; enable the collector's OTLP service on 4317 gRPC or 4318
HTTP.

### Standard OTLP endpoint environment variables are supported (2.4.0)

Router configuration honors `OTEL_EXPORTER_OTLP_ENDPOINT`,
`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, and
`OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` and fixes the default HTTP metrics path. Unencrypted values
may log spurious exporter errors even while delivery succeeds.

### Generic OTLP endpoints can override Studio export (2.11.0)

`OTEL_EXPORTER_OTLP_ENDPOINT` takes precedence over defaults and may redirect
traces away from Studio; the Router warns at startup.

### OTLP endpoint environment variables prevent startup (2.13.0)

Later Router versions refuse startup when `OTEL_EXPORTER_OTLP_ENDPOINT`,
`OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, or
`OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` is set because those variables override
built-in configuration. Remove inherited values. This supersedes earlier
warning-only behavior.

### OpenTelemetry and Zipkin exporter migration (2.13.0)

Router uses OpenTelemetry Rust 0.31, requiring updates for downstream unstable
API use. Native Zipkin export is deprecated and cannot set service name; use a
Zipkin OTLP endpoint.

### Prometheus metrics can carry resource attributes (2.4.0)

Prometheus normally publishes resources only through `target_info`. Set
`resource_selector: all` to attach configured resource attributes to every
metric; OTLP is unaffected.

### Metric renaming through OpenTelemetry views (2.8.0)

Views can rename Router instruments for platform or organizational conventions.

### Configurable delivery for realtime Apollo metrics (2.1.0)

High-cardinality realtime Studio metrics use a secondary path whose interval
follows `telemetry.apollo.batch_processor.scheduled_delay`; other Apollo metrics
stay at 60 seconds. `telemetry.apollo.batch_processor.max_export_timeout` also
controls the Apollo OTLP metric reader.

### Separate Apollo batch-processor tuning (2.7.0)

Use `tracing.batch_processor` for Apollo OTLP/usage traces,
`metrics.otlp.batch_processor` for OTLP metrics, and
`metrics.usage_reports.batch_processor` for usage-report metrics. The old
`telemetry.apollo.batch_processor` block is fallback. OTLP metric
`scheduled_delay` does not affect configuration gauge metrics.

### Per-exporter trace sampling (2.16.0)

OTLP, Zipkin, Datadog, and Apollo exporters accept independent absolute
fractions. They cannot exceed
`telemetry.exporters.tracing.common.sampler`; Datadog's setting is ignored with
agent sampling.

### Experimental HTTP transport for Apollo telemetry (2.14.0)

Apollo metrics/traces can use experimental HTTP via
`telemetry.apollo.experimental_otlp_metrics_protocol` and
`telemetry.apollo.experimental_otlp_tracing_protocol`;
gRPC remains preferred.

### Anonymous telemetry opt-out does not disable fleet detection (2.5.0)

`APOLLO_TELEMETRY_DISABLED` disables anonymous telemetry only, not identifiable
fleet-detector metrics. Do not treat it as a global disable.

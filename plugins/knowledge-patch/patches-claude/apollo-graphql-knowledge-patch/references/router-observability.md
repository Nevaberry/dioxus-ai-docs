# Apollo Router Observability and Telemetry

Use this reference when migrating metrics, configuring selectors/exporters, controlling cardinality and sampling, or interpreting Router operational signals.

## Router 2 telemetry migration

### OpenTelemetry metric replacements

For router-v2-migration, move removed Router metrics to OpenTelemetry instruments or attributes:

- `apollo_router_http_request_retry_total`: use `http.client.request.duration` with `http.request.resend_count`; set `default_requirement_level: recommended`.
- `apollo_router_timeout`: use status 504 on `http.server.request.duration` or `http.client.request.duration`.
- `apollo_router_http_requests_total` and `apollo_router_http_request_duration_seconds`: use server/client request duration.
- `apollo_router_session_count_total`: use `apollo.router.open_connections` (from 2.1.0); `apollo_router_session_count_active`: use `http.server.active_requests`.
- `apollo_require_authentication_failure_count`: use server duration status 401.
- `apollo_authentication_failure_count` and `apollo_authentication_success_count`: use `apollo.router.operations.authentication.jwt` and the presence/value of `authentication.jwt.failed`.
- `apollo_router_deduplicated_subscriptions_total`: use `apollo.router.operations.subscriptions` with `subscriptions.deduplicated`.
- Cache hit/miss counts: derive from `apollo.router.cache.hit.time` and `apollo.router.cache.miss.time`.
- `apollo_router_span` and `apollo_router_processing_time` have no direct replacement; request spans expose `busy_ns` and `idle_ns` for synthetic overhead.

### Router metrics use dotted names

For router-v2-migration, rename underscore metrics:

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

### Telemetry defaults changed

For router-v2-migration, `telemetry.instrumentation.spans.mode` defaults to `spec_compliant`, `telemetry.apollo.signature_normalization_algorithm` to `enhanced`, and `telemetry.apollo.metrics_reference_mode` to `extended`. GraphOS usage reporting via OTLP defaults on under `otlp_tracing_sampler`; replace pre-1.61 `experimental_otlp_tracing_sampler`.

### Response selectors are split by payload part

For router-v2-migration, replace removed `subgraph_response_body` with `subgraph_response_data` or `subgraph_response_errors`; each selected part is its JSONPath root.

### Custom metric attributes moved

For router-v2-migration, static metric attributes move from `telemetry.exporters.metrics.common.attributes` to `common.resource`. Put dynamic values on individual instruments under `telemetry.instrumentation.instruments`.

### Jaeger export moves to OTLP

For router-v2-migration, the `jaeger` exporter is removed. Keep Jaeger propagation if needed and export through OTLP; enable OTLP on the collector at 4317 (gRPC) or 4318 (HTTP).

### Conditional logging uses telemetry events

For router-v2-migration, replace `telemetry.exporters.logging.experimental_when_header` with conditions under `telemetry.instrumentation.events` at router, supergraph, or subgraph request/response stages. At a subgraph stage, read the original client header with `supergraph_request_header`.

## Error and request selectors

### Cardinality-overflow telemetry

Since 2.1.0, `apollo.router.telemetry.metrics.cardinality_overflow` increments when a metric batch crosses cardinality 2,000 and excess attributes are ignored.

### Value-completion error metrics

Since 2.1.0, value-completion failures absent from the GraphQL errors array count in `apollo.router.graphql.error` and `apollo.router.operations.error` with `code="RESPONSE_VALIDATION_FAILED"`.

### Error codes on connector and demand-control spans

Since 2.1.0, Connector and demand-control error spans include span events carrying their GraphQL error codes.

### Extended error telemetry preview

Since 2.1.0, rename `telemetry.apollo.errors.experimental_otlp_error_metrics` to `telemetry.apollo.errors.preview_extended_error_metrics`. Extended metrics honor subgraph `send`. `telemetry.apollo.errors.subgraph.[all|(subgraph name)].redaction_policy` accepts `ErrorRedactionPolicy.Strict` or `ErrorRedactionPolicy.Extended`; with `redact: true`, Extended permits `extensions.code` to Studio.

### Safelist logs distinguish bypassed enforcement

Since 2.3.0, unknown-operation safelist logs include `enforcement_skipped`: `false` means externally rejected, `true` means an internal operation intentionally bypassed enforcement.

### Router response bodies are available to telemetry

Since 2.3.0, the `response_body` selector can capture a Router response in an attribute. Treat it as potentially sensitive and high-cardinality.

### Connector and demand-control traces include error details

Since 2.3.0, GraphOS traces include original message and path for Connector/demand errors as well as codes.

### GraphQL error selectors are consistently boolean

Since 2.4.0, `on_graphql_error` returns `false`, not absent, when no error exists, matching `subgraph_on_graphql_error`; it works at supergraph as well as router stage.

### Router response-error selector

Since 2.7.0, `response_errors` selects only the Router response's GraphQL error array, with that array as JSONPath root, avoiding full-body capture.

### Entity errors retain service attribution

Since 2.7.0, Apollo metrics for `_entities` fetch errors include the responsible subgraph/Connector service rather than attributing them to Router.

### Active subgraph requests selector

Since 2.9.0, custom telemetry may use the documented `active_subgraph_requests` selector.

### Request context IDs in telemetry

Since 2.13.0, `context_id: true` exposes a unique request ID to router, supergraph, subgraph, and Connector instrumentation. Rhai exposes the same ID as `request.id`.

### Response-error telemetry aggregates

Since 2.16.0, `response_errors_count` counts matches from a JSONPath over the response error array, while `response_errors_field` evaluates per error and returns matching values as a string array.

### Counted GraphQL errors emit code span events

Since 2.16.0, with `telemetry.apollo.errors.preview_extended_error_metrics: enabled`, counted subgraph, supergraph, execution, parse, and validation errors emit `graphql.error.extensions.code` events, extending Connector/demand coverage.

## Operational metrics

### Active pipeline gauge

Since 2.1.0, `apollo.router.pipelines` counts active pipelines by `schema.id`, optional `launch.id`, and `config.hash`, revealing old pipelines retained by long requests/subscriptions after reload.

### Configurable delivery for realtime Apollo metrics

Since 2.1.0, high-cardinality realtime Studio metrics use a secondary path scheduled by `telemetry.apollo.batch_processor.scheduled_delay`; other Apollo metrics remain fixed at 60 seconds. `telemetry.apollo.batch_processor.max_export_timeout` also controls the Apollo OTLP metrics `PeriodicReader`.

### Router-service client metadata changes reach telemetry

Since 2.3.0, a router-service plugin's changes to `apollo::telemetry::client_name` or `apollo::telemetry::client_version` propagate to spans/traces.

### `http.route` excludes the query string

Since 2.3.0, Router spans record only the matched path in `http.route`: `/graphql?operation=value` records `/graphql`, preventing query-string-driven cardinality.

### Prometheus metrics can carry resource attributes

Since 2.4.0, Prometheus publishes resources only through `target_info` by default. `resource_selector: all` adds configured resource attributes to every Prometheus metric and does not affect OTLP.

### Open-subscription metrics identify the operation

Since 2.4.0, `apollo.router.opened.subscriptions` includes `graphql.operation.name`.

### Linux jemalloc metrics

Since 2.5.0, Linux builds with default `global-allocator` report `apollo_router_jemalloc_active`, `apollo_router_jemalloc_allocated`, `apollo_router_jemalloc_mapped`, `apollo_router_jemalloc_metadata`, `apollo_router_jemalloc_resident`, and `apollo_router_jemalloc_retained`, distinguishing application use, allocator metadata, resident/mapped memory, and retained virtual mappings.

### Anonymous telemetry opt-out does not disable fleet detection

Since 2.5.0, `APOLLO_TELEMETRY_DISABLED` disables anonymous telemetry only, not identifiable fleet-detector metrics.

### GraphOS-only subgraph fetch histogram

Since 2.6.0, `telemetry.apollo.experimental_subgraph_metrics` enables an uncustomizable fetch-duration histogram sent only to GraphOS. Use `http.client.request.duration` for third-party/customized export. This flag is superseded below.

### Redis cache operational metrics

Since 2.6.0, stable Redis cache metrics are `apollo.router.cache.redis.connections`, `apollo.router.cache.redis.command_queue_length`, `apollo.router.cache.redis.commands_executed`, `apollo.router.cache.redis.redelivery_count`, and `apollo.router.cache.redis.errors`. Experimental metrics `experimental.apollo.router.cache.redis.network_latency_avg`, `experimental.apollo.router.cache.redis.latency_avg`, `experimental.apollo.router.cache.redis.request_size_avg`, and `experimental.apollo.router.cache.redis.response_size_avg` may change. `metrics_interval` defaults to one second.

### Connector custom-instrument selectors

Since 2.6.0, Connector instruments can select `supergraph_operation_name`, `supergraph_operation_kind`, a named `request_context`, and `connector_on_response_error`. The last is true when `is_successful` fails or, without that condition, status is non-200. `connector_request_mapping_problems` and `connector_response_mapping_problems` also accept a boolean “any problem” form.

### Separate Apollo batch-processor tuning

Since 2.7.0, tune `tracing.batch_processor`, `metrics.otlp.batch_processor`, and `metrics.usage_reports.batch_processor` independently. Old `telemetry.apollo.batch_processor` values are fallback. OTLP metrics `scheduled_delay` does not affect configuration-gauge metrics.

### Subgraph Insights flag renamed

Since 2.7.0, replace `experimental_subgraph_metrics` with `preview_subgraph_metrics`.

### Duration instruments honor configured units

Since 2.8.0, duration instruments convert values to configured `s`, `ms`, `us`, or `ns` instead of always seconds. Seconds remain recommended unless the backend requires otherwise.

### Direct router-overhead metric

Since 2.8.0, enable `apollo.router.overhead` to measure Router processing excluding subgraph/Connector waits; coprocessor request time remains included.

### Metric renaming through OpenTelemetry views

Since 2.8.0, rename telemetry instruments through OpenTelemetry views to match backend indexing or organizational conventions.

### Outgoing HTTP header span attributes

Since 2.8.0, `http_client` spans can record headers added by Rhai through a `request_header` selector.

### Subgraph Insights metrics are generally available

Since 2.8.0, replace `preview_subgraph_metrics` with GA `subgraph_metrics`.

### Cache-Control telemetry selector

Since 2.9.0, `response_cache_control` exposes computed subgraph response Cache-Control values such as `max_age` to custom instruments.

### State-change metric event names

Since 2.9.0, `apollo.router.state.change.total` event names drop `_redacted` (`updateconfiguration_redacted` becomes `updateconfiguration`); `UpdateLicense` still appends license state.

### Request allocation histograms

Since 2.11.0, `apollo.router.request.memory` covers a whole request and `apollo.router.query_planner.memory` covers planning jobs, with `allocation.type` and `context`. They require Unix, `global-allocator`, and no `dhat-heap`.

### Outbound HTTP spans expose response status

Since 2.11.0, every `http_request` span, including subgraph calls, has `http.response.status_code`; unsuccessful responses also have `error.type`.

### Histogram buckets should cover configured timeouts

Since 2.11.0, default buckets range from `0.001` to `10.0` seconds. Configure `telemetry.exporters.metrics.common.buckets` to cover larger deployment timeouts or long observations collapse at the top boundary.

### Parser-complexity metrics

Since 2.12.0, `apollo.router.operations.recursion` reports parser recursion and `apollo.router.operations.lexical_tokens` reports lexical-token count.

### HTTP client attributes move spans

Since 2.12.0, configured `telemetry.instrumentation.spans.http_client` attributes attach to `http_request`, not `subgraph_request`; update span queries/processors.

### HTTP response-body size metrics use compressed bytes

Since 2.13.0, `http.client.response.body.size` and `http.server.response.body.size` consistently report compressed bytes for client, subgraph, and Connector responses, even without `Content-Length`.

### Native values in JSON logs

Since 2.14.0, stdout/file JSON formatters with `expand_json_string_values: true` emit strings containing valid JSON objects/arrays as native JSON. OTLP is unaffected.

### Router request-duration selector

Since 2.14.0, router-service `request_duration` measures arrival-to-current elapsed time for custom values/conditions in float seconds or integer milliseconds/nanoseconds.

### Streaming termination telemetry

Since 2.14.0, spans expose `apollo.subscription.end_reason` (`server_close`, `subgraph_error`, `heartbeat_delivery_failed`, `client_disconnect`, `schema_reload`, `config_reload`) and `apollo.defer.end_reason` (`completed`, `client_disconnect`). Counters are `apollo.router.operations.subscriptions.terminated.client`, `apollo.router.operations.subscriptions.rejected`, and `apollo.router.operations.subscriptions.terminated.subgraph`.

### Aliases for standard router-span attributes

Since 2.14.0, router spans can alias `client.name`, `client.version`, `http.route`, and `http.request.method` without changing default emission.

### Connection acquisition telemetry

Since 2.15.0, `apollo.router.connection.acquire.duration` measures only new TCP/Unix connections to subgraphs, Connectors, or coprocessors—not pool hits. Attribute with `network.transport` plus `subgraph.name`, `connector.source.name`, or `coprocessor`.

### Router client attributes accept selectors

Since 2.16.0, standard router metric attributes `client.name` and `client.version` again accept selectors, in addition to boolean/alias forms.

## Exporters, cardinality, and sampling

### Standard OTLP endpoint environment variables are supported

Since 2.4.0, Router initially honored `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT`, and `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`; the default HTTP metrics endpoint also received the correct path. Unencrypted endpoints could emit spurious errors despite delivery. Later releases reverse this behavior below.

### Generic OTLP endpoints can override Studio export

Since 2.11.0, `OTEL_EXPORTER_OTLP_ENDPOINT` could take precedence and redirect traces away from Studio, producing a startup warning. This is superseded below.

### OTLP endpoint environment variables prevent startup

Since 2.13.0, Router refuses startup if `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`, or `OTEL_EXPORTER_OTLP_METRICS_ENDPOINT` is set because these override built-in telemetry configuration. Remove inherited definitions.

### OpenTelemetry and Zipkin exporter migration

Since 2.13.0, Router uses OpenTelemetry Rust 0.31.0; downstream unstable API users must update. Native Zipkin export is deprecated and cannot set service name; use Zipkin's OTLP endpoint.

### `http_client` span attributes have selector restrictions

Since 2.13.0, attributes under `telemetry.instrumentation.spans.http_client` reject conditions and the `static` selector at startup.

### GraphOS OTLP exporters honor HTTP proxies

Since 2.14.0, HTTP GraphOS OTLP export honors `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`; TLS-inspecting proxies require their root CA in the Router trust store.

### Experimental HTTP transport for Apollo telemetry

Since 2.14.0, `telemetry.apollo.experimental_otlp_metrics_protocol` and `telemetry.apollo.experimental_otlp_tracing_protocol` enable HTTP transport; gRPC remains preferred.

### Configurable metric cardinality

Since 2.16.0, `telemetry.exporters.metrics.common.cardinality_limit` overrides the default 2,000 combinations and `views[].cardinality_limit` overrides one metric. Overflow collapses into `otel_metric_overflow="true"`; monitor `apollo.router.telemetry.metrics.cardinality_overflow` and remember higher limits use more memory.

A view without `aggregation` now preserves counter/gauge aggregation rather than becoming a histogram. Explicitly request histogram aggregation if dashboards need `_bucket`, `_sum`, and `_count`.

### Per-exporter trace sampling

Since 2.16.0, OTLP, Zipkin, Datadog, and Apollo exporters may set independent absolute `sampler` fractions no higher than `telemetry.exporters.tracing.common.sampler`. Datadog ignores its field when agent sampling is on.

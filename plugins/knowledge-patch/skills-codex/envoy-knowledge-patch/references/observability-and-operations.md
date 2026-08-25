# Observability and operations

Use this reference for access logs, tracing, metrics, tap, overload controls, admin endpoints, and process diagnostics.

## Access logs and formatters

### Access-log fields and controls (since 1.33.0)

New formatters expose downstream email and OtherName SANs, direct local addresses, and an upstream host name without its port: `%DOWNSTREAM_LOCAL_EMAIL_SAN%`, `%DOWNSTREAM_PEER_EMAIL_SAN%`, `%DOWNSTREAM_LOCAL_OTHERNAME_SAN%`, `%DOWNSTREAM_PEER_OTHERNAME_SAN%`, `%DOWNSTREAM_DIRECT_LOCAL_ADDRESS%`, `%DOWNSTREAM_DIRECT_LOCAL_ADDRESS_WITHOUT_PORT%`, and `%UPSTREAM_HOST_NAME_WITHOUT_PORT%`. `%COMMON_DURATION%` adds `%US_CX_BEG%`, `%US_CX_END%`, and `%US_HS_END%`, while `--skip-deprecated-logs` suppresses deprecated logs.

### Access-log formatting additions (since 1.37.0)

`COALESCE` returns the first non-null formatter result, `ComparisonFilter` supports not-equal, and full-name aliases `%REQUEST_HEADER(X?Y):Z%`, `%RESPONSE_HEADER(X?Y):Z%`, and `%RESPONSE_TRAILER(X?Y):Z%` complement `%REQ%`, `%RESP%`, and `%TRAILER%`. Other additions include the `US_RX_BODY_BEG` time point for `%COMMON_DURATION%`, `REQUESTED_SERVER_NAME`, listener-filter-chain metadata, internal-listener endpoint-ID operators, and header-byte-count attributes.

### Access-log rate limiting and OpenTelemetry export (since 1.37.0)

`ProcessRateLimitFilter` rate-limits access-log emission process-wide, and a new access logger emits configurable metrics. OpenTelemetry access logging can use HTTP and exposes top-level `http_service`, `grpc_service`, `log_name`, buffering, filter-state, and custom-tag fields; `OpenTelemetryAccessLogConfig.common_config` is deprecated.

### Access-logger statistics and network-filter logging (since 1.38.0)

Access loggers can customize their statistics, and the stats access logger supports gauges. Network filters can register access-log instances in the same manner as HTTP filters.

### Address and connection-close formatters (since 1.38.0)

`*_WITHOUT_PORT` address formatters accept a `MASK_PREFIX_LEN` argument and return masked CIDR notation. New operators include `%UPSTREAM_LOCAL_CLOSE_REASON%`, `%DOWNSTREAM_LOCAL_CLOSE_REASON%`, upstream/downstream detected close types, attempted upstream hosts and host names with or without ports, and attempted upstream connection IDs.

### Formatter migration and header-byte accounting (since 1.36.0)

The legacy array forms of `%DYNAMIC_METADATA%` and `%UPSTREAM_METADATA%`, plus `%PER_REQUEST_STATE(key)%`, are deprecated in favor of colon-separated metadata arguments and `%FILTER_STATE(key:PLAIN)%`; `envoy.reloadable_features.remove_legacy_route_formatter` remains false for now and is scheduled to flip after two release periods. New access-log operators expose decompressed header byte counts in all four upstream/downstream and sent/received directions: `%UPSTREAM_DECOMPRESSED_HEADER_BYTES_RECEIVED%`, `%DOWNSTREAM_DECOMPRESSED_HEADER_BYTES_RECEIVED%`, `%UPSTREAM_DECOMPRESSED_HEADER_BYTES_SENT%`, and `%DOWNSTREAM_DECOMPRESSED_HEADER_BYTES_SENT%`.

### Formatter-driven redirect paths (since 1.39.0)

`RedirectAction.path_rewrite` constructs redirect paths from substitution formatters and CEL expressions. It works for route redirects and custom-response redirect policies.

### Metrics and access-log exporters (since 1.38.0)

The OpenTelemetry stats sink adds `http_service` for direct OTLP/HTTP export and no longer emits empty delta counters or histograms. The contrib `envoy.stat_sinks.kafka` sink exports JSON or Metrics Service-compatible protobuf to Kafka with batching, delta-counter, label, TLS, and SASL controls.

### Structured formatter output (since 1.33.0)

The fast JSON formatter is enabled by default, always sorts properties, ignores `sort_properties`, and preserves JSON value types such as numeric durations; revert with `envoy.reloadable_features.logging_with_fast_json_formatter=false`. Metadata formatters now serialize floating-point `NaN` as `null` and `Infinity` as `inf`.

### Trace, query, file, and secret formatters (since 1.38.0)

New substitution operators include `%SPAN_ID%`, `QUERY_PARAMS` in original or decoded form, `%FILE_CONTENT(/path/to/file)%`, and `%SECRET(name)%`; custom-response local policies can also substitute `%TRACE_ID%`. `HttpService.request_headers_to_add` supports secret-retrieving formatter extensions, including in OpenTelemetry, ext-proc, and Zipkin services.

### Tracing and formatter context (since 1.35.0)

OpenTelemetry tracer configuration adds `max_cache_size` to bound cached spans before flushing. `%METADATA%` and `%CEL%` can now access virtual-host metadata when a virtual host was found but no route matched.

## Tracing

### Fluentd tracing (since 1.34.0)

The Fluentd tracer can emit spans in Fluentd Forward format.

### OpenTelemetry sampling precedence (since 1.39.0)

The OpenTelemetry tracer now honors Envoy's request-entry decision, including `overall_sampling`, even when an incoming `traceparent` or the configured OpenTelemetry sampler requests sampling. Upgrades can therefore reduce exported spans for configurations that previously let those later signals override Envoy.

### Request-ID tracing semantics (since 1.33.0)

With `pack_trace_reason=false`, Envoy no longer reads a trace reason from `x-request-id`; with it enabled, Envoy clears the trace reason in externally supplied request IDs instead of trusting it. The OpenTelemetry tracer now emits `telemetry.sdk.*` resource attributes and `otel.scope.name`/`otel.scope.version` scope attributes.

### Tracing after route refresh (since 1.36.0)

Refreshing a route now refreshes the active span's sampling decision and route decoration; disable this with `envoy.reloadable_features.trace_refresh_after_route_refresh=false`. When the default `pack_trace_reason=true` is retained, a request already marked traced cannot become untraced during that refresh.

### Tracing tag and operation formatting (since 1.37.0)

Request-header custom tags now read only HTTP headers; non-HTTP protocols must use substitution-formatter tag values, with `envoy.reloadable_features.get_header_tag_from_header_map=false` as a temporary rollback. Tracing adds formatter-backed custom-tag values and operation names, while generic proxy tags can use `%REQUEST_PROPERTY%` and `%RESPONSE_PROPERTY%`.

## Metrics and exporters

### Connection-pool and ORCA accounting (since 1.38.0)

Requests rejected because the active-request circuit breaker is exhausted now increment `upstream_rq_active_overflow`, not `upstream_rq_pending_overflow`; set `envoy.reloadable_features.skip_pending_overflow_count_on_active_rq=false` to retain the latter increment too. ORCA weighting now prefers named metrics over application utilization unless `envoy.reloadable_features.orca_weight_manager_use_named_metrics_first=false`.

### Dynamic-forward-proxy host state (since 1.35.0)

With `allow_dynamic_host_from_filter_state`, the HTTP dynamic forward proxy consults `envoy.upstream.dynamic_host` and `envoy.upstream.dynamic_port` before the Host header. The flag is disabled by default.

### Filter and endpoint observability (since 1.36.0)

The stateful-session filter emits routing counters under `http.<stat_prefix>.stateful_session.[<filter_stat_prefix>.]`, while setting `stat_prefix` enables Header-To-Metadata rule and metadata-operation counters. Locality load reports now include per-endpoint stats and metrics only for endpoints with updates; HTTP adds `upstream_rq_per_cx`, and MaxMind GeoIP adds `db_build_epoch`.

### gRPC timeout status (since 1.38.0)

The router can return gRPC `DEADLINE_EXCEEDED` (`4`) when it enforces a gRPC request timeout, avoiding the retry-prone `UNAVAILABLE` mapping from an HTTP `504`; opt in with `envoy.reloadable_features.grpc_timeout_returns_deadline_exceeded=true`.

### Load reporting, attributes, and resource statistics (since 1.34.0)

LRS now reports `locality_stats` whenever `rq_issued > 0`, reversible with `envoy.reloadable_features.report_load_with_rq_issued=false`, and `upstream.locality` exposes upstream locality. Clusters add `upstream_rq_headers_count` and `upstream_rs_headers_count` histograms when request/response size statistics are tracked, and resource monitors can report container CPU utilization in Linux Kubernetes environments.

### Metrics batching and filtering (since 1.37.0)

Metrics Service `batch_size` limits each gRPC message to that many metric families; unset or `0` retains one-message delivery. OTLP custom metric conversion adds `DropAction`, and `envoy.reloadable_features.report_load_when_rq_active_is_non_zero` keeps LRS locality reports flowing when active requests exist but none were issued in the poll cycle.

### ORCA out-of-band load reporting (since 1.39.0)

Client-side weighted round robin can open the ORCA `StreamCoreMetrics` server-streaming RPC when `enable_oob_load_report=true`. `oob_reporting_config` can override the reporting port, authority, and transport-socket match criteria, including use of a reporting sidecar.

### OTLP stat-sink enrichment (since 1.36.0)

The OTLP stat sink can reuse resource attributes produced by tracer `resource_detectors`. Its `custom_metric_conversions` can rename stats, attach static labels, and aggregate multiple stats into generated metrics.

### Per-route compression and status reporting (since 1.36.0)

Compressor per-route configuration can override the `compressor_library`, allowing routes to select different algorithms and settings. With `status_header_enabled`, the filter emits `x-envoy-compression-status` describing whether compression occurred or why it was skipped.

### Per-scope statistics controls (since 1.38.0)

Statistics can be limited per scope, and clusters can receive dynamically configured cluster-level stats matchers. A listener can replace the global matcher for its scope with `typed_filter_metadata["envoy.stats_matcher"]`; invalid metadata rejects the listener unless `envoy.reloadable_features.strict_stats_matcher_unpacked=false`.

### Programmable and chunked stats sinks (since 1.39.0)

`envoy.stat_sinks.wasm_filter` can filter, rename, tag, inject, or suppress metrics and histograms before an inner sink, while `envoy.stat_sinks.dynamic_modules` delegates metric flushing to a native module. The OpenTelemetry stats sink adds `max_data_points_per_request` to split large exports.

### Stateful-session controls (since 1.35.0)

The envelope stateful-session extension can preserve an existing session header returned by the upstream, controlled by its `mode`. Stateful-session cookies can now carry configurable cookie attributes.

### Stateful-session failure status (since 1.38.0)

In strict mode, `status_on_strict_destination_not_found` changes the default `503` returned when the requested session destination does not exist; it does not apply when that destination exists but is unhealthy.

## Tap and capture

### Effective tap sampling (since 1.39.0)

The HTTP tap filter and tap transport socket now enforce the previously ignored `tap_enabled` runtime fraction before applying their match predicate. Existing configurations may begin sampling fewer requests or connections after upgrade; `envoy.reloadable_features.tap_honor_tap_enabled=false` temporarily disables enforcement.

### Tap buffering and captured connection data (since 1.36.0)

Streamed tap data held below its configured size is now flushed after 15 seconds instead of waiting for connection close. `record_upstream_connection` controls whether an HTTP buffer trace includes upstream connection information.

## Overload and resource management

### HTTP/2 shedding and response-flush controls (since 1.36.0)

The `envoy.load_shed_points.http2_server_go_away_and_close_on_dispatch` load-shed point sends `GOAWAY`, closes the connection during HTTP/2 request dispatch, and increments `http2.goaway_sent`. Overload management adds the scalable `HttpDownstreamStreamFlush` timer, while `stream_flush_timeout` separates HTTP stream-flush timeout from stream-idle timeout.

### Overload and health-check observability (since 1.33.0)

Overload actions can scale maximum connection duration to shorten it under load. Health-check filter metrics now cover total requests, successful and failed checks, cached responses, and cluster health status.

### Overload pressure calculation (since 1.37.0)

The fixed-heap resource monitor can calculate pressure from allocated bytes divided by maximum heap size with `envoy.reloadable_features.fixed_heap_use_allocated`. The downstream-connections monitor now actually triggers configured overload actions and emits its pressure metric.

### Resource pressure controls (since 1.35.0)

A cgroup memory resource monitor reads cgroup v1 or v2 usage and limits and supports a configurable `max_memory_bytes` limit. At `envoy.load_shed_points.connection_pool_new_connection`, overload handling can refuse new pool connections and cancel their pending downstream requests.

### Runtime-adjustable fixed-heap limit (since 1.39.0)

The fixed-heap overload resource monitor adds `max_heap_size_bytes_runtime`, allowing its maximum heap size to be changed through RTDS or `/runtime_modify`.

### TCMalloc management and shrink-heap controls (since 1.38.0)

Envoy now uses TCMalloc background actions instead of its timer-based release path, removing `tcmalloc.released_by_timer`; `MemoryAllocatorManager` adds `soft_memory_limit_bytes`, `max_per_cpu_cache_size_bytes`, and `max_unfreed_memory_bytes`. The `envoy.overload_actions.shrink_heap` action accepts `ShrinkHeapConfig` with `timer_interval` (minimum `1s`, default `10s`) and `max_unfreed_memory_bytes` (default `100MB`).

## Admin and process operations

### Admin and log-file controls (since 1.37.0)

Admin `allow_paths` restricts the interface to endpoints matching configured string matchers and returns `403` for all others. Envoy also adds `/memory/tcmalloc` and `--file-flush-min-size-kb <integer>` for TCMalloc diagnostics and minimum log-file flush size.

### Admin and process-log diagnostics (since 1.39.0)

With TCMalloc, `/peak_heap_dump` emits the peak heap profile. `--log-stacktrace-single-entry` keeps a whole stack trace in one log event, `%N` adds the Envoy version to spdlog patterns, and gRPC access logging exposes `grpc_entries_flushed` and `grpc_entries_flush_failed` delivery counters.

### Container-aware worker concurrency (since 1.37.0)

On Linux, when `--concurrency` is unset, Envoy now sizes worker threads from the minimum of hardware threads, CPU affinity, and cgroup CPU limits, using conservative floor rounding. Set `ENVOY_CGROUP_CPU_DETECTION=false` to restore hardware-thread and affinity-based sizing.


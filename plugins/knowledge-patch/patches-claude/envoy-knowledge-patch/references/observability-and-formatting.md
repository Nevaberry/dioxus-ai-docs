# Observability and formatting

Use this reference for access logs, substitution formatting, tracing, metrics, statistics, taps, exporters, and diagnostic fields.

## Access-log fields and controls (since 1.33.0)

New formatters expose downstream email and OtherName SANs, direct local addresses, and an upstream host name without its port: `%DOWNSTREAM_LOCAL_EMAIL_SAN%`, `%DOWNSTREAM_PEER_EMAIL_SAN%`, `%DOWNSTREAM_LOCAL_OTHERNAME_SAN%`, `%DOWNSTREAM_PEER_OTHERNAME_SAN%`, `%DOWNSTREAM_DIRECT_LOCAL_ADDRESS%`, `%DOWNSTREAM_DIRECT_LOCAL_ADDRESS_WITHOUT_PORT%`, and `%UPSTREAM_HOST_NAME_WITHOUT_PORT%`. `%COMMON_DURATION%` adds `%US_CX_BEG%`, `%US_CX_END%`, and `%US_HS_END%`, while `--skip-deprecated-logs` suppresses deprecated logs.

## Access-log formatting additions (since 1.37.0)

`COALESCE` returns the first non-null formatter result, `ComparisonFilter` supports not-equal, and full-name aliases `%REQUEST_HEADER(X?Y):Z%`, `%RESPONSE_HEADER(X?Y):Z%`, and `%RESPONSE_TRAILER(X?Y):Z%` complement `%REQ%`, `%RESP%`, and `%TRAILER%`. Other additions include the `US_RX_BODY_BEG` time point for `%COMMON_DURATION%`, `REQUESTED_SERVER_NAME`, listener-filter-chain metadata, internal-listener endpoint-ID operators, and header-byte-count attributes.

## Access-logger statistics and network-filter logging (since 1.38.0)

Access loggers can customize their statistics, and the stats access logger supports gauges. Network filters can register access-log instances in the same manner as HTTP filters.

## Address and connection-close formatters (since 1.38.0)

`*_WITHOUT_PORT` address formatters accept a `MASK_PREFIX_LEN` argument and return masked CIDR notation. New operators include `%UPSTREAM_LOCAL_CLOSE_REASON%`, `%DOWNSTREAM_LOCAL_CLOSE_REASON%`, upstream/downstream detected close types, attempted upstream hosts and host names with or without ports, and attempted upstream connection IDs.

## CEL and substitution formatters (since 1.34.0)

CEL adds `re.extract`, `re.capture`, and `re.captureN`; when their extensions are linked, `%CEL%` and `%METADATA%` can be used directly as built-in substitution formatters. Substitution formatting also adds `QUERY_PARAM`, `CUSTOM_FLAGS`, and `PATH`, while `%RESPONSE_CODE_DETAILS%` accepts `ALLOW_WHITESPACES`; without it, whitespace is replaced by underscores.

## Effective tap sampling (since 1.39.0)

The HTTP tap filter and tap transport socket now enforce the previously ignored `tap_enabled` runtime fraction before applying their match predicate. Existing configurations may begin sampling fewer requests or connections after upgrade; `envoy.reloadable_features.tap_honor_tap_enabled=false` temporarily disables enforcement.

## Endpoint names and default-tag overrides (since 1.39.0)

`Endpoint.observability_name` distinguishes per-endpoint statistics for duplicate addresses. `allow_default_tag_overrides` lets a custom extractor in `stats_tags` replace a built-in extractor with the same tag name while retaining the other default tags.

## Filter and endpoint observability (since 1.36.0)

The stateful-session filter emits routing counters under `http.<stat_prefix>.stateful_session.[<filter_stat_prefix>.]`, while setting `stat_prefix` enables Header-To-Metadata rule and metadata-operation counters. Locality load reports now include per-endpoint stats and metrics only for endpoints with updates; HTTP adds `upstream_rq_per_cx`, and MaxMind GeoIP adds `db_build_epoch`.

## Fluentd tracing (since 1.34.0)

The Fluentd tracer can emit spans in Fluentd Forward format.

## Formatter migration and header-byte accounting (since 1.36.0)

The legacy array forms of `%DYNAMIC_METADATA%` and `%UPSTREAM_METADATA%`, plus `%PER_REQUEST_STATE(key)%`, are deprecated in favor of colon-separated metadata arguments and `%FILTER_STATE(key:PLAIN)%`; `envoy.reloadable_features.remove_legacy_route_formatter` remains false for now and is scheduled to flip after two release periods. New access-log operators expose decompressed header byte counts in all four upstream/downstream and sent/received directions: `%UPSTREAM_DECOMPRESSED_HEADER_BYTES_RECEIVED%`, `%DOWNSTREAM_DECOMPRESSED_HEADER_BYTES_RECEIVED%`, `%UPSTREAM_DECOMPRESSED_HEADER_BYTES_SENT%`, and `%DOWNSTREAM_DECOMPRESSED_HEADER_BYTES_SENT%`.

## Formatter-driven redirect paths (since 1.39.0)

`RedirectAction.path_rewrite` constructs redirect paths from substitution formatters and CEL expressions. It works for route redirects and custom-response redirect policies.

## Load reporting, attributes, and resource statistics (since 1.34.0)

LRS now reports `locality_stats` whenever `rq_issued > 0`, reversible with `envoy.reloadable_features.report_load_with_rq_issued=false`, and `upstream.locality` exposes upstream locality. Clusters add `upstream_rq_headers_count` and `upstream_rs_headers_count` histograms when request/response size statistics are tracked, and resource monitors can report container CPU utilization in Linux Kubernetes environments.

## Metrics and access-log exporters (since 1.38.0)

The OpenTelemetry stats sink adds `http_service` for direct OTLP/HTTP export and no longer emits empty delta counters or histograms. The contrib `envoy.stat_sinks.kafka` sink exports JSON or Metrics Service-compatible protobuf to Kafka with batching, delta-counter, label, TLS, and SASL controls.

## Metrics batching and filtering (since 1.37.0)

Metrics Service `batch_size` limits each gRPC message to that many metric families; unset or `0` retains one-message delivery. OTLP custom metric conversion adds `DropAction`, and `envoy.reloadable_features.report_load_when_rq_active_is_non_zero` keeps LRS locality reports flowing when active requests exist but none were issued in the poll cycle.

## New access-log and certificate metrics (since 1.35.0)

`ExtAuthzLoggingInfo` exposes `grpc_status`; TCP-tunneling access logs add `%BYTES_RECEIVED%`, `%BYTES_SENT%`, `%UPSTREAM_HEADER_BYTES_SENT%`, `%UPSTREAM_HEADER_BYTES_RECEIVED%`, `%UPSTREAM_WIRE_BYTES_SENT%`, and `%UPSTREAM_WIRE_BYTES_RECEIVED%`. TLS and CA certificate expiry epochs are emitted below `cluster.<cluster_name>.ssl.certificate.<cert_name>.` and `listener.<address>.ssl.certificate.<cert_name>.`.

## OpenTelemetry sampling precedence (since 1.39.0)

The OpenTelemetry tracer now honors Envoy's request-entry decision, including `overall_sampling`, even when an incoming `traceparent` or the configured OpenTelemetry sampler requests sampling. Upgrades can therefore reduce exported spans for configurations that previously let those later signals override Envoy.

## OTLP stat-sink enrichment (since 1.36.0)

The OTLP stat sink can reuse resource attributes produced by tracer `resource_detectors`. Its `custom_metric_conversions` can rename stats, attach static labels, and aggregate multiple stats into generated metrics.

## Overload and health-check observability (since 1.33.0)

Overload actions can scale maximum connection duration to shorten it under load. Health-check filter metrics now cover total requests, successful and failed checks, cached responses, and cluster health status.

## Per-scope statistics controls (since 1.38.0)

Statistics can be limited per scope, and clusters can receive dynamically configured cluster-level stats matchers. A listener can replace the global matcher for its scope with `typed_filter_metadata["envoy.stats_matcher"]`; invalid metadata rejects the listener unless `envoy.reloadable_features.strict_stats_matcher_unpacked=false`.

## Programmable and chunked stats sinks (since 1.39.0)

`envoy.stat_sinks.wasm_filter` can filter, rename, tag, inject, or suppress metrics and histograms before an inner sink, while `envoy.stat_sinks.dynamic_modules` delegates metric flushing to a native module. The OpenTelemetry stats sink adds `max_data_points_per_request` to split large exports.

## Prometheus protobuf and native histograms (since 1.38.0)

`/stats/prometheus` negotiates Prometheus protobuf exposition through its `Accept` header or `prom_protobuf=1`; Prometheus clients can request it with `scrape_protocols: [PrometheusProto]`. In protobuf mode, `/stats/prometheus?histogram_buckets=prometheusnative` emits native histograms.

## Request-ID tracing semantics (since 1.33.0)

With `pack_trace_reason=false`, Envoy no longer reads a trace reason from `x-request-id`; with it enabled, Envoy clears the trace reason in externally supplied request IDs instead of trusting it. The OpenTelemetry tracer now emits `telemetry.sdk.*` resource attributes and `otel.scope.name`/`otel.scope.version` scope attributes.

## Structured formatter output (since 1.33.0)

The fast JSON formatter is enabled by default, always sorts properties, ignores `sort_properties`, and preserves JSON value types such as numeric durations; revert with `envoy.reloadable_features.logging_with_fast_json_formatter=false`. Metadata formatters now serialize floating-point `NaN` as `null` and `Infinity` as `inf`.

## Tap and UDP sink behavior (since 1.35.0)

Transport tap adds a counter for streaming and buffered traces, and streamed taps can emit messages according to the configured size. The UDP sink now accepts a single message larger than 64 KB.

## Tap buffering and captured connection data (since 1.36.0)

Streamed tap data held below its configured size is now flushed after 15 seconds instead of waiting for connection close. `record_upstream_connection` controls whether an HTTP buffer trace includes upstream connection information.

## TCP proxy logging and PROXY-protocol TLVs (since 1.38.0)

TCP proxy can emit a log entry when a connection is accepted. `proxy_protocol_tlv_merge_policy` controls how configured TLVs combine with existing PROXY-protocol state through `ADD_IF_ABSENT`, `OVERWRITE_BY_TYPE_IF_EXISTS_OR_ADD`, or `APPEND_IF_EXISTS_OR_ADD`.

## TLS identity attributes and logging (since 1.39.0)

CEL adds `connection.peer_certificate_valid` to distinguish presented-and-validated certificates from untrusted certificates accepted by optional mTLS, plus `upstream.server_name` for the established upstream SNI. The same upstream SNI is available to substitution formatting as `%UPSTREAM_SERVER_NAME%`.

## Trace, query, file, and secret formatters (since 1.38.0)

New substitution operators include `%SPAN_ID%`, `QUERY_PARAMS` in original or decoded form, `%FILE_CONTENT(/path/to/file)%`, and `%SECRET(name)%`; custom-response local policies can also substitute `%TRACE_ID%`. `HttpService.request_headers_to_add` supports secret-retrieving formatter extensions, including in OpenTelemetry, ext-proc, and Zipkin services.

## Tracing after route refresh (since 1.36.0)

Refreshing a route now refreshes the active span's sampling decision and route decoration; disable this with `envoy.reloadable_features.trace_refresh_after_route_refresh=false`. When the default `pack_trace_reason=true` is retained, a request already marked traced cannot become untraced during that refresh.

## Tracing and formatter context (since 1.35.0)

OpenTelemetry tracer configuration adds `max_cache_size` to bound cached spans before flushing. `%METADATA%` and `%CEL%` can now access virtual-host metadata when a virtual host was found but no route matched.

## Tracing tag and operation formatting (since 1.37.0)

Request-header custom tags now read only HTTP headers; non-HTTP protocols must use substitution-formatter tag values, with `envoy.reloadable_features.get_header_tag_from_header_map=false` as a temporary rollback. Tracing adds formatter-backed custom-tag values and operation names, while generic proxy tags can use `%REQUEST_PROPERTY%` and `%RESPONSE_PROPERTY%`.

## Typed CEL formatting (since 1.36.0)

`%TYPED_CEL%` preserves CEL result types such as numbers, booleans, and null in typed formatting destinations like `json_format`, while `%CEL%` retains its string behavior.

## UDP proxy and tap extensions (since 1.34.0)

UDP proxy supports outlier detection unless `envoy.reloadable_features.enable_udp_proxy_outlier_detection=false`. Tap adds a UDP custom-sink extension, and transport-socket tap can control per-event connection output with `SocketTapConfig.set_connection_per_event`.

## Zipkin propagation and collector services (since 1.36.0)

Zipkin `trace_context_option=USE_B3_WITH_W3C_PROPAGATION` falls back to W3C extraction when B3 is absent and injects both formats upstream; the default remains B3-only. `collector_service` uses `HttpService` to add custom headers and accept a path or full URI, takes precedence over `collector_cluster`, `collector_endpoint`, and `collector_hostname`, and derives the `Host` header from a full URI.


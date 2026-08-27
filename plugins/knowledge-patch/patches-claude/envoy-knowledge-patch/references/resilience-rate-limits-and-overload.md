# Resilience, rate limits, and overload

Use this reference for rate limiting, retries, circuit breaking, overload actions, resource monitors, health checks, outlier detection, and pressure controls.

## Access-log rate limiting and OpenTelemetry export (since 1.37.0)

`ProcessRateLimitFilter` rate-limits access-log emission process-wide, and a new access logger emits configurable metrics. OpenTelemetry access logging can use HTTP and exposes top-level `http_service`, `grpc_service`, `log_name`, buffering, filter-state, and custom-tag fields; `OpenTelemetryAccessLogConfig.common_config` is deprecated.

## Connection-pool and ORCA accounting (since 1.38.0)

Requests rejected because the active-request circuit breaker is exhausted now increment `upstream_rq_active_overflow`, not `upstream_rq_pending_overflow`; set `envoy.reloadable_features.skip_pending_overflow_count_on_active_rq=false` to retain the latter increment too. ORCA weighting now prefers named metrics over application utilization unless `envoy.reloadable_features.orca_weight_manager_use_named_metrics_first=false`.

## Connection-pressure controls (since 1.38.0)

Listener and cluster `per_connection_buffer_high_watermark_timeout` close connections that stay above their buffer high watermark, with the timeout disabled by default. `envoy.overload_actions.close_idle_http_connections` can shed idle downstream HTTP connections, currently only for HTTP/3, and the CPU-utilization monitor now detects cgroup v1 or v2 automatically.

## HTTP health-check request bodies (since 1.36.0)

`HttpHealthCheck.send` can now carry hex-encoded text or binary bodies for `POST`, `PUT`, `PATCH`, and `OPTIONS`; configuration is rejected when a payload is combined with `GET`, `HEAD`, `DELETE`, or `TRACE`.

## HTTP/2 shedding and response-flush controls (since 1.36.0)

The `envoy.load_shed_points.http2_server_go_away_and_close_on_dispatch` load-shed point sends `GOAWAY`, closes the connection during HTTP/2 request dispatch, and increments `http2.goaway_sent`. Overload management adds the scalable `HttpDownstreamStreamFlush` timer, while `stream_flush_timeout` separates HTTP stream-flush timeout from stream-idle timeout.

## Matcher-driven outlier classification (since 1.36.0)

Cluster HTTP protocol options can configure `outlier_detection` with an HTTP matcher that classifies a response as success or error for outlier detection.

## Overload pressure calculation (since 1.37.0)

The fixed-heap resource monitor can calculate pressure from allocated bytes divided by maximum heap size with `envoy.reloadable_features.fixed_heap_use_allocated`. The downstream-connections monitor now actually triggers configured overload actions and emits its pressure metric.

## Passive degraded-host detection (since 1.38.0)

With `detect_degraded_hosts=true`, outlier detection marks a host returning `x-envoy-degraded` as degraded rather than ejecting it; degraded hosts remain in rotation at lower priority and recover with the ejection backoff algorithm.

## Rate-limit and adaptive-concurrency controls (since 1.34.0)

The HTTP local-rate-limit filter supports dynamic token buckets, while the rate-limit filter adds explicit `filter_enabled` and `filter_enforced` runtime switches. Adaptive concurrency can fix its minimum RTT with `fixed_value`.

## Rate-limit budgets and shadow mode (since 1.38.0)

`HitsAddend.is_negative_hits` and per-descriptor `RateLimitDescriptor.is_negative_hits` let a rate-limit request refill previously consumed budget. The local rate-limit filter also supports shadow mode, evaluating limits without enforcement.

## Rate-limit descriptor formatting (since 1.37.0)

Rate-limit descriptor values now support substitution formatting, allowing descriptor values to be derived from request and response context.

## Rate-limit descriptor sources and response headers (since 1.38.0)

Rate-limit descriptors can be populated from cluster metadata or cluster-locality metadata, and `RemoteAddressMatch` derives a descriptor by matching the downstream remote address against CIDRs with inversion and formatter support. Per-descriptor `x-ratelimit-*` response headers are configurable through `x_ratelimit_option`.

## Rate-limit descriptors and accounting (since 1.33.0)

Rate-limit time units now include `WEEK`; descriptor generation adds a `rate_limits` field that, when set, overrides `VirtualHost.rate_limits` and `RouteAction.rate_limits`. New controls include per-descriptor local `hits_addend`, `apply_on_stream_done` budget adjustment from request/response context, and a `query_parameters` action for HTTP and Thrift with configurable missing-parameter behavior.

## Rate-limit override sources (since 1.39.0)

The rate-limit service response-metadata namespace is configurable. Filter-level and per-route `rate_limits` now honor descriptor `limit` overrides, including dynamic-metadata sources alongside `hits_addend`, and a new static source can supply fixed `requests_per_unit` and `unit` values without metadata.

## Rate-limit response and failure controls (since 1.35.0)

Local rate limiting now returns `x-ratelimit-reset` when rejecting a request. The rate-limit filter's runtime-fractional `failure_mode_deny_percent` can override the static `failure_mode_deny` response to rate-limit-service errors.

## Resource pressure controls (since 1.35.0)

A cgroup memory resource monitor reads cgroup v1 or v2 usage and limits and supports a configurable `max_memory_bytes` limit. At `envoy.load_shed_points.connection_pool_new_connection`, overload handling can refuse new pool connections and cancel their pending downstream requests.

## Retry budgets and unconditional local limits (since 1.39.0)

Retry-budget circuit breakers add `budget_interval`, which includes new requests from the configured interval in budget calculation and defaults to `0ms` for old behavior. A local-rate-limit token bucket with `max_tokens: 0` now intentionally rejects every matching request, including default, per-descriptor, and wildcard buckets, without requiring a fill interval.

## Runtime-adjustable fixed-heap limit (since 1.39.0)

The fixed-heap overload resource monitor adds `max_heap_size_bytes_runtime`, allowing its maximum heap size to be changed through RTDS or `/runtime_modify`.

## Stateful-session failure status (since 1.38.0)

In strict mode, `status_on_strict_destination_not_found` changes the default `503` returned when the requested session destination does not exist; it does not apply when that destination exists but is unhealthy.

## Stream-complete rate-limit formatting (since 1.36.0)

Rate-limit descriptors generated after stream completion can now use substitution formatters because the filter supplies the completed request and response context.

## TCP proxy retry and early receive controls (since 1.34.0)

`backoff_options` configures the TCP proxy retry strategy. A filter-state object at `envoy.tcp_proxy.receive_before_connect` lets downstream filters read before the proxy opens its upstream connection.

## UDP proxy routing and retry backoff (since 1.33.0)

Session filters can select a cluster through per-session state key `envoy.udp_proxy.cluster`; static and dynamic clusters can coexist, with `envoy.upstream.dynamic_host` distinguishing dynamic-host sessions. `backoff_options` now configures retries when UDP is tunneled over HTTP.

## Zero-valued authorization and rate-limit timeouts (since 1.38.0)

For both the HTTP ext-authz and HTTP rate-limit filters, `timeout: 0s` now means no timeout rather than an immediate timeout.


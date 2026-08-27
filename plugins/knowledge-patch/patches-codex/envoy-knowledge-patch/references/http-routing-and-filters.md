# HTTP, routing, and filters

Use this reference for HTTP protocol behavior, routing, request/response processing, rate limiting, and filter configuration.

## External processing

### External processing transport and sampling (since 1.33.0)

The `ext_proc` filter can now exchange external-processing messages over HTTP. Its generated tracing spans no longer default to always sampled; they inherit the parent span's decision.

### External-processing composition and headers (since 1.38.0)

Multiple ext-proc filters can coexist in one chain under `envoy.reloadable_features.ext_proc_inject_data_with_state_update`, and `allow_content_length_header` lets the original `Content-Length` survive or be changed by the processor. `ExtProcLoggingInfo` adds `received_immediate_response`, while `processing_effect_lib` moves from `extensions/filters/http/ext_proc` to `extensions/filters/common/processing_effect`.

### External-processing failure and request controls (since 1.36.0)

`ext_proc` once again permits `failure_mode_allow` with `FULL_DUPLEX_STREAMED`; fail-open saves the processor's actual gRPC failure status in filter state. `status_on_error` replaces the fixed downstream `500`, and the per-route-capable `ProcessingRequestModifier` extension can alter a `ProcessingRequest` before transmission.

### External-processing failure policy (since 1.35.0)

A spurious `ext_proc` response now follows `failure_mode_allow` for fail-open versus fail-close behavior; `envoy.reloadable_features.ext_proc_fail_close_spurious_resp=false` restores the old handling temporarily. Routes can now override `failure_mode_allow`.

### External-processing lifecycle and responses (since 1.37.0)

Ext-proc closes its gRPC stream once no further processing is needed outside buffered modes; disable this with `envoy.reloadable_features.ext_proc_stream_close_optimization=false`. It also adds `StreamedImmediateResponse`, cluster-metadata forwarding, response-attribute remapping through `MappedAttributeBuilder`, and per-event mutation effects in `ExtProcLoggingInfo.processingEffects`.

### External-processing override and body modes (since 1.34.0)

For `ext_proc` mode overrides, an unset headers or trailers mode (`DEFAULT`) leaves the filter's configured processing mode unchanged, and `request_header_mode` is ignored when checking `allowed_override_modes`. The filter also adds the `FULL_DUPLEX_STREAMED` body mode.

### External-processing startup failures (since 1.39.0)

If the HTTP ext-proc filter cannot create its gRPC client, it now reports `INTERNAL` and obeys `failure_mode_allow` instead of silently ignoring the error. `envoy.reloadable_features.ext_proc_report_client_creation_error=false` restores the old behavior temporarily.

### Network external-processing controls (since 1.39.0)

A network external processor can set `ProcessingResponse.close_stream_to_ext_proc_server` to close its gRPC stream early and let later traffic bypass the filter. `receiving_namespaces` also permits untyped dynamic metadata to flow back from the processor.

## Routing, matching, and mutation

### HTTP matching and metadata limits (since 1.34.0)

`ignore_http_11_upgrade` ignores HTTP/1.1 Upgrade values selected by its matchers, and `max_metadata_size` makes the HTTP/2 metadata limit configurable. Router matching gains a filter-state matcher, and query-parameter `present_match` now observes its configured semantics unless `envoy_reloadable_features_enable_new_query_param_present_match_behavior=false`.

### Repeated-header matching semantics (since 1.39.0)

`HeaderMatcher` now evaluates separately encoded values individually across routing, virtual clusters, rate limits, retries, access logs, health checks, auth filters, and other consumers. Thus two fields containing `user` and `admin` match `admin` but no longer match `user,admin`; CEL and generic-matcher header inputs still see the comma-joined form, and `envoy.reloadable_features.match_headers_individually=false` rolls the change back.

### Request mutation and route overrides (since 1.33.0)

The Header Mutation filter can add or remove request query parameters, and `set_filter_state` supports per-route overrides. The IP-tagging filter can write tags to an alternate `ip_tag_header` instead of `x-envoy-ip-tags`.

### Route tests with dynamic metadata (since 1.36.0)

The router check tool accepts `dynamic_metadata` in test input, allowing route tests to exercise dynamic-metadata matchers.

### Router buffering, mutation, and direct-host controls (since 1.36.0)

The router adds `request_body_buffer_limit` for bodies larger than connection buffer limits; header mutation adds `remove_on_match`, and mirror policies add `request_headers_mutations` plus `host_rewrite_literal`. AsyncClient `StreamOptions.setUpstreamOverrideHost` can select an upstream host directly without load-balancer selection.

### Router local responses and trailer mutation (since 1.35.0)

Router-filter local responses now receive configured `response_headers_to_add` and `response_headers_to_remove` mutations. The Header Mutation filter can also add or remove request and response trailers.

### Router rewriting and buffering (since 1.37.0)

`RouteAction.host_rewrite` and `path_rewrite` accept substitution formatting. Route-level body-buffer limits now apply as soon as the route matches, and async HTTP retries are skipped when their buffer limit is exceeded; the latter can temporarily be reverted with `envoy.reloadable_features.http_async_client_retry_respect_buffer_limits=false`.

### URL-template wildcard matching (since 1.35.0)

The `*` and `**` URL-template operators now include a literal asterisk in their match pattern. Set `envoy.reloadable_features.uri_template_match_on_asterisk=false` for the previous behavior.

## HTTP protocol and connection lifecycle

### Explicit internal-address configuration (since 1.33.0)

RFC1918 addresses are no longer treated as internal by default; configure `internal_address_config` explicitly to retain that classification. The old behavior is temporarily available with `envoy.reloadable_features.explicit_internal_address_config=false`.

### Fair-share bandwidth and connection jitter (since 1.39.0)

The new HTTP bandwidth-share filter fairly divides request and response bandwidth among weighted tenants with filter-chain or per-route limits. `HttpConnectionManager.drain_timeout_jitter` and `HttpProtocolOptions.max_connection_duration_jitter` randomize drain and maximum-duration deadlines to stagger reconnects.

### HTTP filter-chain edge behavior (since 1.33.0)

After 1xx headers have been sent, local replies now traverse the filter chain, while an aborted encoder filter chain can no longer be continued. The respective rollback guards are `envoy.reloadable_features.local_reply_traverses_filter_chain_after_1xx` and `envoy.reloadable_features.filter_chain_aborted_can_not_continue`.

### HTTP Inspector parser default (since 1.39.0)

HTTP Inspector now uses the Balsa parser by default. `envoy.reloadable_features.http_inspector_use_balsa_parser=false` temporarily selects the old parser.

### HTTP request and protocol edge behavior (since 1.34.0)

`generate_request_id` now generates an ID for an empty as well as an absent `x-request-id`, and the HTTP/1 parser accepts leading CR or LF before a request line unless `envoy.reloadable_features.http1_balsa_allow_cr_or_lf_at_request_start=false`. HTTP/3 strips empty cookie headers by default, reversible with `envoy.reloadable_features.http3_remove_empty_cookie=false`, and `envoy.reloadable_features.http2_use_oghttp2` now defaults to true.

### HTTP reset and early-CONNECT handling (since 1.37.0)

HTTP resets now use `INTERNAL_ERROR` instead of `NO_ERROR` by default, and upstream protocol-error reasons are ignored rather than propagated downstream; the temporary rollback guards are `envoy.reloadable_features.reset_with_error` and `envoy.reloadable_features.reset_ignore_upstream_reason`. The `envoy.reloadable_features.reject_early_connect_data` guard is removed, so early data sent before a successful `CONNECT` response is now controlled per router with `reject_connect_request_early_data`.

### HTTP/1 parsing and generated Keep-Alive headers (since 1.38.0)

Strict HTTP/1 chunk parsing is available behind the disabled-by-default `envoy.reloadable_features.strict_chunk_parsing` guard. A `Keep-Alive` response header deliberately added through `response_headers_to_add` is now preserved, while upstream-provided copies are stripped; the temporary guard is `envoy.reloadable_features.preserve_downstream_keepalive`.

### HTTP/1.1 proxy CONNECT formatting (since 1.36.0)

The HTTP/1.1 proxy transport socket now sends RFC 9110 `CONNECT` requests with a `Host` header by default and prefers `hostname:port` over `IP:port` when endpoint metadata provides a hostname. Set `envoy.reloadable_features.http_11_proxy_connect_legacy_format=true` to temporarily restore the headerless format.

### HTTP/2 cookie and reset-rate controls (since 1.39.0)

`envoy.reloadable_features.http2_max_cookies_size_in_kb` sets a limit for the reassembled Cookie header, with no limit by default. Server-side nghttp2 connections also expose `Http2ProtocolOptions.stream_reset_burst` and `stream_reset_rate` for the Rapid Reset token bucket; defaults remain a burst of 1,000 and 33 resets per second.

### HTTP/2 reset propagation (since 1.33.0)

Sending an HTTP/2 `RST_STREAM` now propagates codec reset events. This can temporarily be disabled with `envoy.reloadable_features.http2_propagate_reset_events=false`.

### In-place watched-directory updates (since 1.39.0)

`WatchedDirectory.watch_modify=true` subscribes to in-place `IN_MODIFY` events as well as atomic `IN_MOVED_TO` replacements. This lets direct certificate-file writes trigger SDS rotation; the default remains rename-only watching.

### Mixed literal and variable URI segments (since 1.39.0)

URI-template matching and rewriting now accepts variables embedded beside literals, such as `/api/v{version}/users/{id}.json`. The behavior is enabled by default through `envoy.reloadable_features.uri_template_mixed_variable_literals`.

### Passive degraded-host detection (since 1.38.0)

With `detect_degraded_hosts=true`, outlier detection marks a host returning `x-envoy-degraded` as degraded rather than ejecting it; degraded hosts remain in rotation at lower priority and recover with the ejection backoff algorithm.

### Prometheus protobuf and native histograms (since 1.38.0)

`/stats/prometheus` negotiates Prometheus protobuf exposition through its `Accept` header or `prom_protobuf=1`; Prometheus clients can request it with `scrape_protocols: [PrometheusProto]`. In protobuf mode, `/stats/prometheus?histogram_buckets=prometheusnative` emits native histograms.

### Protocol input-limit hardening (since 1.39.0)

HTTP/2 reassembled cookies now count toward `mutable_max_request_headers_kb` and `max_headers_count`, with oversized streams reset; the rollback is `envoy.reloadable_features.http2_include_cookies_in_limits=false`. JSON nesting is capped at 1,000 levels unless `envoy.reloadable_features.limit_json_parser_nesting_depth=false` relaxes it to 10,000, and overlong combined PROXY-protocol TLVs are removed unless `envoy.reloadable_features.proxy_protocol_remove_too_long_tlvs=false`.

### Safer HTTP/2 defaults (since 1.36.0)

The default maximum concurrent streams drops from `2147483647` to `1024`, the initial stream window from `256MiB` to `16MiB`, and the initial connection window from `256MiB` to `24MiB`. `envoy.reloadable_features.safe_http2_options=false` temporarily restores the old defaults.

### Upstream failure-detail disclosure (since 1.39.0)

HTTP responses no longer expose the upstream transport failure reason, such as a certificate-validation error, in their body; the value remains available through `%UPSTREAM_TRANSPORT_FAILURE_REASON%`. Set `envoy.reloadable_features.hide_transport_failure_reason_in_response_body=false` only to restore the prior disclosure temporarily.

### Zipkin propagation and collector services (since 1.36.0)

Zipkin `trace_context_option=USE_B3_WITH_W3C_PROPAGATION` falls back to W3C extraction when B3 is absent and injects both formats upstream; the default remains B3-only. `collector_service` uses `HttpService` to add custom headers and accept a path or full URI, takes precedence over `collector_cluster`, `collector_endpoint`, and `collector_hostname`, and derives the `Host` header from a full URI.

## Rate limiting, retries, and traffic policy

### Rate-limit and adaptive-concurrency controls (since 1.34.0)

The HTTP local-rate-limit filter supports dynamic token buckets, while the rate-limit filter adds explicit `filter_enabled` and `filter_enforced` runtime switches. Adaptive concurrency can fix its minimum RTT with `fixed_value`.

### Rate-limit budgets and shadow mode (since 1.38.0)

`HitsAddend.is_negative_hits` and per-descriptor `RateLimitDescriptor.is_negative_hits` let a rate-limit request refill previously consumed budget. The local rate-limit filter also supports shadow mode, evaluating limits without enforcement.

### Rate-limit descriptor formatting (since 1.37.0)

Rate-limit descriptor values now support substitution formatting, allowing descriptor values to be derived from request and response context.

### Rate-limit descriptor sources and response headers (since 1.38.0)

Rate-limit descriptors can be populated from cluster metadata or cluster-locality metadata, and `RemoteAddressMatch` derives a descriptor by matching the downstream remote address against CIDRs with inversion and formatter support. Per-descriptor `x-ratelimit-*` response headers are configurable through `x_ratelimit_option`.

### Rate-limit descriptors and accounting (since 1.33.0)

Rate-limit time units now include `WEEK`; descriptor generation adds a `rate_limits` field that, when set, overrides `VirtualHost.rate_limits` and `RouteAction.rate_limits`. New controls include per-descriptor local `hits_addend`, `apply_on_stream_done` budget adjustment from request/response context, and a `query_parameters` action for HTTP and Thrift with configurable missing-parameter behavior.

### Rate-limit override sources (since 1.39.0)

The rate-limit service response-metadata namespace is configurable. Filter-level and per-route `rate_limits` now honor descriptor `limit` overrides, including dynamic-metadata sources alongside `hits_addend`, and a new static source can supply fixed `requests_per_unit` and `unit` values without metadata.

### Rate-limit response and failure controls (since 1.35.0)

Local rate limiting now returns `x-ratelimit-reset` when rejecting a request. The rate-limit filter's runtime-fractional `failure_mode_deny_percent` can override the static `failure_mode_deny` response to rate-limit-service errors.

### Stream-complete rate-limit formatting (since 1.36.0)

Rate-limit descriptors generated after stream completion can now use substitution formatters because the filter supplies the completed request and response context.

### Zero-valued authorization and rate-limit timeouts (since 1.38.0)

For both the HTTP ext-authz and HTTP rate-limit filters, `timeout: 0s` now means no timeout rather than an immediate timeout.

## Body, compression, and response filters

### Compression exclusions (since 1.34.0)

The Compressor filter's `uncompressible_response_codes` lists response status codes for which compression must be skipped.

### HTTP proxy, compression, and header-size controls (since 1.38.0)

The HTTP/1.1 proxy transport socket can use a configured default proxy address when endpoint metadata provides none. Compressor `weaken_etag_on_compress` weakens strong ETags instead of removing them and takes precedence over `disable_on_etag_header`; without weakening, strong-ETag removal now also covers two-character values, while HTTP/2 `max_header_field_size_kb` raises the default 64-KiB nghttp2 limit for a single wire-encoded HPACK field.

### Request-aware custom responses and sub-filter chains (since 1.39.0)

The custom-response filter can now match request properties such as `Accept` as well as response status and headers. A new HTTP filter-chain filter places multiple named subchains in one main-chain slot and supports per-route selection among them.

## Sessions, mirroring, and health checks

### Streaming and sampled shadow requests (since 1.33.0)

Shadow requests now stream alongside the original request, allowing bodies larger than the buffer limit but permitting shadow traffic for requests later cancelled; set `envoy.reloadable_features.streaming_shadow=false` to revert. Unless a shadow policy specifies trace sampling, it now inherits the original request's decision; the rollback guard is `envoy.reloadable_features.shadow_policy_inherit_trace_sampling`.


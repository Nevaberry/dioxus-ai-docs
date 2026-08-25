# HTTP routing and filters

Use this reference for HTTP codec behavior, route matching and rewriting, filter-chain semantics, mutation, compression, mirroring, and custom responses.

## Compression exclusions (since 1.34.0)

The Compressor filter's `uncompressible_response_codes` lists response status codes for which compression must be skipped.

## Direct-response and JSON metadata overrides (since 1.37.0)

`DirectResponseAction.body_format` applies substitution formatting to direct-response bodies. The JSON-to-Metadata HTTP filter now accepts per-route configuration so routes can use different request- or response-body extraction rules.

## Explicit internal-address configuration (since 1.33.0)

RFC1918 addresses are no longer treated as internal by default; configure `internal_address_config` explicitly to retain that classification. The old behavior is temporarily available with `envoy.reloadable_features.explicit_internal_address_config=false`.

## File-backed IP tags (since 1.39.0)

The HTTP IP-tagging filter can load tag definitions from a YAML or JSON file-backed `DataSource`. Supplying `watched_directory` dynamically reloads file changes.

## Filter state, CEL, and address matching (since 1.33.0)

CEL gains `upstream.request_attempt_count`, `upstream.cx_pool_ready_duration`, `xds.virtual_host_name`, and `xds.virtual_host_metadata`; ext-authz exposes `latency_us`, `bytesSent`, and `bytesReceived`, and SNI dynamic forward proxy stores its resolved address as `envoy.stream.upstream_address`. `FilterStateMatcher` adds `ip_range` plus an `AddressMatcher` for matching filter-state IP values against CIDR ranges.

## Filter-state update timing (since 1.38.0)

Listener filtering can update filter state, the network Set Filter State filter adds `on_downstream_data` for values created after the first downstream bytes arrive, and the HTTP Set Filter State filter adds `clear_route_cache` for routing that depends on newly written state.

## Filter-state, local-reply, and CEL matching (since 1.38.0)

`FilterStateInput.field` matches a field from a composite filter-state object through `getField()` instead of its serialized form, and a new matcher input distinguishes Envoy local replies from upstream responses. CEL expressions that refer to response-path data during request processing are now reevaluated when the response data exists unless `envoy.reloadable_features.enable_cel_response_path_matching=false`.

## Graceful reverse-tunnel draining (since 1.39.0)

`enable_drain_with_goaway` makes a reverse-tunnel initiator replace a tunnel when its peer sends GOAWAY while allowing in-flight streams to finish. Reverse-connection clusters can also opt into a drain-aware upstream HTTP/2 codec through `typed_extension_protocol_options`, allowing peers to fail over before existing tunnels close.

## gRPC timeout status (since 1.38.0)

The router can return gRPC `DEADLINE_EXCEEDED` (`4`) when it enforces a gRPC request timeout, avoiding the retry-prone `UNAVAILABLE` mapping from an HTTP `504`; opt in with `envoy.reloadable_features.grpc_timeout_returns_deadline_exceeded=true`.

## HTTP filter-chain edge behavior (since 1.33.0)

After 1xx headers have been sent, local replies now traverse the filter chain, while an aborted encoder filter chain can no longer be continued. The respective rollback guards are `envoy.reloadable_features.local_reply_traverses_filter_chain_after_1xx` and `envoy.reloadable_features.filter_chain_aborted_can_not_continue`.

## HTTP Inspector parser default (since 1.39.0)

HTTP Inspector now uses the Balsa parser by default. `envoy.reloadable_features.http_inspector_use_balsa_parser=false` temporarily selects the old parser.

## HTTP matching and metadata limits (since 1.34.0)

`ignore_http_11_upgrade` ignores HTTP/1.1 Upgrade values selected by its matchers, and `max_metadata_size` makes the HTTP/2 metadata limit configurable. Router matching gains a filter-state matcher, and query-parameter `present_match` now observes its configured semantics unless `envoy_reloadable_features_enable_new_query_param_present_match_behavior=false`.

## HTTP proxy, compression, and header-size controls (since 1.38.0)

The HTTP/1.1 proxy transport socket can use a configured default proxy address when endpoint metadata provides none. Compressor `weaken_etag_on_compress` weakens strong ETags instead of removing them and takes precedence over `disable_on_etag_header`; without weakening, strong-ETag removal now also covers two-character values, while HTTP/2 `max_header_field_size_kb` raises the default 64-KiB nghttp2 limit for a single wire-encoded HPACK field.

## HTTP request and protocol edge behavior (since 1.34.0)

`generate_request_id` now generates an ID for an empty as well as an absent `x-request-id`, and the HTTP/1 parser accepts leading CR or LF before a request line unless `envoy.reloadable_features.http1_balsa_allow_cr_or_lf_at_request_start=false`. HTTP/3 strips empty cookie headers by default, reversible with `envoy.reloadable_features.http3_remove_empty_cookie=false`, and `envoy.reloadable_features.http2_use_oghttp2` now defaults to true.

## HTTP reset and early-CONNECT handling (since 1.37.0)

HTTP resets now use `INTERNAL_ERROR` instead of `NO_ERROR` by default, and upstream protocol-error reasons are ignored rather than propagated downstream; the temporary rollback guards are `envoy.reloadable_features.reset_with_error` and `envoy.reloadable_features.reset_ignore_upstream_reason`. The `envoy.reloadable_features.reject_early_connect_data` guard is removed, so early data sent before a successful `CONNECT` response is now controlled per router with `reject_connect_request_early_data`.

## HTTP/1 parsing and generated Keep-Alive headers (since 1.38.0)

Strict HTTP/1 chunk parsing is available behind the disabled-by-default `envoy.reloadable_features.strict_chunk_parsing` guard. A `Keep-Alive` response header deliberately added through `response_headers_to_add` is now preserved, while upstream-provided copies are stripped; the temporary guard is `envoy.reloadable_features.preserve_downstream_keepalive`.

## HTTP/2 cookie and reset-rate controls (since 1.39.0)

`envoy.reloadable_features.http2_max_cookies_size_in_kb` sets a limit for the reassembled Cookie header, with no limit by default. Server-side nghttp2 connections also expose `Http2ProtocolOptions.stream_reset_burst` and `stream_reset_rate` for the Rapid Reset token bucket; defaults remain a burst of 1,000 and 33 resets per second.

## HTTP/2 reset propagation (since 1.33.0)

Sending an HTTP/2 `RST_STREAM` now propagates codec reset events. This can temporarily be disabled with `envoy.reloadable_features.http2_propagate_reset_events=false`.

## HTTP/3 QPACK control (since 1.34.0)

`envoy_v3_api_field_extensions.upstreams.http.v3.Http3ProtocolOptions.disable_qpack` experimentally disables QPACK compression.

## HTTP/3 validation and flow control (since 1.35.0)

Envoy validates HTTP/3 pseudo-headers by default; `envoy.restart_features.validate_http3_pseudo_headers=false` disables it. Experimental `disable_connection_flow_control_for_streams` lets multiplexed streams make progress independently without connection-level flow control.

## Mixed literal and variable URI segments (since 1.39.0)

URI-template matching and rewriting now accepts variables embedded beside literals, such as `/api/v{version}/users/{id}.json`. The behavior is enabled by default through `envoy.reloadable_features.uri_template_mixed_variable_literals`.

## Per-route compression and status reporting (since 1.36.0)

Compressor per-route configuration can override the `compressor_library`, allowing routes to select different algorithms and settings. With `status_header_enabled`, the filter emits `x-envoy-compression-status` describing whether compression occurred or why it was skipped.

## Prefix-map fallback (since 1.35.0)

When a longer `prefix_match_map` prefix reaches a subtree with no action, matching now resumes at shorter prefixes, like `matcher_list`. Set `envoy.reloadable_features.prefix_map_matcher_resume_after_subtree_miss=false` temporarily, or give each subtree an `on_no_match` action, to retain the old behavior.

## Protocol input-limit hardening (since 1.39.0)

HTTP/2 reassembled cookies now count toward `mutable_max_request_headers_kb` and `max_headers_count`, with oversized streams reset; the rollback is `envoy.reloadable_features.http2_include_cookies_in_limits=false`. JSON nesting is capped at 1,000 levels unless `envoy.reloadable_features.limit_json_parser_nesting_depth=false` relaxes it to 10,000, and overlong combined PROXY-protocol TLVs are removed unless `envoy.reloadable_features.proxy_protocol_remove_too_long_tlvs=false`.

## Repeated-header matching semantics (since 1.39.0)

`HeaderMatcher` now evaluates separately encoded values individually across routing, virtual clusters, rate limits, retries, access logs, health checks, auth filters, and other consumers. Thus two fields containing `user` and `admin` match `admin` but no longer match `user,admin`; CEL and generic-matcher header inputs still see the comma-joined form, and `envoy.reloadable_features.match_headers_individually=false` rolls the change back.

## Request mutation and route overrides (since 1.33.0)

The Header Mutation filter can add or remove request query parameters, and `set_filter_state` supports per-route overrides. The IP-tagging filter can write tags to an alternate `ip_tag_header` instead of `x-envoy-ip-tags`.

## Request-aware custom responses and sub-filter chains (since 1.39.0)

The custom-response filter can now match request properties such as `Accept` as well as response status and headers. A new HTTP filter-chain filter places multiple named subchains in one main-chain slot and supports per-route selection among them.

## Reverse-tunnel tenant isolation (since 1.38.0)

`enable_tenant_isolation` scopes cached reverse-tunnel sockets by `<tenant>@<node>` and `<tenant>@<cluster>` and rejects handshake components that already contain `@`.

## Route tests with dynamic metadata (since 1.36.0)

The router check tool accepts `dynamic_metadata` in test input, allowing route tests to exercise dynamic-metadata matchers.

## Router buffering, mutation, and direct-host controls (since 1.36.0)

The router adds `request_body_buffer_limit` for bodies larger than connection buffer limits; header mutation adds `remove_on_match`, and mirror policies add `request_headers_mutations` plus `host_rewrite_literal`. AsyncClient `StreamOptions.setUpstreamOverrideHost` can select an upstream host directly without load-balancer selection.

## Router local responses and trailer mutation (since 1.35.0)

Router-filter local responses now receive configured `response_headers_to_add` and `response_headers_to_remove` mutations. The Header Mutation filter can also add or remove request and response trailers.

## Router rewriting and buffering (since 1.37.0)

`RouteAction.host_rewrite` and `path_rewrite` accept substitution formatting. Route-level body-buffer limits now apply as soon as the route matches, and async HTTP retries are skipped when their buffer limit is exceeded; the latter can temporarily be reverted with `envoy.reloadable_features.http_async_client_retry_respect_buffer_limits=false`.

## Safer HTTP/2 defaults (since 1.36.0)

The default maximum concurrent streams drops from `2147483647` to `1024`, the initial stream window from `256MiB` to `16MiB`, and the initial connection window from `256MiB` to `24MiB`. `envoy.reloadable_features.safe_http2_options=false` temporarily restores the old defaults.

## Stateful-session controls (since 1.35.0)

The envelope stateful-session extension can preserve an existing session header returned by the upstream, controlled by its `mode`. Stateful-session cookies can now carry configurable cookie attributes.

## Streaming and sampled shadow requests (since 1.33.0)

Shadow requests now stream alongside the original request, allowing bodies larger than the buffer limit but permitting shadow traffic for requests later cancelled; set `envoy.reloadable_features.streaming_shadow=false` to revert. Unless a shadow policy specifies trace sampling, it now inherits the original request's decision; the rollback guard is `envoy.reloadable_features.shadow_policy_inherit_trace_sampling`.

## Upstream failure-detail disclosure (since 1.39.0)

HTTP responses no longer expose the upstream transport failure reason, such as a certificate-validation error, in their body; the value remains available through `%UPSTREAM_TRANSPORT_FAILURE_REASON%`. Set `envoy.reloadable_features.hide_transport_failure_reason_in_response_body=false` only to restore the prior disclosure temporarily.

## URL-template wildcard matching (since 1.35.0)

The `*` and `**` URL-template operators now include a literal asterisk in their match pattern. Set `envoy.reloadable_features.uri_template_match_on_asterisk=false` for the previous behavior.


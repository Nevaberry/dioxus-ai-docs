# Extensions and programmability

Use this reference when writing or operating Lua, Wasm, native dynamic modules, CEL, filter-state, and custom extension code.

## Dynamic modules

### Dynamic modules and Go extension lifecycle (since 1.34.0)

Dynamic modules introduce runtime loading of shared libraries. The Go SDK adds a `SecretManager` interface for generic secrets and calls `Destroy` when an HTTP filter configuration is deleted; configurations implement `github.com/envoyproxy/envoy/contrib/golang/common/go/api.Config`.

### Dynamic-module body and asynchronous APIs (since 1.37.0)

The dynamic-module ABI now supports streaming body manipulation, header addition, and body-size retrieval. Modules can open streaming HTTP callouts with `start_http_stream`, and HTTP-filter configuration gains a main-thread scheduler for asynchronous initialization and background work.

### Dynamic-module bootstrap and process services (since 1.38.0)

Bootstrap modules gain init-manager participation, timers, custom admin handlers, metrics, host-membership notifications, and server drain/shutdown lifecycle callbacks, while `envoy_dynamic_module_callback_is_validation_mode` lets modules detect configuration validation. Process-wide function and shared-data registries enable cross-module coordination, while the Rust SDK can register any combination of HTTP, network, listener, UDP-listener, and bootstrap filters or multiple named access loggers from one module.

### Dynamic-module extension families (since 1.38.0)

Dynamic modules can now implement tracers, input matchers, TLS certificate validators, custom clusters, load-balancing policies, and upstream HTTP-to-TCP bridges. Certificate validators can exchange string filter state, and dynamic HTTP and network filters can use registered factories to exchange typed filter-state objects with built-in filters.

### Dynamic-module listener and network APIs (since 1.38.0)

Listener modules gain socket writes and closes, HTTP callouts, socket/SNI/ALPN/JA3/JA4/TLS inspection, and listener add/update/removal callbacks. Network modules gain connection-state, half-close, buffer-limit, watermark, and read-flow-control callbacks; their buffers remain accessible after read/write callbacks, and they can query cluster host counts.

### Dynamic-module load-balancer host APIs (since 1.38.0)

Load-balancer modules add O(1) host-health lookup through `get_host_health_by_address` plus membership-update events that expose added or removed host addresses.

### Dynamic-module loading and ABI compatibility (since 1.38.0)

`DynamicModuleConfig.module.local.filename` loads a module from an absolute local `.so` path, while `module.remote` asynchronously fetches a SHA-256-verified module, caches it by digest, and fails open by omitting the filter if fetching fails; `nack_on_cache_miss` instead rejects an uncached remote configuration while fetching in the background. Factories now pass `google.protobuf.Struct` configuration as JSON, the extended ABI allows a module built with one SDK release such as 1.38 to load in the next Envoy release, and load-balancer callback `cluster_lb_async_host_selection_complete` now takes `envoy_dynamic_module_type_module_buffer` for its details value.

### Dynamic-module logging and metrics (since 1.36.0)

Dynamic modules gain a logging ABI that writes to Envoy's standard log under the `dynamic_modules` ID, with Rust helpers such as `envoy_log_info`. Their API also adds counters, gauges, histograms, and vector variants.

### Dynamic-module metrics and failure isolation (since 1.38.0)

`DynamicModuleConfig.metrics_namespace` controls the Prometheus prefix for module metrics, with `envoy.reloadable_features.dynamic_modules_strip_custom_stat_prefix=true` restoring the legacy output; load-balancer and bootstrap modules can define and update custom metrics. The Rust SDK's opt-in `CatchUnwind` wrapper converts callback panics into fail-closed request, stream, or connection errors instead of aborting Envoy.

### Dynamic-module request and worker APIs (since 1.39.0)

Dynamic-module load balancers can read host stats and filter state, write request dynamic metadata and filter state, and publish opaque main-thread state to every worker through worker slots and events. Network and listener modules gain typed attribute access, modules can emit metrics from configuration/background contexts, and configuration-load failures now produce tagged `dynamic_modules.*` counters that survive rejected listener updates.

### Expanded dynamic-module extension points (since 1.37.0)

Dynamic modules can implement network, listener, UDP-listener, bootstrap, and access-logger extensions, and `load_globally=true` loads a module globally. Name-based loading uses `ENVOY_DYNAMIC_MODULES_SEARCH_PATH` when set, otherwise the working directory, before standard library paths.

### New dynamic-module extension families (since 1.39.0)

Dynamic modules can now implement substitution formatters, downstream or upstream transport sockets, active health checkers, and stats sinks. Transport-socket modules perform and transform raw connection I/O and can support STARTTLS; health-check modules report standard per-host results, while stats-sink modules receive flush snapshots and histogram samples.

## Wasm

### Lua and Wasm control APIs (since 1.37.0)

Lua `streamInfo():drainConnectionUponCompletion()` marks the connection for HTTP/1.1 close or HTTP/2 and HTTP/3 `GOAWAY`. Wasm adds a `sign` foreign function, and foreign functions now execute on the SDK-selected effective context unless `envoy.reloadable_features.wasm_use_effective_ctx_for_foreign_functions=false`.

### Wasm failure recovery and Go plugins (since 1.33.0)

Wasm VMs can reload after runtime errors through `failure_policy`, with `FAIL_RELOAD` now the default policy. Envoy also supports plugins built with `github.com/proxy-wasm/proxy-wasm-go-sdk` and Go 1.24 or newer.

### Wasm header suspension (since 1.35.0)

When `allow_on_headers_stop_iteration` opts in, Wasm plugins may return `StopIteration` from `onRequestHeader` and `onResponseHeader`; the existing default behavior is unchanged.

### Wasm instance identity and metric scope (since 1.39.0)

Listener metadata no longer contributes to a downstream HTTP or network Wasm plugin's unique key, so listeners with otherwise identical configuration share a plugin instance; use distinct names or root/VM IDs when isolation is required. Upstream HTTP Wasm custom metrics also move from cluster scope to the server-wide root scope unless `envoy.reloadable_features.upstream_wasm_filter_uses_root_scope=false`, and changing only `vm_config.environment_variables` now correctly recreates the VM.

### Wasm routing and xDS properties (since 1.33.0)

For ABI versions newer than 0.2.1, changing request headers no longer clears the route cache by default; plugins can explicitly invoke the new `clear_route_cache` foreign function. Deprecated xDS properties were removed from `get_property`, so plugins must use the `xds` attributes.

## Lua

### Lua extension APIs (since 1.33.0)

Logging functions are now available on every Lua object, and stream information adds `downstreamDirectLocalAddress()` and `routeName()`. Lua can also call `parsedSubjectPeerCertificate()`, query clusters for the current request or connection, and select the current request's upstream with `setUpstreamOverrideHost()`.

### Lua filter-state and routing metadata (since 1.36.0)

Lua `streamInfo():filterState()` exposes string, boolean, and numeric filter-state values. Stream handles also add `virtualHost():metadata()` and `route():metadata()` for metadata scoped to the relevant filter name.

### Lua metadata and context APIs (since 1.35.0)

Lua `metadata()` now looks under the filter configuration name before falling back to `envoy.filters.http.lua`. Lua also adds `filterContext()` plus `dynamicTypedMetadata()` on both `streamInfo()` and `connectionStreamInfo()` for typed metadata from HTTP and network filters.

### Lua routing controls (since 1.34.0)

Lua stream info adds `virtualClusterName()`, and Lua can explicitly clear the route cache with `clearRouteCache()` while `clear_route_cache` controls that behavior.

### Lua statistics and filter state (since 1.38.0)

Lua scripts can create and update counters, gauges, and histograms through `handle:streamInfo():stats()`. The filter-state API also adds `set()` for objects backed by registered factories, and downstream SSL information exposes the verified issuer's SHA-256 digest and serial number.

## CEL, matchers, and filter state

### CEL and substitution formatters (since 1.34.0)

CEL adds `re.extract`, `re.capture`, and `re.captureN`; when their extensions are linked, `%CEL%` and `%METADATA%` can be used directly as built-in substitution formatters. Substitution formatting also adds `QUERY_PARAM`, `CUSTOM_FLAGS`, and `PATH`, while `%RESPONSE_CODE_DETAILS%` accepts `ALLOW_WHITESPACES`; without it, whitespace is replaced by underscores.

### External-processing shutdown, local replies, and filter state (since 1.34.0)

Graceful gRPC side-stream half-close is opt-in with `envoy.reloadable_features.ext_proc_graceful_grpc_close=true`; its remote-close timeout defaults to one second and is controlled by `envoy.filters.http.ext_proc.remote_close_timeout_milliseconds`. Local replies are no longer sent to the processor by default, with `envoy_reloadable_features_skip_ext_proc_on_local_reply=false` as a rollback, and an extension can save the processor response to filter state.

### Filter state, CEL, and address matching (since 1.33.0)

CEL gains `upstream.request_attempt_count`, `upstream.cx_pool_ready_duration`, `xds.virtual_host_name`, and `xds.virtual_host_metadata`; ext-authz exposes `latency_us`, `bytesSent`, and `bytesReceived`, and SNI dynamic forward proxy stores its resolved address as `envoy.stream.upstream_address`. `FilterStateMatcher` adds `ip_range` plus an `AddressMatcher` for matching filter-state IP values against CIDR ranges.

### Filter-state update timing (since 1.38.0)

Listener filtering can update filter state, the network Set Filter State filter adds `on_downstream_data` for values created after the first downstream bytes arrive, and the HTTP Set Filter State filter adds `clear_route_cache` for routing that depends on newly written state.

### Filter-state, local-reply, and CEL matching (since 1.38.0)

`FilterStateInput.field` matches a field from a composite filter-state object through `getField()` instead of its serialized form, and a new matcher input distinguishes Envoy local replies from upstream responses. CEL expressions that refer to response-path data during request processing are now reevaluated when the response data exists unless `envoy.reloadable_features.enable_cel_response_path_matching=false`.

### Network-namespace and post-handshake filter state (since 1.37.0)

Connections accepted on a listener with `network_namespace_filepath` now expose read-only `envoy.network.network_namespace` filter state, and a shared filter-state extension can override the upstream bind-address Linux namespace. The Set Filter State network filter also adds `on_downstream_tls_handshake`, allowing values such as peer-certificate SANs to be populated only after TLS completes.

### Prefix-map fallback (since 1.35.0)

When a longer `prefix_match_map` prefix reaches a subtree with no action, matching now resumes at shorter prefixes, like `matcher_list`. Set `envoy.reloadable_features.prefix_map_matcher_resume_after_subtree_miss=false` temporarily, or give each subtree an `on_no_match` action, to retain the old behavior.

### Typed CEL formatting (since 1.36.0)

`%TYPED_CEL%` preserves CEL result types such as numbers, booleans, and null in typed formatting destinations like `json_format`, while `%CEL%` retains its string behavior.

## Composite and transform filters

### Composite-filter chains (since 1.37.0)

`ExecuteFilterAction.filter_chain` can run a chain of filters, while `Composite.named_filter_chains` defines reusable precompiled chains selected through `filter_chain_name`. Per-route composite matching now also works with response-header and response-trailer inputs.

### Composite-filter insertion phases (since 1.36.0)

The composite filter can now insert a filter outside the decode-headers lifecycle phase.

### Transform HTTP filter (since 1.37.0)

The new transform HTTP filter can modify request and response bodies at any point in the HTTP filter chain and can refresh routing from request-body attributes.

## Extension SDKs and custom APIs

### Custom cluster type resolution (since 1.33.0)

Clusters may no longer name unregistered extensions in `cluster_type`. Cluster factories are registered and resolved by configuration type when that type is available.

### Redis proxy command extensions (since 1.34.0)

Redis transactions support multi-key commands, and `custom_commands` lets the Redis proxy define additional commands.

### Socket and network-filter extension points (since 1.34.0)

The default socket interface gains an `io_uring` option. `ExtensionWithMatcher` can wrap network filters with only `SkipFilter` supported; when enabled, `envoy.reloadable_features.connection_close_through_filter_manager` lets a network filter prevent connection close, and the guard defaults to false.

### UDP proxy and tap extensions (since 1.34.0)

UDP proxy supports outlier detection unless `envoy.reloadable_features.enable_udp_proxy_outlier_detection=false`. Tap adds a UDP custom-sink extension, and transport-socket tap can control per-event connection output with `SocketTapConfig.set_connection_per_event`.


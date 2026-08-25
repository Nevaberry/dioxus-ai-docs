# Discovery, DNS, and load balancing

Use this reference for xDS, SDS, RDS, DNS resolvers and caches, cluster and endpoint updates, host selection, and load-balancing policy.

## Cluster refresh during retries (since 1.39.0)

Retry policies add `refresh_cluster_on_retry` so each attempt can refresh a dynamically selected route cluster. `refreshRouteCluster()` now works for weighted-cluster routes, choosing an untried weighted entry until the pool is exhausted and then resetting the pool.

## Cluster-level routing policies (since 1.37.0)

`HttpProtocolOptions` can define `request_mirror_policies`, `retry_policy`, and `hash_policy` at cluster scope; cluster mirror policies override route mirror policies. An on-demand route can opt into body-aware stream recreation with `envoy.reloadable_features.on_demand_track_end_stream` instead of rejecting every request with a body.

## Connection metadata in subset load balancing (since 1.36.0)

Subset load-balancing matches now include connection-level metadata in the `envoy.lb` namespace.

## Custom cluster type resolution (since 1.33.0)

Clusters may no longer name unregistered extensions in `cluster_type`. Cluster factories are registered and resolved by configuration type when that type is available.

## Delta-xDS node emission (since 1.38.0)

Delta-xDS adds `set_node_on_first_message_only`; its compatibility behavior is guarded by `envoy.reloadable_features.xds_legacy_delta_skip_subsequent_node`.

## DNS resolver and filter controls (since 1.37.0)

The c-ares resolver adds `reinit_channel_on_timeout` to recreate its channel after a DNS timeout. The DNS filter can now emit access logs.

## DNS resolver controls (since 1.33.0)

The c-ares resolver adds `query_timeout_seconds`, `query_tries`, and `rotate_nameservers`; rotation round-robins configured nameservers per resolution. After a successful lookup followed by a failed one, DNS cache refresh now uses `dns_refresh_rate` or `dns_failure_refresh_rate` rather than the prior TTL.

## DNS resolver execution and inheritance (since 1.35.0)

The `getaddrinfo` resolver can run through a thread pool sized by `num_resolver_threads`. An HTTP dynamic-forward-proxy DNS cache with an empty `dns_cache_config` now inherits the bootstrap `typed_dns_resolver_config`.

## Dynamic discovery sources (since 1.33.0)

An SDS backing cluster may now itself be dynamic; set `envoy.restart_features.skip_backing_cluster_check_for_sds=false` to restore the primary-cluster restriction. SRDS-delivered `ScopedRouteConfiguration` resources may contain `route_configuration`, and ADS can be replaced programmatically with `xdsManager().setAdsConfigSource()`.

## Dynamic forward proxy DNS controls (since 1.34.0)

Setting `dns_query_timeout` to `0` disables Envoy's timeout in favor of the underlying DNS implementation; `disable_dns_refresh_on_failure=true` suppresses refreshes after failures and treats failed hosts as cache misses. Null-host resolution uses the async lookup path unless `envoy.reloadable_features.dfp_cluster_resolves_hosts=false`, and empty authority or host entries now fail unless `envoy.reloadable_features.dfp_fail_on_empty_host_header=false`.

## Dynamic-forward-proxy host state (since 1.35.0)

With `allow_dynamic_host_from_filter_state`, the HTTP dynamic forward proxy consults `envoy.upstream.dynamic_host` and `envoy.upstream.dynamic_port` before the Host header. The flag is disabled by default.

## Dynamic-update behavior corrections (since 1.39.0)

An EDS-only change to an endpoint's `hostname` or `health_check_config.hostname` now recreates the host and drains its connection pools, so settings such as `auto_host_sni` see the update. Removing an RTDS override now actually returns a process-wide reloadable guard to its underlying value, and static-route VHDS now sends subscriptions and supports on-demand operation.

## Hickory DNS resolver (since 1.38.0)

`HickoryDnsResolverConfig` provides a DNS resolver backed by the Hickory DNS library.

## Load-balancing policies (since 1.35.0)

Envoy adds the Override Host load-balancing policy. Ring-hash and Maglev policies also accept a load-balancer hash policy; when configured there, it supersedes the route-level hash policy.

## New DNS-cluster implementation and resolver sharing (since 1.39.0)

`envoy.reloadable_features.enable_new_dns_implementation` now defaults to enabled, activating the merged strict/logical DNS-cluster implementation; set it to `false` for temporary rollback. Identical c-ares configurations also share a resolver by default under `envoy.restart_features.shared_cares_dns_resolver`, and `CaresDnsResolverConfig.qcache_max_ttl` can cap qcache entries while its default `0` keeps qcache disabled.

## On-demand CDS stream handling (since 1.38.0)

After an on-demand CDS lookup succeeds, the on-demand filter no longer recreates the stream through an internal redirect, so earlier filters run only once. Set `envoy.reloadable_features.on_demand_cluster_no_recreate_stream=false` to restore the prior behavior temporarily.

## ORCA out-of-band load reporting (since 1.39.0)

Client-side weighted round robin can open the ORCA `StreamCoreMetrics` server-streaming RPC when `enable_oob_load_report=true`. `oob_reporting_config` can override the reporting port, authority, and transport-socket match criteria, including use of a reporting sidecar.

## Original host preservation (since 1.35.0)

The router filter records the host value from before its mutation in `x-envoy-original-host`.

## Resolver inheritance and streamed gRPC limits (since 1.36.0)

An empty DNS-filter `client_config` now inherits bootstrap `typed_dns_resolver_config`. The gRPC JSON transcoder caps streamed gRPC frames at `1MB`, preventing frames that common upstream defaults reject once they exceed `4MB`.

## Reverse-tunnel cluster validation (since 1.37.0)

Reverse-tunnel configuration adds `required_cluster_name`; an initiation whose `x-envoy-reverse-tunnel-upstream-cluster-name` does not match is rejected with `400 Bad Request`.

## Router cluster selection APIs (since 1.35.0)

A matcher-based router cluster-specifier plugin selects clusters through a matcher tree. Stream-filter callbacks add `refreshRouteCluster()` to refresh the selected cluster without invalidating the route cache.

## Upstream HTTP filters and asynchronous load balancing (since 1.34.0)

The Lua and credential-injector HTTP filters can now run as upstream filters. Alpha asynchronous load balancing is enabled unless `envoy.reloadable_features.async_host_selection=false`.

## Weighted-cluster hash selection (since 1.36.0)

`WeightedCluster.use_hash_policy=true` applies the route's existing `hash_policy` while selecting among weighted clusters, giving equal hash values stable weighted-cluster selection for session affinity.

## xDS ingestion and RDS provider reuse (since 1.33.0)

Delta-xDS ingestion no longer copies resources by default, which can reorder elements passed to custom validators or config trackers; revert with `envoy.reloadable_features.xds_prevent_resource_copy=false`. An RDS update that changes only `initial_fetch_timeout` now reuses the provider without requesting routes again; `envoy.reloadable_features.normalize_rds_provider_config=false` restores the prior behavior.


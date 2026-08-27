# Operations and istioctl

Use this reference for scripting the CLI, tuning istiod and proxy behavior, and
interpreting diagnostics. Root flags generally affect all subcommands, while
command-specific timeouts and proxy-admin connectivity remain separate.

## istioctl flag and output changes

- (`1.25.0`) `istioctl analyze` is always recursive; remove `--recursive`.
- (`1.25.0`) `istioctl proxy-status` no longer accepts the experimental
  `--xds-via-agents` flag.
- (`1.27.0`) Root `--kubeclient-timeout` accepts a Go `time.Duration` and
  replaces the default `15s` timeout for Kubernetes-client calls across
  istioctl. It does not change installation or other command-specific
  timeouts. Example:

  ```bash
  istioctl --kubeclient-timeout=30s proxy-status
  ```

- (`1.28.0`) `istioctl admin log` accepts `--level` and
  `--stack-trace-level` together.
- (`1.28.0`) Use `--proxy-admin-port` with `istioctl experimental authz`,
  `istioctl proxystatus`, `istioctl bug-report`, and
  `istioctl experimental describe` when the admin endpoint is not on its
  default port.
- (`1.29.0`) `istioctl ztunnel-config` also accepts `--proxy-admin-port`.
- (`1.29.0`) `istioctl ztunnel-config all` and `istioctl proxy-config all`
  print header rows; update scripts that parse their tables.
- (`1.29.0`) `istioctl waypoint status --wait=false` reports immediately, and
  `--all-namespaces` lists waypoints across the cluster.

## Expanded diagnostics

- (`1.30.0`) `istioctl bug-report` can skip expensive sections with
  `--skip-cluster-dump`, `--skip-analyze`, `--skip-proxy-debug`,
  `--skip-netstat`, and `--skip-coredumps`; `--tail` limits log lines per
  container.
- (`1.30.0`) `istioctl proxy-status` emits JSON or YAML and supports
  namespace-scoped listings.
- (`1.30.0`) `ztunnel-config workload` and `ztunnel-config connections` filter
  by workload pod name.
- (`1.30.0`) Istiod logs configuration-analysis warnings and errors for all
  Istio resource types. `WorkloadEntry` status includes `WaypointBound` for
  waypoint attachment success or failure.
- (`1.25.0`) Sidecar injection configuration errors are surfaced to the user
  rather than logged while processing continues.
- (`1.25.0`) `istioctl x authz check` supports `CUSTOM` AuthorizationPolicy.

## Revision and remote-secret workflows

- (`1.28.0`) `istioctl tag set <tag> --revision <rev>` and Helm
  `revisionTags` create a cluster-IP Service labeled `istio.io/tag` as well as
  the mutating webhook representation.
- (`1.28.0`) When `--revision` is omitted, istioctl commands automatically use
  the revision assigned by `istioctl tag set default`.
- (`1.26.0`) `istioctl create-remote-secret --tls-server-name <name>` writes
  `tls-server-name` into the generated kubeconfig for certificate validation
  when the `server` is a gateway proxy hostname.
- (`1.27.0`) In `profile=remote`, enable a local sidecar injector with
  `.Values.istiodRemote.enabledLocalInjectorIstiod=true` while setting
  `.Values.global.remotePilotAddress="${DISCOVERY_ADDRESS}"` to keep xDS on the
  remote primary.
- (`1.30.0`) `PILOT_MULTICLUSTER_KUBECONFIG_PATH` points istiod at a mounted
  directory of `.yaml` and `.yml` remote-cluster registrations. Files are
  watched dynamically and this source overrides `LOCAL_CLUSTER_SECRET_WATCHER`.

## Control-plane resource use

- (`1.29.0`) Istiod derives `GOMEMLIMIT` as 90% of its container memory limit,
  rather than 100%. Set `GOMEMLIMIT` directly or adjust the ratio with
  `AUTOMEMLIMIT`, for example `AUTOMEMLIMIT=0.85`.
- (`1.29.0`) `PILOT_IGNORE_RESOURCES` accepts comma-separated resources or
  prefixes excluded from Pilot's Istio CRD watcher.
  `PILOT_INCLUDE_RESOURCES` restores matching resources, enabling narrowly
  scoped controllers such as Gateway API-only or HTTPRoute-only deployments.
- (`upgrade-1.30`) `taint.enabled` in the istiod chart automatically sets
  `PILOT_ENABLE_NODE_UNTAINT_CONTROLLERS`.
- (`1.25.0`) Installation values can customize `PodDisruptionBudget`
  `maxUnavailable`.

## DNS proxy and proxy discovery controls

- (`1.25.0`) DNS proxying randomly selects an upstream resolver.
  `PILOT_DNS_JITTER_DURATION` controls periodic-resolution jitter, while
  `PILOT_DNS_CARES_UDP_MAX_QUERIES` sets Cares `udp_max_queries` and defaults
  to `100`.
- (`1.27.0`) `ENABLE_PROXY_FIND_POD_BY_IP` lets Istio associate a proxy with a
  Pod by IP when Pod-name and namespace matching fails.
- (`1.30.0`) `DNS_FORWARD_TIMEOUT` changes the proxy's DNS upstream timeout
  from `5s`; configure it in `istio-proxy` or globally via `proxyMetadata`.

## Proxy and gateway tuning

- (`1.28.0`) Explicitly bound sidecar listeners process at most one connection
  per socket event by default. Set `MAX_CONNECTIONS_PER_SOCKET_EVENT_LOOP=0`
  to restore the earlier behavior.
- (`1.29.0`) `ISTIO_META_GLOBAL_DOWNSTREAM_MAX_CONNECTIONS` proxy metadata sets
  Envoy's global downstream limit and overrides deprecated runtime flag
  `overload.global_downstream_max_connections`.
- (`1.30.0`) `PILOT_GATEWAY_TRANSPORT_SOCKET_CONNECT_TIMEOUT` defaults to
  `15s` on gateway listeners. Set `0s` to disable the timeout for longer TLS
  handshakes.
- (`1.28.0`) `FORCE_IPTABLES_BINARY` selects the iptables binary instead of
  relying on backend detection.
- (`1.29.0`) `ProxyConfig` supports Envoy file flush interval and buffer
  configuration.

## Logging, metrics, and debug access

- (`1.25.0`) Deprecated Envoy logs are skipped by default;
  `ENVOY_SKIP_DEPRECATED_LOGS=false` re-enables them.
- (`upgrade-1.29`) Envoy circuit-breaker `TrackRemaining` metrics default off.
  `DISABLE_TRACK_REMAINING_CB_METRICS=false` retains them.
- (`upgrade-1.29`) Debug endpoint authorization restricts non-system callers to
  `config_dump`, `ndsz`, and `edsz` for same-namespace proxies. Disable it with
  `ENABLE_DEBUG_ENDPOINT_AUTH=false` only if unrestricted access is required.
- (`upgrade-1.30`) Authentication also protects plaintext `syncz` and
  `config_dump` xDS endpoints on port 15010, affecting
  `istioctl --plaintext`.
- (`1.30.0`) `DEBUG_ENDPOINT_AUTH_ALLOWED_NAMESPACES` adds comma-separated
  allowed namespaces when debug authorization is enabled. The system namespace
  remains authorized.
- (`1.29.0`) `istiod_remote_cluster_sync_status` reports remote-cluster
  synchronization as a Pilot gauge.


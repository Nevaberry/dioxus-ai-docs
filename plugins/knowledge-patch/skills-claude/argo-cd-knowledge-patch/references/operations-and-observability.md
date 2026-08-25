# Operations and Observability

## Repo-server operations

### Watch large-monorepo contention

Argo CD 3.2.0 can encounter repo-server lock contention with large monorepos,
severe enough to require pod restarts. The release notes defer the fix to a
later patch. Monitor queueing, health, and restarts, and plan the applicable
patch-level upgrade rather than normalizing recurring restarts.

### Configure pprof through parameters

As of 3.3.13, repo-server mounts `argocd-cmd-params-cm` and registers pprof
endpoints from the parameters ConfigMap. Enable pprof there when profiling is
needed, and keep the diagnostic endpoint within a restricted network and
authorization boundary.

### Observe parallelism and export headers

In 3.5.0, metrics expose the repo-server parallelism limit and webhook-handler
failures. Repo-server also honors `ARGOCD_REPO_SERVER_OTLP_HEADERS` for
OpenTelemetry export. Alert on saturation relative to the configured limit,
track webhook failures, and source export headers from a protected value.

## Redis and cached application state

Application health is stored in Redis by default as of 3.0.0. The global
`--redis-compress` flag selects Redis compression. When diagnosing health,
memory, or decoding issues, examine the controller and Redis settings together
and ensure all components agree on compression.

Setting `timeout.reconciliation=0` in 3.5.0 disables soft expiry while leaving
the diff cache usable. A zero timeout therefore does not mean every result is
recomputed without cache involvement.

## Transport and probes

### Pass WebSocket upgrades

Port forwarding and pod exec use WebSockets rather than SPDY as of 3.0.0.
Ingresses and proxies must pass the HTTP upgrade, preserve required headers,
and allow appropriate idle durations.

### Probe the gRPC server

`argocd-server` provides a gRPC health check in 3.2.0. Use it for operational
probes that need to exercise the gRPC endpoint, and tune failure thresholds to
avoid restart loops during brief dependency stalls.

### Validate Kubernetes compatibility

Argo CD 3.0.0 supports Kubernetes 1.32. Cluster support does not replace
testing of CRDs, admission policies, exec behavior, or installed extensions
against the target cluster.

### Pass cluster context to exec credential providers

Cluster `ExecProviderConfig` includes `ProvideClusterInfo` and `Config` in
3.5.0. Enable cluster information only when the credential plugin needs it,
and treat provider-specific configuration as part of the plugin's security and
compatibility contract.

## Tracing and logs

### Propagate trace context

OpenTelemetry trace context propagates across HTTP requests as of 3.2.0.
Preserve trace headers in proxies and extensions so spans remain connected.

Shipped manifests include environment-reference objects for `otlp.attrs` since
3.0.0. Use those references in overlays instead of duplicating attribute
values, and use `ARGOCD_REPO_SERVER_OTLP_HEADERS` for repo-server exporter
headers where needed.

### Configure log timestamps consistently

Log timestamp format is configurable as of 3.0.0, and klog follows the chosen
log format. Keep timestamps consistent across components and ensure parsers
accept the configured representation.

## Metrics and user interface context

Cluster metrics can include cluster names and labels (3.0.0). GitHub API
rate-limit and sync-duration metrics are available since 3.1.0. Select only
useful cluster labels to control cardinality, and alert before API quota
exhaustion or abnormal sync latency becomes an outage.

Node labels can be propagated into the Application pod view as of 3.1.0.
Expose only labels operators need; high-cardinality or sensitive scheduling
labels can add UI and disclosure cost.

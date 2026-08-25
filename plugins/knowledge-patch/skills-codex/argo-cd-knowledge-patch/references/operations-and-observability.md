# Operations and Observability

## Repository-server contention

Large monorepos can cause repo-server lock contention severe enough to require
pod restarts in 3.2.0. The release notes defer the fix to a later patch. Monitor
queueing, responsiveness, and restart frequency, and plan the patch-level
upgrade instead of treating restarts as a complete mitigation.

## Kubernetes compatibility

Argo CD 3.0.0 supports Kubernetes 1.32. Validate CRDs, admission policies,
extensions, and operational tooling in addition to basic cluster connectivity.

## Redis state and compression

Application health is stored in Redis by default starting in 3.0.0. Redis
compression is selected globally with `--redis-compress` (3.0.0). Include both
the stored health state and compression setting when diagnosing read failures,
staleness, or mixed-component behavior.

## Health probes and profiling

`argocd-server` exposes a gRPC health check in 3.2.0. Use it for operational
probing where the probe stack supports gRPC semantics.

Repo-server mounts `argocd-cmd-params-cm` and registers pprof endpoints from
the parameters ConfigMap in 3.3.13. This allows pprof to be enabled through
that configuration; restrict profiling endpoints according to their
operational sensitivity.

## OpenTelemetry

The shipped manifests include environment-reference objects for `otlp.attrs`
(3.0.0). Preserve those references when composing deployment overlays.

OpenTelemetry trace context propagates across HTTP requests (3.2.0). Ensure
proxies and extensions preserve trace headers so traces remain connected.

Repo-server honors `ARGOCD_REPO_SERVER_OTLP_HEADERS` when exporting telemetry
(3.5.0). Use it where exporter authentication or routing requires headers and
keep sensitive values out of rendered logs.

## Metrics

Cluster metrics can include the cluster name and labels (3.0.0). GitHub API
rate-limit and sync-duration metrics are available (3.1.0). In 3.5.0, metrics
also expose the repo-server parallelism limit and webhook-handler failures.

Select cluster labels deliberately to control cardinality. Use the rate-limit,
duration, parallelism, and webhook metrics together when distinguishing source
provider limits, repository saturation, and event handling failures.

## Logs and pod view

Log timestamp formatting is configurable, and klog follows the selected log
format (3.0.0). Keep parsers aligned with the configured timestamp and format.

Node labels can be propagated to the Application pod view (3.1.0). Expose only
labels operators use; broad propagation can add noise and cardinality.

## Webhook refresh behavior

Webhook-triggered Application refresh supports configurable jitter and GitHub
Container Registry events (3.5.0). Balance jitter against acceptable refresh
latency and monitor webhook-handler failures when expected refreshes do not
occur.

## ApplicationSet concurrency

ApplicationSets can manage generated Applications concurrently (3.5.0), and
manifest hydration queue concurrency is configurable. Tune each concurrency
control against API-server, repository, and controller capacity rather than
raising both without observing contention.

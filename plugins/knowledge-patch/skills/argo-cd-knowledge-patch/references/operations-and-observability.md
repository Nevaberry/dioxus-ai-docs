# Operations and Observability

## Repository-server contention

Argo CD 3.2.0 can hit repo-server lock contention with large monorepos, in some
cases requiring pod restarts. Its release notes defer the fix to a later patch
release. Monitor repo-server latency, blocked work, and restart frequency;
avoid treating repeated restarts as a durable remedy, and plan a patch upgrade.

## Redis-backed health and compression

- The application controller stores Application health status in Redis by
  default since 3.0.0. Include Redis availability and stored state when
  investigating health that appears stale or inconsistent across components.
- Redis compression can be selected globally with `--redis-compress` since
  3.0.0. Keep all communicating components on a compatible setting and include
  it in configuration-drift checks.

## Probing

`argocd-server` exposes a gRPC health check since 3.2.0. Use the gRPC-aware
probe when it matches the served protocol and deployment environment, and test
the exact service path from the same network boundary as the probe runner.

## OpenTelemetry

- Shipped manifests add environment-reference objects for `otlp.attrs` since
  3.0.0. Preserve or deliberately override those references when composing
  manifests; do not accidentally replace the reference with an unrelated
  literal value.
- OpenTelemetry trace context propagates across HTTP requests since 3.2.0, so
  traces can stay connected between components. Configure proxies and
  extensions to forward the trace headers rather than terminating continuity.

## Metrics

- Cluster metrics can include the cluster name and labels since 3.0.0. Enable
  only labels that provide operational value to control cardinality and avoid
  unintentionally exposing sensitive cluster metadata.
- GitHub API rate-limit and sync-duration metrics are available since 3.1.0.
  Use rate-limit data to distinguish upstream throttling from controller
  slowness, and sync-duration data for rollout latency objectives.

## Logs and pod view

- Log timestamp formatting is configurable since 3.0.0, and klog output follows
  the configured log format. Update parsers when changing the format.
- Node labels can optionally be propagated to the Application pod view since
  3.1.0. Limit propagation to useful labels if label volume, sensitivity, or UI
  clutter is a concern.

## Platform compatibility

Argo CD 3.0.0 supports Kubernetes 1.32. Validate installed CRDs, webhooks,
extensions, and cluster policy alongside that support claim; the supported
cluster version does not guarantee every surrounding integration is compatible.

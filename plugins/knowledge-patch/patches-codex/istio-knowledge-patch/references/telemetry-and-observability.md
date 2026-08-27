# Telemetry and Observability

Use this reference for tracing providers, metrics behavior, access logs,
dashboards, baggage, and telemetry identity.

## Contents

- [Provider and dashboard migrations](#provider-and-dashboard-migrations)
- [Workload and application identity](#workload-and-application-identity)
- [Tracing](#tracing)
- [Metrics](#metrics)
- [Logs and file output](#logs-and-file-output)
- [Telemetry custom values](#telemetry-custom-values)

## Provider and dashboard migrations

### Grafana dashboard minimum version (upgrade-1.25)

The dashboards shipped with Istio 1.25 require Grafana 7.2 or later.

### OpenCensus support removed (upgrade-1.25)

Istio no longer supports OpenCensus tracing because Envoy removed its
OpenCensus tracing extension. Migrate OpenCensus configuration to OpenTelemetry
before upgrading.

### Lightstep telemetry provider removal (upgrade-1.26)

The Lightstep telemetry provider, deprecated since Istio 1.22, is scheduled for
removal in Istio 1.27. Migrate Lightstep provider configuration to OpenTelemetry
before upgrading to 1.27.

### Regenerate bundled Grafana dashboards (upgrade-1.27)

After upgrading, regenerate Istio's bundled Grafana dashboards to receive fixed
cross-dashboard links. Dashboard UIDs are explicitly defined so the links
remain stable.

## Workload and application identity

### Telemetry workload-name override (1.25.0)

Set `service.istio.io/workload-name` on a `Pod` or `WorkloadEntry` to override
the workload name reported in telemetry. A `WorkloadEntry` created from a
`WorkloadGroup` falls back to the group name.

### Workload identity tags in waypoint traces (1.29.0)

Waypoint spans include `istio.source_workload`, `istio.source_namespace`,
`istio.destination_workload`, and `istio.destination_namespace`, along with
other peer tags. Upstream and downstream spans also expose
`istio.downstream.workload`, `istio.downstream.namespace`,
`istio.upstream.workload`, and `istio.upstream.namespace`.

### Application-label metric fallbacks (1.30.0)

For `source_app` and `destination_app`, Istio checks `app`, then
`app.kubernetes.io/name`, then `service.istio.io/canonical-name`. Workloads
without the legacy `app` label can therefore populate application metrics.

## Tracing

### Separate upstream gateway tracing spans (1.26.0)

Set `PILOT_SPAWN_UPSTREAM_SPAN_FOR_GATEWAY=true` to separate server- and
client-side gateway tracing spans. It defaults to `false` in 1.26, although the
release notes state that this will become the default later.

### Upstream gateway spans enabled by default (1.28.0)

`PILOT_SPAWN_UPSTREAM_SPAN_FOR_GATEWAY` defaults to `true`.

### Dual B3 and W3C propagation for Zipkin (1.28.0)

Set `trace_context_option: USE_B3_WITH_W3C_PROPAGATION` on a Zipkin provider in
`MeshConfig.extensionProviders` to prefer extracted B3 headers, fall back to W3C
`traceparent`, and inject both formats upstream.

### Ambient cross-network baggage telemetry (1.29.0)

Set `AMBIENT_ENABLE_BAGGAGE=true` on Pilot to enable waypoint-generated baggage
so cross-network metrics receive source and destination labels. Waypoint
support is off by default. ztunnel baggage is on by default and is controlled
with ztunnel's `ENABLE_RESPONSE_BAGGAGE`.

### Zipkin request timeout and headers (1.29.0)

`MeshConfig.extensionProviders` entries for Zipkin accept `timeout` and
`headers`. Headers may contain direct values or environment-variable
references, enabling collector authentication and metadata without hard-coded
credentials.

### Independent trace-context propagation control (1.30.0)

The Telemetry tracing API's `disableContextPropagation` field disables
propagation headers such as `X-B3-*` and `traceparent` without disabling span
reporting.

### OpenTelemetry service attribute enrichment (1.30.0)

Set `serviceAttributeEnrichment: OTEL_SEMANTIC_CONVENTIONS` on an
`OpenTelemetryTracingProvider` to derive `service.name` using OpenTelemetry's
Kubernetes fallback chain. Istio also injects `service.namespace`,
`service.version`, and `service.instance.id` as `OTEL_RESOURCE_ATTRIBUTES` and
enables Envoy's Environment resource detector.

### Baggage metadata limitation for TLS and PROXY routes (1.30.0)

Baggage-based peer metadata discovery is disabled on routes with TLS or PROXY
traffic policies to avoid interference. Multicluster telemetry for these routes
can have incomplete peer metadata.

## Metrics

### Stats eviction configuration migration (upgrade-1.28)

Pilot environment variables `METRIC_ROTATION_INTERVAL` and
`METRIC_GRACEFUL_DELETION_INTERVAL` are removed. Configure the stats eviction
API with the `sidecar.istio.io/statsEvictionInterval` pod annotation.

### Per-pod stats flush interval (1.28.0)

Use `sidecar.istio.io/statsFlushInterval` to configure a pod's stats flush
interval.

### Envoy metrics compression configuration (upgrade-1.29)

HTTP compression for Envoy's `prometheus_stats` endpoint defaults to enabled
through `ProxyConfig.statsCompression`, negotiating Brotli, gzip, or Zstandard
according to the client request. Replace the removed
`sidecar.istio.io/statsCompression` annotation with the global option or a
per-pod override:

```yaml
metadata:
  annotations:
    proxy.istio.io/config: |
      statsCompression: false
```

### Circuit-breaker remaining metrics disabled by default (upgrade-1.29)

Istio no longer enables Envoy's circuit-breaker `TrackRemaining` metrics by
default. Set `DISABLE_TRACK_REMAINING_CB_METRICS=false` in istiod, or select
legacy behavior through the compatibility-version feature, to retain them.

### Remote-cluster synchronization metric (1.29.0)

Pilot exposes the `istiod_remote_cluster_sync_status` gauge for monitoring
remote-cluster synchronization.

## Logs and file output

### Deprecated Envoy logs skipped by default (1.25.0)

Envoy deprecated logs are skipped by default. Set
`ENVOY_SKIP_DEPRECATED_LOGS=false` to enable them.

### Empty-value omission in file access logs (1.26.0)

The Telemetry API's `EnvoyFileAccessLog` provider supports
`omit_empty_values`.

### Envoy file output buffering controls (1.29.0)

`ProxyConfig` can customize Envoy's file flush interval and buffer
configuration.

## Telemetry custom values

### Formatter telemetry custom tags (1.29.0)

Custom tags in the Telemetry API support the `Formatter` type.

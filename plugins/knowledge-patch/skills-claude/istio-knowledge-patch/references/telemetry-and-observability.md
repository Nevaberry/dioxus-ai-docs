# Telemetry and observability

Use this reference for tracing-provider migrations, metrics behavior, access
logs, and cross-network attribution. Check defaults carefully because several
feature flags changed state after their introduction.

## Provider and dashboard migrations

- (`upgrade-1.25`) OpenCensus tracing support is removed after Envoy removed
  its OpenCensus extension. Migrate configurations to OpenTelemetry.
- (`upgrade-1.26`) Lightstep provider configuration must also migrate to the
  OpenTelemetry provider before its removal in Istio 1.27.
- (`upgrade-1.25`) Bundled dashboards require Grafana 7.2 or later.
- (`upgrade-1.27`) Regenerate bundled Grafana dashboards after the upgrade to
  receive corrected cross-dashboard links. Explicit dashboard UIDs keep those
  links stable.

## Workload and application identity

- (`1.25.0`) `service.istio.io/workload-name` on a Pod or `WorkloadEntry`
  overrides the workload name reported in telemetry. A WorkloadEntry created
  from a `WorkloadGroup` falls back to the group name.
- (`1.30.0`) `source_app` and `destination_app` resolve labels in this order:
  `app`, `app.kubernetes.io/name`, then
  `service.istio.io/canonical-name`. Workloads without the legacy `app` label
  can therefore still populate application metrics.
- (`1.29.0`) Waypoint traces include `istio.source_workload`,
  `istio.source_namespace`, `istio.destination_workload`, and
  `istio.destination_namespace`. Upstream and downstream spans also expose the
  `istio.downstream.workload`, `istio.downstream.namespace`,
  `istio.upstream.workload`, and `istio.upstream.namespace` tags.

## Tracing spans and context propagation

- (`1.26.0`) `PILOT_SPAWN_UPSTREAM_SPAN_FOR_GATEWAY=true` creates separate
  server- and client-side gateway spans. It was introduced with a default of
  `false`.
- (`1.28.0`) The same `PILOT_SPAWN_UPSTREAM_SPAN_FOR_GATEWAY` setting now
  defaults to `true`.
- (`1.28.0`) For a Zipkin provider in `MeshConfig.extensionProviders`, set
  `trace_context_option: USE_B3_WITH_W3C_PROPAGATION` to prefer extracted B3,
  fall back to W3C `traceparent`, and inject both formats upstream.
- (`1.29.0`) Zipkin providers accept `timeout` and `headers`. Header values may
  be literal or environment-variable references, supporting authentication and
  custom metadata without embedding credentials.
- (`1.30.0`) Telemetry tracing field `disableContextPropagation` disables
  propagation headers such as `X-B3-*` and `traceparent` without stopping span
  reporting.
- (`1.30.0`) On `OpenTelemetryTracingProvider`, set
  `serviceAttributeEnrichment: OTEL_SEMANTIC_CONVENTIONS` to derive
  `service.name` through OpenTelemetry's Kubernetes fallback chain. Istio also
  injects `service.namespace`, `service.version`, and `service.instance.id` as
  `OTEL_RESOURCE_ATTRIBUTES` and enables Envoy's Environment resource detector.

## Ambient baggage and peer metadata

- (`1.29.0`) `AMBIENT_ENABLE_BAGGAGE=true` on Pilot enables
  waypoint-generated baggage so cross-network metrics get source and
  destination labels. Waypoint support defaults off. ztunnel baggage defaults
  on and is controlled by ztunnel `ENABLE_RESPONSE_BAGGAGE`.
- (`1.30.0`) Baggage peer-metadata discovery is disabled on routes with TLS or
  PROXY traffic policies to avoid interfering with them. Multicluster telemetry
  on those routes can have incomplete peer metadata.

## Metrics collection and retention

- (`upgrade-1.28`) Removed Pilot settings `METRIC_ROTATION_INTERVAL` and
  `METRIC_GRACEFUL_DELETION_INTERVAL` are replaced by the
  `sidecar.istio.io/statsEvictionInterval` pod annotation.
- (`1.28.0`) `sidecar.istio.io/statsFlushInterval` configures stats flushing per
  pod.
- (`upgrade-1.29`) Envoy `prometheus_stats` HTTP compression defaults on through
  `ProxyConfig.statsCompression`, negotiating Brotli, gzip, or Zstandard.
  Replace the removed `sidecar.istio.io/statsCompression` annotation with the
  global option or a per-pod `proxy.istio.io/config` override.
- (`upgrade-1.29`) Circuit-breaker `TrackRemaining` metrics default off. Set
  `DISABLE_TRACK_REMAINING_CB_METRICS=false` on istiod or use the legacy
  compatibility-version behavior to retain them.
- (`1.29.0`) Pilot exports `istiod_remote_cluster_sync_status` as a gauge for
  remote-cluster synchronization.

## Access logs and Envoy file output

- (`1.26.0`) `EnvoyFileAccessLog` in the Telemetry API supports
  `omit_empty_values`.
- (`1.29.0`) `ProxyConfig` can tune Envoy file flush interval and buffer
  configuration.
- (`1.29.0`) Telemetry custom tags support the `Formatter` type.
- (`1.25.0`) Deprecated Envoy log messages are skipped by default. Set
  `ENVOY_SKIP_DEPRECATED_LOGS=false` to include them.


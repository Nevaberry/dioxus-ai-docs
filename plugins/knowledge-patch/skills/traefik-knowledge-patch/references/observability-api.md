# Observability And API

Use this reference for metrics, tracing, logs, support diagnostics, API paths,
and dashboard behavior.

## OpenTelemetry metrics, traces, and logs

- The OTLP metrics exporter can set OpenTelemetry `service.name` (since 3.2.0).
- Access logs can include the trace ID and entry-point span ID for correlation
  with distributed traces (since 3.2.0).
- Application logs and access logs can be exported through OpenTelemetry behind
  an experimental flag (since 3.3.0).
- Metrics, tracing, and access logging can be controlled at entry-point and
  router scope, not just globally (since 3.3.0).
- Metrics accept `resourceAttributes` (since 3.5.0). Resource detection also
  applies across logs, access logs, metrics, and traces; logs and traces running
  in Kubernetes receive Kubernetes resource attributes automatically.
- Tracing has a verbosity setting and emits fewer spans by default (since
  3.5.0). Set verbosity explicitly when existing analysis depends on the old
  span detail.
- Access logs can still write to stdio while OTLP logging is active, use
  OpenTelemetry-conformant trace-context attributes, and include Kubernetes
  Ingress fields (since 3.7.0).
- `metrics.influxdb2.token` can read its secret from a file path (since 3.7.0).

## API and diagnostics

- The API exposes a support-dump endpoint for collecting diagnostic state (since
  3.3.0).
- The API and dashboard can be mounted beneath a configurable base path (since
  3.3.0).

## Dashboard

- The Web UI offers an automatic theme and uses it by default (since 3.4.0).
- The certificate overview shows certificate domains, expiration, and attached
  HTTP and TCP routers (since 3.7.0).
- Service details display server weights, and the dashboard name is configurable
  (since 3.7.0).

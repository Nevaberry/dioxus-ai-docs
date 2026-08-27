# Observability

## Identify OTLP signals

The OTLP metrics exporter can set OpenTelemetry `service.name`; configure it to
give emitted metrics an explicit service identity (3.2.0).

Metrics also accept `resourceAttributes`. Resource detection covers application
logs, access logs, metrics, and traces, and Kubernetes resource attributes are
added automatically to logs and traces when Traefik runs in Kubernetes (3.5.0).

Traefik can export application and access logs through OpenTelemetry when the
required experimental flag is enabled (3.3.0). OTLP logging can coexist with
stdio access-log output (3.7.0), so keep a local stream when operations require
both local and remote collection.

## Correlate requests and traces

Access logs can include the trace ID and entry point's span ID (3.2.0). Use them
to correlate proxy requests with distributed traces.

Tracing has a verbosity setting and emits fewer spans by default. Set verbosity
explicitly when consumers depend on the earlier span detail (3.5.0).

Access logs use OpenTelemetry-conformant trace-context attributes and can
include Kubernetes Ingress fields (3.7.0).

## Scope observability

Metrics, tracing, and access logging can be controlled at both entry-point and
router scope rather than only globally (3.3.0). Decide whether a global default
or a route-specific override owns each signal before changing configuration.

ForwardAuth can expose an authenticated user to access logs through
`LogUserHeader` (3.2.0). Treat the selected identity header as sensitive and
ensure the authentication boundary controls it.

## Use diagnostics and secret files

The API exposes a support-dump endpoint for collecting diagnostic state
(3.3.0). Protect it with the same care as other operational APIs.

`metrics.influxdb2.token` may point to a file containing the secret rather than
embedding the token directly in configuration (3.7.0).

Consul, Consul Catalog, and Nomad log their provider namespace at startup,
which helps distinguish provider instances during diagnosis (3.6.0).

## Configure the API and dashboard

The API and dashboard can use a configurable base path (3.3.0). Set it when the
UI is mounted below a reverse-proxy prefix.

The Web UI's automatic theme is the default theme choice (3.4.0).

The dashboard includes a certificate overview with certificate domains,
expiration, and attached HTTP/TCP routers. Service details include server
weights, and the dashboard name is configurable (3.7.0).

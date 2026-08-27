# Observability

## Give OTLP metrics an identity

Set the OTLP metrics `service.name` explicitly when downstream systems need a
stable Traefik service identity (3.2.0). Metrics also accept
`resourceAttributes` (3.5.0).

Resource detection applies across application logs, access logs, metrics, and
traces. When Traefik runs in Kubernetes, logs and traces automatically receive
Kubernetes resource attributes (3.5.0).

## Correlate access logs and traces

Access logs can include the request trace ID and the entry point's span ID
(3.2.0). Later patch-line behavior uses OpenTelemetry-conformant trace-context
attribute names and adds Kubernetes Ingress fields to access-log records
(3.7.0).

Tracing has a verbosity setting and produces fewer spans by default (3.5.0).
Set verbosity explicitly if dashboards, sampling policy, or diagnostics rely on
the earlier span detail.

## Export logs through OpenTelemetry

Application logs and access logs can be exported through OpenTelemetry behind
an experimental flag (3.3.0). OTLP logging can run while access logs are also
written to stdio, preserving a local stream alongside remote export (3.7.0).

Test both destinations when changing buffering or shutdown behavior so the
local and exported streams remain complete.

## Scope observability controls

Metrics, tracing, and access logging can be controlled at entry-point and
router scope rather than only globally (3.3.0). Use the narrowest scope that
matches the desired traffic boundary and verify inherited behavior on every
router.

## Retrieve diagnostics

The API exposes a support-dump endpoint for collecting diagnostic state
(3.3.0). Protect it like other administrative API surfaces and confirm the
result reflects the provider mix in the target deployment.

The API and dashboard can be mounted under a configurable base path (3.3.0).
Account for that prefix in reverse-proxy routing, redirects, probes, and links.

## Use dashboard additions

The Web UI offers an automatic theme and makes it the default (3.4.0). The
dashboard name is configurable (3.7.0).

The certificate overview lists certificate domains, expiration, and attached
HTTP and TCP routers. Service details show server weights (3.7.0). Use these
views to confirm certificate selection and weighted-service configuration, but
verify runtime behavior with requests and logs as well.

## Read exporter secrets from files

`metrics.influxdb2.token` may point to a file containing the token (3.7.0).
Mount the file with least privilege and ensure secret rotation updates the file
visible to the Traefik process.

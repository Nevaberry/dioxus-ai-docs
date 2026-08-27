# Clients, observability, and operations

## Lambda-promtail preprocessing (3.4.0)

Lambda-promtail accepts Prometheus-style relabel configuration. Use relabeling
to mutate or filter entries before they are sent to Loki. Its Terraform
deployment also exposes a variable for the S3 bucket-notification filter
prefix.

Lambda-promtail is not covered by Promtail's deprecation or removal; do not
remove it merely because a Promtail migration is underway.

## Logcli behavior

### Proxy and common-label output (3.4.0)

`logcli` can opt in to `ProxyFromEnvironment`, allowing the environment's proxy
settings to govern its connections. Its output includes common labels, so
parsers should tolerate that additional label context.

### Delete operations (3.6.0)

`logcli` includes commands for deletion workflows. Use the CLI commands rather
than constructing deletion requests indirectly when an operational runbook can
use the supported surface.

### Custom request headers (3.7.0)

`logcli` can attach custom headers. This is useful when gateways require
deployment-specific routing or authentication headers.

## Ruler operations

### Query attribution (3.4.0)

Queries issued by the ruler carry the rule name and rule type in query tags.
Use those tags to attribute query load and troubleshoot expensive rules.

### Rule checking (3.6.0)

The ruler's rule checker can validate a namespace and group. Include this
targeted validation in rule delivery workflows when a full rule-set check is
unnecessary.

## Discovery and networking

### Configured memberlist interfaces (3.4.0)

Memberlist respects configured interface names when choosing its advertise
address. Set the intended interfaces explicitly on multi-homed hosts.

### IPv6 discovery (3.5.0)

The query frontend can resolve IPv6 addresses. IPv6 interfaces listed in
`common.instance_interface_names` are valid sources for memberlist's advertise
address.

### Component-wide IPv6 enablement (3.6.0)

`common.instance_enable_ipv6` propagates to every component. Prefer the common
setting when IPv6 behavior should be consistent throughout the deployment.

## Tracing migration (3.6.0)

Loki uses OpenTelemetry internally instead of OpenTracing. Existing operational
configuration remains available through `JAEGER_`-prefixed environment
variables, and traces are exported in Jaeger format. Update instrumentation
expectations without unnecessarily renaming the retained configuration surface.

## Fluent outputs (3.6.0)

Fluent Bit v4's `out_loki` plugin can send structured metadata. The Fluentd
plugin accepts `compress gzip`. Validate receiver limits when enabling richer
metadata or compressed transport.

## Health command (3.6.0)

Use `loki health` for command-line health checks. It provides a Loki-native
health surface for probes and operator diagnostics.

## Operational UI architecture (3.6.0)

The Operational UI's JavaScript lives in a Grafana plugin, while its server
APIs remain in Loki. Enabling the UI in the Helm chart enables those APIs on
queriers, and the gateway forwards UI requests to them. Troubleshoot the
plugin, querier API enablement, and gateway routing as separate layers.

## Canary and lokitool controls (3.7.0)

The canary accepts an arbitrary label set for its query, allowing its probe to
match deployment-specific labels.

`lokitool` adds regular-expression namespace filtering, uses the updated ruler
path, and accepts alternative TLS environment variables. Check wrapper scripts
for the path and environment-variable changes.

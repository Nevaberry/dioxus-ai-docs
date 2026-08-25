# Operator, Integrations, and Observability

Use this reference for Loki Operator reconciliation, OTLP, tracing, monitoring,
network policy, managed identity, external log shippers, and Operational UI.

## Operator identity and object storage

The Loki Operator supports managed GCP Workload Identity as of 3.4.0. Use the
managed identity path instead of embedding static credentials when the
deployment model supports it.

In 3.5.0, Operator-managed Swift storage can specify a TLS CA. In 3.6.0, the
Operator can read virtual-host-style S3 access from secrets. Validate the
rendered endpoint style, certificate trust, secret fields, and workload identity
independently for the chosen provider.

AWS STS deployments receive the region through an environment variable as of
3.7.0. Confirm the reconciled workload gets the intended region rather than
depending on an accidental default.

## OTLP labels and attribute handling

OTLP ingestion adds `deployment.environment.name` to the default label set as
of 3.4.0. The Operator also places the log-level attribute in structured
metadata.

The Operator can drop OTLP attributes as of 3.5.0. This change is classified as
breaking: review queries, routing, retention, dashboards, and usage attribution
that depend on any removed attribute. OTLP entry-metadata bytes are counted by
distributor limits, so validate effective limits after changing the retained
attribute set.

The Operator applies OpenTelemetry semantics to LokiStack authorization as of
3.6.0. Check tenant and authorization outcomes against those semantics instead
of older assumptions.

## Time sharding and generated sizing

Operator-managed LokiStack configuration can enable time-based stream sharding
as of 3.5.0. The generated sizing logic also keeps delete workers nonzero and
corrects minimum available ingesters for the `1x.pico` size. Inspect generated
worker and availability settings after upgrading small installations.

## OpenTelemetry tracing backend

Loki uses OpenTelemetry internally instead of OpenTracing as of 3.6.0. It still
accepts tracing configuration through `JAEGER_`-prefixed environment variables
and exports Jaeger-format traces. Update integration expectations while
preserving supported environment configuration.

## Move meta-monitoring ownership

In 3.6.0, meta-monitoring responsibilities move from the Grafana
meta-monitoring Helm chart to the Grafana Kubernetes Monitoring Helm chart.
Move configuration and release ownership, and remove duplicate collection when
both charts overlap during migration.

The 3.4.0 Loki chart also adds overrides-exporter support. The nginx service
stops receiving a ServiceMonitor in 3.5.0, so verify the intended scrape target
and monitor ownership explicitly.

## Deploy the Operational UI plugin

The Operational UI's JavaScript moves to a Grafana plugin in 3.6.0, while its
server APIs remain in Loki. Enabling the UI through the Helm chart enables
those APIs on queriers, and the gateway forwards UI requests to them.

Treat the plugin, querier API enablement, and gateway route as one feature
path. A successful plugin installation alone does not prove the Loki APIs or
gateway forwarding are available.

## Fluent integrations

Fluent Bit v4's `out_loki` plugin can send structured metadata as of 3.6.0.
The Fluentd plugin accepts `compress gzip`. Verify metadata mapping and server
limits for Fluent Bit, and verify both content encoding and server support when
enabling Fluentd compression.

## NetworkPolicies and ingress

The Operator can deploy NetworkPolicies with a LokiStack as of 3.6.0. As of
3.7.0, it can suppress ingress and customize the gateway server certificate.
Review generated ingress, certificate references, Services, and policies
together so a disabled ingress does not leave an assumed route or certificate
consumer.

On OCP 4.20, the Operator no longer deploys NetworkPolicies automatically.
Provide equivalent policies explicitly where isolation is required.

## Metrics authentication

As of 3.7.3, Operator metrics authentication no longer depends on
`kube-rbac-proxy`. Update manifests, security policies, image allowlists, and
scrape configuration that assumed the proxy container or its ports.

## OpenShift stream labels

The Operator changes default OpenShift stream labels in 3.7.0 as a breaking
update. Diff the effective label set and revalidate tenant selection, queries,
alerts, dashboards, retention, and cardinality.

## IPv4 and IPv6 interface selection

Memberlist respects configured interface names when choosing its advertise
address as of 3.4.0. In 3.5.0, IPv6 interfaces listed in
`common.instance_interface_names` are valid advertise-address sources, and the
query frontend can resolve IPv6 addresses.

As of 3.6.0, `common.instance_enable_ipv6` propagates to every component.
Validate mixed-family DNS and interface selection across all workloads rather
than assuming the common setting affects only one process.

## Integration validation checklist

- Confirm managed identity, secret-based storage, endpoint style, TLS CA, and
  region injection for the selected object store.
- Diff default and dropped OTLP attributes and the resulting structured
  metadata and labels.
- Verify generated delete workers and ingester availability for small sizes.
- Trace a request through the OpenTelemetry backend and Jaeger export.
- Ensure exactly one monitoring chart owns each collection responsibility.
- Test the Operational UI plugin, querier APIs, and gateway forwarding end to
  end.
- Send structured metadata through Fluent Bit and gzip output through Fluentd.
- Inspect ingress, gateway certificates, metrics authentication, and
  NetworkPolicies, especially on OCP 4.20.
- Test memberlist advertisement and query-frontend resolution on the deployed
  address families.

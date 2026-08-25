# Helm and Operator deployment

## Helm rendering and ownership

### Checksums, ownership, and conditional resources (3.4.0)

ConfigMap and Secret checksums cover only `.data`. The installation manager,
not the chart template, sets `managed-by`.

Ruler and index-gateway templates include their namespace. Headless backend
gRPC ports declare `appProtocol: tcp`. Ruler configuration renders only when
the ruler is enabled and defaults its WAL directory. Setting
`test.enabled=false` suppresses the test pod.

### Restored and expanded `tpl` evaluation (3.5.0, 3.6.0)

The chart restores `tpl()` evaluation for read, write, and backend pods, and
provisioners can be namespaced. It also applies `tpl` to `pattern_ingester`,
`ingester_client`, and `loki.operational_config`.

### Naming and Service controls (3.7.0)

`nameOverride` is evaluated with `tpl`. The chart can toggle the query-frontend
gRPC load-balancing port and set the Service `trafficDistribution` field.

## Workload placement and rollout

### Overrides exporter and zone-aware controls (3.4.0)

The chart supports overrides-exporter and exposes `topologySpreadConstraints`
for admin-api pods and distributed deployments. Zone-aware replication splits
the ingester HPA. Rollout-group values and ingester names can be prefixed.

### Startup, probes, and placement (3.7.0)

Distributor and read workloads support startup probes. SingleBinary supports
`topologySpreadConstraints`, and the canary `readinessProbe` is configurable.
The filesystem-group change policy is `OnRootMismatch`.

## Workload extensibility and persistence (3.6.0)

The canary can run as a Deployment rather than a DaemonSet and can batch log
pushes. The chart supports user namespaces and configurable init containers for
backend, bloom, distributor, query, read, and write workloads.

PVC access modes and claim-template labels are configurable. PVCs are retained
when a StatefulSet scales down but remain deletable with the StatefulSet.

As of 3.7.0, `volumeAttributesClassName` can be set on volume claim templates.
`dnsConfig` renders for backend, read, write, SingleBinary, and table-manager
workloads. The global image registry applies to sidecars.

## Authentication and caching (3.6.0)

The chart can use external Memcached and an L2 chunks cache. Tenant
authentication can be configured with a password hash instead of a plaintext
password.

## Storage and ruler configuration

### Object-store value rename (3.5.0)

Use `object_store.storage_prefix`; `object_store.prefix` is no longer the chart
value. The nginx Service no longer receives a ServiceMonitor.

### Full configuration and ruler integration (3.6.0)

The chart exposes the full storage configuration and can bypass generated
S3/GCS/Azure settings. It supports separate ruler storage. Ruler pods can run
the rules sidecar, and alert rules can include custom annotations.

### Backend-sensitive bucket validation (3.7.0)

Chunk bucket names are not required when using an S3 URL, MinIO, or local disk.
Ruler bucket names are optional with local ruler storage.

## Block-building deployment (3.6.0)

The chart exposes `block_builder` configuration for the Kafka record-consumer
and block-building path. Size and deploy it as part of the Kafka ingestion
architecture, not as an unrelated chart workload.

## Meta-monitoring migration (3.6.0)

Meta-monitoring responsibilities move from the Grafana meta-monitoring Helm
chart to the Grafana Kubernetes Monitoring Helm chart. Update ownership and
values automation around the destination chart.

## Chart repository transfer (3.7.0)

Effective March 16, 2026, the open-source Loki chart moved to
`grafana-community/helm-charts` for community maintenance. The GEL chart remains
separately maintained. Point chart source references and update automation at
the new open-source repository where applicable.

## Loki Operator capabilities

### Identity, labels, and OTLP defaults (3.4.0)

The Operator supports managed GCP Workload Identity and places the log-level
attribute in structured metadata. OTLP ingestion adds
`deployment.environment.name` to the default label set.

### Ingestion, storage, and sizing (3.5.0)

The Operator can drop OTLP attributes, configure a TLS CA for Swift, and enable
time-based stream sharding. OTLP attribute dropping is a breaking change;
review generated ingestion behavior during upgrades.

Generated sizing keeps delete workers nonzero and corrects the minimum
available ingesters for the `1x.pico` size.

### Networking, storage, and authorization (3.6.0)

The Operator can create NetworkPolicies with a LokiStack, configure
virtual-host-style S3 access from secrets, and apply OpenTelemetry semantics to
LokiStack authorization.

### Ingress, certificates, and metrics authentication (3.7.0)

The Operator can suppress ingress and customize the gateway server certificate.
As of 3.7.3, metrics authentication no longer depends on `kube-rbac-proxy`.

### OpenShift and AWS behavior (3.7.0)

Default OpenShift stream labels changed as a breaking update. On OCP 4.20, the
Operator no longer deploys NetworkPolicies automatically. AWS STS deployments
receive the region through an environment variable.

# Helm and Deployment

Use this reference while editing values, rendering manifests, or validating
workload lifecycle. Render the exact chart version used by the deployment;
several values are templates rather than literal strings.

## Rendering, names, and ownership

### Template evaluation

The chart restored `tpl()` evaluation for read, write, and backend pods in
3.5.0. By 3.6.0 it also applied `tpl` to `pattern_ingester`,
`ingester_client`, and `loki.operational_config`. In 3.7.0, `nameOverride` is
templated as well. Quote and scope template expressions carefully, then inspect
rendered names and configuration rather than reading the values file as the
final result.

Provisioners can be namespaced as of 3.5.0. Ruler and index-gateway templates
include their namespace as of 3.4.0, which matters to name-based policy,
ownership, and diff tooling.

### Ownership and rollout checksums

Since 3.4.0, the installation manager—not the chart template—sets
`managed-by`. ConfigMap and Secret checksums are computed only over `.data`.
Metadata-only changes therefore do not have the same checksum-triggered rollout
effect as data changes.

### Tests and ruler rendering

Set `test.enabled=false` to suppress the chart test pod. Ruler configuration is
rendered only when the ruler is enabled and receives a default WAL directory.
These behaviors date to 3.4.0.

## Services and ports

Headless backend gRPC ports declare `appProtocol: tcp` as of 3.4.0. The nginx
service no longer receives a ServiceMonitor as of 3.5.0; monitoring automation
must not depend on that generated object.

In 3.7.0, the chart can toggle the query-frontend gRPC load-balancing port and
set the Service `trafficDistribution` field. Validate clients and cluster
support when changing either value.

## Workload topology and scaling

### Topology controls

The 3.4.0 chart adds `topologySpreadConstraints` for admin-api pods and
distributed deployments. Zone-aware replication splits the ingester HPA, and
rollout-group values and ingester names can be prefixed.

SingleBinary gains `topologySpreadConstraints` in 3.7.0. Render selectors and
topology keys to ensure the constraints match the generated pod labels.

### Startup and readiness

The 3.7.0 chart adds startup probes for distributor and read workloads and
makes the canary `readinessProbe` configurable. Its filesystem group change
policy becomes `OnRootMismatch`; account for existing volume ownership when
testing startup.

### Canary mode and batching

As of 3.6.0, the canary can run as a Deployment instead of a DaemonSet and can
batch log pushes. Pick a controller based on the coverage behavior required,
and include batching in latency and failure tests.

## Init containers and user namespaces

The 3.6.0 chart supports user namespaces and configurable init containers for
backend, bloom, distributor, query, read, and write workloads. Check security
contexts, volume ownership, ordering, and the effective configuration for every
enabled workload rather than assuming one shared pod template.

## Persistence and volume lifecycle

PVC access modes and claim-template labels are configurable as of 3.6.0. PVCs
are retained when a StatefulSet scales down but remain deletable with the
StatefulSet. Align this lifecycle with the storage class and operational backup
policy.

The 3.7.0 chart supports `volumeAttributesClassName` on volume claim templates.
Validate the Kubernetes and CSI support before setting it.

## DNS configuration

In 3.7.0, `dnsConfig` renders for backend, read, write, SingleBinary, and
table-manager workloads. Confirm that each enabled workload gets the expected
resolver options and that values do not exceed platform constraints.

## Storage generation and validation

The chart exposes the full storage configuration as of 3.6.0 and can bypass
generated S3, GCS, and Azure settings. Use bypass mode only when supplying a
complete configuration. Separate ruler storage is supported.

Object-store values use `object_store.storage_prefix`, not
`object_store.prefix`, as of 3.5.0. The object-store client accepts dashes in
`storage_prefix` as of 3.6.0.

With 3.7.0 chart validation, a chunk bucket name is not required when using an
S3 URL, MinIO, or local disk. A ruler bucket name is optional with local ruler
storage. Do not add dummy bucket values merely to satisfy older validation
assumptions.

## Ruler integration

Ruler pods can run the rules sidecar as of 3.6.0, and alert rules can carry
custom annotations. Render sidecar mounts, discovery configuration, and rule
metadata together. Separate ruler storage can be wired independently of the
main storage configuration.

## Caches and authentication

The 3.6.0 chart can use external Memcached and an L2 chunks cache. Validate
addresses, timeouts, credentials, and failure behavior for each layer.

Tenant authentication can receive a password hash rather than plaintext.
Confirm the selected value is already in the expected hashed form; do not hash
or encode it twice in templating.

## Kafka block-builder deployment

The Helm chart exposes `block_builder` configuration as of 3.6.0 for the path
that consumes Kafka records and builds blocks. Coordinate chart topology with
the Kafka clients and tenant-topic strategy described in the ingestion
reference.

## Global images and sidecars

As of 3.7.0, the global image registry applies to sidecars. In restricted or
mirrored environments, verify both primary images and every generated sidecar
resolve through the intended registry.

## Chart source migration

On March 16, 2026, the open-source chart moved to
`grafana-community/helm-charts`; the GEL chart did not move with it. Update
source URLs and automation as part of the 3.7.0 migration, then compare the
rendered resources before deployment.

## Render-time checklist

- Evaluate every `tpl`-enabled value with production-like inputs.
- Diff names, namespaces, labels, ownership metadata, and checksum annotations.
- Verify gRPC ports, `trafficDistribution`, probes, and ServiceMonitor objects.
- Check topology constraints and zone-aware HPA output.
- Inspect user namespaces, init containers, security contexts, and DNS settings.
- Test PVC retention, access modes, labels, and volume attribute classes.
- Confirm storage generation or bypass mode supplies a complete valid config.
- Resolve primary, canary, rules-sidecar, and other sidecar images through the
  intended registry.

# Helm and Operations

Use this reference when rendering the chart, operating controller components, or
building ESO. Always inspect the values schema for the exact chart installed.

## Images, chart delivery, and releases

### Default image registry (since 1.1.0)

The default image repository moved from
`oci.external-secrets.io/external-secrets/external-secrets` to
`ghcr.io/external-secrets/external-secrets` because the old registry is being
retired. The chart repository remains on GitHub Pages. Move any pinned or
overridden repository to GHCR.

### Flux OCI chart layer (since 2.2.0)

Flux `OCIRepository` users must select and extract the Helm chart content layer:

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: OCIRepository
metadata:
  name: eso-oci
spec:
  interval: 1m0s
  provider: generic
  ref:
    tag: 2.2.0
  url: oci://ghcr.io/external-secrets/charts/external-secrets
  layerSelector:
    mediaType: application/vnd.cncf.helm.chart.content.v1.tar+gzip
    operation: extract
```

### Release and custom-build targets

- Native `darwin_arm64` artifacts are published from 1.1.0 for Apple Silicon.
- Every provider has a build tag from 1.1.0, allowing custom binaries to omit
  unwanted providers.

## Workload customization

- Init containers can be configured for controller deployments from 0.19.0.
- Global chart values became available in 1.2.0 for common deployment settings.
- `hostUsers` can be controlled from 1.3.0.
- Chart-managed certificate algorithms can be controlled from 1.3.0.
- `hostAliases` can be assigned to chart-managed pods from 2.0.0.
- `schedulerName` and `runtimeClassName` are opt-in pod settings from 2.9.0.
- HTTP/2 serving became configurable in 0.20.0, including the ability to disable
  it for a stricter security posture.

## Controller selection and CRDs

### Keep resource and reconciler switches paired

CRD installation defaults on. Disabling a CRD does not stop its reconciler, so
pair each `crds.create*` switch with the corresponding `process*` switch. Disabling
the webhook also requires disabling CRD conversion, or the API server keeps
calling a nonexistent conversion endpoint.

```yaml
crds:
  createPushSecret: false
  conversion:
    enabled: false
processPushSecret: false
webhook:
  create: false
```

### Controller switches

- `processClusterGenerator` controls cluster-scoped generator processing from
  0.20.0.
- A controller flag can enable or disable SecretStore reconciliation from 1.2.0.
- The chart can control behavior when Prometheus CRDs are absent from 0.20.0.

## Availability and leader election

The controller defaults to one replica. Leader election is available, while its
liveness, readiness, and PodDisruptionBudget are disabled by default. Webhook and
cert-controller readiness is enabled by default, but each also defaults to one
replica with liveness and PDB disabled.

Enable the controls needed for the availability target, and assign separate lease
IDs to independent ESO deployments sharing a namespace:

```yaml
replicaCount: 2
leaderElect: true
leaderElectionID: payments-external-secrets
livenessProbe:
  enabled: true
readinessProbe:
  enabled: true
podDisruptionBudget:
  enabled: true
```

- The controller gained a liveness probe in 0.20.0.
- Deployment readiness-probe configuration arrived in 2.2.0.
- Cert-controller and webhook liveness probes arrived in 2.4.0.
- Webhook `startupProbe` configuration arrived in 2.8.0.
- `--leader-election-id` allows explicit HA identity from 2.4.0.
- Leader-election lease timings are configurable from 2.8.0.
- A chart flag can enable the cert-manager leader from 2.1.0.

## PodDisruptionBudgets

- PDB values expressed as percentages render correctly from 0.18.0.
- The PDB spec renders when `minAvailable` or `maxUnavailable` is explicitly zero
  from 2.6.0; zero is no longer mistaken for unset.

## RBAC rendering and scoping

- The `serviceaccounts/token` create rule is rendered conditionally from 2.5.0,
  avoiding the permission when unused.
- Write access to `externalsecrets` is gated by `processClusterExternalSecret`
  from 2.5.0.
- With `scopedRBAC` enabled and no `scopedNamespace`, the namespace defaults to
  `.Release.Namespace` from 2.5.0.
- Cert-controller RBAC is limited to its managed CRDs and webhook Secret from
  2.7.0.
- `aggregateToAdmin` controls chart RBAC aggregation into the Kubernetes admin
  role from 2.8.0.
- An optional chart-managed `NetworkPolicy` is available from 2.8.0.

## Webhooks and certificates

- `ValidatingWebhookConfiguration` annotations are supported from 0.16.0.
- SecretStore `failurePolicy` is determined dynamically from 2.0.0.
- The chart applies `failurePolicy` to the `ClusterSecretStore` webhook from
  2.4.0.
- Cert-controller metrics Service annotations render correctly from 2.1.0.

## Metrics and dashboards

- Secure metrics serving became available in 0.20.0.
- Authentication and authorization through `FilterProvider` became available for
  metrics in 2.5.0.
- Keeper exposes `provider_api_calls_count` from 2.6.0.
- Grafana dashboard resources accept extra labels from 0.20.0, allowing different
  Grafana selectors to discover separate dashboards.

When creating network rules, expected inbound ports are controller metrics 8080
and optional health 8082; webhook admission 10250, metrics 8080, health 8081; and
cert-controller metrics 8080, health 8081.

## Requeueing and logs

- Failed reconciliations retry substantially less aggressively from 0.14.0.
- `storeRequeueInterval` is exposed through chart values from 2.7.0.
- Secret deletions and Secret data-key changes are logged from 2.7.0.

## Dashboard and monitoring defaults

Do not assume observability controls are enabled merely because the chart renders
secure pod contexts. Metrics TLS/authentication and NetworkPolicy default off.
Enable them deliberately and scope access to the intended monitoring clients.

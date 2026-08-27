# Helm, operations, and security

Read this reference when installing or upgrading the Helm chart, configuring
controllers and CRDs, narrowing RBAC, exposing health or metrics endpoints, or
verifying release artifacts.

## Upgrade and release compatibility

### Support window

ESO supports only its newest minor release; publishing the next minor
automatically deprecates the previous minor. At the operations snapshot, 2.8
was the supported line, guaranteed Kubernetes 1.35, and would reach end of life
when 2.9 shipped. Image rebuilds, Go dependency updates, and security or bug
fixes target the supported line. Upgrade one minor at a time.

### Deprecation boundary

The protected surface includes API object specs, status and conditions, enums
and constants, controller flags and environment variables, metrics, and
documented `ExternalSecret` update behavior.

Helm charts, releases, images, signatures, OLM builds, source imports, and
unspecified behavior are outside that guarantee. Introducing a deprecation
requires a minor release during 0.x and a major release from 1.x onward; only
in-scope removals inherit Kubernetes deprecation timelines.

The component policy still classifies ESO as beta: features are enabled by
default and considered safe to enable, but schemas or semantics may change
incompatibly with migration instructions, and the policy does not recommend
beta software for production.

### Removed providers

Alibaba and Device42 were removed in 2.0.0 because they were unsupported and
unmaintained. Migrate those stores before upgrading.

### Image registry and release platforms

The default image repository moved in 1.1.0 from
`oci.external-secrets.io/external-secrets/external-secrets` to
`ghcr.io/external-secrets/external-secrets`; the old image domain was temporary.
Pinned and overridden repositories must move to GHCR. The chart repository
remains on GitHub Pages.

Release artifacts include native `darwin_arm64` builds since 1.1.0.

### Flux OCIRepository content layer

Flux installations fetching the chart as an `OCIRepository` must select and
extract the Helm chart content layer when upgrading to 2.2.0:

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

## Chart customization

### Global values and pod settings

The chart supports global values for common deployment settings (since 1.2.0),
init containers (since 0.19.0), `hostAliases` (since 2.0.0), and `hostUsers` plus
certificate-algorithm controls (since 1.3.0).

Since 2.9.0, opt-in `schedulerName` and `runtimeClassName` values select a
non-default scheduler or Kubernetes RuntimeClass without patching rendered
workloads.

### Controller processing flags

`processClusterGenerator` controls cluster-scoped generator processing (since
0.20.0). The chart gates `externalsecrets` write RBAC on
`processClusterExternalSecret` (since 2.5.0), so disabling that reconciler no
longer leaves its write permission behind. SecretStore reconciliation also has
a controller enable/disable flag (since 1.2.0).

### Webhook registration

`ValidatingWebhookConfiguration` accepts annotations (since 0.16.0).
SecretStore webhook `failurePolicy` is determined dynamically (since 2.0.0),
and chart configuration applies `failurePolicy` to the `ClusterSecretStore`
webhook correctly (since 2.4.0). Webhook provider requests include the
`ExternalSecret` namespace (since 0.20.0).

### Dashboards and Prometheus CRDs

Grafana dashboard resources accept extra labels for discovery by distinct
Grafana instances (since 0.20.0). The chart can control its response when
Prometheus CRDs are missing (since 0.20.0); render the chart in clusters without
those CRDs before relying on the selected behavior.

## CRDs, conversion, and namespace scope

### Separate switches

CRD installation defaults on, but disabling a CRD does not disable its
reconciler. Pair each disabled `crds.create*` setting with its corresponding
`process*` setting or the controller logs missing-CRD errors. Disabling the
webhook also requires disabling CRD conversion, or the API server keeps calling
an absent conversion endpoint.

```yaml
crds:
  createPushSecret: false
  conversion:
    enabled: false
processPushSecret: false
webhook:
  create: false
```

### Namespace-only installation

Namespaced resources cannot reference a namespaced store, Secret, or referent
in another namespace. A namespace-only installation uses scoped roles and
implicitly disables cluster-scoped controllers:

```yaml
scopedRBAC: true
scopedNamespace: payments
```

When `scopedRBAC` is true and `scopedNamespace` is unset, the namespace defaults
to `.Release.Namespace` (since 2.5.0). Cluster-scoped resources require separate
review because they can span namespace boundaries.

## RBAC and controller authority

### ServiceAccount token delegation

Provider authentication through `serviceAccountRef` requires TokenRequest
access. The default controller role can create tokens for any ServiceAccount in
scope. Disable that broad rule, then grant token creation only for each
referenced account with `resourceNames`:

```yaml
rbac:
  serviceAccountTokenCreate: false
```

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: eso-token-provider-reader
  namespace: payments
rules:
  - apiGroups: [""]
    resources: ["serviceaccounts/token"]
    resourceNames: ["provider-reader"]
    verbs: ["create"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: eso-token-provider-reader
  namespace: payments
subjects:
  - kind: ServiceAccount
    name: external-secrets
    namespace: external-secrets
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: eso-token-provider-reader
```

The Helm rule for `serviceaccounts/token` is conditional since 2.5.0, avoiding
that permission where it is not required.

### Role aggregation and cert-controller scope

`aggregateToAdmin` controls aggregation into the Kubernetes admin role (since
2.8.0). Cert-controller RBAC is limited to the CRDs it manages and the webhook
Secret (since 2.7.0). Review default aggregation into view and edit roles as
well as admin aggregation.

### Generic targets

`genericTargets.enabled` defaults false. Enabling it grants create, update, and
delete access to ConfigMaps plus configured verbs for every resource listed
under `genericTargets.resources`. Treat each API group as an explicit privilege
expansion and supply suitable encryption and admission controls.

## Probes, metrics, and availability

### Probe configuration

The controller gained a liveness probe in 0.20.0. Chart-configurable readiness
for the external-secrets Deployment arrived in 2.2.0. Cert-controller and
webhook liveness probes arrived in 2.4.0, and webhook `startupProbe` support in
2.8.0.

### PodDisruptionBudgets

The chart renders percentage PDB values (since 0.18.0) and preserves explicit
zero-valued `minAvailable` or `maxUnavailable` settings (since 2.6.0) instead of
treating zero as unset.

### Availability defaults

The controller defaults to one replica with leader election, liveness,
readiness, and PDB disabled. Webhook and cert-controller readiness is enabled,
but each defaults to one replica with liveness and PDB disabled. Enable the
required controls deliberately:

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

Independent deployments in one namespace need distinct lease IDs. The
controller accepts `--leader-election-id` (since 2.4.0), and leader-election
lease timings are configurable (since 2.8.0). A chart flag can enable the
cert-manager leader (since 2.1.0).

### Metrics

Metrics can be served securely (since 0.20.0) and can use `FilterProvider`
authentication and authorization (since 2.5.0). The cert-controller metrics
Service applies annotations correctly (since 2.1.0). Keeper exposes the
provider-specific `provider_api_calls_count` metric (since 2.6.0).

The chart's metrics TLS and authentication defaults are off. Treat exposure as
an explicit design decision rather than assuming secure serving is enabled.

## Pod and network security

### Pod defaults

Default security contexts use the restricted profile: non-root UID 1000,
read-only root filesystem, no privilege escalation, all capabilities dropped,
and `RuntimeDefault` seccomp. The chart is nevertheless delivered as-is, not as
a complete hardened deployment.

### HTTP/2 and NetworkPolicy

HTTP/2 serving is configurable since 0.20.0, allowing it to be disabled for the
deployment's security posture. The chart can create an optional `NetworkPolicy`
since 2.8.0; it is not automatically a complete egress policy.

The controller needs egress to the Kubernetes API and selected providers; the
webhook and cert controller need the API. Prefer private provider endpoints and
allow DNS plus only required API/provider destinations.

Expected inbound ports are controller metrics 8080 and optional health 8082;
webhook admission 10250, metrics 8080, and health 8081; cert-controller metrics
8080 and health 8081. Policy engines should deny unused providers, constrain
remote-key prefixes, and restrict `ClusterSecretStore` references.

## Providers and custom builds

Provider maturity does not imply feature parity. At the support snapshot, AWS
Secrets Manager, AWS Parameter Store, Akeyless, Azure Key Vault, CyberArk
Secrets Manager, GCP Secret Manager, HashiCorp Vault, IBM Cloud Secrets Manager,
Oracle Vault, and Previder were stable; Kubernetes and SecretServer were beta;
all other listed providers were alpha. Check find, metadata, authentication,
validation, push, merge, and delete separately.

All providers have build tags since 1.1.0, allowing unused providers to be
excluded from custom builds.

## Observability and artifacts

The controller logs Secret deletion and data-key changes (since 2.7.0), making
those reconciliation effects visible without comparing full secret values.

Release images carry keyless Cosign signatures, SLSA provenance attestations,
and SPDX JSON SBOM attestations. Verify an immutable digest and require the
certificate issuer `https://token.actions.githubusercontent.com` and the
External Secrets release workflow subject on `refs/heads/main`. Signatures and
provenance are outside the deprecation guarantee.

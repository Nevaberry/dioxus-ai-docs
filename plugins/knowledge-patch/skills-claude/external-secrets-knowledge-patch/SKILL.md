---
name: external-secrets-knowledge-patch
description: External Secrets Operator
version: 2.8.0
license: MIT
metadata:
  author: Nevaberry
---


# External Secrets Operator Compatibility

Use this skill when designing, upgrading, operating, or troubleshooting External
Secrets Operator (ESO) resources, providers, generators, Helm deployments, and
push workflows. Check the installed chart and controller versions before applying
version-dependent guidance, and trust live CRDs and rendered manifests when they
differ from examples.

## Topic index

| Reference | Topics |
| --- | --- |
| [API and reconciliation](references/api-and-reconciliation.md) | `ExternalSecret`, stores, refresh behavior, validation, metadata, and reconciliation |
| [Cloud and Vault providers](references/cloud-and-vault-providers.md) | AWS, GCP, Azure, Kubernetes, Vault, OpenBao, IBM, Yandex, Cloud.ru, Volcengine, and Barbican |
| [Helm and operations](references/helm-and-operations.md) | Chart values, probes, HA, metrics, logs, CRDs, RBAC, and release artifacts |
| [Integration providers](references/integration-providers.md) | 1Password, Akeyless, BeyondTrust, Conjur, Delinea, Doppler, Infisical, Passbolt, and other integrations |
| [PushSecret workflows](references/push-secrets.md) | `PushSecret`, `ClusterPushSecret`, `dataTo`, policies, mapping, fan-out, and cleanup |
| [Security and support](references/security-and-support.md) | Support policy, deprecation boundaries, hardening, namespace isolation, and provider maturity |
| [Templates, generators, and CLI](references/templates-generators-and-cli.md) | Template behavior, functions, generators, rendering, and `esoctl` |

## Breaking changes and migrations

### Removed providers

Alibaba and Device42 were removed in 2.0.0 because they were unsupported and
unmaintained. Migrate any stores that use them before upgrading.

### Image registry migration

The chart default moved in 1.1.0 from
`oci.external-secrets.io/external-secrets/external-secrets` to
`ghcr.io/external-secrets/external-secrets`. Update pinned or overridden image
repositories; the chart repository remains on GitHub Pages.

### Flux OCI chart extraction

From 2.2.0, a Flux `OCIRepository` must select and extract the Helm chart content
layer:

```yaml
spec:
  url: oci://ghcr.io/external-secrets/charts/external-secrets
  layerSelector:
    mediaType: application/vnd.cncf.helm.chart.content.v1.tar+gzip
    operation: extract
```

### Removed template and generator behavior

- `getHostByName` was removed from template functions in 2.3.0. Replace templates
  that perform DNS lookups.
- The `STSSessionToken` generator lost JWT-token authentication in 0.19.0. Choose
  another supported authentication route.
- Kubernetes-provider pushes replace the complete remote Secret from 2.7.0;
  keys absent from the pushed Secret are removed instead of retained.
- Optional `ExternalSecret` strategy fields are no longer defaulted into the
  stored object in 2.9.0. Do not require omitted fields to be written back.

### API transition

Provider examples use `external-secrets.io/v1`. Legacy beta-version serving became
configurable in 1.3.0; treat it as a migration aid, not a reason to postpone
manifest conversion.

## Reconciliation quick reference

### Refresh policies

- `Periodic` is the default. A zero `refreshInterval` performs the initial fetch
  and create but no later update.
- `OnChange` ignores the interval and reacts to `ExternalSecret` metadata or spec
  changes.
- `CreatedOnce` repairs a changed or deleted target while the same
  `ExternalSecret` survives. Recreating the resource resets status and can rewrite
  an existing target.
- For a generated credential intended to survive source deletion and reject
  replacement, combine `refreshPolicy: CreatedOnce`, `creationPolicy: Orphan`,
  and `target.immutable: true`.

### Manual refresh

Use different annotation names:

```sh
kubectl annotate es my-es force-sync=$(date +%s) --overwrite
kubectl annotate ces my-ces external-secrets.io/force-sync=$(date +%s) --overwrite
```

Changing or deleting the cluster annotation propagates to owned resources. Read
[API and reconciliation](references/api-and-reconciliation.md) for metadata,
selectors, retry settings, status, dynamic targets, and sync windows.

### Creation and store behavior

- `CreateOrMerge` is accepted as an `ExternalSecret` target creation policy from
  2.8.0.
- `SecretStore.refreshInterval` accepts duration strings from 2.8.0.
- A store can be marked deprecated from 1.2.0.
- A `SecretStore` can report unknown status when its state cannot be determined.
- Stores without an explicit maintainer emit controller and admission warnings;
  the maintenance annotation suppresses only the controller event.

## Push quick reference

Use exactly one `selector` source in a namespaced `PushSecret`: a Kubernetes
Secret or `generatorRef`. Transform it with `template` or `templateFrom`, then map
outgoing keys through `data[].match`. `updatePolicy: Replace` allows overwrites;
`deletionPolicy` defaults to `None`, so set `Delete` when remote cleanup is
required.

`dataTo` bulk expansion, introduced in the `2.3-datato` batch, can select all
source keys or a regexp-filtered subset. Each entry needs a `storeRef` that also
appears in `secretStoreRefs`. Without `remoteKey`, matches become separate remote
secrets; with `remoteKey`, they become one JSON object.

Expansion applies the template first, converts keys before matching and rewriting,
and gives an explicit `data` entry precedence for the same original Kubernetes
key. Invalid regexps, duplicate remote keys, and conflicting sources fail
reconciliation; no matches is a successful no-op. Read
[PushSecret workflows](references/push-secrets.md) before relying on deletion,
fan-out, cross-namespace, or provider-specific behavior.

## Helm and operations quick reference

### Keep CRDs and controllers aligned

Disabling CRD creation does not disable its reconciler. Pair each disabled
`crds.create*` value with the matching `process*` value. If the webhook is
disabled, disable CRD conversion too, or the API server calls a missing endpoint.

```yaml
crds:
  createPushSecret: false
  conversion:
    enabled: false
processPushSecret: false
webhook:
  create: false
```

### Availability is mostly opt-in

The controller defaults to one replica; its liveness, readiness, and PDB are not
enabled by default. Webhook and cert-controller readiness are enabled, but their
liveness and PDB remain off. For HA, enable replicas and leader election and use a
distinct `leaderElectionID` for each ESO deployment in a namespace. Lease timing
is configurable from 2.8.0, and a lower-level `--leader-election-id` flag exists
from 2.4.0.

### Metrics, logs, and probes

- Secure metrics serving arrived in 0.20.0; metrics authentication and
  authorization through `FilterProvider` arrived in 2.5.0.
- The controller gained a liveness probe in 0.20.0, configurable readiness in
  2.2.0, and cert-controller/webhook liveness in 2.4.0.
- Webhook startup probes are configurable from 2.8.0.
- Keeper exposes `provider_api_calls_count` from 2.6.0.
- Secret deletions and data-key changes are logged from 2.7.0.

Read [Helm and operations](references/helm-and-operations.md) for all chart values,
probe details, RBAC gates, scheduling, and observability changes.

## Security quick reference

Do not infer a hardened deployment from the restricted default pod security
context. NetworkPolicies and metrics TLS/authentication are off by default, while
broad ServiceAccount-token creation and role aggregation are on. Limit egress to
DNS, the Kubernetes API, and required provider endpoints; constrain store access,
remote-key prefixes, enabled providers, and generic-target permissions.

For namespace-only installs, set both `scopedRBAC: true` and `scopedNamespace`.
Disable blanket token creation with `rbac.serviceAccountTokenCreate: false`, then
grant `serviceaccounts/token` creation by `resourceNames` for each referenced
ServiceAccount. Treat `genericTargets.enabled` as an explicit controller-privilege
expansion.

Verify release images by immutable digest. Keyless signatures, SLSA provenance,
and SPDX JSON SBOM attestations are available, but release artifacts and
signatures are outside the compatibility guarantee. Read
[Security and support](references/security-and-support.md) before making support,
hardening, or provider-maturity assumptions.

## Provider selection quick reference

Provider maturity does not imply capability parity. Confirm each provider's
support for find, metadata, referent authentication, validation, push, and
merge/delete operations. In particular:

- OpenBao has a dedicated provider from 2.7.0; older configurations can use Vault
  compatibility, but new configurations can use OpenBao trust, namespaces,
  `userPass`, or `appRole` directly.
- Vault supports Pod Identity, GCP Workload Identity, token caching with expiry
  validation, namespace-aware client caching, TLS roles, dynamic GET parameters,
  and push operations; load the provider reference for version details.
- AWS metadata synchronization occurs even when a secret value is unchanged, and
  explicit credentials no longer fall back to EC2 instance metadata.
- Kubernetes push replaces the whole Secret, while whole-Secret deletion and
  `SecretExists` are separately supported.
- A provider classified read-write can receive `PushSecret`; unsupported Conjur
  push and delete calls return explicit errors.

Use [Cloud and Vault providers](references/cloud-and-vault-providers.md) or
[Integration providers](references/integration-providers.md) for the exact
provider capability and authentication changes.

## Templates and generators quick reference

Templates support custom delimiters, native values in value scope, templated
`dataFrom` JSONPath, `certSANs`, hexadecimal conversion with `hexdec`, slice
notation, mixed-case generic target paths, decoded `templateFrom` values, and
template-defined finalizers. Source null-byte handling is configurable. Review
[Templates, generators, and CLI](references/templates-generators-and-cli.md) for
generator-specific fields, removed behavior, and rendering commands.

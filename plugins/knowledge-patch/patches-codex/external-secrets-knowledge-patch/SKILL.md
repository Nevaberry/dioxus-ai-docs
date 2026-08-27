---
name: external-secrets-knowledge-patch
description: External Secrets Operator
version: "2.8.0"
license: MIT
metadata:
  author: Nevaberry
---


# External Secrets Operator Knowledge Patch

Use this skill when designing, reviewing, upgrading, or troubleshooting
External Secrets Operator (ESO) resources, providers, Helm installations,
push workflows, generators, and templates.

## How to use this skill

1. Identify the installed chart, controller, and CRD versions from the project.
2. Read the reference matching the resource or provider being changed.
3. Treat manifests, rendered charts, CRDs, controller flags, and observed status
   as the source of truth when they differ from this guidance.
4. Review breaking behavior and security implications before an upgrade.
5. Validate the rendered Kubernetes resources and provider-side effects.

## Reference index

| Reference | Read for |
| --- | --- |
| [API and reconciliation](references/api-and-reconciliation.md) | `ExternalSecret`, stores, refresh policies, metadata, selectors, status, reconciliation, and API validation |
| [Cloud and Kubernetes providers](references/cloud-and-kubernetes-providers.md) | AWS, GCP, Azure, IBM, Kubernetes, Cloud.ru, Yandex, Volcengine, Barbican, and other cloud providers |
| [Helm, operations, and security](references/helm-operations-security.md) | chart values, CRDs, probes, metrics, RBAC, network policy, availability, release artifacts, and custom builds |
| [Push workflows](references/push-workflows.md) | `PushSecret`, `ClusterPushSecret`, `dataTo`, update/deletion policy, replication, and provider writes |
| [Templates, generators, and CLI](references/templates-generators-cli.md) | template semantics and functions, `templateFrom`, generators, dynamic targets, and `esoctl` |
| [Vault and integration providers](references/vault-and-integration-providers.md) | Vault, OpenBao, 1Password, Infisical, Akeyless, Passbolt, GitHub, Grafana, Delinea, and other integrations |

## Breaking changes and migration checks

### Removed providers

Alibaba and Device42 were removed in 2.0.0 because they were unsupported and
unmaintained. Migrate every store that uses either provider before upgrading.

### Removed template and generator behavior

- `getHostByName` is no longer available to templates. Replace DNS lookups with
  explicit data supplied to the template.
- The `STSSessionToken` generator no longer supports JWT-token
  authentication. Select another supported authentication path.
- Kubernetes-provider pushes replace the whole destination Secret; they do not
  merge with keys already present remotely.

### Image registry migration

The default controller image moved from
`oci.external-secrets.io/external-secrets/external-secrets` to
`ghcr.io/external-secrets/external-secrets`. Update pinned or overridden image
repositories; the chart repository itself remains on GitHub Pages.

### API assumptions to remove

- Use `apiVersion: external-secrets.io/v1` in provider examples and current
  `ExternalSecret` manifests.
- Do not rely on omitted optional strategy fields being defaulted back into an
  `ExternalSecret` object.
- `ClusterExternalSecret.spec.namespaceSelectors` is the plural, ORed selector
  list. The singular selector and explicit `namespaces` field are deprecated.
- `target.template.metadata` replaces implicit metadata copying. Empty label or
  annotation maps intentionally suppress copying.
- Invalid `ExternalSecretRewrite`, generator reference types, and namespaced
  `secretRef` values are rejected earlier by validation.

## ExternalSecret quick reference

### Refresh policy

- `Periodic` is the default.
- With `Periodic`, a zero `refreshInterval` performs the initial fetch and
  create but does not update later.
- `OnChange` ignores the interval and responds only to metadata or spec changes.
- `CreatedOnce` repairs a changed or deleted target while its status survives;
  recreating the `ExternalSecret` resets that status and may overwrite the
  target.
- For a generated credential that must survive deletion and never be replaced,
  combine `refreshPolicy: CreatedOnce`, `creationPolicy: Orphan`, and an
  immutable target.

### Manual refresh

Use the correct annotation for the object:

```sh
kubectl annotate es my-es force-sync=$(date +%s) --overwrite
kubectl annotate ces my-ces external-secrets.io/force-sync=$(date +%s) --overwrite
```

Changing or deleting the cluster-scoped annotation propagates to owned
`ExternalSecret` objects. A manual refresh works only when the selected policy
supports refreshing.

### Creation and synchronization

- `CreateOrMerge` is accepted as a target creation policy.
- `SecretStore.refreshInterval` accepts duration strings.
- Sync windows can gate periodic `ExternalSecret` refreshes.
- Dynamic targets allow a source to choose its target at reconciliation time.
- `objectMeta` and `ownerReferences` propagate to target resources.
- A configurable source null-byte policy controls handling of embedded nulls.

### Cluster fan-out

Each `ExternalSecret` created by a `ClusterExternalSecret` independently polls
its provider. For many namespaces, fetch once into a dedicated namespace and
replicate through a Kubernetes-provider `ClusterSecretStore` to reduce upstream
calls.

Namespace selector entries are ORed. A collision with an existing
`ExternalSecret` is a failed namespace; it is not taken over.

## PushSecret quick reference

### Input and lifecycle

A namespaced `PushSecret` selects exactly one source: a Kubernetes Secret or a
`generatorRef`. It may apply `template` and `templateFrom`, then maps outgoing
keys through `data[].match`.

- `updatePolicy: Replace` permits overwrites.
- `deletionPolicy` defaults to `None`; use `Delete` for provider cleanup.
- A referenced `SecretStore` receives a finalizer when deletion policy requires
  remote cleanup.
- Inspect the generated `PushSecret` status for provider synchronization
  failures; `ClusterPushSecret` readiness reports child provisioning, not the
  provider write result.

### Bulk expansion with dataTo

`spec.dataTo` expands all or regexp-selected keys from the selected Kubernetes
Secret. Each entry needs a `storeRef`, and the store must also appear in
`secretStoreRefs`.

- Without `remoteKey`, each match becomes a separate remote secret or variable.
- With `remoteKey`, all matches become one JSON object and rewrites do not apply.
- Template output precedes expansion; conversion precedes matching and rewrite.
- Explicit `spec.data` wins for the same original, unconverted source key.
- Invalid regexps and duplicate remote keys fail; no matches is a successful
  no-op.
- `IfNotExists` applies to each expanded target, and `Delete` tracks all of them
  for cleanup.

Read [Push workflows](references/push-workflows.md) before depending on a
provider's write, merge, existence-check, or deletion behavior; capabilities
vary by provider.

## Helm and operational quick reference

### CRDs and controllers

CRD creation, reconciliation, and conversion are separate switches. Pair every
disabled `crds.create*` value with the corresponding `process*` value. If the
webhook is disabled, disable CRD conversion too, or the API server will call a
missing conversion endpoint.

### Namespace scope and RBAC

`scopedRBAC: true` with `scopedNamespace` creates a namespace-only installation
and implicitly disables cluster-scoped controllers. When `scopedNamespace` is
omitted, it defaults to the Helm release namespace.

Provider authentication through `serviceAccountRef` needs TokenRequest access.
Disable the broad token-creation rule with
`rbac.serviceAccountTokenCreate: false`, then grant `serviceaccounts/token`
creation only for the referenced accounts by `resourceNames`.

`genericTargets.enabled` expands controller authority to ConfigMaps and every
configured extra API resource. Review each API group, verb, encryption rule,
and admission policy before enabling it.

### Health, metrics, and availability

- Controller, cert-controller, and webhook liveness probes are configurable;
  readiness and webhook startup probes are also configurable.
- Metrics can use secure serving plus `FilterProvider` authentication and
  authorization, but TLS and authentication are not secure-by-default chart
  assumptions.
- The controller defaults to one replica; availability controls such as extra
  replicas, probes, and PodDisruptionBudgets must be enabled deliberately.
- Give independent deployments in the same namespace distinct leader-election
  IDs; lease timing and store requeue timing are configurable.
- PDB percentage and explicit zero values render correctly.

### Network and pod security

Restricted pod security defaults do not make the chart a complete hardened
deployment. NetworkPolicy is optional, and default role aggregation and token
permissions require review. Limit egress to DNS, the Kubernetes API, and the
selected provider endpoints; restrict `ClusterSecretStore` references and deny
unused providers where policy tooling allows it.

## Provider selection quick reference

Provider maturity and individual capabilities are separate questions. Before
choosing a provider, verify store validation, find, extraction, metadata,
referent authentication, push, merge, and delete support independently.

Notable current choices include dedicated OpenBao support, AWS Certificate
Manager, Barbican, Cloud.ru Secret Manager, Devolutions Server, Nebius
MysteryBox, OVHcloud, Volcengine, and BeyondTrust WorkloadCredentials. Custom
builds can use provider build tags to exclude providers that are not needed.

For provider-specific authentication, lookup, path, replication, metadata,
cache, error, or write semantics, load the appropriate provider reference
before editing a store.

## Verification checklist

- Confirm the installed controller, chart, and CRDs agree.
- Render Helm output and inspect RBAC, probes, PDBs, Services, webhook
  configuration, conversion, NetworkPolicy, scheduler, and RuntimeClass.
- Validate namespace boundaries for stores, referents, provider credentials,
  and cluster-scoped fan-out.
- Check update and deletion policies against the provider's actual write and
  delete capabilities.
- Inspect `ExternalSecret`, `PushSecret`, and store conditions and events;
  provider errors are not always equivalent to missing secrets.
- Test metadata-only updates, target recreation, key removal, replication, and
  cleanup in a non-production namespace before rollout.
- Verify release images by immutable digest and validate their signature,
  provenance, and SBOM attestations when artifact identity matters.

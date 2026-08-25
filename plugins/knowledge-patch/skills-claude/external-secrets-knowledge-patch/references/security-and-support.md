# Security and Support Policy

Use this reference for upgrade planning, support expectations, controller
authority, namespace isolation, network policy, and release verification.

## Support window (`operations-and-security`)

ESO supports only its newest minor release; publishing the next minor
automatically deprecates the previous one. The policy snapshot recorded 2.8 as
the supported line, with Kubernetes 1.35 guaranteed and end of life when 2.9
shipped. Image rebuilds, Go dependency updates, and security or bug fixes applied
to that supported line. Upgrade one minor at a time and re-check the current
support table rather than treating the snapshot as a permanent support claim.

## Deprecation boundaries (`operations-and-security`)

The protected surface comprises API object specs, status and conditions, enums
and constants, controller flags and environment variables, metrics, and
documented `ExternalSecret` update mechanics.

Helm charts, releases, images, signatures, OLM builds, source imports, and
unspecified behavior are outside the guarantee. Introducing a deprecation
requires a minor release during 0.x or a major release from 1.x onward. Only
in-scope removals inherit Kubernetes deprecation timelines.

The component policy classifies ESO as beta: features are enabled by default and
considered safe to enable, but schemas or semantics can change incompatibly when
migration instructions are supplied. The policy does not recommend beta software
for production.

Legacy beta API serving became configurable in 1.3.0 to aid migration. Do not
confuse temporary serving compatibility with a broader stability promise.

## Provider maturity is not feature parity (`operations-and-security`)

The 2.8 support table classified AWS Secrets Manager, AWS Parameter Store,
Akeyless, Azure Key Vault, CyberArk Secrets Manager, GCP Secret Manager, HashiCorp
Vault, IBM Cloud Secrets Manager, Oracle Vault, and Previder as stable. Kubernetes
and SecretServer were beta; every other listed provider was alpha.

Maturity does not guarantee find, metadata fetch, referent authentication, store
validation, push, or merge/delete support. Check the capability table for the
specific provider and release.

Stores whose provider has no explicit maintainer emit both controller and
admission warning events. The
`external-secrets.io/ignore-maintenance-checks: "true"` annotation suppresses only
the controller warning.

## Default pod security versus chart hardening (`operations-and-security`)

Default pod security contexts have followed the restricted profile since 0.8.2:
non-root UID 1000, read-only root filesystem, privilege escalation disabled, all
capabilities dropped, and `RuntimeDefault` seccomp.

That does not make the chart a hardened deployment. NetworkPolicies and metrics
TLS/authentication default off, while blanket ServiceAccount-token creation and
aggregation into view, edit, and admin roles default on. Review the rendered RBAC,
network paths, provider set, and monitoring endpoints for each installation.

Relevant controls include secure metrics serving from 0.20.0, metrics
authentication and authorization through `FilterProvider` from 2.5.0,
`aggregateToAdmin` from 2.8.0, and an optional chart NetworkPolicy from 2.8.0.

## Namespace-scoped installation (`operations-and-security`)

Namespaced `ExternalSecret` and `SecretStore` resources cannot reference a
`SecretStore`, Secret, or other namespaced referent across namespaces.
Cluster-scoped resources require separate review because they can span namespace
boundaries.

For a namespace-only installation, scoped RBAC also disables cluster-scoped
controllers:

```yaml
scopedRBAC: true
scopedNamespace: payments
```

From 2.5.0, an omitted `scopedNamespace` defaults to `.Release.Namespace` when
`scopedRBAC` is enabled. Prefer an explicit namespace when reviewing generated
permissions.

Use `ClusterSecretStore.spec.conditions` to restrict referencing namespaces.
Label selectors, explicit names, and regular expressions are ORed, so satisfying
any one grants access.

## CRDs, reconcilers, and conversion (`operations-and-security`)

CRD installation defaults on, but CRD and reconciler switches are independent.
Pair each disabled `crds.create*` with the matching `process*` value. If disabling
the webhook, disable CRD conversion too, or the API server continues to call a
conversion endpoint that no longer exists.

```yaml
crds:
  createPushSecret: false
  conversion:
    enabled: false
processPushSecret: false
webhook:
  create: false
```

## ServiceAccount token delegation (`operations-and-security`)

Provider authentication through `serviceAccountRef` requires TokenRequest access.
The default controller role can create tokens for any ServiceAccount in scope.
Disable blanket creation and grant it per referenced account:

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

The chart conditionally renders its token-create rule from 2.5.0. Provider
TokenRequests also use the URL namespace consistently in the body from 2.6.0.

## Generic targets widen authority (`operations-and-security`)

`genericTargets.enabled` defaults false. Enabling it grants create, update, and
delete access to ConfigMaps and the configured verbs for each resource under
`genericTargets.resources`. Treat each added API group as a privilege expansion;
apply encryption and admission controls suitable for that target.

## Network and exfiltration controls (`operations-and-security`)

The controller needs egress to the Kubernetes API and selected secret providers;
webhook and cert-controller need the API. Prefer private provider endpoints. Allow
DNS plus only the required API and provider destinations.

Expected inbound ports are:

- Controller: metrics 8080 and optional health 8082.
- Webhook: admission 10250, metrics 8080, and health 8081.
- Cert-controller: metrics 8080 and health 8081.

Policy engines should deny unused providers, constrain remote-key prefixes, and
limit `ClusterSecretStore` references. HTTP/2 serving is configurable from 0.20.0
and can be disabled when the security posture requires it.

## Availability controls (`operations-and-security`)

The controller defaults to one replica, with leader election, liveness,
readiness, and PodDisruptionBudget disabled. Webhook and cert-controller readiness
is enabled, but each defaults to one replica with liveness and PDB disabled.

Enable controls to meet the availability objective. Give independent ESO
deployments in one namespace distinct lease IDs. Leader identity can be configured
from 2.4.0, and lease timings from 2.8.0.

## Release artifact identity (`operations-and-security`)

ESO images carry keyless Cosign signatures, SLSA provenance attestations, and
SPDX JSON SBOM attestations. Verify an immutable digest and check for certificate
issuer `https://token.actions.githubusercontent.com` and the External Secrets
release workflow subject on `refs/heads/main`.

Signatures and provenance are themselves outside the deprecation guarantee. Their
presence supports supply-chain verification but does not expand the supported API
surface.

---
name: cert-manager-knowledge-patch
description: cert-manager
version: "1.21"
license: MIT
metadata:
  author: Nevaberry
---


# cert-manager Knowledge Patch

Use this skill when upgrading, configuring, operating, or integrating cert-manager. Check the deployed cert-manager patch release before applying version-dependent guidance, and prefer a corrected patch release where one is called out.

## Reference index

| Reference | Topics |
|---|---|
| [ACME and challenge solvers](references/acme-and-challenge-solvers.md) | ACME profiles, HTTP-01 and DNS-01 behavior, solver configuration, retries, and RBAC |
| [Certificates and renewal](references/certificates-and-renewal.md) | Certificate fields, key rotation, renewal, keystores, output formats, validation, and issuance safety |
| [Gateway, Ingress, and cert-shim](references/gateway-ingress-and-cert-shim.md) | Gateway API, ListenerSet, annotations, generated Certificates, and listener selection |
| [Helm and platform operations](references/helm-and-platform-operations.md) | Chart values, ServiceAccounts, security contexts, NetworkPolicies, scheduling, and installation |
| [Issuers and external providers](references/issuers-and-external-providers.md) | Vault, Venafi, Azure, external DNS providers, issuer validation, and API clients |
| [Observability, cainjector, and clients](references/observability-cainjector-and-clients.md) | Metrics, logging, CA injection, webhook recovery, and generated clients |
| [Upgrades and support](references/upgrades-and-support.md) | Upgrade hazards, deprecations, corrective patch releases, compatibility, and support policy |

## Upgrade blockers and changed defaults

### Make private-key rotation explicit before an upgrade

`Certificate.spec.privateKey.rotationPolicy` defaults to `Always`. Set it to `Never` before upgrading if a workload must retain its existing private key.

```yaml
spec:
  privateKey:
    rotationPolicy: Never
```

The old default-changing feature gate is GA and no longer configurable. Use the per-Certificate field.

### Account for the revision-history limit

`Certificate.spec.revisionHistoryLimit` defaults to `1`. Certificates that omit it no longer have the earlier unlimited/nil behavior.

### Treat HTTP-01 ingress selection as exclusive

Specify exactly one of `class`, `ingressClassName`, or `name` on an HTTP-01 solver. Generated solver Ingresses use `PathType: Exact`; if ingress-nginx strict path validation rejects them, use a corrected ingress-nginx release, disable its strict validation, or configure:

```yaml
config:
  featureGates:
    ACMEHTTP01IngressPathTypeExact: false
```

### Avoid known bad initial patch releases

- Use `1.17.1` or later for Cloudflare DNS-01, and `1.17.4` or later for URI name constraints.
- Use `1.18.1` or later when disabling exact HTTP-01 paths.
- Skip `1.19.0`; use `1.19.1` or later to avoid issuer-reference default reissuance and trailing-dot SAN regressions.
- Use `1.19.2` or later for merged `global.nodeSelector` behavior.
- Use `1.20.1` or later on OpenShift and when combining inferred Gateway `parentRefs` with annotation overrides.
- Use `1.20.2` or later when setting both `webhook.config` and `webhook.volumes`.
- Use `1.21.1` or later with disabled renewal and for DNS-01 issuer recovery after a missing Secret is created.

### Prepare chart-managed identity and monitoring changes

Containers default to UID and GID `65532`. Update admission rules and volume permissions that assumed UID `1000` or GID `0`.

The chart no longer creates token-creation RBAC for the controller ServiceAccount. Give issuer-referenced ServiceAccounts explicit token RBAC. Remove the deleted ServiceMonitor/PodMonitor path and port override values; metrics use `/metrics` and the `http-metrics` port name.

## Removed and deprecated behavior

### Remove obsolete feature-gate settings

- Stop enabling `ValidateCAA`; it was deprecated before removal.
- Do not configure `DefaultPrivateKeyRotationPolicyAlways`; the behavior is unconditional.
- Do not rely on disabling `CAInjectorMerging`; bundle merging is unconditional.
- `ServerSideApply` for cainjector is deprecated because cainjector always uses server-side apply.
- Replace controller fields `enableGatewayAPI` and `enableGatewayAPIListenerSet` with `gatewayAPI.enabled` and `gatewayAPI.enableListenerSet`.

```yaml
gatewayAPI:
  enabled: true
  enableListenerSet: true
```

### Remove unavailable API and chart settings

Migrate integrations away from the removed `ObjectReference` API type. Do not use `global.rbac.disableHTTPChallengesRole`; it was withdrawn after `1.18.0`. Remove the deleted Prometheus monitor override values before Helm schema validation.

### Revisit direct ACME resource tooling

The aggregate `cert-manager-edit` ClusterRole does not grant all direct Challenge and Order mutations. Certificate-driven issuance is unaffected; automation that manages these internal resources needs explicit RBAC.

## Certificate and renewal quick reference

### Configure renewal deliberately

Use `renewBefore`, `renewBeforePercentage`, or the expressive `renewalPolicies` field as appropriate. Long-duration percentage calculations are corrected, and failed CertificateRequests default to a maximum backoff of 32 hours:

```yaml
config:
  certificateRequestMaximumBackoffDuration: 8h
```

When `spec.renewal.policy: Disabled` is in use, require the patch release that fixes the controller panic.

### Choose keystore and output compatibility

JKS and PKCS#12 keystores may use a literal `password`, mutually exclusive with `passwordSecretRef`. The literal satisfies consumers that require a password; it does not add keystore security.

```yaml
spec:
  keystores:
    jks:
      create: true
      password: changeit
```

Use the PKCS#12 `Modern2026` profile for AES-256/SHA-256 KDFs and FIPS 140-3 compatibility. Additional certificate output formats are always available without a feature gate.

### Validate issuer output and subject handling

Large RSA keys use SHA-384 at 3072 bits and SHA-512 at 4096 bits. IP common names become IP SANs, IPv6 subjects work with HTTP-01, large PEM chains are accepted, mismatched CSR keys fail with backoff, and already-expired issuer responses stop instead of reissuing forever.

## ACME and DNS quick reference

### Select profiles and renewal information

Select a CA-offered ACME certificate profile when needed. Experimental RFC 9773 renewal information is available with `ACMEUseARI`, allowing the CA to recommend renewal windows.

### Use delayed validation only as an escape hatch

`waitInsteadOfSelfCheck` skips the local HTTP-01 or DNS-01 self-check, waits for the configured duration, and asks the ACME server to validate. Reserve it for environments such as split-horizon DNS or NAT hairpinning.

### Configure newer DNS solver controls

RFC2136 supports explicit `protocol`; Azure DNS supports `zoneType: AzurePrivateZone`. DNS credentials are validated before issuer readiness. CloudDNS handles cleanup with large record sets, while DigitalOcean errors are retried and attached to Challenge events.

## Gateway and ingress quick reference

### Control generated Certificates

Use `--extra-certificate-annotations` to copy selected annotations from Ingresses or Gateways. Changes to Duration or `RenewBefore` annotations reconcile immediately. Cert-shim also maps `cert-manager.io/alt-names` and `cert-manager.io/ip-sans`.

### Configure ListenerSet deliberately

ListenerSet certificate generation is alpha and requires its feature gate. For TLS-only ListenerSets, route HTTP-01 through the parent Gateway with:

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-parentreffallback: "true"
```

Use `cert-manager.io/ignore-tls-listeners` to exclude selected Gateway TLS listeners. Passthrough listeners are ignored.

## Helm and operations quick reference

### Apply chart-wide controls

`global.nodeSelector`, `global.commonLabels`, component and solver runtime classes, chart-managed NetworkPolicies, percentage PodDisruptionBudgets, and templated ServiceAccount annotation keys and values are available. `global.hostUsers: false` opts chart-managed Pods into Kubernetes user namespaces on Kubernetes 1.33 or later.

### Scope and clean up workloads

`--namespace=<namespace>` restricts operation to that namespace and disables cluster-scoped controllers. Set `startupapicheck.ttlSecondsAfterFinished` to let Kubernetes remove the completed startup API check Job.

## Observability and CA injection quick reference

### Update metrics and log consumers

Use the certificate not-before/not-after timestamp metrics and `certmanager_certificate_challenge_status`. ACME request metrics use the bounded `action` label instead of `path`. Structured logging adds context, so exact full-line matches may fail. The Prometheus metrics label is consistently `cert-manager`.

### Plan CA rotation around unconditional merging

Cainjector merges certificates into injected bundles to preserve trust overlap during rotation and always uses server-side apply. Use `--ignore-namespaces` to exclude namespaces from Secret watches.

## Issuer and API quick reference

### Prefer workload identity over long-lived credentials

Vault issuers support AWS IAM authentication through IRSA, EKS Pod Identity, and ambient EC2/ECS credentials. Their service-account token audiences include the Vault server address. Configure a TLS server name when Vault certificate validation requires one, and never put `..` in Vault paths or auth mount paths.

### Query and apply resources safely

Issuer-reference group, kind, and name are selectable fields. Generated apply-configuration types support type-safe server-side apply. Use `iss` and `ciss` as the short names for Issuer and ClusterIssuer.

## Verification checklist

Before rollout:

1. Confirm the exact cert-manager patch release and Kubernetes/OpenShift compatibility.
2. Render the Helm chart with all production values and validate the resulting RBAC, security contexts, Service ports, and NetworkPolicies.
3. Inspect every Certificate for rotation and renewal assumptions.
4. Exercise HTTP-01/DNS-01 solvers against the deployed ingress and DNS providers.
5. Check alerts, dashboards, and log parsing for label and structured-log changes.
6. Test CA-bundle overlap and all relying clients during issuer rotation.
7. Prefer the latest patch release on a supported minor branch.

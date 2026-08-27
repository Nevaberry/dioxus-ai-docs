---
name: cert-manager-knowledge-patch
description: cert-manager
version: "1.21"
license: MIT
metadata:
  author: Nevaberry
---


# cert-manager Knowledge Patch

## When to use

Load this skill for cert-manager work involving upgrades, Certificate behavior,
ACME solvers, issuers, Gateway or Ingress integration, Helm configuration,
metrics, RBAC, or platform compatibility.

First establish the installed cert-manager patch release, chart values,
Kubernetes or OpenShift version, enabled feature gates, and relevant issuer and
Certificate manifests. Patch-level fixes matter: do not assume every patch in a
minor line has the same behavior.

## Reference index

| Reference | Topics |
|---|---|
| [Upgrades and support](references/upgrades-and-support.md) | Upgrade defaults, removals, required patch releases, support and platform policy |
| [Certificates and issuance](references/certificates-and-issuance.md) | Certificate fields, renewal, keystores, validation, output, reconciliation |
| [ACME and DNS solvers](references/acme-and-dns-solvers.md) | HTTP-01, DNS-01, profiles, solver configuration, retry behavior |
| [Gateway, Ingress, and shim](references/gateway-ingress-and-shim.md) | ListenerSet, Gateway listeners, generated Certificates, annotations |
| [Helm, operations, and security](references/helm-operations-and-security.md) | Chart values, Pod settings, NetworkPolicy, RBAC, namespace scope |
| [Issuers, integrations, and API clients](references/issuers-integrations-and-api.md) | Vault, Venafi, cainjector, issuer APIs, apply clients |
| [Observability and reliability](references/observability-and-reliability.md) | Metrics, logging, backoff, recovery, diagnostics |

## Upgrade first: behavior changes and removals

### Preserve private keys explicitly when required

The default `Certificate.spec.privateKey.rotationPolicy` is `Always`. Before an
upgrade, set `Never` on Certificates that must retain their existing key:

```yaml
spec:
  privateKey:
    rotationPolicy: Never
```

The feature gate that once disabled the `Always` default is no longer
configurable. Per-Certificate policy is the supported control.

### Expect a bounded revision history

An omitted `Certificate.spec.revisionHistoryLimit` defaults to `1`. Set the
field explicitly if retaining more CertificateRequests is operationally
important.

### Migrate removed Helm monitor values

Remove these values before chart-schema validation:

- `prometheus.servicemonitor.targetPort`
- `prometheus.servicemonitor.path`
- `prometheus.podmonitor.path`

Metrics use `/metrics` and the `http-metrics` port name. Replace scrape rules
that still refer to `tcp-prometheus-servicemonitor`.

### Supply issuer token RBAC deliberately

The chart does not create the controller ServiceAccount `Role` and
`RoleBinding` for token creation. If an issuer's `serviceAccountRef.name` uses
that ServiceAccount, add explicit RBAC or move the issuer to a dedicated
ServiceAccount with its own permissions.

### Update renamed metrics labels

`certmanager_acme_client_request_count` and
`certmanager_acme_client_request_duration_seconds` use bounded `action` labels,
not `path`. Rewrite dashboards and alerts; use a recording or relabeling rule
only when old path-level semantics are indispensable.

### Stop configuring obsolete feature gates and APIs

- Do not enable deprecated `ValidateCAA`.
- `CAInjectorMerging` is unconditional; replacement semantics cannot be
  restored with its old gate.
- Cainjector always uses server-side apply; `ServerSideApply` is deprecated.
- `AdditionalCertificateOutputFormats` is GA and needs no gate.
- Migrate the removed `ObjectReference` API type.

### Account for security-context identity changes

Default container UID and GID are both `65532`. Review admission rules, volume
ownership, and policies that assumed UID `1000` or GID `0`.

## High-value configuration

### Avoid HTTP-01 path validation failures

HTTP-01 solver Ingresses use `PathType: Exact`. With ingress-nginx strict path
validation, use a fixed ingress-nginx release, disable strict path validation,
or on a compatible cert-manager patch restore the former behavior:

```yaml
config:
  featureGates:
    ACMEHTTP01IngressPathTypeExact: false
```

Configure exactly one of `class`, `ingressClassName`, and `name` in each
HTTP-01 solver.

### Select ACME profiles and validation strategy

An ACME issuer can request a CA-offered certificate profile such as
`tlsserver` or `shortlived`. For split-horizon DNS or NAT hairpin environments,
`waitInsteadOfSelfCheck` can skip the local self-check, wait for a configured
duration, and then request ACME validation.

Experimental RFC 9773 renewal information is enabled with `ACMEUseARI`; it lets
the CA recommend renewal windows for events such as mass revocation or CA key
rollover.

### Configure solver resources per issuer

HTTP-01 solver Pods can override global resource flags in the issuer:

```yaml
spec:
  acme:
    solvers:
      - http01:
          ingress:
            podTemplate:
              spec:
                resources:
                  requests:
                    cpu: 20m
                    memory: 32Mi
```

### Use modern PKCS#12 when FIPS compatibility matters

The `Modern2026` profile uses AES-256 and SHA-256 KDFs rather than legacy 3DES
or RC2 and is compatible with FIPS 140-3 requirements.

### Set retry ceilings to operational needs

Failed CertificateRequests use exponential backoff with a default maximum of
32 hours. Configure the ceiling through
`--certificate-request-maximum-backoff-duration`, the controller config, or:

```yaml
config:
  certificateRequestMaximumBackoffDuration: 8h
```

### Use current Gateway configuration keys

Prefer the nested controller fields:

```yaml
gatewayAPI:
  enabled: true
  enableListenerSet: true
```

The older `enableGatewayAPI` and `enableGatewayAPIListenerSet` fields still
work but are deprecated. ListenerSet support is alpha and requires its feature
gate.

### Isolate chart-managed workloads

The chart can create NetworkPolicies for every cert-manager Deployment. Its
default policy includes IPv6, and `global.nodeSelector` provides a common node
selector across components. On Kubernetes 1.33 or later,
`global.hostUsers: false` opts all chart-managed Pods into user namespaces.

## Diagnostic priorities

1. Identify the exact patch release, not only the minor line.
2. Check controller, webhook, cainjector, and solver events before changing
   manifests.
3. Validate feature-gate availability; GA gates may be ignored or rejected.
4. Compare generated child resources with the source Certificate, Ingress,
   Gateway, ListenerSet, Issuer, or ClusterIssuer.
5. For issuance loops, inspect CSR/public-key matching, certificate expiry,
   renewal policy, and issuer response before forcing reissuance.
6. For DNS-01 readiness, verify referenced Secrets and read Challenge events;
   current providers expose more complete diagnostics and recovery behavior.
7. For upgrade regressions, consult the patch-specific advisories in the
   references before applying a workaround.

# ACME and Challenge Solvers

## HTTP-01 solver behavior

### Exact Ingress paths `(1.18)`

Generated HTTP-01 solver Ingresses use `PathType: Exact`. With ingress-nginx strict path validation, use ingress-nginx 1.12.6+ or 1.13.2+, disable `strict-validate-path-type`, or, with cert-manager 1.18.1+, restore the former behavior:

```yaml
config:
  featureGates:
    ACMEHTTP01IngressPathTypeExact: false
```

### Exclusive ingress selection `(1.19)`

An HTTP-01 solver is invalid when more than one of `class`, `ingressClassName`, and `name` is set. Configure exactly one.

### Per-Issuer solver resources `(1.19)`

Set HTTP-01 solver Pod requests and limits in an Issuer or ClusterIssuer to override the controller-wide `--acme-http01-solver-resource-*` flags for that solver:

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
                  limits:
                    cpu: 100m
                    memory: 64Mi
```

### Per-Ingress class override `(1.20)`

The `acme.cert-manager.io/http01-ingress-ingressclassname` annotation overrides the solver's `http01.ingress.ingressClassName` for one Ingress:

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-ingress-ingressclassname: nginx
```

### IPv6 subjects `(1.18)`

Since 1.18.5, HTTP-01 handles IPv6 addresses in the Host header, enabling IP-address certificate issuance for IPv6 subjects.

## DNS-01 solvers

### Cloudflare correction `(1.17)`

A Cloudflare API change broke DNS-01 issuance until cert-manager 1.17.1 restored it. Require 1.17.1 or later on that minor branch.

### RFC2136 transport selection `(1.19)`

RFC2136 solver configuration accepts a `protocol` field for explicit DNS update transport selection:

```yaml
spec:
  acme:
    solvers:
      - dns01:
          rfc2136:
            protocol: TCP
```

### Azure private zones `(1.20)`

Select an Azure DNS private zone with `zoneType`:

```yaml
spec:
  acme:
    solvers:
      - dns01:
          azureDNS:
            zoneType: AzurePrivateZone
```

### CloudDNS cleanup `(1.20)`

The CloudDNS solver cleans up ACME challenge TXT records even when the DNS name has a large resource-record set.

### DigitalOcean retries and events `(1.20)`

DigitalOcean DNS-01 retries are regulated, and complete solver errors are attached to the Challenge as events for diagnosis.

### Credential validation and recovery `(1.21)` `(1.21.1)`

DNS issuer Secrets are validated before an issuer becomes ready. If an ACME DNS-01 solver Secret is missing, 1.21.1 allows an Issuer or ClusterIssuer stuck at `Ready=False` with reason `InvalidSolver` to recover after the Secret is created; 1.21.0 can remain stuck.

## ACME issuance controls

### Certificate profiles `(1.18)`

ACME issuance can select a profile advertised by the CA. For example, Let's Encrypt offers `tlsserver` for standard server certificates and `shortlived` for six-day certificates.

### Renewal Information `(1.21)`

Experimental RFC 9773 ACME Renewal Information is behind `ACMEUseARI`. When enabled, cert-manager calls the ACME server's `renewalInfo` endpoint so the CA can recommend renewal windows, including during mass revocation or CA key rollover.

### Delayed validation `(1.21)`

HTTP-01 and DNS-01 solvers can set `waitInsteadOfSelfCheck` to skip the local self-check, wait for a configured duration, and then request ACME validation. Use this escape hatch for conditions such as split-horizon DNS or NAT hairpinning.

### Authorization timeout `(1.17)`

Starting in 1.17.3, ACME challenge authorization waits up to two minutes, reducing premature `error waiting for authorization` failures.

### Transient error retries `(1.21)`

TLS handshake timeouts, DNS failures, and context cancellation while fetching nonces or waiting for authorization retry through workqueue backoff instead of terminally failing the Challenge.

### Managed account-key label `(1.18)`

Created Let's Encrypt account-key resources carry `app.kubernetes.io/managed-by: cert-manager`.

## Solver access and observability

### Direct Challenge and Order RBAC `(upgrade-1.19)`

Starting in 1.19.6, the aggregate `cert-manager-edit` ClusterRole cannot create Challenges and cannot create, patch, or update Orders. Certificate-driven issuance is unchanged. Tools that directly mutate these internal objects need explicit RBAC.

### Challenge status metric `(1.19)`

`certmanager_certificate_challenge_status` exposes certificate challenge status for monitoring and alerting.

### Labels on dynamic solver resources `(1.21)`

Use `--acme-http01-solver-extra-labels` to propagate Helm `global.commonLabels` to dynamic HTTP-01 Pods, Services, Ingresses, and Gateway API HTTPRoutes.

# ACME and DNS Solvers

## HTTP-01 behavior

### Exact Ingress paths

Solver Ingresses use `PathType: Exact` (`1.18`). With ingress-nginx strict path
validation, use ingress-nginx 1.12.6+ or 1.13.2+, disable
`strict-validate-path-type`, or from cert-manager 1.18.1 restore the former path
type:

```yaml
config:
  featureGates:
    ACMEHTTP01IngressPathTypeExact: false
```

An HTTP-01 solver is rejected when more than one of `class`,
`ingressClassName`, and `name` is configured. Choose exactly one (`1.19`).

### Per-Issuer resources

An Issuer or ClusterIssuer can override the platform-wide solver resource
flags for its own HTTP-01 Pods (`1.19`):

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

### IPv6 and IP subjects

From 1.18.5, HTTP-01 handles IPv6 addresses in the Host header. For Gateway
solvers, cert-manager 1.20 sets `HTTPRoute.spec.hostnames` when the challenge
name is an IP address, avoiding an invalid HTTPRoute.

### Skip the self-check deliberately

`waitInsteadOfSelfCheck` lets HTTP-01 and DNS-01 skip cert-manager's self-check,
wait for a configured duration, and ask the ACME server to validate (`1.21`).
Treat it as an escape hatch for split-horizon DNS and NAT hairpin deployments.

## ACME accounts, profiles, and authorization

An issuer can select a certificate profile advertised by the CA (`1.18`). For
example, Let's Encrypt offers `tlsserver` for normal server certificates and
`shortlived` for six-day certificates.

New Let's Encrypt account-key Secrets carry
`app.kubernetes.io/managed-by: cert-manager`. From 1.17.3, ACME challenge
authorization waits for up to two minutes, reducing premature
`error waiting for authorization` failures.

TLS handshake timeouts, DNS failures, and context cancellation while fetching
an ACME nonce or awaiting authorization retry with workqueue backoff instead of
terminally failing the Challenge (`1.21`).

## DNS-01 providers

### Azure DNS

With service principals and managed identities, AzureDNS accepts `tenantID` to
select the tenant explicitly in multi-tenant environments (`1.17`). Azure
Private DNS Zones are selectable with `zoneType` (`1.20`):

```yaml
spec:
  acme:
    solvers:
      - dns01:
          azureDNS:
            zoneType: AzurePrivateZone
```

### RFC2136

RFC2136 solver configuration accepts `protocol` so the DNS update transport is
explicit (`1.19`):

```yaml
spec:
  acme:
    solvers:
      - dns01:
          rfc2136:
            protocol: TCP
```

### Provider fixes and diagnostics

- Use 1.17.1 or later for Cloudflare DNS-01 after its API change.
- CloudDNS cleanup handles challenge TXT names with large record sets (`1.20`).
- DigitalOcean retries are regulated, and complete DNS-01 errors are attached
  to the Challenge as events (`1.20`).
- DNS issuer credentials are checked before readiness, exposing Secret errors
  rather than accepting them silently (`1.21`).
- In 1.21.0, an issuer can remain `Ready=False` with `InvalidSolver` after a
  missing solver Secret is created. Version 1.21.1 makes it recover.

## Per-Ingress solver selection

`acme.cert-manager.io/http01-ingress-ingressclassname` overrides an HTTP-01
solver's `http01.ingress.ingressClassName` for one Ingress (`1.20`):

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-ingress-ingressclassname: nginx
```

# Gateway, Ingress, and cert-shim

## Generated Certificate metadata

### Copy selected annotations `(1.18)`

Pass annotation keys to `--extra-certificate-annotations` to copy them from an Ingress or Gateway to the generated Certificate.

### Alternative names `(1.21)`

Cert-shim controllers map the `cert-manager.io/alt-names` and `cert-manager.io/ip-sans` annotations on ingress-like resources into generated Certificates.

### Timing annotations reconcile immediately `(1.20)`

Changing a Duration or `RenewBefore` annotation on an Ingress or Gateway API resource immediately updates the generated Certificate.

## Gateway listener handling

### Passthrough listeners `(1.18)`

Gateway TLS listeners with mode `Passthrough` are skipped rather than treated as certificate-issuing listeners.

### Listener selection `(1.21)`

Use `cert-manager.io/ignore-tls-listeners` to exclude selected Gateway TLS listeners from certificate management. Gateway integration can also consider configured listener protocols beyond its default set.

### Nested controller configuration `(1.21)`

The flat controller fields `enableGatewayAPI` and `enableGatewayAPIListenerSet` are deprecated. Prefer:

```yaml
gatewayAPI:
  enabled: true
  enableListenerSet: true
```

The old fields remain functional during migration.

## ListenerSet integration

### Certificate generation `(1.20)`

Annotated ListenerSet resources can produce Certificates. This integration is alpha, disabled by default, and requires the `ListenerSet` feature gate.

### ACME parent references `(1.20)`

An ACME Gateway configuration can leave Issuer or ClusterIssuer `parentRefs` empty for inference, while Certificate annotations can override the references. Use 1.20.1 or later when combining issuer configuration with annotation overrides; 1.20.0 can generate duplicate `parentRef` entries.

### HTTP-01 parent fallback `(1.21)`

For a TLS-only ListenerSet, make the solver HTTPRoute use the parent Gateway's HTTP listener:

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-parentreffallback: "true"
```

## HTTP-01 and ingress behavior

### Per-Ingress solver class `(1.20)`

Override the HTTP-01 solver's `http01.ingress.ingressClassName` for one Ingress:

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-ingress-ingressclassname: nginx
```

### IP-subject Gateway challenges `(1.20)`

The Gateway solver sets `HTTPRoute.spec.hostnames` when the challenge DNS name is an IP address, preventing invalid HTTPRoutes for IP-address Certificates.

### Exact solver paths `(1.18)`

HTTP-01 solver Ingresses use `PathType: Exact`. If ingress-nginx strict validation rejects them, move to ingress-nginx 1.12.6+ or 1.13.2+, disable `strict-validate-path-type`, or use cert-manager 1.18.1+ with `ACMEHTTP01IngressPathTypeExact: false`.

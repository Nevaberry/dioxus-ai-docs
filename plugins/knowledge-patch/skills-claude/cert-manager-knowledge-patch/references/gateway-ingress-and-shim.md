# Gateway, Ingress, and Shim Controllers

## Generated Certificate metadata and names

`--extra-certificate-annotations` copies selected annotation keys from an
Ingress or Gateway to its generated Certificate (`1.18`). In 1.21, shim
controllers also process `cert-manager.io/alt-names` and
`cert-manager.io/ip-sans` from ingress-like resources.

Changing a Duration or `RenewBefore` annotation on an Ingress or Gateway
immediately reconciles the generated Certificate (`1.20`).

## Gateway listener handling

Passthrough TLS listeners are ignored rather than treated as certificate
issuance listeners (`1.18`). In 1.21,
`cert-manager.io/ignore-tls-listeners` can exclude selected Gateway TLS
listeners, and Gateway integration can consider protocols beyond its default
listener set.

Prefer the nested controller configuration keys introduced in 1.21:

```yaml
gatewayAPI:
  enabled: true
  enableListenerSet: true
```

The old `enableGatewayAPI` and `enableGatewayAPIListenerSet` fields still work
but are deprecated.

## ListenerSet certificate generation

Annotated ListenerSet resources can generate Certificates (`1.20`). This is an
alpha feature, disabled by default, and requires the `ListenerSet` gate.

For ACME Gateway configuration, empty issuer `parentRefs` can be inferred and
Certificate annotations can override configured references. Use 1.20.1 or
later when combining issuer configuration with annotation overrides; 1.20.0
can emit duplicate `parentRef` entries.

For a TLS-only ListenerSet, this annotation makes the solver HTTPRoute use the
parent Gateway's HTTP listener (`1.21`):

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-parentreffallback: "true"
```

## Gateway HTTP-01 with IP subjects

From 1.20, the Gateway solver sets `HTTPRoute.spec.hostnames` when an ACME
challenge DNS name is an IP address. This prevents invalid HTTPRoutes for
IP-address Certificates.

## Per-Ingress HTTP-01 class

An Ingress can override the solver's `http01.ingress.ingressClassName` with
the 1.20 annotation below:

```yaml
metadata:
  annotations:
    acme.cert-manager.io/http01-ingress-ingressclassname: nginx
```

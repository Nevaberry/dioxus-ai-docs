# Routing, middleware, and services

## Compose router hierarchies

Routers can use `parentRefs` to build multi-layer routing (3.6.0). A parent can
apply shared middleware or TLS and enrich the request before the child's rule
runs. Root routers attach to entry points without a service, intermediate
routers may have children, and leaves select services. A child is reachable
only through its parent.

```yaml
http:
  routers:
    api-parent:
      rule: "Host(`api.example.com`) && PathPrefix(`/`)"
      middlewares: [auth-with-tier]
      entryPoints: [websecure]
      tls: {}
    api-enterprise:
      rule: "HeaderRegexp(`X-Customer-Tier`, `(enterprise|business)`)"
      service: stable-backend
      parentRefs: [api-parent]
```

`Host` and `HostSNI` accept wildcard names such as `*.example.com`, and routing
precedence is configurable when routes from different providers compete
(3.7.0).

The `defaultRuleSyntax` and `ruleSyntax` options are deprecated; remove
dependencies on them (3.4.0).

## Handle paths, redirects, and headers

The Headers middleware can emit `Content-Security-Policy-Report-Only` for
non-enforcing CSP evaluation (3.1.0).

The `encodedCharacters` middleware provides route-level encoded-character
policy. Related entry-point settings are opt-in, and rejected requests appear
in access logs. Prefix stripping uses the encoded prefix length and sanitizes
the result; 3.7.7 also sanitizes paths created by `ReplacePathRegex` (3.7.0).

Gateway API header modifiers can change `Host`. Redirects preserve the incoming
scheme when none is configured and emit the configured status. CORS no longer
emits a default zero max-age or combines credentialed requests with wildcard
origin (3.7.0).

The Errors middleware can rewrite status codes (3.4.0). It can select forwarded
request headers with `errorRequestHeaders`; Kubernetes CRDs gained that field
later, and `service` is required (3.7.11).

IPAllowList can choose the rejection response through `rejectStatusCode`
(3.7.11):

```yaml
http:
  middlewares:
    office-only:
      ipAllowList:
        sourceRange: [192.0.2.0/24]
        rejectStatusCode: 404
```

## Configure compression and mirroring

Compress negotiates Zstandard when clients advertise `zstd` (3.1.0), and its
`encodings` option restricts the formats it may negotiate (3.2.0). Version 3.7.9
specifically disables Zstandard in the `gzhttp` wrapper, so do not depend on
Zstd through that wrapper after upgrading (3.7.11).

Mirroring has `mirrorBody` to control whether request bodies are copied to the
mirror (3.2.0). Mirroring also handles empty bodies whose length is unknown
(3.6.21).

HTTP services can preserve the configured backend server path while proxying
(3.2.0).

## Handle WebSocket traffic

The initial 3.3.0 release has a WebSocket-upgrade issue. Deployments requiring
WebSockets must disable HTTP/2 extended CONNECT:

```sh
GODEBUG=http2xconnect=0 traefik
```

Patched 3.7 behavior supports WebSocket upgrades with `h2c` backends (3.7.0).
Retest upgrades when changing either proxy protocol path.

## Attach middleware to services

HTTP services can carry middleware that applies to every selecting router and
allows Gateway API filters on HTTP backends (3.7.0):

```yaml
http:
  services:
    api:
      loadBalancer:
        servers:
          - url: "http://api-backend:8080"
      middlewares: [rate-limit, auth]
```

## Retry and fail over by status

Retry can select response status codes, impose a per-attempt timeout, and opt in
to non-idempotent methods (3.7.0):

```yaml
http:
  middlewares:
    smart-retry:
      retry:
        attempts: 3
        initialInterval: 100ms
        retryOn:
          statusCodes: [502, 503, 504]
        timeout: 2s
```

Failover services can switch on response statuses, including in
`TraefikService` CRDs (3.7.0):

```yaml
apiVersion: traefik.io/v1alpha1
kind: TraefikService
metadata:
  name: api-failover
spec:
  failover:
    service: api-primary
    fallback: api-backup
    healthCheck: {}
    errors:
      status: ["500-504"]
```

## Choose health checks and balancing

Backends can use a distinct probe interval while unhealthy (3.5.0). Services
also support native TCP health checks for non-HTTP backends and passive health
checks based on live traffic (3.6.0).

Health-check paths must be path-only values, not absolute URLs (3.7.0).

The `p2c` service load-balancing strategy is available from 3.4.0. `Least Time`
is available in file and Kubernetes CRD service configuration, while
`HighestRandomWeight` also works through Kubernetes CRDs (3.6.0).

RateLimit can keep shared state in Redis for enforcement across Traefik
instances (3.4.0). Redis keyspace notifications must be enabled for Redis update
notifications (3.7.11).

Sticky-session cookies can set a path (3.3.0) and a domain (3.4.0), allowing
their scope to match the intended routes and hosts.

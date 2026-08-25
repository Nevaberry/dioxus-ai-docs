# Routing, middleware, and services

## Compose multi-layer routers

Routers can form a `parentRefs` hierarchy (3.6.0). A parent applies shared
middleware or TLS and can enrich the request before a child evaluates its rule.
Root routers attach to entry points without selecting a service, intermediate
routers may have children, and leaf routers select services. A request cannot
reach a child without traversing its parent.

```yaml
http:
  routers:
    api-parent:
      rule: "Host(`api.example.com`) && PathPrefix(`/`)"
      middlewares:
        - auth-with-tier
      entryPoints:
        - websecure
      tls: {}
    api-enterprise:
      rule: "HeaderRegexp(`X-Customer-Tier`, `(enterprise|business)`)"
      service: stable-backend
      parentRefs:
        - api-parent
```

`Host` and `HostSNI` accept wildcard names such as `*.example.com`, and provider
routing precedence is configurable when provider-produced routes compete
(3.7.0).

The `defaultRuleSyntax` and `ruleSyntax` options are deprecated (3.4.0). Remove
them instead of extending reliance on syntax-selection behavior.

## Apply service-level middleware

HTTP services can carry middleware that applies to every router selecting the
service; this also enables Gateway API filters on HTTP backends (3.7.0).

```yaml
http:
  services:
    api:
      loadBalancer:
        servers:
          - url: "http://api-backend:8080"
      middlewares:
        - rate-limit
        - auth
```

## Configure ForwardAuth deliberately

ForwardAuth can log the authenticated identity through `LogUserHeader`
(3.2.0). It can preserve the authorization server's `Location` response header
and forward the incoming request body (3.3.0). It can also preserve the original
request method for the authorization request (3.4.0).

When request bodies are forwarded, configure `maxBodySize`; authentication
middleware warns when it is absent (3.6.0). ForwardAuth later adds
`authSignInURL` for sign-in redirects and `maxResponseBodySize` for bounding the
authorization response. `ForwardAuth.TrustForwardHeader` is deprecated
(3.7.0).

Authentication middleware drops untrusted underscore-bearing `X-*` headers
(3.7.0). A patch correction passes the proper `X-Forwarded-Port` value to the
authorization service (3.6.21).

For CONNECT requests, bodies are discarded before ForwardAuth (since 3.7.9;
reported in 3.7.11). Do not design authorization policy that expects a CONNECT
payload.

## Retry and fail over by status

The Retry middleware can select response status codes, set a per-attempt
timeout, and opt in to retrying non-idempotent methods (3.7.0).

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

Failover services can switch on response status codes, and a
`TraefikService` CRD can express the failover directly (3.7.0):

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

## Select health checks and load balancing

Health checks accept a separate interval while a backend is unhealthy (3.5.0).
Services can use native TCP health checks for non-HTTP backends or passive
health checks inferred from real traffic (3.6.0). Health-check paths must be
path-only; absolute URLs are rejected (3.7.0).

The `p2c` server strategy is available from 3.4.0. `Least Time` is supported by
file and Kubernetes CRD services, while `HighestRandomWeight` is also available
through Kubernetes CRDs (3.6.0). Confirm provider support before translating
configuration between providers.

Sticky cookies accept a path (3.3.0) and a domain (3.4.0), allowing their scope
to be narrowed or shared across the intended hosts.

HTTP services can preserve the configured backend server path while proxying
(3.2.0).

## Mirror request bodies intentionally

`mirrorBody` determines whether an HTTP mirror receives request bodies
(3.2.0). A later correction handles empty bodies whose length is unknown
(3.6.21). Test zero-length streaming and chunked requests when body mirroring is
enabled.

## Handle compression and encoded paths

The Compress middleware can negotiate Zstandard with clients advertising
`zstd` (3.1.0), and its `encodings` option limits the compression formats it may
negotiate (3.2.0).

Version 3.7.9 disables Zstandard specifically in the `gzhttp` wrapper
(3.7.11). This scoped change does not imply that every Traefik compression path
loses Zstandard; test the wrapper actually used by the deployment.

The `encodedCharacters` middleware provides route-level encoded-character
policy, while related entry-point options are opt-in. Rejected requests are
written to access logs. Prefix stripping uses the encoded prefix length and
sanitizes the resulting URL; 3.7.7 also sanitizes paths produced by
`ReplacePathRegex` (3.7.0).

Gateway API `URLRewrite` and `RequestRedirect` preserve encoded path segments
in 3.7.11. Exercise encoded delimiters and non-ASCII segments end to end after
an upgrade.

## Configure security-oriented middleware

The Headers middleware can emit `Content-Security-Policy-Report-Only` so a CSP
can be evaluated without enforcement (3.1.0).

`ipStrategy` accepts an IPv6 subnet setting for subnet-normalized client-IP
decisions (3.2.0). IPAllowList later gains `rejectStatusCode`, allowing a chosen
rejection response (3.7.11):

```yaml
http:
  middlewares:
    office-only:
      ipAllowList:
        sourceRange:
          - 192.0.2.0/24
        rejectStatusCode: 404
```

The Errors middleware can rewrite status codes while serving an error page
(3.4.0). It adds `errorRequestHeaders` to select headers sent to the error
service (3.7.0); the matching Kubernetes CRD field is restored in 3.7.11, when
the Errors `service` option is also required.

RateLimit can use Redis for state shared across Traefik replicas (3.4.0).
Configure Redis keyspace notifications before relying on its update events.

## Control forwarded and request headers

A global setting can disable appending to `X-Forwarded-For`, and the server can
remove incoming header names containing underscores (3.7.0). Apply these
settings consistently with the trusted-proxy boundary.

The maximum incoming request-header size is configurable (3.2.0). Choose a
limit that accommodates expected cookies and authentication headers without
accepting unbounded header memory use.

## Handle WebSocket and CONNECT traffic

The 3.3.0 release has a WebSocket-upgrade issue. Deployments that require
WebSockets must disable HTTP/2 extended CONNECT:

```sh
GODEBUG=http2xconnect=0 traefik
```

Patched 3.7 behavior supports WebSocket upgrades with `h2c` backends (3.7.0).

From 3.7.9, CONNECT payloads are held until the backend accepts the tunnel,
CONNECT requests are not returned to the connection pool, and FastProxy rejects
CONNECT (3.7.11). Use the regular proxy path for CONNECT tunnels.

## Account for HTTP behavior corrections

CORS no longer emits a default zero max-age and no longer combines credentialed
requests with a wildcard origin (3.7.0 patch line). Gateway header modifiers can
change `Host`, and redirects retain the incoming scheme when none is configured
while emitting the requested redirect status. Add regression tests for these
details when middleware or Gateway filters participate in routing.

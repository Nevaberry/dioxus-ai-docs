---
name: traefik-knowledge-patch
description: "Traefik changes since training cutoff (latest: 3.6.9) — multi-layer routing, Redis rate limiter, p2c/leasttime LB strategies, fast proxy, ForwardAuth body forwarding, OTLP logs, post-quantum TLS, Knative provider. Load before working with Traefik."
license: MIT
version: "3.6.9"
metadata:
  author: Nevaberry
---

# Traefik Knowledge Patch (v3.1 – v3.6)

Baseline: Traefik v3.0.x. Covers: v3.1 through v3.6.9 (July 2024 – November 2025).

## Index

| Topic | Reference | Key features |
|-------|-----------|-------------|
| Routing & Middleware | [references/routing-and-middleware.md] | Multi-layer routing (parentRefs), ForwardAuth body/method forwarding, Zstandard compression, error page status rewrites, path sanitization, encoded character controls |
| Load Balancing & Services | [references/load-balancing.md] | p2c / leasttime / highestRandomWeight strategies, TCP & passive health checks, sticky cookie domain/path, Redis rate limiter, fast proxy mode |
| Providers & Observability | [references/providers-and-observability.md] | Knative provider, NGINX Ingress provider, OTLP logs, trace verbosity, API dashboard base path |

---

## Breaking Changes & Deprecations

| Version | Change |
|---------|--------|
| v3.1 | `disableIngressClassLookup` renamed to `disableClusterScopeResources` |
| v3.1 | Gateway API provider no longer experimental |
| v3.2.2 | `traefik.docker.network` renamed to `traefik.swarm.network` (Swarm labels) |
| v3.3 | `acme.dnsChallenge.delaybeforecheck` renamed to `acme.dnsChallenge.propagation.delayBeforeChecks` |
| v3.3 | `tracing.globalAttributes` renamed to `tracing.resourceAttributes` |
| v3.4 | `RoundRobin` strategy deprecated — use `wrr` |
| v3.4 | `rootCAsSecrets` deprecated — use `rootCAs` (supports ConfigMaps + Secrets) |
| v3.4 | `core.defaultRuleSyntax` and `ruleSyntax` deprecated (v2 compat removed) |
| v3.5.2 | `proxyProtocol` on TCP LB deprecated — use `TCPServersTransport` |
| v3.6.2 | NGINX Ingress provider no longer experimental |

---

## Quick Reference: New Load Balancer Strategies

| Strategy | Version | Description |
|----------|---------|-------------|
| `wrr` | (default) | Weighted round-robin (replaces deprecated `RoundRobin`) |
| `p2c` | v3.4 | Power of Two Choices — picks the less-loaded of two random backends |
| `leasttime` | v3.6 | Routes to the backend with lowest response time |
| `highestRandomWeight` | v3.6 | Probabilistic weighting |

```yaml
http:
  services:
    my-service:
      loadBalancer:
        strategy: p2c # or leasttime, highestRandomWeight, wrr
        servers:
          - url: "http://backend1:8080"
          - url: "http://backend2:8080"
```

## Quick Reference: ForwardAuth Options

| Option | Version | Description |
|--------|---------|-------------|
| `forwardBody` | v3.3 | Send request body to auth server |
| `maxBodySize` | v3.3 | Limit forwarded body size (bytes) |
| `preserveLocationHeader` | v3.3 | Keep Location header from auth response |
| `preserveRequestMethod` | v3.4 | Keep original HTTP method (GET/POST/etc.) |
| `maxResponseBodySize` | v3.6.9 | Limit auth response body size (default -1 = unlimited) |

## Quick Reference: Compression Encodings

Since v3.1/v3.2, the compress middleware supports Zstandard and explicit encoding order:

```yaml
http:
  middlewares:
    compress:
      compress:
        encodings:
          - gzip
          - br
          - zstd
```

Default order since v3.3.5: `gzip, br, zstd`.

## Multi-Layer Routing (v3.6)

Routers can have parent-child relationships via `parentRefs`. Parent routers apply shared middleware (e.g., auth) and child routers make routing decisions based on enriched request context.

Three router types: **Root** (attached to entryPoints, no service), **Intermediate** (has children, inherits from root), **Leaf** (must define a service).

```yaml
http:
  routers:
    api-parent:
      rule: "Host(`api.example.com`)"
      middlewares:
        - auth-with-tier
      entryPoints:
        - websecure
      tls: {}
      # No service — this is a parent router

    api-enterprise:
      rule: "Header(`X-Customer-Tier`, `enterprise`)"
      service: stable-backend
      parentRefs:
        - api-parent

    api-free:
      rule: "Header(`X-Customer-Tier`, `free`)"
      service: canary-backend
      parentRefs:
        - api-parent
```

Child routers cannot be called directly — requests must flow through their parent.

## Redis Rate Limiter (v3.4)

Distributed rate limiting backed by Redis, replacing in-memory-only for multi-instance deployments:

```yaml
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        redis:
          endpoints:
            - "redis:6379"
```

## Post-Quantum TLS (v3.5)

X25519MLKEM768 curve for post-quantum-secure TLS:

```yaml
tls:
  options:
    default:
      curvePreferences:
        - X25519MLKEM768
        - X25519
```

## Security: Path Sanitization & Encoded Characters

**Path sanitization** (v3.3.6+): Incoming paths are auto-cleaned (`/../`, `/./`, `//`). Disable per-entrypoint if needed:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      sanitizePath: false
```

**Encoded characters** (v3.6.4+): Control which encoded characters to allow in request paths:

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      encodedCharacters:
        allowEncodedSlash: true # %2F - default true since v3.6.7
        allowEncodedBackSlash: true # %5C
        allowEncodedNullCharacter: true # %00
```

---

## Reference Files

- **[references/routing-and-middleware.md]** — Multi-layer routing, ForwardAuth, compression, error pages, path/encoding security
- **[references/load-balancing.md]** — LB strategies, health checks, sticky cookies, Redis rate limiter, fast proxy
- **[references/providers-and-observability.md]** — Knative, NGINX Ingress, OTLP logs, trace verbosity, API dashboard

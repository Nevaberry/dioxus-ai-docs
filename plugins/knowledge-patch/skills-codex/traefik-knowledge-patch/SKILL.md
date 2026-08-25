---
name: traefik-knowledge-patch
description: Traefik
version: 3.7.0
license: MIT
metadata:
  author: Nevaberry
---


# Traefik Knowledge Patch

Use this guide to identify behavior that affects a Traefik task, then open the
matching topic reference before editing static configuration, dynamic
configuration, Kubernetes resources, or deployment manifests.

## Reference index

| Reference | Topics |
| --- | --- |
| [Kubernetes and Gateway API](references/kubernetes.md) | Gateway API, EndpointSlices, CRDs, Ingress, Ingress NGINX, Knative, and namespace controls |
| [Observability](references/observability.md) | OpenTelemetry, access logs, support dumps, API/dashboard paths, and dashboard features |
| [Providers and operations](references/providers-operations.md) | Docker, Swarm, ECS, Nomad, HTTP, plugins, socket activation, proxy controls, and operational fixes |
| [Routing, middleware, and services](references/routing-services.md) | Router hierarchies, matching, retries, compression, mirroring, health checks, balancing, failover, and stickiness |
| [Security, TLS, and authentication](references/security-tls-auth.md) | ACME, TLS, ForwardAuth, forwarded headers, IP strategy, secrets, and security maintenance |

## Check compatibility before editing

- Upgrade Traefik CRDs and RBAC together. Gateway API installations also need
  the matching Gateway API CRDs, and Kubernetes providers discover backends
  through EndpointSlices.
- Revalidate custom resources after a CRD upgrade. CEL and regular-expression
  validation are stricter, and the schema no longer supplies a default
  load-balancing strategy.
- Retest Kubernetes Ingress `Prefix` routes because matching follows Kubernetes
  semantics rather than Traefik's earlier interpretation.
- Treat generated Kubernetes resource names as migration-sensitive, especially
  when automation depends on their exact form.
- Use path-only health-check paths; absolute URLs are rejected.
- Remove reliance on deprecated `defaultRuleSyntax` and `ruleSyntax` settings.
- Replace ForwardAuth configurations that depend on `TrustForwardHeader`, and
  set body-size limits explicitly when forwarding request or response bodies.
- Set trace verbosity explicitly when span detail matters; the default emits
  fewer spans.
- Treat ingress-nginx snippets as constrained translations. Traefik parses only
  supported, allowlisted directives and never inserts arbitrary raw NGINX.
- Audit plugin manifests before allowing unsafe interpreter operations or
  syscalls, since both enlarge the plugin's execution authority.
- On the 3.7 patch line, use 3.7.11 rather than an earlier patch to incorporate
  the accumulated HTTP, TLS, Kubernetes, and security corrections.

Read [Kubernetes and Gateway API](references/kubernetes.md) for controller and
manifest migrations, [Security, TLS, and authentication](references/security-tls-auth.md)
for trust-boundary changes, and [Providers and operations](references/providers-operations.md)
before selecting a deployment image or enabling plugins.

## Build multi-layer HTTP routing

Use `parentRefs` when a parent router must apply shared middleware or TLS and
enrich a request before a child evaluates its own rule.

```yaml
http:
  routers:
    api-parent:
      rule: "Host(`api.example.com`) && PathPrefix(`/`)"
      entryPoints:
        - websecure
      middlewares:
        - auth-with-tier
      tls: {}
    api-enterprise:
      rule: "HeaderRegexp(`X-Customer-Tier`, `(enterprise|business)`)"
      parentRefs:
        - api-parent
      service: stable-backend
```

Keep the hierarchy structural rules intact:

- Attach root routers to entry points and omit a service from them.
- Let intermediate routers have children.
- Put the selected service on leaf routers.
- Expect every request to traverse its parent before reaching a child.

Router rules also accept wildcard `Host` and `HostSNI` names. Set provider
precedence when routes produced by different providers can compete. Review the
encoded-character policy before combining router hierarchies with rewriting or
prefix stripping.

## Apply behavior at the service boundary

Attach middleware directly to an HTTP service when every router selecting that
service must receive the same processing. This also lets Gateway API filters
apply to HTTP backends.

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

Use status-aware retries when retry policy depends on backend responses:

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

Opt in deliberately before retrying non-idempotent methods. For service-level
failover, define the response-status ranges that should switch from the primary
to the fallback. See [Routing, middleware, and services](references/routing-services.md)
for provider-specific balancing strategies and CRD failover syntax.

## Choose health and balancing behavior

- Use native TCP health checks for non-HTTP backends.
- Use passive checks to infer health from live traffic.
- Set a distinct unhealthy interval when failed servers need a different probe
  cadence.
- Choose `p2c`, `Least Time`, or `HighestRandomWeight` only where the target
  provider supports it.
- Scope sticky cookies with both path and domain where the defaults are too
  broad.
- Treat condition-only EndpointSlice updates as backend-state changes.

Read the routing and services reference before translating file-provider
services into Kubernetes CRDs; strategy availability differs by provider.

## Configure Kubernetes integrations

The Gateway provider supports HTTP, gRPC, and TLS routes with method, query,
destination-port, regular-expression path, rewrite, redirect, response-header,
backend-protocol, backend-TLS, and reference-grant behavior. It also reports
route validity and supported features.

For ingress-nginx migration, enable `kubernetesIngressNginx` as a normal
provider and audit every annotation:

```yaml
providers:
  kubernetesIngressNginx:
    enabled: true
```

Compatibility includes many common authentication, rewrite, timeout,
buffering, affinity, canary, rate-limit, header, error, access-log, and
entry-point cases, but it is not a raw NGINX execution layer.

For Knative workloads, enable the experimental integration and scope watched
namespaces:

```yaml
experimental:
  knative: true
providers:
  knative:
    namespaces:
      - serverless-apps
      - production
```

Read [Kubernetes and Gateway API](references/kubernetes.md) for exact API
channels, status ownership, certificate references, safe naming, and
cross-namespace controls.

## Secure certificates and upstream TLS

Treat ACME settings as resolver-local: resolvers can have separate account
email addresses and custom CA trust. Configure profiles, multiple contacts,
challenge propagation, HTTP challenge delay, provider timeouts, certificate
duration, OCSP, and certificate timeouts only where required.

TLS configuration can disable session tickets and default-option fallback,
enable `X25519MLKEM768`, and restrict upstream cipher suites through
`ServersTransport`. Router TLS replaces rather than merges with entry-point TLS.
Read [Security, TLS, and authentication](references/security-tls-auth.md) before
debugging SNI, shared SANs, fragmented ClientHello messages, or missing Secrets.

## Preserve observability intent

- Set OTLP metrics `service.name` and resource attributes deliberately.
- Correlate access logs with traces using trace ID and entry-point span ID.
- Enable application-log and access-log OTLP export through the required
  experimental setting, and use stdio when a local stream is also needed.
- Apply metrics, tracing, and access-log controls at entry-point or router scope
  when global settings are too broad.
- Use the support-dump endpoint for diagnostic state and configure the
  API/dashboard base path when mounting the UI below a prefix.
- Inspect certificate and service details in the dashboard during TLS and
  balancing investigations.

Read [Observability](references/observability.md) for Kubernetes resource
detection, trace-context attributes, secret-file handling, and UI additions.

## Validate the finished change

1. Validate static and dynamic configuration with the same provider mix used
   in the target environment.
2. Apply current CRDs before custom resources, then verify controller status,
   namespace boundaries, and EndpointSlice RBAC.
3. Exercise WebSocket, CONNECT, redirect, CORS, encoded-path, authentication,
   retry, mirroring, and health-check behavior when relevant.
4. Inspect access logs, traces, route status, and dashboard service/certificate
   details for the expected result.
5. Review patch-line security and compatibility fixes before choosing an image.

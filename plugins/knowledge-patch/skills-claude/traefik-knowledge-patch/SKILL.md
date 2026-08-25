---
name: traefik-knowledge-patch
description: Traefik
version: 3.7.0
license: MIT
metadata:
  author: Nevaberry
---


# Traefik Knowledge Patch

Use this guide to identify changed Traefik behavior before editing static
configuration, dynamic configuration, Kubernetes resources, provider settings,
or deployment manifests. Open the matching reference for exact compatibility
details and patch-line corrections.

## Reference index

| Reference | Topics |
| --- | --- |
| [Kubernetes and Gateway API](references/kubernetes.md) | Gateway API, Ingress, Ingress NGINX, EndpointSlices, CRDs, Knative, status, and namespace safety |
| [Observability](references/observability.md) | OpenTelemetry, access logs, support dumps, API/dashboard paths, and dashboard features |
| [Providers and operations](references/providers-operations.md) | Docker, Swarm, Nomad, ECS, HTTP provider, plugins, socket activation, patching, and Redis |
| [Routing, middleware, and services](references/routing-services.md) | Router hierarchies, matching, ForwardAuth, retries, compression, encoded paths, health checks, and load balancing |
| [Security, TLS, and authentication](references/security-tls-auth.md) | ACME, certificate selection, TLS options, upstream TLS, forwarded headers, and authentication boundaries |

## Start with upgrade hazards

- Upgrade Traefik Kubernetes CRDs and RBAC together. All Kubernetes providers
  discover backends through EndpointSlices, while Gateway API installations
  require the CRDs matching the provider's supported channel and release.
- Revalidate custom resources after CRD upgrades. CEL and regular-expression
  validation became stricter, the schema no longer supplies a default
  load-balancing strategy, and patch releases changed generated resource names.
- Retest Kubernetes Ingress `Prefix` routes. Matching follows Kubernetes
  semantics and can differ from earlier Traefik behavior.
- Remove dependencies on `defaultRuleSyntax` and `ruleSyntax`; both options are
  deprecated.
- Use path-only health-check paths. Absolute URLs are rejected.
- Replace ForwardAuth configurations that rely on `TrustForwardHeader`; it is
  deprecated. Set request and response body limits explicitly when bodies cross
  the authentication boundary.
- Set tracing verbosity explicitly when span detail matters because tracing
  emits fewer spans by default.
- Treat ingress-nginx snippets as constrained translation. Snippet fields are
  parsed into allowlisted directives and unsupported input is rejected.
- Review plugin manifests before enabling unsafe operations or syscall access.
  Both expand the code a plugin can execute.
- Keep the active patch line current. Security and behavior corrections landed
  after the initial feature release.

Read [Kubernetes and Gateway API](references/kubernetes.md) before a controller
upgrade, [Routing, middleware, and services](references/routing-services.md)
before middleware migration, and
[Providers and operations](references/providers-operations.md) before selecting
an image or enabling plugins.

## Build hierarchical HTTP routing

HTTP routers can use `parentRefs` so a parent applies middleware or TLS and can
enrich the request before a child evaluates its rule.

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

Preserve the hierarchy's structural rules:

- Attach root routers to entry points and omit a service from them.
- Allow intermediate routers to have children.
- Select a service only on leaf routers.
- Expect each request to traverse its parent before reaching a child.

`Host` and `HostSNI` rules also accept wildcard names. Set provider precedence
when routes from different providers can compete. See
[Routing, middleware, and services](references/routing-services.md) before
combining hierarchies with encoded-path or forwarded-header policy.

## Apply middleware at the service boundary

Attach middleware directly to an HTTP service when every router selecting that
service must receive the same processing. This also allows Gateway API filters
to apply to HTTP backends.

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

Use status-aware retry policy when backend response status controls whether an
attempt should be repeated:

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
failover, configure status ranges that move traffic from the primary service to
the fallback. The services reference documents health-check modes, provider
strategy differences, stickiness, mirroring, and CRD failover syntax.

## Choose health and balancing behavior

- Use native TCP health checks for non-HTTP backends.
- Use passive health checks to infer health from live traffic.
- Set a distinct unhealthy interval when failed servers need a different probe
  cadence.
- Select `p2c`, `Least Time`, or `HighestRandomWeight` only where the provider
  supports the strategy.
- Scope sticky cookies with path and domain when the default scope is too broad.
- Configure Redis keyspace notifications before relying on Redis-driven
  configuration updates.

Read [Routing, middleware, and services](references/routing-services.md) before
translating a file-provider service into a Kubernetes CRD because strategy
availability is not identical across providers.

## Configure Kubernetes integrations

The Gateway provider supports current HTTP, gRPC, and TLS routing features,
including method, query, destination-port, regular-expression path, rewrite,
redirect, response-header, backend-protocol, backend-TLS, and reference-grant
handling. It publishes route validity and supported-feature status.

Enable the ingress-nginx compatibility provider as a normal provider and audit
every annotation:

```yaml
providers:
  kubernetesIngressNginx:
    enabled: true
```

Compatibility covers many authentication, rewrite, timeout, buffering,
affinity, canary, rate-limit, header, error, access-log, and entry-point cases,
but does not execute arbitrary NGINX configuration.

Knative support remains experimental and can be namespace-scoped:

```yaml
experimental:
  knative: true
providers:
  knative:
    namespaces:
      - serverless-apps
      - production
```

Read [Kubernetes and Gateway API](references/kubernetes.md) for API-channel
requirements, status ownership, TLS references, generated-name changes, and
cross-namespace safety controls.

## Secure certificates and upstream TLS

Treat ACME settings as resolver-local. Resolvers can use separate account
emails and custom CA trust. Configure profiles, multiple contacts, challenge
propagation, HTTP challenge delay, provider timeouts, and certificate timeouts
only where required by the CA or network.

TLS configuration can disable session tickets, use the `X25519MLKEM768` curve,
restrict upstream cipher suites with `ServersTransport`, and disable fallback
to the default TLS options. Router TLS replaces entry-point TLS rather than
merging with it.

Certificate selection and router isolation contain patch-line corrections. Read
[Security, TLS, and authentication](references/security-tls-auth.md) before
debugging SNI, shared SANs, fragmented ClientHello messages, missing Secrets,
or multiple Gateway listener certificate references.

## Preserve observability intent

- Set the OTLP metrics `service.name` and resource attributes deliberately.
- Correlate access logs with traces using trace ID and entry-point span ID.
- Gate application-log and access-log OTLP export with the experimental
  setting; use stdio alongside OTLP when a local stream is also required.
- Apply metrics, tracing, and access-log controls at entry-point or router scope
  when global settings are too broad.
- Use the support-dump API for diagnostic state and configure the API/dashboard
  base path when mounting the UI below a prefix.
- Inspect the dashboard's certificate and service details when diagnosing
  certificate attachment, expiration, or backend weighting.

See [Observability](references/observability.md) for Kubernetes resource
detection, trace attributes, access-log fields, secret-file handling, and UI
behavior.

## Validate the finished change

1. Validate static and dynamic configuration with the same provider mix used
   by the target deployment.
2. Apply current CRDs before custom resources, then verify controller status,
   EndpointSlice RBAC, namespace policy, and status ownership.
3. Exercise WebSocket, CONNECT, redirect, CORS, encoded-path, authentication,
   retry, mirroring, and health-check behavior when the change touches them.
4. Inspect access logs, traces, route status, and dashboard service/certificate
   details for the expected result.
5. Check patch-line security and compatibility notes before choosing a
   deployment image.

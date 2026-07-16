---
name: traefik-knowledge-patch
description: Traefik 3.7.0 compatibility. Use for Traefik work.
license: MIT
version: 3.7.0
metadata:
  author: Nevaberry
---

# Traefik Knowledge Patch

Use this guide to identify the changed behavior that affects a Traefik task, then
open the matching topic reference before editing static configuration, dynamic
configuration, Kubernetes resources, or deployment manifests.

## Reference index

| Reference | Topics |
| --- | --- |
| [HTTP routing and middleware](references/http-routing-middleware.md) | Router hierarchies, matching, ForwardAuth, retries, compression, encoded paths, headers, and proxy behavior |
| [Kubernetes providers](references/kubernetes-providers.md) | Gateway API, Ingress NGINX, EndpointSlices, CRDs, Knative, and Kubernetes service discovery |
| [Observability and API](references/observability-api.md) | OpenTelemetry, access logs, support dumps, API/dashboard paths, and dashboard features |
| [Operations and migration](references/operations-migration.md) | Provider operations, plugins, socket activation, migration hazards, and security maintenance |
| [Services, health checks, and load balancing](references/services-health-load-balancing.md) | Service middleware, active/passive health checks, balancing, failover, stickiness, and mirroring |
| [TLS and ACME](references/tls-acme.md) | ACME accounts and challenges, OCSP, TLS curves, session tickets, upstream TLS, and certificate selection |

## Start with compatibility checks

Before changing configuration, check the following high-impact behavior:

- Upgrade Kubernetes CRDs and RBAC together. Gateway API installations need the
  matching Gateway API CRDs, and every Kubernetes provider now discovers
  backends through EndpointSlices.
- Revalidate Kubernetes manifests after a CRD upgrade. CEL and regular-expression
  validation are stricter, and the CRD schema no longer supplies a default
  load-balancing strategy.
- Retest Kubernetes Ingress `Prefix` routes. Matching now follows Kubernetes
  semantics rather than Traefik's earlier interpretation.
- Use path-only health-check paths. Absolute URLs are rejected.
- Remove reliance on `defaultRuleSyntax` and `ruleSyntax`; both are deprecated.
- Replace ForwardAuth configurations that depend on `TrustForwardHeader`; the
  option is deprecated. Also set request-body limits explicitly when bodies are
  forwarded to an authentication service.
- Set trace verbosity explicitly when span detail matters. Tracing emits fewer
  spans by default.
- Treat ingress-nginx snippet compatibility as constrained translation. Snippet
  fields accept only parsed, allowlisted directives, never arbitrary raw NGINX
  configuration.
- Review plugin manifests before enabling unsafe operations or syscall access.
  Both expand the code a plugin can execute.

Read [Kubernetes providers](references/kubernetes-providers.md) for manifest and
controller changes, [HTTP routing and middleware](references/http-routing-middleware.md)
for middleware migrations, and [Operations and migration](references/operations-migration.md)
for provider and security checks.

## Build multi-layer HTTP routing

Use `parentRefs` to make a parent router apply shared middleware or TLS and enrich
the request before a child router evaluates its own rule.

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

Keep these structural rules intact:

- Attach root routers to entry points and omit a service from them.
- Let intermediate routers have children.
- Put the selected service on leaf routers.
- Expect every request to traverse its parent before reaching a child.

Router matching also accepts wildcard `Host` and `HostSNI` names. Configure
provider precedence when routes produced by different providers compete. Read
[HTTP routing and middleware](references/http-routing-middleware.md) before
combining hierarchies with encoded-path policies or forwarded-header handling.

## Apply behavior at the service boundary

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

Use status-aware retries when retry policy depends on the backend response:

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
failover, configure status ranges that should switch from the primary to the
fallback. Read [Services, health checks, and load balancing](references/services-health-load-balancing.md)
for balancing strategies, health-check modes, and CRD failover syntax.

## Choose health and balancing behavior

- Use native TCP health checks for non-HTTP backends.
- Use passive health checks to infer health from live traffic.
- Set a distinct unhealthy interval when failed servers need a different probe
  cadence.
- Select `p2c`, `Least Time`, or `HighestRandomWeight` only where the chosen
  provider supports it.
- Scope sticky cookies with path and domain when the default cookie scope is too
  broad.

Read the services reference before translating a file-provider service into a
Kubernetes CRD; strategy availability is not identical across providers.

## Configure Kubernetes integrations

The Gateway provider supports current HTTP, gRPC, and TLS routing capabilities,
including method, query, destination-port, regular-expression path, rewrite,
redirect, response-header, backend protocol, backend TLS, and reference-grant
handling. It reports route validity and supported features.

For ingress-nginx migration, enable `kubernetesIngressNginx` as a normal provider
and audit every annotation. Compatibility covers many common authentication,
rewrite, timeout, buffering, affinity, canary, rate-limit, header, error, access
log, and entry-point cases, but it is not a raw NGINX execution layer.

For serverless workloads, enable Knative support and scope watched namespaces:

```yaml
experimental:
  knative: true
providers:
  knative:
    namespaces:
      - serverless-apps
      - production
```

Read [Kubernetes providers](references/kubernetes-providers.md) for exact API
capabilities, status ownership, TLS references, and provider-specific safety
controls.

## Secure certificates and upstream TLS

Treat ACME settings as resolver-local: resolvers can use separate account email
addresses and custom CA trust. Configure profiles, multiple contacts, challenge
propagation, HTTP challenge delay, provider timeouts, and certificate timeouts
only where required by the CA or network.

TLS configuration can disable session tickets, enable the post-quantum
`X25519MLKEM768` curve, and restrict upstream cipher suites through
`ServersTransport`. Certificate selection and router TLS isolation include
important patched behavior, so read [TLS and ACME](references/tls-acme.md) before
debugging SNI, shared SANs, fragmented ClientHello messages, or missing Secrets.

## Preserve observability intent

- Set the OTLP metrics `service.name` and resource attributes deliberately.
- Correlate access logs with traces using trace ID and entry-point span ID.
- Enable application-log and access-log OTLP export only with the required
  experimental setting, while using stdio output when a local stream is also
  needed.
- Apply metrics, tracing, and access-log controls at entry-point or router scope
  when global settings are too broad.
- Use the support-dump API for diagnostic state and configure the API/dashboard
  base path when mounting the UI below a prefix.

Read [Observability and API](references/observability-api.md) for Kubernetes
resource detection, trace attributes, access-log fields, secret-file handling,
and dashboard additions.

## Validate the finished change

After editing a deployment or configuration:

1. Validate static and dynamic configuration with the same provider mix used in
   the target environment.
2. Apply current CRDs before applying custom resources, then verify controller
   status and EndpointSlice RBAC.
3. Exercise WebSocket, redirect, CORS, encoded-path, authentication, retry, and
   health-check behavior when the change touches those paths.
4. Inspect access logs, traces, route status, and dashboard service/certificate
   details for the expected result.
5. Check the operations reference for patch-line security and compatibility
   fixes before choosing a deployment image.

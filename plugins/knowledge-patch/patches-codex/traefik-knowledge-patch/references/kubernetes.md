# Kubernetes and Gateway API

## Plan CRD, API, and RBAC upgrades

All Kubernetes providers discover backends through EndpointSlices (since
3.1.0). Make the EndpointSlice API available and grant the required RBAC before
upgrading. Kubernetes discovery also refreshes backend state for condition-only
EndpointSlice changes even when endpoint addresses stay unchanged (3.6.21).

The Kubernetes upgrade from 3.1 to 3.2 ships updated Traefik CRDs. Gateway
installations also require the Gateway API v1.2 CRDs and matching RBAC (3.2.0).
Apply CRDs before custom resources.

Newer Traefik CRDs apply stronger CEL validation and stricter regular-expression
validation for HTTP status codes. Resources accepted by old schemas may fail
after an upgrade. The CRD schema also stopped defaulting the load-balancing
strategy, so set the intended strategy explicitly (3.4.0).

## Match the installed Gateway API channel

The Kubernetes Gateway provider graduated from experimental status with Gateway
API v1.1.0 (3.1.0). It became a regular provider.

Its HTTPRoute support includes method and query-parameter matches,
`RegularExpression` paths, `HTTPURLRewrite`, redirects that set scheme or port,
`ReferenceGrant` backend authorization, and status reporting for invalid routes
(3.1.0).

Gateway API v1.2.0 adds `GRPCRoute` support (3.2.0). HTTPRoute and GRPCRoute can
select backend protocols, including `http` and `https` Service `appProtocol`
values, and `BackendTLSPolicy` secures backend connections. HTTPRoute also
supports destination-port matching, `ResponseHeaderModifier`, and `NativeLB`.
Traefik publishes supported features in `GatewayClass` status.

Gateway API v1.3 resources are supported in 3.5.0. Gateway API v1.4 support in
3.6.0 moves `BackendTLSPolicy` and `SupportedFeatures` reporting from the
Experimental channel to the Standard channel.

Gateway API v1.5.1 support adds multiple listener `certificateRefs` for SNI
selection and permits `BackendTLSPolicy.caCertificateRefs` to select Secrets
containing private CA bundles (3.7.0). Patched releases reject cross-provider
`backendRefs.namespace` references and resolve backend `ExtensionRef` filters
relative to the HTTPRoute namespace.

Gateway API v1.6.1 arrived in 3.7.10 and requires Experimental Channel CRDs
(3.7.11). In 3.7.11, `URLRewrite` and `RequestRedirect` preserve the
representation of encoded path segments.

## Preserve route precedence and controller ownership

The Gateway provider assigns rule priority to TLSRoute rules, defining
precedence when TLS routes compete (3.4.0).

In multi-controller clusters, Traefik ignores route `parentRefs` for Gateways it
does not manage and writes route-parent status only for managed Gateways
(3.6.21). Do not make one controller depend on status owned by another.

## Configure Ingress and CRD discovery

Ingress and CRD providers can use internal node addresses for NodePort services,
which supports clusters without suitable external node addresses. CRD services
backed by Kubernetes `ExternalName` Services can have health checks (3.1.0).

IngressRoute definitions may omit an explicit route `kind`. Ingress and CRD
providers recognize serving endpoints, including when selecting sticky-session
backends (3.3.0).

Ingress can publish status for `ClusterIP` and `NodePort` Service types, while
CRD service TLS configuration can source root CAs from ConfigMaps (3.4.0).

Ingress `Prefix` matching follows Kubernetes-documented semantics. Retest routes
that depended on the older interpretation (3.5.0).

ECS can discover IPv6 endpoints; Docker can discover containers that are not
running; and Kubernetes Ingress can publish `ExternalName` Services through
Traefik (3.6.0).

Kubernetes CRDs add `ingressClassName`, and Knative v1.20 is supported (3.7.0).

Generated Kubernetes names changed to avoid collisions (3.7.11):

- CRD-generated Service names are scoped to the parent resource.
- Failover Services are named after the referenced Kubernetes Service.
- A safe-naming option is available.

Treat automation that consumes generated names as migration-sensitive.

The CRD provider now enforces cross-namespace Service-reference checks correctly
and can restrict which namespace supplies default TLS resources. Kubernetes
Ingress service middlewares enforce `crossProviderNamespace` (3.7.11).

## Migrate ingress-nginx resources

The ingress-nginx compatibility provider began as an experimental integration
covering common use cases and essential annotations. It never promised complete
compatibility, so migrations must inventory the annotations they use (3.5.0).

The `kubernetesIngressNginx` provider is first-class and needs no experimental
flag (3.7.0):

```yaml
providers:
  kubernetesIngressNginx:
    enabled: true
```

It recognizes more than 85 common annotations for authentication, redirects,
rewrites, timeouts, buffering, affinity, canaries, rate limits, custom headers,
custom errors, access logs, and per-Ingress entry points.

`configuration-snippet`, `server-snippet`, and `auth-snippet` have partial
support. Traefik converts supported directives into structured configuration and
rejects unsupported input rather than injecting raw NGINX. Audit
`AllowCrossNamespaceResources`, `GlobalAllowedResponseHeader`,
`strictValidatePathType`, and `ipAllowListStrategy` as explicit compatibility
and safety controls.

Authentication, custom headers, custom errors, and SSL redirects also apply to
the default backend. Default entry-point selection respects `asDefault` and
excludes internal entry points (3.7.11).

## Enable Knative deliberately

The Knative provider discovers services, follows scaling events, and routes
traffic for Knative workloads. It remains experimental and can restrict watched
namespaces (3.6.0):

```yaml
experimental:
  knative: true
providers:
  knative:
    namespaces:
      - serverless-apps
      - production
```

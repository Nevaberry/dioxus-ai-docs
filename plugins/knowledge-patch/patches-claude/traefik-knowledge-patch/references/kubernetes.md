# Kubernetes and Gateway API

## Plan CRD, RBAC, and discovery upgrades

All Kubernetes providers use EndpointSlices for backend discovery (since
3.1.0). Grant Traefik access to EndpointSlices before upgrading a cluster. A
later fix detects condition-only EndpointSlice changes, so endpoint health is
refreshed even when addresses do not change (3.6.21).

The v3.1-to-v3.2 transition includes updated Traefik CRDs. Gateway API users
must also install the v1.2 CRDs and matching RBAC (3.2.0). Revalidate resources
after every CRD update: CEL validation and regular-expression validation for
HTTP status codes became stricter, and the CRD schema stopped supplying a
default load-balancing strategy (3.4.0). Set the intended strategy explicitly.

Patch releases also changed generated Kubernetes resource names to prevent
collisions (3.7.11):

- CRD-generated Service names are scoped to their parent.
- Failover Services are named for the referenced Kubernetes Service.
- A safe-naming option is available.

Treat scripts or policies that depend on generated names as migration-sensitive.

## Track Gateway API capabilities

The Kubernetes Gateway provider became a regular, non-experimental provider
with Gateway API v1.1.0 (3.1.0). That version supports HTTP method and query
parameter matches, `RegularExpression` path matching, `HTTPURLRewrite`, redirects
that set scheme or port, `ReferenceGrant` for HTTPRoute backends, and route
status including invalid routes.

Gateway API v1.2.0 adds `GRPCRoute` (3.2.0). `HTTPRoute` and `GRPCRoute` can
select backend protocols, including Kubernetes Service `appProtocol` values
`http` and `https`, and can use `BackendTLSPolicy`. HTTPRoute additionally gains
destination-port matches and `ResponseHeaderModifier`; Gateway Services support
`NativeLB`. Traefik publishes supported features in `GatewayClass` status.

The provider then progresses through Gateway API v1.3 (3.5.0), v1.4 (3.6.0),
and v1.5.1 (3.7.0). In v1.4, `BackendTLSPolicy` and `SupportedFeatures` status
move from the Experimental channel to the Standard channel. With v1.5.1:

- listeners can provide multiple `certificateRefs` for SNI selection;
- `BackendTLSPolicy.caCertificateRefs` can reference Secrets containing private
  CA bundles;
- patched releases reject cross-provider `backendRefs.namespace` references;
- backend `ExtensionRef` filters resolve relative to the `HTTPRoute` namespace.

The provider moves to Gateway API v1.6.1 in 3.7.10 and requires the Experimental
Channel CRDs (3.7.11). In 3.7.11, `URLRewrite` and `RequestRedirect` preserve
encoded path segments instead of changing their representation.

For `TLSRoute`, Traefik sets rule priority so competing TLS routes have defined
precedence (3.4.0). Gateway API header modifiers can change `Host`; redirects
retain the incoming scheme when no scheme is specified and emit the configured
status (3.7.0 patch line).

## Respect controller status ownership

Traefik reports Gateway route validity and supported features, but must not
claim another controller's objects. The managed-Gateway correction ignores
route `parentRefs` for Gateways Traefik does not manage and updates parent status
only for managed Gateways (3.6.21).

## Configure Kubernetes backends

The Ingress and CRD providers can use node internal addresses for NodePort
Services, which supports clusters without suitable external node addresses
(3.1.0). The CRD provider can health-check `ExternalName` Services (3.1.0), and
Kubernetes Ingress can publish `ExternalName` Services through Traefik (3.6.0).

The Ingress and CRD providers recognize serving endpoints, including for sticky
backend selection (3.3.0). An `IngressRoute` route can omit its explicit `kind`
(3.3.0). Ingress status publication supports `ClusterIP` and `NodePort` Service
types (3.4.0). CRDs later add `ingressClassName` (3.7.0).

Kubernetes CRD service TLS can source root CA certificates from ConfigMaps
(3.4.0). Health-check paths are validated and must be path-only; absolute URLs
are invalid (3.7.0).

## Recheck Ingress prefix matching

Kubernetes Ingress `Prefix` routes follow Kubernetes matching semantics rather
than Traefik's older interpretation (3.5.0). Test edge cases around segment
boundaries during an upgrade.

## Migrate ingress-nginx resources

The ingress-nginx compatibility provider begins as experimental and intentionally
covers common use cases and essential annotations rather than the full NGINX
surface (3.5.0). It graduates as the first-class `kubernetesIngressNginx`
provider in 3.7.0:

```yaml
providers:
  kubernetesIngressNginx:
    enabled: true
```

It supports more than 85 common annotations across authentication, redirect and
rewrite, timeout and buffering, affinity and canary, rate limiting, custom
headers and errors, access logs, and per-Ingress entry points. Audit each
annotation rather than assuming drop-in equivalence.

`configuration-snippet`, `server-snippet`, and `auth-snippet` have partial
support. Traefik parses them into structured, allowlisted directives and rejects
unsupported input; it does not inject raw NGINX. Use
`AllowCrossNamespaceResources`, `GlobalAllowedResponseHeader`,
`strictValidatePathType`, and `ipAllowListStrategy` for the corresponding
compatibility and safety policies (3.7.0).

Authentication, custom headers, custom errors, and SSL redirects also apply to
the ingress-nginx default backend (3.7.11). Default entry-point selection honors
`asDefault` and excludes internal entry points.

## Enforce namespace boundaries

The CRD provider corrects cross-namespace Service-reference checks, and
Kubernetes Ingress service middleware enforces `crossProviderNamespace`
(3.7.11). The CRD provider can restrict which namespace supplies default TLS
resources. Keep these checks enabled unless cross-namespace access is an
explicit part of the design.

## Run Knative workloads

The experimental Knative provider discovers services, follows scaling events,
and routes workload traffic (3.6.0). Limit the namespaces it watches:

```yaml
experimental:
  knative: true
providers:
  knative:
    namespaces:
      - serverless-apps
      - production
```

Knative v1.20 is supported (3.7.0).

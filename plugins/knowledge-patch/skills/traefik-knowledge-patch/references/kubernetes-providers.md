# Kubernetes Providers

Use this reference for Gateway API, Kubernetes Ingress and CRD behavior,
Ingress NGINX migration, EndpointSlice discovery, and Knative.

## Gateway API routes and status

- The Kubernetes Gateway provider graduated from experimental status with
  Gateway API v1.1.0 (since 3.1.0).
- `HTTPRoute` supports method and query-parameter matches,
  `RegularExpression` paths, `HTTPURLRewrite`, and redirects that set scheme or
  port. It honors `ReferenceGrant` for backends and reports status for valid and
  invalid routes (since 3.1.0).
- Gateway API v1.2.0 and `GRPCRoute` are supported (since 3.2.0). `HTTPRoute` and
  `GRPCRoute` support backend protocol selection, including `http` and `https`
  Service `appProtocol` values, plus `BackendTLSPolicy` for TLS backends.
- `HTTPRoute` can match the destination port and use
  `ResponseHeaderModifier` to add, set, or remove response headers; Gateway
  services can use `NativeLB` (since 3.2.0).
- Traefik publishes supported features in `GatewayClass` status (since 3.2.0).
- `TLSRoute` rules receive a priority to define precedence when routes compete
  (since 3.4.0).
- Gateway API v1.3 resources are supported (since 3.5.0).
- Gateway API v1.4 is supported (since 3.6.0); `BackendTLSPolicy` and
  `SupportedFeatures` status reporting are Standard-channel features in that API
  release rather than Experimental-channel features.
- Gateway API v1.5.1 is supported (since 3.7.0). Listeners can use multiple
  `certificateRefs` for SNI selection, and `BackendTLSPolicy.caCertificateRefs`
  can reference Secrets containing private CA bundles.
- Patched 3.7 behavior rejects cross-provider `backendRefs.namespace` references
  and resolves backend `ExtensionRef` filters relative to the `HTTPRoute`
  namespace (3.7.0 batch).
- The provider ignores route `parentRefs` for Gateways it does not manage and
  updates parent status only for managed Gateways (3.6.21). This avoids status
  ownership conflicts in clusters with multiple Gateway controllers.

## Endpoint and Service discovery

- All Kubernetes providers discover backends through EndpointSlices (since
  3.1.0). Upgrade RBAC so Traefik can read EndpointSlices before rollout.
- Condition-only EndpointSlice updates now refresh backend state even when
  endpoint addresses are unchanged (3.6.21).
- Kubernetes Ingress and CRD providers can use node internal IPs for NodePort
  Services (since 3.1.0).
- The CRD provider supports health checks for Kubernetes `ExternalName`
  Services (since 3.1.0).
- Kubernetes Ingress and CRD providers recognize serving endpoints, including
  during sticky-session backend selection (since 3.3.0).
- Kubernetes Ingress can publish status for `ClusterIP` and `NodePort` Service
  types (since 3.4.0).
- Kubernetes CRD service TLS can load root CAs from ConfigMaps (since 3.4.0).
- Kubernetes Ingress can publish Services of type `ExternalName` through
  Traefik (since 3.6.0).

## CRDs and upgrade validation

- Upgrading from the preceding minor release to the 3.2.0 batch requires updated
  Traefik CRDs. Gateway API installations also require the v1.2 CRDs and matching
  RBAC.
- `IngressRoute` definitions may omit the explicit route `kind` (since 3.3.0).
- Ingress CRDs have stricter CEL validation and tighter regular-expression
  validation for HTTP status codes (since 3.4.0). A previously accepted manifest
  can fail after upgrading the CRD schema.
- Kubernetes CRDs no longer supply a default load-balancing strategy (since
  3.4.0). Set the intended strategy explicitly.
- Kubernetes CRDs add `ingressClassName` (since 3.7.0).

## Kubernetes Ingress matching

- Ingress `Prefix` matching follows the behavior in Kubernetes documentation
  (since 3.5.0). Retest routes that depended on Traefik's former prefix
  interpretation.

## Ingress NGINX compatibility

- The Ingress NGINX provider began as an experimental migration path in 3.5.0.
  It consumes existing ingress-nginx resources without rewriting manifests, but
  its initial support covered common use cases and essential annotations rather
  than complete compatibility.
- `kubernetesIngressNginx` is a first-class provider and no longer needs the
  experimental flag (since 3.7.0). It supports more than 85 common annotations
  spanning authentication, redirects and rewrites, timeouts and buffering,
  affinity and canaries, rate limits, custom headers and errors, access logs,
  and per-Ingress entry points.

  ```yaml
  providers:
    kubernetesIngressNginx:
      enabled: true
  ```

- `configuration-snippet`, `server-snippet`, and `auth-snippet` receive partial
  support: Traefik parses allowlisted structured directives and rejects
  unsupported input instead of injecting raw NGINX configuration (since 3.7.0).
- `AllowCrossNamespaceResources`, `GlobalAllowedResponseHeader`,
  `strictValidatePathType`, and `ipAllowListStrategy` add compatibility and
  safety controls (since 3.7.0).

## Knative

- The Knative provider is experimental (since 3.6.0). It discovers Services,
  follows scaling events, routes Knative workloads, and can restrict discovery
  to configured namespaces.
- Knative v1.20 is supported (since 3.7.0).

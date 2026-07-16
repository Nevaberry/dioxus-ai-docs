# Networking, Services, and Gateway API

Use this reference for Services, EndpointSlices, kube-proxy, network validation, Gateway API, and Ingress-to-Gateway migration.

Entries are grouped by task; the parenthetical identifier is the source batch.

## `PreferClose` is deprecated (1.34-guide)

For Service `trafficDistribution`, use the clearer `PreferSameZone` alias or `PreferSameNode`; these values are beta and enabled by default, while `PreferClose` is deprecated.

## Aggregated APIs resolve EndpointSlices (1.34.0)

Kube-apiserver now proxies an APIService through EndpointSlices for its referenced Service rather than through Endpoints. Operators that manually publish aggregated-server backends must create an EndpointSlice instead of, or alongside, the legacy Endpoints object.

## BackendTLSPolicy standardizes upstream TLS (gateway-api-updates)

The v1.4 Standard channel includes `BackendTLSPolicy` for TLS from a Gateway to a backend. Its validation uses `hostname` for SNI and, unless `subjectAltNames` is supplied, identity verification; trust must come from up to eight `caCertificateRefs` bundles or implementation-provided roots via `wellKnownCACertificates: System`, and when SANs are present the hostname must also be listed there to remain an authenticated identity.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: BackendTLSPolicy
metadata:
  name: tls-upstream
spec:
  targetRefs:
  - group: ""
    kind: Service
    name: dev
    sectionName: btls
  validation:
    wellKnownCACertificates: System
    hostname: dev.example.com
```

## Built-in IP fields can use strict parsing (1.33.0)

With `StrictIPCIDRValidation`, built-in APIs reject IPv4 octets with leading zeroes and IPv4-mapped IPv6 forms such as `::ffff:192.168.0.1`; with the gate off, the API server warns instead. The stricter parsing does not apply to CRDs, component configuration, or command-line arguments.

## Client-certificate policy is scoped to a Gateway port (gateway-api-updates)

Gateway v1.4 adds `Gateway.spec.tls.default` for client-certificate validation shared by all HTTPS listeners and `Gateway.spec.tls.perPort` overrides. Per-hostname listener policies are unsafe because HTTP connection coalescing can reuse a connection without a new certificate check, so validation must be consistent for listeners sharing a port.

## Controllers canonicalize IP and CIDR fields (1.36-guide)

With `StrictIPCIDRValidation` now beta, Kubernetes controllers canonicalize IP values they write back to API objects and warn when they encounter malformed values already stored in the cluster.

## GatewayClass status advertises supported features (gateway-api-updates)

Standard `GatewayClass.status.supportedFeatures` lets implementations declare capabilities for users, tools, and automatic conformance-test selection. An implementation must populate the list before, or atomically with, accepting the GatewayClass.

```yaml
status:
  supportedFeatures:
  - HTTPRoute
  - HTTPRouteHostRewrite
  - HTTPRouteQueryParamMatching
```

## GRPCRoute now requires `spec` (gateway-api-updates)

The Standard GRPCRoute CRD now rejects objects with no top-level `.spec`; automation that previously emitted such objects must include it, even when empty.

```yaml
spec: {}
```

## HTTPRoute can call an external authorization service (gateway-api-updates)

The Experimental `ExternalAuth` filter calls an HTTP- or gRPC-based authentication and authorization backend and controls which headers it receives; HTTP mode can also configure a path prefix. For HTTP auth, a `200` allows the request and may add forwarded headers, while `403` denies it.

```yaml
filters:
- type: ExternalAuth
  externalAuth:
    protocol: HTTP
    backendRef:
      name: auth-service
    http:
      allowedHeaders:
      - Authorization
```

## HTTPRoute gains an experimental CORS filter (gateway-api-updates)

The Experimental HTTPRoute CRD accepts a `CORS` filter with `allowOrigins`, `allowMethods`, `allowHeaders`, `allowCredentials`, `exposeHeaders`, and `maxAge`. In v1.4, `allowCredentials` is strictly Boolean; previously accepted non-Boolean forms are rejected.

```yaml
filters:
- type: CORS
  cors:
    allowOrigins:
    - "https://app.example.com"
    allowMethods:
    - GET
    allowCredentials: true
```

## Ingress NGINX is retiring (1.35-guide)

The Kubernetes project announced best-effort Ingress NGINX maintenance only through March 2026, followed by archival without further updates. Existing users should plan a migration to Gateway API.

## Ingress-NGINX translation covers many more annotations (ingress-migration)

Version 1.0 expands support from three to more than 30 common annotations, including CORS, backend TLS, regular-expression matching, and path rewrites. `--emitter agentgateway`, `--emitter envoy-gateway`, or `--emitter kgateway` can add implementation-specific extensions when Standard Gateway API cannot represent the original setting.

## Ingress2Gateway 1.0 reads files or live cluster state (ingress-migration)

`ingress2gateway print` translates Ingress resources and provider-specific configuration into Gateway API YAML. It can read comma-separated manifests, one namespace, or every namespace in the current cluster.

```console
go install github.com/kubernetes-sigs/ingress2gateway@v1.0.0
ingress2gateway print --input-file ingress.yaml,other.yaml --providers=ingress-nginx > gwapi.yaml
ingress2gateway print --namespace my-api --providers=ingress-nginx > gwapi.yaml
ingress2gateway print --providers=ingress-nginx --all-namespaces > gwapi.yaml
```

## kube-proxy IPVS mode is deprecated (1.35-guide)

`ipvs` mode still works in 1.35 but emits a startup warning and should be migrated to the recommended `nftables` mode on Linux.

## Kube-proxy nftables mode is stable (1.33.0)

The nftables proxier is GA but is not the default; select it with `--proxy-mode=nftables` or `mode: nftables` in kube-proxy configuration. Its kernel-version check is skipped only when `KUBE_PROXY_NFTABLES_SKIP_KERNEL_VERSION_CHECK` is set to a non-empty value.

## Network API validation changes in both directions (1.36.0)

Default-on strict validation rejects ambiguous CIDRs such as `192.168.0.5/24`; use the network address or `/32`. Conversely, beta default-on `RelaxedServiceNameValidation` uses DNS-label rules, so Service names may begin with a digit.

## New experimental kinds have distinct API identities (gateway-api-updates)

Starting with v1.3, new Experimental-channel kinds use an `X` prefix and the `gateway.networking.x-k8s.io` API group. They can coexist with Standard resources, but if they graduate, migration requires recreating them under the non-`X` kind and non-`x-k8s` group.

## Node kube-proxy version status is removed (1.33-guide)

The inaccurate `.status.nodeInfo.kubeProxyVersion` field, disabled by default since 1.31, no longer exists in 1.33.

## Pod DNS search validation is relaxed (1.33.0)

The beta `RelaxedDNSSearchValidation` feature permits a Pod search domain to be a single dot or to contain an underscore.

## Request mirroring can select a percentage (gateway-api-updates)

Gateway API v1.3 adds Standard-channel partial mirroring: a `RequestMirror` filter can set either an integer `percent` or a `fraction` instead of copying every request to the mirror backend.

```yaml
filters:
- type: RequestMirror
  requestMirror:
    backendRef:
      name: foo-v2
      port: 8080
    fraction:
      numerator: 5
      denominator: 1000
```

## Route rules can be named and targeted (gateway-api-updates)

All route rule types gain an optional validated `name`, enabling rule-specific status, observability, tooling, and policy attachment through `targetRefs[].sectionName`. Implementations do not supply a default and may make the name immutable.

```yaml
spec:
  rules:
  - name: admin
    backendRefs:
    - name: admin-service
      port: 8080
```

## Routes can bind to default Gateways (gateway-api-updates)

Experimental defaulting lets a Route set `spec.useDefaultGateways: All` while operators opt Gateways in with `spec.defaultScope: All`. Binding is recorded only in `status.parents`, not injected into `parentRefs`, and a Route binds to every matching default Gateway.

```yaml
# HTTPRoute
spec:
  useDefaultGateways: All
  rules:
  - backendRefs:
    - name: app
      port: 80
---
# Gateway
spec:
  defaultScope: All
```

## Service `externalIPs` is deprecated (1.36-guide)

Using `Service.spec.externalIPs` emits deprecation warnings from 1.36 and is planned for removal in 1.43; migrate to `LoadBalancer`, `NodePort`, or Gateway API exposure as appropriate.

## Service CIDRs are managed through a stable API (1.33.0)

With `MultiCIDRServiceAllocator` stable, additional cluster Service ranges can be represented by `ServiceCIDR` objects. Administrators that require one range, a restricted range, or non-overlap with other networks must enforce those constraints themselves, for example with a `ValidatingAdmissionPolicy`.

## Service topology preferences move to `trafficDistribution` (1.33.0)

EndpointSlice `hints` and Service `trafficDistribution: PreferClose` are stable, while `service.kubernetes.io/topology-mode` is deprecated. With `PreferSameTrafficDistribution`, Services can instead request `PreferSameNode`; `PreferSameZone` is an alias for `PreferClose`.

```yaml
spec:
  trafficDistribution: PreferSameNode
```

## Some generated routes intentionally approximate Ingress-NGINX (ingress-migration)

Ingress-NGINX regex paths are emitted as case-insensitive prefix expressions such as `(?i)/users/(\d+).*`, and TCP-level `proxy-read-timeout` and `proxy-send-timeout` settings are mapped best-effort to an HTTPRoute request timeout. To reproduce Ingress-NGINX's default redirect behavior, output can also include an HTTP listener and a separate HTTPRoute that redirects to HTTPS; review all three conversions before applying them.

## The Endpoints API is deprecated (1.33-guide)

Kubernetes 1.33 warns on reads and writes of core `v1` Endpoints; consumers should list all `discovery.k8s.io/v1` EndpointSlices carrying the Service label because slices have no predictable one-to-one name mapping. Slices are separated by address family and port set and split beyond 100 endpoints; producers must set `addressType`, use one address per endpoint, and represent readiness with endpoint conditions.

```console
kubectl get endpointslice -l kubernetes.io/service-name=myservice
```

## Warnings are part of the migration result (ingress-migration)

The tool reports unsupported and approximate conversions alongside the generated manifests. For example, `configuration-snippet` is unsupported, `proxy-body-size` has no Standard Gateway API equivalent, and URL-normalization behavior must be checked against the selected Gateway implementation.

## XBackendTrafficPolicy sets retry budgets (gateway-api-updates)

Experimental `XBackendTrafficPolicy`, which replaces the experimental `BackendLBPolicy`, can cap retries as a percentage of active requests over an interval while allowing a minimum retry rate.

```yaml
spec:
  retryConstraint:
    budget:
      percent: 20
      interval: 10s
    minRetryRate:
      count: 3
      interval: 1s
```

## XListenerSet delegates and merges Gateway listeners (gateway-api-updates)

Experimental `XListenerSet` objects attach listener lists to a parent Gateway, allowing delegated TLS configuration and more than the former 64-listener ceiling. `Gateway.spec.allowedListeners` admits sets from `Same`, `All`, `None`, or selector-chosen namespaces; merged listeners undergo the same compatibility checks as direct listeners, with direct listeners ordered first and the rest ordered by creation time then namespace/name.

```yaml
apiVersion: gateway.networking.x-k8s.io/v1alpha1
kind: XListenerSet
metadata:
  name: app-listeners
spec:
  parentRef:
    name: edge
  listeners:
  - name: app-https
    hostname: app.example.com
    protocol: HTTPS
    port: 443
```

## XMesh exposes mesh-wide ownership and capabilities (gateway-api-updates)

The cluster-scoped experimental `gateway.networking.x-k8s.io/v1alpha1` `XMesh` resource identifies its implementation with `spec.controllerName`; status reports acceptance and supported mesh features. Implementations are expected to create a default matching XMesh at startup when one does not already exist.

```yaml
apiVersion: gateway.networking.x-k8s.io/v1alpha1
kind: XMesh
metadata:
  name: default-mesh
spec:
  controllerName: mesh.example.com/controller
```


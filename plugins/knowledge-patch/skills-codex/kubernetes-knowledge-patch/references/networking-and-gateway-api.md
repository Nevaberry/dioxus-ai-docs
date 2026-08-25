# Networking, Services, and Gateway API

## Services and EndpointSlices

### The Endpoints API is deprecated (1.33-guide)

Reads and writes of core v1 Endpoints warn. Consumers must list all
`discovery.k8s.io/v1` EndpointSlices labeled for the Service; names have no
one-to-one mapping. Slices split by address family, port set, and above 100
endpoints. Producers set `addressType`, use one address per endpoint, and express
readiness through endpoint conditions.

```console
kubectl get endpointslice -l kubernetes.io/service-name=myservice
```

### Service topology preferences move to `trafficDistribution` (1.33.0)

EndpointSlice hints and `trafficDistribution: PreferClose` are stable;
`service.kubernetes.io/topology-mode` is deprecated. With the applicable
feature, use `PreferSameNode`; `PreferSameZone` aliases `PreferClose`.

### `PreferClose` is deprecated (1.34-guide)

Use `PreferSameZone` or `PreferSameNode`; both are beta and default-on.

### Service CIDRs are managed through a stable API (1.33.0)

`ServiceCIDR` objects represent additional Service ranges. Enforce single,
restricted, or non-overlapping ranges separately, for example with a
ValidatingAdmissionPolicy.

### Built-in IP fields can use strict parsing (1.33.0)

`StrictIPCIDRValidation` rejects IPv4 leading zeroes and mapped IPv6 such as
`::ffff:192.168.0.1`; with the gate off, the API server warns. This does not
cover CRDs, component config, or flags.

### Controllers canonicalize IP and CIDR fields (1.36-guide)

With strict validation beta, controllers canonicalize written IP values and
warn about malformed values already stored.

### Network API validation changes in both directions (1.36.0)

Default-on strict validation rejects ambiguous CIDRs such as
`192.168.0.5/24`; use the network address or `/32`. Default-on beta
`RelaxedServiceNameValidation` uses DNS-label rules and permits Service names
beginning with a digit.

### Service `externalIPs` is deprecated (1.36-guide)

`Service.spec.externalIPs` warns from 1.36 and is planned for removal in 1.43.
Choose LoadBalancer, NodePort, or Gateway API exposure instead.

## Proxies and Windows networking

### Kube-proxy nftables mode is stable (1.33.0)

The GA nftables proxier is not default. Select `--proxy-mode=nftables` or
`mode: nftables`. Its kernel-version check is skipped only when
`KUBE_PROXY_NFTABLES_SKIP_KERNEL_VERSION_CHECK` is non-empty.

### Node kube-proxy version status is removed (1.33-guide)

The inaccurate `.status.nodeInfo.kubeProxyVersion` field no longer exists.

### kube-proxy IPVS mode is deprecated (1.35-guide)

IPVS still works but warns at startup; migrate Linux nodes to nftables.

### Windows Pods no longer support `hostNetwork` (1.33-guide)

The alpha Windows implementation is removed. Windows HostProcess containers
remain the option for host networking plus host-level access.

### Windows nodes gain lifecycle and networking graduations (1.34-guide)

Windows graceful shutdown is beta and default-on, honoring hooks and grace
periods after a pre-shutdown notification. Windows kube-proxy DSR and overlay
networking are stable.

## Gateway API routing and policy

### Request mirroring can select a percentage (gateway-api-updates)

Gateway API v1.3 Standard `RequestMirror` supports integer `percent` or a
`fraction`, rather than mirroring every request.

```yaml
filters:
- type: RequestMirror
  requestMirror:
    backendRef: {name: foo-v2, port: 8080}
    fraction: {numerator: 5, denominator: 1000}
```

### BackendTLSPolicy standardizes upstream TLS (gateway-api-updates)

The v1.4 Standard `BackendTLSPolicy` controls Gateway-to-backend TLS. `hostname`
drives SNI and, without `subjectAltNames`, identity verification. Trust comes
from at most eight `caCertificateRefs` bundles or
`wellKnownCACertificates: System`. If SANs are supplied, the hostname must also
be among them to remain an authenticated identity.

### GatewayClass status advertises supported features (gateway-api-updates)

`GatewayClass.status.supportedFeatures` declares capabilities for tooling and
conformance selection. Populate it before, or atomically with, accepting the
class.

### Route rules can be named and targeted (gateway-api-updates)

All route rule types have an optional validated `name`, enabling rule-specific
status, observability, tooling, and policy attachment through
`targetRefs[].sectionName`. Implementations do not default it and may make it
immutable.

### Routes can bind to default Gateways (gateway-api-updates)

Experimental Routes set `spec.useDefaultGateways: All`; operators opt Gateways
in with `spec.defaultScope: All`. Bindings appear only in `status.parents`, not
`parentRefs`, and each Route binds to every matching default Gateway.

### Client-certificate policy is scoped to a Gateway port (gateway-api-updates)

Gateway v1.4 uses `Gateway.spec.tls.default` across HTTPS listeners and
`Gateway.spec.tls.perPort` overrides. Do not scope validation by hostname:
connection coalescing can reuse a connection without another certificate check.

### GRPCRoute now requires `spec` (gateway-api-updates)

The Standard CRD rejects objects without top-level `.spec`; emit `spec: {}` if
empty.

## Experimental Gateway identities and filters

### New experimental kinds have distinct API identities (gateway-api-updates)

Starting in v1.3, new Experimental kinds use an `X` prefix and
`gateway.networking.x-k8s.io`. They can coexist with Standard objects; graduation
requires recreation under the non-`X`, non-`x-k8s` identity.

### HTTPRoute gains an experimental CORS filter (gateway-api-updates)

The filter supports `allowOrigins`, `allowMethods`, `allowHeaders`,
`allowCredentials`, `exposeHeaders`, and `maxAge`. In v1.4,
`allowCredentials` is strictly Boolean.

### HTTPRoute can call an external authorization service (gateway-api-updates)

Experimental `ExternalAuth` calls HTTP or gRPC auth and controls forwarded
headers; HTTP mode may set a path prefix. HTTP `200` allows and may add headers;
`403` denies.

### XListenerSet delegates and merges Gateway listeners (gateway-api-updates)

`XListenerSet` attaches listener lists to a parent Gateway for delegated TLS and
more than 64 listeners. `Gateway.spec.allowedListeners` admits sets from `Same`,
`All`, `None`, or selected namespaces. Compatibility checks match direct
listeners; direct listeners order first, then sets by creation time and
namespace/name.

```yaml
apiVersion: gateway.networking.x-k8s.io/v1alpha1
kind: XListenerSet
spec:
  parentRef: {name: edge}
  listeners:
  - {name: app-https, hostname: app.example.com, protocol: HTTPS, port: 443}
```

### XBackendTrafficPolicy sets retry budgets (gateway-api-updates)

The experimental replacement for `BackendLBPolicy` caps retries as a percentage
of active requests over an interval while allowing a minimum retry rate.

```yaml
spec:
  retryConstraint:
    budget: {percent: 20, interval: 10s}
    minRetryRate: {count: 3, interval: 1s}
```

### XMesh exposes mesh-wide ownership and capabilities (gateway-api-updates)

Cluster-scoped `gateway.networking.x-k8s.io/v1alpha1` `XMesh` identifies its
implementation through `spec.controllerName`; status reports acceptance and
features. An implementation is expected to create a matching default XMesh at
startup when absent.

## Ingress migration

### Ingress NGINX is retiring (1.35-guide)

Best-effort project maintenance was announced only through March 2026, followed
by archival without further updates. Plan a Gateway API migration.

### Ingress2Gateway 1.0 reads files or live cluster state (ingress-migration)

`ingress2gateway print` translates Ingress and provider settings from
comma-separated files, one namespace, or all namespaces.

```console
go install github.com/kubernetes-sigs/ingress2gateway@v1.0.0
ingress2gateway print --input-file ingress.yaml,other.yaml --providers=ingress-nginx > gwapi.yaml
ingress2gateway print --namespace my-api --providers=ingress-nginx > gwapi.yaml
ingress2gateway print --providers=ingress-nginx --all-namespaces > gwapi.yaml
```

### Ingress-NGINX translation covers many more annotations (ingress-migration)

Version 1.0 covers more than 30 annotations including CORS, backend TLS, regex
matching, and rewrites. `--emitter agentgateway`, `envoy-gateway`, or `kgateway`
may add implementation extensions when Standard Gateway API cannot represent a
setting.

### Warnings are part of the migration result (ingress-migration)

Review unsupported and approximate results. `configuration-snippet` is
unsupported, `proxy-body-size` lacks a Standard equivalent, and URL
normalization depends on the selected implementation.

### Some generated routes intentionally approximate Ingress-NGINX (ingress-migration)

Regex paths become case-insensitive prefix expressions such as
`(?i)/users/(\d+).*`; TCP `proxy-read-timeout` and `proxy-send-timeout` map
best-effort to an HTTPRoute request timeout. Default redirect reproduction may
add an HTTP listener and separate redirecting HTTPRoute. Review all of these
before applying output.

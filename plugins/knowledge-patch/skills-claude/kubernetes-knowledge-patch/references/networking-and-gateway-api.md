# Networking, Services, and Gateway API

Use this reference for Service discovery, traffic locality, IP validation,
kube-proxy, Gateway API policy, and Ingress migration.

## Service discovery and EndpointSlices

### Replace Endpoints consumers (1.33-guide)

Core `v1` Endpoints is deprecated and produces warnings. List every
`discovery.k8s.io/v1` EndpointSlice labeled for the Service; slices have no
predictable one-to-one name mapping, separate address families and port sets,
and split after 100 endpoints.

```console
kubectl get endpointslice -l kubernetes.io/service-name=myservice
```

Producers must set `addressType`, store one address per endpoint, and represent
readiness through endpoint conditions.

Aggregated APIService backends are also resolved through EndpointSlices, so
manual backend publishers must create them (1.34.0).

### Use managed Service CIDRs (1.33.0)

The stable `MultiCIDRServiceAllocator` represents additional Service ranges as
`ServiceCIDR` objects. Kubernetes does not itself enforce a single range,
restricted ranges, or non-overlap with every external network; add admission
policy where those constraints matter.

## Traffic locality and proxy modes

### Use `trafficDistribution` (1.33.0, 1.34-guide)

Replace `service.kubernetes.io/topology-mode`. Use `PreferSameNode` for node
locality or `PreferSameZone` for zone locality. `PreferClose` is deprecated;
`PreferSameZone` is its clearer alias. EndpointSlice hints and the supported
Service field drive the behavior. The earlier rollout used the
`PreferSameTrafficDistribution` gate; the clearer values are beta and enabled
by default.

```yaml
spec:
  trafficDistribution: PreferSameNode
```

### Prefer nftables over IPVS (1.33.0, 1.35-guide)

The nftables proxier is stable but must be selected with
`--proxy-mode=nftables` or `mode: nftables`. Its kernel check is skipped only
when `KUBE_PROXY_NFTABLES_SKIP_KERNEL_VERSION_CHECK` is non-empty. IPVS still
works through `ipvs` mode but is deprecated and warns at startup.

The inaccurate Node `.status.nodeInfo.kubeProxyVersion` field was removed
(1.33-guide).

### Account for Windows networking (1.33-guide, 1.34-guide)

Windows Pods cannot use the removed alpha `hostNetwork` implementation;
HostProcess containers remain available for host-level access. Windows
kube-proxy Direct Service Return and overlay-network support are stable.

## IP, CIDR, DNS, and Service-name validation

### Validate built-in IP fields strictly (1.33.0, 1.36-guide)

`StrictIPCIDRValidation` rejects IPv4 octets with leading zeroes and
IPv4-mapped IPv6 such as `::ffff:192.168.0.1`; before beta enforcement, the API
server could warn instead. Controllers now canonicalize IPs they write and warn
about malformed values already stored. This behavior does not cover CRD,
component-config, or command-line parsing.

### Use canonical CIDRs and relaxed Service names (1.36.0)

Default-on strict validation rejects host-bit CIDRs such as
`192.168.0.5/24`; use `192.168.0.0/24` or `/32`. Default-on beta
`RelaxedServiceNameValidation` applies DNS-label rules, allowing Service names
to begin with a digit.

### Accept the relaxed Pod DNS search forms (1.33.0)

Beta `RelaxedDNSSearchValidation` permits a Pod search domain that is a single
dot or contains an underscore.

## Service exposure migration

### Replace `externalIPs` (1.36-guide)

`Service.spec.externalIPs` is deprecated, warns from 1.36, and is planned for
removal in 1.43. Use LoadBalancer, NodePort, or Gateway API exposure according
to the network design.

## Gateway API channels and identities

### Treat Experimental kinds as separate resources

From Gateway API v1.3, new Experimental kinds use an `X` prefix and the
`gateway.networking.x-k8s.io` API group. They may coexist with Standard
resources. Graduation requires recreation under the non-`X` kind and stable
group; it is not an in-place API-version conversion.

### Mirror a fraction of requests

Standard v1.3 `RequestMirror` accepts either integer `percent` or a `fraction`:

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

### Configure experimental CORS

The HTTPRoute `CORS` filter supports `allowOrigins`, `allowMethods`,
`allowHeaders`, `allowCredentials`, `exposeHeaders`, and `maxAge`. Gateway v1.4
requires `allowCredentials` to be Boolean; reject older non-Boolean forms.

### Delegate listeners with XListenerSet

An experimental `gateway.networking.x-k8s.io/v1alpha1` `XListenerSet` attaches
listeners to a parent Gateway, supports delegated TLS, and exceeds the former
64-listener ceiling. `Gateway.spec.allowedListeners` admits `Same`, `All`,
`None`, or namespace-selector matches. Direct listeners sort first; compatible
delegated listeners then sort by creation time and namespace/name.

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

### Set retry budgets with XBackendTrafficPolicy

Experimental `XBackendTrafficPolicy` replaces `BackendLBPolicy`. It can cap
retries as a percentage of active requests over an interval while retaining a
minimum retry rate.

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

### Secure upstreams with BackendTLSPolicy

Gateway v1.4 Standard `BackendTLSPolicy` controls TLS from Gateway to backend.
`hostname` drives SNI and, absent `subjectAltNames`, identity verification.
Trust comes from at most eight `caCertificateRefs` bundles or
`wellKnownCACertificates: System`. If SANs are supplied, the hostname must also
appear there to remain an authenticated identity.

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

### Advertise implementation features

Standard `GatewayClass.status.supportedFeatures` tells users, tools, and
conformance selection what an implementation supports. Populate it before, or
atomically with, accepting the GatewayClass.

### Name and target route rules

Every route rule type has an optional validated `name` for rule-level status,
telemetry, tooling, and policy attachment through
`targetRefs[].sectionName`. Implementations do not default it and may make it
immutable.

### Call an external authorization service

Experimental HTTPRoute `ExternalAuth` calls an HTTP or gRPC backend and limits
the headers it receives. HTTP mode can add a path prefix; status 200 allows and
may forward headers, while 403 denies.

### Declare mesh ownership with XMesh

The cluster-scoped experimental
`gateway.networking.x-k8s.io/v1alpha1` `XMesh` names its implementation through
`spec.controllerName`; status reports acceptance and supported mesh features.
An implementation should create its default matching XMesh at startup if none
exists.

### Bind Routes to default Gateways

Experimental defaulting pairs Route `spec.useDefaultGateways: All` with
Gateway `spec.defaultScope: All`. A Route binds to every match. Bindings appear
only in `status.parents`; the controller does not inject `parentRefs`.

### Scope client certificates by port

Gateway v1.4 adds `Gateway.spec.tls.default` plus
`Gateway.spec.tls.perPort` overrides for client-certificate validation. Do not
vary validation by hostname on the same port: HTTP connection coalescing can
reuse a connection without another certificate check.

### Always include GRPCRoute spec

The Standard GRPCRoute CRD rejects an object without top-level `.spec`. Emit at
least:

```yaml
spec: {}
```

## Ingress NGINX migration

### Plan migration to Gateway API (1.35-guide)

The Kubernetes project announced best-effort Ingress NGINX maintenance only
through March 2026, followed by archival without further updates. Treat
migration as required operational work.

### Run ingress2gateway 1.0

`ingress2gateway print` translates manifests or live cluster state. It accepts
comma-separated input files, one namespace, or every namespace:

```console
go install github.com/kubernetes-sigs/ingress2gateway@v1.0.0
ingress2gateway print --input-file ingress.yaml,other.yaml --providers=ingress-nginx > gwapi.yaml
ingress2gateway print --namespace my-api --providers=ingress-nginx > gwapi.yaml
ingress2gateway print --providers=ingress-nginx --all-namespaces > gwapi.yaml
```

Version 1.0 handles more than 30 common annotations, including CORS, backend
TLS, regex matching, and rewrites. `--emitter agentgateway`,
`--emitter envoy-gateway`, and `--emitter kgateway` can emit implementation
extensions when Standard Gateway API is insufficient.

### Treat warnings as migration output

Review unsupported and approximate conversions with the YAML.
`configuration-snippet` is unsupported, `proxy-body-size` lacks a Standard
equivalent, and URL normalization depends on the implementation.

Ingress-NGINX regex paths become case-insensitive prefix expressions such as
`(?i)/users/(\d+).*`. TCP `proxy-read-timeout` and `proxy-send-timeout` map only
approximately to an HTTPRoute request timeout. Reproducing default redirects
may create an HTTP listener plus a separate redirecting HTTPRoute. Review all
such output before applying it.

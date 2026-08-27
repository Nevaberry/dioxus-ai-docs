# Traffic, Routing, and Gateways

Use this reference for service discovery, load balancing, retries, DNS-backed
routing, Gateway API resources, and Envoy configuration.

## Contents

- [Service discovery and address allocation](#service-discovery-and-address-allocation)
- [Endpoint selection and traffic distribution](#endpoint-selection-and-traffic-distribution)
- [DestinationRule, retry, and connection behavior](#destinationrule-retry-and-connection-behavior)
- [Traffic manipulation and Envoy configuration](#traffic-manipulation-and-envoy-configuration)
- [Waypoint and Gateway selection](#waypoint-and-gateway-selection)
- [Gateway API enablement and generated resources](#gateway-api-enablement-and-generated-resources)

## Service discovery and address allocation

### Status-based ServiceEntry IP auto-allocation (1.25.0)

`PILOT_ENABLE_IP_AUTOALLOCATE` defaults to `true`. A `ServiceEntry` without
`spec.address` receives allocated addresses in `status.addresses`; proxies use
them only when DNS proxying is configured.
`ISTIO_META_DNS_AUTO_ALLOCATE` in `proxyMetadata` is deprecated in favor of this
status-based controller.

### DNS proxy upstream selection and resolver controls (1.25.0)

DNS proxying randomly selects an upstream resolver.
`PILOT_DNS_JITTER_DURATION` configures periodic-resolution jitter.
`PILOT_DNS_CARES_UDP_MAX_QUERIES` controls the Cares resolver's
`udp_max_queries` and defaults to `100`.

### Configurable auto-allocated VIP ranges (1.27.0)

Set `PILOT_IP_AUTOALLOCATE_IPV4_PREFIX` and
`PILOT_IP_AUTOALLOCATE_IPV6_PREFIX` on Pilot to select the CIDR prefixes used by
the `ipallocate` controller.

### DNS-backed connection controls (1.30.0)

Set `istio.io/connect-strategy: RACE_FIRST_TCP_CONNECT` on a `ServiceEntry` to
try multiple DNS A-record endpoints and use the first successful TCP
connection. DNS clusters also support failover priority.
`DNS_FORWARD_TIMEOUT` changes the proxy DNS upstream timeout from its `5s`
default and can be set in `istio-proxy` or mesh-wide through `proxyMetadata`.

### Sidecar wildcard DYNAMIC_DNS routing (1.30.0)

Sidecars support wildcard `ServiceEntry` hosts with
`resolution: DYNAMIC_DNS` for `MESH_INTERNAL` and `MESH_EXTERNAL`, including
HTTP Host-based and TLS SNI-based routing. Treat clients as trusted because a
client can spoof SNI within the wildcard.

### Wildcard DYNAMIC_DNS hosts for TLS (1.29.0)

Wildcard `ServiceEntry` hosts with `DYNAMIC_DNS` resolution can route TLS by SNI
without termination. This alpha behavior is off by default; enable it with
`ENABLE_WILDCARD_HOST_SERVICE_ENTRIES_FOR_TLS=true` only for trusted clients
because spoofed SNI can select a route.

## Endpoint selection and traffic distribution

### Terminating endpoints excluded from unhealthy endpoint discovery (1.25.0)

When the off-by-default `PILOT_SEND_UNHEALTHY_ENDPOINTS` feature is enabled, it
does not include terminating endpoints. This prevents scale-down and rollout
events from making a service appear unhealthy.

### Traffic distribution across all data planes (1.25.0)

Istio honors `Service.spec.trafficDistribution` and the
`networking.istio.io/traffic-distribution` annotation across all data planes,
rather than only in ztunnel, to prefer geographically close endpoints.

### Expanded Kubernetes Service traffic distribution (1.27.0)

Istio honors `PreferSameNode` and `PreferSameZone` in
`Service.spec.trafficDistribution`. For `PreferClose`, distribution disregards
subzone when selecting nearby endpoints.

### Locality label precedence (1.29.0)

Istio recognizes `topology.istio.io/locality`; when both locality labels are
present, it takes precedence over `istio-locality`.

### Namespace-level traffic distribution (1.30.0)

Set `networking.istio.io/traffic-distribution` on a namespace. A Service
inherits it unless it has its own traffic-distribution setting.

### Sidecar service-namespace selection (upgrade-1.30)

For a hostname visible in multiple namespaces, sidecar configuration prefers a
Kubernetes `Service`, then the oldest non-Kubernetes service by creation time,
instead of selecting the first visible namespace alphabetically. Mixed service
types may route differently. Set
`PILOT_SIDECAR_PICK_BEST_SERVICE_NAMESPACE=false` or use
`compatibilityVersion` 1.28 or earlier to restore the prior selection.

## DestinationRule, retry, and connection behavior

### ConfigMap CA references for DestinationRule TLS (1.26.0)

A `DestinationRule` using `SIMPLE` TLS can reference a `ConfigMap` as well as a
`Secret`, allowing a CA-only certificate reference without placing it in a
Secret.

### Retry API host predicates and backoff (1.26.0)

The Retry API supports the `retry_ignore_previous_hosts` host predicate and
configurable retry backoff intervals.

### DestinationRule retry budgets (1.27.0)

`DestinationRule` resources support retry budgets.

### HTTP/2 upgrade connection pools (1.28.0)

HTTP/2 connection-pool settings are applied when HTTP/2 upgrades are enabled;
they were previously ignored.

### Proxyless gRPC traffic controls (1.29.0)

Proxyless gRPC clients support `LEAST_REQUEST` load balancing and circuit
breaking through `http2MaxRequests`.

### Correct DestinationRule retry budgets (1.30.0)

The default `retryBudget.percent` is the intended 20%, not 0.2%. Retry budgets
at top-level and subset `trafficPolicy` scope are preserved when subsets define
their own traffic policy.

### Sidecar socket-event connection limit (1.28.0)

Inbound and outbound sidecar listeners that explicitly bind ports accept at
most one connection per socket event by default. Set
`MAX_CONNECTIONS_PER_SOCKET_EVENT_LOOP=0` to restore the old behavior.

### Global downstream connection limit metadata (1.29.0)

Set proxy metadata `ISTIO_META_GLOBAL_DOWNSTREAM_MAX_CONNECTIONS` to configure
Envoy's global downstream connection limit. It takes precedence over the
deprecated `overload.global_downstream_max_connections` runtime flag, which is
still supported but emits warnings.

## Traffic manipulation and Envoy configuration

### Virtual-interface traffic rerouting (1.25.0)

`traffic.sidecar.istio.io/kubevirtInterfaces` is deprecated. Replace it with
`istio.io/reroute-virtual-interfaces`, whose value is a comma-separated list of
virtual interfaces for which inbound traffic is unconditionally treated as
outbound in sidecar and ambient modes.

### EnvoyFilter virtual-host domain matching (1.26.0)

An `EnvoyFilter` can match an Envoy `VirtualHost` by domain name.

### LISTENER_FILTER merge patches (1.27.0)

An `EnvoyFilter` patch targeting `LISTENER_FILTER` can use `MERGE`.

### Consistent-hash cookie attributes (1.28.0)

Cookie-based consistent-hash load balancing can set attributes including
`SameSite`, `Secure`, and `HttpOnly`.

### Mirrored-request shadow host suffix (1.28.0)

`DISABLE_SHADOW_HOST_SUFFIX` controls whether mirrored-request hostnames receive
a shadow suffix. Despite the variable name, `true` is the default and adds the
suffix; set it to `false` to omit the suffix.

### X-Forwarded proxy headers (1.28.0)

`ProxyConfig.ProxyHeaders` can configure `X-Forwarded` headers.

### First-class Lua TrafficExtension API (1.30.0)

The extensions package includes a `TrafficExtension` API for first-class Lua
extensibility.

## Waypoint and Gateway selection

### Waypoint policy defaults through GatewayClass (1.25.0)

Policy defaults for `istio-waypoint` can be attached by targeting its
`GatewayClass`.

### Namespace-level ingress waypoint selection (1.25.0)

Configure the `istio.io/ingress-use-waypoint` label on a namespace.

## Gateway API enablement and generated resources

### Experimental Gateway API backend policies (1.26.0)

Istio has initial support for experimental `BackendTLSPolicy` and
`XBackendTrafficPolicy`. They are disabled by default; enable both with
`PILOT_ENABLE_ALPHA_GATEWAY_API=true`.

### Customizable automated Gateway API deployments (1.26.0)

Automated deployments for ingress, egress, and waypoint `Gateway` resources can
customize the generated `Service`, `Deployment`, `ServiceAccount`,
`HorizontalPodAutoscaler`, and `PodDisruptionBudget`.

### Existing gateway deployment attachment control (1.26.0)

`ENABLE_GATEWAY_API_MANUAL_DEPLOYMENT` controls whether istiod automatically
attaches Gateway API resources to existing gateway deployments. It defaults to
`true`; set it to `false` to disable attachment.

### Gateway API metadata propagation control (1.27.0)

Resources generated for a Gateway API `Gateway` inherit the parent resource's
labels and annotations by default. The enabled-by-default
`EnableGatewayAPICopyLabelsAnnotations` flag controls propagation.

### Gateway API Inference Extension (1.27.0)

Gateway API Inference Extension support is available but disabled by default.
Enable it with `SUPPORT_GATEWAY_API_INFERENCE_EXTENSION`.

### Port-specific BackendTLSPolicy (1.28.0)

A Gateway API `BackendTLSPolicy` can use `sectionName` to target a named
`Service` port, allowing different TLS settings per port.

### BackendTLSPolicy for ServiceEntry (1.28.0)

`BackendTLSPolicy.targetRef` can select a `ServiceEntry`, applying TLS settings
to represented external services.

### Experimental agentgateway support (1.30.0)

Enable experimental agentgateway configuration through Gateway API resources
with `PILOT_ENABLE_AGENTGATEWAY`.

### TLSRoute termination and GA TLS listeners (1.30.0)

Gateway API `TLSRoute` supports termination and mixed mode. `protocol: TLS`
listeners used for TLS passthrough are accepted by default without
`PILOT_ENABLE_ALPHA_GATEWAY_API=true`, following `TLSRoute` graduation in
Gateway API v1.5.0.

### Gateway transport-socket connection timeout (1.30.0)

`PILOT_GATEWAY_TRANSPORT_SOCKET_CONNECT_TIMEOUT` configures the transport-socket
connection timeout on gateway listeners. It defaults to `15s`; set it to `0s`
to disable the timeout for longer TLS handshakes.

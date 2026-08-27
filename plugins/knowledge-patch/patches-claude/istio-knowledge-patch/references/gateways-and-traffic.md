# Gateways, service discovery, and traffic policy

Use this reference for Gateway API resources, Istio routing APIs, ServiceEntry
behavior, and Envoy traffic controls. Check both the API version and the feature
gate before using an experimental resource.

## Gateway API enablement and attachment

- (`1.26.0`) Initial experimental `BackendTLSPolicy` and
  `XBackendTrafficPolicy` support is disabled by default; enable both with
  `PILOT_ENABLE_ALPHA_GATEWAY_API=true`.
- (`1.26.0`) `ENABLE_GATEWAY_API_MANUAL_DEPLOYMENT` controls whether istiod
  attaches Gateway API resources to existing gateway Deployments. It defaults
  to `true`; set it to `false` to disable attachment.
- (`1.27.0`) Gateway API Inference Extension support is off by default. Enable
  it with `SUPPORT_GATEWAY_API_INFERENCE_EXTENSION`.
- (`upgrade-1.28`) Only `BackendTLSPolicy` v1 is accepted; v1alpha3 is removed,
  and the stable API no longer needs `PILOT_ENABLE_ALPHA_GATEWAY_API=true`.
- (`upgrade-1.30`) Install Gateway API v1.5.x CRDs before upgrading Istio so
  `TLSRoute` and `ReferenceGrant` in `gateway.networking.k8s.io/v1` are visible.
- (`1.30.0`) `protocol: TLS` listeners for passthrough are accepted without
  `PILOT_ENABLE_ALPHA_GATEWAY_API=true`, and `TLSRoute` supports termination and
  mixed mode following its v1.5 graduation.
- (`1.30.0`) Enable experimental agentgateway configuration through Gateway API
  with `PILOT_ENABLE_AGENTGATEWAY`.

## Generated Gateway workloads

- (`1.26.0`) Automated ingress, egress, and waypoint Gateway deployments can
  customize the generated `Service`, `Deployment`, `ServiceAccount`,
  `HorizontalPodAutoscaler`, and `PodDisruptionBudget`.
- (`1.26.0`) `replicaCount=0` in the `istio/gateway` chart is rendered as
  `replicas: 0`.
- (`1.27.0`) Generated Gateway resources inherit their parent Gateway's labels
  and annotations by default. Enabled-by-default
  `EnableGatewayAPICopyLabelsAnnotations` controls propagation.
- (`1.30.0`) `networkGatewayPorts` values override network gateway Service
  ports.

## Backend and frontend TLS policies

- (`1.28.0`) `BackendTLSPolicy.sectionName` targets a named Service port, so
  each port can have different TLS settings.
- (`1.28.0`) `BackendTLSPolicy.targetRef` can select a `ServiceEntry` for
  external-service TLS configuration.
- (`1.28.0`) Gateway API `FrontendTLSValidation` from GEP-91 is supported.
- (`1.26.0`) A `DestinationRule` using `SIMPLE` TLS may reference a `ConfigMap`
  as well as a `Secret`, allowing a CA-only reference outside a Secret.
- (`1.28.0`) `ServerTLSSettings.caCertCredentialName` may reference a `Secret`
  or `ConfigMap` holding the CA certificates for gateway mutual TLS.
- (`upgrade-1.27`) Istio and Kubernetes Gateway resources may configure
  multiple certificate types, such as RSA and ECDSA, so clients select a type
  they support.
- (`1.29.0`) Set `gateway.istio.io/tls-cipher-suites` on a Gateway to a
  comma-separated custom cipher-suite list.
- (`1.30.0`) `PILOT_GATEWAY_TRANSPORT_SOCKET_CONNECT_TIMEOUT` controls the
  transport-socket connection timeout on gateway listeners. It defaults to
  `15s`; `0s` disables it for long TLS handshakes.

## Waypoints and ingress selection

- (`1.25.0`) Policy defaults can target the `istio-waypoint` `GatewayClass`.
- (`1.25.0`) Configure `istio.io/ingress-use-waypoint` on a namespace.
- (`1.26.0`) Waypoints process Gateway API `TCPRoute`.
- (`1.28.0`) Ambient waypoints route to remote networks.
- (`1.29.0`) Ambient multicluster ingress to exposed remote backends is opt-in
  with `AMBIENT_ENABLE_MULTI_NETWORK_INGRESS=true`.
- (`1.30.0`) With `AMBIENT_ENABLE_MULTI_NETWORK`, east-west gateways expose
  non-HBONE TLS passthrough ports using Gateway API resources.

## ServiceEntry addressing and DNS routing

- (`1.25.0`) `PILOT_ENABLE_IP_AUTOALLOCATE` defaults to `true`. An addressless
  `ServiceEntry` receives values in `status.addresses`, consumed by proxies only
  when DNS proxying is configured.
- (`1.27.0`) `PILOT_IP_AUTOALLOCATE_IPV4_PREFIX` and
  `PILOT_IP_AUTOALLOCATE_IPV6_PREFIX` choose the allocation controller's CIDRs.
- (`1.25.0`) Ambient DNS proxying resolves Kubernetes `ExternalName` Services.
- (`1.28.0`) Wildcard `DYNAMIC_DNS` hosts initially require ambient mode, an
  egress waypoint, and HTTP.
- (`1.29.0`) Enable alpha TLS-by-SNI routing for wildcard `DYNAMIC_DNS` hosts
  with `ENABLE_WILDCARD_HOST_SERVICE_ENTRIES_FOR_TLS=true`. It is off by
  default and should be restricted to trusted clients that cannot misuse SNI.
- (`1.30.0`) Sidecars support wildcard `DYNAMIC_DNS` ServiceEntries for both
  `MESH_INTERNAL` and `MESH_EXTERNAL`, with HTTP Host and TLS SNI routing. Treat
  clients as trusted because they select routes through those values.
- (`1.30.0`) Ambient ServiceEntry addresses may be CIDRs; ztunnel uses
  longest-prefix-match routing.
- (`1.30.0`) Set `istio.io/connect-strategy: RACE_FIRST_TCP_CONNECT` on a
  ServiceEntry to try multiple DNS A-record endpoints and use the first TCP
  connection that succeeds. DNS clusters also support failover priority.
- (`1.30.0`) `DNS_FORWARD_TIMEOUT` changes the proxy DNS upstream timeout from
  the `5s` default. Set it in `istio-proxy` or mesh-wide through
  `proxyMetadata`.

## Service selection and locality

- (`1.25.0`) `Service.spec.trafficDistribution` and
  `networking.istio.io/traffic-distribution` apply across every data plane.
- (`1.27.0`) Traffic distribution supports `PreferSameNode` and
  `PreferSameZone`; `PreferClose` disregards subzone.
- (`1.29.0`) `topology.istio.io/locality` is recognized and takes precedence
  over `istio-locality` when both labels exist.
- (`1.30.0`) A namespace-level
  `networking.istio.io/traffic-distribution` annotation is inherited by a
  Service unless the Service specifies its own setting.
- (`upgrade-1.30`) When multiple namespaces expose one hostname, sidecars now
  prefer a Kubernetes Service, then the oldest non-Kubernetes service. To
  temporarily restore alphabetical namespace selection, set
  `PILOT_SIDECAR_PICK_BEST_SERVICE_NAMESPACE=false` or use
  `compatibilityVersion` 1.28 or earlier.
- (`1.29.0`) ztunnel's canonical WDS service for hostname resolution is a
  Kubernetes Service or the oldest ServiceEntry for that hostname, unless a
  Service in the client's namespace overrides it.

## Retries, connection pools, and limits

- (`1.26.0`) Retry policy supports the `retry_ignore_previous_hosts` host
  predicate and configurable retry backoff intervals.
- (`1.27.0`) `DestinationRule` supports retry budgets.
- (`1.30.0`) The default `retryBudget.percent` is correctly 20%, not 0.2%.
  Retry budgets at top-level and subset `trafficPolicy` scope survive when a
  subset declares its own traffic policy.
- (`1.28.0`) HTTP/2 connection-pool settings apply when HTTP/2 upgrade is
  enabled; they were previously ignored.
- (`1.29.0`) Proxyless gRPC supports `LEAST_REQUEST` load balancing and circuit
  breaking through `http2MaxRequests`.
- (`1.28.0`) Explicitly bound inbound and outbound sidecar listeners accept at
  most one connection per socket event by default. Set
  `MAX_CONNECTIONS_PER_SOCKET_EVENT_LOOP=0` for the old behavior.
- (`1.29.0`) Configure Envoy's global downstream connection limit with
  `ISTIO_META_GLOBAL_DOWNSTREAM_MAX_CONNECTIONS` proxy metadata. It takes
  precedence over deprecated runtime flag
  `overload.global_downstream_max_connections`, which still works with a
  warning.

## Load balancing, mirroring, and headers

- (`1.28.0`) Consistent-hash cookies support `SameSite`, `Secure`, and
  `HttpOnly` attributes.
- (`1.28.0`) `DISABLE_SHADOW_HOST_SUFFIX=true` is the default and, despite its
  name, adds the suffix to mirrored-request hosts. Set it to `false` to omit the
  suffix.
- (`1.28.0`) `ProxyConfig.ProxyHeaders` configures `X-Forwarded` headers.
- (`1.25.0`) When off-by-default `PILOT_SEND_UNHEALTHY_ENDPOINTS` is enabled,
  terminating endpoints are excluded, preventing rollout or scale-down from
  making a Service appear unhealthy.
- (`1.28.0`) ztunnel applies `WorkloadEntry` port maps when the Service port is
  referenced by name.

## Envoy and extension APIs

- (`1.26.0`) `EnvoyFilter` can match an Envoy `VirtualHost` by domain name.
- (`1.27.0`) An `EnvoyFilter` patch targeting `LISTENER_FILTER` supports the
  `MERGE` operation.
- (`1.30.0`) The extensions package includes a first-class `TrafficExtension`
  API for Lua extensibility.


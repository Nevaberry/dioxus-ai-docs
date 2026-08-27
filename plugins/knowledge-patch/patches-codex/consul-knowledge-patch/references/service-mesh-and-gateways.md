# Service Mesh and Gateways

## Envoy compatibility

### Bundled Envoy and CA-dependent TLS sockets

Consul 1.22.0 bundles Envoy 1.35.3 and drops support for Envoy 1.31.10. With
Envoy 1.35 and later, generated configuration includes a TLS transport socket
only when a CA bundle is present, preventing startup failure when it is absent.

### Envoy 1.37.2 and newer

Consul 2.0.0 updates service-mesh compatibility to Envoy 1.37.2 and newer. This
is especially important when Envoy is installed or pinned independently from
Consul. Choose an Envoy version supported by both sides of a rolling upgrade.

## Multi-port service-mesh routing

Since 2.0.0, Enterprise sidecars can advertise named local ports with
`proxy.local_service_ports`. An upstream selects a named destination through
`proxy.upstreams[].destination_port`.

Direct-mode applications continue to use `localhost:<bind-port>`.
Transparent-proxy applications can dial
`<port-name>.<service>.virtual.consul`.

## HTTP path normalization

### Managed gateway listeners

Since 2.0.0, API Gateway and terminating-gateway HTTP listeners normalize
request paths. The normalization prevents non-normalized paths from bypassing
L7 intention RBAC checks.

### Custom Envoy public listeners

Since 2.0.3, user-supplied `envoy_public_listener_json` HTTP Connection Manager
filter chains receive Consul's default path normalization before L7 intention
enforcement. The behavior applies to custom public listeners unless the mesh
option `InsecureDisablePathNormalization` is set. Treat disabling normalization
as a security-sensitive exception.

## SDS-backed gateway certificates

Since 2.0.0, API Gateway listeners can use a default SDS TLS certificate. HTTP
or TCP route services can override it and inherit the listener's SDS cluster
when no override cluster is supplied. Conflicting override mappings are
rejected.

Terminating-gateway upstream TLS also uses SDS, so certificates can change
without restarting the gateway.

## API Gateway upstream limits

Since 2.0.0, API Gateway supports gateway-wide upstream defaults and
route-service overrides for:

- `MaxConnections`;
- `MaxPendingRequests`; and
- `MaxConcurrentRequests`.

Use the gateway-wide values as a baseline and reserve route overrides for
services with distinct capacity or latency characteristics.

## Kubernetes API Gateway scaling

Since 2.0.0, Enterprise API Gateways on Kubernetes can scale beyond the
previous eight-replica limit. Enable Horizontal Pod Autoscaling through
annotations on the Gateway resource.

## CyberArk Workload Identity Manager CA

Since 2.0.0, Enterprise can delegate service-mesh certificate signing to
CyberArk Workload Identity Manager, also known as Venafi Firefly. Configure:

```hcl
connect {
  ca_provider = "pan-distributed-issuer"
}
```

## Passive upstream health thresholds

Since 2.0.0, Enterprise `PassiveHealthCheck` supports these Envoy outlier
detection fields:

- `Consecutive5xx` for general 5xx responses;
- `ConsecutiveGatewayFailure` for 502, 503, and 504 responses; and
- `EnforcingConsecutiveGatewayFailure` to control enforcement of the gateway
  failure threshold.

Tune detection and enforcement together so observation does not unintentionally
become ejection.

## API Gateway server headers

Since 2.0.3, `ProxyDefaults.spec.config` provides:

- `envoy_suppress_envoy_headers` to remove the server response header; and
- `envoy_server_header_name` to rename that header.

Suppression takes precedence when both settings are present.

```yaml
spec:
  config:
    envoy_server_header_name: edge-gateway
```

## XFCC on inbound gRPC

Since 2.0.3, Connect-proxy inbound listeners add XFCC headers to gRPC requests,
matching their existing behavior for HTTP requests. Review upstream trust and
header-processing logic if it distinguishes HTTP from gRPC.

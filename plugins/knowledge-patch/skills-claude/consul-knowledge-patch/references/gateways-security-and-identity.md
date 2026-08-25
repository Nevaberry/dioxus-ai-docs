# Gateways, Security, and Identity

## Configure UI OIDC clients

Since 1.22.0, PKCE is enabled by default for Consul UI OIDC login. OIDC providers can authenticate the client with a JWT assertion instead of a client secret. Match the provider's client registration and Consul configuration to the intended authentication method.

## Handle KV key validation

Since 1.22.0, the key/value endpoint validates key names. This is a breaking security change for clients or existing data that relied on previously accepted invalid names.

Audit key producers and names before rollout. `DisableKVKeyValidation` controls whether validation is disabled; use it only as a temporary, explicit compatibility decision.

## Normalize paths before L7 intention checks

Since 2.0.0, API Gateway and terminating-gateway HTTP listeners normalize request paths before L7 intention RBAC evaluation. This prevents non-normalized paths from bypassing authorization checks.

Since 2.0.3, Consul also applies its default normalization to user-supplied `envoy_public_listener_json` HTTP Connection Manager filter chains and other custom public listeners. The mesh option `InsecureDisablePathNormalization` disables that protection. Avoid the insecure option unless its security consequence is understood and accepted.

## Source gateway certificates through SDS

Since 2.0.0, an API Gateway listener can use a default SDS TLS certificate. HTTP and TCP route services can override that certificate. Without an override, a service inherits the listener's SDS cluster; Consul rejects conflicting override mappings.

Terminating-gateway upstream TLS also uses SDS. Certificate material can therefore change without restarting the gateway.

## Apply API Gateway upstream limits

Since 2.0.0, API Gateway accepts gateway-wide defaults and route-service overrides for:

- `MaxConnections`.
- `MaxPendingRequests`.
- `MaxConcurrentRequests`.

Use route overrides for exceptional destinations and keep the gateway-wide values aligned with normal upstream capacity.

## Delegate mesh signing to CyberArk WIM

Since 2.0.0, Enterprise can delegate service-mesh certificate signing to CyberArk Workload Identity Manager, also known as Venafi Firefly:

```hcl
connect {
  ca_provider = "pan-distributed-issuer"
}
```

## Respect agent API body limits

Since 2.0.3, the agent caps request bodies at 512 KiB before decoding or ACL resolution for:

- Check updates.
- Check registration.
- Service registration.
- Connect authorization.

The limit also applies to chunked transfer encoding. Oversized requests return HTTP 413. Split large payloads rather than retrying them with a different transfer encoding or token.

## Limit external gRPC connections by source

Since 2.0.3, external gRPC and gRPC-TLS listeners default to 100 connections per source IP. Configure the value with `limits.grpc_max_conns_per_client`:

```hcl
limits {
  grpc_max_conns_per_client = 100
}
```

Their handshake timeout is 20 seconds rather than 120 seconds. Consider shared NAT addresses when choosing a connection limit.

## Control the API Gateway server header

Since 2.0.3, `ProxyDefaults.spec.config` accepts:

- `envoy_suppress_envoy_headers` to remove the server response header.
- `envoy_server_header_name` to rename it.

If both are set, suppression takes precedence.

```yaml
spec:
  config:
    envoy_server_header_name: edge-gateway
```

## Forward XFCC on inbound gRPC

Since 2.0.3, Connect-proxy inbound listeners add XFCC headers to gRPC requests, matching their existing HTTP behavior. Account for the header in applications or intermediaries that validate or consume forwarded client-certificate identity.

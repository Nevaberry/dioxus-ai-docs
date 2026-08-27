# Discovery and Networking

## Agentless External Service Monitor

Since 1.21.0, Consul External Service Monitor can connect directly to Consul
servers instead of requiring a colocated Consul agent. It uses one outbound TCP
connection and does not join cluster gossip. This is useful where inbound
connectivity or gossip participation is constrained.

## Session-driven health checks

Since 1.21.0, a Consul session can update the state of a health check. Use this
when session lifecycle should directly affect service-health reporting.

## Multi-port catalog and DNS discovery

Since 1.22.0, service definitions can use the optional `ports` parameter to
register multiple ports in the catalog. Kubernetes Service sync handles
multi-port Kubernetes Services, and Consul DNS accepts a `port` field to select
a particular service port.

Keep port names stable across registration, Kubernetes sync, DNS consumers, and
service-mesh configuration. See the service-mesh reference for Enterprise
sidecar and upstream routing.

## IPv6 and dual-stack addressing

Since 1.22.0, agents and services on VMs and Kubernetes can use IPv4 or IPv6.
Prefer a single address family within a datacenter. IPv6 is not supported on
OpenShift, Nomad, or ECS in this release.

Envoy bootstrap uses `127.0.0.1` in IPv4-only environments and `::1` in IPv6 or
dual-stack environments. When the agent bind address is IPv6,
`upstream.local_bind_address` and `proxy.local_service_address` default to
`::1`. Audit configurations that assume an IPv4 loopback.

## Agent API request-body ceiling

Since 2.0.3, the agent rejects request bodies larger than 512 KiB before body
decoding or ACL resolution for:

- check updates;
- check registration;
- service registration; and
- Connect authorization.

The cap also applies to chunked transfer encoding. Oversized requests return
HTTP 413. Split large registrations or authorization inputs, and classify 413
responses separately from ACL denials.

## External gRPC connection limiting

Since 2.0.3, external gRPC and gRPC-TLS listeners default to 100 connections per
source IP. Configure the limit with:

```hcl
limits {
  grpc_max_conns_per_client = 100
}
```

The listener handshake timeout is 20 seconds rather than 120 seconds. Account
for clients concentrated behind NAT or a load balancer, and test slow
connections before adopting a stricter value.

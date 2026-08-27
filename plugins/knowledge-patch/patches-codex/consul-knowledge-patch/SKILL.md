---
name: consul-knowledge-patch
description: HashiCorp Consul
version: "2.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# HashiCorp Consul Compatibility Guide

Use this skill when planning, configuring, upgrading, or troubleshooting Consul
deployments whose behavior may depend on recent agent, platform, service-mesh,
gateway, licensing, or operational changes.

Prefer the running deployment's configuration, API responses, release notes,
and observed behavior when they disagree with this guidance. Separate Community
and Enterprise advice: several controls described here are Enterprise-only.

## Working method

1. Identify the Consul version and edition on every server and client.
2. Record the deployment environment: VM, Kubernetes, OpenShift, Nomad, or ECS.
3. For service mesh, identify the Envoy version and whether proxies run in
   direct or transparent mode.
4. For federated deployments, map the primary and secondary datacenters before
   selecting a rollout order.
5. Check ACL token persistence, quorum, redundancy, and rollback readiness
   before restarting agents.
6. Apply version-sensitive defaults explicitly when predictable behavior is
   more important than inheriting a changed default.
7. Validate security-sensitive paths, listener behavior, and request limits
   with representative traffic after the change.

## Reference index

| Reference | Topics |
| --- | --- |
| [Discovery and networking](references/discovery-and-networking.md) | Agentless ESM, sessions, multi-port registration and DNS, IP families, agent request and gRPC limits |
| [Operations and telemetry](references/operations-and-telemetry.md) | Snapshots, utilization, HTTP timeouts, RPC limits, telemetry, certificate monitoring, licensing |
| [Platforms, identity, and storage](references/platforms-identity-and-storage.md) | Kubernetes security, OpenShift support and migration, OIDC, Azure identity, KV validation |
| [Service mesh and gateways](references/service-mesh-and-gateways.md) | Envoy compatibility, routing, normalization, SDS, gateway scaling and limits, CA and health controls |
| [Upgrades and lifecycle](references/upgrades-and-lifecycle.md) | Support cadence, rolling and federated upgrades, protocol transitions, ACL recovery, Autopilot migrations |

## Breaking and security-sensitive changes

### Validate KV keys before enabling enforcement

The KV endpoint rejects invalid key names by default in affected releases.
Audit producers and stored key conventions before upgrading. Use
`DisableKVKeyValidation` only as a deliberate compatibility escape hatch, and
plan to remove it after callers are corrected.

### Budget for bounded agent API bodies

Check updates, check and service registration, and Connect authorization have a
512 KiB request-body ceiling. The limit is enforced before decoding or ACL
resolution and also applies to chunked requests. Split oversized payloads and
treat HTTP 413 as a size failure, not an ACL failure.

### Preserve L7 path normalization

API Gateway and terminating-gateway HTTP listeners normalize paths before L7
intention RBAC checks. Custom Envoy public-listener HTTP Connection Manager
chains also receive the default normalization. Do not disable it casually with
`InsecureDisablePathNormalization`; doing so restores a bypass-prone boundary.

### Account for gRPC listener limits

External gRPC and gRPC-TLS listeners default to 100 connections per source IP
and a 20-second handshake timeout. Review concentrated clients, NAT gateways,
and load balancers before rollout. Set `limits.grpc_max_conns_per_client`
explicitly when the default is unsuitable.

### Recheck Envoy pins

Do not assume an independently installed Envoy remains compatible. Affected
releases dropped Envoy 1.31.10, bundled 1.35.3, and later moved service-mesh
compatibility to Envoy 1.37.2 and newer. Find a mutually supported Envoy version
before rolling agents and proxies.

## Upgrade guardrails

### Preserve quorum and service availability

- Upgrade server agents one at a time and wait for health and membership before
  proceeding.
- Upgrade Raft followers before the leader when controlling order explicitly.
- Roll client agents only after servers are healthy on the new release.
- Provide redundant service instances because a client and its services are
  unavailable between `consul leave` and agent restart.
- On mesh clients, stop the old agent and associated proxies, start the new
  agent, then start compatible proxies.
- Confirm versions and protocols with `consul members` after each phase.

### Treat federation as an ordered rollout

Upgrade the primary datacenter first, servers then clients, and repeat for each
secondary datacenter. Afterward, verify WAN membership and query ACL replication
from a secondary datacenter; the primary reports replication disabled even when
replication is functioning.

### Use two phases for incompatible protocols

When release notes require a protocol transition, first run the new binary with
the previous protocol override. After every node runs the new binary, restart
all agents without the override. The override changes the protocol spoken, not
the full protocol range understood, and can suppress new features while active.

### Restore non-persistent ACL tokens

If `enable_token_persistence` was disabled and tokens are absent from server
configuration, restore the `agent` and `default` tokens after restart so the
server can rejoin.

### Respect Enterprise license ordering

For the updated `enterprise-standard` license transition, move servers first,
one at a time, and restart only those servers. After the server set is ready,
apply the new license to clients and restart them.

## Configuration changes worth making explicit

### Agent HTTP timeouts

`http_config.read_timeout` and `write_timeout` default to 15 minutes, allowing
long-polling blocking queries to complete. `read_header_timeout` remains 10
seconds and `idle_timeout` remains 120 seconds. Pin all four when proxies or
clients depend on a particular timeout budget.

### Multi-port services

Use a service definition's optional `ports` parameter to register named ports.
Kubernetes Service sync understands multi-port Services, and Consul DNS accepts
a `port` selector. In Enterprise mesh, sidecars advertise named local ports with
`proxy.local_service_ports` and upstreams select one through
`proxy.upstreams[].destination_port`.

Direct-mode applications still dial `localhost:<bind-port>`. Transparent-proxy
applications can dial `<port-name>.<service>.virtual.consul`.

### IPv6 and dual stack

Choose one address family per datacenter where possible. IPv6 is available for
agents and services on VMs and Kubernetes but is not supported on OpenShift,
Nomad, or ECS in the affected release. Envoy bootstrap loopback and proxy bind
defaults change to `::1` when the agent bind address is IPv6.

### Cluster-wide RPC controls

Enterprise clusters can change RPC limits at runtime with the Raft-replicated
`rate-limit` configuration entry. Exempt critical methods deliberately. Obtain
targetable method names from `GET /v1/internal/rpc/methods` using a token with
`operator:read`.

## Service-mesh and gateway checks

### Manage certificates through SDS

API Gateway listeners can use a default SDS TLS certificate while HTTP or TCP
route services override it. An override without its own cluster inherits the
listener's SDS cluster; conflicting mappings are rejected. Terminating-gateway
upstream TLS also uses SDS, allowing certificate rotation without restart.

### Tune gateway resource pressure

Set gateway-wide defaults or route-service overrides for `MaxConnections`,
`MaxPendingRequests`, and `MaxConcurrentRequests`. On Kubernetes, Enterprise API
Gateways can exceed eight replicas and can enable Horizontal Pod Autoscaling
through Gateway annotations.

### Control response identity and client certificates

In `ProxyDefaults.spec.config`, use `envoy_suppress_envoy_headers` to remove the
server response header or `envoy_server_header_name` to rename it. Suppression
wins if both are set. Connect-proxy inbound listeners add XFCC headers to gRPC
requests as well as HTTP requests.

### Monitor certificate and passive health

Scrape `/agent/metrics` for active root and signing CAs, agent certificates, and
leaf-renewal health. Use structured certificate-expiration logs and Connect CA
`NotAfter` values for alerting. Enterprise passive checks can distinguish
general 5xx failures from gateway failures through `Consecutive5xx`,
`ConsecutiveGatewayFailure`, and `EnforcingConsecutiveGatewayFailure`.

## Platform and identity checks

### Prepare OpenShift migrations

OpenShift 4.19 and later requires the newer `consul.hashicorp.com` gateway
resource types. Migrate older Kubernetes Gateway API `v1alpha` resources during
the platform upgrade. Do not plan IPv6 for the affected OpenShift support line.

### Use current Kubernetes security controls

Apply Kubernetes Pod Security Admission per namespace; it replaces
PodSecurityPolicy for enforcing minimum pod security requirements.

### Review OIDC and storage credentials

PKCE is enabled by default for UI OIDC login, and providers may authenticate the
OIDC client using a JWT assertion rather than a secret. Snapshot workflows can
use Google Cloud Storage, or Azure Blob Storage with Azure Managed Service
Identity, reducing static credential use.

## Post-change verification

- Confirm every server is healthy and quorum is intact.
- Confirm every agent reports the intended build and protocol.
- Exercise blocking queries longer than 30 seconds.
- Test valid and invalid KV key names.
- Test normalized and deliberately malformed gateway paths.
- Exercise payloads near the 512 KiB agent API ceiling.
- Check gRPC connection concentration by source IP.
- Verify named-port discovery in catalog, DNS, direct mesh, and transparent
  proxy modes as applicable.
- Confirm certificate metrics, logs, and renewal health are visible.
- In federation, confirm WAN membership and ACL replication from a secondary.

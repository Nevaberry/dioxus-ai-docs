---
name: consul-knowledge-patch
description: HashiCorp Consul
version: "2.0.0"
license: MIT
metadata:
  author: Nevaberry
---


# HashiCorp Consul

Use this skill when designing, configuring, upgrading, or troubleshooting Consul deployments whose behavior depends on recent discovery, service-mesh, gateway, Kubernetes, security, Enterprise, or operational changes.

Treat the reference files as task-oriented supplements. Inspect the deployment's actual Consul and Envoy versions, edition, platform, topology, and configuration before applying guidance. Release-specific behavior does not replace an existing tested constraint.

## Reference index

| Reference | Topics |
| --- | --- |
| [Discovery, networking, and mesh](references/discovery-networking-and-mesh.md) | ESM, sessions, multi-port services, IPv6, Envoy compatibility, mesh routing, passive health |
| [Enterprise operations and telemetry](references/enterprise-operations-and-telemetry.md) | support policy, utilization, RPC limits, HTTP timeouts, product and certificate telemetry, IBM licensing |
| [Gateways, security, and identity](references/gateways-security-and-identity.md) | OIDC, KV validation, path normalization, SDS, gateway limits, CA providers, request limits, headers |
| [Kubernetes and snapshots](references/kubernetes-and-snapshots.md) | GCS and Azure snapshots, Pod Security Admission, OpenShift, API Gateway scaling and migration |
| [Upgrades and rollouts](references/upgrades-and-rollouts.md) | license sequencing, maintained-version cadence, federated rollouts, protocol transitions, Autopilot |

## Start with compatibility and security changes

### Validate KV names before rollout

The KV endpoint rejects invalid key names by default. Audit writers and stored keys before upgrading. Use `DisableKVKeyValidation` only as a deliberate compatibility escape hatch, with a plan to remove invalid names.

### Keep HTTP paths normalized before L7 authorization

API Gateway and terminating-gateway HTTP listeners normalize paths before intention RBAC checks. Custom `envoy_public_listener_json` HTTP Connection Manager filter chains receive the same normalization. Do not set `InsecureDisablePathNormalization` unless the bypass risk is explicitly accepted.

### Account for bounded agent requests

Check updates, check and service registration, and Connect authorization requests are limited to 512 KiB before decoding or ACL resolution. This includes chunked requests. Split oversized registrations and treat HTTP 413 as a size failure, not an ACL failure.

### Bound external gRPC clients

External gRPC and gRPC-TLS listeners default to 100 connections per source IP, and their handshake timeout is 20 seconds. Tune `limits.grpc_max_conns_per_client` only after checking client fan-out and shared-NAT behavior.

```hcl
limits {
  grpc_max_conns_per_client = 100
}
```

### Match Consul and Envoy deliberately

The bundled Envoy line changed to 1.35.3 while 1.31.10 support was removed, and Consul 2.0 service mesh expects Envoy 1.37.2 or newer. Verify separately installed or pinned Envoy binaries before rolling agents. For Envoy 1.35+, generated configuration adds a TLS transport socket only when a CA bundle exists.

### Migrate OpenShift gateway resources

OpenShift 4.19+ requires the newer resource types in the `consul.hashicorp.com` API group. Inventory and migrate older Kubernetes Gateway API `v1alpha` resources as part of the OpenShift upgrade.

## High-value configuration changes

### Preserve blocking queries with agent HTTP defaults

Agent `http_config.read_timeout` and `write_timeout` now default to 15 minutes. `read_header_timeout` remains 10 seconds and `idle_timeout` remains 120 seconds. Set all four explicitly when load balancers, proxies, or clients need a different timeout contract.

### Register and route named ports

Use service `ports` for multi-port catalog registration. Kubernetes Service sync understands multi-port Services, and DNS can select a port with its `port` field.

Enterprise sidecars advertise named local ports with `proxy.local_service_ports`; upstreams choose one with `proxy.upstreams[].destination_port`. Direct-mode callers still use `localhost:<bind-port>`, while transparent-proxy callers use `<port-name>.<service>.virtual.consul`.

### Change Enterprise RPC limits without restarts

Use the Raft-replicated `rate-limit` configuration entry for cluster-wide RPC limits and critical-method exemptions. Discover targetable method names with:

```shell
curl -H "X-Consul-Token: $CONSUL_HTTP_TOKEN" \
  https://consul.example/v1/internal/rpc/methods
```

The token needs `operator:read`.

### Rotate gateway certificates through SDS

API Gateway listeners can use a default SDS certificate. HTTP or TCP route services may override it and otherwise inherit the listener's SDS cluster; conflicting override mappings are rejected. Terminating-gateway upstream TLS also uses SDS, so certificates can change without restarting the gateway.

### Tune gateway upstream pressure

Apply gateway-wide defaults or route-service overrides for `MaxConnections`, `MaxPendingRequests`, and `MaxConcurrentRequests`. Keep overrides consistent with the capacity of each destination.

### Configure passive failure detection

Enterprise `PassiveHealthCheck` supports `Consecutive5xx`, `ConsecutiveGatewayFailure`, and `EnforcingConsecutiveGatewayFailure`. Gateway failures cover HTTP 502, 503, and 504; choose thresholds that distinguish a bad upstream from brief transients.

## Safe upgrade workflow

1. Confirm the source and target Consul versions support a direct upgrade. Routine upgrades should cross no more than two major jumps; Enterprise LTS operators may cross at most three.
2. Confirm that the installed Envoy version is supported by both old and new Consul versions. Centralize sidecar and mesh-gateway configuration before WAN-federated mesh upgrades.
3. Snapshot state, verify quorum, and identify the Raft leader with `consul operator raft list-peers`.
4. Upgrade primary-datacenter server followers one at a time, then the leader, waiting for each server to rejoin and become healthy. Upgrade clients afterward.
5. Repeat servers then clients for each secondary datacenter. Preserve redundant service instances because a client is undiscoverable between `consul leave` and restart.
6. If the release requires an incompatible protocol transition, run the new binary with `-protocol=PREVIOUS` everywhere first, then restart all agents without the override.
7. Restore non-persisted `agent` and `default` ACL tokens when needed. Verify LAN and WAN membership, agent builds, and protocol versions.
8. Query `/v1/acl/replication` from a secondary datacenter after the rollout; the primary reports replication as disabled even when replication works.

See [Upgrades and rollouts](references/upgrades-and-rollouts.md) for exact Enterprise license order, Envoy stop/start sequencing, commands, and Autopilot replacement behavior.

## Platform decisions

### Choose one address family per datacenter

Agents and services on VMs and Kubernetes can use IPv4 or IPv6, but one family per datacenter is recommended. IPv6 is unavailable on OpenShift, Nomad, and ECS for the relevant behavior. Envoy uses `127.0.0.1` in IPv4-only environments and `::1` in IPv6 or dual-stack environments; IPv6 agent binds also default local upstream and proxy service addresses to `::1`.

### Apply namespace pod-security controls

Use Kubernetes Pod Security Admission per namespace instead of PodSecurityPolicy. Validate Consul components against the namespace policy before enforcing it.

### Select snapshot authentication by platform

The Enterprise Kubernetes snapshot-agent sidecar can store snapshots locally, in Amazon S3, Azure Blob Storage, or Google Cloud Storage. Azure Blob can use Azure Managed Service Identity instead of static credentials.

### Scale and migrate gateways consciously

Enterprise Kubernetes API Gateways can exceed eight replicas and use Horizontal Pod Autoscaling enabled with Gateway annotations. On OpenShift upgrades, coordinate scaling changes with the required resource migration.

## Identity and certificate choices

PKCE is enabled by default for UI OIDC login. Providers may authenticate the OIDC client with a JWT assertion rather than a client secret; align the provider registration with the selected method.

Enterprise service-mesh certificate signing can be delegated to CyberArk Workload Identity Manager (Venafi Firefly) with:

```hcl
connect {
  ca_provider = "pan-distributed-issuer"
}
```

Use the Connect CA API `NotAfter` values plus `/agent/metrics` certificate metrics to monitor roots, intermediates, signing CAs, agent certificates, and leaf renewal. Structured certificate-expiration logs support configurable severity thresholds.

## Observability and reporting

Self-managed Enterprise product-usage telemetry is opt-in and disabled by default. Keep the choice explicit in configuration and change review.

Census metrics collection is always enabled, while export for license reporting is configurable. For manual or air-gapped reporting, use `/v1/operator/utilization` or generate a census bundle:

```shell
consul operator utilization [-today-only] [-message] [-y]
```

Certificate metrics carry datacenter, partition, and namespace labels. Design alerts with those dimensions so the affected trust domain is identifiable.

## Troubleshooting checklist

- HTTP 413 during registration or authorization: measure the encoded body and split it below 512 KiB.
- Long-poll query ends too early: inspect all four agent HTTP timeout values and every intermediary timeout.
- External gRPC clients cannot connect: check per-source-IP counts, NAT aggregation, and the 20-second handshake window.
- Envoy fails after an agent upgrade: compare the Envoy version with both Consul versions and verify whether a CA bundle exists.
- L7 intentions behave unexpectedly: confirm path normalization applies to standard and custom public listeners.
- A route receives the wrong certificate: check listener defaults, route overrides, SDS-cluster inheritance, and conflicting mappings.
- Multi-port traffic reaches the wrong endpoint: align catalog port names, local sidecar ports, upstream `destination_port`, and the application dial mode.
- ACL replication appears disabled: make the check against a secondary datacenter, not the primary.
- A restarted server cannot rejoin: restore non-persisted `agent` and `default` tokens.
- Gateway responses expose an unwanted server header: use `envoy_suppress_envoy_headers`, or rename it with `envoy_server_header_name`; suppression wins when both are set.

## Detailed lookup

Read only the reference relevant to the task, then validate against the live configuration:

- Service registration, DNS, IP families, Envoy, or outlier detection: [Discovery, networking, and mesh](references/discovery-networking-and-mesh.md).
- Support policy, license reporting, runtime limits, or certificate monitoring: [Enterprise operations and telemetry](references/enterprise-operations-and-telemetry.md).
- Authentication, gateway TLS, L7 enforcement, gRPC, or proxy headers: [Gateways, security, and identity](references/gateways-security-and-identity.md).
- Kubernetes security, snapshots, OpenShift, or gateway controllers: [Kubernetes and snapshots](references/kubernetes-and-snapshots.md).
- Rolling, federated, automated, license, or protocol upgrades: [Upgrades and rollouts](references/upgrades-and-rollouts.md).

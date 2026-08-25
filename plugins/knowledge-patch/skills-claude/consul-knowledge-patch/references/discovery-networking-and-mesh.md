# Discovery, Networking, and Service Mesh

## Deploy External Service Monitor without a local agent

Since 1.21.0, Consul External Service Monitor can connect directly to Consul servers over one outbound TCP connection. It no longer requires a colocated Consul agent and does not join cluster gossip. This reduces the network access needed for deployments in constrained environments.

## Drive health state from a session

Since 1.21.0, a Consul session can update a health check's state. Use this when session lifecycle should directly affect the health presented through service discovery.

## Register and resolve multiple service ports

Since 1.22.0, service definitions accept an optional `ports` parameter for registering multiple catalog ports. Kubernetes Service sync also supports multi-port Kubernetes Services. Consul DNS exposes a `port` field so a lookup can target a specific service port.

Keep port names consistent across the workload, catalog registration, Kubernetes Service, DNS query, and mesh configuration.

## Plan IPv6 and dual-stack deployments

Since 1.22.0, agents and services on VMs and Kubernetes can use IPv4 or IPv6. Prefer a single address family within each datacenter. IPv6 is not supported on OpenShift, Nomad, or ECS for this behavior.

Envoy bootstrap selects loopback by environment:

- IPv4-only: `127.0.0.1`.
- IPv6 or dual-stack: `::1`.
- When the agent bind address is IPv6, `upstream.local_bind_address` and `proxy.local_service_address` also default to `::1`.

Audit explicit loopback values when moving an existing datacenter to IPv6 or dual-stack.

## Keep Envoy versions compatible

In 1.22.0, Consul bundles Envoy 1.35.3 and no longer supports Envoy 1.31.10. With Envoy 1.35 and later, generated configuration includes a TLS transport socket only when a CA bundle is present, avoiding startup failure when there is no bundle.

In 2.0.0, the compatible service-mesh Envoy level is 1.37.2 or newer. This is especially important when Envoy is installed or pinned separately. Before a rolling upgrade, choose an Envoy version supported by both the old and new Consul versions when possible.

## Route Enterprise mesh traffic to named ports

Since 2.0.0, Enterprise sidecars can advertise named local ports through `proxy.local_service_ports`. An upstream selects a named service port through `proxy.upstreams[].destination_port`.

The application address depends on proxy mode:

- Direct mode continues to dial `localhost:<bind-port>`.
- Transparent proxy mode dials `<port-name>.<service>.virtual.consul`.

Do not substitute the virtual address into a direct-mode application configuration.

## Configure passive upstream health thresholds

Since 2.0.0, Enterprise `PassiveHealthCheck` configuration adds:

- `Consecutive5xx` for general HTTP 5xx responses.
- `ConsecutiveGatewayFailure` for HTTP 502, 503, and 504 responses.
- `EnforcingConsecutiveGatewayFailure` to control enforcement for that gateway-failure threshold.

Use these values to tune Envoy outlier detection. Calibrate them to traffic volume and retry behavior so intermittent gateway errors do not eject a healthy upstream too aggressively.

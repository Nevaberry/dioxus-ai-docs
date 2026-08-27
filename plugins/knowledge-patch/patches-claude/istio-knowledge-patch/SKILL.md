---
name: istio-knowledge-patch
description: Istio
version: "1.30.0"
license: MIT
metadata:
  author: Nevaberry
---


# Istio Knowledge Patch

Use this skill when configuring, upgrading, operating, or troubleshooting Istio.
Determine the deployed Istio and Kubernetes versions before applying advice.
Use only guidance introduced at or below the deployed Istio version, and prefer
the manifests, rendered charts, CRDs, and observed runtime behavior when they
disagree with compatibility guidance.

## Reference map

| Reference | Topics |
| --- | --- |
| [references/upgrades-and-migrations.md](references/upgrades-and-migrations.md) | Upgrade gates, removals, renamed settings, default changes, and mixed-version hazards |
| [references/installation-and-cni.md](references/installation-and-cni.md) | Helm and istioctl installation, profiles, charts, CNI, nftables, resource scope, and platform integration |
| [references/ambient-and-multicluster.md](references/ambient-and-multicluster.md) | Ambient enrollment, DNS capture, waypoints, ztunnel, service scoping, and cross-network behavior |
| [references/gateways-and-traffic.md](references/gateways-and-traffic.md) | Gateway API, ServiceEntry, routing, retries, load balancing, traffic distribution, and extensions |
| [references/security-and-identity.md](references/security-and-identity.md) | TLS, CA integration, JWT, AuthorizationPolicy, Wasm, debug authorization, and compliance |
| [references/telemetry-and-observability.md](references/telemetry-and-observability.md) | Metrics, access logs, tracing, baggage, dashboards, and workload identity tags |
| [references/operations-and-istioctl.md](references/operations-and-istioctl.md) | istioctl behavior, control-plane tuning, diagnostics, revision tags, and operational defaults |

## Upgrade workflow

1. Record the current control-plane, gateway, ztunnel, CNI, and sidecar image
   versions; do not assume they advance atomically.
2. Render every Helm chart with production values and diff cluster-scoped RBAC,
   webhook, Service, EndpointSlice, NetworkPolicy, and CNI resources.
3. Upgrade external CRDs before the control plane when the target consumes a
   newer Gateway API version.
4. Review removed APIs, flags, annotations, and telemetry providers in
   [references/upgrades-and-migrations.md](references/upgrades-and-migrations.md).
5. Test mutating webhooks against native sidecars and validate mixed-version
   ambient behavior before broad rollout.
6. Ensure every ztunnel meets a feature's stated minimum version before
   enabling new ambient xDS fields.
7. Restart or reconcile workloads when a change depends on pod-time CNI or DNS
   capture state.
8. Validate Gateway status, proxy configuration, authorization, metrics, and
   multicluster synchronization after each phase.

## Highest-risk upgrade changes

### Prepare Kubernetes and Gateway API first

Istio 1.30 requires Kubernetes 1.32 or newer. Before that upgrade, install
Gateway API v1.5.x CRDs; otherwise `TLSRoute` and `ReferenceGrant` objects in
`gateway.networking.k8s.io/v1` are invisible to istiod. TLS passthrough can then
show `attachedRoutes: 0` without programming an Envoy listener.

Use the standard or experimental v1.5 CRD channel consistently with the APIs
you deploy. See the exact commands and listener changes in
[references/upgrades-and-migrations.md](references/upgrades-and-migrations.md).

### Migrate removed APIs and settings

- Replace OpenCensus and Lightstep tracing providers with OpenTelemetry.
- Remove reliance on `ENABLE_AUTO_SNI`.
- Migrate InferencePool resources to v1 and use
  `spec.endpointPickerRef.port.number`; specify the port explicitly.
- Migrate `BackendTLSPolicy` from v1alpha3 to v1.
- Replace `METRIC_ROTATION_INTERVAL` and
  `METRIC_GRACEFUL_DELETION_INTERVAL` with
  `sidecar.istio.io/statsEvictionInterval`.
- Replace `sidecar.istio.io/statsCompression` with
  `ProxyConfig.statsCompression`, globally or through a per-pod
  `proxy.istio.io/config` override.
- Replace `traffic.sidecar.istio.io/kubevirtInterfaces` with
  `istio.io/reroute-virtual-interfaces`.

### Account for data-plane rollout hazards

Eligible injected pods use native sidecars by default beginning with Istio
1.27. Test admission webhooks and controllers that expect `istio-proxy` to be a
regular container.

During an upgrade to 1.28, `ServiceEntry` resources with `resolution: NONE`
produce a `PASSTHROUGH` service type that older ztunnels NACK. Existing config
stays in place, but new entries can act absent until ztunnel is upgraded.

Do not enable ambient dry-run authorization until every connected ztunnel is
at least 1.29. Older ztunnels can fully enforce policy intended only for
dry-run.

### Review chart-owned object changes

The ztunnel chart briefly derived resource names from the Helm release in 1.25;
1.26 restored static `ztunnel` names. Pin `resourceName` deliberately when
crossing these releases.

The base chart later stopped creating RBAC and service-account objects that are
owned by the istiod chart. Names and suffix rules changed, so automation must
not depend on the earlier object names. Also set `global.enableReaderRBAC` on
both base and istiod when disabling multicluster reader resources.

## High-value configuration

### Ambient enrollment and CNI

DNS capture is on by default for newly enrolled ambient workloads. Existing
pods need restart or startup reconciliation; opt a pod out with
`ambient.istio.io/dns-capture=false`. DNS traffic honors outbound IP-range and
port exclusions for both TCP and UDP.

Ambient iptables or nftables startup reconciliation became enabled by default
in 1.29. Disable it only with
`cni.ambient.reconcileIptablesOnStartup=false`. Safe in-place CNI restart
handling separately prevents new pods from starting while the node agent
restarts; `AMBIENT_DISABLE_SAFE_UPGRADE=true` disables that protection.

Use `cni.istioOwnedCNIConfig=true` when Istio must own a combined primary and
Istio conflist. Both ambient and chained CNI must be enabled, and a custom
filename must sort before the primary CNI file.

### Service discovery and traffic placement

Addressless `ServiceEntry` resources receive IPs in `status.addresses` when
`PILOT_ENABLE_IP_AUTOALLOCATE` is enabled, which is the default. Proxies consume
them only with DNS proxying. Configure allocation prefixes with
`PILOT_IP_AUTOALLOCATE_IPV4_PREFIX` and
`PILOT_IP_AUTOALLOCATE_IPV6_PREFIX`.

`Service.spec.trafficDistribution` and the
`networking.istio.io/traffic-distribution` annotation work across data planes.
Namespace annotations provide inherited defaults, while a Service setting wins.
`PreferSameNode` and `PreferSameZone` are supported, and `PreferClose` ignores
subzone when selecting nearby endpoints.

Wildcard `DYNAMIC_DNS` routing has mode- and version-dependent constraints.
Read [references/gateways-and-traffic.md](references/gateways-and-traffic.md)
before using it, and trust only clients allowed to choose HTTP Host or TLS SNI.

### Gateway API and waypoints

Gateway-generated workloads can customize their `Service`, `Deployment`,
`ServiceAccount`, `HorizontalPodAutoscaler`, and `PodDisruptionBudget`.
Generated resources inherit Gateway labels and annotations by default.

Waypoints accept `TCPRoute`, can route to remote networks, and can receive
policy defaults through the `istio-waypoint` `GatewayClass`. Namespace-level
ingress waypoint selection uses the `istio.io/ingress-use-waypoint` label.

Gateway API `BackendTLSPolicy` supports named Service ports and ServiceEntry
targets. `FrontendTLSValidation` is supported, and TLSRoute termination and
mixed mode are available with the graduated TLS listener behavior.

### Security defaults

`FAIL_CLOSE` Wasm fetch failure installs deny-all RBAC. Wasm binary limits are
enforced after gzip decompression, and bearer-token realm URLs are validated.

JWT rules may omit `issuer` only when `jwksUri` is explicit. JWKS CIDR blocking
is applied after DNS resolution and across redirects and issuer discovery;
blocked or failed fetches reject JWT-authenticated requests.

Debug endpoints are authorized by default. Namespace-scoped access and the
`DEBUG_ENDPOINT_AUTH_ALLOWED_NAMESPACES` allowlist affect monitoring and
plaintext xDS tooling; the system namespace remains allowed.

### Telemetry defaults

OpenTelemetry is the replacement for removed tracing providers.
`disableContextPropagation` suppresses propagation headers without disabling
span reporting, and `serviceAttributeEnrichment: OTEL_SEMANTIC_CONVENTIONS`
adds standard service resource attributes.

Gateway upstream spans default on in newer installations. Zipkin can propagate
both B3 and W3C context and supports request timeouts plus literal or
environment-sourced headers.

Envoy Prometheus endpoint compression defaults on through
`ProxyConfig.statsCompression`. Circuit-breaker remaining-capacity metrics
default off unless legacy behavior is selected.

## Operational checks

- Treat headers in `istioctl proxy-config all` and `ztunnel-config all` as part
  of their tabular output contract.
- Use root `--kubeclient-timeout` for Kubernetes-client calls; it does not alter
  installation or command-specific timeouts.
- Use `--proxy-admin-port` with commands that must reach a non-default proxy
  admin endpoint.
- Watch `istiod_remote_cluster_sync_status` for remote-cluster synchronization.
- Expect istiod to derive `GOMEMLIMIT` as 90% of its container limit unless
  `GOMEMLIMIT` or `AUTOMEMLIMIT` overrides it.
- Review [references/operations-and-istioctl.md](references/operations-and-istioctl.md)
  before scripting output or renamed flags.

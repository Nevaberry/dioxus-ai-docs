---
name: istio-knowledge-patch
description: Istio
version: "1.30.0"
license: MIT
metadata:
  author: Nevaberry
---


# Istio Knowledge Patch

Use this skill when designing, upgrading, configuring, or troubleshooting Istio.
Resolve the deployed Istio, Kubernetes, Gateway API, CNI, and Helm versions from
manifests and live configuration before applying version-sensitive advice. Trust
the project's manifests, rendered resources, tests, and observed behavior when
they differ from guidance here.

## How to use this skill

1. Identify whether the task concerns an upgrade, installation, ambient mode,
   traffic management, security, telemetry, or command-line operations.
2. Read the matching reference file from the index. Read more than one when the
   task crosses control-plane, data-plane, and installation boundaries.
3. Check feature gates, environment variables, chart values, API versions, and
   defaults against the deployed release.
4. Treat entries marked experimental or alpha as opt-in and verify their
   Kubernetes API prerequisites.
5. During mixed-version upgrades, preserve compatibility until every affected
   proxy, ztunnel, gateway, and control-plane component has moved forward.

## Reference index

| Reference | Topics |
| --- | --- |
| [installation-and-upgrades.md](references/installation-and-upgrades.md) | Upgrade gates, removals, Helm behavior, platform requirements, chart resources, and installation security contexts |
| [ambient-cni-and-multicluster.md](references/ambient-cni-and-multicluster.md) | Ambient enrollment, DNS capture, CNI reconciliation, nftables, waypoints, ztunnel, and cross-network routing |
| [traffic-routing-and-gateways.md](references/traffic-routing-and-gateways.md) | ServiceEntry, DestinationRule, retries, traffic distribution, Gateway API, DNS routing, and EnvoyFilter behavior |
| [security-identity-and-policy.md](references/security-identity-and-policy.md) | Authorization, JWT, mTLS, certificates, trust bundles, JWKS, Wasm safety, and TLS controls |
| [telemetry-and-observability.md](references/telemetry-and-observability.md) | Metrics, tracing, logs, dashboards, baggage, workload identity tags, and OpenTelemetry |
| [operations-and-istioctl.md](references/operations-and-istioctl.md) | istioctl changes, debug access, Pilot controls, resource watching, proxy administration, and diagnostics |

## Breaking upgrade checks

### Prepare Kubernetes and Gateway API first

- Istio 1.30 requires Kubernetes 1.32 or newer.
- Before a 1.30 upgrade, install Gateway API v1.5.x CRDs. Istiod reads
  `TLSRoute` and `ReferenceGrant` from `gateway.networking.k8s.io/v1`; older
  CRDs can silently leave TLS passthrough routes unattached.
- Migrate `BackendTLSPolicy` from `v1alpha3` to `v1` before moving to 1.28.
- Migrate InferencePool objects to `v1`; use
  `spec.endpointPickerRef.port.number` and set the port explicitly.

### Account for data-plane transitions

- Native sidecars are enabled by default for eligible pods from 1.27. Test
  mutating webhooks and controllers that expect `istio-proxy` to be a regular
  container.
- During a mixed-version 1.28 ambient rollout, older ztunnels NACK the new
  `PASSTHROUGH` ServiceEntry type. Upgrade ztunnel before relying on newly added
  `resolution: NONE` entries or waypoint enforcement for them.
- Ambient startup reconciliation changed from opt-in to default-on by 1.29.
  Use `cni.ambient.reconcileIptablesOnStartup=false` only when deliberately
  disabling repair of enrolled-pod iptables or nftables state.
- Sidecar listeners that explicitly bind ports accept one connection per socket
  event by default from 1.28. Set
  `MAX_CONNECTIONS_PER_SOCKET_EVENT_LOOP=0` to restore the prior behavior.

### Update renamed or removed settings

- Replace OpenCensus and Lightstep tracing providers with OpenTelemetry.
- Remove reliance on `ENABLE_AUTO_SNI`; the flag and its code paths are gone.
- Replace `traffic.sidecar.istio.io/kubevirtInterfaces` with
  `istio.io/reroute-virtual-interfaces`.
- Replace `ISTIO_META_DNS_AUTO_ALLOCATE` with status-based ServiceEntry address
  allocation.
- Replace `METRIC_ROTATION_INTERVAL` and
  `METRIC_GRACEFUL_DELETION_INTERVAL` with
  `sidecar.istio.io/statsEvictionInterval`.
- Replace `sidecar.istio.io/statsCompression` with
  `ProxyConfig.statsCompression` or a per-pod `proxy.istio.io/config` override.
- Remove `--recursive` from `istioctl analyze`; analysis is always recursive.
  Remove `--xds-via-agents` from `istioctl proxy-status`.

### Protect chart-driven upgrades

- A nondefault ztunnel release name can rename resources in 1.25. Pin
  `resourceName=ztunnel`; 1.26 restores `ztunnel` as the default resource name.
- The 1.29 chart split moves duplicated RBAC and service-account objects from
  `base` to `istiod` and changes several names. Update ownership and automation
  before applying the charts.
- Istio-written CNI configuration defaults to mode `0600` from 1.30. Set
  `values.cni.env.CNI_CONF_GROUP_READ=true` when non-root group readers require
  `0640`.
- Istio 1.30 images default to `registry.istio.io`; allow or mirror that
  registry before rollout.
- With Helm 4 server-side apply, set
  `base.validationFailurePolicy: Fail` when rendering charts and applying them
  separately.

## High-value configuration changes

### Installation and CNI

- Set `global.platform=gke` for Helm or
  `values.global.platform=gke` for `istioctl`. GKE installations then create
  required ResourceQuotas and set `cniBinDir`; `istioctl` can detect GKE.
- Use `global.resourceScope: namespace` or `cluster` for persona-based installs.
  The ztunnel chart uses top-level `resourceScope`.
- Enable chart NetworkPolicies with `global.networkPolicy.enabled=true`; newer
  defaults include istiod, gateways, and istio-cni.
- For an Istio-owned ambient CNI conflist, enable
  `cni.istioOwnedCNIConfig=true` with both ambient and chained CNI. Ensure a
  custom filename sorts before the primary CNI file.
- Choose iptables explicitly with `FORCE_IPTABLES_BINARY`, or enable native
  nftables with `values.global.nativeNftables=true`.

### Service discovery and routing

- ServiceEntries without `spec.address` receive addresses in
  `status.addresses` by default; proxies consume them only with DNS proxying.
- Use `PILOT_IP_AUTOALLOCATE_IPV4_PREFIX` and
  `PILOT_IP_AUTOALLOCATE_IPV6_PREFIX` to choose controller VIP ranges.
- `Service.spec.trafficDistribution` and
  `networking.istio.io/traffic-distribution` apply across data planes. A
  namespace annotation supplies a default unless the Service overrides it.
- Sidecars and ambient egress waypoints can route wildcard
  `DYNAMIC_DNS` ServiceEntries under their documented constraints. Treat SNI
  and Host values as trusted-client inputs.
- Use `istio.io/connect-strategy: RACE_FIRST_TCP_CONNECT` to race DNS A-record
  endpoints; configure proxy DNS upstream timeout with `DNS_FORWARD_TIMEOUT`.
- DestinationRule retry budgets default to 20%; preserve both top-level and
  subset policies when subsets define their own traffic policy.

### Gateway API

- `BackendTLSPolicy` can target a named Service port with `sectionName` and can
  target a ServiceEntry.
- Gateway API `TLSRoute` supports termination, mixed mode, and GA TLS
  passthrough listeners without the alpha Gateway API flag.
- Generated Gateway resources inherit labels and annotations unless
  `EnableGatewayAPICopyLabelsAnnotations` is disabled.
- Use `ENABLE_GATEWAY_API_MANUAL_DEPLOYMENT=false` to stop automatic attachment
  to existing gateway deployments.
- Enable experimental Inference Extension with
  `SUPPORT_GATEWAY_API_INFERENCE_EXTENSION`; enable agentgateway with
  `PILOT_ENABLE_AGENTGATEWAY`.
- Use `PILOT_GATEWAY_TRANSPORT_SOCKET_CONNECT_TIMEOUT`; `15s` is the default
  and `0s` disables the gateway transport-socket timeout.

### Security and policy

- A failed Wasm fetch with `FAIL_CLOSE` installs deny-all RBAC. Do not assume
  fetch failure permits traffic.
- Ambient port-level `STRICT` PeerAuthentication rules enforce strict mTLS.
- JWT rules may omit `issuer` only when `jwksUri` is explicit.
- Enable ambient dry-run authorization only after all connected ztunnels are at
  least 1.29; older ztunnels can enforce a policy intended for dry-run.
- Keep debug endpoint authorization enabled where possible. Use
  `DEBUG_ENDPOINT_AUTH_ALLOWED_NAMESPACES` for explicit namespace access.
- For post-quantum policy, set `COMPLIANCE_POLICY=PQC` in both Pilot and
  ztunnel in ambient mode.
- Set `ISTIO_WASM_MAX_BINARY_SIZE_BYTES` to bound fetched and decompressed Wasm
  modules.

### Telemetry and operations

- Gateway upstream spans are enabled by default from 1.28. Configure the
  earlier opt-in with `PILOT_SPAWN_UPSTREAM_SPAN_FOR_GATEWAY`.
- Use `service.istio.io/workload-name` to override telemetry workload names.
- Set per-pod flush and eviction with
  `sidecar.istio.io/statsFlushInterval` and
  `sidecar.istio.io/statsEvictionInterval`.
- Use `serviceAttributeEnrichment: OTEL_SEMANTIC_CONVENTIONS` for Kubernetes
  service attributes in OpenTelemetry traces.
- Expect headers from `istioctl ztunnel-config all` and
  `istioctl proxy-config all` when parsing tabular output.
- Use root `--kubeclient-timeout` for Kubernetes-client calls and
  `--proxy-admin-port` when proxy administration is not on the default port.

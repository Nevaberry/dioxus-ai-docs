# Upgrades and migrations

Use this reference before changing control-plane or data-plane versions. Items
are grouped by the migration action they require; parenthetical identifiers are
the source batch in which the compatibility change was recorded.

## Prerequisites and preflight

- **Kubernetes floor** (`1.30.0`): Istio 1.30 requires Kubernetes 1.32.x or
  later. Upgrade Kubernetes before the mesh.
- **Gateway API CRDs** (`upgrade-1.30`): upgrade Gateway API CRDs to v1.5.x
  before Istio. Istio reads `TLSRoute` and `ReferenceGrant` from
  `gateway.networking.k8s.io/v1`; older CRDs make them invisible to istiod and
  can leave passthrough listeners with `attachedRoutes: 0` and no Envoy
  listener. Apply the standard channel with:

  ```bash
  kubectl apply -k "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v1.5.1"
  ```

  Use `config/crd/experimental?ref=v1.5.1` for the experimental channel.
- **Grafana** (`upgrade-1.25`): dashboards shipped with Istio 1.25 require
  Grafana 7.2 or later.
- **Dashboards** (`upgrade-1.27`): regenerate the bundled Grafana dashboards
  after upgrading. Explicit dashboard UIDs stabilize corrected cross-dashboard
  links.
- **Admission integrations** (`upgrade-1.27`): native sidecars are enabled by
  default for eligible pods, representing `istio-proxy` as an init container.
  Test mutating webhooks and controllers that expect a regular container.

## Removed providers, APIs, and options

- **OpenCensus** (`upgrade-1.25`): tracing support is removed with Envoy's
  OpenCensus extension. Migrate to OpenTelemetry before upgrading.
- **Lightstep** (`upgrade-1.26`): migrate Lightstep provider configuration to
  OpenTelemetry before Istio 1.27, where the provider is removed.
- **Auto SNI flag** (`1.26.0`): `ENABLE_AUTO_SNI` and its code paths are
  removed. Do not retain automation that relies on the flag.
- **InferencePool APIs** (`upgrade-1.28`): only v1 is accepted; alpha and RC
  versions are removed. When migrating from v1.0.0-rc.1, replace
  `spec.endpointPickerRef.portNumber` with
  `spec.endpointPickerRef.port.number` when `kind` is absent or `Service`, and
  specify the port because `9002` is no longer inferred.
- **BackendTLSPolicy** (`upgrade-1.28`): v1alpha3 is removed. Move policies to
  v1; the stable policy no longer needs `PILOT_ENABLE_ALPHA_GATEWAY_API=true`.
- **Stats eviction flags** (`upgrade-1.28`):
  `METRIC_ROTATION_INTERVAL` and `METRIC_GRACEFUL_DELETION_INTERVAL` are
  removed. Use the `sidecar.istio.io/statsEvictionInterval` pod annotation.
- **Stats compression annotation** (`upgrade-1.29`): replace removed
  `sidecar.istio.io/statsCompression` with `ProxyConfig.statsCompression`.
  Compression is enabled by default and negotiates Brotli, gzip, or Zstandard.
  A per-pod opt-out is:

  ```yaml
  metadata:
    annotations:
      proxy.istio.io/config: |
        statsCompression: false
  ```

- **Virtual-interface annotation** (`1.25.0`): replace deprecated
  `traffic.sidecar.istio.io/kubevirtInterfaces` with
  `istio.io/reroute-virtual-interfaces`. Its comma-separated interfaces cause
  inbound traffic to be treated as outbound in sidecar and ambient modes.
- **ServiceEntry IP metadata** (`1.25.0`):
  `ISTIO_META_DNS_AUTO_ALLOCATE` is deprecated. The enabled-by-default
  `PILOT_ENABLE_IP_AUTOALLOCATE` controller writes allocations to
  `status.addresses`; proxies use them only when DNS proxying is configured.

## Mixed-version data-plane hazards

- **Ambient PASSTHROUGH type** (`upgrade-1.28`): `ServiceEntry` objects with
  `resolution: NONE` use a new `PASSTHROUGH` service type. Older ztunnels NACK
  it. Existing configuration remains, but a new entry is treated as absent, so
  traffic passes through without determining whether a waypoint is required
  until ztunnel is upgraded.
- **Ambient dry-run policy** (`upgrade-1.29`): set
  `AMBIENT_ENABLE_DRY_RUN_AUTHORIZATION_POLICY=true` only after every connected
  ztunnel is at least 1.29. Older ztunnels do not understand the xDS field and
  fully enforce policy intended only for dry-run.
- **CNI reconciliation** (`upgrade-1.25`, changed by `upgrade-1.29`): startup
  reconciliation was initially opt-in through
  `cni.ambient.reconcileIptablesOnStartup=true`. It later became enabled by
  default for ambient iptables or nftables rules; set the value to `false` to
  disable it.
- **DNS capture state** (`upgrade-1.25`): newly created ambient workloads get
  DNS capture by default. Existing pods require restart or CNI startup
  reconciliation during upgrade.

## Chart names, ownership, and permissions

- **ztunnel naming** (`upgrade-1.25`, reversed by `upgrade-1.26`): Istio 1.25
  derived chart resource names from `.Resource.Name`, so a release name other
  than `ztunnel` could rename resources and cause downtime. Use
  `resourceName=ztunnel` to preserve names. Istio 1.26 restored static
  `ztunnel` names by default; use `resourceName=my-custom-name` only when a
  custom name is intentional.
- **Base/istiod ownership** (`upgrade-1.29`): the base chart no longer creates
  objects duplicated by istiod. Update automation for these changes:

  | Old object | New object |
  | --- | --- |
  | `ClusterRole istiod` | `ClusterRole istiod-clusterrole` |
  | `ClusterRole istiod-reader` | `ClusterRole istio-reader-clusterrole` |
  | `ClusterRoleBinding istiod` | `ClusterRoleBinding istiod-clusterrole` |
  | `ServiceAccount istiod-service-account` | `ServiceAccount istiod` |

  The names of the istiod `Role` and `RoleBinding` remain unchanged. For
  cluster-scoped resources, the old `-<global.istioNamespace>` suffix becomes
  an optional `-<revision>` followed by `-<release namespace>`.
- **CNI file modes** (`upgrade-1.30`): Istio-written CNI configuration defaults
  to `0600` rather than `0644`. Set
  `values.cni.env.CNI_CONF_GROUP_READ=true` for `0640` when non-root group
  tooling must read it.
- **Excluded namespaces** (`upgrade-1.30`): the CNI agent now enforces
  `excludeNamespaces` as well as the plugin. It un-enrolls existing ambient
  pods in excluded namespaces and does not enroll new ambient-labeled pods
  there.

## Changed routing and security defaults

- **Sidecar service selection** (`upgrade-1.30`): when a hostname is visible in
  multiple namespaces, select a Kubernetes `Service` first, then the oldest
  non-Kubernetes service by creation time. This replaces alphabetical namespace
  selection and can change mixed-service routing. Restore the old rule with
  `PILOT_SIDECAR_PICK_BEST_SERVICE_NAMESPACE=false` or `compatibilityVersion`
  1.28 or earlier.
- **Debug authorization** (`upgrade-1.29`): non-system clients are restricted
  to `config_dump`, `ndsz`, and `edsz` for proxies in their own namespace. This
  can affect Kiali and custom monitoring. Set `ENABLE_DEBUG_ENDPOINT_AUTH=false`
  only when the previous unrestricted behavior is required.
- **Plaintext xDS debug endpoints** (`upgrade-1.30`): authentication now covers
  `syncz` and `config_dump` on port 15010, affecting `istioctl --plaintext` and
  custom plaintext clients. `ENABLE_DEBUG_ENDPOINT_AUTH=false` restores the
  unauthenticated behavior.
- **Circuit-breaker metrics** (`upgrade-1.29`): Envoy `TrackRemaining` metrics
  are no longer enabled by default. Set
  `DISABLE_TRACK_REMAINING_CB_METRICS=false` or choose legacy behavior through
  the compatibility-version feature.

## CLI compatibility

- **Recursive analysis** (`1.25.0`): `istioctl analyze` is always recursive and
  no longer accepts `--recursive`.
- **Proxy status** (`1.25.0`): the experimental `--xds-via-agents` flag is
  removed from `istioctl proxy-status`.
- **Combined output** (`1.29.0`): `istioctl ztunnel-config all` and
  `istioctl proxy-config all` now print a header row. Update tabular parsers.


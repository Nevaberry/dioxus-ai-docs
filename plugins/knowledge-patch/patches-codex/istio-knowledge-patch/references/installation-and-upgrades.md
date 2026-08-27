# Installation and Upgrades

Use this reference for release preparation, Helm rendering, platform profiles,
resource ownership, and installation-time pod settings.

## Contents

- [Upgrade prerequisites and breaking transitions](#upgrade-prerequisites-and-breaking-transitions)
- [Helm names, ownership, and rendering](#helm-names-ownership-and-rendering)
- [Platform-specific installation](#platform-specific-installation)
- [CNI pod and node installation](#cni-pod-and-node-installation)
- [Generated resources](#generated-resources)

## Upgrade prerequisites and breaking transitions

### Native sidecars enabled by default (upgrade-1.27)

Native sidecars are enabled by default for eligible pods, changing
`istio-proxy` from a regular container to an init container. Test mutating
webhooks and controllers before upgrading because integrations that expect to
modify `istio-proxy` as a regular container may be incompatible.

### RuntimeDefault seccomp for sidecar containers (upgrade-1.28)

Configure `RuntimeDefault` seccomp for `istio-validation` and `istio-proxy`
through global proxy settings:

```yaml
global:
  proxy:
    seccompProfile:
      type: RuntimeDefault
```

### InferencePool v1 migration (upgrade-1.28)

Only the v1 InferencePool API is supported. Alpha and release-candidate API
versions have been removed. When migrating from v1.0.0-rc.1, replace
`spec.endpointPickerRef.portNumber` with the required
`spec.endpointPickerRef.port.number` structure when `kind` is unset or
`Service`. Specify the port explicitly because `9002` is no longer inferred.

### BackendTLSPolicy v1 only (upgrade-1.28)

The `v1alpha3` `BackendTLSPolicy` API has been removed. Migrate policies to
`v1`. The policy is no longer alpha, so
`PILOT_ENABLE_ALPHA_GATEWAY_API=true` is not required for processing it.

### Base chart RBAC and service-account removals (upgrade-1.29)

The `base` chart no longer creates objects duplicated in `istiod`. Account for
these changes in ownership and automation:

- `ClusterRole istiod` becomes `istiod-clusterrole`.
- `ClusterRole istiod-reader` becomes `istio-reader-clusterrole`.
- `ClusterRoleBinding istiod` becomes `istiod-clusterrole`.
- `ServiceAccount istiod-service-account` becomes `istiod`.
- The istiod `Role` and `RoleBinding` retain their names.
- The old `-<global.istioNamespace>` suffix becomes an optional `-<revision>`
  suffix followed by `-<release namespace>` for cluster-scoped resources.

### Gateway API v1.5 CRDs required (upgrade-1.30)

Upgrade Gateway API CRDs to v1.5.x before upgrading Istio. Istio reads
`TLSRoute` and `ReferenceGrant` from `gateway.networking.k8s.io/v1`; older CRDs
make them invisible to istiod, leaving TLS passthrough listeners with
`attachedRoutes: 0` and no programmed Envoy listener.

```bash
kubectl apply -k "github.com/kubernetes-sigs/gateway-api/config/crd?ref=v1.5.1"
```

Use `config/crd/experimental?ref=v1.5.1` for the experimental channel.

### Minimum supported Kubernetes version (1.30.0)

Istio 1.30 requires Kubernetes 1.32.x or later.

## Helm names, ownership, and rendering

### ztunnel Helm resource naming (upgrade-1.25)

In 1.25, ztunnel chart resources are named from `.Resource.Name` rather than
always being named `ztunnel`. A Helm release name other than `ztunnel` can
therefore rename resources and cause downtime. Preserve prior names with
`--set resourceName=ztunnel`.

### Static ztunnel Helm resource names restored (upgrade-1.26)

In 1.26, `ztunnel` is restored as the default static name for ztunnel chart
resources, reversing the 1.25 default. Override it when needed with
`--set resourceName=my-custom-name`.

### Helm platform and profile override forms (1.25.0)

The `platform` and `profile` values support both local and global forms, such as
`--set platform=foo` and `--set global.platform=foo`.

### Customizable PodDisruptionBudget availability (1.25.0)

Installation configuration can customize the `PodDisruptionBudget`
`maxUnavailable` field.

### Gateway scale-to-zero behavior (1.26.0)

Setting `replicaCount=0` in the `istio/gateway` Helm chart emits `replicas: 0`
instead of omitting the field.

### Persona-based Helm installations (1.28.0)

Set `global.resourceScope` to `namespace` or `cluster` to install only resources
of that scope; leaving it unset installs both. In the ztunnel chart,
`resourceScope` is a top-level value.

### Optional installation NetworkPolicies (1.28.0)

Set `global.networkPolicy.enabled=true` to deploy default `NetworkPolicy`
resources for istiod and gateways.

### Default NetworkPolicy coverage for istio-cni (1.29.0)

With `global.networkPolicy.enabled=true`, the default NetworkPolicies also cover
istio-cni.

### Optional multicluster reader RBAC (1.30.0)

`global.enableReaderRBAC`, defaulting to `true`, controls the remote-secret
workflow's reader service account, ClusterRole, and ClusterRoleBinding. To
disable them with Helm, set it to `false` on both the base and istiod charts
because the resources are split between those charts.

### Helm 4 server-side apply support (1.30.0)

Istio charts support Helm 4 server-side apply and avoid taking `failurePolicy`
ownership during upgrades. Workflows that combine `helm template` with
server-side apply should set `base.validationFailurePolicy: Fail`.

### Network gateway port overrides (1.30.0)

Use `networkGatewayPorts` chart values to override ports on the network gateway
Service.

### Default image registry (1.30.0)

The default registry for Istio images is `registry.istio.io`.

## Platform-specific installation

### Explicit GKE ambient platform profile (1.25.0)

Ambient installations on GKE should select the explicit profile with
`--set global.platform=gke` for Helm or
`--set values.global.platform=gke` for `istioctl`. This replaces the CNI chart's
Kubernetes-version-based GKE auto-detection.

### GKE installation automation (1.26.0)

With `global.platform=gke`, installation creates required `ResourceQuota`
resources and configures `cniBinDir`. `istioctl` enables this platform setting
automatically when it detects GKE.

### Helm-managed untaint controller (upgrade-1.30)

Setting `taint.enabled` in the istiod Helm chart automatically configures
`PILOT_ENABLE_NODE_UNTAINT_CONTROLLERS`; the istiod deployment no longer needs
that variable activated manually.

### EKS branch-ENI ambient probes (1.30.0)

On AWS EKS with Security Groups for Pods, istio-cni detects branch-ENI pods and
routes kubelet probes through the veth pair instead of the VPC fabric. The
enabled-by-default `AMBIENT_ENABLE_AWS_BRANCH_ENI_PROBE` controls this behavior.

## CNI pod and node installation

### istio-cni capability and AppArmor changes (1.25.0)

The `istio-cni-node` DaemonSet receives `DAC_OVERRIDE` and an unconfined
AppArmor annotation, restoring privileges needed after the privileged security
context was removed in 1.24.

### CNI DNS policy with host networking (1.25.0)

When istio-cni runs with `hostNetwork=true`, its pod uses
`dnsPolicy: ClusterFirstWithHostNet`.

### Safe in-place istio-cni upgrades (1.25.0)

Safe restart and upgrade handling for the `system-node-critical` istio-cni
DaemonSet is enabled by default. It prevents new pods from starting on a node
while the agent restarts. Set `AMBIENT_DISABLE_SAFE_UPGRADE=true` in istio-cni
to disable it.

### CNI operation without host networking (1.26.0)

The CNI agent no longer requires `hostNetwork`; it enters the host network
dynamically when needed. Restore the previous behavior temporarily with the
istio-cni chart field `ambient.shareHostNetworkNamespace`.

### Restrictive CNI config file permissions (upgrade-1.30)

Istio-written CNI configuration files default to mode `0600` instead of `0644`.
Non-root group tooling that must read them can request `0640` with
`values.cni.env.CNI_CONF_GROUP_READ=true`.

### Kubernetes user namespaces with istio-cni (1.30.0)

Pods using Kubernetes user namespaces with `hostUsers: false` work with
istio-cni on operating systems that provide the `nsenter` binary.

### CNI AppArmor representation (1.30.0)

The istio-cni chart's `useAppArmorAnnotation` value defaults to `true`, retaining
the deprecated Kubernetes annotation form. Set it to `false` to render
`securityContext.appArmorProfile` instead.

### istio-cni termination grace period (1.29.0)

The istio-cni pod's `terminationGracePeriodSeconds` is configurable, and its
default has increased from 5 seconds to 30 seconds.

### ztunnel DNS configuration (1.30.0)

The ztunnel Helm chart exposes `dnsPolicy` and `dnsConfig` for environments
requiring custom pod DNS settings.

## Generated resources

### Shipped gateways excluded from ambient capture (1.25.0)

Istio-shipped gateways carry ambient dataplane exclusion labels by default,
avoiding accidental ambient enrollment when installed outside `istio-system`.

### EndpointSlices for remote istiod (1.28.0)

The istiod Helm chart creates `EndpointSlice` rather than `Endpoints` resources
for remote-istiod installations.

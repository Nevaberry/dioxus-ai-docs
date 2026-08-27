# Installation, Helm, and CNI

Use this reference when rendering charts, choosing installation profiles, or
operating node-level traffic capture. Keep base, istiod, gateway, ztunnel, and
CNI values scoped to the chart that owns them.

## Profiles and platform selection

- (`1.25.0`) `platform` and `profile` accept local and global Helm forms, such
  as `--set platform=foo` and `--set global.platform=foo`.
- (`1.25.0`) Ambient installation on GKE should explicitly use
  `--set global.platform=gke` with Helm or
  `--set values.global.platform=gke` with `istioctl`. This replaces CNI
  chart auto-detection based on Kubernetes version.
- (`1.26.0`) `global.platform=gke` creates required `ResourceQuota` resources
  and selects the appropriate `cniBinDir`. `istioctl` automatically enables the
  setting when it detects GKE.
- (`1.28.0`) Persona-based installs use `global.resourceScope=namespace` or
  `global.resourceScope=cluster` to render only that resource scope. An unset
  value renders both. The ztunnel chart uses top-level `resourceScope` instead.
- (`1.30.0`) The default Istio image registry is `registry.istio.io`; mirror or
  allow that registry explicitly where image policy requires it.

## Chart rendering and resource ownership

- (`1.25.0`) Installation configuration can set `PodDisruptionBudget`
  `maxUnavailable`.
- (`1.25.0`) Sidecar injection configuration errors are returned to the caller
  instead of being logged while processing continues with bad configuration.
- (`1.26.0`) `replicaCount=0` in the `istio/gateway` chart now emits
  `replicas: 0` rather than omitting the field.
- (`1.28.0`) Set `global.networkPolicy.enabled=true` for chart-managed default
  `NetworkPolicy` objects covering istiod and gateways.
- (`1.29.0`) Those default policies also cover istio-cni.
- (`upgrade-1.29`) The base chart no longer owns RBAC and service-account
  resources duplicated in the istiod chart. Account for the renamed objects
  and new revision/release-namespace suffixing described in
  [upgrades-and-migrations.md](upgrades-and-migrations.md).
- (`upgrade-1.30`) `taint.enabled` in the istiod chart automatically configures
  `PILOT_ENABLE_NODE_UNTAINT_CONTROLLERS`; do not separately inject the
  environment variable.
- (`1.30.0`) `networkGatewayPorts` chart values override ports on the network
  gateway `Service`.
- (`1.30.0`) Charts support Helm 4 server-side apply and avoid ownership of
  `failurePolicy` during upgrades. When piping `helm template` output to
  server-side apply, set `base.validationFailurePolicy: Fail`.
- (`1.30.0`) `global.enableReaderRBAC` defaults to `true` and controls the
  remote-secret reader service account, `ClusterRole`, and
  `ClusterRoleBinding`. Set it to `false` on both base and istiod to disable the
  resources, because ownership is split across the charts.

## Pod security and kernel integration

- (`1.25.0`) `istio-cni-node` has `DAC_OVERRIDE` and an unconfined AppArmor
  annotation, restoring access needed after the privileged security context was
  removed.
- (`upgrade-1.28`) Configure `RuntimeDefault` seccomp for the validation and
  proxy containers through global proxy values:

  ```yaml
  global:
    proxy:
      seccompProfile:
        type: RuntimeDefault
  ```

- (`1.30.0`) `useAppArmorAnnotation` defaults to `true` in the istio-cni chart,
  retaining the deprecated annotation representation. Set it to `false` to
  render `securityContext.appArmorProfile`.
- (`1.30.0`) Pods with Kubernetes user namespaces (`hostUsers: false`) work
  with istio-cni when the operating system supplies `nsenter`.
- (`upgrade-1.30`) Istio-created CNI configuration uses mode `0600` by default.
  `values.cni.env.CNI_CONF_GROUP_READ=true` requests `0640` for group-readable
  tooling.

## Host networking and DNS

- (`1.25.0`) When istio-cni uses `hostNetwork: true`, its pod uses
  `dnsPolicy: ClusterFirstWithHostNet`.
- (`1.26.0`) The CNI agent no longer requires `hostNetwork`; it enters the host
  network namespace dynamically when needed. Temporarily restore the previous
  behavior with the chart field `ambient.shareHostNetworkNamespace`.
- (`1.30.0`) The ztunnel chart exposes `dnsPolicy` and `dnsConfig` for custom pod
  DNS environments.
- (`1.30.0`) On EKS with Security Groups for Pods, istio-cni detects branch-ENI
  pods and sends kubelet probes through the veth pair rather than the VPC
  fabric. Enabled-by-default `AMBIENT_ENABLE_AWS_BRANCH_ENI_PROBE` controls the
  behavior.

## Capture backends and interface routing

- (`1.25.0`) Replace `traffic.sidecar.istio.io/kubevirtInterfaces` with
  `istio.io/reroute-virtual-interfaces`. Supply a comma-separated interface
  list; inbound traffic on those interfaces is treated as outbound in ambient
  and sidecar modes.
- (`1.27.0`) Enable native nftables for sidecar pod and Service redirection with
  `--set values.global.nativeNftables=true`.
- (`1.28.0`) The same `values.global.nativeNftables=true` setting enables native
  nftables in ambient mode.
- (`1.28.0`) `FORCE_IPTABLES_BINARY` bypasses backend detection and selects a
  specific iptables binary.
- (`upgrade-1.25`) TCP and UDP DNS traffic both honor pod exclusions including
  `traffic.sidecar.istio.io/excludeOutboundIPRanges` and
  `traffic.sidecar.istio.io/excludeOutboundPorts`; UDP DNS previously bypassed
  them.

## CNI startup, enrollment, and availability

- (`upgrade-1.25`) Startup reconciliation can inspect previously enrolled
  ambient pods and repair differing in-pod iptables rules. It was disabled by
  default in 1.25 and could be enabled with:

  ```bash
  helm install cni --set ambient.reconcileIptablesOnStartup=true
  istioctl install --set values.cni.ambient.reconcileIptablesOnStartup=true
  ```

- (`upgrade-1.29`) Reconciliation of ambient iptables or nftables rules is now
  enabled by default. Disable it with
  `cni.ambient.reconcileIptablesOnStartup=false`.
- (`1.25.0`) Safe restart and upgrade handling for the
  `system-node-critical` istio-cni DaemonSet is enabled by default. It blocks
  new pods on a node while the agent restarts. Set
  `AMBIENT_DISABLE_SAFE_UPGRADE=true` in istio-cni to turn it off.
- (`1.27.0`) `cni.istioOwnedCNIConfig=true` creates an Istio-owned conflist
  combining the primary CNI configuration with Istio's plugin, avoiding mesh
  bypass if the CNI DaemonSet is absent during node startup. Both ambient and
  chained CNI must be enabled. The default file is `02-istio-cni.conflist`; a
  custom `cni.istioOwnedCNIConfigFilename` must have higher lexicographical
  priority than the primary CNI file.
- (`1.29.0`) `ambient.enableAmbientDetectionRetry` retries transient ambient
  enrollment detection failures and is disabled by default.
- (`upgrade-1.30`) CNI agent enforcement of `excludeNamespaces` un-enrolls
  existing ambient pods and prevents new enrollment in excluded namespaces.
- (`1.29.0`) istio-cni `terminationGracePeriodSeconds` is configurable and now
  defaults to 30 seconds rather than 5 seconds.

## Gateways, revisions, and injected pods

- (`1.25.0`) Istio-shipped gateways carry ambient dataplane exclusion labels,
  preventing accidental enrollment when installed outside `istio-system`.
- (`upgrade-1.27`) Eligible pods use native sidecars by default, so
  `istio-proxy` is an init container. Verify webhook and controller handling.
- (`1.28.0`) Waypoint Deployments use Kubernetes' default
  `terminationGracePeriodSeconds` of 30 seconds instead of a hard-coded 2.
- (`1.28.0`) Revision tags created with
  `istioctl tag set <tag> --revision <rev>` or Helm `revisionTags` also create a
  cluster-IP `Service` labeled `istio.io/tag`, alongside the mutating webhook
  representation.
- (`1.28.0`) If `--revision` is omitted, istioctl commands use the revision
  assigned by `istioctl tag set default`.


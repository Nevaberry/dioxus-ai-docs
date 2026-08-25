# Nodes, Runtimes, and Kubelet

## Cgroups, CPU, memory, and runtime support

### Manual cgroup-driver selection is deprecated (1.34-guide)

Kubelet should discover the driver through CRI. `cgroupDriver` and
`--cgroup-driver` are deprecated. Kubernetes 1.35 is the final release
supporting containerd 1.x; use `kubelet_cri_losing_support` to identify nodes
needing a runtime upgrade.

### cgroup v1 nodes cannot run kubelet (1.35-guide)

Kubelet fails to start on Linux without cgroup v2.

### CPU Manager adds stricter reservation controls (1.33.0)

Static-policy `strict-cpu-reservation` reserves `reservedSystemCPUs` exclusively
for daemons and interrupts. Guaranteed containers with exclusive integer CPUs
run without CFS quota; set default-on `DisableCPUQuotaWithExclusiveCPUs=false`
to restore quota.

### Topology Manager can support more NUMA nodes (1.35-guide)

Stable `max-allowable-numa-nodes` lifts the old eight-NUMA limit, though affinity
calculation can degrade as NUMA count grows.

### Kubelet exports cgroup v2 pressure metrics (1.36-guide)

Stable PSI support exposes CPU, memory, and I/O stall pressure.

### Memory QoS uses tiered cgroup v2 protection (1.36-guide)

Beta Memory QoS refines `memory.high` and `memory.min`, with metrics, livelock
safeguards, and operator tunables for cgroup v2 memory protection.

### Cgroup CPU-priority conversion changed (project-news)

The cgroup v1 CPU-shares to cgroup v2 CPU-weight conversion uses an improved
formula, changing CPU priority for affected workloads.

## User namespaces and operating systems

### Pod user namespaces are beta and enabled by default (1.33-guide)

Linux Pods opt in with `hostUsers: false`. They need containerd 2.0+ or CRI-O,
idmapped-mount support for root and every volume filesystem, and non-overlapping
host ID ranges. NFS is unsupported; tmpfs Secret, ConfigMap, projected, and
downward-API volumes need Linux 6.3.

### Kubelet user-namespace ranges are configurable (1.33.0)

`KubeletConfiguration.subidsPerPod` sizes each Pod's subordinate-ID range.

### User-namespaced Pods cannot use block devices (1.34.0)

Pods with `hostUsers: false` are rejected when they declare `volumeDevices`.

### Host-network Pods can use user namespaces (1.35.0)

Default-off alpha `UserNamespacesHostNetworkSupport` permits Linux Pods to
combine `hostNetwork` and a user namespace.

## Kubelet configuration and startup

### Kubelet eviction settings can inherit missing defaults (1.33.0)

Set `mergeDefaultEvictionSettings: true` so explicitly configured hard/soft
eviction, grace period, and minimum-reclaim signals override defaults while
unspecified signals retain their defaults.

### Kubelet drops legacy configuration (1.34.0)

Remove `--cloud-config` and `--register-schedulable` before upgrade.
`StreamingConnectionIdleTimeout` is deprecated.

### Remove kubelet's sandbox-image flag before upgrading (1.35.0)

`--pod-infra-container-image` is removed and prevents startup. Kubeadm attempts
to remove it from generated flags, but custom `extraArgs` require cleanup.

### The cgroup-v1 startup block has an explicit override (1.35.0)

The compatibility path requires both ignoring kubeadm `SystemVerification` and
setting `failCgroupV1: false`; it is not a migration target.

### Kubelet configuration-flag removal moves to 1.38 (1.34.10)

Deprecated kubelet configuration flags and fallback behavior remain through
1.37 to align with containerd 1.7 support. Remove reliance before 1.38.

## Node state and capability discovery

### Pods receive selected Node topology labels (1.33.0)

At binding, Kubernetes copies `topology.k8s.io/zone`,
`topology.k8s.io/region`, and `kubernetes.io/hostname` to the Pod, enabling
downward-API access without Node read permission.

### The node PodResources API lists only active Pods (1.34.0)

Inactive Pods are excluded by default. Disable
`KubeletPodResourcesListUseActivePods` only for temporary compatibility.

### Nodes can declare feature compatibility (1.35-guide)

Alpha `Node.status.declaredFeatures` lets schedulers, admission, and extensions
keep feature-dependent Pods off incompatible nodes during skewed upgrades.

### Strict supplemental groups expose support and identity (1.35-guide)

GA strict groups need containerd 2.0+ or CRI-O 1.31+ and advertise support at
`Node.status.features.supplementalGroupsPolicy`. Kubelet reports initial UID,
GID, and groups in `status.containerStatuses[*].user.linux`; privileged
processes can later change identity.

### Kubelet restarts preserve Pod readiness (1.35-guide)

After restart or upgrade, kubelet restores existing container runtime state
instead of transiently marking healthy Pods NotReady.

### Pod sandbox readiness is reported earlier (1.36.0)

`PodReadyToStartContainers=True` is set immediately after sandbox creation, not
after image pulling. Do not treat it as proof images are available.

### Node Readiness Controller accounts for infrastructure dependencies (project-news)

The controller extends binary Node Ready semantics for environments whose
workload suitability also depends on network, storage, or other infrastructure
agents.

## CRI compatibility

### CRI `KeyValue.value` JSON encoding returns to its pre-1.34 form (1.34.10)

The `cri-api` JSON form of `KeyValue.value` reverts the encoding introduced by
earlier 1.34 patch releases. JSON-serializing integrations should expect the
pre-1.34 representation after upgrading to 1.34.10.

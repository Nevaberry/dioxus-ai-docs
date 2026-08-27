# Nodes, Runtimes, and Kubelet

Use this reference for cgroups, runtimes, kubelet startup and configuration,
node capabilities, resource managers, pressure, and node-local APIs.

## Startup and runtime compatibility

### Require cgroup v2 (1.35-guide, 1.35.0)

Linux kubelet does not run on cgroup v1. Kubeadm's `SystemVerification`
preflight rejects it. A temporary compatibility start requires both ignoring
that error and setting `failCgroupV1: false` in the
`kube-system/kubelet-config` ConfigMap; migrate the host to cgroup v2 instead.

### Remove the sandbox-image flag (1.35.0)

Kubelet rejects removed `--pod-infra-container-image` and fails startup.
Kubeadm may remove it from `/var/lib/kubelet/kubeadm-flags.env`, but operators
must clean up service files and user `extraArgs`.

### Let CRI select the cgroup driver (1.34-guide)

Kubelet should discover its cgroup driver from CRI. The `cgroupDriver`
configuration field and `--cgroup-driver` flag are deprecated. Kubernetes 1.35
was the final release supporting containerd 1.x; use
`kubelet_cri_losing_support` to identify runtime upgrades.

### Plan configuration-flag removal for 1.38 (1.34.10)

Removal of deprecated kubelet configuration flags and their fallback behavior
was deferred from 1.37 to 1.38 to align with containerd 1.7 support. Remove
reliance on the fallback before 1.38.

### Remove legacy kubelet configuration (1.34.0)

Kubelet no longer accepts `--cloud-config` or `--register-schedulable`.
`StreamingConnectionIdleTimeout` is deprecated.

## User namespaces and platform behavior

### Validate every user-namespace prerequisite (1.33-guide)

Linux Pods opt in with `spec.hostUsers: false`. Use containerd 2.0 or newer, or
compatible CRI-O, and ensure idmapped-mount support for the root filesystem and
every volume filesystem. NFS is unsupported. Tmpfs Secret, ConfigMap,
projected, and downward-API volumes need Linux 6.3. Each Pod receives a
non-overlapping host ID range.

```yaml
spec:
  hostUsers: false
```

Set `KubeletConfiguration.subidsPerPod` to size each subordinate-ID range
(1.33.0). User-namespaced Pods cannot declare `volumeDevices` (1.34.0).
Alpha default-off `UserNamespacesHostNetworkSupport` permits combining a Linux
user namespace with `hostNetwork` (1.35.0).

Windows no longer supports the removed alpha Pod `hostNetwork` behavior;
HostProcess remains the host-level alternative (1.33-guide).

### Honor Windows graceful shutdown (1.34-guide)

Windows graceful node shutdown is beta and default-on. Kubelet observes the
Windows pre-shutdown notification and runs normal Pod hooks and grace periods.

## Restart and eviction behavior

### Configure shorter crash-loop backoff (1.33.0)

`ReduceDefaultCrashLoopBackOffDecay` changes restart delay to 1 second initially
and 60 seconds maximum. If `KubeletCrashLoopBackOffMax` also sets a node maximum,
apply its conflict rules to derive the effective values.

### Merge eviction defaults explicitly (1.33.0)

Set `mergeDefaultEvictionSettings: true` so configured values override defaults
while omitted signals retain defaults across `evictionHard`, `evictionSoft`,
`evictionSoftGracePeriod`, and `evictionMinimumReclaim`.

```yaml
mergeDefaultEvictionSettings: true
```

### Preserve readiness across kubelet restarts (1.35-guide)

Kubelet restores existing container state from the runtime after restart or
upgrade rather than transiently marking healthy Pods NotReady.

### Interpret sandbox readiness correctly (1.36.0)

`PodReadyToStartContainers=True` is set after sandbox creation, before image
pulling. Do not use it as evidence that images are present or containers can
start immediately.

## CPU, memory, and topology management

### Reserve system CPUs strictly (1.33.0)

The static CPU Manager `strict-cpu-reservation` option reserves
`reservedSystemCPUs` exclusively for daemons and interrupts. Guaranteed
containers with exclusive whole CPUs run without CFS quota; set default-on
`DisableCPUQuotaWithExclusiveCPUs=false` only when quota enforcement is
required.

### Support large NUMA systems deliberately (1.35-guide)

The stable Topology Manager `max-allowable-numa-nodes` policy option lifts the
old eight-node limit, but affinity calculation may become expensive as NUMA
count grows.

### Use Memory QoS on cgroup v2 (1.36-guide)

Beta Memory QoS programs tiered `memory.high` and `memory.min`, with metrics,
livelock safeguards, and tunables for protection. Validate the operator values
under real pressure.

### Account for changed CPU-priority conversion

Cgroup v1 CPU shares now convert to cgroup v2 CPU weight with an improved
formula. Mixed or migrated environments may observe a different relative CPU
priority for the same workload settings.

## Node capabilities and local APIs

### Publish node feature compatibility (1.35-guide)

Alpha node declarations expose supported features in
`Node.status.declaredFeatures`. Schedulers, admission, and extensions can keep
workloads requiring newer behavior away from incompatible nodes during skewed
upgrades.

### List only active PodResources (1.34.0)

The node PodResources endpoint omits inactive Pods by default. Disable
`KubeletPodResourcesListUseActivePods` only as a temporary compatibility step.

### Use fine-grained kubelet authorization (1.36-guide)

Stable `KubeletFineGrainedAuthz` lets monitoring clients receive narrow kubelet
HTTPS permissions rather than broad `nodes/proxy` access.

### Enable node log queries explicitly (1.36-guide)

`NodeLogQuery` is stable and its gate enabled, but kubelet still requires
`enableSystemLogQuery: true`. Queryable node services must write below
`/var/log`.

```yaml
enableSystemLogQuery: true
```

### Read cgroup v2 pressure metrics (1.36-guide)

Stable PSI metrics expose CPU, memory, and I/O stall time. Use them to
distinguish high utilization from workloads actively blocked on resources.

### Model infrastructure-dependent readiness

The Node Readiness Controller augments binary Node `Ready` for environments
where suitability depends on network, storage, or other infrastructure agents.
Integrations should consume those dependency signals before placing workloads.

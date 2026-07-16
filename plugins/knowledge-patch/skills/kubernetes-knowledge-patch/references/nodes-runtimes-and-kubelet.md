# Nodes, Runtimes, and Kubelet

Use this reference for kubelet and runtime configuration, node capabilities, cgroup behavior, lifecycle, pressure, and node-local APIs.

Entries are grouped by task; the parenthetical identifier is the source batch.

## Cgroup CPU-priority conversion changed (project-news)

Conversion from cgroup v1 CPU shares to cgroup v2 CPU weight now uses an improved formula, changing how CPU priority is allocated to Kubernetes workloads on affected systems.

## cgroup v1 nodes cannot run kubelet (1.35-guide)

Kubernetes 1.35 removes cgroup v1 support; kubelet fails to start on Linux systems that do not have cgroup v2 enabled.

## CPU Manager adds stricter reservation controls (1.33.0)

The static policy's `strict-cpu-reservation` option reserves `reservedSystemCPUs` exclusively for system daemons and interrupts. Guaranteed containers with exclusive integer CPU assignments now run without CFS quota; set the default-on `DisableCPUQuotaWithExclusiveCPUs` gate to `false` to restore quota enforcement if needed.

## Kubelet drops legacy configuration (1.34.0)

The kubelet no longer accepts `--cloud-config` or `--register-schedulable`; remove them from service definitions before upgrading. `StreamingConnectionIdleTimeout` in kubelet configuration is also deprecated.

## Kubelet eviction settings can inherit missing defaults (1.33.0)

Set `mergeDefaultEvictionSettings` so explicitly configured `evictionHard`, `evictionSoft`, `evictionSoftGracePeriod`, and `evictionMinimumReclaim` signals override defaults while unspecified signals retain their defaults.

```yaml
mergeDefaultEvictionSettings: true
```

## Kubelet exports cgroup v2 pressure metrics (1.36-guide)

Stable Pressure Stall Information support reports CPU, memory, and I/O contention, allowing operators and autoscalers to distinguish ordinary utilization from workloads that are actively stalled.

## Kubelet restarts preserve Pod readiness (1.35-guide)

After a kubelet restart or upgrade, kubelet restores existing container state from the runtime instead of transiently marking healthy Pods `NotReady`, avoiding needless removal from load balancers.

## Kubelet user-namespace ranges are configurable (1.33.0)

`KubeletConfiguration` gains `subidsPerPod`, allowing operators to size the subordinate-ID range assigned per user-namespaced Pod.

## Manual cgroup-driver selection is deprecated (1.34-guide)

Kubelet should discover its cgroup driver from the CRI; both the `cgroupDriver` configuration field and `--cgroup-driver` are deprecated for eventual removal no earlier than 1.36. Kubernetes 1.35 is also the final release supporting containerd 1.x; `kubelet_cri_losing_support` identifies nodes that need a runtime upgrade.

## Memory QoS uses tiered cgroup v2 protection (1.36-guide)

The beta Memory QoS behavior refines how kubelet programs `memory.high` and `memory.min`, adding metrics, livelock safeguards, and operator tunables for memory protection on cgroup v2 nodes.

## Node log queries require an explicit kubelet option (1.36-guide)

`NodeLogQuery` is GA and its feature gate is enabled by default, but kubelet must also set `enableSystemLogQuery: true`; queried node services must write beneath `/var/log`.

```yaml
enableSystemLogQuery: true
```

## Node Readiness Controller accounts for infrastructure dependencies (project-news)

The Node Readiness Controller extends the usual binary node `Ready` model for environments where workload suitability also depends on infrastructure such as network and storage agents.

## Nodes can declare feature compatibility (1.35-guide)

The alpha node-declaration framework publishes supported Kubernetes features in `Node.status.declaredFeatures`, allowing schedulers, admission controllers, and extensions to keep Pods that require newer features off incompatible nodes during version-skewed upgrades.

## Pod sandbox readiness is reported earlier (1.36.0)

Kubelet sets `PodReadyToStartContainers=True` immediately after sandbox creation rather than after image pulling, so consumers must not treat the condition as proof that images are already available.

## Remove kubelet's sandbox-image flag before upgrading (1.35.0)

The `--pod-infra-container-image` flag is removed and prevents kubelet startup if it remains configured. Kubeadm upgrade attempts to remove it from `/var/lib/kubelet/kubeadm-flags.env`, but user-supplied `extraArgs` must be cleaned up manually.

## The cgroup-v1 startup block has an explicit override (1.35.0)

Kubeadm's `SystemVerification` check errors for a 1.35 kubelet on cgroup v1; proceeding requires both ignoring that preflight error and setting `failCgroupV1: false` in the `kube-system/kubelet-config` ConfigMap.

## The node PodResources API lists only active Pods (1.34.0)

The node-local PodResources endpoint now excludes inactive Pods by default; disable `KubeletPodResourcesListUseActivePods` to temporarily restore the older listing behavior.

## Topology Manager can support more NUMA nodes (1.35-guide)

The stable `max-allowable-numa-nodes` Topology Manager policy option lifts the historical limit of eight NUMA nodes for large hosts, although affinity calculation can perform poorly as the NUMA count grows.

## WebSocket streaming can reach kubelet directly (1.36.0)

The beta, default-on `ExtendWebSocketsToKubelet` behavior sends WebSocket exec, attach, and port-forward requests directly to kubelets that advertise support through node-declared features, instead of translating or tunneling them at the API server.

## Windows nodes gain lifecycle and networking graduations (1.34-guide)

Graceful node shutdown is beta and default-on for Windows kubelets, which honor normal Pod hooks and grace periods after a Windows pre-shutdown notification. Windows kube-proxy Direct Service Return and overlay-network support are stable.

## Windows Pods no longer support `hostNetwork` (1.33-guide)

The alpha Windows host-network implementation is removed in 1.33; Windows HostProcess containers are unaffected and remain the option when host networking plus host-level access is required.


# Workloads, Lifecycle, and Scheduling

Use this reference for Pods, containers, Jobs, controllers, autoscaling, resource management, scheduler behavior, and workload APIs.

Entries are grouped by task; the parenthetical identifier is the source batch.

## `nominatedNodeName` can advertise intended placement (1.34-guide)

With `NominatedNodeNameForExpectation`, the scheduler may set `status.nominatedNodeName` for an intended binding, not only for preemption, so autoscalers and other components can avoid disrupting a node with a pending placement.

## A restart rule can restart every container (1.35.0)

The alpha `RestartAllContainersOnContainerExit` gate makes a matching restart-policy rule on a source container restart all containers when that source exits.

## Agent Sandbox targets AI agent workloads (project-news)

Agent Sandbox provides a way to run AI agents on Kubernetes as these workloads move beyond transient, stateless execution.

## Container restart rules are default-on beta (1.35-guide)

Per-container `restartPolicy` and exit-code-based `restartPolicyRules` are now available by default for regular and init containers.

## Containers can have exit-code-specific restart rules (1.34-guide)

With `ContainerRestartRules`, each regular or init container can set its own `restartPolicy` and a `restartPolicyRules` list that overrides that policy for selected exit codes, instead of every container being governed only by the Pod-level policy.

## Containers can import runtime-generated environment files (1.34-guide)

With the alpha `EnvFiles` gate, an earlier container can write environment values to a file and a later container can import them at startup, avoiding an entrypoint wrapper for values produced during Pod initialization.

## Crash-loop restart delays can be shortened (1.33.0)

Enabling `ReduceDefaultCrashLoopBackOffDecay` changes container restart backoff to a 1-second initial delay and a 60-second maximum; if `KubeletCrashLoopBackOffMax` also configures a per-node maximum, its conflict-resolution rules determine the effective values.

```text
--feature-gates=ReduceDefaultCrashLoopBackOffDecay=true
```

## Deployments can report terminating replicas (1.33.0)

With `DeploymentPodReplacementPolicy`, Deployments and ReplicaSets expose `.status.terminatingReplicas`, allowing controllers and rollout tooling to distinguish terminating Pods from other replica counts.

## Downward resource references use Pod-level limits (1.34.0)

For `resourceFieldRef`, an absent container-level limit now falls back to the Pod-level limit before falling back to node allocatable resources.

## EnvFiles values must be single-quoted (1.35.0)

The EnvFiles feature is beta and enabled by default, but its syntax is now restricted so every value is wrapped in single quotes.

```text
TOKEN='value'
```

## Environment variable names accept nearly all printable ASCII (1.34-guide)

Pod `env` entries and keys imported from ConfigMaps or Secrets with `envFrom` may contain any printable ASCII character except `=`, including names such as .NET configuration keys containing `:`.

## HPA tolerance is default-on beta (1.35-guide)

HorizontalPodAutoscalers can set a custom per-resource tolerance in `behavior`, such as `0.05` for a five-percent window, instead of relying only on the global ten-percent tolerance.

## HPAs can override the global tolerance (1.33.0)

The alpha `HPAConfigurableTolerance` gate adds a per-HorizontalPodAutoscaler `tolerance` field, allowing an HPA to override the cluster-wide scaling tolerance.

## In-place Pod resize is beta and default-on (1.33-guide)

CPU and memory changes for a running Pod must now go through the `resize` subresource; `spec.containers[*].resources` is desired state while `status.containerStatuses[*].resources` is actual state, and native sidecars can also be resized. The old `status.resize` is deprecated in favor of `PodResizePending` (`Deferred` or `Infeasible`) and `PodResizeInProgress` conditions.

```console
kubectl edit pod <pod-name> --subresource resize
```

## In-place Pod resize reaches GA with new integrations (1.35-guide)

VPA's `InPlaceOrRecreate` update mode is beta, while resizing Pod-level resources is a separate alpha capability. In-place resize still applies only to CPU and memory and is prohibited with swap or the static CPU and Memory Manager policies.

## In-place resize changes memory and priority behavior (1.34.0)

A memory limit may now be decreased with `resizePolicy[*].restartPolicy: NotRequired`; kubelet makes a best-effort check against current usage to avoid an immediate OOM kill. When resources cannot satisfy all pending resizes, requests are prioritized by PriorityClass and QoS, while Guaranteed Pods under the static Memory Manager policy require the default-off `InPlacePodVerticalScalingExclusiveMemory` gate.

## In-place resize has stricter mutation rules (1.33.0)

A memory limit cannot be reduced unless that container's memory resize policy is `RestartContainer`, and `resizePolicy` itself is no longer mutable. Swap-enabled containers are likewise ineligible for in-place resize without that memory restart policy.

## Indexed Job success policies are stable (1.33-guide)

An Indexed Job can finish when any `successPolicy` rule's `succeededIndexes`, `succeededCount`, or combination is satisfied, terminating remaining Pods. The controller first adds `SuccessCriteriaMet`, then adds `Complete` after cleanup.

## Jobs can delegate reconciliation (1.35-guide)

The stable `Job.spec.managedBy` field lets an external controller own Job status synchronization while the built-in Job controller stands aside. It delegates reconciliation only; it does not carry controller parameters or alter CronJob concurrency behavior.

## Jobs can wait for a terminated Pod before replacing it (1.34-guide)

The stable `podReplacementPolicy: Failed` setting prevents a Job from creating a replacement while the old Pod is merely terminating, avoiding overlapping Pods for the same work or completion index.

```yaml
spec:
  podReplacementPolicy: Failed
```

## Native gang scheduling begins as alpha (1.35-guide)

The new Workload API and PodGroup concept provide all-or-nothing scheduling for interdependent Pods, preventing part of a parallel workload from consuming resources while the rest cannot be placed.

## Native sidecars are stable (1.33-guide)

Kubernetes 1.33 makes native sidecars stable and enabled by default; `initContainers` entries with container-level `restartPolicy: Always` retain init ordering, remain running with the application, stop afterward in reverse order, and do not block Job completion.

## Native sidecars have a one-release compatibility gate (1.33.0)

`LegacySidecarContainers` restores the pre-native-sidecar code path when explicitly enabled; the default-off escape hatch exists only in 1.33 and is removed in 1.34.

## Per-index Job retry limits are stable (1.33-guide)

Indexed Jobs can use `backoffLimitPerIndex` so one fast-failing index does not consume the entire Job retry budget; `maxFailedIndexes` caps total failed indexes, a Pod failure policy can short-circuit retries with `FailIndex`, and exhausted indexes appear in `status.failedIndexes`.

## Pod observed generations are beta and default-on (1.34.0)

Kubernetes now populates both `status.observedGeneration` and `status.conditions[*].observedGeneration`, allowing clients to detect an individually stale Pod condition as well as stale top-level status.

## Pod status can track observed generations (1.33-guide)

The alpha Pod generation feature makes `metadata.generation` meaningful for Pods and adds `status.observedGeneration`, letting clients distinguish status for the current spec from stale status.

## Pod-level resource management expands (1.36.0)

`InPlacePodLevelResourcesVerticalScaling` is beta and enabled by default, and the Topology, CPU, and Memory managers now act on `spec.resources`; running non-sidecar init containers can also be resized. Requests that exceed node capacity or target an unsupported OS fail admission, and non-sidecar init containers cannot use the `RestartContainer` resize policy.

## Pod-level resources are beta and work with HPA (1.34-guide)

Pod-wide requests and limits graduate to beta and can be consumed by HorizontalPodAutoscaler, allowing a multi-container Pod to expose one shared resource budget to scheduling and autoscaling.

## Pod-level resources have platform and topology limits (1.34.0)

Pods with `spec.resources` are rejected when `spec.os.name` is `windows`. On Linux, Pod-level resources do not produce CPU or memory alignment or hints from the CPU Manager, Memory Manager, or Topology Manager.

## Pod-level resources support huge pages (1.33.0)

With `PodLevelResources` enabled, huge-page requests and limits can now be declared in the Pod-level `spec.resources` field rather than only on individual containers.

```yaml
spec:
  resources:
    limits:
      hugepages-2Mi: 1Gi
    requests:
      hugepages-2Mi: 1Gi
```

## PodGroups can be scheduled atomically (1.36-guide)

The alpha Workload Aware Scheduling additions revise the Workload API and decouple the PodGroup API; a PodGroup scheduling cycle now binds every Pod in the group together or binds none, rather than only checking that a minimum count is schedulable.

## Pods can override their hostname (1.34.0)

With the `HostnameOverride` feature gate, `PodSpec.hostnameOverride` accepts any RFC 1123 DNS subdomain as the Pod hostname.

```yaml
spec:
  hostnameOverride: app.example
```

## Pods can select a container stop signal (1.33-guide)

With the alpha `ContainerStopSignals` gate, `lifecycle.stopSignal` overrides the image's stop signal or runtime default; the Pod must also declare `spec.os.name`.

```yaml
spec:
  os:
    name: linux
  containers:
  - name: app
    image: example/app
    lifecycle:
      stopSignal: SIGUSR1
```

## Pods receive selected Node topology labels (1.33.0)

At binding time Kubernetes copies `topology.k8s.io/zone`, `topology.k8s.io/region`, and `kubernetes.io/hostname` from the Node onto the Pod, so workloads can consume topology through the downward API without permission to read Node objects.

## Restart-all rules are default-on beta (1.36.0)

`RestartAllContainersOnContainerExits` is now beta and enabled by default, making restart-policy rules that restart every container available without opting into the former alpha gate.

## Scheduler failures clear `nominatedNodeName` (1.35.0)

The scheduler now clears a Pod's `nominatedNodeName` after scheduling or binding failure. External components such as autoscalers must not overwrite this scheduler-owned field.

## Scheduler framework types move to a staging module (1.34.0)

Out-of-tree scheduler plugins must move framework types such as `Status`, `CycleState`, `ClusterEvent`, and `NodeInfo` from `k8s.io/kubernetes/pkg/scheduler/framework` to `k8s.io/kube-scheduler/framework`; `CycleState` is now an interface and some moved types require getter and setter methods instead of direct field access.

## Scheduler plugin contracts changed (1.36.0)

`PreBindPreFlight` now returns `PreBindPreFlightResult`; return `AllowParallel: true` to opt into parallel PreBind execution, while `nil` preserves sequential execution. Custom plugins using `Handle.WorkloadManager` must also rename `PodGroupInfo` to `PodGroupState`.

## Scheduler plugin contracts gain preflight inputs (1.34.0)

PreFilter plugins now accept the `NodeInfo` list through their arguments, and every `PreBindPlugin` must implement `PreBindPreFlight`. Returning `Skip` suppresses that plugin's `PreBind` call, while a successful preflight can cause the scheduler to publish the intended node through `nominatedNodeName`.

## StatefulSet `maxUnavailable` is disabled by default (1.36.0)

The `MaxUnavailableStatefulSet` gate is off by default in 1.36 because of a regression in parallel Pod management; clusters relying on rolling-update `maxUnavailable` must explicitly enable it.

## StatefulSet rollouts can tolerate more unavailability (1.35-guide)

The beta, default-on `.spec.updateStrategy.rollingUpdate.maxUnavailable` accepts a positive count or percentage and defaults to `1`; it is most useful with parallel Pod management.

```yaml
spec:
  podManagementPolicy: Parallel
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 10%
```

## Static Pods cannot reference API objects (1.34.0)

Kubelet now denies static Pods that reference API objects, explicitly including arbitrary ResourceClaims, rather than letting the workload run after mirror-Pod creation fails.

## Suspended Job resource edits are beta and default-on (1.36-guide)

`MutablePodResourcesForSuspendedJobs` now permits CPU, memory, GPU, and other extended-resource request or limit changes while a Job is suspended, or after its Pods have terminated during suspension; active Pods remain immutable.

## Suspended Jobs accept scheduling edits by default (1.36.0)

`MutableSchedulingDirectivesForSuspendedJobs` is enabled by default, allowing changes to `nodeSelector`, tolerations, and node affinity while a Job is suspended, including before the controller has recorded the `JobSuspended` condition.

## Suspended Jobs can change container resources (1.35-guide)

With `MutablePodResourcesForSuspendedJobs`, a suspended Job's Pod template can update CPU and memory requests or limits before the Job resumes, preserving the Job identity and status during correction.

## Suspended Jobs can change scheduling directives (1.35.0)

The alpha, default-off `MutableSchedulingDirectivesForSuspendedJobs` gate allows scheduling-directive edits while a Job is suspended and clears `status.startTime` when the Job is suspended.

## Tolerations can compare numeric thresholds (1.35-guide)

Alpha numeric comparison operators in Pod tolerations let scheduling policies match threshold-valued taints, such as reliability or service-level tiers, instead of relying only on equality or existence.

## Topology-spread selectors are merged by the API server (1.34.0)

For `topologySpreadConstraints`, kube-apiserver now merges keys selected by `matchLabelKeys` into `labelSelector`, so controllers no longer need to perform that merge. Upgrade 1.32 clusters through 1.33 before 1.34 and ensure Pods created on 1.32 with `matchLabelKeys` have been scheduled; the default-on `MatchLabelKeysInPodTopologySpreadSelectorMerge` gate controls the new behavior.

## Workload scheduling moves to `v1alpha2` (1.36.0)

Workload and PodGroup objects use `scheduling.k8s.io/v1alpha2`, and the `v1alpha1` Workload API is removed. The scheduler also reports a `PodGroupScheduled` condition for successful or unschedulable groups.


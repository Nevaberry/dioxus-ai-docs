# Workloads, Lifecycle, and Scheduling

## Containers, sidecars, and restart behavior

### Native sidecars are stable (1.33-guide)

An `initContainers` entry with container-level `restartPolicy: Always` preserves
init ordering, remains with the application, stops afterward in reverse order,
and does not block Job completion.

### Native sidecars have a one-release compatibility gate (1.33.0)

Default-off `LegacySidecarContainers` restores pre-native-sidecar behavior only
in 1.33; it is removed in 1.34.

### Pods can select a container stop signal (1.33-guide)

Alpha `ContainerStopSignals` lets `lifecycle.stopSignal` override the image or
runtime default; the Pod must declare `spec.os.name`.

### Crash-loop restart delays can be shortened (1.33.0)

`ReduceDefaultCrashLoopBackOffDecay` changes restart backoff to one second
initially and 60 seconds maximum. If `KubeletCrashLoopBackOffMax` also sets a
node maximum, its conflict rules determine effective values.

### Containers can have exit-code-specific restart rules (1.34-guide)

`ContainerRestartRules` gives regular and init containers individual
`restartPolicy` and `restartPolicyRules` overrides for selected exit codes.

### Container restart rules are default-on beta (1.35-guide)

Per-container policies and exit-code rules are available by default.

### A restart rule can restart every container (1.35.0)

Alpha `RestartAllContainersOnContainerExit` lets a matching rule on one source
container restart all containers.

### Restart-all rules are default-on beta (1.36.0)

The later gate name is `RestartAllContainersOnContainerExits`; the behavior is
beta and enabled by default.

### Containers can import runtime-generated environment files (1.34-guide)

Alpha `EnvFiles` lets an earlier container write values that a later container
imports at startup, avoiding an entrypoint wrapper.

### EnvFiles values must be single-quoted (1.35.0)

The feature is beta/default-on and every value must be single-quoted:

```text
TOKEN='value'
```

### Environment variable names accept nearly all printable ASCII (1.34-guide)

Pod `env` names and keys imported with `envFrom` may contain any printable ASCII
except `=`, including .NET-style names containing `:`.

## Pod status, identity, and metadata

### Pod status can track observed generations (1.33-guide)

Alpha Pod generation makes `metadata.generation` meaningful and adds
`status.observedGeneration` for detecting stale status.

### Pod observed generations are beta and default-on (1.34.0)

Kubernetes populates top-level status and
`status.conditions[*].observedGeneration`, allowing condition-level freshness
checks.

### Pods can override their hostname (1.34.0)

With `HostnameOverride`, `PodSpec.hostnameOverride` accepts an RFC 1123 DNS
subdomain.

### Pod DNS search validation is relaxed (1.33.0)

Beta `RelaxedDNSSearchValidation` permits a search domain that is a single dot
or contains an underscore.

### Namespace deletion removes Pods first (1.33.0)

Default-on alpha `OrderedNamespaceDeletion` deletes Pods before other namespaced
resources, affecting finalizer and dependency cleanup order.

### Pod sandbox readiness is reported earlier (1.36.0)

Kubelet sets `PodReadyToStartContainers=True` after sandbox creation, before
image pulling; consumers must not treat it as proof images are present.

## In-place resize and Pod-level resources

### In-place Pod resize is beta and default-on (1.33-guide)

Change CPU and memory through the `resize` subresource. Spec is desired state;
`status.containerStatuses[*].resources` is actual state. Native sidecars are
resizable. Replace deprecated `status.resize` with `PodResizePending`
(`Deferred`/`Infeasible`) and `PodResizeInProgress` conditions.

```console
kubectl edit pod <pod-name> --subresource resize
```

### In-place resize has stricter mutation rules (1.33.0)

At this stage a memory limit reduction or swap-enabled resize requires that
container's memory policy to be `RestartContainer`; `resizePolicy` is immutable.

### In-place resize changes memory and priority behavior (1.34.0)

A memory limit may later decrease with `restartPolicy: NotRequired`; kubelet
best-effort checks current use to avoid immediate OOM. Pending resizes prioritize
by PriorityClass and QoS. Guaranteed Pods under static Memory Manager need
default-off `InPlacePodVerticalScalingExclusiveMemory`.

### In-place Pod resize reaches GA with new integrations (1.35-guide)

VPA `InPlaceOrRecreate` is beta and Pod-level resize is a separate alpha
capability. Resize remains CPU/memory only and is prohibited with swap or static
CPU/Memory Manager policies.

### Pod-level resources support huge pages (1.33.0)

With `PodLevelResources`, huge-page requests and limits may be placed in Pod
`spec.resources`, not only individual containers.

### Pod-level resources are beta and work with HPA (1.34-guide)

Pod-wide requests and limits provide one shared scheduling/autoscaling budget.

### Pod-level resources have platform and topology limits (1.34.0)

Pods with `spec.resources` are rejected on Windows. At this stage on Linux they
do not produce CPU/Memory/Topology Manager alignment or hints.

### Downward resource references use Pod-level limits (1.34.0)

When `resourceFieldRef` finds no container limit, it falls back to the Pod limit
before node allocatable.

### Pod-level resource management expands (1.36.0)

`InPlacePodLevelResourcesVerticalScaling` is beta/default-on; Topology, CPU, and
Memory managers act on `spec.resources`, and running non-sidecar init containers
can resize. Requests exceeding node capacity or using an unsupported OS fail
admission. Non-sidecar init containers cannot use `RestartContainer` resize.

## Autoscaling and controllers

### HPAs can override the global tolerance (1.33.0)

Alpha `HPAConfigurableTolerance` adds per-HPA tolerance.

### HPA tolerance is default-on beta (1.35-guide)

Set per-resource tolerance in HPA `behavior`, such as `0.05`, rather than using
only the global ten-percent window.

### Deployments can report terminating replicas (1.33.0)

With `DeploymentPodReplacementPolicy`, Deployment and ReplicaSet status exposes
`terminatingReplicas` separately.

### StatefulSet rollouts can tolerate more unavailability (1.35-guide)

Default-on beta rolling-update `maxUnavailable` accepts a positive count or
percentage, defaults to one, and is especially useful with parallel management.

### StatefulSet `maxUnavailable` is disabled by default (1.36.0)

Because of a parallel-management regression, `MaxUnavailableStatefulSet` is off
by default in 1.36; clusters relying on it must opt in explicitly.

## Jobs

### Per-index Job retry limits are stable (1.33-guide)

Indexed Jobs use `backoffLimitPerIndex`; `maxFailedIndexes` caps failed indexes,
`FailIndex` short-circuits retries, and `status.failedIndexes` reports exhausted
indexes.

### Indexed Job success policies are stable (1.33-guide)

A Job completes when any `successPolicy` rule's `succeededIndexes`,
`succeededCount`, or combination is met, terminating remaining Pods. The
controller adds `SuccessCriteriaMet`, then `Complete` after cleanup.

### Jobs can wait for a terminated Pod before replacing it (1.34-guide)

Stable `podReplacementPolicy: Failed` prevents creating a replacement while the
old Pod is merely terminating.

### Jobs can delegate reconciliation (1.35-guide)

Stable `Job.spec.managedBy` makes the built-in controller stand aside for an
external controller. It carries no controller parameters and does not change
CronJob concurrency.

### Suspended Jobs can change container resources (1.35-guide)

`MutablePodResourcesForSuspendedJobs` permits CPU and memory request/limit edits
before resume while preserving Job identity and status.

### Suspended Jobs can change scheduling directives (1.35.0)

Default-off alpha `MutableSchedulingDirectivesForSuspendedJobs` permits edits
while suspended and clears `status.startTime` on suspension.

### Suspended Job resource edits are beta and default-on (1.36-guide)

Resource edits now include CPU, memory, GPU, and extended-resource requests or
limits while suspended or after Pods terminate during suspension. Active Pods
remain immutable.

### Suspended Jobs accept scheduling edits by default (1.36.0)

Default-on `MutableSchedulingDirectivesForSuspendedJobs` permits nodeSelector,
toleration, and node-affinity changes, including before `JobSuspended` is
recorded.

## Scheduling framework and topology

### Scheduler framework types move to a staging module (1.34.0)

Out-of-tree plugins import `Status`, `CycleState`, `ClusterEvent`, and `NodeInfo`
from `k8s.io/kube-scheduler/framework`, not the Kubernetes internal package.
`CycleState` is an interface; moved types may require getters/setters instead of
field access.

### Scheduler plugin contracts gain preflight inputs (1.34.0)

PreFilter receives the `NodeInfo` list. Every `PreBindPlugin` implements
`PreBindPreFlight`; `Skip` suppresses its `PreBind`, and success may publish the
intended node in `nominatedNodeName`.

### Scheduler plugin contracts changed (1.36.0)

`PreBindPreFlight` returns `PreBindPreFlightResult`; `AllowParallel: true` opts
into parallel PreBind and `nil` remains sequential. Rename
`Handle.WorkloadManager.PodGroupInfo` to `PodGroupState`.

### `nominatedNodeName` can advertise intended placement (1.34-guide)

With `NominatedNodeNameForExpectation`, the scheduler may set the status field
for intended binding, not just preemption, so autoscalers can avoid disruption.

### Scheduler failures clear `nominatedNodeName` (1.35.0)

Scheduling or binding failure clears the field. External components must not
overwrite this scheduler-owned status.

### Topology-spread selectors are merged by the API server (1.34.0)

Kube-apiserver merges `matchLabelKeys` into a topology constraint's
`labelSelector`. Upgrade 1.32 through 1.33 before 1.34 and ensure affected 1.32
Pods have scheduled. The default-on
`MatchLabelKeysInPodTopologySpreadSelectorMerge` gate controls behavior.

### Tolerations can compare numeric thresholds (1.35-guide)

Alpha numeric comparison operators match threshold-valued taints such as
reliability tiers rather than equality/existence only.

## Gang and workload-aware scheduling

### Native gang scheduling begins as alpha (1.35-guide)

The Workload API and PodGroup concept provide all-or-nothing placement for
interdependent Pods, avoiding partial resource consumption.

### PodGroups can be scheduled atomically (1.36-guide)

The revised Workload API decouples PodGroup. A scheduling cycle binds every Pod
in the group or none, instead of merely checking a minimum schedulable count.

### Workload scheduling moves to `v1alpha2` (1.36.0)

Workload and PodGroup use `scheduling.k8s.io/v1alpha2`; v1alpha1 Workload is
removed. The scheduler reports `PodGroupScheduled` for successful or
unschedulable groups.

### Agent Sandbox targets AI agent workloads (project-news)

Agent Sandbox provides a Kubernetes execution model for agent workloads as they
move beyond transient, stateless execution.

# Workloads, Lifecycle, and Scheduling

Use this reference for Pods, containers, Jobs, workload controllers, resource
management, scheduler integrations, and group scheduling.

## Containers and Pod lifecycle

### Define native sidecars correctly (1.33-guide, 1.33.0)

A native sidecar is an `initContainers` entry with container-level
`restartPolicy: Always`. It preserves init ordering, stays with the application,
stops afterward in reverse order, and does not block Job completion. The
default-off `LegacySidecarContainers` escape hatch existed only in 1.33 and was
removed in 1.34.

### Override the stop signal (1.33-guide)

With `ContainerStopSignals`, set `lifecycle.stopSignal` to override the image or
runtime default, and declare the Pod OS.

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

### Use per-container restart rules (1.34-guide, 1.35-guide)

`ContainerRestartRules` lets regular and init containers set their own
`restartPolicy` and `restartPolicyRules`, overriding that policy for selected
exit codes. The feature is beta, default-on, and applies independently of the
Pod-level policy.

### Restart every container when required (1.35.0, 1.36.0)

The alpha `RestartAllContainersOnContainerExit` behavior let a matching rule on
one source container restart all containers. The beta, default-on feature uses
`RestartAllContainersOnContainerExits`; update feature-gate configuration to
the current name and semantics.

### Import generated environment files (1.34-guide, 1.35.0)

`EnvFiles` lets an earlier container write values that a later container loads
at startup. The beta default-on syntax requires every value to be single
quoted:

```text
TOKEN='value'
```

### Use expanded environment names (1.34-guide)

Pod `env` names and ConfigMap or Secret keys imported with `envFrom` may contain
any printable ASCII except `=`, including names containing `:`.

### Override a Pod hostname (1.34.0)

With `HostnameOverride`, `PodSpec.hostnameOverride` accepts an RFC 1123 DNS
subdomain.

```yaml
spec:
  hostnameOverride: app.example
```

## Running Pod resize

### Use the resize subresource (1.33-guide)

Submit CPU and memory changes through `resize`. Pod spec is desired state;
`status.containerStatuses[*].resources` is actual state. Native sidecars can be
resized. Replace deprecated `status.resize` checks with `PodResizePending`
(`Deferred` or `Infeasible`) and `PodResizeInProgress` conditions.

```console
kubectl edit pod <pod-name> --subresource resize
```

### Apply the changing memory restrictions (1.33.0, 1.34.0)

In 1.33, memory-limit reduction required `RestartContainer`, `resizePolicy` was
immutable, and swap also required the restart policy. Later behavior permits
`resizePolicy[*].restartPolicy: NotRequired` reductions after a best-effort
usage check. Pending resizes are prioritized by PriorityClass and QoS.
Guaranteed Pods under static Memory Manager need
`InPlacePodVerticalScalingExclusiveMemory` where applicable.

### Use stable resize with integration limits (1.35-guide)

In-place CPU and memory resize is GA. VPA `InPlaceOrRecreate` is beta and
Pod-level resize was initially separate alpha behavior. Swap and static CPU or
Memory Manager policies can still prohibit a requested resize.

### Resize Pod-level resources and init containers (1.36.0)

`InPlacePodLevelResourcesVerticalScaling` is beta and default-on. Topology, CPU,
and Memory managers act on `spec.resources`, and running non-sidecar init
containers may be resized. Admission rejects capacity overflow and unsupported
OS targets. A non-sidecar init container cannot use `RestartContainer` resize
policy.

## Pod-level resource budgets and HPA

### Declare shared Pod resources (1.33.0, 1.34-guide)

`PodLevelResources` enables Pod-level `spec.resources` for CPU, memory, and huge
pages and is beta. HPA can consume the shared request and limit for
multi-container Pods.

```yaml
spec:
  resources:
    requests:
      hugepages-2Mi: 1Gi
    limits:
      hugepages-2Mi: 1Gi
```

### Respect platform and topology limits (1.34.0)

Pods with `spec.resources` are rejected when `spec.os.name: windows`. On Linux,
the initial behavior supplied no CPU or memory alignment or hints from CPU,
Memory, or Topology Manager. Use the current manager integration when enabled,
but keep OS checks.

For `resourceFieldRef`, a missing container limit falls back to the Pod-level
limit before node allocatable.

### Configure HPA tolerance per resource (1.33.0, 1.35-guide)

Beta default-on `HPAConfigurableTolerance` allows a value such as `0.05` in
`behavior` for an individual resource, overriding the cluster-wide tolerance.

## Indexed Jobs and completion

### Limit retries per index (1.33-guide)

Indexed Jobs use `backoffLimitPerIndex` so one failing index does not consume
the whole budget. `maxFailedIndexes` caps total failures, `FailIndex` stops
retries through Pod failure policy, and `status.failedIndexes` reports exhausted
indexes.

### Complete on a success policy (1.33-guide)

An Indexed Job completes when a `successPolicy` rule's `succeededIndexes`,
`succeededCount`, or combination matches. The controller sets
`SuccessCriteriaMet`, terminates remaining Pods, then sets `Complete` after
cleanup.

### Avoid overlapping replacement Pods (1.34-guide)

Set `podReplacementPolicy: Failed` so a terminating Pod reaches a terminal
phase before the Job creates its replacement.

```yaml
spec:
  podReplacementPolicy: Failed
```

## Mutable and delegated Jobs

### Edit suspended Job resources (1.35-guide, 1.36-guide)

`MutablePodResourcesForSuspendedJobs` is beta and default-on. While a Job is
suspended, or after its Pods terminate during suspension, its template may
change CPU, memory, GPU, and other extended-resource requests or limits. Active
Pods remain immutable.

### Edit suspended Job scheduling (1.35.0, 1.36.0)

`MutableSchedulingDirectivesForSuspendedJobs` began alpha and default-off and
is now default-on. It permits changes to `nodeSelector`, tolerations, and node
affinity while suspended, even before the controller records `JobSuspended`.
Suspending clears `status.startTime`.

### Delegate Job reconciliation (1.35-guide)

Stable `Job.spec.managedBy` lets an external controller own status and keeps the
built-in Job controller out. It carries no controller parameters and does not
change CronJob concurrency behavior.

## Deployment and StatefulSet rollout status

### Count terminating Deployment replicas (1.33.0)

`DeploymentPodReplacementPolicy` adds `.status.terminatingReplicas` to
Deployments and ReplicaSets so rollout tooling can distinguish terminating Pods
from other counts.

### Handle StatefulSet unavailability regression (1.35-guide, 1.36.0)

`.spec.updateStrategy.rollingUpdate.maxUnavailable` accepts a positive number or
percentage and defaults to `1`; it is especially useful with parallel Pod
management. In 1.36 `MaxUnavailableStatefulSet` is disabled by default because
of a parallel management regression, so explicitly enable it only after
validating the risk.

```yaml
spec:
  podManagementPolicy: Parallel
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 10%
```

## Placement signals and topology

### Consume copied node topology labels (1.33.0)

At binding, Kubernetes copies `topology.k8s.io/zone`,
`topology.k8s.io/region`, and `kubernetes.io/hostname` from Node to Pod. The
downward API can expose them without granting Node read permission.

### Treat `nominatedNodeName` as scheduler-owned (1.34-guide, 1.35.0)

With `NominatedNodeNameForExpectation`, scheduler may publish an intended
binding, not only preemption. Autoscalers can account for that placement, but
must not overwrite `status.nominatedNodeName`. Scheduler clears it after
scheduling or binding failure.

### Let the API server merge topology-spread selectors (1.34.0)

Kube-apiserver merges keys named by `matchLabelKeys` into
`topologySpreadConstraints[*].labelSelector`. Controllers should not repeat the
merge. Upgrade 1.32 through 1.33 before 1.34 and let affected 1.32 Pods schedule
first. `MatchLabelKeysInPodTopologySpreadSelectorMerge` controls the behavior.

### Compare numeric toleration thresholds (1.35-guide)

Alpha numeric comparison operators let Pod tolerations match threshold-valued
taints such as reliability tiers rather than only equality or existence.

## Group and workload-aware scheduling

### Schedule PodGroups atomically (1.35-guide, 1.36-guide)

Workload-aware scheduling provides PodGroups for interdependent Pods. A current
PodGroup cycle binds every Pod together or none, rather than merely checking
that a minimum is schedulable.

### Use the current Workload API (1.36.0)

Workload and PodGroup objects use `scheduling.k8s.io/v1alpha2`; `v1alpha1`
Workload is removed. Scheduler reports `PodGroupScheduled` for successful or
unschedulable groups.

### Consider sandboxed agent workloads

Agent Sandbox provides a Kubernetes execution model for long-lived or stateful
agent workloads that need isolation beyond transient stateless execution.

## Scheduler extension contracts

### Import framework types from the staging module (1.34.0)

Out-of-tree plugins must import `Status`, `CycleState`, `ClusterEvent`, and
`NodeInfo` from `k8s.io/kube-scheduler/framework`, not
`k8s.io/kubernetes/pkg/scheduler/framework`. `CycleState` is an interface, and
moved types may require methods instead of direct field access.

### Implement preflight inputs and skip behavior (1.34.0)

PreFilter receives the `NodeInfo` list. Every `PreBindPlugin` implements
`PreBindPreFlight`; returning `Skip` suppresses its `PreBind`, while success may
publish the intended `nominatedNodeName`.

### Return the current preflight result (1.36.0)

`PreBindPreFlight` returns `PreBindPreFlightResult`. Set
`AllowParallel: true` for parallel PreBind; return `nil` for sequential
execution. Plugins using `Handle.WorkloadManager` rename `PodGroupInfo` to
`PodGroupState`.

## Cleanup ordering

### Expect Pods to delete first with namespaces (1.33.0)

Default-on alpha `OrderedNamespaceDeletion` removes Pods before other
namespaced resources. Account for the new ordering in finalizers and dependent
cleanup controllers.

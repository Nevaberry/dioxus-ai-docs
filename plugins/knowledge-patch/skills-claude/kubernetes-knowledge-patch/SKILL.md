---
name: kubernetes-knowledge-patch
description: Kubernetes
version: 1.36.0
license: MIT
metadata:
  author: Nevaberry
---


# Kubernetes Knowledge Patch

Use this skill before changing Kubernetes manifests, cluster configuration,
controllers, scheduler plugins, node setup, clients, or operational tooling.
Start with the upgrade hazards, then open the topic reference that matches the
task. Prefer the cluster's manifests, code, tests, and observed behavior when
they disagree with guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [API extensibility and clients](references/api-extensibility-and-clients.md) | CRDs, aggregated APIs, client-go, protobuf, serializers, streaming APIs |
| [Control plane and observability](references/control-plane-and-observability.md) | API server, watches, APF, feature gates, metrics, diagnostics, audit, mixed-version proxy |
| [Dynamic Resource Allocation](references/dynamic-resource-allocation.md) | ResourceClaims, ResourceSlices, DRA drivers, sharing, health, binding, quotas |
| [Kubectl and kubeadm](references/kubectl-and-kubeadm.md) | kuberc, KYAML, command changes, kubeadm endpoints, probes, arguments |
| [Networking and Gateway API](references/networking-and-gateway-api.md) | Services, EndpointSlices, kube-proxy, Gateway API, Ingress migration |
| [Nodes, runtimes, and kubelet](references/nodes-runtimes-and-kubelet.md) | cgroup v2, runtime discovery, kubelet configuration, node capabilities, pressure |
| [Security, identity, and admission](references/security-identity-and-admission.md) | authentication, authorization, ServiceAccounts, Pod identity, admission, audit |
| [Storage](references/storage.md) | PVs, CSI, snapshots, VolumeAttributesClass, image volumes, migration |
| [Workloads and scheduling](references/workloads-and-scheduling.md) | Pods, containers, Jobs, controllers, HPA, resize, scheduling, workload APIs |

## Breaking changes and deprecations

### Clear node startup blockers

- Linux kubelets require cgroup v2. Treat `failCgroupV1: false` plus an
  ignored kubeadm preflight error only as a temporary compatibility override.
- Remove kubelet `--pod-infra-container-image`; leaving it configured prevents
  startup.
- Remove kubelet `--cloud-config` and `--register-schedulable`.
  `StreamingConnectionIdleTimeout` is deprecated.
- Let kubelet discover the cgroup driver from CRI. Manual `cgroupDriver` and
  `--cgroup-driver` selection are deprecated; remaining configuration-flag
  fallback is scheduled for removal in 1.38.
- Upgrade old runtimes before relying on image volumes, strict supplemental
  groups, user namespaces, or newer kubelet integrations.

### Migrate removed APIs and extension contracts

- Use `resource.k8s.io/v1` for core DRA objects. Remove or recreate incompatible
  alpha DRA data before crossing the documented upgrade boundaries.
- Use `storage.k8s.io/v1` for `VolumeAttributesClass` and the `v1beta1`
  `StorageVersionMigration` API; delete unsupported alpha objects first.
- Use `admissionregistration.k8s.io/v1` for `MutatingAdmissionPolicy` and
  migrate older stored objects before removing their served versions.
- Use `scheduling.k8s.io/v1alpha2` for Workload and PodGroup objects. The
  `v1alpha1` Workload API is removed.
- Kubectl no longer accepts legacy beta CSR, EndpointSlice, Ingress, or
  PodDisruptionBudget objects.
- Kubernetes API Go types and extension protocols use standard protobuf.
  Remove gogo registry and `ProtoMessage()` assumptions.
- Scheduler extensions import framework types from
  `k8s.io/kube-scheduler/framework` and must implement current preflight return
  types and parallelism contracts.

### Remove obsolete configuration

- Delete removed feature-gate names. Components reject enabled features whose
  dependencies are disabled.
- Remove kube-apiserver cloud-provider flags and configure external cloud
  integration separately.
- Move leader-election locks from `configmapsleases` or `endpointsleases` to
  `leases`.
- Update metric names and API-group labels before upgrading dashboards and
  alerts.
- Configure `--peer-ca-file` before relying on mixed-version API-server
  proxying.
- When request-header and ordinary client CA bundles overlap, set
  `--requestheader-allowed-names`.

### Replace deprecated networking and volumes

- Read Services through all labeled EndpointSlices, not the deprecated
  Endpoints object.
- Prefer kube-proxy `nftables`; IPVS is deprecated.
- Replace `trafficDistribution: PreferClose` with `PreferSameZone` or
  `PreferSameNode`.
- Plan alternatives to `Service.spec.externalIPs` with LoadBalancer, NodePort,
  or Gateway API.
- Migrate Ingress NGINX deployments to Gateway API and review every approximate
  ingress2gateway conversion.
- Replace `gitRepo` volumes with an init container or git-sync. The old
  feature-gate escape hatch is gone.
- Migrate removed in-tree and flex-volume integrations to CSI before control
  plane upgrades.

### Update command and access assumptions

- Write `kubectl exec POD -- COMMAND`; the separator is required.
- Expect `kubectl debug` to use the `general` profile unless another profile is
  selected.
- Add `--show-events` when describing multiple objects and related events are
  required.
- Grant `create` on `pods/exec`, `pods/attach`, and `pods/portforward`;
  WebSocket access no longer succeeds with only `get`.
- Do not treat `PodReadyToStartContainers=True` as proof that image pulling is
  complete.

## Workload quick reference

### Resize running Pods through the subresource

`spec.containers[*].resources` is desired state; container status reports
actual resources. Submit CPU and memory changes through the `resize`
subresource and inspect `PodResizePending` or `PodResizeInProgress` conditions.

```console
kubectl edit pod <pod-name> --subresource resize
```

Memory changes, swap, static CPU or Memory Manager policies, sidecars, init
containers, and Pod-level resources have distinct restrictions. Read the
workload reference before automating resize.

### Use Pod-level resource budgets deliberately

Pod-wide CPU, memory, and huge-page requests and limits simplify shared
budgets and HPA calculations. They are unsupported on Windows, and topology
manager integration depends on the active behavior.

```yaml
spec:
  resources:
    requests:
      cpu: "2"
      memory: 4Gi
    limits:
      cpu: "4"
      memory: 8Gi
```

### Distinguish sidecars and restart rules

- A native sidecar is an `initContainers` entry with container-level
  `restartPolicy: Always`; it preserves init ordering, runs with the app, stops
  in reverse order, and does not block Job completion.
- Regular and init containers can have per-container restart policies and
  exit-code rules. Restart-all rules can restart every container when a
  selected source container exits.
- `lifecycle.stopSignal` can override the image or runtime signal when the Pod
  declares its OS.

### Choose Job semantics explicitly

- Indexed Jobs can use `backoffLimitPerIndex`, `maxFailedIndexes`, `FailIndex`,
  and `successPolicy`.
- Set `podReplacementPolicy: Failed` to avoid overlapping a terminating Pod
  with its replacement.
- Suspended Jobs can accept resource and scheduling edits under the applicable
  feature behavior; active Pods remain immutable.
- `managedBy` delegates Job reconciliation but does not encode controller
  parameters.
- PodGroups provide all-or-nothing scheduling through the current
  `scheduling.k8s.io` API and condition semantics.

## Dynamic Resource Allocation quick reference

### Select claim lifecycle correctly

- A direct `ResourceClaim` is namespaced, reusable by multiple Pods, and
  manually managed.
- A `ResourceClaimTemplate` creates one claim per Pod and deletes it with the
  Pod.
- Do not set `spec.nodeName` on DRA Pods. Use an exact hostname node selector
  so scheduling still allocates and reserves devices.
- Quota can charge device-class keys and mapped extended-resource keys.

### Account for advanced allocation

Prioritized alternatives, device taints and tolerations, shared counters,
consumable capacity, binding conditions, and extended-resource mapping affect
eligibility and timing. Drivers can report device status and health, and DRA
status writers need granular binding and driver subresource permissions.

## Security and identity quick reference

### Prefer bounded workload credentials

- Bound ServiceAccount tokens carry JTI and node identity and can be restricted
  to a designated node.
- Kubelet image credential providers can request short-lived, audience-bound
  ServiceAccount tokens.
- Cached private images can require fresh credential verification through
  `imagePullCredentialsVerificationPolicy`.
- Pod certificates let kubelet generate, request, rotate, and project X.509
  credentials; verify feature and API enablement before depending on them.
- Put CSI ServiceAccount tokens in the secrets channel rather than routinely
  logged volume context.

### Harden authorization and admission

- Selector-aware authorization can require field or label selectors for list,
  watch, and delete-collection requests.
- Restrict anonymous authentication to explicit health paths.
- Constrained impersonation adds operation-specific checks while retaining
  compatibility with existing `impersonate` rules.
- Mutating admission policies use CEL apply configurations or JSON Patch and
  require bindings; escape `/` and `~` in JSON Patch keys.
- Restricted Pod security rejects probes and lifecycle handlers with an
  explicit remote `host`.
- `supplementalGroupsPolicy: Strict` prevents image `/etc/group` memberships
  from being merged.

## Operations quick reference

- Use `trafficDistribution` for Service locality and validate strict IP and
  CIDR forms while accounting for relaxed Service-name rules.
- Treat Gateway API Standard and Experimental channels as distinct identities;
  experimental `X` resources must be recreated if they graduate.
- Informers process events in order, and atomic list/relist updates let handlers
  observe one resource version.
- Large LIST operations consume APF seats according to memory size; WatchList
  changes initial-list behavior.
- Use `/flagz` and `/statusz` structured output for authorized diagnostics;
  node log queries also require `enableSystemLogQuery: true`.
- Keep personal kubectl behavior in `.kuberc`; use its credential-plugin policy
  and allowlist when command overrides are shared.
- Use `kubectl -o kyaml` for Kubernetes-oriented output when a less ambiguous
  YAML representation is useful.

---
name: kubernetes-knowledge-patch
description: Kubernetes 1.36.0 compatibility. Use for Kubernetes work.
license: MIT
version: 1.36.0
metadata:
  author: Nevaberry
---

# Kubernetes Knowledge Patch

Use this skill before changing Kubernetes manifests, cluster configuration, controllers, scheduler plugins, node setup, or operational tooling. Start with the upgrade hazards below, then open the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [API extensibility and clients](references/api-extensibility-and-clients.md) | CRDs, aggregated APIs, client-go, protobuf, serializers, streaming APIs |
| [Control plane and observability](references/control-plane-and-observability.md) | API server, watches, APF, feature gates, metrics, diagnostics, mixed-version proxy |
| [Dynamic Resource Allocation](references/dynamic-resource-allocation.md) | ResourceClaims, ResourceSlices, DRA drivers, sharing, health, binding, quotas |
| [Kubectl and kubeadm](references/kubectl-and-kubeadm.md) | kuberc, KYAML, command changes, kubeadm endpoints, probes, arguments |
| [Networking and Gateway API](references/networking-and-gateway-api.md) | Services, EndpointSlices, kube-proxy, Gateway API, Ingress migration |
| [Nodes, runtimes, and kubelet](references/nodes-runtimes-and-kubelet.md) | cgroup v2, runtime discovery, kubelet configuration, node capabilities, pressure |
| [Security, identity, and admission](references/security-identity-and-admission.md) | authentication, authorization, ServiceAccounts, Pod identity, admission, audit |
| [Storage](references/storage.md) | PVs, CSI, snapshots, VolumeAttributesClass, image volumes, migration |
| [Workloads and scheduling](references/workloads-and-scheduling.md) | Pods, containers, Jobs, controllers, HPA, resize, scheduling, workload APIs |

## Breaking changes and deprecations

### Clear node startup blockers

- Linux kubelets require cgroup v2. Treat `failCgroupV1: false` plus an ignored kubeadm preflight error only as an explicit compatibility override, not a migration target.
- Remove kubelet `--pod-infra-container-image`; leaving it configured prevents startup.
- Remove kubelet `--cloud-config` and `--register-schedulable`. `StreamingConnectionIdleTimeout` is deprecated.
- Let kubelet discover the cgroup driver from CRI. Manual `cgroupDriver` and `--cgroup-driver` selection are deprecated.
- Upgrade old runtimes: image volumes, strict supplemental groups, user namespaces, and other features have runtime and kernel prerequisites.

### Migrate removed APIs and wire formats

- Use `resource.k8s.io/v1` for core DRA objects. Follow the reference migrations before carrying alpha DRA objects or partitionable-device data across upgrades.
- Use `storage.k8s.io/v1` for `VolumeAttributesClass` and the `v1beta1` `StorageVersionMigration` API; delete unsupported alpha objects first.
- Use `admissionregistration.k8s.io/v1` for `MutatingAdmissionPolicy`; older beta storage may require migration.
- Kubectl no longer accepts legacy beta CSR, EndpointSlice, Ingress, or PodDisruptionBudget objects.
- Extension protocols and Kubernetes API Go types use standard protobuf. Remove gogo registry and `ProtoMessage()` assumptions.
- Scheduler extensions import framework types from `k8s.io/kube-scheduler/framework` and must implement the current preflight contracts.

### Remove obsolete configuration

- Delete feature-gate names after graduation or removal; components now reject enabled features whose dependencies are disabled.
- Remove the kube-apiserver cloud-provider flags and configure external cloud integration separately.
- Move leader-election locks from `configmapsleases` or `endpointsleases` to `leases`.
- Update metric names and label selectors before upgrading dashboards and alerts; API groups are now separated from resource labels in several API-server metrics.
- Configure `--peer-ca-file` before relying on mixed-version API-server proxying.
- When request-header and ordinary client CA bundles overlap, set `--requestheader-allowed-names`.

### Replace deprecated networking and volumes

- Read Services through all labeled EndpointSlices, not the deprecated Endpoints object.
- Prefer kube-proxy `nftables`; IPVS is deprecated.
- Replace `trafficDistribution: PreferClose` with `PreferSameZone` or `PreferSameNode`.
- Plan alternatives to `Service.spec.externalIPs` using LoadBalancer, NodePort, or Gateway API.
- Migrate Ingress NGINX deployments to Gateway API and review every approximate ingress2gateway conversion.
- Replace `gitRepo` volumes with an init container or git-sync. The old feature-gate escape hatch is gone.
- Migrate removed in-tree and flex-volume integrations to CSI before control-plane upgrades.

### Update command and access assumptions

- Write `kubectl exec POD -- COMMAND`; the separator is required.
- Expect `kubectl debug` to use the `general` profile unless another profile is selected.
- Add `--show-events` when describing multiple objects and related events are required.
- Grant `create` on `pods/exec`, `pods/attach`, and `pods/portforward`; WebSocket access no longer succeeds with only `get`.
- Do not treat `PodReadyToStartContainers=True` as proof that image pulling is complete.

## High-value workload behavior

### Resize running Pods through the subresource

`spec.containers[*].resources` is desired state; container status reports actual resources. Submit CPU and memory changes through the `resize` subresource and inspect `PodResizePending` or `PodResizeInProgress` conditions.

```console
kubectl edit pod <pod-name> --subresource resize
```

Memory reductions, swap, static CPU or Memory Manager policies, sidecars, init containers, and Pod-level resources have distinct restrictions. Read the workload reference before generating resize automation.

### Use Pod-level resource budgets deliberately

Pod-wide CPU, memory, and huge-page requests and limits can simplify multi-container scheduling and HPA calculations. They are unsupported on Windows, and topology-aware managers have version-dependent integration limits. A missing container limit in `resourceFieldRef` can fall back to the Pod-level limit.

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

- A native sidecar is an `initContainers` entry with container-level `restartPolicy: Always`; it preserves init ordering, runs with the app, stops in reverse order, and does not block Job completion.
- Regular and init containers can have per-container restart policies and exit-code rules.
- Restart-all rules can restart every container when a selected source container exits.
- `lifecycle.stopSignal` can override the image or runtime signal when the Pod declares its OS.

### Choose Job semantics explicitly

- Indexed Jobs can use `backoffLimitPerIndex`, `maxFailedIndexes`, `FailIndex`, and `successPolicy`.
- Set `podReplacementPolicy: Failed` to avoid overlapping a terminating Pod with its replacement.
- A suspended Job can accept resource and scheduling edits only under the applicable feature behavior; active Pods remain immutable.
- `managedBy` delegates Job reconciliation to an external controller but does not encode controller parameters.
- PodGroups provide all-or-nothing scheduling; use the current `scheduling.k8s.io` API and condition semantics.

## Dynamic Resource Allocation essentials

### Select claim lifecycle correctly

- A direct `ResourceClaim` is namespaced, reusable by multiple Pods, and manually managed.
- A `ResourceClaimTemplate` creates one claim per Pod and deletes it with the Pod.
- Do not set `spec.nodeName` on DRA Pods. Use an exact hostname node selector so scheduling still allocates and reserves devices.
- Quota can charge both device-class keys and mapped extended-resource keys.

### Account for advanced allocation

- Prioritized alternatives, device taints and tolerations, shared counters, consumable capacity, binding conditions, and extended-resource mapping affect eligibility and timing.
- Drivers can report device status and health; `Unknown` and `Unhealthy` allocations appear in Pod status.
- Binding can wait for external preparation and fail after the scheduler's configured timeout.
- DRA status writers need the granular binding and driver subresource permissions described in the DRA reference.
- Driver and ResourceSlice implementations must honor the stable kubelet plugin protocol and upgrade migrations.

## Security and identity essentials

### Prefer bounded workload credentials

- Bound ServiceAccount tokens carry JTI and node identity and can be restricted to a designated node.
- Kubelet image credential providers can request short-lived, audience-bound ServiceAccount tokens.
- Cached private images can require fresh credential verification according to `imagePullCredentialsVerificationPolicy`.
- Pod certificates let kubelet generate, request, rotate, and project X.509 credentials; verify both feature and API enablement before depending on them.
- CSI ServiceAccount tokens belong in the secrets channel rather than routinely logged volume context.

### Harden authorization and admission

- Selector-aware authorization can require field or label selectors for list, watch, and delete-collection requests.
- Restrict anonymous authentication to explicit health paths instead of enabling it globally.
- Constrained impersonation adds operation-specific checks while retaining compatibility with existing `impersonate` rules.
- Mutating admission policies use CEL apply configurations or JSON Patch and require bindings; escape `/` and `~` in JSON Patch keys.
- Restricted Pod security rejects probes and lifecycle handlers with an explicit remote `host`.
- `supplementalGroupsPolicy: Strict` prevents image `/etc/group` memberships from being merged.

## Networking and Gateway API essentials

### Model Service locality with supported fields

Use `trafficDistribution` rather than the old topology annotation. `PreferSameNode` requests node locality; `PreferSameZone` requests zone locality. Validate strict IP and CIDR forms, while accounting for relaxed Service-name rules.

### Treat Gateway features by channel

- Standard features include partial request mirroring, upstream `BackendTLSPolicy`, supported-feature status, and named route rules.
- Experimental resources use `gateway.networking.x-k8s.io` and `X`-prefixed kinds; graduation requires object recreation under the stable identity.
- Experimental HTTPRoute filters include CORS and external authorization.
- `XListenerSet` delegates listeners; `XBackendTrafficPolicy` defines retry budgets; `XMesh` advertises mesh ownership and capabilities.
- Default Gateway binding is recorded in Route status, not injected into `parentRefs`.
- Client-certificate policy is scoped by Gateway port because connection coalescing makes per-hostname validation unsafe.

## Storage essentials

- Stable `VolumeAttributesClass` supports online CSI `ModifyVolume` operations and has a ResourceQuota scope.
- PV deletion finalizers ensure `Delete` reclaim policy removes backing storage regardless of PVC/PV deletion order.
- Mutable CSI allocatable counts refresh periodically and after capacity failures.
- Image volumes can mount OCI artifacts but require compatible runtimes; review Pod Security and subpath behavior.
- Volume group snapshots provide one crash-consistent recovery point across multiple PVCs.
- SELinux-aware CSI volumes can be labeled at mount time; shared-volume label conflicts can prevent Pod startup.

## Client and operations essentials

- Informers process events in order, and atomic list/relist updates let handlers observe a single resource version.
- Large LIST operations consume APF seats according to memory size; streaming WatchList changes initial-list behavior.
- CRD conditions can carry `observedGeneration`, and numeric schema formats enforce their declared ranges.
- Use `/flagz` and `/statusz` structured output for authorized diagnostics; node log queries also require `enableSystemLogQuery: true`.
- Kubelet PSI metrics expose CPU, memory, and I/O pressure on cgroup v2.
- Keep personal kubectl behavior in `.kuberc`; use its credential-plugin policy and allowlist where command overrides are shared.
- KYAML is available through `kubectl -o kyaml` for less ambiguous Kubernetes-oriented output.

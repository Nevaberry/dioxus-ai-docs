---
name: kubernetes-knowledge-patch
description: Kubernetes
version: "1.36.0"
license: MIT
metadata:
  author: Nevaberry
---


# Kubernetes Knowledge Patch

Use this skill before changing Kubernetes manifests, cluster configuration,
controllers, scheduler plugins, node setup, client integrations, or operational
tooling. Start with the upgrade hazards, then open the reference matching the
task; details that differ by patch release remain attributed in the references.

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

- Linux kubelets require cgroup v2. Treat `failCgroupV1: false` plus an ignored
  kubeadm preflight error only as an explicit compatibility override.
- Remove kubelet `--pod-infra-container-image`; leaving it configured prevents
  startup. Remove `--cloud-config` and `--register-schedulable` too.
- Let kubelet discover the cgroup driver from CRI. Manual `cgroupDriver` and
  `--cgroup-driver` selection are deprecated.
- Upgrade old runtimes before using image volumes, strict supplemental groups,
  user namespaces, or other runtime-dependent features.

### Migrate APIs and extension contracts

- Use `resource.k8s.io/v1` for core DRA objects. Delete or recreate incompatible
  alpha DRA objects and partitionable-device data as the DRA reference directs.
- Use `storage.k8s.io/v1` for `VolumeAttributesClass` and `v1beta1` for
  `StorageVersionMigration`; delete unsupported alpha objects before upgrade.
- Use `admissionregistration.k8s.io/v1` for `MutatingAdmissionPolicy`; beta-era
  storage may still require migration.
- Kubectl no longer accepts legacy beta CSR, EndpointSlice, Ingress, or
  PodDisruptionBudget objects.
- Kubernetes API Go types and extension protocols use standard protobuf. Remove
  gogo registry and `ProtoMessage()` assumptions.
- Scheduler extensions import framework types from
  `k8s.io/kube-scheduler/framework` and must implement current preflight result
  and workload-state contracts.

### Remove obsolete configuration

- Delete feature-gate names after graduation or removal. Components reject an
  enabled feature when a required dependency is disabled.
- Remove kube-apiserver cloud-provider flags and configure external cloud
  integration separately.
- Move leader-election locks from `configmapsleases` or `endpointsleases` to
  `leases`.
- Update renamed metrics and labels before upgrading dashboards and alerts;
  several API-server metrics now separate API groups from resource labels.
- Configure `--peer-ca-file` before depending on mixed-version API-server
  proxying.
- When request-header and ordinary client CA bundles overlap, set
  `--requestheader-allowed-names`.

### Replace deprecated networking and volumes

- Read Services through every labeled EndpointSlice, not the deprecated
  Endpoints object.
- Prefer kube-proxy `nftables`; IPVS is deprecated.
- Replace `trafficDistribution: PreferClose` with `PreferSameZone` or
  `PreferSameNode`.
- Plan alternatives to `Service.spec.externalIPs` with LoadBalancer, NodePort,
  or Gateway API exposure.
- Migrate Ingress NGINX deployments to Gateway API and inspect every warning or
  approximate ingress2gateway conversion.
- Replace `gitRepo` volumes with an init container or git-sync. The feature-gate
  escape hatch is gone.
- Migrate removed in-tree and flex-volume integrations to CSI before upgrading.

### Update command and access assumptions

- Write `kubectl exec POD -- COMMAND`; the separator is required.
- Expect `kubectl debug` to use the `general` profile unless selected otherwise.
- Add `--show-events` when describing multiple objects and events are needed.
- Grant `create` on `pods/exec`, `pods/attach`, and `pods/portforward`;
  WebSocket access no longer succeeds with only `get`.
- Do not interpret `PodReadyToStartContainers=True` as proof that image pulling
  has completed.

## Workload quick reference

### Resize running Pods through the subresource

`spec.containers[*].resources` is desired state; container status reports actual
resources. Submit CPU and memory changes through the `resize` subresource and
inspect `PodResizePending` or `PodResizeInProgress` conditions.

```console
kubectl edit pod <pod-name> --subresource resize
```

Memory reductions, swap, static CPU or Memory Manager policies, native sidecars,
init containers, and Pod-level resources have distinct restrictions. Read the
workload reference before automating resize.

### Use Pod-level resource budgets deliberately

Pod-wide CPU, memory, and huge-page requests and limits can simplify scheduling
and HPA calculations. They are unsupported on Windows, and topology-aware
manager integration depends on the active behavior. A missing container limit
in `resourceFieldRef` can fall back to the Pod-level limit.

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
- Regular and init containers can have per-container policies and exit-code
  rules. Restart-all rules can restart every container when a selected source
  exits.
- `lifecycle.stopSignal` can override the image or runtime signal when the Pod
  declares its OS.

### Choose Job semantics explicitly

- Indexed Jobs support per-index retry limits, failed-index caps, `FailIndex`,
  and success policies.
- Set `podReplacementPolicy: Failed` to avoid overlapping a terminating Pod and
  its replacement.
- Suspended Jobs can accept resource and scheduling edits under the applicable
  feature behavior; active Pods remain immutable.
- `managedBy` delegates reconciliation but does not carry controller parameters.
- PodGroups provide all-or-nothing scheduling; use the current
  `scheduling.k8s.io` API and conditions.

## Dynamic Resource Allocation essentials

### Select claim lifecycle correctly

- A direct `ResourceClaim` is namespaced, reusable by multiple Pods, and
  manually managed.
- A `ResourceClaimTemplate` creates one claim per Pod and deletes it with the
  Pod.
- Do not set `spec.nodeName` on DRA Pods. Use an exact hostname node selector so
  scheduling still allocates and reserves devices.
- Quota can charge device-class and mapped extended-resource keys.

### Account for advanced allocation

- Prioritized alternatives, taints and tolerations, shared counters, consumable
  capacity, binding conditions, and extended-resource mapping affect eligibility
  and timing.
- Drivers report device status and health; `Unknown` and `Unhealthy` allocations
  appear in Pod status.
- Binding can wait for external preparation and time out under scheduler
  configuration.
- Status writers need granular binding and driver subresource permissions.
- Drivers and ResourceSlice implementations must honor the stable kubelet
  plugin protocol and release-specific migrations.

## Security and identity essentials

### Prefer bounded workload credentials

- Bound ServiceAccount tokens carry JTI and node identity and can be restricted
  to a designated node.
- Kubelet image credential providers can request short-lived, audience-bound
  ServiceAccount tokens.
- Cached private images can require fresh credential verification according to
  `imagePullCredentialsVerificationPolicy`.
- Pod certificates let kubelet generate, request, rotate, and project X.509
  credentials; verify feature and API enablement.
- CSI ServiceAccount tokens belong in the secrets channel rather than routinely
  logged volume context.

### Harden authorization and admission

- Selector-aware authorization can require field or label selectors for list,
  watch, and delete-collection requests.
- Restrict anonymous authentication to explicit health paths.
- Constrained impersonation adds operation-specific checks while retaining
  compatibility with existing `impersonate` rules.
- Mutating admission policies require bindings and use CEL apply configurations
  or JSON Patch; escape `/` and `~` in JSON Patch keys.
- Restricted Pod security rejects probes and lifecycle handlers with a remote
  `host`.
- `supplementalGroupsPolicy: Strict` prevents image `/etc/group` memberships
  from being merged.

## Networking, storage, and client essentials

- Use supported `trafficDistribution` values and validate canonical IP/CIDR
  forms while accounting for relaxed Service-name validation.
- Treat Gateway features by channel. Experimental kinds use
  `gateway.networking.x-k8s.io` and `X` prefixes and must be recreated if they
  graduate to stable identities.
- Stable `VolumeAttributesClass` supports CSI `ModifyVolume`; PV finalizers make
  `Delete` reclaim reliable; CSI allocatable counts can refresh dynamically.
- Image volumes require compatible runtimes. Volume group snapshots provide one
  crash-consistent recovery point across PVCs. SELinux mount labeling can fail
  on shared-label conflicts.
- Informers process events in order and atomic list updates expose one resource
  version. Large LISTs consume APF seats by memory size.
- Use `/flagz` and `/statusz` for authorized structured diagnostics; enable
  `enableSystemLogQuery` for node logs. Kubelet PSI metrics require cgroup v2.
- Keep kubectl preferences in `.kuberc`; use its credential-plugin policy and
  allowlist. Use `kubectl -o kyaml` for Kubernetes-oriented YAML output.

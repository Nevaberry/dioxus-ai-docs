# Dynamic Resource Allocation

Use this reference for DRA API migrations, claim lifecycle, device selection,
sharing, health, binding, quotas, driver protocols, and authorization.

## API and driver migrations

### Use the stable core API (1.34-guide, 1.35-guide)

Use `resource.k8s.io/v1` for `ResourceClaim`, `DeviceClass`,
`ResourceClaimTemplate`, and `ResourceSlice`. Pods reference claims through
`spec.resourceClaims`. Core structured DRA can no longer be disabled.

The earlier 1.33 beta added `resource.k8s.io/v1beta2`, driver-owned per-device
claim status, standardized network-interface data, `edit`-role access for
namespaced users, and rolling kubelet driver upgrades without ResourceSlice
recreation (1.33-guide). The preceding `resource.k8s.io/v1beta1` API was
deprecated for removal in 1.36 and must not remain in manifests.

### Clean up old alpha data (1.34.0, 1.35.0)

`resource.k8s.io/v1alpha3` retains only `DeviceTaintRule`. Before upgrading,
delete and recreate claims, templates, classes, or slices stored by a pre-1.32
cluster on Kubernetes 1.32 or newer. During a 1.33-to-1.34 transition, set both
`resource.k8s.io/admin-access` and the new
`resource.kubernetes.io/admin-access` namespace labels; remove the old label
when downgrade is no longer required.

Partitionable-device schemas are incompatible between 1.34 and 1.35. Delete
affected ResourceSlices before upgrading or downgrading. Devices in incomplete
pools are not allocation candidates.

### Serve the stable kubelet plugin protocol (1.34.0)

DRA drivers should implement kubelet gRPC v1. `v1beta1` is deprecated and
`v1alpha4` removed. The 1.34
`k8s.io/dynamic-resource-allocation/kubeletplugin` helper serves v1 and v1beta1
for rolling upgrades. Use standard protobuf definitions, and call
`PublishResources()` with `resourceslice.DriverResources` (1.33.0).

## Claim lifecycle and scheduling

### Choose reusable or per-Pod claims (1.35-guide)

A directly referenced `ResourceClaim` must exist in the Pod namespace, may be
shared by multiple Pods, and is manually managed. A `ResourceClaimTemplate`
creates a distinct claim per Pod and Kubernetes deletes it when the Pod ends.

### Preserve scheduler allocation (1.35-guide)

Do not set `spec.nodeName` on a DRA Pod: it bypasses allocation and reservation
and can leave kubelet waiting while the Pod consumes ordinary resources. Use an
exact hostname selector:

```yaml
spec:
  nodeSelector:
    kubernetes.io/hostname: worker-1
```

Static Pods cannot reference API objects, including arbitrary ResourceClaims
(1.34.0).

### Understand claim limits and `All` (1.33.0)

A beta claim may reserve up to 256 Pods; a claim using the higher limit cannot
be downgraded to 1.32.0. An `All` request selects only nodes that have at least
one device. Use a prioritized `count: 0` alternative to preserve the old
zero-device fallback.

## Selection, sharing, and capacity

### Use prioritized requests and administrative access (1.33-guide, 1.34-guide)

`DRAPrioritizedList` supplies ordered `firstAvailable` alternatives and is beta
and default-on. `DRAAdminAccess` controls administrative access, and
`DRAPartitionableDevices` controls dynamically selected overlapping
partitions. These alpha controls initially also required
`DynamicResourceAllocation`. Only namespaces labeled
`resource.kubernetes.io/admin-access: "true"` should submit `adminAccess`
claims after the migration period; the earlier label was
`resource.k8s.io/admin-access: "true"`.

### Map ordinary extended resources (1.35-guide)

With `DRAExtendedResource`, `DeviceClass.spec.extendedResourceName` maps an
existing extended resource to DRA devices. Any class may also be requested as
`deviceclass.resource.kubernetes.io/<class-name>`, which creates an implicit
exact-count claim.

```yaml
resources:
  limits:
    deviceclass.resource.kubernetes.io/gpu.example.com: "2"
```

### Share partition counters (1.35-guide)

Put each `sharedCounters` entry in a ResourceSlice separate from devices.
Devices may reference it with `consumesCounters` from any ResourceSlice in the
same pool. Allocation succeeds only when every referenced counter retains the
requested quantity.

### Consume device capacity across claims (1.34-guide, 1.35-guide)

`DRAConsumableCapacity` allows capacity advertised on a device to be shared
across claims or requests. For a device with `allowMultipleAllocations: true`,
define a `requestPolicy` and request quantities through
`devices.requests[*].exactly.capacity.requests`. Allocation status records the
consumed amount and `shareID`. Use CEL such as
`device.allowMultipleAllocations == true` to forbid whole-device fallback.

### Apply list-aware selection and deterministic ordering (1.36.0)

DRA CEL can call `.includes` on scalar and list attributes, for example
`device.attributes["dra.example.com"].model.includes("model-a")`.
ResourceSlice controllers sort slices and pools lexicographically before
allocation, so names can determine priority.

### Use current beta sharing behavior (1.36-guide)

Partitionable devices, consumable capacity, device taints and tolerations,
claim device status, pre-binding attachment checks, and extended-resource
integration are beta and default-on. Earlier alpha names and storage still need
the migrations above.

## Taints, health, and status

### Control taints independently (1.33-guide, 1.35.0)

`DRADeviceTaints` covers device taints and tolerations, while
`DRADeviceTaintRules` separately controls `DeviceTaintRule`. Disabling only the
rule gate preserves driver-supplied ResourceSlice taints.

### Dry-run a DeviceTaintRule (1.35-guide)

The `resource.k8s.io/v1alpha3` rule can select by class, driver, pool, device,
or CEL. Use `effect: None` to report affected devices, allocations, and Pods;
after review, use `NoExecute` to evict affected Pods.

### Diagnose allocated-device health (1.34-guide, 1.36-guide)

`ResourceHealthStatus` lets drivers expose DRA device health through the
`DRAResourceHealth` gRPC service. The beta Pod `allocatedResourcesStatus` field
now covers DRA and traditional device plugins and reports `Unhealthy` or
`Unknown`; `kubectl describe pod` displays it.

The kubelet PodResources API reports allocated DRA resources by default so
node-local agents can discover them (1.34-guide).

## Binding and status authorization

### Wait for external preparation (1.34-guide, 1.35-guide)

Devices may publish `bindingConditions`, `bindingFailureConditions`, and
`bindsToNode`. The scheduler waits for preparation or abandons a failed
allocation. The default timeout is 600 seconds; configure
`DynamicResources.bindingTimeout` in `KubeSchedulerConfiguration`.

### Grant granular status permissions (1.36.0)

With `DRAResourceClaimGranularStatusAuthorization`, schedulers and controllers
need `update` or `patch` on `resourceclaims/binding`. Drivers need
`associated-node:update` or `arbitrary-node:update`, or patch equivalents, on
`resourceclaims/driver`, restricted to their driver `resourceNames`.

## Quotas and integrations

### Charge every resource key (1.35.0)

A claim's worst-case device count consumes
`requests.deviceclass.resource.k8s.io/<deviceclass>`. A DeviceClass mapped to an
extended resource also consumes `requests.<extended-resource-name>`.

### Track emerging integrations (1.36-guide)

Alpha capabilities add native claims to higher-level workloads, device
attributes to the downward API, resource-availability reporting, list-valued
attributes, and DRA-native integration with CPU management.

## Patch-level allocator behavior

### Avoid leaked shared-capacity reservations (1.36.3)

The structured allocator now releases shared-counter reservations when it
rejects or backtracks a candidate and preserves in-use markers while sharing a
device. Upgrade to avoid Pods remaining pending despite sufficient capacity.

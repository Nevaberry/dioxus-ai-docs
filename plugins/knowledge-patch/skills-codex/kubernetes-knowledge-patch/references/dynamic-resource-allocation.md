# Dynamic Resource Allocation

## API and driver migrations

### DRA adds a simpler beta API and device status (1.33-guide)

`resource.k8s.io/v1beta2` is the simplified beta API. Driver-owned per-device
ResourceClaim status, including standardized network-interface data, is beta.
Namespaced users with cluster `edit` may use DRA, and kubelet supports rolling
driver upgrades without recreating ResourceSlices.

### DRA claim limits and `All` semantics changed (1.33.0)

`v1beta1` is deprecated in favor of `v1beta2`. A claim can reserve up to 256
Pods, but a claim using the larger limit cannot downgrade to 1.32.0. An `All`
request selects only nodes with at least one device; preserve a zero-device
fallback with a prioritized alternative having `count: 0`.

### The stable DRA API is `resource.k8s.io/v1` (1.34-guide)

Use `resource.k8s.io/v1` for `ResourceClaim`, `DeviceClass`,
`ResourceClaimTemplate`, and `ResourceSlice`. Pods reference claims through
`spec.resourceClaims`.

### The DRA kubelet plugin protocol reaches v1 (1.34.0)

Drivers should support stable kubelet gRPC v1. v1beta1 is deprecated and
v1alpha4 removed. The 1.34
`k8s.io/dynamic-resource-allocation/kubeletplugin` helper serves v1 and v1beta1
for rolling upgrades.

### Alpha DRA users need upgrade migrations (1.34.0)

`resource.k8s.io/v1alpha3` retains only `DeviceTaintRule`. Delete and recreate
claims, templates, classes, or slices stored by pre-1.32 clusters on 1.32 or
newer before upgrading. The admin-access namespace label changes from
`resource.k8s.io/admin-access` to `resource.kubernetes.io/admin-access`; set both
during a 1.33-to-1.34 transition, then remove the old label when downgrade is no
longer required.

### Core DRA can no longer be disabled (1.35-guide)

Stable `resource.k8s.io/v1` DRA is always enabled; the 1.34 off switch is gone.

### Alpha partitionable-device data needs upgrade cleanup (1.35.0)

The 1.35 partitionable-device schema is incompatible with 1.34. Delete slices
using it before upgrade or downgrade. Devices in incomplete pools are not
allocation candidates.

## Claims, lifetime, placement, and quota

### DRA claim choice controls sharing and lifetime (1.35-guide)

A direct claim must already exist in the Pod namespace, may be shared among
Pods, and is manually managed. A template creates a distinct claim per Pod and
Kubernetes deletes it when the Pod terminates.

### Avoid prebinding DRA Pods with `nodeName` (1.35-guide)

`spec.nodeName` bypasses allocation and can leave a Pod consuming ordinary node
resources while kubelet waits for an unallocated or unreserved claim. Preserve
scheduler allocation with an exact selector:

```yaml
spec:
  nodeSelector:
    kubernetes.io/hostname: worker-1
```

### DRA device requests consume additional quota keys (1.35.0)

With extended-resource integration, charge a claim's worst-case device count to
`requests.deviceclass.resource.k8s.io/<deviceclass>`. A class mapped to an
extended resource also consumes `requests.<extended-resource-name>`.

### DRA status writes require granular RBAC (1.36.0)

With `DRAResourceClaimGranularStatusAuthorization`, schedulers and controllers
need `update` or `patch` on `resourceclaims/binding`. Drivers need
`associated-node:update`, `arbitrary-node:update`, or patch equivalents on
`resourceclaims/driver`, restricted to their driver `resourceNames`.

## Selection, sharing, and capacity

### DRA gains alpha device-selection controls (1.33-guide)

With core DRA enabled, `DRADeviceTaints`, `DRAPrioritizedList`, and
`DRAPartitionableDevices` add taints/tolerations, ordered `firstAvailable`
alternatives, and overlapping partitions. `DRAAdminAccess` permits
`adminAccess` claims only in namespaces labeled
`resource.k8s.io/admin-access: "true"` at this stage.

### More DRA integrations are beta and default-on (1.34-guide)

Administrative access and prioritized `firstAvailable` requests are beta;
`DRAPrioritizedList` is enabled by default. The kubelet PodResources API reports
allocated DRA resources by default for node-local discovery.

### DRA gains alpha health, sharing, and compatibility controls (1.34-guide)

`ResourceHealthStatus` exposes allocated-device health when the driver serves
`DRAResourceHealth`. Extended-resource mapping lets existing workloads request
DRA devices through container resources. `DRAConsumableCapacity` shares a
device's advertised capacity across claims or requests, and binding conditions
can hold Pod binding until external resources are ready.

### DRA can back ordinary extended-resource requests (1.35-guide)

`DRAExtendedResource` lets `DeviceClass.spec.extendedResourceName` map an
existing extended resource to devices. Any class is also requestable as
`deviceclass.resource.kubernetes.io/<class-name>`, creating an implicit
exact-count claim.

```yaml
resources:
  limits:
    deviceclass.resource.kubernetes.io/gpu.example.com: "2"
```

### Partitionable DRA devices use shared counters (1.35-guide)

Put `sharedCounters` in a separate ResourceSlice from devices. Devices may refer
through `consumesCounters` to counters in any slice in the same pool. Allocation
requires sufficient remaining quantity in every referenced counter.

### DRA capacity can be consumed across claims (1.35-guide)

A device with `allowMultipleAllocations: true` can expose consumable capacity
and `requestPolicy`. Claims request quantities with
`devices.requests[*].exactly.capacity.requests`; allocation status records the
amount and a `shareID`. CEL may require
`device.allowMultipleAllocations == true` to prevent whole-device fallback.

### Advanced DRA sharing features are beta and default-on (1.36-guide)

Partitionable devices, consumable capacity, taints/tolerations, claim device
status, pre-binding attachment checks, and extended-resource integration are
beta with their gates enabled by default.

### DRA selection gains list and ordering controls (1.36.0)

DRA CEL supports `.includes` across scalar and list attributes, for example
`device.attributes["dra.example.com"].model.includes("model-a")`.
ResourceSlice controllers sort slices and pools lexicographically before
allocation, so names can determine priority.

### DRA shared-capacity allocation no longer leaves schedulable Pods pending (1.36.3)

The structured allocator now releases shared-counter reservations when a
candidate is rejected or backtracked and preserves in-use markers when devices
are shared. This avoids leaked or double-charged capacity that could leave a Pod
pending despite sufficient device capacity.

## Taints, health, and binding

### Device taint rules support dry runs (1.35-guide)

`resource.k8s.io/v1alpha3` `DeviceTaintRule` selects by class, driver, pool,
device, or CEL. `effect: None` reports affected devices, allocations, and Pods
without scheduling or eviction effects; after review, `NoExecute` evicts them.

### DeviceTaintRule has a separate feature gate (1.35.0)

`DRADeviceTaintRules` independently controls rule objects. Disabling it while
leaving `DRADeviceTaints` enabled preserves driver-supplied ResourceSlice taints.

### DRA binding has explicit readiness fields and a timeout (1.35-guide)

Devices publish `bindingConditions`, `bindingFailureConditions`, and
`bindsToNode`; the scheduler waits for preparation or abandons a failed
allocation. The default wait is 600 seconds and is configurable as
`DynamicResources.bindingTimeout` in `KubeSchedulerConfiguration`.

### Device health reporting now spans device plugins and DRA (1.36-guide)

Beta Pod `allocatedResourcesStatus` reports `Unhealthy` or `Unknown` devices
from classic plugins or DRA. `kubectl describe pod` surfaces the state during
container-failure diagnosis.

## Workload and node integration

### DRA gains alpha workload and metadata integrations (1.36-guide)

Alpha capabilities add native claims to higher-level workloads, expose device
attributes through the downward API, report resource availability, support
list-valued attributes, and integrate DRA-native resources with CPU management.

### Static Pods cannot reference API objects (1.34.0)

Kubelet rejects static Pods referencing API objects, including arbitrary
ResourceClaims, rather than running after mirror-Pod creation fails.

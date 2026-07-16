# Dynamic Resource Allocation

Use this reference for ResourceClaims, ResourceSlices, device classes, DRA drivers, device sharing, health, binding, quotas, and DRA authorization.

Entries are grouped by task; the parenthetical identifier is the source batch.

## Advanced DRA sharing features are beta and default-on (1.36-guide)

Partitionable devices, consumable capacity, device taints and tolerations, ResourceClaim device status, pre-binding attachment checks, and extended-resource integration all graduate to beta with their feature gates enabled by default.

## Alpha DRA users need upgrade migrations (1.34.0)

`resource.k8s.io/v1alpha3` now retains only `DeviceTaintRule`; clusters with claims, claim templates, device classes, or resource slices stored by a pre-1.32 cluster must delete and recreate them on Kubernetes 1.32 or newer before upgrading. The admin-access namespace label also changes from `resource.k8s.io/admin-access` to `resource.kubernetes.io/admin-access`; set both during a 1.33-to-1.34 transition, then remove the old label once downgrade is no longer needed.

## Alpha partitionable-device data needs upgrade cleanup (1.35.0)

The 1.35 partitionable-device schema is incompatible with 1.34; delete ResourceSlices using that alpha feature before upgrading or downgrading between the two releases. Devices from incomplete resource pools are no longer allocation candidates.

## Avoid prebinding DRA Pods with `nodeName` (1.35-guide)

Setting `spec.nodeName` bypasses DRA scheduling and can leave a Pod consuming ordinary node resources while kubelet repeatedly waits for a missing, unallocated, or unreserved claim. Use an exact hostname selector to retain the scheduler's allocation flow.

```yaml
spec:
  nodeSelector:
    kubernetes.io/hostname: worker-1
```

## Core DRA can no longer be disabled (1.35-guide)

The stable `resource.k8s.io/v1` Dynamic Resource Allocation functionality, which still had an off switch in 1.34, is always enabled in 1.35.

## Device health reporting now spans device plugins and DRA (1.36-guide)

The beta `allocatedResourcesStatus` field in Pod status reports `Unhealthy` or `Unknown` allocated devices from either traditional device plugins or DRA, and `kubectl describe pod` surfaces that state when diagnosing container failures.

## Device taint rules support dry runs (1.35-guide)

The alpha `resource.k8s.io/v1alpha3` `DeviceTaintRule` can taint devices selected by class, driver, pool, device, or CEL. Using `effect: None` reports affected devices, allocations, and Pods without scheduling or eviction effects; after review, change it to `NoExecute` to evict affected Pods.

## DeviceTaintRule has a separate feature gate (1.35.0)

`DRADeviceTaintRules` now controls DeviceTaintRule support independently; disabling it while leaving `DRADeviceTaints` enabled preserves driver-supplied taints in ResourceSlices.

## DRA adds a simpler beta API and device status (1.33-guide)

Dynamic Resource Allocation remains beta and adds `resource.k8s.io/v1beta2`; driver-owned per-device ResourceClaim status, including standardized network-interface data, is also beta. Namespaced users with the cluster `edit` role can use DRA, and kubelet now supports rolling driver upgrades without recreating ResourceSlices.

## DRA binding has explicit readiness fields and a timeout (1.35-guide)

Devices can publish `bindingConditions`, `bindingFailureConditions`, and `bindsToNode` so the scheduler waits for external preparation before binding or abandons a failed allocation. The default wait is 600 seconds and can be changed with the DynamicResources plugin's `bindingTimeout` in `KubeSchedulerConfiguration`.

## DRA can back ordinary extended-resource requests (1.35-guide)

The alpha `DRAExtendedResource` feature lets `DeviceClass.spec.extendedResourceName` map an existing extended resource to matching devices. Any DeviceClass can also be requested through `deviceclass.resource.kubernetes.io/<class-name>`, which creates an exact-count claim implicitly.

```yaml
resources:
  limits:
    deviceclass.resource.kubernetes.io/gpu.example.com: "2"
```

## DRA capacity can be consumed across claims (1.35-guide)

A ResourceSlice device with `allowMultipleAllocations: true` can expose consumable capacity and a `requestPolicy`; claims request amounts through `devices.requests[*].exactly.capacity.requests`. Allocation status reports the consumed amount and a `shareID`, and CEL can require `device.allowMultipleAllocations == true` when whole-device fallback is undesirable.

## DRA claim choice controls sharing and lifetime (1.35-guide)

A directly referenced `ResourceClaim` must already exist in the Pod's namespace, can be shared by multiple Pods, and has a manually managed lifecycle. A `ResourceClaimTemplate` instead produces a separate claim per Pod and Kubernetes deletes that claim when its Pod terminates.

## DRA claim limits and `All` semantics changed (1.33.0)

The `resource.k8s.io/v1beta1` API is deprecated for removal in 1.36 in favor of `v1beta2`; a ResourceClaim can now reserve up to 256 Pods instead of 32, but a claim using the larger limit cannot be downgraded to 1.32.0. An `All` device request now selects only nodes with at least one device; to retain the old zero-device fallback, use a prioritized alternative with `count: 0`.

## DRA device requests consume additional quota keys (1.35.0)

With `DRAExtendedResource`, a claim's worst-case device count is charged to `requests.deviceclass.resource.k8s.io/<deviceclass>`. A class mapped to an extended resource also consumes `requests.<extended-resource-name>`.

## DRA gains alpha device-selection controls (1.33-guide)

With `DynamicResourceAllocation` also enabled, `DRADeviceTaints`, `DRAPrioritizedList`, and `DRAPartitionableDevices` add device taints and tolerations, ordered `firstAvailable` alternatives, and dynamically chosen overlapping partitions. `DRAAdminAccess` restricts claims using `adminAccess` to namespaces labeled `resource.k8s.io/admin-access: "true"`.

## DRA gains alpha health, sharing, and compatibility controls (1.34-guide)

`ResourceHealthStatus` exposes allocated-device health in Pod status when the driver implements the `DRAResourceHealth` gRPC service. Extended-resource mapping lets existing workloads consume DRA-managed devices through container `resources`, while `DRAConsumableCapacity` lets capacity advertised in a device's `capacity` field be shared across claims or device requests; device binding conditions can delay Pod binding until external resources are ready.

## DRA gains alpha workload and metadata integrations (1.36-guide)

New alpha capabilities add native ResourceClaim support for higher-level workloads, expose device attributes through the downward API, report resource availability, allow list-valued device attributes, and integrate DRA-native resources with CPU management.

## DRA selection gains list and ordering controls (1.36.0)

DRA CEL expressions can call `.includes`, for example `device.attributes["dra.example.com"].model.includes("model-a")`, across scalar and list attributes. ResourceSlice controllers also sort slices and pools lexicographically before allocation, so their names can determine allocation priority.

## DRA status writes require granular RBAC (1.36.0)

With the beta `DRAResourceClaimGranularStatusAuthorization` gate, schedulers and controllers need `update` or `patch` on `resourceclaims/binding`, while drivers need `associated-node:update` or `arbitrary-node:update` (or their patch equivalents) on `resourceclaims/driver`, restricted to their driver `resourceNames`.

## More DRA integrations are beta and default-on (1.34-guide)

Administrative access and prioritized `firstAvailable` requests graduate to beta, with `DRAPrioritizedList` enabled by default. Kubelet's PodResources API also reports allocated DRA resources by default so node-local agents can discover them.

## Partitionable DRA devices use shared counters (1.35-guide)

With `DRAPartitionableDevices`, a `sharedCounters` entry must live in a separate ResourceSlice from devices, but devices can reference it through `consumesCounters` from any ResourceSlice in the same pool. Allocation succeeds only while every referenced counter has enough remaining quantity.

## The DRA kubelet plugin protocol reaches v1 (1.34.0)

DRA drivers should support the stable kubelet gRPC v1 API; v1beta1 is deprecated and v1alpha4 is removed. The 1.34 `k8s.io/dynamic-resource-allocation/kubeletplugin` helper serves both v1 and v1beta1 for rolling upgrades.

## The stable DRA API is `resource.k8s.io/v1` (1.34-guide)

The core structured-parameter DRA types (`ResourceClaim`, `DeviceClass`, `ResourceClaimTemplate`, and `ResourceSlice`) graduate to `resource.k8s.io/v1` and are available by default; Pods continue to reference claims through `spec.resourceClaims`.


# API Extensibility and Client Libraries

Use this reference for CRDs, aggregated APIs, client-go behavior, Go API
migrations, serialization, and streaming integrations.

## CRDs and API machinery

### Track condition generations (1.35.0)

CRD conditions can set `observedGeneration`. Controllers should update it with
the generation they evaluated, and clients should reject conditions that lag
behind the CRD's current generation.

### Enforce declared numeric formats (1.36.0)

CRD schemas using `int32`, `int64`, `float`, or `double` now enforce the
corresponding numeric range. Validation ratcheting preserves existing invalid
objects but rejects new out-of-range values.

### Compare resource versions only where guaranteed (1.35-guide)

In-tree resources use comparable decimal `resourceVersion` values, so clients
may order two versions numerically. Do not extend that guarantee to CRDs or
other non-in-tree resources.

### Treat Pod generations as freshness signals (1.33-guide, 1.34.0)

Pods have meaningful `metadata.generation`, top-level
`status.observedGeneration`, and per-condition
`status.conditions[*].observedGeneration`. Check the relevant generation before
acting on status or a condition.

## Aggregated APIs

### Forward authenticated user UIDs (1.33.0)

The default-on `RemoteRequestHeaderUID` behavior sends the authenticated UID to
aggregated servers as `X-Remote-Uid`. Incoming UID headers are ignored unless
kube-apiserver explicitly configures `--requestheader-uid-headers`.

### Publish EndpointSlices for APIService backends (1.34.0)

Kube-apiserver resolves an APIService's Service through EndpointSlices rather
than Endpoints. Operators that manually publish aggregated-server backends must
create a correctly labeled EndpointSlice.

## Client-go cache and informer behavior

### Expect ordered events (1.33.0)

`InOrderInformers` processes watch events sequentially rather than coalescing
nearby updates to the same object. Embedders that do not wire Kubernetes
feature gates can temporarily opt out with
`KUBE_FEATURE_InOrderInformers=false`.

### Pass context to named cache synchronization (1.35.0)

Replace `WaitForNamedCacheSync` with `WaitForNamedCacheSyncWithContext`.

### Observe atomic list state (1.36.0)

With default-on `AtomicFIFO`, list and relist operations replace the entire
store before individual handlers run. Handlers therefore see one server
resource version. Read it with `LastStoreSyncResourceVersion()`; the method
returns an empty string before synchronization.

## Go API and extension migrations

### Update extension renames (1.33.0)

Scheduler integrations rename the `UpdatePodTolerations` action to
`UpdatePodToleration`. DRA drivers must call `PublishResources()` with
`resourceslice.DriverResources`, not `Resources`.

### Use standard protobuf definitions (1.34.0, 1.35.0)

The `k8s.io/cri-api`, `k8s.io/externaljwt`, `k8s.io/kms/apis`, kubelet
plugin-registration, device-plugin, PodResources, and DRA protocols use
`google.golang.org/protobuf`. Kubernetes API Go types are not registered in the
global gogo registry and do not implement `ProtoMessage()` by default. The
`kubernetes_protomessage_one_more_release` build tag was only a one-release
bridge.

### Complete the protobuf migration (1.36.0)

The temporary build-tagged `ProtoMessage()` methods are gone. Serialize REST
API objects with `k8s.io/apimachinery/pkg/runtime/serializer/protobuf`.

### Use the FieldsV1 accessors (1.36.0)

Direct access to `metav1.FieldsV1.Raw` is deprecated. Use
`NewFieldsV1(string)`, `GetRawBytes()`, `GetRawString()`, and `SetRawBytes()`.
Admission code calling `NewLifecycle` must pass `sets.Set[string]`.

## Streaming APIs

### Move to the dedicated modules (1.36.0)

Use `k8s.io/streaming` for streaming transport and `k8s.io/cri-streaming` for
CRI server code. `k8s.io/apimachinery/pkg/util/httpstream` remains only as a
deprecated wrapper. CRI also provides streaming RPCs for sandboxes, containers,
their stats and metrics, and images.

### Account for direct kubelet WebSockets (1.36.0)

With default-on beta `ExtendWebSocketsToKubelet`, the API server sends exec,
attach, and port-forward WebSockets directly to kubelets that advertise support
through declared node features, rather than translating or tunneling them.

## Patch-level client compatibility

### Accept server-side apply container updates again (1.36.3)

Kubernetes 1.36.3 fixes the 1.36 regression that returned `422 required` when
server-side apply patched container types represented as lists or maps.
Previously valid apply requests should work without manifest changes.

### Expect restored CRI KeyValue JSON (1.34.10)

The `cri-api` JSON representation of `KeyValue.value` returns to its pre-1.34
form. Integrations that serialize or inspect that JSON must expect the restored
encoding after upgrading.

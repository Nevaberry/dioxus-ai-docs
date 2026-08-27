# API Extensibility and Client Libraries

## API machinery and schemas

### Extension protocols use standard protobuf definitions (1.34.0)

The gogo definitions are removed from `k8s.io/cri-api`, `k8s.io/externaljwt`,
`k8s.io/kms/apis`, and kubelet plugin-registration, device-plugin, and
PodResources packages. Integrations must use `google.golang.org/protobuf`.

### Kubernetes API Go types drop gogo protobuf compatibility (1.35.0)

API types are no longer in the global gogo registry and do not implement
`ProtoMessage()` by default. The `kubernetes_protomessage_one_more_release`
build tag is a one-release escape hatch. DRA protocol users must also move to
standard protobuf.

### Go integrations have API migrations (1.36.0)

Replace direct `metav1.FieldsV1.Raw` access with `NewFieldsV1(string)`,
`GetRawBytes()`, `GetRawString()`, and `SetRawBytes()`. Admission callers of
`NewLifecycle` must pass `sets.Set[string]`. The temporary `ProtoMessage()`
methods are gone; serialize Kubernetes REST types with
`k8s.io/apimachinery/pkg/runtime/serializer/protobuf`.

### CRD conditions can report their observed generation (1.35.0)

CRD conditions have `observedGeneration`, allowing clients to distinguish a
condition calculated for the current CRD generation from stale status.

### CRD numeric formats are range-checked (1.36.0)

Schemas declaring `int32`, `int64`, `float`, or `double` enforce the matching
range. Validation ratcheting preserves existing out-of-range objects but rejects
new invalid values.

### In-tree resource versions are numerically comparable (1.35-guide)

For in-tree resources, `resourceVersion` is a comparable decimal value, so a
client may order two versions instead of testing only string equality. Do not
extend this guarantee to arbitrary extension resources.

## Aggregated APIs and discovery

### Aggregated APIs receive user UIDs (1.33.0)

Default-on `RemoteRequestHeaderUID` sends authenticated user UIDs to aggregated
servers in `X-Remote-Uid`. Incoming UID headers are ignored unless
`--requestheader-uid-headers` enables them.

### Aggregated APIs resolve EndpointSlices (1.34.0)

Kube-apiserver proxies an APIService through EndpointSlices for its referenced
Service. Operators manually publishing aggregated-server backends must create
an EndpointSlice instead of, or alongside, a legacy Endpoints object.

### Obsolete API versions are disabled or removed (1.33.0)

`apidiscovery.k8s.io/v2beta1` is disabled by default. The `v1alpha1`
ValidatingAdmissionPolicy and Binding APIs are no longer served.

## Informers, lists, and caches

### Client-go informers process events in order (1.33.0)

Default-on `InOrderInformers` processes watch events sequentially rather than
grouping nearby updates to one object. Embedders that do not wire Kubernetes
feature gates can opt out with `KUBE_FEATURE_InOrderInformers=false`.

### Named cache synchronization now takes context (1.35.0)

Replace `WaitForNamedCacheSync` with `WaitForNamedCacheSyncWithContext`.

### Client-go informers expose atomic list state (1.36.0)

Default-on `AtomicFIFO` updates the entire store for a list or relist before
calling individual handlers, so every handler observes one server resource
version. `LastStoreSyncResourceVersion()` exposes that version and returns an
empty string before synchronization.

## Streaming and apply clients

### Streaming integrations use new APIs (1.36.0)

Use `k8s.io/streaming` and `k8s.io/cri-streaming` for streaming transport and
CRI server code. `k8s.io/apimachinery/pkg/util/httpstream` is a deprecated
wrapper. CRI adds streaming RPCs for sandboxes, containers, their stats and
metrics, and images.

### WebSocket streaming can reach kubelet directly (1.36.0)

Default-on beta `ExtendWebSocketsToKubelet` sends exec, attach, and port-forward
WebSockets directly to kubelets advertising support through node-declared
features instead of translating or tunneling at the API server.

### `kubectl apply` preserves null metadata keys (1.33.0)

Null label and annotation values are coerced to empty strings, matching typed
JSON metadata decoding, rather than dropping all labels or annotations.

### Server-side apply accepts container list and map updates again (1.36.3)

The patch release fixes a 1.36 regression that returned `422 required` when
server-side apply patched container types represented as lists or maps. Requests
that worked before 1.36 should work again without manifest changes.

## Extension upgrade contracts

### Extension APIs have upgrade-breaking renames (1.33.0)

Scheduling plugins rename `UpdatePodTolerations` to `UpdatePodToleration`. DRA
drivers pass `resourceslice.DriverResources`, not `Resources`, to
`PublishResources()`.

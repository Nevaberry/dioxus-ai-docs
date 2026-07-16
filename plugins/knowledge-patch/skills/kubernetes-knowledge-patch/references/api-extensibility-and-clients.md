# API Extensibility and Client Libraries

Use this reference when maintaining CRDs, aggregated APIs, client-go code, serializers, extension protocols, or API-version integrations.

Entries are grouped by task; the parenthetical identifier is the source batch.

## Aggregated APIs receive user UIDs (1.33.0)

The beta, default-on `RemoteRequestHeaderUID` feature sends authenticated user UIDs to aggregated API servers in `X-Remote-Uid`; incoming UID headers remain ignored unless `--requestheader-uid-headers` explicitly enables them.

## Client-go informers expose atomic list state (1.36.0)

With default-on `AtomicFIFO`, a list or relist updates the entire store before invoking individual handlers, so handlers observe state from one server resource version. Stores expose that version through `LastStoreSyncResourceVersion()`, which returns an empty string before synchronization.

## Client-go informers process events in order (1.33.0)

The default-on `InOrderInformers` behavior processes watch events sequentially instead of grouping nearby updates to the same object. Programs embedding client-go without wiring Kubernetes feature gates can opt out with `KUBE_FEATURE_InOrderInformers=false`.

## CRD conditions can report their observed generation (1.35.0)

CustomResourceDefinition conditions gain `observedGeneration`, letting controllers and clients distinguish a condition calculated for the current CRD generation from stale status.

## CRD numeric formats are range-checked (1.36.0)

CRD schemas that specify `int32`, `int64`, `float`, or `double` now enforce those formats' numeric ranges; validation ratcheting preserves existing out-of-range objects while rejecting new invalid values.

## Extension APIs have upgrade-breaking renames (1.33.0)

Scheduling plugins must rename the `UpdatePodTolerations` action to `UpdatePodToleration`, while DRA drivers must update `PublishResources()` calls to pass `resourceslice.DriverResources` instead of `Resources`.

## Extension protocols use standard protobuf definitions (1.34.0)

Deprecated gogo protocol definitions are removed from `k8s.io/cri-api`, `k8s.io/externaljwt`, `k8s.io/kms/apis`, and kubelet plugin-registration, device-plugin, and PodResources packages; integrations must use `google.golang.org/protobuf` definitions.

## Go integrations have API migrations (1.36.0)

Direct access to `metav1.FieldsV1.Raw` is deprecated in favor of `NewFieldsV1(string)`, `GetRawBytes()`, `GetRawString()`, and `SetRawBytes()`, and admission code calling `NewLifecycle` must use `sets.Set[string]`. Kubernetes REST API types also lose the temporary build-tagged `ProtoMessage()` methods; serialize them with `k8s.io/apimachinery/pkg/runtime/serializer/protobuf`.

## In-tree resource versions are numerically comparable (1.35-guide)

Kubernetes 1.35 defines in-tree `resourceVersion` values as a comparable decimal form, so clients may determine which of two versions is newer rather than testing only string equality. This guarantee is specifically for in-tree resources.

## Kubernetes API Go types drop gogo protobuf compatibility (1.35.0)

API types are no longer registered in the global gogo registry and no longer implement `ProtoMessage()` by default; the `kubernetes_protomessage_one_more_release` build tag is a one-release escape hatch. DRA plugin protocol users must likewise move from the removed gogo definitions to `google.golang.org/protobuf`.

## Named cache synchronization now takes context (1.35.0)

Client-go callers must replace `WaitForNamedCacheSync` with `WaitForNamedCacheSyncWithContext`.

## Obsolete API versions are disabled or removed (1.33.0)

`apidiscovery.k8s.io/v2beta1` is disabled by default, and the `v1alpha1` versions of `ValidatingAdmissionPolicy` and `ValidatingAdmissionPolicyBinding` are no longer served.

## Streaming integrations use new APIs (1.36.0)

New `k8s.io/streaming` and `k8s.io/cri-streaming` modules host streaming transport and CRI server code; `k8s.io/apimachinery/pkg/util/httpstream` remains only as a deprecated compatibility wrapper. CRI also adds streaming RPCs for sandboxes, containers, their stats and metrics, and images.


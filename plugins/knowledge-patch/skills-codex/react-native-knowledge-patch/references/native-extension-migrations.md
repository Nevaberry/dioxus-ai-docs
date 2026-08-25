# Native extension migrations

## Android and Kotlin signature changes

Recompile native overrides against the pinned React Native version. Several
Java-to-Kotlin migrations change nullability or parameter types, so preserving
an old signature with casts can hide a real contract change.

In 0.77:

- Non-primitive `ReadableArray` getters become nullable.
- `ReactHost.createSurface()` becomes non-null.
- `DevSupportManagerBase.getCurrentContext()` is renamed to
  `getCurrentReactContext()`.

The 0.78 Kotlin migration makes `RootView` parameters non-null. In 0.80,
Java-to-Kotlin migrations can change nullability and parameter types in
`devsupport`, `ColorPropConverter`, `ReactEditText`, and
`ReactTextInputManager`. Version 0.80 also removes React Native's deprecated
`StandardCharsets`; use `java.nio.charset.StandardCharsets`.

## New Architecture C++ builds

Libraries with a custom `CMakeLists.txt` must use the 0.81 compiler helper to
receive `RN_SERIALIZABLE_STATE` and the required React Native C++ flags:

```cmake
target_compile_reactnative_options(myLibraryName PRIVATE)
```

Codegen libraries without a custom CMake file do not need this call. Custom
Fabric text integrations must treat `textAlignVertical` as a paragraph
attribute, not a text attribute.

## Removed, private, and deprecated internals

### Feature flags and Android helpers

In 0.82, `ReactNativeFeatureFlags` moves to private source, Android
`JSONArguments` is removed, and `MessageQueueThreadPerfStats` becomes a stub.
Do not create compatibility dependencies on their former implementations.

### C++ headers, buffers, and aliases

From 0.82, include `CallbackWrapper.h` and `LongLivedObject.h` from
`<react/bridging/...>`, not `<ReactCommon/...>`.

In 0.84, `JSBigString` implements `jsi::Buffer` directly and the
`BigStringBuffer` indirection is removed. The deprecated aliases
`ShadowNode::Shared`, `ShadowNode::Weak`, `ShadowNode::Unshared`,
`SharedImageManager`, and `ContextContainer::Shared` are removed in 0.85.

### Networking, animation, and host extension points

In 0.84, `XHRInterceptor` and `WebSocketInterceptor` are deprecated in favor of
the CDP `Network` domain, and `TurboModuleProviderFunctionType` is deprecated.
Android networking's `sendRequestInternal` and animation's
`startOperationBatch` and `finishOperationBatch` were already deprecated in
0.83. On iOS, `RCTHostRuntimeDelegate` is deprecated in 0.85 and merged into
`RCTHostDelegate`.

### Image observer contracts

In 0.84, iOS `RCTImage` observer declarations change to reference-counted
pointers. Recompile conforming native code against the new declarations.

### Legacy bridge and UIManager types

Android 0.84 removes `LazyReactPackage`, `CxxModuleWrapper`, `CallbackImpl`,
`BridgeDevSupportManager`, `LayoutAnimationController`, and
`OnBatchCompleteListener`. Version 0.85 removes `CatalystInstanceImpl`, stubs
`NativeViewHierarchyManager`, makes `ReactTextUpdate` internal, and deprecates
`ReactZIndexedViewGroup` and `UIManagerHelper`.

## View-transition integration

React Native 0.86.0 adds `ViewTransitionModule`,
`UIManagerViewTransitionDelegate`, UIManager view-transition APIs, and
`unstable_getViewTransitionInstance`. The unstable entry point is an
integration surface, not a compatibility promise; pin the React Native version
when adopting it.

## Android window lifecycle

Native modules can implement `ExtraWindowEventListener` in 0.86.0 to react
when windows such as modal dialogs are created or destroyed.

## iOS networking interception

React Native 0.86.0 exposes selective interception points for different
request paths:

- `RCTHTTPRequestInterceptor` can selectively modify HTTP requests.
- `RCTSetCustomMultipartDataTaskRequestInterceptor` covers multipart data-task
  requests.
- `SRWebSocketProvider` can selectively inject WebSocket headers.

Use the interceptor that owns the relevant transport path rather than assuming
one hook sees all requests.

## iOS required-reason APIs

The React-timing module in 0.86.0 includes a privacy manifest that declares its
use of `mach_absolute_time()`. Preserve that manifest when repackaging or
embedding the module so the declaration is present in the shipped app.

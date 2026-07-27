# Native extension migrations

## Android signature and Kotlin migrations

Recompile native overrides against the exact React Native version. Several
Java-to-Kotlin conversions change source-visible nullability or parameter types.

In 0.77:

- Non-primitive `ReadableArray` getters become nullable.
- `ReactHost.createSurface()` becomes non-null.
- `DevSupportManagerBase.getCurrentContext()` is renamed to
  `getCurrentReactContext()`.

The 0.78 Kotlin migration makes `RootView` parameters non-null. The 0.80
Java-to-Kotlin migrations can change nullability and parameter types in
`devsupport`, `ColorPropConverter`, `ReactEditText`, and
`ReactTextInputManager`. Version 0.80 also removes React Native's deprecated
`StandardCharsets`; use `java.nio.charset.StandardCharsets`.

Do not silence mismatches with platform types or unchecked casts. Update method
signatures and null handling so Kotlin and generated override checks agree.

## New Architecture C++ build flags

Libraries with a custom `CMakeLists.txt` must apply the 0.81 helper that adds
`RN_SERIALIZABLE_STATE` and the required React Native C++ compiler flags:

```cmake
target_compile_reactnative_options(myLibraryName PRIVATE)
```

Codegen libraries without custom CMake configuration are unaffected. Custom
Fabric text integrations must also move `textAlignVertical` from a text
attribute to a paragraph attribute.

## Header, type, and extension-point changes

In 0.82:

- `ReactNativeFeatureFlags` moves to private source.
- Android `JSONArguments` is removed.
- `MessageQueueThreadPerfStats` becomes a stub.
- C++ code must include `CallbackWrapper.h` and `LongLivedObject.h` from
  `<react/bridging/...>` rather than `<ReactCommon/...>`.

In 0.83, Android networking's `sendRequestInternal` and animation's
`startOperationBatch` and `finishOperationBatch` are deprecated.

In 0.84:

- `JSBigString` implements `jsi::Buffer` directly; the `BigStringBuffer`
  indirection is removed.
- iOS `RCTImage` observer declarations use reference-counted pointers.
- `XHRInterceptor` and `WebSocketInterceptor` are deprecated in favor of the
  CDP `Network` domain.
- `TurboModuleProviderFunctionType` is deprecated.

React Native 0.85 removes deprecated aliases `ShadowNode::Shared`,
`ShadowNode::Weak`, `ShadowNode::Unshared`, `SharedImageManager`, and
`ContextContainer::Shared`. On iOS, `RCTHostRuntimeDelegate` is deprecated and
merged into `RCTHostDelegate`.

The Legacy implementation removals that affect native extensions are cataloged
in [upgrades-and-architecture.md](upgrades-and-architecture.md).

## View-transition runtime integration

React Native 0.86 adds `ViewTransitionModule`,
`UIManagerViewTransitionDelegate`, UIManager view-transition APIs, and
`unstable_getViewTransitionInstance`. The explicitly unstable getter is an
integration surface, not a compatibility promise. Keep its use isolated and
version-gated.

## Android window lifecycle

Native modules can implement `ExtraWindowEventListener` in 0.86 to observe the
creation and destruction of additional windows, including modal dialogs. Use it
when module state must follow a window rather than only the host activity.

## iOS request interception

React Native 0.86 exposes selective request hooks for different transports:

- `RCTHTTPRequestInterceptor` modifies selected HTTP requests.
- `RCTSetCustomMultipartDataTaskRequestInterceptor` handles multipart data-task
  requests.
- `SRWebSocketProvider` can inject headers selectively into WebSocket requests.

Choose the narrowest hook for the transport being modified. These native hooks
are separate from the deprecated JavaScript DevTools interceptors and the CDP
Network inspection domain.

## Required-reason API declaration

The React-timing module in 0.86 includes a privacy manifest declaring its use of
`mach_absolute_time()`. Account for the module's existing declaration when
auditing the app's required-reason API use.

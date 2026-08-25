# Native extension migrations

## Android signature migrations

Recompile native overrides against the exact React Native version instead of
carrying old signatures forward with casts.

- In 0.77, non-primitive `ReadableArray` getters become nullable,
  `ReactHost.createSurface()` becomes non-null, and
  `DevSupportManagerBase.getCurrentContext()` is renamed to
  `getCurrentReactContext()`.
- The 0.78 Kotlin migration makes `RootView` parameters non-null.
- The 0.80 Java-to-Kotlin migrations can change nullability and parameter types
  in `devsupport`, `ColorPropConverter`, `ReactEditText`, and
  `ReactTextInputManager`.
- React Native 0.80 removes its deprecated `StandardCharsets`; use
  `java.nio.charset.StandardCharsets`.

These migrations are part of batch `0.77-0.81`.

## Custom New Architecture C++ builds

Libraries with a custom `CMakeLists.txt` must use the 0.81 helper that supplies
`RN_SERIALIZABLE_STATE` and required React Native C++ flags:

```cmake
target_compile_reactnative_options(myLibraryName PRIVATE)
```

Codegen libraries without custom CMake are unaffected. Custom Fabric text
integrations must treat `textAlignVertical` as a paragraph attribute rather
than a text attribute.

## Removed and deprecated native APIs

In 0.82, `ReactNativeFeatureFlags` moves to private source, Android
`JSONArguments` is removed, and `MessageQueueThreadPerfStats` becomes a stub.
C++ code must include `CallbackWrapper.h` and `LongLivedObject.h` from
`<react/bridging/...>` rather than `<ReactCommon/...>`.

In 0.84, `JSBigString` implements `jsi::Buffer` directly and the
`BigStringBuffer` indirection is removed. iOS `RCTImage` observer declarations
change to reference-counted pointers. `XHRInterceptor` and
`WebSocketInterceptor` are deprecated in favor of the CDP `Network` domain,
and `TurboModuleProviderFunctionType` is deprecated.

React Native 0.85 removes `ShadowNode::Shared`, `ShadowNode::Weak`,
`ShadowNode::Unshared`, `SharedImageManager`, and `ContextContainer::Shared`.
On iOS, `RCTHostRuntimeDelegate` is deprecated and merged into
`RCTHostDelegate`. Android networking's `sendRequestInternal` and animation's
`startOperationBatch` and `finishOperationBatch` were already deprecated in
0.83. These changes are from batch `0.82-0.85`.

## View-transition runtime integration

React Native 0.86.0 adds `ViewTransitionModule`,
`UIManagerViewTransitionDelegate`, UIManager view-transition APIs, and
`unstable_getViewTransitionInstance`. The explicitly unstable entry point is
an integration surface, not a compatibility promise.

## Android window lifecycle

Native Android modules in 0.86.0 can implement `ExtraWindowEventListener` to
react when windows such as modal dialogs are created or destroyed.

## iOS request interception

React Native 0.86.0 adds selective request hooks:

- `RCTHTTPRequestInterceptor` can modify selected HTTP requests.
- `RCTSetCustomMultipartDataTaskRequestInterceptor` handles multipart
  data-task requests.
- `SRWebSocketProvider` can inject headers into selected WebSocket requests.

## iOS required-reason declarations

The React-timing module in 0.86.0 includes a privacy manifest declaring its use
of the required-reason API `mach_absolute_time()`.

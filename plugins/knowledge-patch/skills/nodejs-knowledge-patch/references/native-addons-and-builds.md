# Native Addons, Embedding, and Builds

Supported build platforms, toolchains, addon ABIs, Node-API, embedding, and native integration.

## Contents

- [Source builds and supported platforms](#source-builds-and-supported-platforms)
- [Node-API and native addons](#node-api-and-native-addons)
- [Embedding and native integration](#embedding-and-native-integration)

## Source builds and supported platforms

### Experimental Node-API build warning (since 25.0.0)

Native addon builds that define `NAPI_EXPERIMENTAL` now produce a warning, making accidental dependence on the unstable experimental Node-API surface visible during compilation.

### Shared `nbytes` source builds (since 25.5.0)

Source builds now accept the `--shared-nbytes` configure flag for using a shared `nbytes` dependency.

### Source-build additions (since 25.4.0)

Source builds now support Visual Studio 2026 and add `--shared-hdr-histogram`, `--shared-gtest`, and `--debug-symbols`; the last option includes debug symbols without enabling DCHECKs.

### Source-build requirements and addon ABI (since 25.0.0)

Clang-based source builds now require Clang 19, while Apple builds require Xcode 16.4. Native addons tied to Node's V8 ABI need builds for `NODE_MODULE_VERSION` 141.

### Source-build requirements and targets (since 26.0.0)

Building Node.js now requires GCC 13.2 and no longer supports Python 3.9. Windows builds target SDK 11, Power8 and IBM z13 support is removed, and AIX or IBM i builds target Power9.

Temporal-enabled source builds now check for `rustc` and Cargo, and the build honors the `CARGO` environment variable when selecting the Cargo executable.

### Supported platforms and source builds (since 24.0.0)

Windows source builds now require ClangCL; MSVC support has been removed. The minimum supported macOS version is 13.5 and the minimum Xcode version is 16.1, Python 3.8 is no longer supported for builds, 32-bit PowerPC and s390 support is removed, and Armv7 support is experimental.

Native addons tied to Node's module ABI need builds for `NODE_MODULE_VERSION` 137; portable Node-API addons are not tied to that V8 ABI number.

### Supported platforms and source-build toolchains (since 23.0.0)

Node.js 23 no longer supports 32-bit Windows or Windows before 10. Building Node itself now uses C++20, warns with GCC older than 12.2, and requires GCC 12 on AIX.

### Upcoming macOS x64 support change (since 26.5.0)

Tier 2 support for macOS x64 is scheduled to end, so build and release planning should move away from relying on that support tier.


## Node-API and native addons

### Buffer views for Node-API addons (since 23.0.0)

Node-API adds `napi_create_buffer_from_arraybuffer()`, which creates a `Buffer` view over a specified byte range of an existing JavaScript `ArrayBuffer`.

```c
napi_create_buffer_from_arraybuffer(env, arraybuffer, offset, length,
                                    &data, &buffer);
```

### Native addon ABI and headers (since 26.0.0)

Native addons tied to Node's V8 ABI need builds for `NODE_MODULE_VERSION` 147. The public `node.h` header now includes `node_api_types.h` instead of `node_api.h`, so addons that use the full Node-API surface must include `node_api.h` explicitly rather than relying on the former transitive include.

### Node-API reference cleanup in finalizers (since 23.5.0)

Native addon finalizers may now call `napi_delete_reference()`, allowing a reference to be released as part of finalization.

### Node-API typed-memory support (since 25.4.0)

Node-API now supports `Float16Array`, and `napi_create_dataview()` can create a view backed by a `SharedArrayBuffer`.

### Shared array buffers in Node-API (since 24.9.0)

Node-API now exposes creation, inspection, and type checking for JavaScript `SharedArrayBuffer` values, so native addons can work with shared backing memory directly.


## Embedding and native integration

### `node::ObjectWrap` cleanup hooks (since 26.4.0)

Native addons can now attach cleanup hooks to `node::ObjectWrap` instances so wrapped resources can participate in environment cleanup.

### ESM support in the embedder API (since 24.14.0)

Node's C++ embedder API now has initial support for ES modules. Native hosts embedding Node can integrate ESM execution through the supported embedder surface instead of being limited to CommonJS-oriented startup.

### Experimental fast FFI calls (since 26.4.0)

The experimental FFI surface now has a fast-call API for AArch64 and x86_64, with fast support extended to almost all other platforms.

### Node-managed embedder contexts (since 24.18.0)

The C++ embedder API now exposes `node::RegisterContext()` for turning a V8 context into a Node-managed context.

### Removed C++ embedding APIs (since 25.0.0)

The deprecated `node::InitializeNodeWithArgs()`, `node::CreatePlatform()`, `node::FreePlatform()`, `node::EmitBeforeExit()`, and `node::EmitExit()` APIs are removed, along with callback helpers that omit async context. Embedders must use the current once-per-process, platform, event-loop, and async-context-aware callback APIs.

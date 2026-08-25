# Native Addons, Embedding, and Builds

## ABI and platform baselines

- Node.js 23.0.0 removes 32-bit Windows support and experimental support for
  Windows older than 10. Node itself builds as C++20, GCC older than 12.2
  warns, AIX uses GCC 12, and final `NODE_MODULE_VERSION` is 131. Rebuild or
  replace ABI-dependent addon binaries.
- Node.js 24.0.0 requires ClangCL rather than MSVC for Windows source builds,
  uses a macOS 13.5 and Xcode 16.1 baseline, and drops Python 3.8. It removes
  32-bit s390 and PowerPC support, classifies ARMv7 as experimental, and uses
  `NODE_MODULE_VERSION` 137.
- Node.js 25.0.0 requires Clang 19 and Xcode 16.4 for macOS source builds. Its
  `NODE_MODULE_VERSION` is 141. Distributions no longer bundle Corepack, so
  projects that need it must install it separately.
- Node.js 26.0.0 requires GCC 13.2, drops Python 3.9, targets Windows SDK 11,
  removes Power8 and IBM z13, and targets Power9 on AIX and IBM i. Temporal-
  enabled builds check for `rustc` and Cargo and honor `CARGO`.
  `NODE_MODULE_VERSION` is 147.
- In 26.7.0, source builds require `rustc` 1.86 or newer.
- In 26.5.0, Tier 2 macOS x64 support is due to end; build and CI planning
  should not depend on that tier.

## Node-API

- In 23.5.0, addon finalizers may call `napi_delete_reference()`.
- In 23.6.0, Node-API defines version 10 as a compatibility and feature-check
  boundary.
- In 24.9.0, Node-API can create, inspect, and type-check JavaScript
  `SharedArrayBuffer` values.
- In 24.12.0, `napi_create_object_with_properties()` creates an object and
  defines its property descriptors in one call. It requires explicit
  experimental opt-in because `node.h` no longer defines `NAPI_EXPERIMENTAL`
  automatically: define it before including `node_api.h`.
- In 24.13.0, the 24.13.1 APIs add `Float16Array` support and allow
  `napi_create_dataview()` to use `SharedArrayBuffer` backing memory.
- In 26.0.0, `node.h` includes `node_api_types.h` rather than the complete
  `node_api.h`; addons using the complete Node-API surface must include
  `node_api.h` explicitly.

## Source-build controls and optional components

- In 23.8.0, source builds accept `suppress_all_error_on_warn` to suppress
  warning-as-error treatment.
- In 24.1.0, custom builds can omit SQLite. Software targeting custom builds
  must feature-detect `node:sqlite` instead of inferring it from the version.
- In 24.13.0, 24.13.1 supports Python 3.14 source builds, including the Windows
  setup.
- In 25.4.0, source builds add `--shared-hdr-histogram` and `--shared-gtest`.
  `--debug-symbols` adds `-g` without enabling DCHECKs, and Windows builds
  support Visual Studio 2026.
- In 25.5.0, `--shared-nbytes` links a shared nbytes dependency.
- In 25.9.0, Node can build and link with OpenSSL 4.0.
- In 24.18.0, `--enable-all-experimentals` compiles with all experimental
  features enabled.

## Native embedders

- In 25.0.0, embedders must migrate from removed callback-without-async-
  context APIs and removed `node::EmitBeforeExit`, `node::EmitExit`,
  `node::CreatePlatform`, `node::FreePlatform`, and
  `node::InitializeNodeWithArgs`.
- In 24.14.0, the C++ embedder API gains initial ESM support.
- In 24.18.0, `node::RegisterContext()` makes a V8 context managed by Node.

## Native extension surfaces

- In 25.9.0, native addons gain `crypto::GetSSLCtx()` for OpenSSL context
  access.
- In 26.4.0, the FFI implementation adds an experimental fast-call API on
  AArch64 and x86_64 and extends fast-call support to almost all other
  platforms in that release.
- In 26.4.0, `node::ObjectWrap` adds object-associated cleanup hooks.

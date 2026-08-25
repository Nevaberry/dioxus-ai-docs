# Native Addons, Embedding, and Builds

Use this reference for native addons, embedding, and builds work.

## Distribution, build, and addon baselines (`25.0.0`)

Node distributions no longer include Corepack, so projects that depend on it must install it separately. The minimum Clang version is 19, macOS source builds require Xcode 16.4, and `NODE_MODULE_VERSION` is 141, requiring matching ABI-dependent addon binaries.

## Enable all experiments in source builds (`24.18.0`)

Source builds accept `--enable-all-experimentals` to compile with all experimental features enabled.

```sh
./configure --enable-all-experimentals
```

## Experimental ESM loading for native addons (`23.6.0`)

The ESM loader now has experimental support for addon modules, allowing native addons to participate directly in ESM loading.

## Experimental fast FFI calls (`26.4.0`)

The FFI implementation gains an experimental fast-call API for AArch64 and x86_64, with fast-call support extended to almost all other platforms in the same release.

## Experimental Node-API object construction (`24.12.0`)

Native addons can create an object and define its property descriptors in one call with `napi_create_object_with_properties()`. This API requires an explicit experimental opt-in because `node.h` no longer defines `NAPI_EXPERIMENTAL` automatically.

```c
#define NAPI_EXPERIMENTAL
#include <node_api.h>

napi_value object;
napi_create_object_with_properties(env, property_count, properties, &object);
```

## Initial ESM support for native embedders (`24.14.0`)

The C++ embedder API now has initial support for ES modules, allowing native hosts that embed Node.js to integrate ESM execution.

## Managed contexts for native embedders (`24.18.0`)

The C++ embedder API now exposes `node::RegisterContext()` for making a V8 context managed by Node.

## Native `ObjectWrap` cleanup hooks (`26.4.0`)

The C++ `node::ObjectWrap` API adds cleanup hooks, giving native addons an object-associated cleanup path.

## Native addon ABI and headers (`26.0.0`)

ABI-dependent addons need builds for `NODE_MODULE_VERSION` 147. Because `node.h` now includes `node_api_types.h` rather than the complete `node_api.h`, addons using the full Node-API surface must include `node_api.h` explicitly.

## Native-addon imports enabled by default (`26.5.0`)

The module loader now enables import support for native addons by default, so ESM addon imports no longer require separate enablement.

## Node-API reference cleanup in finalizers (`23.5.0`)

Native addons may now call `napi_delete_reference()` from finalizers.

## Node-API typed-array support (`24.13.0`)

Node-API adds `Float16Array` support and allows `napi_create_dataview()` to use `SharedArrayBuffer` backing memory in 24.13.1.

## Node-API version 10 (`23.6.0`)

Node-API now defines version 10, giving native addons a new version boundary for feature and compatibility checks.

## Platform, build, and addon baselines (`24.0.0`)

Windows source builds now require ClangCL instead of MSVC, the supported macOS baseline is 13.5 with Xcode 16.1, and Python 3.8 is no longer supported for builds. Support for 32-bit s390 and PowerPC is removed, ARMv7 is experimental, and `NODE_MODULE_VERSION` is 137, so ABI-dependent addons need matching binaries.

## Platform, compiler, and addon baselines (`23.0.0`)

Node.js 23 removes 32-bit Windows support and the experimental support for Windows older than 10, builds Node itself as C++20, warns for GCC older than 12.2, and uses GCC 12 on AIX. Its final `NODE_MODULE_VERSION` is 131, so ABI-dependent native addon binaries must be rebuilt or replaced.

## Python 3.14 source builds (`24.13.0`)

Node.js 24.13.1 supports Python 3.14 for source builds, including the Windows build setup. Build environments no longer need to pin an older Python solely for this Node.js line.

## Rust source-build baseline (`26.7.0`)

Source builds now require `rustc` 1.86 or newer, so build images and toolchains pinned to an older Rust compiler must be upgraded.

## Shared nbytes source builds (`25.5.0`)

Source builds can link against a shared nbytes dependency with the new `--shared-nbytes` configure flag.

```sh
./configure --shared-nbytes
```

## SharedArrayBuffer support in Node-API (`24.9.0`)

Node-API now supports creating, inspecting, and type-checking JavaScript `SharedArrayBuffer` values, so native addons can work with shared backing memory directly.

## Source-build controls (`25.4.0`)

Source builds add `--shared-hdr-histogram` and `--shared-gtest`; `--debug-symbols` adds `-g` without enabling DCHECKs. Windows source builds also support Visual Studio 2026.

```sh
./configure --shared-hdr-histogram --shared-gtest --debug-symbols
```

## Source-build requirements (`26.0.0`)

Source builds now require GCC 13.2 and no longer support Python 3.9; Windows targets SDK 11, Power8 and IBM z13 support is removed, and AIX or IBM i targets Power9. Temporal-enabled builds check for `rustc` and Cargo and honor the `CARGO` environment variable.

## Source-build warning control (`23.8.0`)

Source builds gain the `suppress_all_error_on_warn` option for suppressing warning-as-error treatment.

## Upcoming macOS x64 support change (`26.5.0`)

Tier 2 support for macOS x64 is due to end, so build and CI planning should avoid depending on that support tier.

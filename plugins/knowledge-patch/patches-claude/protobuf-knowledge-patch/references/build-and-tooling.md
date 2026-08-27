# Build and tooling

## CMake dependency resolution (`30.0-migration`)

The `protobuf_*_PROVIDER` switches were removed. CMake first uses installed
dependencies and fetches protobuf-pinned versions when they are unavailable.
Choose the dependency policy explicitly when hermetic or offline builds matter:

```sh
cmake . -Dprotobuf_LOCAL_DEPENDENCIES_ONLY=ON
cmake . -Dprotobuf_FORCE_FETCH_DEPENDENCIES=ON
```

`protobuf_LOCAL_DEPENDENCIES_ONLY=ON` forbids fetching;
`protobuf_FORCE_FETCH_DEPENDENCIES=ON` fetches even when an installed dependency
is available.

## CMake package and test targets (`34.0-announcement`, `34.0`)

CMake installs no longer include protoc's private generator headers. Those
headers were never a public interface, so downstream generators must stop
including them from the installed package.

Protobuf's own tests are no longer built by default. Source builds and CI jobs
that need the test targets must explicitly enable them.

## C++ distribution (`30.0-migration`)

The C++ CocoaPods distribution was removed. Consume the C++ runtime from the
project's release artifacts instead.

## Bazel on Windows (`30.0-migration`, `34.0-announcement`)

The earlier Windows Bazel transition rejected MSVC by default and required a
clang-cl toolchain. During that transition,
`--define=protobuf_allow_msvc=true` temporarily suppressed the error. In the
same release, MSVC remained usable through CMake. In the later Bazel build
rules, MSVC remains supported and that temporary flag is removed. Do not carry
the escape hatch into current invocations.

## Proto toolchain resolution (`34.0-announcement`)

Native `--proto_toolchain_for*` and `--proto_compiler` flags are no longer read
by Proto rules. Their short-term repository-scoped replacements are:

```text
--@protobuf//bazel/flags/cc:proto_toolchain_for_cc
--@protobuf//bazel/flags/java:proto_toolchain_for_java
--@protobuf//bazel/flags/java:proto_toolchain_for_javalite
--@protobuf//bazel/flags:proto_compiler
```

The durable migration is to enable
`--incompatible_enable_proto_toolchain_resolution` and register ordinary
platform toolchains. This resolution mode is the Bazel 9 default.

Other Proto flags moved below `--@protobuf//bazel/flags`, including
`strict_proto_deps`, `strict_public_imports`,
`experimental_proto_descriptor_sets_include_source_info`, and `protocopt`.
C++ header/source suffix flags live below `--@protobuf//bazel/flags/cc`.

The v34.0 `protocopt` path is
`--@protobuf//bazel/flags/cc:protocopt`; v34.1 moves it to
`--@protobuf//bazel/flags:protocopt`. The old location remains a deprecated
alias only until the next breaking release.

## Bazel version and dependency mode (`34.0-migration`)

Protobuf v34 requires Bazel 8 or newer. Bazel 8 also changes the default
dependency mode from WORKSPACE to Bzlmod, so upgrade both the tool and the
dependency declaration strategy.

## Prebuilt compiler selection (`34.0`)

`@protobuf//bazel/flags:prefer_prebuilt_proto` now defaults to true. Pin the flag
when a build must preserve the previous compiler-selection behavior rather than
silently switching to a prebuilt `protoc`.

## Provider API (`34.0-announcement`)

`ProtoInfo.transitive_imports` was removed. Starlark rules must use
`ProtoInfo.transitive_sources`.

## Python Bazel rules (`30.0-migration`)

The `bazel/system_python.bzl` alias was removed. Prefer `protobuf_deps.bzl`, or
use its moved location at `python/dist/system_python.bzl`. The internal
`py_proto_library` from `protobuf.bzl` was also removed; use the official rule
under `bazel/py_proto_library`.

## Option-only dependencies (`edition-2024-announcement`)

An `import option` declaration imports custom options without exposing the
source file's messages or enums as ordinary symbols. It must follow all normal
imports. In Bazel, list that dependency under `option_deps`, not `deps`;
`option_deps` requires Bazel 8 or later.

```proto
edition = "2024";
import option "bar.proto";

option (file_opt1) = true;
option (file_opt2) = {bar: true};
```

```build
proto_library(
  name = "foo",
  srcs = ["foo.proto"],
  option_deps = [":custom_option"],
)
```

## Compiler output paths (`35.0`)

`protoc` now fails a file write when any generated file output path is relative.
Build wrappers and generator invocations must provide absolute output locations.

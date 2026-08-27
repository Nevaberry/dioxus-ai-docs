# Compatibility, Builds, and Releases

## Generated-code and runtime compatibility

### Compatibility window (`release-lifecycle`)

Generated code must never run against a runtime older than the `protoc` and
plugin release that produced it, even when only the patch version differs. For
most languages, major `V` generated code is supported from its own release
through runtime major `V+1`; runtime `V+2` or later is unsupported. Older-minor
generated code works on later runtimes in the same major.

Security fixes can require paired runtime and generated-code updates despite
that window. Loading multiple major runtime versions in one process is also
unsupported. Regenerate on every release update; the compatibility window is
for existing-project migration, not a reason to keep stale outputs.

### Exact-match languages

C++ and Rust require generated code and runtime releases to match exactly. C++
also makes no ABI-stability promise between minor or patch releases.

### Python's extended window

Python generated code from 3.20.0 onward is descriptor-based and supported
through at least runtime 8.x. A future major that ends that window is expected
to warn and then error in advance. Older gencode paired with a newer runtime can
therefore emit poison warnings for a combination that will fail at the next
runtime major, as happened for Python 4.x gencode on runtime 5.x before 6.x
(`30.0-migration`).

## Release numbering and support policy

The shared Protobuf release is a `minor.point`, while each runtime prepends its
own major. For example, shared release `34.1` maps to Java `4.34.1` and C#
`3.34.1`. A shared release can bump some language majors without bumping others.

The `34.0-announcement` package-boundary plan moved C++ and Python from 6.33 to
7.34.0 and PHP and Objective-C from 4.33 to 5.34.0. Java, Ruby, C#, Rust, and
JRuby did not take a major bump. Python generated-code format did not change for
7.34.x, and its poison checks were relaxed for old generated files.

The support snapshot in this patch is:

- `protoc`: 35.x active; 33.x and Java-specific 25.x maintenance.
- C++: 7.35.x active; 6.33.x maintenance; exact-match gencode.
- C#: 3.35.x active; minimum gencode 3.0.0.
- Java: 4.35.x active; 3.25.x maintenance; minimum gencode 3.0.0.
- PHP: 5.35.x active; 4.33.x maintenance; minimum gencode 4.26.0.
- Python: 7.35.x active; 6.33.x maintenance; minimum gencode 3.20.0.
- Ruby: 4.35.x active; minimum gencode 3.0.0.

Updates are quarterly and breaking releases target Q1. A new minor immediately
ends support for the preceding minor. After a new major, the prior major remains
supported for four more quarters; Java 3.x is the exception, with a 36-month
maintenance window.

Edition numbers are independent of compiler and runtime versions. Edition 2023
requires `protoc` 27.0 or newer and Edition 2024 requires 32.0 or newer. The
latest compiler still accepts proto2, proto3, Edition 2023, and Edition 2024.

Minor and patch releases may add or deprecate `descriptor.proto` elements,
introduce an Edition, or add/drop OS, language, and tooling support. Enforcing
an existing policy, such as dropping an end-of-life platform, is not treated as
a breaking change and need not wait for a language-major bump.

Android's supported minimum SDK is the lower of the Google Play services
minimum and Jetpack's default. JRuby is best-effort; its target is the latest
JRuby compatible with the minimum supported Ruby version.

## CMake

### Dependency resolution (`30.0-migration`)

The `protobuf_*_PROVIDER` switches are removed. CMake first prefers installed
dependencies, then fetches pinned versions when dependencies are missing. Make
the policy explicit for hermetic or offline builds:

```sh
cmake . -Dprotobuf_LOCAL_DEPENDENCIES_ONLY=ON
cmake . -Dprotobuf_FORCE_FETCH_DEPENDENCIES=ON
```

`protobuf_LOCAL_DEPENDENCIES_ONLY=ON` forbids fetching;
`protobuf_FORCE_FETCH_DEPENDENCIES=ON` always fetches.

CMake distributions no longer install protoc's private generator headers
(`34.0-announcement`). Stop including them from an installed package. The C++
CocoaPods distribution is also gone; consume the C++ runtime from the GitHub
release instead (`30.0-migration`).

### Tests (`34.0`)

CMake does not build Protobuf's tests by default. Source builds and CI jobs that
need the test targets must enable them explicitly.

## Bazel

### Version and dependency mode (`34.0-migration`)

Protobuf 34 drops Bazel 7; Bazel 8 is the minimum. Bazel 8 also changes the
default dependency mode from WORKSPACE to Bzlmod, so upgrade the build and
migrate dependency declarations together.

### Proto toolchain resolution (`34.0-announcement`)

Native `--proto_toolchain_for*` and `--proto_compiler` flags are no longer read
by Proto rules. Their short-term replacements are:

```text
--@protobuf//bazel/flags/cc:proto_toolchain_for_cc
--@protobuf//bazel/flags/java:proto_toolchain_for_java
--@protobuf//bazel/flags/java:proto_toolchain_for_javalite
--@protobuf//bazel/flags:proto_compiler
```

The durable migration is to enable
`--incompatible_enable_proto_toolchain_resolution` (the Bazel 9 default) and
register normal platform toolchains.

Other Proto flags move under `--@protobuf//bazel/flags`, including
`strict_proto_deps`, `strict_public_imports`,
`experimental_proto_descriptor_sets_include_source_info`, and `protocopt`.
C++ header/source suffix flags live under `--@protobuf//bazel/flags/cc`.

In 34.0, `protocopt` is mistakenly located at
`--@protobuf//bazel/flags/cc:protocopt`. Release 34.1 moves it to
`--@protobuf//bazel/flags:protocopt` and retains the old spelling only as a
deprecated alias until the next breaking release.

### Providers, Python rules, and Windows

`ProtoInfo.transitive_imports` is removed; use `transitive_sources`
(`34.0-announcement`). The `bazel/system_python.bzl` alias is removed; prefer
`protobuf_deps.bzl`, or use its moved location at
`python/dist/system_python.bzl`. The internal `py_proto_library` from
`protobuf.bzl` is removed; use the official rule under
`bazel/py_proto_library` (`30.0-migration`).

At the 30.0 migration boundary, Windows Bazel builds rejected MSVC and required
clang-cl; `--define=protobuf_allow_msvc=true` temporarily suppressed the error,
while CMake could still use MSVC. By `34.0-announcement`, Bazel again continued
to support MSVC, but that temporary allow flag was removed. Match the behavior
to the pinned Protobuf release rather than retaining the obsolete override.

### Compiler selection and bounds checks (`34.0`)

`@protobuf//bazel/flags:prefer_prebuilt_proto` now defaults to true. Pin it when
reproducible builds depend on source-built compiler selection. The old
`safe_boundary_check` mechanism is gone; source builds configure checking with:

```text
--//third_party/protobuf:bounds_check_mode
```

## `protoc` output paths

As of `35.0`, the compiler rejects a file write when any file output path is
relative. Supply absolute output locations in direct invocations and generator
wrappers.

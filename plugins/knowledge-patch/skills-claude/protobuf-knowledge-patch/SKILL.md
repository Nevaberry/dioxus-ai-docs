---
name: protobuf-knowledge-patch
description: Protocol Buffers
version: 35.0
license: MIT
metadata:
  author: Nevaberry
---


# Protocol Buffers Knowledge Patch

Use this skill when upgrading `protoc`, a language runtime, generated code, build
rules, or an Editions schema. It captures compatibility rules, removed APIs,
stricter validation, and generated-API changes that are easy to miss during an
otherwise routine dependency update.

## How to use this patch

1. Identify the exact `protoc`, plugin, runtime, and generated-code versions in
   the project. A shared protobuf release number maps to different package majors.
2. Read the compatibility rules before changing only one component. C++ and Rust
   require exact gencode/runtime matches; other languages have bounded windows.
3. Open the reference matching the affected build system, schema, or language.
4. Regenerate code after upgrades, then compile and exercise parsing, JSON,
   reflection, deep-input, and bounds-sensitive paths.
5. Treat poisoned-gencode warnings and deprecation diagnostics as migration
   work, not harmless noise.

## Reference index

| Reference | Topics |
| --- | --- |
| [Build and tooling](references/build-and-tooling.md) | CMake dependency fetching, Bazel toolchains and Bzlmod, Python rules, package layout, `protoc` output paths |
| [Compatibility and lifecycle](references/compatibility-and-lifecycle.md) | Gencode/runtime windows, language package numbering, supported lines, cadence, Android and JRuby policy |
| [C++](references/cpp.md) | Removed APIs, string views, arenas, repeated fields, bounds checks, debug output, Edition-generated APIs |
| [Editions and schema](references/editions-and-schema.md) | Edition 2024/2026 features, visibility, naming, imports, descriptor labels, compiler validation |
| [Java, C#, and Objective-C](references/java-csharp-objective-c.md) | Java enum and initialization APIs, recursion, C# packages and UTF-8, Objective-C unknown fields and descriptors |
| [PHP and Ruby](references/php-and-ruby.md) | Runtime baselines, JSON strictness, generated setters, reflection, RBS, JRuby |
| [Python](references/python.md) | Runtime baselines, removed reflection APIs, field validation, formatting, recursion, NumPy, free-threading |
| [Rust and Go](references/rust-and-go.md) | Rust generated traits and views, exact-version rule, Go Opaque API and enum-prefix controls |

## Breaking-change triage

### Keep compiler, plugins, generated code, and runtimes coherent

- Never run gencode against a runtime older than the compiler/plugin that
  produced it, even when only the patch number differs.
- Match C++ and Rust gencode to the runtime exactly. Do not assume C++ ABI
  stability across minor or patch releases.
- For most other languages, gencode from runtime major V remains supported
  through V+1, but not V+2. Python gencode from 3.20.0 has an extended window.
- Do not load multiple protobuf runtime majors into one process.
- Regenerate on every release update; compatibility windows are for staged
  upgrades and existing artifacts, not a preferred steady state.

See [compatibility and lifecycle](references/compatibility-and-lifecycle.md).

### Account for language-specific package majors

The shared protobuf release is not the package major. For example, shared
release `34.1` maps to Java `4.34.1` and C# `3.34.1`. Compare the shared release
and the language package coordinate before deciding whether an upgrade is
major-breaking.

### Regenerate after removed reflection APIs

- Replace descriptor `label` access with semantic predicates such as
  `isRepeated`, `isRequired`, and `hasPresence`; removed accessors cannot be
  restored by pinning only the compiler.
- In Python, replace removed factory and symbol-database creation methods with
  `message_factory.GetMessageClass()` or `GetMessageClassesForFiles()`.
- In Objective-C, regenerate code older than 3.22 before using current runtime
  entry points.

## Build-system migration

### CMake dependency policy

The old provider switches are gone. Installed dependencies are preferred and
missing pinned dependencies may be fetched. Use:

```sh
cmake . -Dprotobuf_LOCAL_DEPENDENCIES_ONLY=ON
cmake . -Dprotobuf_FORCE_FETCH_DEPENDENCIES=ON
```

Enable protobuf test targets explicitly when building its source tests; they are
no longer part of the default CMake build. Installed CMake packages also omit
private generator headers.

### Bazel toolchains and dependencies

- Bazel 8 is the minimum for the newer build rules, and Bzlmod becomes the
  default dependency mode.
- Move from native `--proto_toolchain_for*` and `--proto_compiler` flags toward
  platform toolchain resolution with
  `--incompatible_enable_proto_toolchain_resolution`.
- Use `ProtoInfo.transitive_sources`, not the removed `transitive_imports`.
- Put Edition option-only imports in `option_deps`; this requires Bazel 8.
- Pin `@protobuf//bazel/flags:prefer_prebuilt_proto` if the changed default
  would alter reproducible compiler selection.

See [build and tooling](references/build-and-tooling.md) for flag paths and the
Windows and Python-rule transitions.

## C++ migration essentials

### Language and borrowed strings

C++17 is required. Several descriptor/name APIs now return
`absl::string_view`; do not assume `data()` is null-terminated, and copy into
`std::string` where ownership or termination is required. Edition-generated
string and enum-name APIs can also default to views.

### Arenas and repeated fields

- Use `Arena::Create`, not `Arena::CreateMessage`.
- Do not construct `RepeatedField`, `RepeatedPtrField`, or `Map` directly from
  `Arena*`; those constructors were removed.
- Validate all indices and ranges before `Get`, `ExtractSubrange`,
  `DeleteSubrange`, `UnsafeArenaExtractSubrange`, `ReleaseLast`, or
  `SwapElements`; invalid access can abort.
- Do not access an arena oneof message after clearing it. Debug/ASAN builds now
  diagnose that stale access.
- Review assumptions about `RepeatedPtrField` copies, moves, and unsafe arena
  operations after its chunked-layout change.

### Debug text is not serialization

Debug stringification redacts `debug_redact` fields, adds a randomized prefix,
and is not parseable TextFormat. Serialize with the binary format, or explicitly
use `TextFormat.printer().printToString(proto)` when unredacted parseable text is
required.

See [C++](references/cpp.md) for the full removal and generated-API tables.

## Editions and schema essentials

### Edition 2024

- C++ strings default to view behavior, and enum-name helpers can return
  `absl::string_view`.
- Strict naming-style enforcement is enabled by default.
- Visibility defaults to exported top-level symbols and local nested symbols;
  use `export` and `local` deliberately.
- Replace `java_multiple_files` with `nest_in_file_class` behavior and use
  `java_outer_classname` when the filename-derived `*Proto` name is unsuitable.
- Replace weak declarations used only for custom options with `import option`.
- Replace `ctype` with `features.(pb.cpp).string_type`.

### Edition 2026

- Field names that collide after language-specific conversion can be rejected.
- Go defaults generated APIs to Opaque; select Open or Hybrid explicitly when
  direct field access is still required.
- C++ repeated-field proxy access is opt-in, while generated C++ namespaces can
  be separated from proto packages.
- Enum values can define custom JSON strings.
- Remove `cc_api_version`, `cc_utf8_verification`, and `cc_enable_arenas` from
  schemas selecting this edition.

See [Editions and schema](references/editions-and-schema.md),
[C++](references/cpp.md), and [Rust and Go](references/rust-and-go.md).

## Runtime-focused checks

### Python

- Confirm the interpreter baseline before upgrading; newer packages require
  Python 3.10 or later.
- Stop assigning `bool` to integer or enum fields, and expect invalid
  `Timestamp`/`Duration` conversion to raise `TypeError`.
- Pass both key and value to scalar-map `setdefault`; do not call `setdefault`
  for message-valued maps.
- Set text-format recursion limits for untrusted input and test deep dynamic
  descriptors against stricter upb validation.
- Free-threaded Python is supported by upb, including fixes for lazy-init and
  repeated-field-presence races.

See [Python](references/python.md).

### Java and C#

- Expect deprecation diagnostics from generated Java `isInitialized()` when a
  message has no required fields.
- Test recursion limits for Java JSON `Any` nesting and C# JSON well-known types.
- Resolve well-known-type imports from the `include` directory shipped in
  `Google.Protobuf.Tools`.

See [Java, C#, and Objective-C](references/java-csharp-objective-c.md).

### PHP, Ruby, and JRuby

- Confirm PHP 8.2 or newer and Ruby 3.1 or newer before adopting the relevant
  runtimes.
- Treat JSON numeric, range, oneof, string, `Infinity`, and `NaN` validation as
  input-contract changes.
- Update PHP reflection to `hasPresence()` and account for typed generated
  setters and honored proto2/Editions defaults.
- JRuby uses FFI by default and remains best-effort rather than officially
  supported.

See [PHP and Ruby](references/php-and-ruby.md).

### Rust and Go

- Replace `protobuf::Optional` in generated Rust accessor integrations with the
  standard `Option`.
- Satisfy the `Send` bound now required by Rust `MessageMut`.
- Update map-trait integrations from `ProxiedInMapValue` to `MapValue`, and do
  not treat floating-point values as map keys.
- For Go Editions code, choose `API_OPEN`, `API_HYBRID`, or `API_OPAQUE`
  intentionally and stage enum-prefix removal with the generate-both mode.

See [Rust and Go](references/rust-and-go.md).

## Upgrade validation checklist

- Regenerate all checked-in artifacts with the selected compiler and plugins.
- Compile every generated-language target with warnings enabled.
- Exercise reflection and descriptor parsing, especially custom options and
  malformed dynamic descriptors.
- Test JSON parsing and serialization, default-value emission, and out-of-range
  numeric input where relevant.
- Test deeply nested binary, JSON, text-format, and well-known-type inputs under
  configured recursion limits.
- Run bounds-sensitive repeated-field and recursive `CopyFrom` tests in a debug
  or sanitizer build.
- Verify symbol visibility, generated names, file output paths, and option-only
  dependency declarations after changing Editions or build rules.

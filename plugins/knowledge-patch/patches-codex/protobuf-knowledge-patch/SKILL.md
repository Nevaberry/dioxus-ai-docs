---
name: protobuf-knowledge-patch
description: Protocol Buffers
version: "35.0"
license: MIT
metadata:
  author: Nevaberry
---


# Protocol Buffers Knowledge Patch

Use this skill when changing `.proto` schemas, upgrading `protoc` or a language
runtime, regenerating bindings, maintaining reflection code, or updating
Protobuf build rules. Inspect the repository's compiler, runtime, generated-code,
edition, language, and build-tool versions before applying advice.

## Working method

1. Identify every `protoc`, generator/plugin, runtime, and checked-in generated-code
   version in the project. Do not infer compatibility from the shared release number
   alone because language packages prepend different majors.
2. Read the declared syntax or edition and all imported feature/options files.
   Edition behavior can change generated APIs independently of runtime version.
3. Match guidance to the project's actual release. Preserve older-version behavior
   when the project has not crossed the corresponding change.
4. Regenerate bindings after compiler or edition changes. Treat generated files as
   outputs, then compile and test each consuming language.
5. Exercise malformed input, recursion limits, presence/reflection behavior, arena
   ownership, and JSON/text round trips when those surfaces are involved.

## Reference index

| Reference | Topics |
| --- | --- |
| [Compatibility, Builds, and Releases](references/compatibility-builds-and-releases.md) | Gencode/runtime rules, release numbering and support, CMake, Bazel, `protoc`, toolchains |
| [C++ Runtime and Generated APIs](references/cpp-runtime-and-generated-apis.md) | C++17, arenas, repeated fields, descriptors, debug output, bounds checks, JSON, flags |
| [Editions, Schema, and Descriptors](references/editions-schema-and-descriptors.md) | Edition 2024/2026 features, visibility, imports, naming, descriptors, custom options |
| [Java, C#, and Objective-C](references/java-csharp-and-objective-c.md) | Java generation and parsing, C# packages and recursion, Objective-C runtime migration |
| [PHP, Ruby, and Rust](references/php-ruby-and-rust.md) | Baselines, strict parsing, reflection, generated typing, RBS, Rust views and traits |
| [Python Runtime and Generated APIs](references/python-runtime-and-generated-apis.md) | Python baselines, removed APIs, maps, descriptors, formatting, upb, NumPy and text parsing |

## Upgrade blockers first

### Keep compiler, generated code, and runtime compatible

- Never run generated code against a runtime older than the compiler/plugin that
  generated it, including patch-version mismatches.
- C++ and Rust require exact generated-code/runtime release matches. C++ does not
  promise ABI stability even across minor or patch releases.
- Most other runtimes accept major `V` generated code on runtime `V` and `V+1`,
  plus older-minor generated code within the same major. Runtime `V+2` is unsupported.
- Python's descriptor-based generated code from 3.20.0 onward has an extended window
  through at least runtime 8.x.
- Do not load multiple major runtime versions into one process. Security fixes can
  require both a runtime upgrade and regeneration even inside a nominal window.

### Check language and build baselines

Before upgrading, enforce these relevant floors and build changes:

- C++ requires C++17 from release 30 onward.
- Python requires 3.9 from runtime 6.30 and 3.10 from runtime 7.34.
- PHP requires PHP 8.2 from runtime 5.34.
- Ruby 3.0 is unsupported from release 31; use Ruby 3.1 or newer.
- Protobuf 34 requires Bazel 8 and defaults dependency setup to Bzlmod.
- CMake no longer builds Protobuf's tests by default; explicitly enable them in CI
  when test targets are required.

### Replace removed reflection and runtime APIs

- Replace C++ `Arena::CreateMessage` with `Arena::Create`, `Arena::GetArena` with
  `value->GetArena()`, and `JsonOptions` with `JsonPrintOptions`.
- Replace removed descriptor label accessors with semantic queries: repetition,
  requiredness, and presence. Do not reconstruct those concepts from a legacy label.
- Python dynamic-message creation uses `message_factory.GetMessageClass()` or
  `GetMessageClassesForFiles()`; the old reflection/factory creation APIs are gone.
- Objective-C uses ordering-preserving `GPBUnknownFields`, not
  `GPBUnknownFieldSet`, and runtimes no longer support generated code older than 3.22.
- PHP uses `Google\Protobuf\Field\Kind`, `Google\Protobuf\Field\Cardinality`, and
  `Google\Protobuf\RepeatedField`; the underscored/internal types are gone.

### Stop relying on unchecked repeated-field operations

C++ repeated-field reflection no longer exposes `Reserve()`. Range and index checks
now cover `Get`, `ExtractSubrange`, `DeleteSubrange`, `UnsafeArenaExtractSubrange`,
`ReleaseLast`, and `SwapElements`; invalid access can abort. Validate positions,
counts, and nonempty assumptions before calling them.

## Edition migration quick reference

### Edition 2024

- C++ string fields default to view-style APIs, and enum-name helpers can return
  `absl::string_view`. Copy when ownership or null termination is required.
- Naming-style enforcement is strict by default. Fix names or explicitly request
  legacy style where supported.
- Top-level symbols default to exported while nested symbols default to local;
  use `export` and `local` deliberately.
- Replace weak declarations with `import option`; place option imports after normal
  imports and put them in Bazel `option_deps` (Bazel 8+).
- Replace `ctype` with `features.(pb.cpp).string_type`.
- Java generates classes in separate files by default. `nest_in_file_class` replaces
  `java_multiple_files`, and the default outer name is the camel-cased filename plus
  `Proto` unless `java_outer_classname` overrides it.

### Edition 2026 features available to schemas

- Go defaults to the Opaque API in Editions 2024 and 2026. Select `API_HYBRID` for
  a staged field-to-accessor migration or `API_OPEN` to preserve direct fields.
- C++ can opt into repeated-field proxy accessors with
  `features.(pb.cpp).repeated_type = PROXY`; the default stays `LEGACY`.
- Go can keep, strip, or temporarily generate both forms of enum prefixes with
  `features.(pb.go).strip_enum_prefix`.
- Enum values can set a custom JSON spelling with `(pb.enumvalue.json).string`.
- C++ bindings can set a namespace independent of the proto package with
  `(pb.file.cpp).namespace`.
- Remove `cc_api_version`, `cc_utf8_verification`, and `cc_enable_arenas` from
  Edition 2026 schemas.

## C++ migration decisions

### Borrowed strings

Descriptor names, `MessageLite::GetTypeName`, and
`UnknownField::length_delimited` return `absl::string_view`. Keep views only while
their source remains alive; copy to `std::string` for storage or C APIs. Never assume
`data()` is null-terminated.

### Arenas and containers

Do not call the removed arena-taking constructors for `RepeatedField`,
`RepeatedPtrField`, or `Map`. Review copy/move assumptions around the chunked
`RepeatedPtrField` layout. Use `Arena::Ptr` and `Arena::UniquePtr` when explicit
smart-pointer forms fit arena-associated values. In debug/ASAN builds, clearing an
arena oneof invalidates and poisons the cleared message; later access is a real
use-after-free bug.

### Debug and serialization output

Debug-string APIs redact `debug_redact` fields, add a randomized process prefix,
and are not parseable TextFormat. Use them only for logs. Use binary encoding for
serialization or an explicit TextFormat printer when parseable unredacted text is
intentionally required.

## Reflection and presence

Treat cardinality, requiredness, optional-keyword state, oneof membership, and
presence as distinct questions:

- repetition: `isRepeated` / `is_repeated()`;
- requiredness: `isRequired` / `is_required()`;
- presence: `hasPresence` / `has_presence()`;
- proto3 optional keyword: `hasOptionalKeyword` where still supported;
- real oneof membership: `getRealContainingOneof` where applicable.

For Editions, singular fields no longer gain useful semantic distinctions from a
legacy label. PHP's broken `hasOptionalKeyword()` is gone in favor of
`hasPresence()`; Objective-C replaces `-[GPBFieldDescriptor optional]` with
`!required && fieldType == GPBFieldTypeSingle`.

## Parser hardening checklist

When accepting untrusted input:

- set recursion controls for Python text format and account for recursion checks in
  nested Python/upb messages, Java JSON `Any`, and C# JSON well-known types;
- expect Ruby/PHP JSON numeric fields to reject nonnumeric strings;
- expect PHP JSON parsing to reject range errors, fractional values for integer
  fields, duplicate oneof members, and non-string values for string fields;
- expect upb to reject malformed descriptor `syntax` or `edition` values;
- expect C++ `BinaryToJson` to report failures while skipping malformed unknown
  fields rather than silently succeeding.

## Verification checklist

- Confirm all generated files come from the intended compiler/plugin release.
- Compile C++ with C++17 and warnings that surface newly `[[nodiscard]]` results.
- Test reflection against repeated, required, present, proto3-optional, and oneof
  fields rather than asserting legacy labels.
- Test invalid bounds and ownership paths in debug and sanitizer builds.
- Test JSON numeric limits, duplicate oneofs, non-finite numbers, deep nesting, and
  text-format recursion limits.
- Check serialized ordering only when the API promises it; do not parse debug text.
- Use absolute `protoc` file output paths.
- For CMake/Bazel changes, pin dependency and toolchain selection where reproducible
  builds depend on a prior default.

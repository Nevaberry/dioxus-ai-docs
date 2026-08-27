---
name: c-cpp-knowledge-patch
description: C and C++
version: null
license: MIT
metadata:
  author: Nevaberry
---


# C and C++ Compatibility Guide

Use this skill when upgrading Clang, GCC, libstdc++, compiler-facing tools, or target-specific C and C++ builds. It focuses on source, ABI, optimizer, diagnostics, library, tooling, and offload changes that are easy to miss when a build merely continues to compile.

## Working method

1. Identify the compiler family and exact release used by every compile and link step.
2. Read the project manifest and build configuration before assuming a language dialect, standard-library mode, target, or sanitizer set.
3. Pin language modes explicitly; compiler defaults are not a portability contract.
4. Treat object files, static libraries, modules, plugins, and generated bindings as compatibility boundaries.
5. Prefer project code, compiler probes, and tests when behavior differs across targets or newer releases.
6. Open the topic reference that matches the task, then apply only the compiler- and target-specific guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Language and standards](references/language-and-standards.md) | C23, C2y, C++20/23/26/29, constexpr, templates, reflection, modules, conformance limits |
| [Migration and ABI](references/migration-and-abi.md) | Default dialect changes, removals, source breaks, mangling, record layout, mixed-object hazards |
| [Diagnostics and safety](references/diagnostics-and-safety.md) | Warnings, analyzers, aliasing, overflow, lifetime checks, sanitizers, suppression behavior |
| [Code generation and builtins](references/codegen-and-builtins.md) | Optimizer controls, assembly, LTO, attributes, allocation contracts, compiler builtins |
| [Libraries and tooling](references/libraries-and-tooling.md) | libstdc++, modules, diagnostic formats, clang-format, libclang, Python bindings, plugins |
| [Targets and offload](references/targets-and-offload.md) | Architecture defaults, ABI details, CUDA/HIP, OpenMP, OpenACC, WebAssembly, OpenCL |

## Highest-priority upgrade checks

### Pin both C and C++ dialects

GCC changed its implicit C mode to GNU C23 and later changed its implicit C++ mode to GNU C++20. Add explicit `-std=` choices to reproducible builds, including configure tests, generated build rules, examples, and plugin test harnesses.

For C, audit empty parameter lists and identifiers that became keywords. For C++, audit code that was relying on pre-C++20 parsing, overload, and library behavior.

Do not infer full standards conformance from acceptance of `-std=c23`, `-std=c++23`, `-std=c++2c`, or `-std=c++2d`. Probe required facilities and preserve target-specific fallbacks.

### Rebuild across ABI boundaries

Several Clang upgrades alter mangling, C++ record returns, Arm argument passing, or Windows destructor entry points. GCC and libstdc++ changes affect Solaris integer identities, a narrow `std::variant` layout, and multiple formerly experimental C++20 components.

When affected types or classes cross a boundary, rebuild the complete boundary together:

- application objects and static libraries;
- shared-library producers and consumers;
- plugins and their host compiler;
- generated bindings and native extensions;
- module interfaces and consumers.

Use compatibility switches only as temporary migration aids. Record them in the build configuration and remove them after all producers and consumers are rebuilt.

### Audit undefined-behavior assumptions

Clang performs stricter pointer type-based alias analysis and more aggressive pointer-overflow and null-pointer-arithmetic optimization. Avoid overflow tests based on forming an overflowing pointer. Validate offsets before addition or use integer-domain checks, and run the relevant sanitizers during migration.

Do not depend on whole-object bytes being zero after automatic union `{0}` initialization. Padding may remain indeterminate; initialize or clear representation storage deliberately before hashing, serialization, comparison, or exposure.

Do not copy merely relocatable C++ objects with `memcpy`. Use the supported relocation builtin where applicable, and account for the later removal of explicit relocatability marking.

### Treat new errors as migration signals

Clang upgrades make several formerly tolerated constructs errors by default, including incompatible C pointer types, chained comparisons, invalid GNU assembly casts, some template headers, and C++ array comparisons. Fix the source when practical; if staged migration requires demotion, use the narrow warning group's `-Wno-error=` form.

GCC warning levels for unused-but-set variables and parameters became more sensitive. Level 1 is the closest staged-migration setting, but the long-term fix is to remove writes whose prior value is never observed.

### Move machine diagnostics to SARIF

GCC first deprecated and then removed the JSON value of `-fdiagnostics-format=`. Convert parsers and CI consumers to SARIF. When multiple outputs are needed, use the additive or explicit output controls supported by the relevant release.

### Make modules build-system aware

Clang's reduced BMI spelling stabilized and reduced BMIs later became the default. Two-phase module builds must understand the reduced artifact and must not depend on implementation details intentionally discarded from it.

GCC can prebuild its experimental standard modules before other inputs. Treat those module artifacts as compiler- and library-specific generated products, not portable cached objects.

## Task-oriented guidance

### Upgrading Clang

1. Read [Migration and ABI](references/migration-and-abi.md) for mixed-object hazards and removed compatibility paths.
2. Read [Diagnostics and safety](references/diagnostics-and-safety.md) for default-error, analyzer, aliasing, and sanitizer changes.
3. Read [Code generation and builtins](references/codegen-and-builtins.md) if the code uses compiler builtins, inline assembly, allocation hooks, or optimizer flags.
4. Read [Libraries and tooling](references/libraries-and-tooling.md) for modules, embedding libraries, formatter schemas, AST tooling, or Python bindings.
5. Read [Targets and offload](references/targets-and-offload.md) for architecture, CUDA/HIP, OpenMP, OpenACC, OpenCL, or WebAssembly builds.

### Upgrading GCC or libstdc++

1. Pin the intended C and C++ modes before investigating downstream failures.
2. Regenerate old Autoconf outputs if they inject an unintended C++ mode.
3. Add direct standard-library includes instead of relying on transitive headers.
4. Review debug-assertion, allocator-assumption, random-sequence, and library ABI changes.
5. Migrate diagnostic consumers from JSON to SARIF.
6. Review target removals, Solaris changes, and AArch64 deprecations for platform builds.

### Maintaining a stable binary interface

Inventory every type that crosses the interface and every compiler/runtime combination that produces or consumes it. Pay particular attention to:

- virtual destructors under the Windows C++ ABI;
- record returns and explicitly aligned empty classes;
- template or construction-vtable mangling;
- fixed-width integer aliases on Solaris;
- library types whose formerly experimental representation changed;
- module and plugin interfaces tied to compiler internals.

Add a clean-build job that rejects stale object files. ABI compatibility flags can keep an emergency build working, but they do not make arbitrary mixtures safe.

### Adopting newer language facilities

Check [Language and standards](references/language-and-standards.md) for the exact implemented subset. Distinguish these cases:

- a standard feature implemented only by one compiler;
- an extension accepted in older language modes;
- syntax accepted while lowering or runtime support is incomplete;
- a feature-test macro that lags actual implementation;
- a proposal implemented and later rolled back or revised.

Use small configure-time compile probes for required syntax and semantics. For ABI-sensitive facilities, also link and run a probe built through the real toolchain.

### Hardening and sanitizer work

Use [Diagnostics and safety](references/diagnostics-and-safety.md) to choose explicit sanitizer groups. In particular, undefined-behavior sanitization no longer implies virtual-pointer checks, and optimizer merging can reduce the distinct trap reasons visible to a debugger.

Keep suppression mappings ordered deliberately: newer Clang uses the last matching rule. Review ignorelists when adopting positive entries or finer overflow and local-bounds controls.

Use realtime checks only around functions whose nonblocking contract is meaningful, and treat the type sanitizer as experimental. Allocation-token instrumentation is specialized allocator tooling, not a general memory-safety replacement.

### Compiler integration and formatting tools

Read [Libraries and tooling](references/libraries-and-tooling.md) before upgrading formatter configuration, libclang consumers, Python bindings, AST matchers, embedded frontend tools, or GCC plugins.

Do not rely on transitive compiler-library linkage. Link the driver/options libraries used directly. Expect bindings to distinguish absence with `None` or empty strings according to the particular API and release, and handle reparse failures as exceptions.

### Architecture and offload builds

Read [Targets and offload](references/targets-and-offload.md) before changing a target compiler. Verify:

- selected CPU, architecture, ABI, vector width, and code model;
- runtime compatibility for GPU code-object or RDC formats;
- target-specific feature macros in each offload compilation;
- deprecated target triples and feature-flag spellings;
- frontend-only language support versus executable lowering;
- OpenMP runtime build assumptions and address-mapping behavior.

Do not assume an `asm goto` label is a valid register-controlled branch target under branch-target enforcement. Do not assume a header-only feature macro describes the currently active offload target.

## Verification checklist

- [ ] Compiler family and exact release are recorded for compile and link steps.
- [ ] C and C++ language modes are explicit.
- [ ] Configure-generated flags select the intended language mode.
- [ ] Full clean rebuild covers every affected ABI boundary.
- [ ] Removed options, targets, headers, tools, checkers, and matchers are replaced.
- [ ] Warning demotions are narrow, documented, and temporary.
- [ ] Alias, overflow, null arithmetic, padding, lifetime, and relocation assumptions are tested.
- [ ] Machine-readable diagnostics use supported formats.
- [ ] Module artifacts are rebuilt and build-system compatible.
- [ ] Standard-library includes name their owning headers directly.
- [ ] Feature probes cover facilities whose standards tables remain partial.
- [ ] Sanitizer groups and ignorelists are selected explicitly.
- [ ] Target CPU, ABI, vector width, feature macros, and runtime requirements are verified.
- [ ] Formatter, libclang, AST, Python, plugin, and embedding integrations have dedicated tests.
- [ ] CUDA/HIP, OpenMP, OpenACC, OpenCL, and WebAssembly assumptions are checked where relevant.

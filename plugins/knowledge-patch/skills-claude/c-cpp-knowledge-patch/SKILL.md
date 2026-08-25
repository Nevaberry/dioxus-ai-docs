---
name: c-cpp-knowledge-patch
description: C and C++
version: null
license: MIT
metadata:
  author: Nevaberry
---


# C and C++ compatibility guidance

Use this skill when upgrading Clang, GCC, libclang, libstdc++, or C/C++
language modes; diagnosing a compiler-version regression; changing modules,
sanitizers, static analysis, formatting, offloading, or target options; or
reviewing an ABI boundary built with different toolchain versions.

Treat the project as the source of truth. Inspect its compiler constraints,
dialect flags, target triples, standard-library selection, warning policy,
sanitizer configuration, module pipeline, and ABI consumers before applying a
compatibility switch. Prefer a source migration or a consistent rebuild over
leaving a legacy switch in place indefinitely.

## Topic index

| Reference | Read when working on |
| --- | --- |
| [C language and standards](references/c-language-and-standards.md) | C23/C2y modes, C compatibility, declarations, initialization, and conformance gaps |
| [C++ language and modules](references/cpp-language-and-modules.md) | C++20/23/26/29 features, constexpr, templates, modules, coroutines, and dialect defaults |
| [Diagnostics and tooling](references/diagnostics-and-tooling.md) | warnings, machine-readable diagnostics, clang-format, libclang, AST matchers, plugins, and the Static Analyzer |
| [Libraries, builtins, and attributes](references/libraries-builtins-and-attributes.md) | libstdc++, builtins, annotations, format checking, and allocation contracts |
| [Migration and ABI](references/migration-and-abi.md) | mixed compiler objects, mangling, record layout, removed compatibility paths, and library ABI transitions |
| [Optimization, debugging, and sanitizers](references/optimization-debugging-and-sanitizers.md) | aliasing, overflow, floating point, LTO, debug information, profiles, and sanitizer controls |
| [Targets, offloading, and OpenMP](references/targets-offloading-and-openmp.md) | CPU/OS targets, CUDA/HIP, OpenACC, WebAssembly, OpenMP, and architecture flags |

## Upgrade triage: breaking changes first

### Pin the intended language dialect

- GCC changes its default C and C++ dialects across major releases. Add an
  explicit `-std=` selection to build configuration instead of accepting a
  new default accidentally.
- In C, a declaration such as `f()` has different meaning under C23, and
  identifiers such as `bool`, `true`, `false`, `nullptr`, and `thread_local`
  may become keywords.
- In C++, check configure-generated flags as well as handwritten build files;
  older Autoconf can force an unexpectedly old dialect with a new GCC.
- A compiler accepting `-std=c23`, `-std=c2y`, `-std=c++23`, `-std=c++2c`, or
  `-std=c++2d` does not imply complete implementation of that standard. Check
  the precise feature, feature-test macro, target, and library support.

### Do not mix incompatible ABI generations

- Rebuild all objects across boundaries affected by changed return
  conventions, destructor variants, mangling, record layout, fundamental type
  identity, or standard-library object state.
- Clang compatibility flags can bridge particular transitions, but each flag
  addresses only its documented ABI change; it is not a general mixed-version
  guarantee.
- On Windows, take special care with virtual destructors and `::delete` when
  mixing Clang-generated objects. Wrong deallocator selection can corrupt
  memory.
- On Solaris, changed `int8_t` identity changes C++ mangling. On AArch64, Arm,
  LoongArch, and selected Windows/Itanium-layout cases, inspect the targeted
  layout and calling-convention notes before shipping binaries.
- libstdc++ ABI changes can affect random-number reproducibility, `variant`,
  C++20 synchronization and formatting types, stop tokens, and range adaptors.

### Audit pointer assumptions

- Strict type-based alias analysis and pointer-overflow optimization can expose
  undefined behavior that previously appeared to work.
- Do not use `ptr + offset < ptr` as an overflow check. Validate the integer
  offset before pointer arithmetic or use a suitable integer representation.
- Avoid forming member addresses through null pointers, including in constant
  expressions, and avoid depending on general null-pointer arithmetic.
- Use compatibility flags only while migrating. Sanitizers can help find the
  affected code, but they do not make unrelated undefined behavior portable.

### Revalidate C++20 module builds

- Reduced BMIs are the default in newer Clang. Two-phase module builds must
  consume reduced BMIs correctly and must not depend on implementation details
  intentionally discarded from them.
- Module-level lookup and proposal support differ across releases. Test the
  exact compiler and build-system pipeline rather than inferring support from
  the language-mode flag.
- Treat standard-module workflows as compiler-specific and experimental where
  documented; build their prerequisite artifacts before translating eligible
  header includes into imports.

### Rebaseline diagnostics deliberately

- Some former warnings are errors by default, including selected incompatible
  pointer conversions, chained comparisons, GNU assembly casts, and C++
  compatibility cases.
- Demote a diagnostic with its narrow `-Wno-error=` spelling only after
  determining that the construct is intentional and safe.
- GCC machine-readable diagnostic consumers should use SARIF; the former JSON
  diagnostic format is removed in newer GCC.
- Warning groups change membership. Pin individual diagnostics when a stable
  CI contract matters instead of assuming `-Wall` or `-Wextra` is fixed.
- Warning-suppression mapping precedence is order-sensitive in newer Clang;
  place the intended winning rule last.

### Stop relying on incidental library behavior

- Include the header that owns each libstdc++ name; do not rely on transitive
  inclusions.
- Remove obsolete C++ compatibility headers and constrain iterator-adaptor
  operations to capabilities the wrapped iterator actually provides.
- Do not assume union `{0}` clears padding. Never serialize, hash, compare, or
  expose padding on that basis.
- Debug assertions may now be enabled in unoptimized libstdc++ builds. Fix
  violated preconditions before considering a temporary opt-out.

### Remove retired targets, flags, and APIs

- Verify that configured targets still exist and that fallback CPU defaults
  have not changed.
- Replace removed Clang tools, analyzer checker names, AST matchers, Python
  binding sentinels, GCC plugin diagnostics interfaces, and AVX10 flag
  spellings rather than probing them indefinitely.
- Direct use of compiler implementation builtins is especially fragile; use
  the documented header intrinsic or retained builtin when one exists.

## High-value capability guide

### C language work

- C23 adds `#embed`, improved enumerations, standard keyword changes, and new
  headers or macros, but several proposal-level gaps and tag-compatibility edge
  cases remain.
- C2y modes expose features incrementally, including named loops, new escape
  and octal syntax, generic-selection extensions, and expression-level static
  assertions. Check the compiler-specific status before depending on them.
- For counted flexible arrays or pointer members, use the documented
  `counted_by` forms and initialize the count before sanitizer-checked access.
- GNU C supplies additional integer-limit operators, empty-initialized
  variable-size compound literals, and safer noncapturing nested-function
  behavior where supported.

### C++ language and library work

- C++26 implementations add substantial syntax and library surface, but
  reflection may require an explicit compiler flag and several adopted
  facilities remain absent in other toolchains.
- Clang's trivial-relocation surface changed after initial rollout. Do not use
  removed explicit-marking facilities; distinguish relocation from `memcpy` of
  a non-trivially-copyable object.
- New overload, constraint-normalization, and strict-integral-trait behavior
  can change which template is instantiated or selected even when source code
  is unchanged.
- Use the dedicated reference to distinguish core-language support from
  standard-library availability and target-dependent coroutine behavior.

### Builtins and annotations

- Check availability with the compiler's feature-query mechanism and preserve
  a portable fallback when using new elementwise, vector, comparison,
  reflection-adjacent, allocation, stack-address, or lifetime builtins.
- Respect the exact signature: some builtins change parameter types across
  releases, and fixed-vector or constexpr support may be narrower than runtime
  support.
- Use allocation, nullability, format-forwarding, lifetime, function-effect,
  and tail-call annotations to express real contracts, not to silence evidence
  that the code violates them.

### Debugging and sanitizer work

- Request `-fsanitize=vptr` explicitly when it is required; it is no longer
  implied by Clang's undefined-behavior group.
- Realtime and type sanitizers cover different risks from conventional UBSan.
  Select them explicitly and understand whether failure traps, recovers, or
  exits nonzero.
- For optimized debugging, variable-liveness and key-instruction controls can
  improve source fidelity, while sanitizer trap-reason and merge controls can
  preserve distinct failure explanations.
- Profile, ThinLTO distribution, incremental LTO, speculative
  devirtualization, and floating-point models all affect generated code; record
  these choices as build inputs.

### Tool integrations

- Update formatter configuration when an option changes type or an enum value
  or key is renamed. Validate formatting on representative C, C++, and header
  files after the upgrade.
- Adapt libclang and Python callers to new null/failure behavior before
  enabling new layout, method, assembly, or fully-qualified-name queries.
- Update analyzer checker names and configuration rather than enabling both old
  and new spellings.
- Downstream Clang embedding tools must link the libraries that now own the
  APIs they call; former transitive dependencies are not contracts.

### Targets and offloading

- Treat CPU-feature defaults, code-object versions, runtime minimums, linker
  relaxation, frame-pointer behavior, and ABI alignment as deployment inputs.
- CUDA's newer offloading path has a distinct RDC format; do not assume it is
  interchangeable with another producer's device objects.
- OpenACC frontend acceptance does not imply executable code generation.
- For OpenMP, align syntax, runtime construction, mapping behavior, and version
  selection; compiler acceptance alone does not validate device execution.

## Working method

1. Identify compiler, standard library, linker, target, dialect, and relevant
   tool versions from manifests and build output.
2. Start with the breaking-change sections above, then read the topic reference
   for the subsystem being modified.
3. Compare every compatibility flag with the exact failure it addresses.
4. Rebuild all ABI participants when layout, mangling, calling convention, or
   library state changes.
5. Run compile-only probes, unit tests, sanitizer tests, module builds, and
   target-specific integration tests in proportion to the change.
6. Document intentional dialect, warning, sanitizer, ABI, and target choices in
   the build configuration so future upgrades do not rediscover them.

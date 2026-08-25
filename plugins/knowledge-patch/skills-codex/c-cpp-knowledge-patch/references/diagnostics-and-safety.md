# Diagnostics and Safety

Use this reference for optimizer-sensitive safety assumptions, compiler warning migrations, Static Analyzer changes, and sanitizer selection.

## Pointer and object-model safety

### Stricter pointer alias analysis

Clang 20 (`clang-20.1`) emits distinct type-based alias-analysis tags for incompatible pointer types by default. Strict-aliasing violations can therefore change behavior without a diagnostic after an upgrade. Fix the aliasing violation; `-fno-pointer-tbaa` restores the earlier optimization behavior only as a migration aid. Experimental `-fsanitize=type` can detect violations of C and C++ type-based aliasing rules.

### Pointer overflow and null arithmetic

Clang 20 (`clang-20.1`) more aggressively treats pointer-addition overflow as undefined. Checks such as `ptr + offset < ptr` can fold to false. Validate the offset before pointer addition, use integer-domain arithmetic where appropriate, or diagnose the path with `-fsanitize=pointer-overflow`.

`-fwrapv` now covers only signed integers, `-fwrapv-pointer` covers pointers, and `-fno-strict-overflow` implies both. Pointer-overflow sanitization no longer reports `NULL + 0` in C.

Clang 21 (`clang-21.1`) also optimizes null-pointer arithmetic more aggressively. Old-style `offsetof` idioms remain preserved, while `-fwrapv-pointer` or `-fno-delete-null-pointer-checks` defines the arithmetic more generally.

### Lifetime diagnostics

Clang 20 (`clang-20.1`) rejects `[[clang::lifetimebound]]` on types, unnamed parameters, explicit-object member functions, and parameters or implicit objects of void-returning functions instead of ignoring it. The compiler automatically applies the annotation to parameters of `std::span` and `std::string_view` constructors, producing additional dangling-reference diagnostics.

`-Wdangling-assignment-gsl` is enabled by default in the same release.

### Union padding is not initialized by `{0}`

For automatic C or C++ unions, GCC 15 (`gcc-15.1-porting`) initializes the first member with `{0}` but does not guarantee that every padding byte becomes zero. Do not hash, serialize, compare, or expose the entire representation on that assumption. Use `{}` where supported, clear representation storage explicitly, or temporarily use `-fzero-init-padding-bits=unions` as a controlled compatibility measure.

## Warning and error migrations

### Clang 20 warning groups

Clang 20 (`clang-20.1`) adds or changes these controls:

- `-Warray-compare` diagnoses array comparisons before C++20.
- `-Warray-compare-cxx26` diagnoses them from C++26 and is an error by default.
- `-Wnontrivial-memcall` checks memory-function destinations that are not trivially copyable and is implied by `-Wnontrivial-memaccess`.
- `-Winvalid-gnu-asm-cast` is enabled and defaults to an error.
- `-fheinous-gnu-extensions` is deprecated as an alias for demoting that assembly diagnostic.

### Clang 21 compatibility diagnostics

Clang 21 (`clang-21.1`) makes chained comparisons such as `a < b < c`, and fold expressions over comparison operators, errors by default. `-Wno-error=parentheses` narrowly demotes them.

`-Wextra` now includes `-Wunterminated-string-initialization`. C can mark an intentionally non-terminated array with `nonstring`; the C++-compatibility form cannot be suppressed that way. `-Wc++-compat` adds checks for implicit `void *` and integer-to-enum conversions, C++ keywords and hidden tags, tentative definitions, default initialization of `const` objects, and jumps bypassing initialization. `-Wundef-true` is enabled by default before C23.

Other additions are `-Wunique-object-duplication`, `-Wshift-bool`, `-Wunnecessary-virtual-specifier` under `-Wextra`, and `-Wunsafe-buffer-usage-in-libc-call`. Thread-safety analysis adds opt-in `-Wthread-safety-pointer` and reentrant capabilities; the pointer check does not perform alias analysis.

### Clang 22 warning behavior

Clang 22 (`clang-22.1`) makes incompatible C pointer types an error by default. Prefer fixing the type mismatch; use `-Wno-error=incompatible-pointer-types` only for staged migration.

Pedantic function-effect redeclaration checks move to `-Wfunction-effect-redeclarations`, while `-Wperf-constraint-implies-noexcept` leaves `-Wall`. New warnings include `-Walloc-size`, `-Wenum-compare-typo`, and `-Wshadow-header`. `ACQUIRED_BEFORE` and `ACQUIRED_AFTER` no longer need `-Wthread-safety-beta`.

`-Wformat-nonliteral` can identify wrappers that lack `format` or `format_matches` annotations. Use `__attribute__((format_matches(printf, 1, "%x %s")))` from Clang 21 (`clang-21.1`) to declare that a forwarded format parameter must match a reference format even when the wrapper receives no matching arguments.

### Suppression mapping precedence

Clang 22 (`clang-22.1`) resolves overlapping `--warning-suppression-mappings=` entries by the last match rather than the longest match. Reorder existing mapping files so the intended most-specific policy wins last.

### GCC warning controls

GCC 15 (`gcc-15.1`) adds `-Wheader-guard`, enabled by `-Wall`, plus `-Wtrailing-whitespace=` and `-Wleading-whitespace=` for whitespace policy.

GCC 16 (`gcc-16.1-porting`) makes `-Wunused-but-set-variable` and `-Wunused-but-set-parameter` sensitivity level 3 by default, including through `-Wall` or `-Wextra`. Level 2 stops treating increment/decrement as use; level 3 also stops treating compound assignment as use when the old value is not read on the right-hand side. Level 1 is closest to older behavior:

```text
-Wunused-but-set-variable=1 -Wunused-but-set-parameter=1
```

GCC 16 (`gcc-16.1`) can display hierarchical C++ diagnostics with nested explanations. Use `-fno-diagnostics-show-nesting` or `-fdiagnostics-plain-output` for tools or users that require the former flat presentation.

## Static Analyzer changes

### Function effects, suppression, and checker moves

Clang 20 (`clang-20.1`) teaches the analyzer to verify `nonblocking` and `nonallocating` effects and adds `-warning-suppression-mappings` for per-file suppression. The Z3 cross-check timeout returns to 15 seconds from 300 ms; rlimit and equivalence-class timeout defaults become disabled.

Checker names move as follows:

- `alpha.unix.Chroot` to `unix.Chroot`;
- `alpha.core.PointerSub` to `security.PointerSub`;
- alpha taint checkers to `optin.taint.*`;
- the two nondeterministic-pointer checkers to clang-tidy's `bugprone-nondeterministic-pointer-iteration-order`.

### Fixed-address and array-bounds analysis

Clang 21 (`clang-21.1`) understands `[[clang::assume]]`, adds `core.FixedAddressDereference`, and graduates `alpha.security.ArrayBoundV2` to `security.ArrayBound`. The old alpha checker and `optin.cplusplus.VirtualCall:PureOnly` option are removed.

### Null arithmetic, immutable stores, and va_list

Clang 22 (`clang-22.1`) adds `core.NullPointerArithm` and `alpha.core.StoreToImmutable`. All `valist.*` behavior moves to `security.VAList`, while `alpha.core.CastSize` is removed. `[[clang::suppress]]` works in primary templates, and analyzer model paths and taint configuration honor virtual-file-system overlays.

## Sanitizers

### Realtime and type checks

Clang 20 (`clang-20.1`) introduces `-fsanitize=realtime`, which reports unsafe calls such as allocation or mutex locking while executing a `[[clang::nonblocking]]` function and exits nonzero. `-fsanitize=type` is experimental and checks type-based aliasing violations.

### Finer UBSan controls

Clang 20 (`clang-20.1`) adds `-fsanitize-undefined-ignore-overflow-pattern=` values `add-signed-overflow-test`, `add-unsigned-overflow-test`, `negated-unsigned-const`, `unsigned-post-decr-while`, `all`, and `none`. Special-case lists gain a `type` prefix for integer-overflow, truncation, and enum checks.

Other controls include `-f[no-]sanitize-{trap,recover}=local-bounds` and `-f[no-]sanitize-merge`.

Clang 21 (`clang-21.1`) stops including `vptr` in `-fsanitize=undefined`; request `-fsanitize=vptr` explicitly. Ignorelists can contain positive entries such as `src:*=sanitize`, with equivalent `type`, `fun`, `global`, and `mainfile` forms.

### Trap reasons and sanitizer-aware code

Clang 22 (`clang-22.1`) emits detailed trapping-UBSan reasons into DWARF by default. Choose `basic` or `detailed` with `-fsanitize-debug-trap-reasons=`, disable with `-fno-sanitize-debug-trap-reasons`, and use `-fno-sanitize-merge=` or `-O0` when optimization merges distinct reasons.

`__builtin_allow_sanitize_check("name")` reports whether a supported address, hardware-address, memory, or thread sanitizer is active for the current function after inlining, while respecting `no_sanitize`.

### Allocation tokens

Clang 22 (`clang-22.1`) adds `-fsanitize=alloc-token` to tag allocation functions for allocator-level heap organization. Controls include `-falloc-token-max=`, `-fsanitize-alloc-token-fast-abi`, and `-fsanitize-alloc-token-extended`; `__builtin_infer_alloc_token(args...)` computes the inferred token for allocation arguments at compile time.

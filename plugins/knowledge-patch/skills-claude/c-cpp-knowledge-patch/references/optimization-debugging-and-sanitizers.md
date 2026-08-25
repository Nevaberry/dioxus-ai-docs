# Optimization, debugging, and sanitizers

Use this reference when an upgrade changes optimized behavior, floating-point
assumptions, LTO or profile workflows, debug information, or sanitizer
coverage and reporting.

## Aliasing and pointer arithmetic

### Type-based pointer alias analysis

Clang 20 emits distinct type-based alias-analysis tags for incompatible pointer
types by default (`clang-20.1`). Strict-aliasing violations can therefore
change behavior without a diagnostic after an upgrade. Fix the object access
or representation. `-fno-pointer-tbaa` restores earlier analysis behavior only
as a migration aid.

Experimental `-fsanitize=type` can diagnose C/C++ type-based aliasing
violations at run time (`clang-20.1`). Evaluate its experimental status and
coverage separately from ordinary undefined-behavior checks.

### Pointer overflow

Clang 20 more aggressively treats pointer-addition overflow as undefined, so a
check such as `ptr + offset < ptr` can fold to false (`clang-20.1`). Validate
the integer offset before forming the pointer, use a suitable integer address
representation where legitimate, or diagnose with
`-fsanitize=pointer-overflow`.

`-fwrapv` now covers signed integers only. `-fwrapv-pointer` covers pointers,
and `-fno-strict-overflow` implies both. Choose the narrowest temporary switch
that matches required legacy semantics.

Clang 21 optimizes arithmetic on null pointers more aggressively
(`clang-21.1`). Old-style `offsetof` idioms remain recognized, while
`-fwrapv-pointer` or `-fno-delete-null-pointer-checks` defines such arithmetic
more generally. Prefer standard offset facilities and valid objects.

With branch-target enforcement, `asm goto` labels are no longer guaranteed to
start with `bti` or `endbr64`. A register-controlled indirect branch must not
target them.

## Floating-point models

Clang 20 makes `-ffp-model=fast` less aggressive: it no longer assumes
finite-only math and uses promoted complex division where possible
(`clang-20.1`). `-ffp-model=aggressive` selects the former fast behavior.
Rebaseline numeric, exception, infinity/NaN, and complex-arithmetic tests when
changing models.

## Code generation and LTO

### Static destructor registration

Clang 20's `-fc++-static-destructors={all,thread-local,none}` controls which C++
static destructors are registered (`clang-20.1`). `all` is the default;
`none` is equivalent to `-fno-c++-static-destructors`. Ensure resource lifetime
and shutdown behavior match the chosen mode.

### Incremental and distributed LTO

GCC 15 adds incremental link-time optimization through `-flto-incremental=`
(`gcc-15.1`). Treat its cache as a derived artifact tied to toolchain and
inputs.

Clang 21 adds `-fthinlto-distributor=` and
`-Xthinlto-distributor=` for externally distributed ThinLTO backends
(`clang-21.1`). Record distributor configuration in reproducible build inputs.

### Speculative devirtualization and matrix layout

Clang 22's `-fdevirtualize-speculatively` enables speculative virtual-call
devirtualization that is otherwise disabled (`clang-22.1`). Validate dynamic
type assumptions and performance on representative workloads.

`-fmatrix-memory-layout={column-major,row-major}` selects Clang matrix-type
storage order. It is layout-significant at interfaces and in serialized or
device-visible storage.

## Optimized debugging and profiles

### Variable liveness

Clang 20's `-fextend-variable-liveness=all` retains all user variables and
`this` for optimized debugging; `=this` limits it to the C++ implicit object
(`clang-20.1`). Clang 21 makes `-Og` enable variable-liveness extension by
default (`clang-21.1`). Measure code-size and optimization effects where they
matter.

### Key-instruction debug information

Clang 21 adds DWARF-only `-gkey-instructions` (`clang-21.1`). Clang 22 enables
it by default for optimized plain C/C++ with DWARF (`clang-22.1`). Debug-info
size and stepping output may change after the upgrade.

### Profiles and precompiled headers

Clang 21 adds `-fprofile-continuous` and `-ignore-pch` (`clang-21.1`). Continuous
profiles require a collection and merge workflow that tolerates incremental
updates; `-ignore-pch` must be an intentional choice when diagnosing or
bypassing a precompiled header.

### Constexpr evaluation limits

Clang 22 interprets `-fconstexpr-steps=0` as no evaluation-step limit
(`clang-22.1`). Unlimited evaluation can consume substantial build resources;
use it only for trusted source and when the default cap is the actual blocker.

## Realtime and type sanitizers

Clang 20's `-fsanitize=realtime` reports unsafe library calls such as allocation
or mutex locking while a `[[clang::nonblocking]]` function runs, and exits
nonzero (`clang-20.1`). Its contract is execution-context specific; annotate
only code intended to obey realtime constraints.

Experimental `-fsanitize=type` detects violations of C/C++ type-based aliasing
rules (`clang-20.1`). Keep it distinct from compile-time alias-analysis flags
and conventional UBSan groups.

## UBSan and related controls

### Granular overflow exclusions

Clang 20 adds
`-fsanitize-undefined-ignore-overflow-pattern=` values
`add-signed-overflow-test`, `add-unsigned-overflow-test`,
`negated-unsigned-const`, `unsigned-post-decr-while`, `all`, and `none`
(`clang-20.1`). Use narrow exclusions for recognized idioms rather than
blanket suppression.

Sanitizer special-case lists gain a `type` prefix for integer-overflow,
truncation, and enum checks. New controls include
`-f[no-]sanitize-{trap,recover}=local-bounds` and
`-f[no-]sanitize-merge`. Pointer-overflow sanitization no longer reports
`NULL + 0` in C.

### `vptr` must be requested explicitly

In Clang 21, `-fsanitize=undefined` no longer includes `-fsanitize=vptr`
(`clang-21.1`). Add the latter explicitly wherever virtual-pointer checks are
part of the test contract.

Ignorelists can contain positive entries such as `src:*=sanitize`, with
equivalent `type`, `fun`, `global`, and `mainfile` forms. Review ordering and
scope when mixing positive and suppressing entries.

### Trap reasons in debug information

Clang 22 emits detailed trapping-UBSan reasons into DWARF by default
(`clang-22.1`). Select `basic` or `detailed` using
`-fsanitize-debug-trap-reasons=`, or disable with
`-fno-sanitize-debug-trap-reasons`.

Optimization can merge distinct reasons. Use the appropriate
`-fno-sanitize-merge=` control or `-O0` when preserving separate explanations
matters more than optimized shape.

### Sanitizer-aware conditional code

Clang 22's `__builtin_allow_sanitize_check("name")` reports whether a supported
address, hardware-address, memory, or thread sanitizer is active for the
current function after inlining and honors `no_sanitize` (`clang-22.1`). Use it
only for behavior that is specifically safe to vary under instrumentation.

## Allocation-token instrumentation

Clang 22's `-fsanitize=alloc-token` attaches token IDs to allocation functions
for allocator-level heap organization (`clang-22.1`). Related controls are
`-falloc-token-max=`, `-fsanitize-alloc-token-fast-abi`, and
`-fsanitize-alloc-token-extended`.

`__builtin_infer_alloc_token(args...)` computes the token that allocation
arguments would infer at compile time. Keep the compiler, runtime, allocator,
and selected ABI mode aligned.

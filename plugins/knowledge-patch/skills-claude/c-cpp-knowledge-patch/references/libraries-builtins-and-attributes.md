# Libraries, builtins, and attributes

Use this reference for standard-library migrations, compiler builtins,
source-level contracts, format checking, and allocation annotations.

## Header ownership and compatibility headers

### Stop relying on transitive libstdc++ headers

GCC 15's libstdc++ exposes fewer implementation-detail inclusions
(`gcc-15.1-porting`). Include the owner of every name:

- use `<stdint.h>` for global fixed-width integer typedefs;
- use `<cstdint>` for their `std::` forms; and
- use `<ostream>` for stream declarations, `std::endl`, and `std::flush`.

### Remove compatibility C++ headers

GCC 15 warns on compatibility headers (`gcc-15.1-porting`). Remove
`<cstdbool>` and `<cstdalign>`, replace `<ccomplex>` with `<complex>`, and
replace `<ctgmath>` with `<cmath>`, `<complex>`, or both as the used names
require.

## libstdc++ behavior and ABI-sensitive facilities

### Iterator-adaptor constraints

GCC 15's `std::vector` range constructor recognizes C++20 iterator concepts
and can select a stronger optimized path (`gcc-15.1-porting`). Adaptors that
expose invalid operations unconditionally can fail during instantiation.
Constrain each operation to the wrapped iterator's actual capability, with
equivalent SFINAE in older modes:

```cpp
iterator_adaptor& operator--()
  requires std::bidirectional_iterator<Iter>
{
  --iter;
  return *this;
}
```

### Debug assertions

GCC 15 enables libstdc++ debug assertions by default in unoptimized builds
(`gcc-15.1`). Fix invalid preconditions. `_GLIBCXX_NO_ASSERTIONS` disables the
behavior when a controlled migration needs the old setting.

### C++23 additions

GCC 15 adds the `std` and `std.compat` modules, flat associative containers,
range constructors and modifiers, and range and tuple formatting
(`gcc-15.1`).

GCC 16 additionally supplies `std::mdspan`, starts-with and ends-with range
algorithms, shift algorithms, and `allocate_at_least` (`gcc-16.1`). Check both
the selected dialect and library implementation.

### C++26 additions

GCC 15's experimental library adds `views::concat`, `views::to_input`,
`views::cache_latest`, constexpr sorting and raw-memory algorithms,
`<stdbit.h>`, `<stdckdint.h>`, `std::is_virtual_base_of`, member `visit`, and
type checking for `std::format` arguments (`gcc-15.1`).

GCC 16 expands support with `std::simd`, `std::inplace_vector`,
`std::optional<T&>`, `std::copyable_function`, `std::function_ref`,
`std::indirect`, `std::polymorphic`, `std::owner_equal`, `<debugging>`,
string-view overloads, padded `mdspan` layouts, `std::philox_engine`, and
`std::atomic_ref::address()` (`gcc-16.1`).

### Random-number sequence compatibility

GCC 16 adopts P0952R2 for `std::generate_canonical`, changing result sequences
(`gcc-16.1`). Define `_GLIBCXX_USE_OLD_GENERATE_CANONICAL` only when temporary
reproduction of the former sequence is required; otherwise update golden data
and reproducibility documentation.

## Builtins

### Clang 20 elementwise and constexpr builtins

Clang 20 adds (`clang-20.1`):

- `__builtin_elementwise_popcount`;
- `__builtin_elementwise_fmod`;
- `__builtin_elementwise_minimum` and `__builtin_elementwise_maximum`;
- `__builtin_elementwise_atan2`; and
- `__builtin_common_type`.

Integer-reduction and elementwise bit/count/saturating builtins, floating
comparison builtins, `__builtin_signbit`, and `__builtin_abs` also become
usable in constant expressions.

### Clang 21 additions and signature changes

Clang 21 adds `__builtin_elementwise_exp10`,
`__builtin_elementwise_minnum`, `__builtin_elementwise_maxnum`,
`__builtin_invoke`, and `__builtin_get_vtable_pointer` (`clang-21.1`).

`__builtin___clear_cache` now has signature `void(void *, void *)`, matching
GCC rather than accepting `char *`. Update direct declarations and wrappers.

### Clang 22 comparison, pack, and low-level builtins

The Clang 22 `__builtin_{lt,gt,le,ge}_synthesizes_from_spaceship` family tells
whether a relational operator is synthesized from `<=>` (`clang-22.1`). In a
template argument or base specifier, `__builtin_dedup_pack<Ts...>...` produces
an unexpanded pack with duplicate types removed.

New vector and low-level operations include:

- `__builtin_elementwise_ldexp`;
- `__builtin_elementwise_fshl` and `__builtin_elementwise_fshr`;
- `__builtin_elementwise_minnumnum` and
  `__builtin_elementwise_maxnumnum`;
- generic `__builtin_bswapg`;
- `__builtin_stack_address()`; and
- masked load, store, gather, and scatter builtins.

Integer elementwise min/max and abs gain constant-expression support. Fixed
boolean vectors work with generic popcount and count-zero builtins and as `?:`
conditions. `__builtin_assume_dereferenceable` accepts run-time sizes.

### Clang 20 C++ implementation builtins

For C++26 implementation work, Clang 20 adds
`__builtin_is_virtual_base_of` and `__builtin_is_within_lifetime`
(`clang-20.1`). Use feature queries and retain portable fallbacks; these do not
by themselves establish standard-library availability.

## Function and pointer contracts

### Required tail calls and conditional non-null pointers

GCC 15 adds the `musttail` statement attribute to require a tail call
(`gcc-15.1`). `nonnull_if_nonzero` states that a pointer parameter must be
non-null when a distinct size or count parameter is nonzero. Apply these only
when the implementation satisfies the contract on all supported paths.

### `lifetimebound` placement and inference

Clang 20 rejects `[[clang::lifetimebound]]` on types, unnamed parameters,
explicit-object member functions, and parameters or implicit objects of
void-returning functions rather than silently ignoring it (`clang-20.1`). It
also infers the annotation on parameters of `std::span` and
`std::string_view` constructors, enabling more dangling-reference diagnostics.

### Function effects and specialization control

Clang 20 adds `[[clang::no_specializations]]`,
`[[clang::lifetime_capture_by(X)]]`, `[[clang::coro_await_elidable]]`, and
`[[clang::coro_await_elidable_argument]]` (`clang-20.1`). It also supports
`__attribute__((format(syslog, ...)))`, and `swift_attr` can annotate types.
Attributes after a namespace name are no longer accepted; move them to a valid
declaration position.

## Format-string contracts

### Forwarded formats

Clang 21's `format_matches` annotation describes a format-string parameter that
must be equivalent to a reference format (`clang-21.1`):

```c
__attribute__((format_matches(printf, 1, "%x %s")))
```

This lets the compiler check wrappers that receive the format but not its
arguments and avoids inappropriate `-Wformat-nonliteral` warnings inside a
correctly annotated wrapper.

### Modular static-libc formats

Clang 22's `modular_format` attribute lets a cooperating static C library
select required `printf` features at link time (`clang-22.1`). It is a
coordinated compiler-and-library contract, not a general replacement for
ordinary format annotations.

## Allocation and layout annotations

### Allocation assumptions in GCC

GCC 15 enables `-fassume-sane-operators-new-delete` by default (`gcc-15.1`). A
program whose replacement global allocation functions expose global state may
need `-fno-assume-sane-operators-new-delete` while the dependency is removed or
made explicit.

### Pointer-pair allocation results

Clang 22's `malloc_span` gives malloc-like semantics to a function returning a
pointer-and-size or pointer-pair structure (`clang-22.1`). Apply it only when
the returned representation and ownership satisfy those semantics.

### Record layout and unchecked callees

On Itanium-ABI targets, Clang 22's `[[gnu::gcc_struct]]` requests Itanium record
layout even when Microsoft bit-field layout is active (`clang-22.1`). Treat it
as ABI-significant.

`[[clang::cfi_unchecked_callee]]` now propagates from declaration to definition
and suppresses `-fsanitize=function` on affected indirect calls. Limit it to a
reviewed boundary whose unchecked behavior is intentional.

### Target-specific declarations

Clang 21 permits x86-64 globals to select
`__attribute__((model("small")))` or `model("large")` independently of the
translation unit's code model (`clang-21.1`).
`[[clang::atomic(...)]]` sets AMDGPU atomic metadata per statement. Attributes
before an `extern template` declaration are rejected; move them to a supported
declaration.

## Flexible-array counts

Clang 20's `__builtin_counted_by_ref` provides assignable access to the counter
associated with a flexible member's `counted_by` annotation (`clang-20.1`).
Set the count immediately after allocation and before checked member access.

GCC 16 extends GNU C `counted_by` to pointer members (`gcc-16.1`). The named
count member must describe the pointer's accessible element count throughout
its lifetime.

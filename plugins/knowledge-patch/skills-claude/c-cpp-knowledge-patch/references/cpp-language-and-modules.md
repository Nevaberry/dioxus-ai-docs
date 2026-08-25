# C++ language and modules

Use this reference for C++ dialect migrations, constexpr and template behavior,
modules, coroutines, and the boundary between implemented core-language and
library features.

## Dialect selection and feature status

### GCC's default C++ dialect

GCC 16 changes the default dialect from GNU C++17 to GNU C++20
(`gcc-16.1-porting`). Add an explicit `-std=` selection so an upgrade does not
silently change parsing, overload resolution, constexpr rules, or library
surface.

Autoconf before 2.73 can mis-detect GCC 16 in `AC_PROG_CXX` and inject
`-std=gnu++11`, making expected facilities such as `std::make_unique` appear
missing (`gcc-16.1-porting`). Regenerate the build system with a corrected
Autoconf setup rather than adding feature-by-feature workarounds.

### Mode flags do not imply full standards support

Clang's C++23 table still lists constexpr `<cmath>`/`<cstdlib>`, standard
extended floating-point types, CTAD from inherited constructors, and explicit
lifetime management as unsupported (`standards-status`). Unicode identifiers
are accepted without NFC-normalization checking.

Use `-std=c++2c` for Clang's C++26 work. Support remains uneven: Clang 23
forbids macro-generated module declarations and only partially implements
expansion statements because iterating expansions are diagnosed; Clang 24 adds
constexpr virtual inheritance (`standards-status`). Contracts, reflection,
`#embed`, constexpr exceptions, trivial unions, and several other adopted
facilities remain unsupported in the documented Clang status.

Clang accepts `-std=c++2d`, but the C++29 table is preliminary and most listed
proposals are unsupported (`standards-status`). More named universal-character
escapes arrive in Clang 23; do not treat mode availability as broad C++29
coverage.

## Compatibility errors and constant expressions

### Removed or hardened compatibility diagnostics

Clang 20 removes `__is_nullptr`; replace it with
`__is_same(__remove_cv(T), decltype(nullptr))` (`clang-20.1`).
`__is_referenceable` is deprecated for removal in Clang 21.

Out-of-range enum values in constant expressions can no longer be accepted by
disabling `-Wenum-constexpr-conversion`; the flag itself is removed. Extraneous
template headers are errors, though `-Wno-error=extraneous-template-head` can
temporarily demote the diagnostic.

### Pointer expressions during constant evaluation

In Clang 20, comparing distinct evaluations of the same string literal is not
a constant expression, while literals that cannot overlap may compare false
at compile time (`clang-20.1`). Forming a member address through a null pointer,
such as `&((S *)nullptr)->member`, is rejected in a constant expression.

Clang 22 further rejects sibling-member pointer access during constant
evaluation (`clang-22.1`). Restructure the expression around a valid live
object or an offset representation instead of manufacturing a pointer.

### Chained comparisons

Clang 21 makes diagnostics for `a < b < c` and fold expressions over comparison
operators errors by default (`clang-21.1`). Spell the intended boolean
relationship explicitly. `-Wno-error=parentheses` is a temporary demotion, not
a semantic fix.

## C++20 and C++23 behavior

### Core language

Clang 20 completes C++23 range-for temporary lifetime extension (P2718R0),
permits unknown pointers and references in constant expressions (P2280R4),
removes the literal-type restriction in constexpr functions, and defines
`__cpp_explicit_this_parameter` (`clang-20.1`).

Clang 20's defect-report behavior also changes several existing programs:

- for a `T` prvalue `e`, `T{e}` prefers a viable initializer-list constructor
  before guaranteed-copy-elision fallback;
- suitably narrow bit-fields are non-narrowing;
- C-style varargs promote `nullptr` to `void *`;
- `void{}` is accepted;
- explicit deduction guides may have trailing requires-clauses; and
- constructor constraints propagate into CTAD.

### Coroutines and target limits

C++20 coroutines are fully supported except on Windows, where stability and ABI
issues remain (`standards-status`). On 32-bit x86 Windows,
`__cpp_impl_coroutine` is not defined and use produces a warning. Make coroutine
availability a target-specific decision.

### Template edge cases

Generalized scalar non-type template parameters still do not fully support
references to instantiation-dependent objects or subobjects
(`standards-status`). Alias-template CTAD exists, but
`__cpp_deduction_guides` has not been updated to advertise it.

## Modules

### Lookup and proposal coverage

Clang 20 performs module-level lookup in C++20 modules (`clang-20.1`). However,
P1857R3 is not implemented until Clang 23 and P1815R2 remains partial in the
documented status (`standards-status`). Probe the exact pattern your module
graph uses.

### Reduced BMI is the default

Clang 20 promotes `-fmodules-reduced-bmi` from its experimental spelling
(`clang-20.1`). Clang 22 then enables Reduced BMI mode by default
(`clang-22.1`). Two-phase module build systems must support reduced BMIs, and
code must not depend on implementation details that a reduced BMI discards.

### GCC standard modules

With GCC 16's experimental C++20 modules enabled, `--compile-std-module` builds
the `<bits/stdc++.h>` header unit plus the `std` and `std.compat` modules before
other explicit inputs (`gcc-16.1`). Once that header unit exists, eligible
standard-header includes can be translated into imports. Treat the artifact
ordering as part of the build graph.

## C++26 language facilities

### Clang additions

Clang 20 implements variadic friends (P2893R3), constexpr placement new
(P2747R2), and the Oxford variadic comma (P3176R1), and accepts user-defined
`static_assert` messages as an extension back to C++11 (`clang-20.1`). It adds
`__builtin_is_virtual_base_of` and `__builtin_is_within_lifetime` for
implementation work.

Clang 21 adds structured-binding packs, trivial relocatability,
structured-binding declarations as conditions, and attachment of `main` to the
global module (`clang-21.1`). `__builtin_structured_binding_size(T)` reports the
number of bindings produced by destructuring `T`.

Clang 22 adds constexpr structured bindings for arrays and aggregates, but not
for references or tuple-like decomposition (`clang-22.1`). It normalizes
constraints before satisfaction, type-checks constant template parameters in
template definitions, and disallows immediate escalation in destructors.

### GCC additions and strictness

GCC 15 adds pack indexing, attributes on structured bindings, reason strings
in `= delete("reason")`, and structured bindings as conditions (`gcc-15.1`).
The basic character set includes `@`, `$`, and backtick.

GCC 15 also implements standard-attribute ignorability, forbids module
declarations produced by macros, makes deletion through a pointer to an
incomplete type ill-formed, removes deprecated array comparisons, and
deprecates the notion of trivial types (`gcc-15.1`).

GCC 16 implements expansion statements, contracts, erroneous behavior for
uninitialized reads, constexpr exceptions, constexpr virtual inheritance,
partial program correctness, and defined preprocessing behavior
(`gcc-16.1`).

### Reflection in GCC

GCC 16's P2996R13 reflection requires both `-std=c++26` and `-freflection`
(`gcc-16.1`):

```sh
g++ -std=c++26 -freflection source.cc
```

Related support covers annotations, parameter reflection, base-class subobject
splicing, error handling, and `define_static_string`, `define_static_object`,
and `define_static_array`.

## Templates, overloads, and traits

### Earlier current-instantiation diagnostics

GCC 15 diagnoses invalid lookup into the current template instantiation while
parsing the template rather than waiting for instantiation (`gcc-15.1`). Fix
the dependent lookup or qualification at the definition site.

### Concepts TS removal

GCC 15 removes Concepts TS behavior and `-fconcepts-ts` (`gcc-15.1`). Migrate
to standard concepts syntax and semantics.

### Suppressed template instantiation

Under Clang 21's implemented parts of P3606, an identity-conversion match from
a non-template candidate prevents template candidates from being instantiated
(`clang-21.1`). Diagnostics that existed only as a side effect of instantiating
an unused template can therefore disappear; test actual selected behavior.

### Constraint normalization and `__int128`

Clang 22 normalizes constraints before testing satisfaction (`clang-22.1`),
which can change subsumption and overload selection.

On GCC 16 targets with 128-bit integers, traits such as
`std::is_integral<__int128>` are true in strict dialects as well as GNU
dialects (`gcc-16.1`). Recheck constrained overload sets and specializations.

## Trivial relocation

Clang 21 introduces `__builtin_is_cpp_trivially_relocatable`,
`__builtin_is_replaceable`, and `__builtin_trivially_relocate`, while
deprecating `__is_trivially_relocatable` (`clang-21.1`). A relocatable but
non-trivially-copyable object must be moved with the relocation builtin rather
than copied with `memcpy`.

Clang 22 removes `__builtin_is_replaceable`,
`trivially_relocable_if_eligible`, and `replaceable_if_eligible` after the
corresponding proposal leaves C++26 (`clang-22.1`).
`__builtin_is_cpp_trivially_relocatable` and
`__builtin_trivially_relocate` remain with the earlier proposal's semantics,
but source can no longer explicitly mark a type relocatable.

## Constant-expression assembly and allocation

GCC 15 permits C++ inline-assembly strings generated by constexpr evaluation
(`gcc-15.1`). Clang 21 likewise accepts GNU `asm` strings as constant
expressions (`clang-21.1`), for example:

```cpp
asm((std::string_view("nop")) ::: (std::string_view("memory")));
```

Clang 21 also implements type-aware allocation and deallocation (P2719R5) as an
extension in every C++ language mode (`clang-21.1`). Keep extension use behind
compiler feature checks when supporting other implementations.

# Language and Standards

Use this reference when selecting language modes, adopting language features, or deciding whether a standards-mode flag is sufficient evidence of implementation support.

## C language modes and compatibility

### C23 mode and feature set

GCC 15 (`gcc-15.1`) implements `#embed`, the `unsequenced` and `reproducible` attributes, and reports `__STDC_VERSION__` as `202311L` in `-std=c23` and `-std=gnu23`.

Clang 20 (`clang-20.1`) supports C23 Improved Normal Enumerations (N3029), exposes `__nullptr` as an alias for `nullptr` in every C mode, and rejects `register void` parameters.

Clang 21 (`clang-21.1`) accepts `-std=iso9899:2024` as a C23 alias and clang-cl accepts `/std:clatest`. Structurally equivalent tag definitions can coexist in one translation unit, and structure or union rvalues containing array members follow C11 temporary-lifetime rules through the containing full expression, including in older modes.

Clang 22 (`clang-22.1`) adds `FLT_SNAN`, `DBL_SNAN`, and `LDBL_SNAN` to `<float.h>` in C23 and later. With dependency generation, `-MG` suppresses missing-file errors from `#embed`. Fixed-underlying enumeration constants now have the enumerated type, while distinct unnamed tag types with identical fields are no longer compatible.

### C2y facilities

GCC 15 (`gcc-15.1`) exposes C2y through `-std=c2y` and `-std=gnu2y`. Implemented facilities include type operands in generic selections, complex increment/decrement and literals, byte-array access, `alignof` on incomplete array types, delimited escapes, named loops, rotate and non-undefined absolute-value builtins, case-range expressions, declarations in `if`, and zero-length operations on null pointers.

Clang 20 (`clang-20.1`) suppresses GNU-extension warnings for imaginary suffixes, case ranges, and empty structures or unions in C2y mode.

Clang 21 (`clang-21.1`) adds `0o` and `0O` octal syntax and deprecates older nonzero leading-zero octal literals. Delimited `\x{12}` and `\o{12}` escapes are also extensions in older modes. `_Countof(array)` is available as an extension in older C modes; `<stdcountof.h>` provides `countof`, and `__has_feature(c_countof)` or `__has_extension(c_countof)` can probe it.

Clang 22 (`clang-22.1`) enables the draft C `defer` Technical Specification with `-fdefer-ts` and adds named loops in C2y. C2y permits static functions or variables inside `extern inline` functions without `-Wstatic-in-inline`. `__COUNTER__` warns as an extension in other modes and errors after 2,147,483,647 expansions.

GCC 16 (`gcc-16.1`) supports static assertions in expressions and unspecified or variably modified array types in generic associations. It diagnoses as constraint violations some cases classified only as undefined behavior by older standards.

### GNU C additions

GCC 16 (`gcc-16.1`) adds `_Maxof` and `_Minof` for integer type limits:

```c
int highest = _Maxof(int);
int lowest = _Minof(int);
```

GNU C also accepts empty initialization of variable-size compound literals, such as `(int[n]) {}`, producing a run-time-sized zero-initialized temporary.

## C++ language behavior

### Constant expressions and defect-report behavior

Clang 20 (`clang-20.1`) no longer treats comparisons between different evaluations of the same string literal as constant expressions. Literals that cannot overlap may compare constant-false. Forming a member address through a null pointer, such as `&((S *)nullptr)->member`, is rejected during constant evaluation.

The same release changes several defect-report outcomes: for a `T` prvalue `e`, `T{e}` prefers a viable initializer-list constructor before guaranteed copy elision; suitably narrow bit-fields are non-narrowing; `nullptr` is promoted to `void *` through C-style varargs; and `void{}` is accepted. Trailing requires-clauses on explicit deduction guides are accepted, and constructor constraints propagate into CTAD.

Clang 22 (`clang-22.1`) rejects sibling-member pointer access during constant evaluation, type-checks constant template parameters in template definitions, normalizes constraints before satisfaction checks, and disallows immediate escalation in destructors.

### C++20 and C++23

Clang 20 (`clang-20.1`) performs module-level lookup for C++20 modules. Its C++23 mode fully implements range-for temporary lifetime extension, permits unknown pointers and references in constant expressions, removes the literal-type restriction from constexpr functions, and defines `__cpp_explicit_this_parameter`.

Clang's standards status (`standards-status`) remains partial despite those additions. C++23 still lacks constexpr `<cmath>`/`<cstdlib>`, standard extended floating-point types, CTAD from inherited constructors, and explicit lifetime management. Unicode identifiers are accepted without NFC normalization checks.

For C++20, coroutines remain target-dependent: Windows has stability and ABI issues, and 32-bit x86 Windows neither defines `__cpp_impl_coroutine` nor accepts coroutine use without a warning. Module proposal P1857R3 arrives only in Clang 23, while P1815R2 remains partial. Generalized scalar non-type template parameters do not fully support references to instantiation-dependent objects or subobjects. Alias-template CTAD works even though `__cpp_deduction_guides` does not advertise it.

### C++26 language additions

Clang 20 (`clang-20.1`) implements variadic friends, constexpr placement new, and the Oxford variadic comma. It accepts user-defined `static_assert` messages as an extension back to C++11 and provides `__builtin_is_virtual_base_of` and `__builtin_is_within_lifetime` for implementation support.

GCC 15 (`gcc-15.1`) implements pack indexing, attributes on structured bindings, reason strings in `= delete("reason")`, and structured bindings as conditions. The basic character set includes `@`, `$`, and backtick. It also implements standard-attribute ignorability, rejects macro-produced module declarations and deletion through a pointer to incomplete type, removes deprecated array comparisons, and deprecates the notion of trivial types.

Clang 21 (`clang-21.1`) implements structured-binding packs, structured-binding declarations as conditions, attaching `main` to the global module, and `__builtin_structured_binding_size(T)`. Its partial P3606 implementation allows a perfect identity-conversion non-template overload to suppress instantiation of template candidates, so diagnostics produced only by unused instantiations can disappear.

Clang 22 (`clang-22.1`) supports constexpr structured bindings for arrays and aggregates, but not references or tuple-like decomposition.

GCC 16 (`gcc-16.1`) implements expansion statements, contracts, erroneous behavior for uninitialized reads, constexpr exceptions, constexpr virtual inheritance, partial program correctness, and defined preprocessing behavior. P2996R13 reflection requires both `-std=c++26` and `-freflection`; related support covers annotations, parameters, base-class subobject splicing, reflection error handling, and `define_static_string`, `define_static_object`, and `define_static_array`.

```sh
g++ -std=c++26 -freflection source.cc
```

### Trivial relocation changed twice

Clang 21 (`clang-21.1`) introduced `__builtin_is_cpp_trivially_relocatable`, `__builtin_is_replaceable`, and `__builtin_trivially_relocate`, while deprecating `__is_trivially_relocatable`. Relocatable but non-trivially-copyable objects must be moved with `__builtin_trivially_relocate`, not copied with `memcpy`.

Clang 22 (`clang-22.1`) then removed `__builtin_is_replaceable`, `trivially_relocable_if_eligible`, and `replaceable_if_eligible` after the associated proposal left C++26. `__builtin_is_cpp_trivially_relocatable` and `__builtin_trivially_relocate` remain with the proposal's semantics, but source can no longer mark a type explicitly relocatable.

## Templates, overloads, and type traits

GCC 15 (`gcc-15.1`) diagnoses invalid lookup into the current template instantiation while parsing the template rather than waiting for instantiation. This can reveal errors in templates that were never instantiated.

GCC 16 (`gcc-16.1`) treats `__int128` as integral in strict dialects on targets that support it. Traits and constraints such as `std::is_integral<__int128>` can therefore change overload selection.

## Standards support is selective

### C23 gaps

The Clang status data (`standards-status`) says `-std=c23` is available from Clang 18, but unsequenced functions (N2956) and storage-class specifiers on compound literals (N3038) are unsupported. Pointer-to-array qualifier compatibility remains partial: older modes miss some pedantic diagnostics, and `?:` can compute the wrong qualified-array result type.

Improved tag compatibility is only partial from Clang 21. Attributes and extensions can still make structurally similar definitions incorrectly accepted or rejected, so code near those cases may break as conformance improves.

### C2y gaps

Clang exposes `-std=c2y` from Clang 19, but `if` declarations require Clang 24. Static assertions in expressions, bit-precise enums, multidimensional-array matching in generic selections, and array subscripting without decay remain unsupported in the recorded status (`standards-status`).

### C++26 and C++29 gaps

Clang uses `-std=c++2c` for C++26. Clang 23 rejects macro-produced module declarations and only partially implements expansion statements because iterating expansions are diagnosed. Clang 24 adds constexpr virtual inheritance, while contracts, reflection, `#embed`, constexpr exceptions, trivial unions, and several other adopted facilities remain unsupported (`standards-status`).

Clang accepts `-std=c++2d` for C++29, but most listed proposals remain unsupported. Additional named universal character escapes arrive in Clang 23; the mode is not evidence of broad C++29 implementation.

### Probe instead of assuming

The recorded standards tables (`standards-status`) classify C11, C17, C23, C2y, C++20, C++23, C++2c, and C++2d support as partial. Some C11 and C23 proposal entries remain under investigation; treat `Unknown` as unknown, not implemented. Use feature-test macros where reliable and small compile/link/run probes where they are not.

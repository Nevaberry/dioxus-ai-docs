# C language and standards

Use this reference for C dialect migrations, C23 and C2y feature decisions,
source-compatibility failures, and compiler-specific C extensions.

## Select the dialect explicitly

### GCC's default C dialect

GCC 15 changes the default from GNU C17 to GNU C23 (`gcc-15.1-porting`). Pin
the intended dialect or migrate affected source. Under C23, `f()` declares a
function taking no arguments, not unspecified arguments; declare the real
parameter list. `bool`, `true`, `false`, `nullptr`, and `thread_local` are
keywords, so rename legacy identifiers. Do not assume public C `bool` uses the
same ABI representation as `int`.

### Mode flags are not conformance guarantees

The compiler status tables classify C11, C17, C23, and C2y support as partial
(`standards-status`). Proposal entries marked `Unknown` are not evidence of
implementation. Check the individual feature, target, and diagnostic behavior
rather than relying on acceptance of a `-std=` flag.

Clang accepts `-std=c23` from Clang 18 and `-std=c2y` from Clang 19. Clang 21
also accepts `-std=iso9899:2024` as a C23 alias, and clang-cl accepts
`/std:clatest` (`clang-21.1`).

## C23 language and headers

### Implemented facilities

- GCC 15 implements `#embed`, the `unsequenced` and `reproducible` attributes,
  and reports `__STDC_VERSION__` as `202311L` in `-std=c23` and `-std=gnu23`
  (`gcc-15.1`).
- Clang 20 implements C23 Improved Normal Enumerations (N3029), provides
  `__nullptr` as an alias for `nullptr` in every C mode, and rejects
  `register void` parameters (`clang-20.1`).
- Clang 21 permits structurally equivalent tag definitions in one translation
  unit. Structure and union rvalues containing array members follow C11
  temporary-lifetime rules through the containing full expression, including
  in older C modes (`clang-21.1`).
- Clang 22 defines `FLT_SNAN`, `DBL_SNAN`, and `LDBL_SNAN` in `<float.h>` for
  C23 and later. During dependency scanning, `-MG` suppresses missing-file
  errors from `#embed` (`clang-22.1`).

### Enumeration and tag compatibility

Clang 22 treats constants of a fixed-underlying enumeration as having the
enumerated type and no longer considers distinct unnamed tag types compatible
merely because their fields are identical (`clang-22.1`).

Improved tag compatibility nevertheless remains partial: attributes and other
extensions can cause some structurally similar definitions to be accepted or
rejected incorrectly (`standards-status`). Treat code near these edge cases as
unstable and keep compatible declarations in one authoritative header.

### Known C23 gaps

Clang's status still lists unsequenced functions (N2956) and storage-class
specifiers for compound literals (N3038) as unsupported (`standards-status`).
Pointer-to-array qualifier compatibility is partial: C17 and earlier miss some
pedantic diagnostics, and conditional expressions can compute the wrong
qualified-array result type.

## C2y language work

### GCC facilities

GCC 15 exposes the early dialect through `-std=c2y` and `-std=gnu2y`
(`gcc-15.1`). Its implemented set includes:

- type operands in generic selections;
- complex increment/decrement and complex literals;
- byte-array access and `alignof` on incomplete array types;
- delimited escapes, named loops, and case-range expressions;
- rotate and non-undefined absolute-value builtins;
- declarations in `if`; and
- zero-length operations on null pointers.

GCC 16 additionally permits static assertions in expressions and unspecified
or variably modified array types in generic associations (`gcc-16.1`). It also
diagnoses as constraint violations some cases that older standards classified
only as undefined behavior.

### Clang facilities

In Clang 20 C2y mode, imaginary suffixes and case ranges no longer produce
their GNU-extension warnings, and empty structures or unions no longer produce
`-Wgnu-empty-struct` (`clang-20.1`).

Clang 21 accepts `0o` and `0O` octal prefixes and deprecates older nonzero
leading-zero octal literals (`clang-21.1`). Delimited escapes such as `\x{12}`
and `\o{12}` are also extensions in older modes. `_Countof(array)` is available
as an extension in older C modes; `<stdcountof.h>` supplies `countof`, and
`__has_feature(c_countof)` or `__has_extension(c_countof)` can test support.

Clang 22 adds named loops and the experimental draft `defer` Technical
Specification behind `-fdefer-ts` (`clang-22.1`). C2y also permits static
functions or variables inside `extern inline` functions without
`-Wstatic-in-inline`. `__COUNTER__` warns as an extension in other modes and
fails after 2,147,483,647 expansions.

### Known C2y gaps

Clang's status says `if` declarations require Clang 24 (`standards-status`).
Static assertions in expressions, bit-precise enums, multidimensional-array
matching in generic selections, and array subscripting without decay remain
unsupported in the documented status. Gate each facility independently.

## Compatibility diagnostics and changed source meaning

### C-to-C++ compatibility checks

Clang 21 expands `-Wc++-compat` to cover implicit `void *` and integer-to-enum
conversions, C++ keywords and hidden tags, tentative definitions, default
initialization of `const` objects, and jumps that bypass initialization
(`clang-21.1`). `-Wundef-true` is enabled by default before C23.

`-Wextra` now includes `-Wunterminated-string-initialization`. Mark an
intentional non-terminated C array with `nonstring`; that annotation does not
suppress the C++-compatibility variant.

### Incompatible pointers and statement expressions

In Clang 22, `-Wincompatible-pointer-types` is an error by default
(`clang-22.1`). Fix the pointed-to type or, as a temporary migration measure,
demote only that group with `-Wno-error=incompatible-pointer-types`.

A trailing null statement now gives a GNU statement expression type `void`, so
`({ 1;; })` no longer has type `int`. Remove the extra null statement when the
value is intended.

### Union representation is not initialized by `{0}`

For an automatic C or C++ union, `{0}` initializes the first member but need
not clear padding (`gcc-15.1-porting`). Do not hash, serialize, compare, or
expose the full representation assuming zeroed padding. Use `{}` where
supported, clear representation storage explicitly, or use
`-fzero-init-padding-bits=unions` as a controlled compatibility measure.

## Counted storage and GNU C extensions

### Flexible-array count access

Clang 20's `__builtin_counted_by_ref(flexible_member)` returns access to the
counter named by that member's `counted_by` attribute (`clang-20.1`). Allocation
helpers can therefore set the counter before sanitizer-checked access:

```c
*__builtin_counted_by_ref(p->items) = count;
```

### Counted pointer members

GNU C in GCC 16 permits `counted_by` on pointer members (`gcc-16.1`):

```c
struct buffer {
  unsigned count;
  int *data __attribute__((counted_by(count)));
};
```

Keep the count synchronized with the allocation and the number of accessible
elements.

### Integer limits

GCC 16 adds GNU C `_Maxof` and `_Minof` for integer-type limits (`gcc-16.1`):

```c
int highest = _Maxof(int);
int lowest = _Minof(int);
```

### Variable-size compound literals

GNU C in GCC 16 accepts an empty initializer for a variable-size compound
literal, such as `(int[n]) {}`, producing a run-time-sized zero-initialized
temporary (`gcc-16.1`). Keep this extension behind a compiler/dialect check
when portability is required.

### Noncapturing nested functions

GCC 16 guarantees that a nested function which does not capture its environment
does not need a run-time trampoline (`gcc-16.1`). This permits such functions
in environments that disallow executable-stack-style trampoline support, but
capturing nested functions retain different requirements.

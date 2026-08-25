# Migration and ABI

Use this reference before compiler upgrades, clean rebuilds, binary-interface changes, or attempts to mix objects produced by different compiler releases.

## Pin language defaults

### GCC changes the default C dialect

GCC 15 (`gcc-15.1-porting`) changes the default C mode from `-std=gnu17` to `-std=gnu23`. Pin an older mode or migrate deliberately. In particular:

- `f()` now declares a function taking no arguments, not unspecified arguments;
- `bool`, `true`, `false`, `nullptr`, and `thread_local` are keywords, so legacy identifiers need renaming;
- public C `bool` uses must not be treated as ABI-identical to `int`.

Declare real callback signatures rather than relying on an empty parameter list:

```c
void (*handler)(int);
```

### GCC changes the default C++ dialect

GCC 16 (`gcc-16.1-porting`) changes the default from `-std=gnu++17` to `-std=gnu++20`. Select the intended dialect explicitly in all build and probe commands.

```sh
g++ -std=gnu++20 -c file.cc
```

Autoconf before 2.73 can mis-detect GCC 16 in `AC_PROG_CXX` and inject `-std=gnu++11`, making default-mode facilities such as `std::make_unique` appear unavailable. Regenerate build outputs with corrected Autoconf logic rather than adding isolated feature workarounds.

## Clang ABI transitions

### Mangling changes

Clang 20 (`clang-20.1`) changes Microsoft mangling for placeholder, `auto`, and `decltype(auto)` return types to match newer MSVC behavior. `-fms-compatibility-version=19.14` retains compatibility with older Clang objects. Itanium construction-vtable names and member-like friend function-template mangling also change; `-fclang-abi-compat=19` selects the older forms.

### Record returns

Clang 21 (`clang-21.1`) returns larger C++ records in memory rather than AVX registers. Objects built by earlier Clang releases are incompatible across that boundary unless new compilations temporarily use `-fclang-abi-compat=20`.

### Windows destructor entry points

Under the MSVC ABI, Clang 22 (`clang-22.1`) makes `::delete` invoke the scalar deleting destructor. Mixing Clang 21-or-earlier objects with Clang 22 objects can choose the wrong deallocator and corrupt memory; `-fclang-abi-compat=21` retains the older scalar behavior during migration.

Windows vtables also switch to the differently named and linked MSVC vector deleting destructor. Classes with virtual destructors therefore create a second mixed-version runtime hazard. Rebuild all producers and consumers together.

### Arm and AArch64 records

On 32-bit Arm, Clang 20 (`clang-20.1`) passes empty C++ structs as one-byte objects to match AAPCS32 and GCC. `-fclang-abi-compat=19` restores the older ignored-argument behavior. SME function-type attributes also become part of mangling.

Clang 22 (`clang-22.1`) changes AArch64 argument passing for empty C++ classes with large explicit alignment. Treat such records as an ABI boundary during a toolchain upgrade.

## GCC and libstdc++ ABI transitions

### Solaris fixed-width integers

On Solaris, GCC 16 (`gcc-16.1-porting`) changes `int8_t`, `int_fast8_t`, and `int_least8_t` from plain `char` to `signed char`. Those types mangle differently in C++, so rebuild every object across an affected interface. `_LEGACY_INT8_T` is a temporary compatibility option when a full rebuild is impossible.

### C++17 `std::variant`

GCC 16 (`gcc-16.1`) corrects a narrow C++17 `std::variant` layout involving an empty base and the first member. `_GLIBCXX_USE_VARIANT_CXX17_OLD_ABI` restores the old layout temporarily.

### Formerly experimental C++20 components

GCC 16 (`gcc-16.1`) declares its C++20 library non-experimental and changes ABI in atomic waiting, semaphores, syncstream, format-argument representation, partial ordering, some stop-token/variant combinations, and some range adaptors. Rebuild objects that exchange affected types or state across binary boundaries.

### Reproducible random sequences

GCC 16 (`gcc-16.1`) adopts P0952R2 behavior for `std::generate_canonical`, changing result sequences. `_GLIBCXX_USE_OLD_GENERATE_CANONICAL` temporarily reproduces the older sequence when compatibility is required.

## Source and option removals

### Removed Clang tools, targets, and builtins

Clang 20 (`clang-20.1`) removes `le32`, `le64`, RenderScript target support, and `clang-rename`. It also removes `__is_nullptr`; use `__is_same(__remove_cv(T), decltype(nullptr))`. `__is_referenceable` is deprecated for removal in Clang 21.

Out-of-range enum values in constant expressions can no longer be accepted by disabling `-Wenum-constexpr-conversion`, because the flag is removed. Extraneous template headers are errors unless staged migration demotes them with `-Wno-error=extraneous-template-head`.

### Removed Clang compatibility paths

Clang 21 (`clang-21.1`) removes the Objective-C ARC migrator and the workaround for libstdc++ 4.7; libstdc++ 4.8.3 becomes the oldest supported version. It also removes `-frelaxed-template-template-args` and its negative spelling.

### Removed Concepts TS

GCC 15 (`gcc-15.1`) removes Concepts TS behavior and `-fconcepts-ts`. Migrate to standard concepts under an appropriate standard mode.

### C source incompatibilities

Clang 22 (`clang-22.1`) makes `-Wincompatible-pointer-types` an error by default; `-Wno-error=incompatible-pointer-types` is the narrow temporary demotion. A trailing null statement makes a GNU statement expression `void`, so `({ 1;; })` no longer has type `int`.

Clang 20 (`clang-20.1`) no longer accepts attributes after a namespace name. It rejects invalid `[[clang::lifetimebound]]` placement rather than ignoring it; valid placement and inference details are in [Diagnostics and safety](diagnostics-and-safety.md).

## Target and platform retirement

GCC 15 (`gcc-15.1`) removes Nios II and Solaris 11.3 support and deprecates AArch64 ILP32 (`-mabi=ilp32`). It is the final GCC release with the old `reload` register allocator; targets without LRA support are affected when GCC 16 removes it.

On SPARC Linux, Clang 20 (`clang-20.1`) makes `clang -m32` default to `-mcpu=v9`. Distributions retaining SPARC V8 must pass `-mcpu=v8`.

On Solaris, GCC 16 (`gcc-16.1-porting`) ignores `-pthread` and `-pthreads` and no longer defines `_REENTRANT` or `_PTHREADS`. Code that used those feature macros for application behavior must define its own explicit macro.

## Upgrade procedure

1. Pin language modes before comparing diagnostics.
2. Remove stale objects, module artifacts, generated bindings, and plugin binaries.
3. Identify compiler-specific ABI switches already present in the build.
4. Rebuild all sides of affected C++ and standard-library interfaces together.
5. Run layout, calling-convention, exception, allocation, and virtual-destruction tests.
6. Use compatibility switches only while coordinating the rebuild; remove them afterward.

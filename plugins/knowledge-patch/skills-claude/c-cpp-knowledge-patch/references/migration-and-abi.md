# Migration and ABI

Use this reference before mixing objects, shared libraries, plugins, or public
headers built by different compiler or standard-library generations. A
compatibility flag named here addresses a specific transition only.

## Clang C++ ABI transitions

### Mangling changes in Clang 20

Microsoft mangling for placeholder, `auto`, and `decltype(auto)` return types
matches MSVC 1920 and later in Clang 20 (`clang-20.1`). Compile with
`-fms-compatibility-version=19.14` only when compatibility with objects built by
older Clang behavior is required.

Itanium construction-vtable names and member-like friend function-template
mangling also change. `-fclang-abi-compat=19` restores the former encodings.
Prefer rebuilding every object that names these entities.

### C++ record returns in Clang 21

Clang 21 returns larger C++ records in memory rather than AVX registers
(`clang-21.1`). Objects built by older Clang releases are incompatible across
affected calls unless new compilation uses `-fclang-abi-compat=20`. Treat this
as a whole-boundary rebuild, especially for virtual calls, callbacks, and
plugin APIs.

### Windows destructor ABI in Clang 22

For the MSVC ABI, `::delete` now invokes the scalar deleting destructor in
Clang 22 (`clang-22.1`). Mixing Clang 21-or-earlier and Clang 22 objects can
select the wrong deallocator and corrupt memory. `-fclang-abi-compat=21`
retains the prior scalar behavior as a migration bridge.

Windows vtables now use the differently named and linked MSVC vector deleting
destructor. That is a separate mixed-version runtime incompatibility for
classes with virtual destructors. Rebuild all producers and consumers of such
classes together.

## Arm and target-layout transitions

### Empty Arm records

On 32-bit Arm, Clang 20 passes empty C++ structs as one-byte objects to match
AAPCS32 and GCC (`clang-20.1`). `-fclang-abi-compat=19` restores the earlier
ignored-argument behavior. SME function-type attributes also begin
participating in mangling.

### Explicitly aligned empty AArch64 classes

Clang 22 changes AArch64 argument passing for empty C++ classes with large
explicit alignment (`clang-22.1`). Rebuild both sides of any affected call and
validate generated interfaces that expose such types.

### LoongArch `_BitInt` layout

Clang 21 consistently gives LoongArch `_BitInt(N)` values wider than 64 bits
16-byte alignment (`clang-21.1`). Inspect record layout, parameter passing, and
serialized/native shared structures.

## libstdc++ ABI and sequence transitions

### Solaris integer typedef identity

On Solaris, GCC 16 changes `int8_t`, `int_fast8_t`, and `int_least8_t` from
plain `char` to `signed char` (`gcc-16.1-porting`). These types mangle
differently in C++. Rebuild every object across an affected ABI boundary.
`_LEGACY_INT8_T` is a temporary compatibility option when a complete rebuild
cannot happen immediately.

### Narrow C++17 `variant` correction

GCC 16 corrects a C++17 `std::variant` layout case involving an empty base and
the first member (`gcc-16.1`).
`_GLIBCXX_USE_VARIANT_CXX17_OLD_ABI` restores the former layout while migrating.

### Formerly experimental C++20 components

GCC 16 no longer treats the C++20 library as experimental, and several
components change ABI (`gcc-16.1`): atomic waiting, semaphores, syncstream,
format-argument representation, partial ordering, some stop-token/variant
combinations, and some range adaptors. Rebuild objects that exchange affected
types or state across binary boundaries.

### `generate_canonical` reproducibility

GCC 16 adopts P0952R2 for `std::generate_canonical`, changing generated result
sequences (`gcc-16.1`). `_GLIBCXX_USE_OLD_GENERATE_CANONICAL` temporarily
restores the old sequence; it is a behavioral compatibility switch rather than
a general ABI switch.

## Removed compatibility paths and targets

### Clang 20 removals

Clang 20 removes `le32`, `le64`, `clang-rename`, and RenderScript target
support (`clang-20.1`). Replace the tool or target configuration; do not leave
dead probes in the build indefinitely.

On SPARC Linux, `clang -m32` now defaults to `-mcpu=v9`. A distribution that
retains SPARC V8 must pass `-mcpu=v8` explicitly.

### GCC 15 removals and deprecations

GCC 15 removes Nios II and Solaris 11.3 support and deprecates AArch64 ILP32
(`-mabi=ilp32`) (`gcc-15.1`). It is also the final release with the old
`reload` register allocator; targets without LRA support are affected by the
removal in GCC 16.

### Clang 21 compatibility removals

Clang 21 removes the Objective-C ARC migrator and the libstdc++ 4.7 workaround,
making libstdc++ 4.8.3 the oldest supported version (`clang-21.1`). It also
removes deprecated `-frelaxed-template-template-args` and its negative
spelling. Migrate source to the standard matching rules.

## Intrinsic and low-level migration

### X86 MMX header intrinsics

In Clang 20, `*mmintrin.h` intrinsics operating on `__m64` always use SSE2 and
XMM registers (`clang-20.1`). They no longer work on MMX-only targets or with
`-mmmx -mno-sse2`; MMX inline assembly remains supported.

Former `__builtin_ia32_*` implementation builtins used by those intrinsics are
removed. Direct callers must migrate to the header intrinsics and accept their
SSE2 requirement or replace the implementation.

### Extended assembly red-zone declarations

GCC 15 permits extended assembly at file scope, subject to its documented
restrictions (`gcc-15.1`). Assembly that overwrites the stack red zone can name
the special `"redzone"` clobber. Add it wherever the assembly truly destroys
that region so surrounding generated code does not rely on it.

## Platform build semantics

### Solaris pthread flags

On Solaris, GCC 16 ignores `-pthread` and `-pthreads`; these flags no longer
define `_REENTRANT` or `_PTHREADS` (`gcc-16.1-porting`). Code that used those
implementation macros for its own feature selection should define a distinct
application macro explicitly.

### Clang-cl static Blocks runtime

On Windows in Clang 21, `-static-libclosure` changes only Blocks-extension code
generation and does not itself alter linker behavior (`clang-21.1`). Configure
the intended runtime linkage separately.

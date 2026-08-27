# Safety, FFI, and Low-Level Programming

## Raw pointers, provenance, and pinning

### Forming raw references

- Since 1.84.0, `&raw const *ptr` and `&raw mut *ptr` may form a raw reference to the place behind a raw pointer without an unsafe block. Dereferencing the result still needs the normal validity proof.
- Since 1.92.0, the same rule permits projecting a union field with `&raw`; reading the union field or dereferencing the result remains unsafe.

```rust
union Slot { number: u32 }

fn number_ptr(slot: *const Slot) -> *const u32 {
    &raw const (*slot).number
}
```

### Null pointers and validity

- Since 1.86.0, debug-assertion builds issue a non-unwinding panic for non-zero-sized null reads/writes and null reborrows as references. This is diagnostic only: dependencies built without debug assertions omit the check.
- Since 1.96.0, the library-wide definition of memory valid for reads or writes excludes null. Only methods documenting an explicit exception may receive null.
- Raw-pointer diagnostics added in 1.88.0 and 1.91.0 catch implicit autoref, invalid-null, dangling-local, and integer-transmute patterns, but diagnostics do not replace unsafe reasoning.

### Provenance-aware addresses

- `NonNull::{without_provenance, with_exposed_provenance, expose_provenance}` are stable since 1.89.0.
- `ptr::{with_exposed_provenance, with_exposed_provenance_mut}` are const-capable since 1.91.0.
- Use no-provenance construction only where the API contract permits it. Reconstruct pointers from integers through exposed-provenance APIs instead of transmutation.

### Pinning

- Downstream `DerefMut for Pin<LocalType>` implementations are rejected since 1.92.0.
- `pin!(x)` no longer performs a dereference coercion as of 1.97.0. If `x: &mut T`, the result is `Pin<&mut &mut T>`; explicitly identify the pointee when `Pin<&mut T>` is intended.
- Non-extended `pin!` arguments stopped receiving incidental temporary lifetime extension in 1.92.0. Bind borrowed temporaries first.

## Initialization, allocation, and ownership

### Zeroed and staged initialization

- Since 1.92.0, `Box`, `Rc`, and `Arc` have `new_zeroed` and `new_zeroed_slice`. They return `MaybeUninit`; use `assume_init` only when every all-zero bit pattern is valid for `T`.
- Since 1.93.0, `[MaybeUninit<T>]` supports `write_copy_of_slice`, `write_clone_of_slice`, `assume_init_ref`, `assume_init_mut`, and `assume_init_drop` for whole-buffer operations.
- Since 1.95.0, `MaybeUninit<[T; N]>` converts to/from `[MaybeUninit<T>; N]` and exposes `AsRef`/`AsMut` array and slice views.

### Ownership transfer and layouts

- Since 1.93.0, `Vec::into_raw_parts` and `String::into_raw_parts` yield pointer, length, and capacity without freeing. Reconstruct exactly once with compatible raw-parts APIs.
- Since 1.95.0, `Layout::{dangling_ptr, repeat, repeat_packed, extend_packed}` support allocator layout composition.
- Since 1.95.0, raw pointers also provide stable `as_ref_unchecked` and `as_mut_unchecked`; callers must establish the reference validity contract themselves. `core::hint::cold_path` is stable for marking an unlikely path.
- Since 1.93.0, standard bookkeeping for `thread_local!` and `std::thread::current()` uses the system allocator where needed, so a Rust global allocator may call those facilities without bookkeeping re-entering that allocator.

### Allocation and pointer guarantees

- `Vec::with_capacity(n)` guarantees since 1.87.0 that its allocation requests the specified amount even when reported capacity differs.
- The pointer from `Thread::into_raw` has at least eight-byte alignment since 1.90.0.
- `AtomicPtr` gained element-scaled, byte-scaled, and bitwise read-modify-write operations in 1.91.0; atomic pointer, bool, and integer types gained `update`/`try_update` in 1.95.0.

## Foreign interfaces and ABIs

### Explicit and variadic ABIs

- Spell the ABI in `extern "C"`; `missing_abi` warns by default since 1.86.0 even though omission still selects C.
- Since 1.91.0, extern blocks may declare C-style variadic functions with `sysv64`, `win64`, `efiapi`, and `aapcs`; Rust still cannot define them.
- Since 1.93.0, `extern "system"` foreign declarations may also be variadic.
- Unsupported ABI strings are rejected consistently in every position since 1.90.0.

### Integer and character ABI types

- `core::ffi::c_char` changed signedness on many Tier 2/3 platforms in 1.85.0 to follow each C ABI; `libc` aligns beginning with 0.2.169. Do not assume `i8` or `u8`.
- `i128`/`u128` in `extern "C"` definitions and `#[repr(i128)]`/`#[repr(u128)]` are stable since 1.89.0. They match C `__int128` where it exists, not necessarily `_BitInt(128)` or any type on every platform.
- `core::ffi::c_double` is `f32` on AVR as of 1.96.0, matching that target's ABI.

### Exported symbols and attributes

- `#[track_caller]` may accompany `#[unsafe(no_mangle)]` since 1.92.0, provided all declarations specify `#[track_caller]`.
- Since 1.96.0, the first repeated `export_name`, `link_name`, or `link_section` attribute takes precedence.
- Since 1.97.0, invalid Mach-O `link_section`, empty `export_name`, and invalid `link_name` or native-link names are errors; `varargs_without_pattern` is reported in dependencies.
- Stable rustc uses v0 symbol mangling by default since 1.97.0. Update demanglers, profilers, debuggers, and backtrace snapshots; the legacy scheme is nightly-only and planned for removal.

## Inline assembly and intrinsics

### Assembly control flow and naked functions

- Since 1.87.0, `asm!` accepts a `label` operand with a `()` or `!` block. A jump runs the block, then continues after the assembly. Combining label and output operands remains unstable.
- Since 1.88.0, a naked function uses `#[unsafe(naked)]` and a body containing exactly one `naked_asm!`. The compiler emits no prologue, epilogue, or argument/return handling; the assembly defines all of it.
- Since 1.93.0, template strings and operands inside `asm!`, `global_asm!`, and `naked_asm!` may carry `#[cfg]` individually.
- Inline assembly became stable on PowerPC/PowerPC64 in 1.95.0; s390x vector-register assembly support arrived in 1.96.0.

### Target-feature intrinsics

- Since 1.87.0, most architecture intrinsics whose sole safety precondition is an enabled target feature, and which accept no pointers, are safe inside a function carrying the matching `#[target_feature]`. Runtime dispatch still requires an unsafe call into that target-feature function.
- The accidentally stable `std::intrinsics::{copy, copy_nonoverlapping, write_bytes}` became proper intrinsics in 1.89.0: they no longer add debug UB checks and cannot coerce to function pointers. `std::intrinsics::drop_in_place` was removed.

## Volatile memory, unwind data, and layouts

- Volatile operations may access memory outside Rust allocations, including address zero, since 1.90.0. This does not relax each operation's other preconditions.
- Linux `-C panic=abort` emits unwind tables by default since 1.92.0 for useful backtraces; use `-C force-unwind-tables=no` for the old omission.
- `#[repr(Int)]` enum layout can differ from older output in 1.96.0 edge cases involving fields of uninhabited zero-sized types.
- Some non-`repr` enums changed encoding in 1.97.0. Layout without an explicit representation is not a compatibility contract; never expose the observed encoding through unsafe code or FFI.
- Out-of-range discriminants on `repr(C)` enums receive a future-compatibility warning since 1.93.0.

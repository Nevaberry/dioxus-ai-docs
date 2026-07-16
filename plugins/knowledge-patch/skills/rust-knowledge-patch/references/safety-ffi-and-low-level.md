# Safety, FFI, and Low-Level Programming

Use this reference for raw-pointer reasoning, pinning, allocation, provenance, atomics, foreign interfaces, target-feature functions, and inline assembly. Edition-specific unsafe requirements are in [edition-2024.md](edition-2024.md).

## Raw pointers, references, and provenance

### Safe raw-reference formation

Forming a raw reference to the place behind a raw pointer no longer requires an unsafe block (1.84.0). Dereferencing the resulting pointer still requires the usual validity proof.

```rust
fn same_place(ptr: *mut u32) -> *mut u32 {
    &raw mut *ptr
}
```

The same rule applies to union fields from 1.92.0: safe code may form `&raw const bits.integer` or `&raw mut bits.integer`, but reading the active field through the pointer remains unsafe.

### Debug null checks

With debug assertions, non-zero-sized reads or writes through a null raw pointer and reborrowing it as a reference cause a non-unwinding panic (1.86.0). This does not establish soundness: the check is absent in code compiled without debug assertions.

### Provenance APIs

`NonNull` gains `from_ref`, `from_mut`, `without_provenance`, `with_exposed_provenance`, and `expose_provenance` (1.89.0). Const evaluation supports `ptr::with_exposed_provenance` and its mutable form from 1.91.0. Prefer these explicit APIs to integer-to-pointer transmutation.

`dangling_pointers_from_locals` and `integer_to_ptr_transmutes` warn by default from 1.91.0. Returning a pointer to a local is not itself an unsafe operation, but dereferencing it after the local dies is invalid.

### Pointer and pinning APIs

- Raw pointers support unsigned `offset_from` and `byte_offset_from`, and `NonNull` supports the corresponding operations (1.87.0).
- Raw pointers gain `as_ref_unchecked` and `as_mut_unchecked` (1.95.0); callers must uphold all reference validity and aliasing requirements.
- `pin!` no longer dereference-coerces an `&mut T` in 1.97.0. `pin!(x)` for `x: &mut T` consistently produces `Pin<&mut &mut T>`; explicitly dereference when pinning `T` is intended.
- Raw trait-object pointers used in upcasting must contain a valid vtable even if code does not dereference them immediately (1.86.0).

## Target-feature functions and architecture intrinsics

### Safe `#[target_feature]` functions

A safe function may carry `#[target_feature]` from 1.86.0. Calling it is safe from a function with the required features; an unmarked caller must detect or otherwise establish the CPU feature and call it in an unsafe block. Such functions cannot be passed to `Fn*`-bounded generics and coerce to function pointers only inside appropriately feature-enabled functions.

```rust
#[target_feature(enable = "avx2")]
fn avx2_only() {}

fn dispatch() {
    if is_x86_feature_detected!("avx2") {
        unsafe { avx2_only() };
    }
}
```

Most `std::arch` intrinsics without pointer arguments are contextually safe when called from code enabling all required target features (1.87.0). Old unsafe blocks around them can trigger `unused_unsafe`; pointer-taking intrinsics still require their pointer preconditions.

## Inline assembly

### Label operands

`asm!` accepts a `label` operand containing a block of type `()` or `!` (1.87.0). Assembly may jump to the block, which then continues after the assembly. Combining label and output operands remains unstable.

```rust
unsafe {
    std::arch::asm!("jmp {}", label {
        println!("jumped from asm");
    });
}
```

### Conditional templates and operands

Attach `#[cfg(...)]` to individual template strings and operands in `asm!`, `global_asm!`, and `naked_asm!` (1.93.0):

```rust
unsafe {
    core::arch::asm!(
        "nop",
        #[cfg(target_feature = "sse2")]
        "mov eax, {value}",
        #[cfg(target_feature = "sse2")]
        value = const 123,
    );
}
```

PowerPC and PowerPC64 inline assembly is stable from 1.95.0. S390x vector registers are supported in inline assembly from 1.96.0.

## Foreign functions and ABIs

### Explicit ABI declarations

`missing_abi` warns by default for `extern {}` and `extern fn` from 1.86.0. Omission still means C, but spell `extern "C"` explicitly.

Unsupported ABI strings are rejected in every position from 1.90.0, including trait impls for function pointers. From 1.89.0, legacy 32-bit x86 spellings such as `"stdcall"`, `"fastcall"`, and `"cdecl"` are linted on targets where they do not apply. Dependencies warned in 1.87.0 when a function pointer named an unsupported ABI.

### C-style variadics

- `sysv64`, `win64`, `efiapi`, and `aapcs` permit C-style variadic declarations in foreign blocks from 1.91.0.
- The `system` ABI permits them from 1.93.0.
- Rust may declare these variadic functions but still cannot define them.

```rust
unsafe extern "sysv64" {
    fn log(format: *const core::ffi::c_char, ...);
}
```

### C integer and character compatibility

`i128` and `u128` no longer trigger `improper_ctypes_definitions` in C-ABI functions, and `#[repr(i128)]` and `#[repr(u128)]` are stable (1.89.0). They match C `__int128` where it exists, are not necessarily compatible with `_BitInt(128)`, and have no guaranteed matching C type on platforms lacking `__int128`.

`core::ffi::c_char` changed between `i8` and `u8` on many Tier 2 and Tier 3 targets to follow the platform C `char` default (1.85.0). `libc` matches from 0.2.169. On AVR, `core::ffi::c_double` is `f32` from 1.96.0 to match that platform's C ABI.

### Representation diagnostics and contracts

- A `repr(C)` enum whose discriminant does not fit `c_int` or `c_uint` receives a future-compatibility warning (1.93.0).
- `repr(transparent)` receives a warning when it would ignore a field type's `repr(C)` representation (1.93.0).
- Some enum layouts involving uninhabited zero-sized fields were corrected in 1.96.0; unspecified layouts also changed in 1.97.0. Add an explicit representation only when a stable external layout is required.
- When duplicate `export_name`, `link_name`, or `link_section` attributes appear, the first takes precedence from 1.96.0.

### Call metadata and symbols

`#[track_caller]` and `#[no_mangle]` may be combined from 1.92.0, but every declaration of the function must carry `#[track_caller]`.

## Allocation and staged initialization

### `MaybeUninit`

- `Box<MaybeUninit<T>>::write` initializes a boxed allocation in place (1.87.0).
- `[MaybeUninit<T>]` supports `assume_init_drop`, `assume_init_ref`, `assume_init_mut`, `write_copy_of_slice`, and `write_clone_of_slice` for slice-wide initialization and access (1.93.0).
- `MaybeUninit<[T; N]>` converts to and from `[MaybeUninit<T>; N]` and exposes array or slice views through `AsRef` and `AsMut` (1.95.0).

Each `assume_init_*` operation still requires proof that the relevant elements are initialized and valid for `T`.

### Zeroed allocation and raw parts

`Box`, `Rc`, and `Arc` provide `new_zeroed` and `new_zeroed_slice` from 1.92.0. Zero bytes are not a valid value for every type; initialization must be completed before assuming the value is initialized.

`String::into_raw_parts` and `Vec::into_raw_parts` stably transfer ownership into pointer, length, and capacity from 1.93.0. Reconstruct with the matching allocator and original invariants exactly once.

### Global allocators

A Rust global allocator may use `thread_local!` and `std::thread::current()` from 1.93.0. The standard library uses the system allocator in paths that must avoid re-entering the custom allocator.

## Layout construction and dangling pointers

`Layout` gains `dangling_ptr`, `repeat`, `repeat_packed`, and `extend_packed` in 1.95.0. Earlier const stabilization includes `Layout::for_value`, `align_to`, `pad_to_align`, `extend`, and `array` (1.85.0). A dangling pointer is non-null and aligned but does not make memory dereferenceable.

Pointers from `Thread::into_raw` have at least eight-byte alignment from 1.90.0.

## Atomics and volatile memory

### Atomic operations

- `AtomicPtr` gains element- and byte-offset fetch-add/subtract plus `fetch_or`, `fetch_and`, and `fetch_xor` (1.91.0).
- Atomic pointer, boolean, and integer types gain `update` and `try_update` (1.95.0).
- Const evaluation supports `from_ptr` for every supported atomic integer type, `AtomicBool`, and `AtomicPtr` from 1.84.0.

Apply the documented memory ordering to both success and failure cases of update loops; stabilization does not relax atomic ordering rules.

### Mutable and external memory in constants

Constants may end with references to mutable or external memory from 1.90.0, but such constants cannot be used as patterns. Const evaluation can copy pointers byte by byte, and a const item may hold a mutable reference to a static from 1.93.0; the latter remains highly unsafe despite being accepted.

Volatile access to non-Rust memory, including address zero, is permitted from 1.90.0. Volatile affects access observability, not pointer validity, alignment, races, or device-specific ordering.

## Low-level diagnostic changes

- `invalid_null_arguments` detects invalid null-pointer arguments from 1.88.0.
- The accidentally stable `copy`, `copy_nonoverlapping`, and `write_bytes` compiler intrinsics became proper intrinsics in 1.89.0. They do not coerce to function pointers and do not add runtime undefined-behavior checks.
- `offset_of!` rejects ill-formed user types from 1.93.0.
- Empty or malformed native-link attributes are rejected in 1.97.0; keep unsafe attribute invariants explicit.

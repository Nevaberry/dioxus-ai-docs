# Safety, FFI, and Low-Level Programming

## Pointer provenance and raw references

### Strict and exposed provenance

The stable pointer/address APIs (`1.84.0`) avoid pointer-to-integer casts for
tagged pointers and address comparisons:

- `<ptr>::addr()`, `<ptr>::with_addr(usize)`, and `<ptr>::map_addr(f)` retain
  provenance while inspecting or changing an address.
- `ptr::without_provenance` and `ptr::without_provenance_mut` create
  address-only pointers that must not be dereferenced.
- `ptr::dangling()` and `ptr::dangling_mut()` create aligned dangling pointers
  and replace `ptr::invalid()` or `NonNull::dangling`-style manual invalid
  pointer construction.
- For deliberately exposing and later reconstructing an address, pair
  `<ptr>::expose_provenance()` with `ptr::with_exposed_provenance` or
  `ptr::with_exposed_provenance_mut`.

```rust
let tagged = p.map_addr(|a| a | 1);
let untagged = tagged.map_addr(|a| a & !1);
let is_tagged = tagged.addr() & 1 == 1;
```

`ptr::with_exposed_provenance{,_mut}` becomes const-callable in `1.91.0`.
That release's `integer_to_ptr_transmutes` warning directs intentional
reconstruction to these APIs or to a plain `as` cast.

### Raw reference formation

Forming `&raw const *p` through a raw-pointer dereference is safe from `1.84.0`
because it performs no memory access. Forming a raw pointer to a union field is
likewise safe from `1.92.0`. Dereferencing either result still requires valid
unsafe reasoning.

```rust
fn reborrow(p: *const u32) -> *const u32 { &raw const *p }

union U { a: u32, b: f32 }
fn field_ptr(u: &U) -> *const u32 { &raw const u.a }
```

Volatile reads and writes to non-Rust memory, including address zero, are
allowed from `1.90.0`, supporting MMIO use cases.

### Raw pointer invariants and helpers

Trait-object upcasting makes raw trait-object pointer metadata significant:
never fabricate a raw trait-object pointer with a bogus vtable, even
transiently (`1.86.0`). Casting a raw trait object to add an auto trait is a
hard error (`ptr_cast_add_auto_to_object`, `1.87.0`).

`<*const T>::as_ref_unchecked`, `<*mut T>::as_ref_unchecked`, and
`as_mut_unchecked` create references without an `Option` wrapper (`1.95.0`).
`<[T]>::element_offset(&T)` reports the index only when a reference points into
the slice (`1.94.0`). Raw slice pointers also gain checked `as_array` and
`as_mut_array` views in `1.93.0`.

`offset_from_unsigned` and `byte_offset_from_unsigned` on `*const`, `*mut`, and
`NonNull` return `usize` offsets and require `self >= origin` (`1.87.0`). These
replace nightly `sub_ptr`.

With debug assertions, rustc inserts non-unwinding null checks for nonzero-sized
reads and writes and raw-pointer-to-reference reborrows (`1.86.0`). These checks
may be absent from dependencies or std built without debug assertions and are a
debugging aid, never a soundness guarantee.

## Pinning and temporary lifetimes

From `1.92.0`, temporaries passed to a non-extended `pin!` invocation or to
`format_args!`-based macros are not lifetime-extended. Bind the temporary to a
local first when the resulting borrow must survive.

`pin!` no longer deref-coerces in `1.97.0`. If `x: &mut T`, then `pin!(x)`
produces `Pin<&mut &mut T>`, not `Pin<&mut T>`. Code relying on the old coercion
must use an explicit reborrow, `Pin::new`, or `Pin::as_mut`.

Downstream crates cannot implement `DerefMut` for `Pin<LocalType>` from
`1.92.0`. In `1.96.0`, unsize coercions into `Pin<Foo>` are removed when `Foo`
does not implement `Deref`.

## Allocation and staged initialization

### Zeroed allocation

`Box::new_zeroed`, `Box::new_zeroed_slice`, `Rc::new_zeroed`,
`Arc::new_zeroed`, and the slice forms are stable in `1.92.0`. They use
`alloc_zeroed` and return smart pointers containing `MaybeUninit`; the caller
must establish that the all-zero representation is valid before `assume_init`.

```rust
let bytes: Box<[MaybeUninit<u8>]> = Box::new_zeroed_slice(1 << 20);
let bytes: Box<[u8]> = unsafe { bytes.assume_init() };
```

### `MaybeUninit` and ownership transfer

- `Box<MaybeUninit<T>>::write(value) -> Box<T>` is stable from `1.87.0`.
- `MaybeUninit` slices gain `assume_init_ref`, `assume_init_mut`,
  `assume_init_drop`, `write_copy_of_slice`, and `write_clone_of_slice` in
  `1.93.0`.
- Array-shaped conversions between `MaybeUninit<[T; N]>` and
  `[MaybeUninit<T>; N]` arrive in `1.95.0`.
- `Vec::into_raw_parts` and `String::into_raw_parts` return pointer, length,
  and capacity from `1.93.0`.

Global allocators written in Rust may use `thread_local!` and
`std::thread::current()` from `1.93.0`; allocations made by those operations
are routed to the system allocator to avoid re-entering the global allocator.

`Layout` gains `dangling_ptr`, `repeat`, `repeat_packed`, and `extend_packed` in
`1.95.0`. Earlier const-callable layout operations are listed in
[standard-library.md](standard-library.md).

## Atomics and arithmetic primitives

`AtomicPtr` gains `fetch_ptr_add`/`fetch_ptr_sub` in units of `T`, byte-offset
`fetch_byte_add`/`fetch_byte_sub`, and `fetch_or`/`fetch_and`/`fetch_xor` for
tagged-pointer operations (`1.91.0`).

`AtomicBool`, `AtomicPtr`, and integer atomics gain `update` and `try_update`
(`1.95.0`). `update(set_order, fetch_order, f)` runs an infallible update in a
CAS loop. `try_update` accepts `FnMut(T) -> Option<T>` and returns
`Result<T, T>`. Unlike `fetch_update`, success returns the new value; failure
carries the unchanged value.

Unsigned integer bigint primitives `carrying_add`, `borrowing_sub`,
`carrying_mul`, `carrying_mul_add`, and `checked_signed_diff` are stable in
`1.91.0`; `checked_signed_diff` returns the same-width signed `Option`. Integers
add `unchecked_shl`, `unchecked_shr`, and signed
`unchecked_neg` in `1.93.0`.

`cfg(target_has_atomic_primitive_alignment)` distinguishes targets where an
atomic has the corresponding primitive's alignment (`1.97.0`), including the
important counterexample of `AtomicU64` on 32-bit x86.

## Target features, intrinsics, and assembly

### Safe target-feature functions

Safe functions may use `#[target_feature]` from `1.86.0`. They are safe to call
only from code with the same feature enabled; other callers need an unsafe call
guarded by runtime feature detection. Such functions cannot satisfy `Fn`
bounds, and function-pointer coercion is allowed only inside a function with
the feature.

This stabilization was tracked as `target_feature_11`.

```rust
#[target_feature(enable = "avx2")]
fn requires_avx2() {}

fn checked_call() {
    if is_x86_feature_detected!("avx2") {
        unsafe { requires_avx2() };
    }
}
```

Most `std::arch` intrinsics that were unsafe only because they required target
features become safe in a suitably annotated function in `1.87.0`. Existing
SIMD code may acquire `unused_unsafe` warnings. Pointer-taking intrinsics remain
unsafe.

AVX-512 feature families and intrinsics plus x86 `sha512`, `sm3`, `sm4`, `kl`,
and `widekl` are stable in `1.89.0`. LoongArch stabilizes `f`, `d`, `frecipe`,
`lasx`, `lbt`, `lsx`, and `lvz`. In `1.94.0`, x86 `avx512fp16`, AArch64 NEON
fp16 intrinsics except those using unstable `f16`, and 29 more RISC-V features
become stable.

### Inline and naked assembly

The `asm_goto` capability lets inline assembly jump to a Rust block using a
`label` operand (`1.87.0`).
The block must have type `()` or `!`, and combining labels with output operands
remains unstable.

```rust
unsafe {
    asm!("jmp {}", label { println!("jumped from asm!"); });
}
```

Naked functions (`1.88.0`) use `#[unsafe(naked)]`, contain exactly one
`naked_asm!` invocation, and have no compiler-generated prologue or epilogue.
They need an explicit non-Rust ABI because the assembly handles arguments and
return itself.

```rust
#[unsafe(naked)]
pub unsafe extern "sysv64" fn wrapping_add(a: u64, b: u64) -> u64 {
    core::arch::naked_asm!("lea rax, [rdi + rsi]", "ret")
}
```

The `asm_cfg` capability allows individual template strings and operands in
`asm!`, `global_asm!`, and `naked_asm!` to carry `#[cfg(...)]` from `1.93.0`.
Inline assembly stabilizes
for PowerPC/PowerPC64 in `1.95.0` and s390x vector registers in `1.96.0`.

`-Cjump-tables=bool` is stable as the inverse of former `-Zno-jump-tables`
(`1.93.0`); pass `-Cjump-tables=no` to disable them. The default remains `yes`.

## FFI declarations and ABI contracts

### Explicit and supported ABIs

`missing_abi` warns by default from `1.86.0`; spell `extern "C"` on blocks and
function types. Declaring a calling convention unsupported by the current
target became a hard error in `1.84.0`, and `1.90.0` applies rejection in all
positions, including function-pointer types in trait impls.

Vector types in a non-Rust ABI require the corresponding target feature; use
without it is a hard error from `1.88.0`.

### C integer and character compatibility

`core::ffi::c_char` follows each platform's C compiler from `1.85.0`, changing
between `i8` and `u8` on many embedded Arm and RISC-V targets. Code must not
assume `i8`; `libc` 0.2.169 or newer matches the definition.

`i128` and `u128` are accepted in `extern "C"` signatures from `1.89.0`. They
match C `__int128` where it exists, have no corresponding C type where it does
not, and are not compatible with `_BitInt(128)` on x86-64. The `repr128`
capability also stabilizes `#[repr(u128)]` and `#[repr(i128)]` for fieldless
enums.

On AVR, `c_double` is `f32` from `1.96.0` to match C.

### Cross-crate symbol contracts

`#[track_caller]` may be combined with `#[no_mangle]` from `1.92.0`, but the
attribute changes the ABI by appending a caller-location argument. Every
declaration of that symbol, including declarations in foreign blocks of other
crates, must also carry `#[track_caller]`.

`Location::file_as_c_str` (`1.92.0`) passes panic-location paths to FFI without
a UTF-8 conversion.

Repeated `export_name`, `link_name`, or `link_section` attributes use the first
one from `1.96.0`. `1.97.0` rejects empty `export_name`, malformed link names,
and invalid Mach-O link-section specifiers.

### WebAssembly C ABI and imports

`wasm32-unknown-unknown` changes to the standards-compliant C ABI in `1.89.0`.
This silently breaks ABI compatibility with older objects; rebuild every object
on both sides. From `1.96.0`, Wasm linkers no longer receive
`--allow-undefined`; undefined symbols error unless the link flag is restored
intentionally or an import is declared with
`#[link(wasm_import_module = "env")]`.

### Representation is not an implicit contract

Future-compatibility checks warn on repr-C enum discriminants that do not fit
`c_int`/`c_uint` and transparent types that ignore a repr-C field (`1.93.0`).
The layout algorithm for enums without explicit `repr` changes again in
`1.97.0`; do not depend on a particular encoding.

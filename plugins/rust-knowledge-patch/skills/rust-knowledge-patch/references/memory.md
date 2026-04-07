# Memory & Unsafe (1.84–1.94)

## Strict Provenance APIs — 1.84

For unsafe code that manipulates pointer bits. Avoids losing provenance through integer casts.

```rust
use std::ptr;

// Create a dangling (non-null, well-aligned) pointer for sentinel use
let p: *const u8 = ptr::dangling();

// Work with pointer address without losing provenance
let addr = p.addr();              // usize, provenance preserved
let p2 = p.with_addr(addr);      // reconstruct with same provenance
let p3 = p.map_addr(|a| a & !7); // modify address bits, same provenance

// Expose provenance (allows round-trip through integer, marks as "exposed")
let addr: usize = p.expose_provenance();
let p4 = ptr::with_exposed_provenance::<u8>(addr);

// Create pointer with no provenance (for sentinel/tagged values only)
let p5: *const u8 = ptr::without_provenance(0x1);
let p6: *mut u8   = ptr::without_provenance_mut(0x1);
```

**When to use:**
- `addr()` / `with_addr()` / `map_addr()`: normal pointer-tagging (low-bit tricks, arena offsets)
- `expose_provenance()` / `with_exposed_provenance()`: when you must round-trip through an integer (FFI, external allocators)
- `without_provenance()`: sentinel values that are never dereferenced
- `dangling()`: typed null-like pointer that passes alignment checks

## `NonNull::from_ref` / `NonNull::from_mut` — 1.89

Safe constructors from references (no unsafe, no manual casting).

```rust
use std::ptr::NonNull;

let x = 42i32;
let p: NonNull<i32> = NonNull::from_ref(&x);
// Previously: NonNull::new(&x as *const _ as *mut _).unwrap()

let mut y = 42i32;
let p: NonNull<i32> = NonNull::from_mut(&mut y);
// Previously: NonNull::new(&mut y as *mut _).unwrap()
```

## `MaybeUninit` Slice Methods — 1.93

New safe/unsafe helpers for `[MaybeUninit<T>]`.

```rust
use std::mem::MaybeUninit;

let mut buf: [MaybeUninit<u8>; 4] = MaybeUninit::uninit_array();

// Initialize from existing slice:
buf.write_copy_of_slice(&[1, 2, 3, 4]);   // T: Copy
buf.write_clone_of_slice(&[1, 2, 3, 4]);  // T: Clone

// Treat initialized slice as initialized (unsafe):
let init: &[u8] = unsafe { buf.assume_init_ref() };
let init_mut: &mut [u8] = unsafe { buf.assume_init_mut() };

// Drop initialized elements (unsafe — assumes they are initialized):
unsafe { buf.assume_init_drop() };
```

## `Box/Rc/Arc::new_zeroed` / `new_zeroed_slice` — 1.92

Allocate zero-initialized memory. Returns `Box<MaybeUninit<T>>` — call `assume_init()` (unsafe) to use.

```rust
// Single value:
let b: Box<MaybeUninit<[u8; 1024]>> = Box::new_zeroed();
let b: Box<[u8; 1024]> = unsafe { b.assume_init() };

// Slice:
let s: Box<[MaybeUninit<u8>]> = Box::new_zeroed_slice(1024);
let s: Box<[u8]> = unsafe { s.assume_init() };

// Also available on Rc and Arc:
let r: Rc<MaybeUninit<u32>> = Rc::new_zeroed();
let a: Arc<MaybeUninit<u32>> = Arc::new_zeroed();
let r: Rc<[MaybeUninit<u8>]> = Rc::new_zeroed_slice(64);
let a: Arc<[MaybeUninit<u8>]> = Arc::new_zeroed_slice(64);
```

**Use case:** Large zero-initialized buffers without writing a default value first.

## `String::into_raw_parts` / `Vec::into_raw_parts` — 1.93

Decompose without `mem::forget`. Previously: `.as_mut_ptr()` + `.len()` + `.capacity()` + `mem::forget(v)`.

```rust
let s = String::from("hello");
let (ptr, len, cap) = s.into_raw_parts();
// s is consumed; ptr is now the sole owner
let s = unsafe { String::from_raw_parts(ptr, len, cap) };

let v: Vec<u8> = vec![1, 2, 3];
let (ptr, len, cap) = v.into_raw_parts();
let v = unsafe { Vec::from_raw_parts(ptr, len, cap) };
```

# Standard Library

Use this reference to select stable APIs, check their minimum release, and account for observable contract changes. Low-level preconditions for pointers, allocation, atomics, and FFI are expanded in [safety-ffi-and-low-level.md](safety-ffi-and-low-level.md).

## Collections and simultaneous access

### Disjoint mutable borrowing

Slices and `HashMap` provide `get_disjoint_mut` and `get_disjoint_unchecked_mut` from 1.86.0. Slices return `GetDisjointMutError` from the checked form.

```rust
let values = &mut [1, 2, 3];
if let Ok([first, last]) = values.get_disjoint_mut([0, 2]) {
    *first = 10;
    *last = 30;
}
```

Use the checked operation unless distinctness is already guaranteed; the unchecked form requires every selected location to be in bounds and mutually disjoint.

### Conditional extraction

- `Vec::extract_if` and `LinkedList::extract_if` provide draining iterators for selected elements from 1.87.0.
- `BTreeMap::extract_if` and `BTreeSet::extract_if` are stable from 1.91.0.
- B-tree `Entry` and `VacantEntry` gain `insert_entry` from 1.92.0.

### B-tree and heap contracts

- Appending a B-tree entry whose key is already present no longer replaces the stored key (1.93.0); the existing key object is retained.
- Some `BinaryHeap` methods no longer require `T: Ord` (1.94.0); check the individual method rather than adding an unnecessary bound.

## Slices, arrays, and views

### Splitting and windows

- Slice references gain `split_off`, `split_off_mut`, and first/last variants (1.87.0).
- `array_windows` iterates overlapping `&[T; N]` windows rather than dynamically sized `&[T]` windows (1.94.0), with `N` inferable from destructuring:

  ```rust
  fn has_double(values: &[u8]) -> bool {
      values.array_windows().any(|[a, b]| a == b)
  }
  ```

- Slices gain `element_offset` in 1.94.0.

### Repetition and cell views

- `core::array::repeat` is stable from 1.91.0.
- `Cell::as_array_of_cells` is stable from 1.91.0.
- `Cell<[T; N]>` and `Cell<[T]>` implement `AsRef` views as arrays or slices of `Cell<T>` from 1.95.0.
- `MaybeUninit<[T; N]>` gains `AsRef` and `AsMut` array and slice views plus conversion to and from `[MaybeUninit<T>; N]` in 1.95.0.

## Iterators and ranges

### Repeat behavior

Calling `last` or `count` on `iter::Repeat` panics from 1.92.0 instead of looping forever. Do not use terminal traversal on an infinite iterator.

### Peekable and fused iterators

- `Peekable::next_if_map` and `next_if_map_mut` are stable from 1.94.0.
- `Fuse::<I>::default()` wraps `I::default()` from 1.90.0 instead of always constructing an empty iterator.
- `vec::IntoIter<T>` no longer requires `T: RefUnwindSafe` to implement `UnwindSafe` (1.93.0).

### New range family

`core::range::RangeInclusive`, `RangeInclusiveIter`, and the module itself are stable from 1.95.0. From 1.96.0, `core::range::{Range, RangeFrom, RangeToInclusive}` and their iterator types are stable; the range values use `IntoIterator` instead of implementing `Iterator`, so the ranges can be `Copy`. Ranges of `NonZero` integers are iterable, and the new `RangeInclusive` exposes its fields.

`core::hint::cold_path` is also stable from 1.95.0 for marking an unlikely branch.

Range syntax still creates legacy `core::ops` types. Construct a `core::range` value explicitly when the concrete type matters, and accept `RangeBounds` in public APIs that should support both families.

```rust
use core::range::Range;

#[derive(Clone, Copy)]
struct Span(Range<usize>);
```

## I/O, files, and processes

### Error kinds and C strings

- `std::io::ErrorKind` gains `QuotaExceeded` and `CrossesDevices` (1.85.0).
- On Windows, writing after shutting down a socket's write side returns `ErrorKind::BrokenPipe` instead of `Other` (1.97.0).
- `FromBytesWithNulError`, returned by `CStr::from_bytes_with_nul`, is an enum from 1.86.0, allowing callers to distinguish conversion failures.

### File locking and removal

- `File::{lock, lock_shared, try_lock, try_lock_shared, unlock}` provides portable file locking from 1.89.0.
- `RwLockWriteGuard::downgrade` is stable from 1.92.0.
- On recent Windows, `std::fs::remove_file` removes a read-only file instead of failing solely due to the attribute (1.86.0).
- The file-lock family is available on illumos from the 1.91.1 regression fix.

### Anonymous pipes

`std::io::pipe()` returns `PipeReader` and `PipeWriter`, integrates with `Command` through `Stdio`, and converts to owned file descriptors or Windows handles (1.87.0). Read from the pipe before waiting for the child; waiting first can deadlock when the OS buffer fills.

```rust
let (mut recv, send) = std::io::pipe()?;
let mut child = std::process::Command::new("tool")
    .stdout(send.try_clone()?)
    .stderr(send)
    .spawn()?;
let mut output = Vec::new();
std::io::Read::read_to_end(&mut recv, &mut output)?;
child.wait()?;
```

### Thread and socket behavior

- Panic output includes the thread ID (1.91.0).
- Thread creation returns an error rather than panicking when the requested stack size cannot be set (1.91.0).
- On Unix, `UnixStream` writes use `MSG_NOSIGNAL` (1.90.0). Handle the returned error instead of relying on a termination signal.
- `std::fs::File` implements `Send` on UEFI from 1.97.0.

## Environment, time, and platform modules

### Home-directory lookup

- On Windows, `std::env::home_dir()` ignores the nonstandard `HOME` variable from 1.85.0. It remained deprecated in that release.
- `home_dir()` is no longer deprecated from 1.87.0.
- On Unix, it falls back to platform lookup when `HOME` is empty from 1.90.0.

### Time and platform APIs

- On Windows, `SystemTime::checked_sub_duration` returns `None` for results before the Windows epoch, 1601-01-01 (1.94.0).
- `std::os::darwin` is public from 1.84.0 as a shared module for Darwin-family targets.

## Numerics and arithmetic

### Midpoints and bit operations

- Floating-point, unsigned integer, and unsigned `NonZero` midpoint methods are stable from 1.85.0; signed-integer midpoint is stable from 1.87.0.
- Integers gain `unbounded_shl` and `unbounded_shr` in 1.87.0.
- Integer primitives and their `NonZero` forms gain `isolate_highest_one`, `isolate_lowest_one`, `highest_one`, and `lowest_one` (1.97.0); unsigned forms also gain `bit_width`.

### Signed/unsigned mixed arithmetic

- Unsigned integers gain `checked_sub_signed`, `overflowing_sub_signed`, `saturating_sub_signed`, and `wrapping_sub_signed` (1.90.0).
- The integer `strict_*` family, unsigned `carrying_add`, `borrowing_sub`, `carrying_mul`, `carrying_mul_add`, and `checked_signed_diff` are stable from 1.91.0.
- Integer primitives implement fallible conversion to `bool` from 1.95.0.

### Floating-point and constants

- `f32` and `f64` provide `abs`, `signum`, and `copysign` in `core` from 1.84.0, making them available to `#![no_std]` crates.
- Euler's constant and the golden ratio are available as `f32` and `f64` constants from 1.94.0.

## Text, paths, formatting, and lazy values

### Paths and strings

- `Path::file_prefix`, `PathBuf::add_extension`, and `PathBuf::with_added_extension` are stable from 1.91.0.
- `Path` and `PathBuf` can compare directly with strings from 1.91.0.
- `str::ceil_char_boundary` and `floor_char_boundary` are stable from 1.91.0.
- `TryFrom<char> for usize` is stable from 1.94.0.

### Formatting values

`format_args!()` results can be stored in a variable from 1.89.0:

```rust
let name = "Rust";
let message = format_args!("hello, {name}");
println!("{message}");
```

`std::fmt::from_fn` and its `FromFn` value create callback-backed formatting from 1.93.0; the closure receives a `Formatter`.

### Lazy initialization

`LazyCell` and `LazyLock` gain `get`, `get_mut`, and `force_mut` from 1.94.0.

## Other stable APIs and contracts

- `NonZero<char>` is stable from 1.89.0.
- `CStr`, `CString`, and `Cow<CStr>` compare directly from 1.90.0.
- `IntErrorKind` is `Copy` and `Hash` from 1.90.0.
- `proc_macro::Ident::new` accepts `$crate` from 1.90.0.
- Pinned `Box`, `Rc`, and `Arc` values implement `Default` when their pointer type does (1.91.0).
- Unsigned `Saturating` values implement `Sum` and `Product` from 1.91.0.
- `core::panic::Location::file` has a less restrictive return lifetime from 1.91.0.
- Comparator argument order is guaranteed for `std::cmp` `_by` forms of `min`, `max`, and `minmax` from 1.91.0.
- `Location::file_as_c_str` is stable from 1.92.0.
- `TokenStream` implements `Extend` for `Group`, `Literal`, `Punct`, and `Ident` from 1.92.0.

## Allocation and collection contracts

`Vec::with_capacity` guarantees an allocation for the requested amount from 1.87.0 even when `capacity()` later reports a different amount. Raw-pointer `Debug` output includes pointer metadata from the same release.

Ignoring a returned `ControlFlow` warns from 1.87.0 because it is `#[must_use]`. Later exceptions for infallible unit results are described in [language-and-macros.md](language-and-macros.md).

## Const-stable operations

Runtime stability does not imply const stability. Use the following minimum releases.

### Memory, pointers, and pinning

- 1.84.0: raw-pointer `is_null`, `as_ref`, and `as_mut`; `Pin::{new, new_unchecked, get_ref, into_ref, get_mut, get_unchecked_mut, static_ref, static_mut}`; atomic `from_ptr` operations described in the low-level reference.
- 1.85.0: `size_of_val`, `align_of_val`, `mem::swap`, `ptr::swap`, `NonNull::new`, `MaybeUninit::write`, `HashMap::with_hasher`, `HashSet::with_hasher`, `BuildHasherDefault::new`, and `Layout::{for_value, align_to, pad_to_align, extend, array}`.
- 1.86.0: `hint::black_box`, `io::Cursor::{get_mut, set_position}`, and `str::{is_char_boundary, split_at, split_at_checked, split_at_mut, split_at_mut_checked}`.
- 1.87.0: `core::str::from_utf8_mut`, slice `copy_from_slice`, common `String` and `Vec` accessors including mutable slice, string, vector, and pointer forms.
- 1.88.0: `NonNull::replace`, raw-pointer `replace`, `ptr::swap_nonoverlapping`, and `Cell::{replace, get, get_mut, from_mut, as_slice_of_cells}`.
- 1.89.0: array `as_mut_slice`.
- 1.90.0: slice `reverse`.
- 1.91.0: array `each_ref` and `each_mut`, `OsString::new`, `PathBuf::new`, `TypeId::of`, and exposed-provenance pointer constructors.
- 1.92.0: slice `rotate_left` and `rotate_right`.

### Numeric, character, and text operations

- 1.85.0: floating-point `recip`, degree/radian conversions, `max`, `min`, `clamp`, `abs`, `signum`, and `copysign`.
- 1.87.0: `char::{is_digit, is_whitespace}`.
- 1.89.0: ASCII-case-insensitive equality for byte slices and strings.
- 1.90.0: `f32` and `f64` `floor`, `ceil`, `trunc`, `fract`, `round`, and `round_ties_even`.
- 1.94.0: floating-point `mul_add`.
- 1.97.0: `char::is_control`.

### Slices, networking, formatting, and control flow

- 1.87.0: `SocketAddr*` IP, port, flow-info, and scope setters; slice `as_flattened` and `as_flattened_mut`.
- 1.95.0: `fmt::from_fn` and `ControlFlow::{is_break, is_continue}`.

Standard macros such as `assert_eq!` and `vec!` also accept const-block expressions from 1.87.0.

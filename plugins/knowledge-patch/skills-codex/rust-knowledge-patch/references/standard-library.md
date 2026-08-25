# Standard Library

## Collections, slices, and iterators

### Borrowed slices and fixed-size views

- Since 1.87.0, slices provide `split_off`, `split_off_mut`, and first/last variants to consume part of a borrowed view without allocation.
- Since 1.88.0, `as_chunks`/`as_rchunks` families, including mutable and unchecked forms, expose arrays plus a remainder.
- Since 1.94.0, `array_windows` iterates overlapping windows as `&[T; N]`; array patterns and use sites can infer `N`.
- Since 1.94.0, slices also expose `element_offset`.

### Conditional extraction and mutable insertion

- `HashMap::extract_if` and `HashSet::extract_if` remove and yield selected entries since 1.88.0.
- `BTreeMap::extract_if` and `BTreeSet::extract_if` do the same since 1.91.0.
- Since 1.95.0, `Vec::{push_mut, insert_mut}`, matching front/back/indexed `VecDeque` methods, and `LinkedList::{push_front_mut, push_back_mut}` return mutable access to newly inserted elements.
- Some `BinaryHeap<T>` methods dropped unnecessary `T: Ord` bounds in 1.94.0.
- `[T; N]::from_fn` is guaranteed since 1.88.0 to invoke a stateful initializer in increasing index order.

### Iterator behavior and traits

- `ControlFlow` became `#[must_use]` in 1.87.0.
- `array::IntoIter: Default`, `slice::ChunkBy: Clone`, and `io::Take: Seek` were added in 1.89.0.
- `Fuse<I>::default()` wraps `I::default()` instead of always producing an empty iterator as of 1.90.0.
- `Iterator::last` and `Iterator::count` on `iter::Repeat` panic rather than loop forever as of 1.92.0.
- `Peekable::{next_if_map, next_if_map_mut}` are stable since 1.94.0.
- `iter::RepeatN: Default` is stable since 1.97.0.

## Ranges, patterns, and cells

### Copyable range family

- `core::range::RangeInclusive` and `RangeInclusiveIter` became stable in 1.95.0.
- `core::range::{Range, RangeFrom, RangeToInclusive}` and their iterator types followed in 1.96.0. Iterable values implement `IntoIterator`, not `Iterator`, so range values can be `Copy`.
- Range syntax still creates legacy `core::ops` types. Accept `impl RangeBounds` when an API should support both families.
- Ranges with `NonZero` integer endpoints are iterable since 1.96.0.

### Cell and text views

- `Cell<[T; N]>::as_array_of_cells` exposes independently writable cells since 1.91.0.
- `str::{floor_char_boundary, ceil_char_boundary}` move arbitrary byte positions to neighboring UTF-8 boundaries since 1.91.0.
- Array- and slice-backed `Cell` values implement `AsRef` for per-element cell views since 1.95.0.

## Files, paths, sockets, and environment

### Home directories and Windows files

- On Windows, `std::env::home_dir()` stopped consulting nonstandard `HOME` in 1.85.0; it was still deprecated in that release and became undeprecated in 1.87.0.
- On Unix, an empty `HOME` triggers the fallback lookup since 1.90.0.
- On recent Windows systems, `std::fs::remove_file` can remove read-only files since 1.86.0.

### Locking and I/O behavior

- `File::{lock, try_lock, lock_shared, try_lock_shared, unlock}` are stable since 1.89.0.
- `RwLockWriteGuard::downgrade` converts a write guard directly into a read guard since 1.92.0.
- Unix `UnixStream` writes use `MSG_NOSIGNAL` since 1.90.0. Exit on the returned write error rather than expecting `SIGPIPE`.
- After write-side shutdown, a subsequent Windows socket write returns `ErrorKind::BrokenPipe` rather than `Other` since 1.97.0.

### Paths and time

- Since 1.91.0, `Path::file_prefix` returns the portion before the first non-leading dot; `PathBuf::{add_extension, with_added_extension}` append rather than replace an extension.
- Since 1.94.0, Windows `SystemTime::checked_sub_duration` returns `None` for a result before 1601-01-01.

## Numerics and atomics

### Strict and multiword arithmetic

- Since 1.91.0, integer `strict_*` arithmetic, division, remainder, negation, shifts, powers, and mixed-signed operations always panic on overflow, independent of profile settings.
- Also since 1.91.0, unsigned integers provide `carrying_add`, `borrowing_sub`, `carrying_mul`, `carrying_mul_add`, and `checked_signed_diff`; `Saturating<uN>` implements `Sum` and `Product`.
- Since 1.97.0, integer and `NonZero` integer types have `isolate_highest_one`, `isolate_lowest_one`, `highest_one`, and `lowest_one`; unsigned variants also have `bit_width`.

### Floating point and conversions

- `f32`/`f64` `abs`, `signum`, and `copysign` moved into `core` in 1.84.0 for `no_std` use.
- `f32`/`f64` gained `EULER_GAMMA` and `GOLDEN_RATIO` in 1.94.0.
- `usize: TryFrom<char>` is stable since 1.94.0.
- `bool: TryFrom<integer primitive>` provides checked 0/1 conversion since 1.95.0.

### Atomic operations

- Since 1.91.0, `AtomicPtr` supports element-scaled `fetch_ptr_add`/`fetch_ptr_sub`, byte-scaled `fetch_byte_add`/`fetch_byte_sub`, and `fetch_or`/`fetch_and`/`fetch_xor`.
- Since 1.95.0, atomic pointer, boolean, signed, and unsigned types support closure-based `update` and `try_update`.

## Strings, formatting, FFI helpers, and contracts

- `FromBytesWithNulError` became an inspectable enum in 1.86.0, letting callers distinguish `CStr::from_bytes_with_nul` failures.
- Wide raw-pointer `Debug` output includes pointer metadata since 1.87.0, which can change logs and snapshots.
- Formatting width and precision are capped at 16 bits on every target since 1.87.0.
- Placeholder-bearing `format_args!` values can be stored in variables since 1.89.0, while borrowed inputs must still outlive use.
- `std::fmt::{from_fn, FromFn}` create ad hoc formatting values from closures since 1.93.0.
- `LazyCell` and `LazyLock` implement `DerefMut` since 1.89.0 and add `get`, `get_mut`, and `force_mut` in 1.94.0.
- `NonZero<char>` and Linux `TcpStreamExt::{quickack, set_quickack}` are stable since 1.89.0.
- `ffi::FromBytesUntilNulError: Copy` and `File: Send` on UEFI are stable since 1.97.0.
- Since 1.91.0, panic messages include thread IDs, thread-stack-size application failures return errors rather than panicking internally, and `_by` forms of `min`, `max`, and `minmax` guarantee comparator argument order.
- Since 1.92.0, `unused_must_use` ignores `Result<(), Uninhabited>` and `ControlFlow<Uninhabited, ()>`; 1.97.0 generalizes treatment to the corresponding successful value `T`.
- Since 1.92.0, procedural-macro `TokenStream` implements `Extend` directly for `Group`, `Literal`, `Punct`, and `Ident`.
- `std::char` functions and constants are deprecated since 1.97.0; use primitive `char` associated items.

## Const-stable API inventory

Runtime-stable APIs do not automatically work in const contexts. The following release-specific additions are part of the compatibility surface.

### 1.84.0

- Atomic integer types, `AtomicBool`, and `AtomicPtr`: `from_ptr`.
- Raw pointers: `is_null`, `as_ref`, `as_mut`.
- `Pin`: `new`, `new_unchecked`, `get_ref`, `into_ref`, `get_mut`, `get_unchecked_mut`, `static_ref`, `static_mut`.

### 1.85.0

- `mem::{size_of_val, align_of_val, swap}`, `ptr::swap`, `NonNull::new`, and `MaybeUninit::write`.
- `Layout::{for_value, align_to, pad_to_align, extend, array}`.
- `HashMap::with_hasher`, `HashSet::with_hasher`, and `BuildHasherDefault::new`.
- Floating-point `recip`, `to_degrees`, `to_radians`, `max`, `min`, `clamp`, `abs`, `signum`, and `copysign`.

### 1.86.0

- `hint::black_box`, `io::Cursor::{get_mut, set_position}`.
- `str::{is_char_boundary, split_at, split_at_checked, split_at_mut, split_at_mut_checked}`.

### 1.87.0

- `core::str::from_utf8_mut`, slice copying and nested-slice flattening, socket-address setters, and `char::{is_digit, is_whitespace}`.
- `String::{into_bytes, as_str, capacity, as_bytes, len, is_empty, as_mut_str, as_mut_vec}`.
- `Vec::{as_ptr, as_slice, capacity, len, is_empty, as_mut_slice, as_mut_ptr}`.

### 1.88.0

- `NonNull::replace`, raw-pointer `replace`, `ptr::swap_nonoverlapping`.
- `Cell::{replace, get, get_mut, from_mut, as_slice_of_cells}`.

### 1.89.0

- Array `as_mut_slice` and ASCII case-insensitive equality for byte slices and strings.

### 1.90.0

- Slice `reverse` and floating-point `floor`, `ceil`, `trunc`, `fract`, `round`, and `round_ties_even`.

### 1.91.0

- Array `each_ref` and `each_mut`, `OsString::new`, `PathBuf::new`, `TypeId::of`.
- `ptr::{with_exposed_provenance, with_exposed_provenance_mut}`.

### 1.92.0

- Slice `rotate_left` and `rotate_right`.

### 1.94.0

- Floating-point `mul_add`.

### 1.95.0

- `fmt::from_fn` and `ControlFlow::{is_break, is_continue}`.

### 1.97.0

- `char::is_control`.

# Standard Library

## Collections, slices, and extraction

### Disjoint mutable access

Slices and `HashMap` can return several mutable references at once from
`1.86.0`. This is the renamed stable form of nightly `get_many_mut`. Slice
`get_disjoint_mut` accepts an array of indices or ranges and
returns `Result<_, slice::GetDisjointMutError>` on overlap or out-of-bounds;
`HashMap::get_disjoint_mut` accepts key references. Both types also expose
unchecked variants.

```rust
let v = &mut [1, 2, 3];
if let Ok([a, b]) = v.get_disjoint_mut([0, 2]) {
    *a = 413;
    *b = 612;
}
```

### Conditional removal

The collection-specific `extract_if` signatures differ:

- `Vec::extract_if(range, predicate)` (`1.87.0`) visits only the range and
  yields removed matches. Dropping the iterator early leaves unvisited values
  in the vector.
- `LinkedList::extract_if(predicate)` (`1.87.0`) has no range.
- `HashMap::extract_if(predicate)` and `HashSet::extract_if(predicate)`
  (`1.88.0`) have no range and arbitrary iteration order.
- `BTreeMap::extract_if(range, predicate)` and
  `BTreeSet::extract_if(range, predicate)` (`1.91.0`) visit a key range and
  yield removals in sort order.

`Vec::pop_if` conditionally removes the last item (`1.86.0`).
`VecDeque::pop_front_if` and `pop_back_if` provide the deque forms in `1.93.0`.

### Insertion and entries

`Vec::push_mut`/`insert_mut`, `VecDeque::push_front_mut`/`push_back_mut`/
`insert_mut`, and `LinkedList::push_front_mut`/`push_back_mut` return a mutable
reference to the inserted element (`1.95.0`).

`btree_map::Entry::insert_entry` and `VacantEntry::insert_entry` return an
`OccupiedEntry`, matching the `HashMap` API (`1.92.0`).

`BTreeMap::append` changed in `1.93.0`: when both maps contain the same key,
the value already in `self` is retained instead of being overwritten by
`other`.

### Slice partitioning and views

The `split_off` family on slice references (`1.87.0`) acts on `&mut &[T]` or
its mutable counterpart, shrinks the cursor in place, and returns `Option`
instead of panicking. The range must be one-sided. The family includes
`split_off`, `split_off_mut`, `split_off_first`, `split_off_first_mut`,
`split_off_last`, and `split_off_last_mut`; it is unrelated to
`Vec::split_off(at)`.

```rust
let mut s: &[i32] = &[1, 2, 3, 4];
let head = s.split_off(..2).unwrap();
let first = s.split_off_first().unwrap();
```

`as_chunks::<N>` and `as_rchunks::<N>` (`1.88.0`) reinterpret a slice as
fixed-size arrays plus a remainder: `as_chunks` leaves a tail remainder and
`as_rchunks` a head remainder. Mutable and unchecked variants exist; `N == 0`
panics. The unchecked methods are `as_chunks_unchecked` and
`as_chunks_unchecked_mut`.

`<[T]>::as_array::<N>()` and `as_mut_array` return checked fixed-array views in
`1.93.0`; raw slice pointers gain corresponding methods. In `1.95.0`,
array-shaped conversions cover `Cell<[T; N]>`/`Cell<[T]>` to `[Cell<T>]` and
`MaybeUninit<[T; N]>` to and from `[MaybeUninit<T>; N]`.

`<[T]>::element_offset(&T)` returns the index only for a reference inside the
slice (`1.94.0`). `Cell::as_array_of_cells` converts `&Cell<[T; N]>` to
`&[Cell<T>; N]` (`1.91.0`).

### Windows over slices and arrays

`array_windows::<N>()` yields overlapping `&[T; N]` windows (`1.94.0`), with
`N` often inferred from a destructuring pattern:

```rust
let has_abba = bytes.array_windows().any(
    |[a1, b1, b2, a2]| a1 != b1 && a1 == a2 && b1 == b2
);
```

`core::array::repeat(value)` clones a value into `[T; N]` when `T` is not
`Copy`, and `core::iter::chain(a, b)` is a receiver-neutral free function
(`1.91.0`). `[T; N]::from_fn` is guaranteed to call its closure in increasing
index order from `1.88.0`.

## Iterators and ranges

### New range family

`core::range::RangeInclusive` and `RangeInclusiveIter` stabilize in `1.95.0`.
`Range`, `RangeFrom`, `RangeToInclusive`, and their `RangeIter`,
`RangeFromIter`, and `RangeToInclusiveIter` types join in `1.96.0`. These range
values are `Copy`, are not themselves iterators, implement `IntoIterator`, and
convert in both directions with legacy `core::ops` ranges. Range syntax still
creates the legacy types.

The new `RangeInclusive` exposes public `start` and `end` fields. `RangeFull`,
`RangeTo`, and `core::range::legacy` re-exports remain future work. Public APIs
that should accept either family should use `RangeBounds`; prefer the new
concrete type when a concrete range must be stored.

Ranges over `NonZero` integers are iterable from `1.96.0`.

### Iterator behavior and helpers

`FromIterator` and `Extend` for tuples cover arities 1 through 12 (`1.85.0`),
allowing one iterator of tuples to collect into multiple collections.

`Peekable::next_if_map` and `next_if_map_mut` consume the peeked item only when
the closure returns `Some` and return that mapped value (`1.94.0`).

`ControlFlow` is `#[must_use]` from `1.87.0`. Its `is_break` and `is_continue`
methods become const-callable in `1.95.0`; discarding a `try_fold`-style result
therefore warns. `iter::Repeat::last()` and
`.count()` panic rather than hanging forever from `1.92.0`.

`core::iter::Fuse::default()` now wraps `I::default()` instead of constructing
an always-empty iterator (`1.90.0`). Several `BinaryHeap<T>` methods no longer
require `T: Ord` (`1.94.0`).

## Numeric operations

### Roots, averages, and multiples

`isqrt` is stable on every integer and `NonZero` type (`1.84.0`). Signed types
also expose `checked_isqrt`, which returns `None` on negative input; `isqrt`
panics there.

Overflow-free `midpoint` stabilizes for floats, unsigned integers, and
`NonZeroU*` in `1.85.0`, and for signed integers in `1.87.0`.

Unsigned integers gain `is_multiple_of` in `1.87.0`. For a zero divisor,
`x.is_multiple_of(0)` is true exactly when `x == 0`; it does not panic.

### Shifts and sign conversion

All integers gain `unbounded_shl` and `unbounded_shr` in `1.87.0`. An oversized
shift yields zero, except right-shifting a negative value yields `-1`.
`cast_signed` and `cast_unsigned` on integers and `NonZero` express a sign-only
reinterpretation without a generic `as` cast.

`unchecked_shl`, `unchecked_shr`, and signed `unchecked_neg` stabilize in
`1.93.0`.

### Overflow policy

The `strict_*` family (`1.91.0`) returns a plain value and always panics on
overflow, including release builds. It includes add, subtract, multiply,
division and remainder variants, negation, shifts, powers, signed absolute
value, and signed/unsigned mixed forms: `strict_add`, `strict_sub`,
`strict_mul`, `strict_div`, `strict_div_euclid`, `strict_rem`,
`strict_rem_euclid`, `strict_neg`, `strict_shl`, `strict_shr`, `strict_pow`,
signed `strict_add_unsigned`, `strict_sub_unsigned`, and `strict_abs`, plus
unsigned `strict_add_signed` and `strict_sub_signed`. This contrasts with
`wrapping_*` and `checked_*`.

Unsigned types also gain `checked_sub_signed`, `overflowing_sub_signed`,
`saturating_sub_signed`, and `wrapping_sub_signed` in `1.90.0`.

### Bit operations

Every integer and `NonZero` type gains `isolate_highest_one`,
`isolate_lowest_one`, `highest_one`, and `lowest_one` in `1.97.0`. Unsigned
types also gain `bit_width`, equivalent to `BITS - leading_zeros()`.

```rust
assert_eq!(0b1011u8.isolate_highest_one(), 0b1000);
assert_eq!(0b1011u8.isolate_lowest_one(), 0b0001);
assert_eq!(0b1011u8.bit_width(), 4);
```

Unsigned bigint primitives `carrying_add`, `borrowing_sub`, `carrying_mul`,
`carrying_mul_add`, and `checked_signed_diff` are stable from `1.91.0`.

### Floating-point and character operations

Float `abs`, `signum`, and `copysign` move into `core` in `1.84.0`, so they are
usable in `no_std`. `next_up` and `next_down` produce adjacent representable
values from `1.86.0`. `{float}::NAN` is guaranteed quiet from `1.88.0`.

`floor`, `ceil`, `trunc`, `fract`, `round`, and `round_ties_even` become
const-callable in `1.90.0`; `mul_add` follows in `1.94.0`. Float constants add
`EULER_GAMMA` and `GOLDEN_RATIO` in `1.94.0`.

`NonZero::count_ones` returns `NonZero<u32>` from `1.86.0`;
`NonZero<uN>::div_ceil` stabilizes in `1.92.0`. `NonZero<char>` exists from
`1.89.0`. `TryFrom<char> for usize` lands in `1.94.0`, and
`TryFrom<{integer}> for bool` accepts only zero or one from `1.95.0`.

`char::MAX_LEN_UTF8` and `MAX_LEN_UTF16` name the 4- and 2-code-unit maxima
(`1.93.0`). Module-level `std::char` constants and functions are deprecated in
favor of the associated items on primitive `char` in `1.97.0`, including
`MAX`, `from_u32`, `from_digit`, `decode_utf16`, and `REPLACEMENT_CHARACTER`;
inherent calls such as `char::from_u32` generally keep their spelling, while
imports should be removed. `char::is_control` is const-callable from `1.97.0`.

## Text, paths, and platform strings

`OsStr::display()` and `OsString::display()` provide lossy, allocation-free
`Display` output (`1.87.0`), avoiding `to_string_lossy()` when only formatting
is needed and avoiding quoted `Debug` output.

`str::from_utf8` and related functions also exist as inherent associated
functions from `1.87.0`. `String::extend_from_within` and
`TryFrom<Vec<u8>> for String` stabilize in the same release.

`str::floor_char_boundary(i)` and `ceil_char_boundary(i)` clamp byte indices to
valid UTF-8 boundaries (`1.91.0`).

`Path::file_prefix` splits before the first dot, while `file_stem` splits before
the last (`1.91.0`). `PathBuf::add_extension` and `with_added_extension` append
instead of replacing it like `set_extension`. `Path` and `PathBuf` compare directly with
`str` and `String` in both directions. `OsString::new` and `PathBuf::new` also
become const-callable in this release.

Unicode data updates to version 17 in `1.94.0`.

## I/O, processes, files, and synchronization

### Anonymous pipes and child processes

`std::io::pipe()` returns `(PipeReader, PipeWriter)` (`1.87.0`); both integrate
with `Stdio`, `OwnedFd`, and `OwnedHandle`. Move or drop every writer so the
reader can observe EOF, and drain the pipe before `wait()` so a full OS buffer
cannot deadlock the child.

```rust
let (mut recv, send) = std::io::pipe()?;
let mut child = Command::new("path/to/bin")
    .stdout(send.try_clone()?)
    .stderr(send)
    .spawn()?;
let mut output = Vec::new();
recv.read_to_end(&mut output)?;
assert!(child.wait()?.success());
```

### File locking

`File::lock`, `lock_shared`, `try_lock`, `try_lock_shared`, and `unlock` are
stable from `1.89.0`. Locks are advisory: they constrain cooperating lockers,
not arbitrary I/O. `lock` and `lock_shared` block; the `try_` forms report
failure instead. Dropping the file releases its lock; re-locking in the same
process is platform-specific. These APIs remove the usual need for `fs2` or
`fd-lock` solely to obtain file locking.

`1.91.1` fixes `File::lock` incorrectly reporting `Unsupported` on illumos,
which prevented Cargo from locking its build directory there.

### Locks, initialization, and lazy values

`Once::wait`, `Once::wait_force`, and `OnceLock::wait` block for another
initializer instead of initializing the value (`1.86.0`).

`RwLockWriteGuard::downgrade(write_guard)` atomically creates a read guard
without allowing another writer between them (`1.92.0`). It is an associated
function, not a method; there is no read-guard upgrade.

`LazyCell` and `LazyLock` implement `DerefMut` from `1.89.0`. They gain `get`,
`get_mut`, and `force_mut` in `1.94.0`. `From<T>` constructs an already
initialized `LazyCell<T, F>` or `LazyLock<T, F>` from `1.96.0`.
`AssertUnwindSafe<T>` also implements `From<T>` from `1.96.0`.

### Sockets and filesystem behavior

- `UnixStream` writes suppress `SIGPIPE` with `MSG_NOSIGNAL` from `1.90.0`;
  a closed peer yields `EPIPE`, so programs relying on signal termination must
  handle the error.
- Linux `TcpStreamExt::{quickack, set_quickack}` exposes `TCP_QUICKACK` from
  `1.89.0`.
- Windows `fs::remove_file` deletes read-only files on recent systems from
  `1.86.0`.
- On Windows, a socket write after shutting down the write half returns
  `io::ErrorKind::BrokenPipe` instead of `Other` from `1.97.0`.

`io::ErrorKind` adds `QuotaExceeded` and `CrossesDevices` in `1.85.0`.

### Threads, panic hooks, and time

`Waker::noop()` returns a no-op `&'static Waker` for manual polling in tests
(`1.85.0`).

`PanicHookInfo::payload_as_str` avoids separate `&str` and `String` downcasts,
and panic messages include the thread id (`1.91.0`). If the OS rejects a thread
stack size, `spawn` returns `io::Error` rather than panicking inside std.

`Ipv4Addr::from_octets`, `Ipv6Addr::from_octets`, and
`Ipv6Addr::from_segments` provide named const constructors from `1.91.0`.

`Duration::from_mins` and `from_hours` land in `1.91.0`;
`Duration::from_nanos_u128` accepts values beyond `u64::MAX` in `1.93.0`.
On Windows, `SystemTime::checked_sub_duration` returns `None` below the 1601
epoch from `1.94.0`.

## Formatting, comparison, and behavior contracts

`std::fmt::from_fn` wraps a formatter callback in a value implementing
`Display` and `Debug` (`1.93.0`):

```rust
let list = std::fmt::from_fn(|f| {
    f.write_str("generated")
});
```

Raw-pointer `Debug` output includes metadata such as slice length or vtable
from `1.87.0`; tests matching the old output must change. Format width and
precision are capped to 16 bits on every target. `Vec::with_capacity` now
guarantees an allocation at least as large as requested even if the reported
capacity differs.

`cmp::min_by`, `max_by`, and `minmax_by` define their tie-breaking argument
order from `1.91.0`.

`BuildHasherDefault::new()` is a named constructor (`1.85.0`). `Cell::update`
applies a function in place, returns `()`, and requires `T: Copy` (`1.88.0`).
`hint::select_unpredictable` chooses eagerly evaluated alternatives while
discouraging a branch (`1.88.0`); use it for genuinely unpredictable hot-loop
conditions. `core::hint::cold_path()` marks a path unlikely from `1.95.0`.

`*const T` and `*mut T` implement `Default` as null from `1.88.0`.
`CStr::from_bytes_with_nul`'s error changes from opaque struct to a matchable
`FromBytesWithNulError` enum in `1.86.0`.

`std::env::home_dir()` on Windows ignores nonstandard `HOME` from `1.85.0`.
Its longstanding deprecation is being lifted in a later release, making it
usable again. On Unix from `1.90.0`, an empty `HOME` counts as unset and the
function falls back to the passwd entry.

## Const-callable inventory

The following become const-callable in `1.85.0`:

- `mem::size_of_val`, `mem::align_of_val`, `mem::swap`, and `ptr::swap`;
- `MaybeUninit::write`, `NonNull::new`;
- `Layout::for_value`, `align_to`, `pad_to_align`, `extend`, and `array`;
- `HashMap::with_hasher`, `HashSet::with_hasher`, and
  `BuildHasherDefault::new`;
- float `recip`, `to_degrees`, `to_radians`, `max`, `min`, `clamp`, `abs`,
  `signum`, and `copysign`.

The `1.86.0` additions are `hint::black_box`, string split methods
`split_at`, `split_at_mut`, `split_at_checked`, `split_at_mut_checked`,
`str::is_char_boundary`, and `Cursor::get_mut`/`set_position`.

In `1.90.0`, float rounding methods and slice `reverse` become const-callable.
`1.91.0` adds `TypeId::of`, array `each_ref`/`each_mut`, `OsString::new`,
`PathBuf::new`, and exposed-provenance pointer constructors. `1.92.0` adds
slice rotation. `1.94.0` adds float `mul_add`. `1.95.0` adds `fmt::from_fn` and
`ControlFlow` predicates. `1.97.0` adds `char::is_control`.

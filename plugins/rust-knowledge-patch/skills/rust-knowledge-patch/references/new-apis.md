# New Stabilized APIs (1.85–1.94)

## Numeric APIs

### `cast_signed()` / `cast_unsigned()` (1.87)

Type-safe sign casting (replaces `as` for sign conversion):

```rust
let x: u32 = 42;
let y: i32 = x.cast_signed();
let z: u32 = y.cast_unsigned();
```

### `is_multiple_of(other)` (1.87)

Cleaner than `x % n == 0`:

```rust
assert!(15u32.is_multiple_of(5));
```

### `midpoint(a, b)` (1.85)

Average without overflow. Available on `f32`, `f64`, `u8`–`u128`:

```rust
let m = u32::midpoint(200, u32::MAX); // correct, no overflow
```

### `unbounded_shl()` / `unbounded_shr()` (1.87)

Shift saturating to 0/sign instead of panicking on out-of-range shift amounts.

### `strict_add/sub/mul/div/rem/shl/shr/pow/neg` (1.91)

Like default arithmetic but **always panics on overflow** (even in release mode). Complements `checked_*`, `wrapping_*`, `saturating_*`:

```rust
let x: u8 = 200u8.strict_add(100); // panics even in release mode
```

### `carrying_add` / `borrowing_sub` / `carrying_mul` / `carrying_mul_add` (1.91)

Extended-precision arithmetic primitives:

```rust
let (sum, carry) = 200u8.carrying_add(100, false);
// sum = 44, carry = true (overflow)
```

### `unchecked_shl` / `unchecked_shr` / `unchecked_neg` (1.93)

UB on overflow — for optimizer hints only.

## Path APIs

### `Path::file_prefix()` (1.91)

Returns portion before the *first* dot (vs `file_stem()` which returns before the *last* dot):

```rust
use std::path::Path;
assert_eq!(Path::new("foo.bar.baz").file_prefix(), Some("foo".as_ref()));
assert_eq!(
    Path::new("foo.bar.baz").file_stem(),
    Some("foo.bar".as_ref())
);
```

### `PathBuf::add_extension("gz")` (1.91)

Appends extension without replacing:

```rust
use std::path::PathBuf;
let mut p = PathBuf::from("archive.tar");
p.add_extension("gz"); // "archive.tar.gz"
// with_added_extension returns a new PathBuf
```

### `Path`/`PathBuf` `PartialEq<str>` (1.91)

Direct comparisons work:

```rust
let p = std::path::Path::new("foo.txt");
assert!(p == "foo.txt");
```

### `OsString::leak()` / `PathBuf::leak()` (1.89)

Convert to `&'static OsStr` / `&'static Path`.

## Duration

### `Duration::from_mins(n)` / `Duration::from_hours(n)` (1.91)

Convenience constructors alongside existing `from_secs`.

## String & Formatting

### `fmt::from_fn` (1.93)

Create a `Display`/`Debug` impl from a closure:

```rust
use std::fmt;
let display = fmt::from_fn(|f| write!(f, "hello {}", 42));
println!("{display}");

fn format_list(items: &[i32]) -> impl fmt::Display + '_ {
    fmt::from_fn(move |f| {
        for (i, item) in items.iter().enumerate() {
            if i > 0 { write!(f, ", ")?; }
            write!(f, "{item}")?;
        }
        Ok(())
    })
}
```

### `format_args!()` Storable in Variables (1.89)

```rust
let args = format_args!("hello {}", name);
writer.write_fmt(args)?;
```

### `str::from_utf8()` Inherent Method (1.87)

Now an inherent method, not just `std::str::from_utf8()`.

### `OsStr::display()` / `OsString::display()` (1.87)

Returns a `Display` impl (lossy).

### `str::ceil_char_boundary(idx)` / `floor_char_boundary(idx)` (1.91)

Find nearest valid UTF-8 char boundary at or above/below byte index.

### `TryFrom<Vec<u8>> for String` (1.87)

Fallible conversion preserving the vec on error.

## Result

### `Result::flatten()` (1.89)

`Result<Result<T, E>, E>` → `Result<T, E>` (like `Option::flatten`).

## Memory & Allocation

### `Box`/`Arc`/`Rc::new_zeroed` (1.92)

Allocate zero-initialized memory:

```rust
let zeroed: Box<MaybeUninit<[u8; 4096]>> = Box::new_zeroed();
let zeroed: Box<[u8; 4096]> = unsafe { zeroed.assume_init() };
// Also: Box::new_zeroed_slice(len), Arc::new_zeroed(), Rc::new_zeroed()
```

### `Vec::into_raw_parts` / `String::into_raw_parts` (1.93)

Decompose into raw components (inverse of `from_raw_parts`):

```rust
let v = vec![1u8, 2, 3];
let (ptr, len, cap) = v.into_raw_parts();
// Reconstruct: unsafe { Vec::from_raw_parts(ptr, len, cap) }
```

### `MaybeUninit::{assume_init_ref, assume_init_mut, assume_init_drop}` (1.93)

Safe(r) access to initialized `MaybeUninit` values.

### `[MaybeUninit<T>]::write_copy_of_slice` / `write_clone_of_slice` (1.93)

Initialize uninitialized slice from an existing slice.

### `NonNull::from_ref(r)` / `NonNull::from_mut(r)` (1.89)

Safe constructors from references.

### `char::MAX_LEN_UTF8` (4) / `char::MAX_LEN_UTF16` (2) (1.93)

Associated constants.

## Miscellaneous

### `ptr::fn_addr_eq` (1.85)

Compare function pointer addresses.

### `io::ErrorKind::QuotaExceeded` / `CrossesDevices` (1.85)

New error kinds.

### `env::home_dir` Undeprecated (1.87)

Now works correctly on all platforms.

## Cargo

### `build.build-dir` (1.91)

Configurable directory for intermediate build artifacts:

```toml
# .cargo/config.toml
[build]
build-dir = "build"
```

### Cargo Config `include` (1.94)

Include other config files:

```toml
include = [{ path = "shared.toml" }, { path = "local.toml", optional = true }]
```

### Compiler: `-O` Means `opt-level=3` (1.86)

`rustc -O` now maps to `-C opt-level=3` (was `2`), matching Cargo's `--release` default.

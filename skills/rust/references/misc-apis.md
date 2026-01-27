# Miscellaneous APIs

## Floats

### `next_up` / `next_down`

Get the next representable floating-point value.

```rust
let x = 1.0_f64;
let next = x.next_up();   // Smallest f64 > 1.0
let prev = x.next_down(); // Largest f64 < 1.0
```

### Const Rounding

Float rounding methods work in const contexts.

```rust
const FLOOR: f64 = 3.7_f64.floor();     // 3.0
const CEIL: f64 = 3.2_f64.ceil();       // 4.0
const TRUNC: f64 = (-3.7_f64).trunc();  // -3.0
const FRACT: f64 = 3.7_f64.fract();     // 0.7
const ROUND: f64 = 3.5_f64.round();     // 4.0
const ROUND_TIES: f64 = 2.5_f64.round_ties_even();  // 2.0
```

## Duration

### Convenience Constructors

```rust
use std::time::Duration;

let five_mins = Duration::from_mins(5);
let two_hours = Duration::from_hours(2);
let huge = Duration::from_nanos_u128(10_000_000_000_000_000_000_000u128);
```

## Result

### `Result::flatten`

Flatten nested `Result<Result<T, E>, E>`.

```rust
let nested: Result<Result<i32, &str>, &str> = Ok(Ok(42));
let flat: Result<i32, &str> = nested.flatten();
assert_eq!(flat, Ok(42));
```

### No `unused_must_use` for Infallible Results

`Result<(), Infallible>` no longer triggers warnings.

```rust
use std::convert::Infallible;
fn cannot_fail() -> Result<(), Infallible> { Ok(()) }
fn main() { cannot_fail(); }  // No warning
```

## Formatting

### `std::fmt::from_fn`

Create `Display` impl from a closure.

```rust
use std::fmt;

let display = fmt::from_fn(|f| write!(f, "Custom: {}", 42));
println!("{}", display);

fn format_list(items: &[i32]) -> impl fmt::Display + '_ {
    fmt::from_fn(move |f| {
        write!(f, "[")?;
        for (i, item) in items.iter().enumerate() {
            if i > 0 { write!(f, ", ")?; }
            write!(f, "{}", item)?;
        }
        write!(f, "]")
    })
}
```

## Characters

### `char::MAX_LEN_UTF8` / `MAX_LEN_UTF16`

Constants for maximum encoded length.

```rust
const MAX_UTF8: usize = char::MAX_LEN_UTF8;   // 4
const MAX_UTF16: usize = char::MAX_LEN_UTF16; // 2

let mut buf = [0u8; char::MAX_LEN_UTF8];
let len = 'ñ'.encode_utf8(&mut buf).len();
```

## Diagnostics

### `#[diagnostic::do_not_recommend]`

Prevents misleading trait suggestions in error messages.

```rust
#[diagnostic::do_not_recommend]
impl<T: Copy> MyTrait for T { }
// Errors won't suggest "implement Copy" when MyTrait is missing
```

## Type System

### Const `TypeId::of`

Get type IDs at compile time.

```rust
use std::any::TypeId;

const STRING_ID: TypeId = TypeId::of::<String>();

const fn is_string<T: 'static>() -> bool {
    TypeId::of::<T>() == STRING_ID
}
```

### Const Generic Inference with `_`

Let compiler infer const generic values.

```rust
pub fn all_false<const LEN: usize>() -> [bool; LEN] {
    [false; _]  // Compiler infers LEN
}

let arr: [i32; 5] = [0; _];  // Infers 5
```

Cannot use `_` in function signatures or const declarations.

### `use<...>` in Trait Definitions

Precise capturing syntax in traits.

```rust
trait Container {
    fn iter(&self) -> impl Iterator<Item = &u8> + use<'_>;
}
```

## proc_macro

### `Span` Location Methods

Access source location info.

```rust
use proc_macro::Span;

fn get_location(span: Span) -> String {
    format!("{}:{}:{}",
        span.file().to_string_lossy(),
        span.start().line(),
        span.start().column())
}
```

Methods: `line()`, `column()`, `start()`, `end()`, `file()`, `local_file()`.

### `Location::file_as_c_str`

Get panic location file as C string.

```rust
use std::panic::Location;

#[track_caller]
fn log_location() {
    let loc = Location::caller();
    let file: &std::ffi::CStr = loc.file_as_c_str();
}
```

## Boolean `cfg` Literals

Explicit `true`/`false` in cfg predicates.

```rust
#[cfg(true)]
fn always_compiled() {}

#[cfg(false)]
fn never_compiled() {}
```

## Never Type Lints

Deny-by-default lints preparing for `!` stabilization:
- `never_type_fallback_flowing_into_unsafe`
- `dependency_on_unit_never_type_fallback`

Suppress with `#[allow(dependency_on_unit_never_type_fallback)]`.

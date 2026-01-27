# Rust 2024 Edition

Migration guide for Edition 2024 (stabilized in Rust 1.85).

## Unsafe `extern` Blocks

External declarations require `unsafe` keyword.

```rust
// Old (2021)
extern "C" {
    fn external_func();
}

// New (2024)
unsafe extern "C" {
    fn external_func();
}
```

## Unsafe Attributes

`export_name`, `link_section`, and `no_mangle` must be marked unsafe.

```rust
// Old (2021)
#[no_mangle]
pub fn exported() {}

// New (2024)
#[unsafe(no_mangle)]
pub fn exported() {}
```

## `unsafe_op_in_unsafe_fn` Warns by Default

Unsafe operations inside unsafe functions require explicit `unsafe {}` blocks.

```rust
// Old (2021) - implicit unsafe scope
unsafe fn do_stuff(ptr: *const i32) -> i32 {
    *ptr
}

// New (2024) - explicit unsafe required
unsafe fn do_stuff(ptr: *const i32) -> i32 {
    unsafe { *ptr }
}
```

## Static Mutable References Denied

References to `static mut` now error by default. Use `std::sync` types instead.

```rust
// Old - now errors
static mut COUNTER: u32 = 0;
unsafe { COUNTER += 1; }  // Error

// New - use atomics or sync primitives
use std::sync::atomic::{AtomicU32, Ordering};
static COUNTER: AtomicU32 = AtomicU32::new(0);
COUNTER.fetch_add(1, Ordering::SeqCst);
```

## `gen` Keyword Reserved

Cannot use `gen` as identifier in 2024 edition (reserved for future generators).

## Prelude Additions

`Future` and `IntoFuture` now in prelude - no import needed.

## Environment Functions Now Unsafe

`std::env::set_var` and `std::env::remove_var` are now unsafe.

```rust
// Old
std::env::set_var("KEY", "value");

// New
unsafe { std::env::set_var("KEY", "value"); }
```

## Let Chains

Chain `let` patterns with `&&` in `if` and `while` conditions. **Edition 2024 only.**

```rust
if let Some(user) = get_user()
    && let Some(email) = user.email
    && email.contains("@")
{
    send_notification(&email);
}
```

Works in `while` loops:

```rust
while let Some(item) = iter.next()
    && item.is_valid()
{
    handle(item);
}
```
